"""Deterministic and OpenAI-backed weekend-plan providers."""

from __future__ import annotations

from typing import Any, Callable, Protocol

from openai import DefaultHttpxClient, OpenAI

from .config import MAX_OUTPUT_TOKENS_CAP, Settings
from .planning import build_prompt

PROVIDER_INSTRUCTIONS = (
    "You are Weekendia, a professional, realistic, creative, and kind "
    "weekend activity planner. Carefully respect the user's budget, time, "
    "weather, location, transportation, group size, interests, and constraints. "
    "Never fabricate live or unverified information. Always respond entirely "
    "in clear, natural English, regardless of the language used in the input."
)


class ConfigurationError(RuntimeError):
    """Raised when settings cannot safely configure the selected provider."""


class ProviderResponseError(RuntimeError):
    """Raised when a provider response is incomplete or unusable."""


class PlanProvider(Protocol):
    def generate(self, user_data: dict[str, str]) -> str:
        """Return a Markdown weekend plan."""


def openai_client_options(settings: Settings) -> dict[str, Any]:
    """Build tightly bounded OpenAI client options from validated settings."""

    options: dict[str, Any] = {
        "api_key": settings.api_key,
        "base_url": settings.base_url,
        "timeout": settings.provider_timeout_seconds,
        "max_retries": settings.provider_max_retries,
    }
    if settings.proxy_url:
        options["http_client"] = DefaultHttpxClient(proxy=settings.proxy_url)
    return options


class OpenAIPlanProvider:
    """Generate plans through the Responses API using an injectable client."""

    def __init__(
        self,
        settings: Settings,
        client_factory: Callable[..., Any] = OpenAI,
    ) -> None:
        self._settings = settings
        self._client_factory = client_factory

    def generate(self, user_data: dict[str, str]) -> str:
        issues = self._settings.configuration_issues()
        if issues:
            raise ConfigurationError("The selected provider is not configured.")

        client = self._client_factory(**openai_client_options(self._settings))
        try:
            response = client.responses.create(
                model=self._settings.model,
                instructions=PROVIDER_INSTRUCTIONS,
                input=build_prompt(user_data),
                max_output_tokens=min(
                    MAX_OUTPUT_TOKENS_CAP,
                    max(1, self._settings.max_output_tokens),
                ),
                store=False,
            )
            status = getattr(response, "status", "completed")
            if status != "completed":
                raise ProviderResponseError(
                    "The provider did not return a completed response."
                )
            return (response.output_text or "").strip()
        finally:
            close = getattr(client, "close", None)
            if callable(close):
                close()


class DemoPlanProvider:
    """Create a deterministic local-only plan without making network calls."""

    def generate(self, user_data: dict[str, str]) -> str:
        location = user_data["location"]
        interests = user_data["interests"]
        budget = user_data["budget"]
        group_size = user_data["group_size"]
        available_time = user_data["available_time"]
        weather = user_data["weather"]
        transport = user_data["transport"]
        constraints = user_data["constraints"]

        return f"""# Weekendia demo plan

## 1. User Snapshot
This local demo is tailored for {group_size} people in {location}, with interests in {interests}, a total budget of {budget}, and availability of {available_time}. It also accounts for {weather}, travel by {transport}, and this preference: {constraints}

## 2. Top Recommendations

1. **Flexible neighborhood discovery loop**
   - Why it fits: It can combine the listed interests without depending on a specific venue.
   - Start and duration: Begin near the start of the available window and allow 60–90 minutes.
   - Cost: Choose free public areas so most of the stated budget remains available.
   - Suitability: Keep the route short enough for the group and use the weather-appropriate option.
   - Tip: Select and verify an accessible local route before leaving.

2. **Self-guided interest challenge**
   - Why it fits: Each person can choose a small photo, observation, or creative prompt connected to {interests}.
   - Start and duration: Follow the discovery loop for about 45–60 minutes.
   - Cost: Free unless the group chooses optional supplies.
   - Suitability: Works indoors or outdoors and scales to the stated group size.
   - Tip: Agree on a meeting point and boundaries first.

3. **Relaxed food or drink break**
   - Why it fits: It provides rest and conversation between activities.
   - Start and duration: Use the middle of the available window and allow 45–75 minutes.
   - Cost: Set a per-person ceiling from the total budget before ordering.
   - Suitability: Choose a place that meets the group's access, noise, and weather needs.
   - Tip: Verify current prices, opening hours, and seating directly with the venue.

4. **Shared low-cost wind-down**
   - Why it fits: A short game, recap, sketch, or playlist session ends the plan without a long transfer.
   - Start and duration: Reserve the final 30–45 minutes.
   - Cost: Free with items the group already has.
   - Suitability: Adapt it to the group's energy and stated constraints.
   - Tip: Keep this optional if earlier activities run long.

## 3. Final Weekend Schedule
1. Before departure, choose one compact area and verify transport, access, weather, and opening details.
2. Start with the neighborhood discovery loop.
3. Continue with the self-guided interest challenge nearby.
4. Take the planned food or drink break while staying within the agreed spending ceiling.
5. Finish with the shared wind-down and leave buffer time for the return journey.

## 4. Backup Option
If weather, capacity, access, or closures disrupt the route, use one verified indoor public space and run the same interest challenge and wind-down there. This demo does not know live venue availability.

## 5. Before-You-Go Checklist
- Verify live weather, opening hours, prices, accessibility, and capacity.
- Confirm the route and return transport with the whole group.
- Set a simple per-person spending limit within {budget}.
- Bring only the weather and activity essentials you have verified.
- Share the meeting point and any relevant access needs.

_Demo mode is deterministic and local. It does not use live venue, price, availability, transport, or weather data._"""


def create_provider(
    settings: Settings,
    client_factory: Callable[..., Any] = OpenAI,
) -> PlanProvider:
    """Create the explicitly selected provider; never silently change modes."""

    if settings.mode == "demo":
        return DemoPlanProvider()
    if settings.mode == "openai":
        return OpenAIPlanProvider(settings, client_factory=client_factory)
    raise ConfigurationError("The selected provider mode is invalid.")


__all__ = [
    "ConfigurationError",
    "DemoPlanProvider",
    "OpenAIPlanProvider",
    "PROVIDER_INSTRUCTIONS",
    "PlanProvider",
    "ProviderResponseError",
    "create_provider",
    "openai_client_options",
]
