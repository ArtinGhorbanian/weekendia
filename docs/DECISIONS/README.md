# Architecture Decision Records

These records explain decisions in the current private-evaluation build. “Accepted” means implemented or governing this repository; it does not imply production approval, legal clearance, or public-release authority.

| ADR | Status | Decision |
| --- | --- | --- |
| [0001](0001-provider-boundary.md) | Accepted | Isolate plan generation behind an explicit provider boundary |
| [0002](0002-disable-response-storage.md) | Accepted | Do not persist Response objects by default; document residual state and retention |
| [0003](0003-private-rights-gate.md) | Accepted | Keep the repository private until rights and brand clearance are documented |

## Status meanings

- **Proposed:** under review and not yet governing.
- **Accepted:** implemented or currently governing.
- **Superseded:** replaced by a linked later decision.
- **Rejected:** considered and not adopted.

Future ADRs should state context, decision, consequences, verification, and conditions for reconsideration. They must distinguish current behavior from planned work and must not convert unknown legal or security facts into assumptions.

Related system documentation:

- [Architecture](../ARCHITECTURE.md)
- [Technical Deep Dive](../TECHNICAL_DEEP_DIVE.md)
- [Security Model](../SECURITY_MODEL.md)
- [Release Checklist](../RELEASE_CHECKLIST.md)
