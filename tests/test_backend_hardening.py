from __future__ import annotations

import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from openai import APITimeoutError

import main
from weekendia.config import MAX_OUTPUT_TOKENS_CAP, Settings, load_settings
from weekendia.guards import ConcurrencyGuard, SlidingWindowRateLimiter
from weekendia.providers import OpenAIPlanProvider, ProviderResponseError


def valid_payload() -> dict[str, str]:
    return {
        "location": "Example City",
        "interests": "nature, cafes, photography",
        "budget": "$80",
        "group_size": "2",
        "available_time": "Saturday from 1 PM to 6 PM",
        "weather": "cool with possible rain",
        "transport": "Public transit",
        "constraints": "Prefer accessible routes and quiet spaces",
    }


DEMO_SETTINGS = Settings(
    mode="demo",
    rate_limit_requests=20,
    rate_limit_window_seconds=60.0,
    max_concurrent_plans=2,
)


class SettingsHardeningTests(unittest.TestCase):
    def test_process_environment_takes_precedence_over_dotenv(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env"
            env_file.write_text(
                "WEEKENDIA_MODE=openai\nOPENAI_MODEL=file-model\n",
                encoding="utf-8",
            )

            with patch.dict(os.environ, {"WEEKENDIA_MODE": "demo"}, clear=True):
                settings = load_settings(env_file)

                self.assertEqual(settings.mode, "demo")
                self.assertEqual(settings.model, "file-model")

    def test_missing_dotenv_is_optional_and_mode_defaults_to_openai(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_file = Path(temporary_directory) / "does-not-exist.env"
            with patch.dict(os.environ, {}, clear=True):
                settings = load_settings(missing_file)

        self.assertEqual(settings.mode, "openai")
        self.assertFalse(settings.configured)

    def test_output_tokens_are_configurable_but_capped(self) -> None:
        settings = Settings.from_mapping(
            {
                "WEEKENDIA_MODE": "demo",
                "WEEKENDIA_MAX_OUTPUT_TOKENS": "999999",
            }
        )
        self.assertEqual(settings.max_output_tokens, MAX_OUTPUT_TOKENS_CAP)

    def test_base_url_requires_https_except_loopback_and_rejects_userinfo(self) -> None:
        common = {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "test-model"}

        remote_http = Settings.from_mapping(
            {**common, "OPENAI_BASE_URL": "http://provider.example/v1"}
        )
        loopback_http = Settings.from_mapping(
            {**common, "OPENAI_BASE_URL": "http://127.0.0.1:8080/v1"}
        )
        userinfo = Settings.from_mapping(
            {**common, "OPENAI_BASE_URL": "https://user:pass@provider.example/v1"}
        )

        self.assertFalse(remote_http.configured)
        self.assertTrue(loopback_http.configured)
        self.assertFalse(userinfo.configured)

    def test_debug_mode_is_refused_for_non_loopback_bindings(self) -> None:
        self.assertTrue(
            main.development_server_debug_mode(
                replace(DEMO_SETTINGS, host="127.0.0.1", debug=True)
            )
        )
        with self.assertRaisesRegex(RuntimeError, "loopback"):
            main.development_server_debug_mode(
                replace(DEMO_SETTINGS, host="0.0.0.0", debug=True)
            )


class ProviderHardeningTests(unittest.TestCase):
    def test_openai_responses_call_disables_storage_and_bounds_output(self) -> None:
        captured_client_options: dict[str, object] = {}
        captured_request: dict[str, object] = {}

        class FakeResponses:
            def create(self, **kwargs):
                captured_request.update(kwargs)
                return SimpleNamespace(output_text="  # Fake plan  ")

        class FakeClient:
            def __init__(self) -> None:
                self.responses = FakeResponses()
                self.closed = False

            def close(self) -> None:
                self.closed = True

        fake_client = FakeClient()

        def fake_client_factory(**kwargs):
            captured_client_options.update(kwargs)
            return fake_client

        settings = Settings(
            mode="openai",
            api_key="test-key",
            model="test-model",
            base_url="https://provider.example/v1",
            max_output_tokens=1234,
        )
        result = OpenAIPlanProvider(settings, fake_client_factory).generate(
            valid_payload()
        )

        self.assertEqual(result, "# Fake plan")
        self.assertEqual(captured_client_options["timeout"], 45.0)
        self.assertEqual(captured_client_options["max_retries"], 0)
        self.assertIs(captured_request["store"], False)
        self.assertEqual(captured_request["max_output_tokens"], 1234)
        self.assertTrue(fake_client.closed)

    def test_incomplete_provider_response_is_rejected(self) -> None:
        class FakeResponses:
            def create(self, **_kwargs):
                return SimpleNamespace(
                    status="incomplete",
                    output_text="# Partial plan",
                    incomplete_details=SimpleNamespace(reason="max_output_tokens"),
                )

        fake_client = SimpleNamespace(
            responses=FakeResponses(),
            close=lambda: None,
        )
        settings = Settings(
            mode="openai",
            api_key="test-key",
            model="test-model",
        )

        with self.assertRaises(ProviderResponseError):
            OpenAIPlanProvider(
                settings,
                client_factory=lambda **_kwargs: fake_client,
            ).generate(valid_payload())


class AppHardeningTests(unittest.TestCase):
    def test_demo_mode_is_deterministic_and_never_needs_an_external_client(
        self,
    ) -> None:
        application = main.create_app(settings=DEMO_SETTINGS)
        client = application.test_client()

        first = client.post("/api/plan", json=valid_payload())
        second = client.post("/api/plan", json=valid_payload())

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()["plan"], second.get_json()["plan"])
        self.assertIn("deterministic and local", first.get_json()["plan"])
        self.assertEqual(first.get_json()["meta"]["mode"], "demo")

    def test_health_is_generic_and_does_not_claim_provider_reachability(self) -> None:
        application = main.create_app(settings=DEMO_SETTINGS)
        response = application.test_client().get("/api/health")
        body = response.get_json()

        self.assertEqual(set(body), {"ok", "configured", "mode", "external_processing"})
        self.assertTrue(body["configured"])
        self.assertEqual(body["mode"], "demo")
        self.assertFalse(body["external_processing"])
        self.assertNotIn("model", body)
        self.assertNotIn("proxy", body)

    def test_timeout_is_caught_before_connection_error_and_maps_to_504(self) -> None:
        def time_out(_user_data: dict[str, str]) -> str:
            raise APITimeoutError(
                request=httpx.Request("POST", "https://private.invalid")
            )

        application = main.create_app(
            settings=DEMO_SETTINGS,
            plan_generator=time_out,
        )
        with self.assertLogs("weekendia", level="WARNING") as captured:
            response = application.test_client().post("/api/plan", json=valid_payload())

        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.get_json()["error"]["code"], "timeout_error")
        self.assertNotIn("private.invalid", " ".join(captured.output))

    def test_oversized_payload_and_wrong_media_type_are_json(self) -> None:
        application = main.create_app(
            settings=replace(DEMO_SETTINGS, max_content_length=128)
        )
        client = application.test_client()

        oversized = client.post(
            "/api/plan",
            data=b'{"location":"' + (b"x" * 512) + b'"}',
            content_type="application/json",
        )
        unsupported = client.post("/api/plan", data="plain text")

        self.assertEqual(oversized.status_code, 413)
        self.assertTrue(oversized.is_json)
        self.assertEqual(oversized.get_json()["error"]["code"], "payload_too_large")
        self.assertEqual(unsupported.status_code, 415)
        self.assertTrue(unsupported.is_json)

    def test_non_scalar_fields_are_rejected(self) -> None:
        payload = valid_payload()
        payload["location"] = {"city": "Example City"}
        payload["interests"] = ["nature", "cafes"]

        response = (
            main.create_app(settings=DEMO_SETTINGS)
            .test_client()
            .post("/api/plan", json=payload)
        )

        self.assertEqual(response.status_code, 400)
        fields = response.get_json()["error"]["fields"]
        self.assertIn("location", fields)
        self.assertIn("interests", fields)

    def test_invalid_requests_do_not_consume_provider_capacity(self) -> None:
        guard = ConcurrencyGuard(1)
        application = main.create_app(
            settings=DEMO_SETTINGS,
            concurrency_guard=guard,
        )

        response = application.test_client().post("/api/plan", data="plain text")

        self.assertEqual(response.status_code, 415)
        self.assertTrue(guard.try_acquire())
        guard.release()

    def test_provider_failure_releases_capacity(self) -> None:
        guard = ConcurrencyGuard(1)

        def fail_safely(_user_data: dict[str, str]) -> str:
            raise RuntimeError("synthetic test failure")

        application = main.create_app(
            settings=DEMO_SETTINGS,
            plan_generator=fail_safely,
            concurrency_guard=guard,
        )

        response = application.test_client().post("/api/plan", json=valid_payload())

        self.assertEqual(response.status_code, 500)
        self.assertTrue(guard.try_acquire())
        guard.release()

    def test_rate_limit_is_a_per_app_sliding_window(self) -> None:
        limiter = SlidingWindowRateLimiter(1, 60.0, clock=lambda: 100.0)
        application = main.create_app(
            settings=DEMO_SETTINGS,
            rate_limiter=limiter,
        )
        client = application.test_client()

        first = client.post("/api/plan", json=valid_payload())
        limited = client.post("/api/plan", json=valid_payload())

        self.assertEqual(first.status_code, 200)
        self.assertEqual(limited.status_code, 429)
        self.assertEqual(limited.get_json()["error"]["code"], "rate_limit_error")
        self.assertEqual(limited.headers["Retry-After"], "60")

    def test_api_responses_are_private_no_store_and_have_request_ids(self) -> None:
        application = main.create_app(settings=DEMO_SETTINGS)
        response = application.test_client().get(
            "/api/health", headers={"X-Request-ID": "safe-test-id"}
        )

        self.assertIn("private", response.headers["Cache-Control"])
        self.assertIn("no-store", response.headers["Cache-Control"])
        self.assertEqual(response.headers["X-Request-ID"], "safe-test-id")

    def test_cross_site_fetch_metadata_rejects_post_before_processing(self) -> None:
        def should_not_run(_user_data: dict[str, str]) -> str:
            self.fail("The provider must not run for a cross-site request.")

        application = main.create_app(
            settings=DEMO_SETTINGS,
            plan_generator=should_not_run,
        )
        response = application.test_client().post(
            "/api/plan",
            json=valid_payload(),
            headers={"Sec-Fetch-Site": "cross-site"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["error"]["code"], "cross_site_request")

    def test_concurrency_guard_fails_fast_when_local_capacity_is_full(self) -> None:
        guard = ConcurrencyGuard(1)
        self.assertTrue(guard.try_acquire())
        try:
            application = main.create_app(
                settings=DEMO_SETTINGS,
                concurrency_guard=guard,
            )
            response = application.test_client().post("/api/plan", json=valid_payload())
        finally:
            guard.release()

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"]["code"], "capacity_error")


if __name__ == "__main__":
    unittest.main()
