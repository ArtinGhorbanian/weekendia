# Technical Deep Dive

> Scope: implemented behavior in the private evaluation repository. Proposed follow-on work is labeled explicitly. This document does not assert production readiness or public-release clearance.

## Application construction

`main.create_app()` builds the Flask application and accepts injected settings, provider, plan generator, rate limiter, and concurrency guard. This keeps normal startup simple while allowing route behavior to be tested without network calls. A module-level `app` remains available for simple Flask tooling and compatibility.

Settings are represented by an immutable `Settings` dataclass. `load_settings()` reads an optional `.env` file with `override=False`, so an operator-supplied process environment wins. Numeric settings are bounded before use. The selected provider mode is explicit; invalid or incomplete OpenAI configuration produces a safe configuration error rather than a demo fallback.

## Input contract

`POST /api/plan` accepts a JSON object with eight fields:

| Field | Required | Server limit or rule |
| --- | --- | --- |
| `location` | Yes | 120 characters |
| `interests` | Yes | 300 characters |
| `budget` | Yes | 100 characters |
| `group_size` | Yes | Whole number from 1 to 50 |
| `available_time` | Yes | 180 characters |
| `weather` | Yes | 160 characters |
| `transport` | Yes | 160 characters |
| `constraints` | No | 500 characters; receives an explicit default when blank |

Server normalization removes null bytes and collapses whitespace. Non-scalar values are rejected rather than stringified. Browser validation improves feedback, but the server remains authoritative.

The prompt builder labels the values as untrusted user data and directs the model not to invent live facts. This reduces instruction confusion and overclaiming, but it is not a complete prompt-injection defense or a factual-verification system.

## Provider implementations

Both implementations satisfy the small `PlanProvider.generate()` boundary.

### Demo provider

`DemoPlanProvider` formats a fixed five-part plan from normalized fields. It performs no network call, uses no live data, and returns the same text for the same input. The output itself tells the user to verify weather, prices, access, capacity, transport, and opening details.

### OpenAI provider

`OpenAIPlanProvider` creates a client per request, calls the Responses API, checks that the response completed, extracts text, and closes the client in `finally`. Current request bounds are:

- provider timeout: 45 seconds;
- SDK retries: zero;
- output tokens: operator-configured, clamped to 1 through 4096;
- default persistent Response-object storage: disabled with `store=False`; prompt-cache and abuse-log retention can still apply.

A custom OpenAI-compatible base URL and optional proxy can be configured after validation. These options increase operator responsibility: the application cannot attest to the privacy, security, or API compatibility of a custom endpoint or proxy.

## HTTP behavior

### Public routes

- `GET /` renders the page and a configuration-safe status label.
- `GET /api/health` returns only `ok`, `configured`, `mode`, and `external_processing`. It reports configuration state, not a live provider probe.
- `POST /api/plan` returns `{ ok, plan, meta }` on success or `{ ok: false, error }` on failure.

The API maps validation, configuration, capacity, timeout, connection, authentication, provider-status, incomplete-response, and unexpected failures to stable HTTP statuses and generic messages. Logs include a request ID and safe category; exception text, prompts, request bodies, provider URLs, and tracebacks are deliberately omitted from application log calls.

### Response policy

Every response receives a content security policy, clickjacking defense, MIME sniffing protection, a referrer policy, a permissions policy, same-origin resource policy, and a request ID. API responses additionally receive `Cache-Control: no-store, private` and `Pragma: no-cache`. HSTS is emitted only when Flask identifies the request as secure.

These headers are defense in depth. They do not replace TLS termination, trusted proxy configuration, authentication, authorization, distributed abuse prevention, or operational monitoring.

## Browser behavior

The client checks `/api/health`, reports demo/external/degraded/offline state, mirrors form values into a summary, and submits JSON with an abort timeout. Existing successful output is preserved when a later request fails. The result renderer escapes user/provider text before applying a restricted Markdown-like presentation, then exposes copy, plain-text download, and new-plan actions.

The interface includes a skip link, field-level status regions, focus movement after validation and success, theme persistence, reduced-motion handling, and a responsive layout. These features have automated or browser-smoke coverage where present, but they are not a claim of formal WCAG conformance.

## Guard behavior and scaling limits

The sliding-window limiter uses Flask's direct peer address and intentionally ignores forwarding headers. A bounded key map prevents unlimited attacker-controlled in-memory key growth. The concurrency guard uses a non-blocking semaphore, and teardown releases acquired slots after success or failure.

Both guards are process-local. With multiple workers or hosts, every process has separate state. Before internet exposure, use authenticated quotas and an edge or shared limiter, then decide deliberately how a trusted reverse proxy supplies client identity.

## Test evidence

The standard-library `unittest` suites cover validation and prompt characterization, mocked route success and error behavior, configuration precedence, URL rules, debug binding, deterministic demo output, OpenAI request options, request headers, error sanitization, and local guard behavior:

- [`tests/test_characterization.py`](../tests/test_characterization.py)
- [`tests/test_backend_hardening.py`](../tests/test_backend_hardening.py)

The tests use mocks or demo mode and do not prove a live OpenAI credential, model, custom endpoint, proxy, or deployment path works. See the [Release Checklist](RELEASE_CHECKLIST.md) for the evidence required at each release stage.

## Known limitations

- No live-data retrieval or verification.
- No authentication, user isolation, persistence, deletion workflow, or audit trail.
- No distributed rate limit, durable queue, provider spend ceiling, or per-user quota.
- No production server or deployment configuration.
- Markdown support is intentionally limited rather than a full CommonMark parser.
- Rights, provenance, licensing, and name/logo clearance remain unresolved; the repository must stay private.

## Follow-on work

Planned work must not be described as present behavior. Candidates include a production deployment profile, authenticated usage tiers, shared rate/spend controls, consent-aware licensed live-data sources, structured observability, and formal accessibility/security testing. Any public branding or distribution remains blocked by the rights gate in [ADR 0003](DECISIONS/0003-private-rights-gate.md).
