## Summary

Describe the user-visible or engineering outcome and why the change is needed.

## Verification

- [ ] `python -m ruff check .`
- [ ] `python -m ruff format --check .`
- [ ] `python -m unittest discover -s tests -v`
- [ ] `python -m compileall -q main.py weekendia tests`
- [ ] `node --check static/script.js`
- [ ] `node --check static/theme-init.js`
- [ ] Relevant demo-mode and OpenAI-mode behavior was considered.

List any additional manual checks and their results:

## Security and privacy

- [ ] No secret, credential, personal data, or private provider content is included.
- [ ] New external requests, data recipients, permissions, and cost exposure are documented.
- [ ] Error handling and logs do not expose request contents or provider internals.
- [ ] Configuration changes use safe defaults and are reflected in `.env.example`.

## Rights and provenance

- [ ] Every added code snippet, dependency, image, SVG, font, data source, and name has documented provenance.
- [ ] Required licenses and notices are identified without asserting unverified ownership.
- [ ] This change does not weaken the private-release gate in `docs/LICENSE_DECISION.md`.

## Documentation and compatibility

- [ ] User-facing documentation is updated where needed.
- [ ] API or configuration compatibility impact is described below.
- [ ] Screenshots or recordings contain no private data and are included only when their provenance is clear.

Compatibility notes:
