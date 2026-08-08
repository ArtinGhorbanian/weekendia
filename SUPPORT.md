# Support

Weekendia is a private evaluation build with no public support channel or response-time commitment. Authorized collaborators should use the private repository's issue tracker for reproducible product and development questions.

## Choose the right route

- **Bug or unexpected behavior:** open a private bug report with reproduction steps.
- **Setup or configuration question:** open a private support issue and state the selected mode.
- **Feature proposal:** open a private feature request that explains the user need and privacy, security, accessibility, and rights impact.
- **Security vulnerability:** follow [SECURITY.md](SECURITY.md). Do not place exploit details, secrets, or sensitive plan content in a general issue.
- **Rights, provenance, or licensing concern:** raise it through an authorized private project channel and pause the affected publication or reuse decision.

## Helpful diagnostic information

Include:

- the operating system, Python version, and browser version;
- whether the application is in `demo` or `openai` mode;
- the command or user flow that failed;
- expected behavior and actual behavior;
- a minimal reproduction and relevant test output;
- the response status, stable error code, and `X-Request-ID` when available.

Before posting, remove API keys, authorization headers, proxy details, personal information, submitted plan fields, generated plan content, local usernames, and private URLs. Prefer a newly created synthetic example. Do not attach `.env` files or raw provider responses.

## Scope and limitations

Support can help interpret documented local setup, tests, application errors, and private-evaluation behavior. It cannot verify live venue information, make bookings, provide emergency or safety services, resolve provider billing or account access, or approve public release and licensing by itself.

The Flask development server is supported only for local evaluation. Any future hosted deployment requires a separately reviewed architecture, access model, observability plan, data-handling assessment, and operational owner.

Start with the [README](README.md), then consult [Architecture](docs/ARCHITECTURE.md), [Security model](docs/SECURITY_MODEL.md), and [Validation](docs/VALIDATION.md).

