"""Weekendia Flask entry point and backwards-compatible backend facade."""

from __future__ import annotations

import logging
import re
import uuid
from pathlib import Path
from typing import Any, Callable

from flask import (
    Flask,
    Response,
    g,
    has_request_context,
    jsonify,
    render_template,
    request,
)
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    NotFoundError,
    OpenAI,
    RateLimitError,
)
from werkzeug.exceptions import RequestEntityTooLarge

from weekendia.config import (
    API_KEY_PLACEHOLDERS,
    DEFAULT_ENV_FILE,
    VALID_MODES,
    Settings,
    is_loopback_host,
    is_placeholder_api_key,
    load_settings,
)
from weekendia.guards import ConcurrencyGuard, SlidingWindowRateLimiter
from weekendia.planning import (
    FIELD_RULES,
    build_prompt,
    normalize_text,
    validate_payload,
)
from weekendia.providers import (
    ConfigurationError,
    PlanProvider,
    ProviderResponseError,
    create_provider,
    openai_client_options,
)

APP_DIRECTORY = Path(__file__).resolve().parent
ENV_FILE = DEFAULT_ENV_FILE
SETTINGS = load_settings(ENV_FILE)

# Compatibility constants retained for existing imports and simple deployments.
API_KEY = SETTINGS.api_key
MODEL = SETTINGS.model
BASE_URL = SETTINGS.base_url
PROXY_URL = SETTINGS.proxy_url
HOST = SETTINGS.host
PORT = SETTINGS.port
DEBUG_MODE = SETTINGS.debug

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("weekendia")

_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def configuration_issues(settings: Settings | None = None) -> list[str]:
    """Return safe configuration issues for the selected application mode."""

    return (settings or SETTINGS).configuration_issues()


def create_openai_client(
    settings: Settings | None = None,
    client_factory: Callable[..., Any] = OpenAI,
) -> Any:
    """Create a bounded OpenAI client while retaining the legacy helper."""

    selected = settings or SETTINGS
    if selected.mode != "openai" or selected.configuration_issues():
        raise ConfigurationError("The selected provider is not configured.")
    return client_factory(**openai_client_options(selected))


def generate_weekend_plan(
    user_data: dict[str, str],
    *,
    settings: Settings | None = None,
    provider: PlanProvider | None = None,
) -> str:
    """Generate a weekend plan using the explicitly configured provider."""

    selected = settings or SETTINGS
    selected_provider = provider or create_provider(selected)
    return selected_provider.generate(user_data)


def _request_id() -> str | None:
    if not has_request_context():
        return None
    return getattr(g, "request_id", None)


def json_error(message: str, status: int, code: str, **extra: Any):
    """Return a consistent JSON error response without leaking internals."""

    error: dict[str, Any] = {"code": code, "message": message}
    error.update(extra)
    request_id = _request_id()
    if request_id:
        error["request_id"] = request_id
    return jsonify({"ok": False, "error": error}), status


def _response_with_status(result: tuple[Response, int]) -> Response:
    response, status = result
    response.status_code = status
    return response


def _safe_request_id(candidate: str | None) -> str:
    if candidate and _SAFE_REQUEST_ID.fullmatch(candidate):
        return candidate
    return uuid.uuid4().hex


