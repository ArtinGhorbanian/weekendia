# Validation Record

> Scope: the current private-evaluation build. These checks are point-in-time engineering evidence, not certification, a security guarantee, a performance service level, or proof of production readiness.

## Verified results

| Area | Result |
| --- | --- |
| Python runtime | Python 3.12 |
| Server tests | 26 of 26 `unittest` cases passed |
| Python lint | Ruff `E4`, `E7`, `E9`, `F`, `I`, and `B` checks clean |
| Python formatting | Ruff format check clean |
| Python syntax | `compileall` completed successfully |
| JavaScript syntax | `node --check static/script.js` and `node --check static/theme-init.js` completed successfully |
| Desktop browser | Load, saved theme, demo focus/escape, validation, loading, submission, semantic result, copy, download, failed retry, and reset flows exercised at 1440 by 900 |
| Mobile and tablet browser | 375 by 812, 390 by 844, and 768 by 1024; `scrollWidth` matched each viewport; minimum measured control target 44 px; minimum input font 16 px; zero unexpected console, page, request, or HTTP errors |
| Light-theme contrast | Minimum measured design-token contrast 4.84:1 |
| Light-theme form focus | Three-pixel `#006f59` outline; minimum 5.61:1 contrast across the sampled light surfaces |
| Dependency audit | Resolved 26-package environment: no known vulnerabilities reported by `pip-audit`; unhashed-lock warning remains |
| Secret scan | Source scan clean outside local `.env` |
| Rendered root | Final rendered HTML: 31,414 bytes |
| Warm test-client timing | Mean 2.44 ms across 20 requests |

Captured browser evidence: [desktop planner](screenshots/weekendia-desktop.png),
[mobile planner](screenshots/weekendia-mobile.png),
[desktop result](screenshots/weekendia-result.png), and
[mobile result](screenshots/weekendia-mobile-result.png).

Timing is a local warm Flask test-client measurement, not browser latency, provider latency, throughput, capacity, or a production benchmark. The contrast result covers the measured token pairs, not every rendered state or a formal WCAG audit. “No known vulnerabilities” is limited to the tool, database, versions, and dependency set examined at that time.

## Evidence boundaries

The validation did not include:

- a live OpenAI API call, credential, selected model, custom endpoint, or proxy;
- an automated axe accessibility scan or formal assistive-technology audit;
- physical devices, mobile landscape, or an exhaustive browser matrix;
- load, soak, concurrency-topology, resilience, or provider-cost testing;
- penetration testing or a deployed edge/proxy/TLS chain;
- legal review, source/asset provenance verification, license approval, or name/logo clearance.

## Interpretation

The results support local private evaluation of the checked artifact. They do not establish production readiness, compliance, accessibility conformance, internet-exposure safety, availability, factual accuracy, public distribution rights, or brand clearance.

Any change to code, dependencies, environment, browser support, provider configuration, assets, deployment, or repository visibility requires proportionate revalidation. The remaining gates are tracked in the [Release Checklist](RELEASE_CHECKLIST.md), with trust boundaries in the [Security Model](SECURITY_MODEL.md).
