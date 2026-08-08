"""Environment-backed application settings with conservative defaults."""

from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit

from dotenv import load_dotenv

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = PROJECT_DIRECTORY / ".env"

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MAX_OUTPUT_TOKENS = 1800
MAX_OUTPUT_TOKENS_CAP = 4096
DEFAULT_RATE_LIMIT_REQUESTS = 12
DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 60.0
DEFAULT_MAX_CONCURRENT_PLANS = 4

VALID_MODES = frozenset({"openai", "demo"})

API_KEY_PLACEHOLDERS = {
    "paste_your_real_api_key_here",
    "paste_your_api_key_here",
    "your_real_api_key_here",
    "your_api_key_here",
    "replace_me",
    "changeme",
}


def is_placeholder_api_key(value: str) -> bool:
    """Return whether an API key is an obvious documentation placeholder."""

    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    return normalized in API_KEY_PLACEHOLDERS or normalized.startswith("paste_your_")


def _text(values: Mapping[str, str], name: str, default: str = "") -> str:
    return str(values.get(name, default) or "").strip()


def _boolean(values: Mapping[str, str], name: str, default: bool = False) -> bool:
    value = _text(values, name)
    if not value:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _bounded_integer(
    values: Mapping[str, str],
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    try:
        parsed = int(_text(values, name, str(default)))
    except ValueError:
        return default
    return min(maximum, max(minimum, parsed))


def _bounded_float(
    values: Mapping[str, str],
    name: str,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    try:
        parsed = float(_text(values, name, str(default)))
    except ValueError:
        return default
    return min(maximum, max(minimum, parsed))


def is_loopback_host(hostname: str | None) -> bool:
    """Return whether a hostname or address is restricted to loopback."""

    if not hostname:
        return False
    normalized = hostname.rstrip(".").lower()
    if normalized == "localhost" or normalized.endswith(".localhost"):
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def validate_base_url(value: str) -> str | None:
    """Return a safe validation error for an OpenAI-compatible base URL."""

    if not value:
        return "OPENAI_BASE_URL is required."

    try:
        parsed = urlsplit(value)
        # Accessing port performs validation that urlsplit otherwise defers.
        _ = parsed.port
    except ValueError:
        return "OPENAI_BASE_URL is not a valid URL."

    if parsed.username is not None or parsed.password is not None:
        return "OPENAI_BASE_URL must not contain embedded credentials."
    if not parsed.hostname or not parsed.netloc:
        return "OPENAI_BASE_URL must include a host."
    if parsed.query or parsed.fragment:
        return "OPENAI_BASE_URL must not contain a query or fragment."

    scheme = parsed.scheme.lower()
    if scheme == "https":
        return None
    if scheme == "http" and is_loopback_host(parsed.hostname):
        return None
    return "OPENAI_BASE_URL must use HTTPS (HTTP is allowed only for localhost)."


def validate_proxy_url(value: str) -> str | None:
    """Validate an optional proxy without returning or logging its value."""

    if not value:
        return None
    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError:
        return "OPENAI_PROXY_URL is not a valid URL."
    if parsed.username is not None or parsed.password is not None:
        return "OPENAI_PROXY_URL must not contain embedded credentials."
    if parsed.scheme.lower() not in {"http", "https", "socks5", "socks5h"}:
        return "OPENAI_PROXY_URL uses an unsupported scheme."
    if not parsed.hostname or not parsed.netloc or parsed.query or parsed.fragment:
        return "OPENAI_PROXY_URL is not a valid proxy URL."
    return None


@dataclass(frozen=True, slots=True)
class Settings:
    """All server configuration required to build an application instance."""

    mode: str = "openai"
    api_key: str = ""
    model: str = ""
    base_url: str = DEFAULT_BASE_URL
    proxy_url: str = ""
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = False
    max_content_length: int = 32 * 1024
    provider_timeout_seconds: float = 45.0
    provider_max_retries: int = 0
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS
    rate_limit_requests: int = DEFAULT_RATE_LIMIT_REQUESTS
    rate_limit_window_seconds: float = DEFAULT_RATE_LIMIT_WINDOW_SECONDS
    max_concurrent_plans: int = DEFAULT_MAX_CONCURRENT_PLANS

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> "Settings":
        """Build settings from an environment-like mapping."""

        output_token_name = (
            "WEEKENDIA_MAX_OUTPUT_TOKENS"
            if _text(values, "WEEKENDIA_MAX_OUTPUT_TOKENS")
            else "OPENAI_MAX_OUTPUT_TOKENS"
        )
        base_url = _text(values, "OPENAI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")

        return cls(
            mode=_text(values, "WEEKENDIA_MODE", "openai").lower(),
            api_key=_text(values, "OPENAI_API_KEY"),
            model=_text(values, "OPENAI_MODEL"),
            base_url=base_url,
            proxy_url=_text(values, "OPENAI_PROXY_URL"),
            host=_text(values, "FLASK_HOST", "127.0.0.1") or "127.0.0.1",
            port=_bounded_integer(values, "FLASK_PORT", 5000, 1, 65535),
            debug=_boolean(values, "FLASK_DEBUG", False),
            max_output_tokens=_bounded_integer(
                values,
                output_token_name,
                DEFAULT_MAX_OUTPUT_TOKENS,
                1,
                MAX_OUTPUT_TOKENS_CAP,
            ),
            rate_limit_requests=_bounded_integer(
                values,
                "WEEKENDIA_RATE_LIMIT_REQUESTS",
                DEFAULT_RATE_LIMIT_REQUESTS,
                1,
                1000,
            ),
            rate_limit_window_seconds=_bounded_float(
                values,
                "WEEKENDIA_RATE_LIMIT_WINDOW_SECONDS",
                DEFAULT_RATE_LIMIT_WINDOW_SECONDS,
                1.0,
                3600.0,
            ),
            max_concurrent_plans=_bounded_integer(
                values,
                "WEEKENDIA_MAX_CONCURRENT_PLANS",
                DEFAULT_MAX_CONCURRENT_PLANS,
                1,
                64,
            ),
        )

    @property
    def external_processing(self) -> bool:
        """Whether normal plan requests are sent to an external provider."""

        return self.mode == "openai"

    def configuration_issues(self) -> list[str]:
        """Return configuration errors without including any secret values."""

        if self.mode not in VALID_MODES:
            return ["WEEKENDIA_MODE must be either 'openai' or 'demo'."]
        if self.mode == "demo":
            return []

        issues: list[str] = []
        if not self.api_key or is_placeholder_api_key(self.api_key):
            issues.append("OPENAI_API_KEY is not configured.")
        if not self.model:
            issues.append("OPENAI_MODEL is not configured.")

        base_url_issue = validate_base_url(self.base_url)
        if base_url_issue:
            issues.append(base_url_issue)
        proxy_url_issue = validate_proxy_url(self.proxy_url)
        if proxy_url_issue:
            issues.append(proxy_url_issue)
        return issues

    @property
    def configured(self) -> bool:
        return not self.configuration_issues()


def load_settings(
    env_file: str | os.PathLike[str] | None = DEFAULT_ENV_FILE,
    environ: Mapping[str, str] | None = None,
) -> Settings:
    """Load a dotenv file without overriding process-level configuration.

    A physical dotenv file is optional. Passing an explicit mapping is useful for
    dependency-injected tests and does not mutate the process environment.
    """

    if environ is None:
        if env_file is not None:
            load_dotenv(dotenv_path=env_file, override=False, encoding="utf-8")
        values: Mapping[str, str] = os.environ
    else:
        values = environ
    return Settings.from_mapping(values)


__all__ = [
    "API_KEY_PLACEHOLDERS",
    "DEFAULT_ENV_FILE",
    "MAX_OUTPUT_TOKENS_CAP",
    "Settings",
    "is_loopback_host",
    "is_placeholder_api_key",
    "load_settings",
    "validate_base_url",
    "validate_proxy_url",
]
