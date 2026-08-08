# Security Policy

## Current status

Weekendia is under private evaluation. No release line is currently designated
as supported for public production use. Security reports concerning the current
default branch are welcome.

## Report a vulnerability privately

Contact an authorized maintainer through the same access-controlled channel
used to grant or coordinate access to this private repository. Ask the
maintainer to establish a restricted reporting thread, and share technical
details only after confirming who can read that thread.

Do not disclose a suspected vulnerability in a general repository issue,
discussion, pull request, screenshot, or broadly visible log. In particular,
do not open an issue when every repository collaborator can read issues. Do not
include API keys, access tokens, personal data, provider responses containing
private details, or other live secrets in a report. Replace sensitive values
with clearly marked placeholders and attach only the minimum reproduction
material needed.

If no appropriately restricted channel is available, send only a request to
establish one; do not include vulnerability details until access is confirmed.

## Helpful report contents

Include, when applicable:

- the affected commit or private release identifier;
- the component, endpoint, and configuration mode involved;
- minimal reproduction steps and the observed impact;
- whether the issue requires `WEEKENDIA_MODE=openai` or occurs in demo mode;
- sanitized request and response metadata, excluding plan contents and secrets;
- any mitigation already tested.

## Security boundaries

- Demo mode is local and deterministic. OpenAI mode sends submitted planning
  fields to the configured external provider.
- `.env` files and provider credentials must remain outside version control.
- The in-process rate and concurrency guards do not coordinate across multiple
  application instances.
- Flask's built-in development server and debugger are not production controls.
- A custom `OPENAI_BASE_URL` or proxy changes the data recipient and trust
  boundary; operators must review that endpoint independently.

Repository maintainers will assess reports and coordinate remediation through
the agreed access-controlled channel. No response or remediation timeframe is
promised.
