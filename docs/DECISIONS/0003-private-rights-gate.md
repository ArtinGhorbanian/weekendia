# ADR 0003: Keep the Repository Private Until Rights Are Cleared

- Status: Accepted
- Date: 2026-08-08
- Scope: Repository visibility, licensing, branding, releases, and promotion

## Context

The available materials do not establish complete source and asset provenance, original ownership, contributor permissions, or authority to apply a project license. There is no approved project `LICENSE`. The “Weekendia” name and current logo/assets have no documented clearance in the repository. No competition, employer, client, course, starter-repository, or other origin disclosure should be invented in the absence of evidence.

AIONEX is used only as the maintainer/project identity for this private evaluation. It must not be represented as a verified owner, original author, or rights holder without supporting records.

## Decision

Keep the repository private. Do not add a project license by assumption, publish a demo, distribute a package, make screenshots/promotional assets public, create a public release, or make ownership/endorsement claims.

A private prerelease or internal handoff may be used only if it remains access-controlled, contains no secrets, is labeled private evaluation, and carries this unresolved-rights notice.

## Clearance required

Before changing the gate, obtain and record:

1. original repository/source identity and chain of custody;
2. every contributor and the permission or inbound license for each contribution;
3. provenance and reuse rights for icons, SVGs, images, fonts, copy, and other assets;
4. exact dependency licenses and required notices;
5. authorized selection of a compatible project license;
6. trademark/name/domain/logo clearance;
7. any required event, employer, client, course, starter-code, or competition disclosure;
8. written authorization for the intended public distribution and promotional scope.

## Consequences

- Technical work can continue in the private repository.
- Documentation must use neutral, evidence-based language.
- Public discoverability, licensing, launch, portfolio use, and external client reuse remain blocked.
- Technical readiness cannot override missing rights or brand authorization.
- If provenance reveals incompatible terms, affected source or assets must be replaced or removed before release.

## Verification

The release checklist begins with this hard gate, and the repository has no project `LICENSE`. The current status is also summarized in [License Decision](../LICENSE_DECISION.md). This is a risk-control decision based on missing evidence, not a legal opinion or a conclusion that infringement occurred.

## Reconsider when

Only an authorized reviewer may supersede this ADR, after the clearance evidence above is recorded and any required remediation is complete. The superseding decision must identify the approved license, branding scope, repository visibility, distribution channels, notices, and accountable rights holder.

