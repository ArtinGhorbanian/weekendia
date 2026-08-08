from __future__ import annotations

import unittest
from unittest.mock import patch

import main


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


class ValidationCharacterizationTests(unittest.TestCase):
    def test_valid_payload_preserves_all_eight_planning_signals(self) -> None:
        cleaned, errors = main.validate_payload(valid_payload())

        self.assertEqual(errors, {})
        self.assertEqual(cleaned, valid_payload())

    def test_optional_constraints_receive_an_explicit_default(self) -> None:
        payload = valid_payload()
        payload["constraints"] = "   "

        cleaned, errors = main.validate_payload(payload)

        self.assertEqual(errors, {})
        self.assertEqual(
            cleaned["constraints"],
            "No additional constraints or preferences were provided.",
        )

    def test_group_size_boundary_and_null_byte_normalization(self) -> None:
        payload = valid_payload()
        payload["group_size"] = "50"
        payload["location"] = "Example\x00   City"

        cleaned, errors = main.validate_payload(payload)

        self.assertEqual(errors, {})
        self.assertEqual(cleaned["location"], "Example City")

        payload["group_size"] = "51"
        _, errors = main.validate_payload(payload)
        self.assertIn("group_size", errors)

    def test_non_object_payload_returns_form_error(self) -> None:
        cleaned, errors = main.validate_payload(["not", "an", "object"])

        self.assertEqual(cleaned, {})
        self.assertIn("form", errors)


class PromptCharacterizationTests(unittest.TestCase):
    def test_prompt_keeps_product_structure_and_truthfulness_guardrails(self) -> None:
        prompt = main.build_prompt(valid_payload())

        for heading in (
            "1. User Snapshot",
            "2. Top Recommendations",
            "3. Final Weekend Schedule",
            "4. Backup Option",
            "5. Before-You-Go Checklist",
        ):
            self.assertIn(heading, prompt)

        for value in valid_payload().values():
            self.assertIn(value, prompt)

        self.assertIn("untrusted user data", prompt)
        self.assertIn("Do not invent exact opening hours", prompt)
        self.assertIn("Output English only", prompt)


class RouteCharacterizationTests(unittest.TestCase):
    def setUp(self) -> None:
        main.app.config.update(TESTING=True)
        self.client = main.app.test_client()

    def test_root_and_health_routes_return_json_safe_security_headers(self) -> None:
        root = self.client.get("/")
        health = self.client.get("/api/health")

        self.assertEqual(root.status_code, 200)
        self.assertEqual(health.status_code, 200)
        self.assertIn("Weekendia", root.get_data(as_text=True))
        self.assertEqual(root.headers["X-Frame-Options"], "DENY")
        self.assertIn("default-src 'self'", root.headers["Content-Security-Policy"])

    def test_plan_route_returns_the_provider_result_without_live_api_use(self) -> None:
        with patch.object(
            main,
            "generate_weekend_plan",
            return_value="# Sample plan\n\n- A deterministic test result",
        ):
            response = self.client.post("/api/plan", json=valid_payload())

        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["ok"])
        self.assertIn("deterministic test result", body["plan"])
        self.assertEqual(body["meta"]["location"], "Example City")

    def test_plan_route_reports_field_errors_without_calling_provider(self) -> None:
        with patch.object(main, "generate_weekend_plan") as provider:
            response = self.client.post("/api/plan", json={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "validation_error")
        provider.assert_not_called()


if __name__ == "__main__":
    unittest.main()
