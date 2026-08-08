# ADR 0002: Do Not Persist Response Objects by Default

- Status: Accepted
- Date: 2026-08-08
- Scope: OpenAI provider requests in private evaluation

## Context

OpenAI mode sends normalized planning fields to an external provider. The application does not need a provider-persisted Response object for later retrieval or conversation state for its single-request plan flow. Persisting that object would therefore add data exposure without an implemented product requirement.

## Decision

Set `store=False` on every OpenAI Responses API request. Keep the request single-turn and do not persist a provider response identifier in the application.

Document the limit precisely: `store=False` prevents default persistence of the Response object for later retrieval, but it is not a zero-retention guarantee and does not disable every form of provider application state. OpenAI's published [API data-controls documentation](https://developers.openai.com/api/docs/guides/your-data) describes temporary encrypted prompt-cache state and states that abuse-monitoring logs may be retained for up to 30 days by default, subject to account controls and applicable policy. Custom endpoints and proxies may follow different practices that this application does not verify.

## Consequences

Benefits:

- aligns the provider request with the application's stateless plan flow;
- reduces avoidable persistent Response-object storage;
- makes the intended privacy posture testable at the request boundary.

Costs and limits:

- provider-side retrieval of the response is unavailable;
- prompt-cache, abuse-monitoring, infrastructure, proxy, client-device, or operator retention may still occur;
- the setting does not supply consent, deletion, data residency, or legal-basis workflows;
- external processing must still be disclosed before submission.

## Verification

The provider test captures the Responses API arguments and asserts `store` is exactly `False`. The user interface discloses external processing, and [Security Model](../SECURITY_MODEL.md) records the residual retention boundary. No live provider account setting or zero-data-retention eligibility was verified.

## Reconsider when

Revisit only if a reviewed product requirement needs provider-side state. Any change requires privacy/legal review, updated disclosure and retention handling, new tests, and a replacement ADR. Defaulting to storage for convenience is not sufficient justification.
