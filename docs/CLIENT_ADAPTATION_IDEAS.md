# Client Adaptation Ideas

> Internal planning material only. None of these ideas is implemented or committed. Any client adaptation must first establish rights to the source and assets, choose a license, and clear the product name and logo. AIONEX is only the private-evaluation maintainer/project identity.

## Adaptation candidates

| Idea | Possible adaptation | Required safeguards and evidence | Status |
| --- | --- | --- | --- |
| Organization outing planner | Approved activity categories, policy reminders, configurable group constraints | Authentication, administrator ownership, employee privacy review, spend controls, accessibility policy | Concept only |
| Destination or venue guide | Licensed inventory, operating hours, prices, booking links, and availability | Data licenses, freshness indicators, source attribution, fallback behavior, commercial/legal review | Concept only |
| Community weekend guide | Curated low-cost, family, quiet, or accessible options | Editorial workflow, safeguarding rules, moderation, verified accessibility data, local consent | Concept only |
| Hospitality concierge | Property-specific recommendations and transport handoff | Tenant isolation, brand approval, service-level ownership, provider quotas, human escalation | Concept only |
| Fully local planning aid | Rules/templates tailored to a private knowledge base without external generation | Approved local content, update workflow, device/browser security, documented data lifecycle | Concept only |

## Reusable extension points

The current provider protocol can support another deterministic or generated-plan implementation without changing the route contract. `Settings` can be extended for a separately reviewed integration, and the form/result boundary can accept structured enrichment after server validation.

These are architectural extension points, not proof that a third-party service is compatible, licensed, secure, or accurate.

## Adaptation principles

1. Keep demo, generated, and live-data capabilities visibly distinct.
2. Display source and freshness for any licensed live fact.
3. Ask only for data needed to plan; avoid names, exact addresses, health data, and credentials by default.
4. Put authentication, tenant isolation, quotas, and spend limits in place before shared access.
5. Preserve keyboard, responsive, reduced-motion, contrast, error-recovery, and plain-language behavior.
6. Provide a human escalation path for safety, access, booking, or policy questions.
7. Test local cultural, legal, accessibility, safeguarding, and language requirements with qualified reviewers.
8. Do not reuse the current name, logo, or visual assets externally until clearance is documented.

## Discovery questions

- Who is responsible for recommendations and incident response?
- Which data sources are contractually permitted, and how fresh must they be?
- What personal data is actually necessary, who can access it, and when is it deleted?
- Is anonymous use allowed, and who owns abuse and provider spend?
- Which safety, accessibility, child-protection, employment, or consumer rules apply?
- What evidence is required before a recommendation may be described as verified?

Any resulting scope should update the [Architecture](ARCHITECTURE.md), [Security Model](SECURITY_MODEL.md), and [Release Checklist](RELEASE_CHECKLIST.md) before implementation.
