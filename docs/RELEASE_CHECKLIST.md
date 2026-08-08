# Release Checklist

## Current gate

**Status: private evaluation only. Public release is blocked.**

No verified record establishes source/asset ownership and provenance, contributor permissions, a distributable project license, or name/logo clearance. There is no `LICENSE`, and one must not be added by assumption. AIONEX is only the maintainer/project identity for this private evaluation.

## Evidence legend

- `[x]` verified against the current private-evaluation artifact.
- `[ ]` required or not yet verified.
- A checked technical item does not override an unchecked rights, privacy, security, or deployment gate.

## 1. Rights and release authority

- [ ] Identify the original source and every contributor.
- [ ] Record contributor permission or inbound license for each contribution.
- [ ] Record provenance and reuse rights for SVG, icon, image, font, copy, and other assets.
- [ ] Complete dependency notice review.
- [ ] Choose and approve a project license with authorized rights holders.
- [ ] Complete name, trademark, domain, and logo clearance for “Weekendia” and any replacement brand.
- [ ] Document whether any event, employer, client, course, starter-repository, or competition disclosure is required.
- [ ] Obtain written public-release authorization.
- [x] Keep the repository private while these items remain unresolved.

**Stop condition:** if any item above is unknown, do not make the repository, package, screenshots, social preview, demo URL, release, or promotional material public.

## 2. Reproducibility and code quality

- [x] Install and execute with Python 3.12 in the validated environment.
- [x] Run all 26 `unittest` cases successfully.
- [x] Run Ruff selected checks and format verification.
- [x] Run Python bytecode compilation and JavaScript syntax validation.
- [x] Verify deterministic demo behavior without a provider call.
- [ ] Repeat checks from a clean clone of the exact candidate commit.
- [ ] Record commit SHA, tool versions, commands, and timestamp in release evidence.

Exact current results and limits are in [Validation](VALIDATION.md).

## 3. Product and accessibility review

- [x] Exercise principal desktop, 375/390-pixel mobile, and 768-pixel tablet flows.
- [x] Check mobile horizontal overflow, control target size, and input font floor.
- [x] Check the measured light-theme token contrast floor used in validation.
- [x] Confirm zero console errors during the recorded browser flow.
- [ ] Run an automated accessibility scanner such as axe against all states.
- [ ] Complete keyboard-only and screen-reader testing with documented results.
- [ ] Test physical mobile devices, landscape, zoom, high contrast, and supported browsers.
- [ ] Commission formal accessibility review before making a conformance claim.

## 4. Privacy and security

- [x] Keep `.env` and credential-shaped files ignored.
- [x] Scan repository source outside `.env` for secret patterns.
- [x] Use `store=False` for OpenAI Responses API requests.
- [x] Disclose external processing and the default abuse-monitoring retention caveat.
- [x] Return private no-store headers for API responses.
- [x] Bound payloads, fields, output, timeout, retries, local rate, and local concurrency.
- [x] Keep client errors and application log messages free of prompt/body/credential values.
- [ ] Rotate any credential that may have been stored in a synchronized plaintext `.env` or otherwise exposed.
- [ ] Add authentication or approve and own a documented anonymous-access model.
- [ ] Add shared edge limits, per-user quotas, provider spend ceilings, and emergency shutdown.
- [ ] Deploy behind TLS and a production WSGI server with a reviewed proxy-trust policy.
- [ ] Define privacy notice, lawful basis/consent, retention, deletion, and incident response.
- [ ] Complete SAST, DAST, penetration, and threat-model review of the candidate deployment.

See [Security Model](SECURITY_MODEL.md). Process-local guards alone are never sufficient evidence for internet exposure.

## 5. Dependency and supply chain

- [x] Audit the resolved validation environment with no known vulnerabilities reported.
- [ ] Resolve or formally accept the unhashed-lock warning.
- [ ] Generate a clean, reproducible lock with hashes or another approved integrity mechanism.
- [ ] Verify licenses and notices for the exact resolved dependency graph.
- [ ] Enable least-privilege CI and dependency update review on the private repository.
- [ ] Review generated artifacts and source maps for embedded secrets or local paths.

## 6. Provider and real-world accuracy

- [x] Keep the public health shape provider-minimal and avoid reachability claims.
- [x] Make demo mode deterministic, local, and explicit about missing live data.
- [ ] Validate intended OpenAI model access in a controlled non-production environment without logging sensitive prompts.
- [ ] Define provider error, quota, cost, latency, and deprecation ownership.
- [ ] License, source, timestamp, and attribute any future live data.
- [ ] Add a human escalation process for safety, access, booking, and factual disputes.

## 7. Deployment and operations

- [ ] Define supported topology, production server, health/readiness semantics, TLS, backups, and rollback.
- [ ] Add structured privacy-safe metrics, alerting, capacity tests, and runbooks.
- [ ] Perform load and failure testing against the release topology.
- [ ] Verify security headers through the actual edge and proxy chain.
- [ ] Document data residency, subprocesses, retention, and deletion in the deployed system.
- [ ] Obtain operational owner sign-off.

## 8. Private evaluation handoff

- [ ] Confirm repository visibility is private.
- [ ] Confirm the candidate contains no `.env`, key, token, local database, log, or cache artifact.
- [ ] Confirm screenshots and documentation contain only fictional/non-sensitive data.
- [ ] Link the exact validation record and unresolved-risk list.
- [ ] Label any tag or release as private evaluation or prerelease.
- [ ] Re-run this checklist if code, dependencies, provider settings, assets, branding, deployment, or visibility changes.

## Decision record

The governing publication decision is [ADR 0003: Keep the repository private until rights are cleared](DECISIONS/0003-private-rights-gate.md).
