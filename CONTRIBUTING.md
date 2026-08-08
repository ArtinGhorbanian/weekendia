# Contributing to Weekendia

Weekendia is currently a private-evaluation project. Contributions are limited to collaborators who already have authorized repository access, and accepting a change does not alter the project's unresolved ownership, provenance, or licensing status.

## Before starting

1. Open or reference a private issue describing the problem, intended outcome, and affected area.
2. Confirm that any code, text, design, or asset you plan to submit is original to you or covered by permission compatible with the project's eventual licensing decision.
3. Do not submit copied starter-project material, event or employer work, third-party media, personal data, credentials, or generated assets whose usage terms have not been reviewed.
4. Keep scope narrow. Separate behavior changes, refactors, dependency updates, and documentation work when they can be reviewed independently.

If origin or permission is uncertain, stop and record the question instead of adding the material.

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.lock -r requirements-dev.txt
$env:WEEKENDIA_MODE = "demo"
python main.py
```

Use demo mode for routine development so tests and interface work do not submit form data to an external provider. Never place a real credential in committed files, fixtures, screenshots, logs, or issue content.

## Change standards

- Preserve the explicit distinction between deterministic demo output and externally processed OpenAI output.
- Keep server-side validation authoritative; browser validation is an additional usability layer.
- Escape untrusted provider and user content before inserting it into the document.
- Maintain keyboard access, focus visibility, semantic labels, live announcements, responsive behavior, and reduced-motion support.
- Do not add telemetry, persistent plan storage, external requests, or new data collection without an explicit privacy and security review.
- Keep errors useful to users while excluding secrets, prompts, submitted details, provider URLs, and raw exception messages from logs.
- Update tests and documentation whenever configuration, API behavior, security boundaries, or user flows change.

## Required checks

Run these from the repository root:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q main.py weekendia tests
python -m ruff check .
python -m ruff format --check .
node --check static/script.js
node --check static/theme-init.js
```

Also exercise the affected browser flow at desktop and narrow mobile widths. OpenAI-provider calls should be mocked unless an authorized integration test explicitly requires them.

## Commits and private pull requests

Use a short, imperative commit subject that describes one coherent change. A private pull request should include:

- the user or engineering problem;
- the chosen approach and important tradeoffs;
- tests run and their outcomes;
- screenshots for visible changes;
- privacy, security, accessibility, dependency, and rights implications;
- remaining limitations or follow-up work.

Do not claim performance, security, accessibility, or product outcomes without reproducible evidence. Do not mark a check complete when it was skipped; state why it could not run.

## Review and acceptance

Review may request changes for correctness, maintainability, user safety, privacy, accessibility, provenance, or repository-scope reasons. Substantive outside contributions should not be accepted until authorized maintainers establish appropriate contribution terms. Repository access and contribution acceptance do not grant a project-wide license.

All collaboration is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). For a vulnerability, follow [SECURITY.md](SECURITY.md) rather than opening a general issue.
