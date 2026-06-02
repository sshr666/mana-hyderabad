# Research Notes: Mana Hyderabad Platform

## Spec Kit Integration Decision

The team requested Spec Kit integration using the workshop cheatsheet workflow:

1. Constitution
2. Specify
3. Clarify
4. Plan
5. Tasks
6. Analyze/checklist as optional quality gates
7. Implement

Because Mana Hyderabad already exists as a working brownfield project, the repo uses project-local Spec Kit artifacts instead of reinitializing or moving the app.

## Why Project-Local Artifacts

- Avoids rewriting the working Next.js/FastAPI repo.
- Gives future phases durable specs and task lists.
- Keeps CLI installation optional for contributors.
- Matches the expected `.specify/` and `specs/` structure from the workshop cheatsheet.

## Key Product Decisions

- Preserve citizen language and original message.
- Keep AI and translation assistive, not authoritative.
- Keep geospatial features explainable: radius search, locality grouping, hotspots.
- Prioritize a manual fallback whenever provider services fail.

## Key Technical Decisions

- Next.js frontend remains at repo root.
- FastAPI backend remains in `mana-hyderabad-backend/`.
- PostgreSQL/PostGIS remains the persistence layer.
- Cloudinary remains the MVP image storage provider.
- BHASHINI remains the primary translation/speech provider path.
- IndicTrans2 remains a future fallback option.

## Open Questions for Future Specs

- Should citizens authenticate before tracking complaints?
- Which official ward boundary dataset should be used?
- What BHASHINI production access constraints apply?
- Should duplicate detection be admin-confirmed only?
- What SLA/status workflow should municipal stakeholders expect?
