# Changelog

Material changes to Weekendia are recorded here. The project is still private, and no public release history is evidenced in the available records.

## 0.1.0 — 2026-08-08 (private prerelease candidate)

### Added

- Deterministic local demo mode with no external model-provider request.
- Explicit OpenAI Responses provider with bounded output and configurable endpoint settings.
- Responsive planner and result flows with theme controls, keyboard support, status announcements, copy, and text download actions.
- Characterization and hardening tests for validation, provider behavior, API errors, request controls, and security headers.
- Private-evaluation documentation, governance guidance, validation records, and decision records.

### Changed

- Separated configuration, validation and prompt construction, provider adapters, and request guards from HTTP routing.
- Made process-level environment variables take precedence over the optional `.env` file.
- Replaced simulated loading percentages with status language tied to request state.
- Improved narrow-viewport layout, touch targets, high-contrast form focus, error recovery, and reduced-motion handling.
- Removed the blocking ornamental page loader, consolidated validation announcements, rendered numbered plan sequences as ordered lists, and applied saved theme preferences before first paint.
- Made health output provider-minimal and limited it to local configuration state.

### Security

- Prevented default persistent Response-object storage with `store=False`, documented residual provider-state and retention limits, and removed automatic provider retries.
- Added input length and body-size limits, safe JSON errors, request identifiers, no-store API caching, and conservative browser headers.
- Added per-process rate and concurrency guards plus fetch-metadata rejection for cross-site POST requests.
- Sanitized provider failure logs and restricted Flask debug mode to loopback bindings.
- Kept secrets and local environment files outside the tracked source set.

### Known limitations

- Project rights, provenance, naming clearance, and license selection remain unresolved; the repository must stay private.
- Request controls are process-local, and the application has no authentication or approved production deployment design.
- Plans do not contain verified live prices, opening hours, availability, weather, transport, or booking data.