def create_app(
    settings: Settings | None = None,
    *,
    plan_provider: PlanProvider | None = None,
    plan_generator: Callable[[dict[str, str]], str] | None = None,
    rate_limiter: SlidingWindowRateLimiter | None = None,
    concurrency_guard: ConcurrencyGuard | None = None,
) -> Flask:
    """Build an injectable Flask application without contacting a provider."""

    app_settings = settings or SETTINGS
    application = Flask(
        __name__,
        static_folder=str(APP_DIRECTORY / "static"),
        template_folder=str(APP_DIRECTORY / "templates"),
    )
    application.config.update(
        MAX_CONTENT_LENGTH=app_settings.max_content_length,
        TEMPLATES_AUTO_RELOAD=app_settings.debug,
    )
    application.json.ensure_ascii = False
    application.extensions["weekendia.settings"] = app_settings

    local_rate_limiter = rate_limiter or SlidingWindowRateLimiter(
        app_settings.rate_limit_requests,
        app_settings.rate_limit_window_seconds,
    )
    local_concurrency_guard = concurrency_guard or ConcurrencyGuard(
        app_settings.max_concurrent_plans
    )
    application.extensions["weekendia.rate_limiter"] = local_rate_limiter
    application.extensions["weekendia.concurrency_guard"] = local_concurrency_guard

    def plan_path() -> bool:
        return request.method == "POST" and request.path == "/api/plan"

    @application.before_request
    def apply_request_guards():
        g.request_id = _safe_request_id(request.headers.get("X-Request-ID"))
        g.weekendia_concurrency_acquired = False

        if (
            request.method == "POST"
            and request.headers.get("Sec-Fetch-Site", "").strip().lower()
            == "cross-site"
        ):
            return json_error(
                "Cross-site POST requests are not accepted.",
                403,
                "cross_site_request",
            )

        if not plan_path():
            return None

        # This deliberately uses Flask's direct peer address. It does not trust
        # spoofable forwarding headers and is only a small per-process safeguard.
        client_key = request.remote_addr or "unknown"
        allowed, remaining, retry_after = local_rate_limiter.check(client_key)
        g.weekendia_rate_limit_remaining = remaining
        if not allowed:
            response = _response_with_status(
                json_error(
                    "Too many plan requests. Please wait and try again.",
                    429,
                    "rate_limit_error",
                )
            )
            response.headers["Retry-After"] = str(retry_after)
            return response

        if (
            request.content_length is not None
            and request.content_length > app_settings.max_content_length
        ):
            return json_error(
                "The request body is too large.",
                413,
                "payload_too_large",
            )

        return None

    @application.teardown_request
    def release_concurrency_slot(_error: BaseException | None) -> None:
        if getattr(g, "weekendia_concurrency_acquired", False):
            g.weekendia_concurrency_acquired = False
            local_concurrency_guard.release()

    @application.get("/")
    def index():
        if app_settings.mode == "demo":
            planner_mode_label = "Local demo mode"
        elif app_settings.configured:
            planner_mode_label = "External planner mode"
        else:
            planner_mode_label = "Configuration required"
        return render_template(
            "index.html",
            # Keep the old template variable while the UI migrates to the
            # configuration-safe label.
            model_name=planner_mode_label,
            planner_mode_label=planner_mode_label,
        )

    @application.get("/api/health")
    def health():
        public_mode = (
            app_settings.mode if app_settings.mode in VALID_MODES else "invalid"
        )
        return jsonify(
            {
                "ok": True,
                "configured": app_settings.configured,
                "mode": public_mode,
                "external_processing": app_settings.external_processing,
            }
        )

    @application.post("/api/plan")
    def create_plan():
        if not request.is_json:
            return json_error(
                "Send the request as JSON.",
                415,
                "unsupported_media_type",
            )

        payload = request.get_json(silent=True)
        user_data, validation_errors = validate_payload(payload)
        if validation_errors:
            return json_error(
                "A few form fields need your attention.",
                400,
                "validation_error",
                fields=validation_errors,
            )

        if not local_concurrency_guard.try_acquire():
            response = _response_with_status(
                json_error(
                    "The planner is busy. Please try again shortly.",
                    503,
                    "capacity_error",
                )
            )
            response.headers["Retry-After"] = "1"
            return response
        g.weekendia_concurrency_acquired = True

        try:
            if plan_generator is not None:
                result = plan_generator(user_data)
            elif plan_provider is not None:
                result = plan_provider.generate(user_data)
            else:
                # Resolve this global at request time so legacy monkeypatching of
                # main.generate_weekend_plan continues to work.
                result = generate_weekend_plan(user_data, settings=app_settings)

        except ConfigurationError:
            logger.warning(
                "Planner configuration unavailable | request_id=%s", _request_id()
            )
            return json_error(
                "The planner service is not configured.",
                503,
                "configuration_error",
            )

        except ProviderResponseError:
            logger.warning(
                "Provider response incomplete | request_id=%s", _request_id()
            )
            return json_error(
                "The planning service returned an incomplete response.",
                502,
                "incomplete_provider_response",
            )

        except AuthenticationError:
            logger.warning(
                "Provider authentication failed | request_id=%s", _request_id()
            )
            return json_error(
                "The planning service could not authenticate with its provider.",
                502,
                "authentication_error",
            )

        # APITimeoutError subclasses APIConnectionError, so this order matters.
        except APITimeoutError:
            logger.warning("Provider request timed out | request_id=%s", _request_id())
            return json_error(
                "The planning service took too long to respond.",
                504,
                "timeout_error",
            )

        except APIConnectionError:
            logger.warning("Provider connection failed | request_id=%s", _request_id())
            return json_error(
                "The planning service is temporarily unavailable.",
                503,
                "connection_error",
            )

        except RateLimitError:
            logger.warning("Provider capacity reached | request_id=%s", _request_id())
            return json_error(
                "The planning service is temporarily at capacity.",
                503,
                "provider_rate_limit_error",
            )

        except NotFoundError:
            logger.warning(
                "Configured provider resource unavailable | request_id=%s",
                _request_id(),
            )
            return json_error(
                "The planning service is temporarily unavailable.",
                502,
                "provider_resource_error",
            )

        except APIStatusError as error:
            status_code = getattr(error, "status_code", None)
            safe_status = status_code if isinstance(status_code, int) else "unknown"
            logger.warning(
                "Provider returned an error | request_id=%s | status=%s",
                _request_id(),
                safe_status,
            )
            return json_error(
                "The planning service returned an unexpected response.",
                502,
                "api_status_error",
            )

        except Exception as error:
            # Deliberately omit exception text, request bodies, prompts, URLs, and
            # tracebacks from logs because they may contain sensitive data.
            logger.error(
                "Unexpected planner failure | request_id=%s | category=%s",
                _request_id(),
                type(error).__name__,
            )
            return json_error(
                "An unexpected server error occurred.",
                500,
                "unexpected_error",
            )

        if not result:
            return json_error(
                "The planning service did not return a text response.",
                502,
                "empty_response",
            )

        return jsonify(
            {
                "ok": True,
                "plan": result,
                "meta": {
                    "mode": app_settings.mode,
                    "location": user_data["location"],
                    "budget": user_data["budget"],
                    "group_size": user_data["group_size"],
                },
            }
        )

    @application.errorhandler(RequestEntityTooLarge)
    def payload_too_large(_error: RequestEntityTooLarge):
        return json_error(
            "The JSON request body is too large.",
            413,
            "payload_too_large",
        )

    @application.after_request
    def add_security_headers(response: Response) -> Response:
        """Apply conservative browser and API response headers."""

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["X-Request-ID"] = _request_id() or uuid.uuid4().hex

        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, private"
            response.headers["Pragma"] = "no-cache"
        if plan_path():
            response.headers["X-RateLimit-Limit"] = str(local_rate_limiter.limit)
            remaining = getattr(g, "weekendia_rate_limit_remaining", None)
            if isinstance(remaining, int):
                response.headers["X-RateLimit-Remaining"] = str(remaining)
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    return application


app = create_app()


def development_server_debug_mode(settings: Settings) -> bool:
    """Refuse to expose Flask's interactive debugger beyond loopback."""

    if settings.debug and not is_loopback_host(settings.host):
        raise RuntimeError(
            "FLASK_DEBUG may only be enabled when FLASK_HOST is a loopback address."
        )
    return settings.debug


if __name__ == "__main__":
    safe_debug_mode = development_server_debug_mode(SETTINGS)
    print("=" * 72)
    print("Weekendia | Weekend Activity Planner")
    print(f"Application URL: http://{HOST}:{PORT}")
    print(f"Mode: {SETTINGS.mode if SETTINGS.mode in VALID_MODES else 'invalid'}")
    print("=" * 72)

    app.run(
        host=HOST,
        port=PORT,
        debug=safe_debug_mode,
        use_reloader=safe_debug_mode,
    )


__all__ = [
    "API_KEY_PLACEHOLDERS",
    "BASE_URL",
    "ConfigurationError",
    "ENV_FILE",
    "FIELD_RULES",
    "MODEL",
    "PROXY_URL",
    "Settings",
    "app",
    "build_prompt",
    "configuration_issues",
    "create_app",
    "create_openai_client",
    "development_server_debug_mode",
    "generate_weekend_plan",
    "is_placeholder_api_key",
    "normalize_text",
    "validate_payload",
]
