# Mana Hyderabad Constitution

Version: 1.0.0
Last updated: 2026-06-02

This constitution governs Spec Kit driven work for Mana Hyderabad. It should be treated as the project memory for future `/speckit.*` workflows.

## 1. Civic Usefulness First

Every feature must make it easier for residents to report civic issues or for municipal teams to review and act on complaints. Do not add decorative functionality that does not improve reporting, tracking, triage, accessibility, operations, or safety.

## 2. Preserve Citizen Trust and Language

Original citizen text must never be overwritten. Store the original message and the normalized English text separately. Preserve Hyderabad locality names, landmarks, reference IDs, dates, and proper nouns across translation, display, and admin workflows.

## 3. Human Verification for AI Signals

AI, translation, image analysis, duplicate detection, and urgency scoring are assistive signals only. The product must never present machine output as confirmed evidence, resolved status, or official municipal action without human review.

## 4. Accessibility and Mobile-First Citizen UX

Citizen flows must be mobile-first, keyboard accessible where practical, multilingual, and resilient when GPS, map tiles, camera upload, translation, or backend services fail. A citizen must always have a manual path to submit a useful complaint.

## 5. Operational Clarity for Admins

Admin experiences must be dense, scannable, and action-oriented. Tables, filters, maps, status updates, nearby complaints, and hotspot summaries must clearly distinguish stored facts from recommendations or fallback outputs.

## 6. Backend Boundaries and Data Integrity

Frontend API calls stay in `lib/api-client.ts`. Backend route handlers delegate business logic to services and repositories. Database schema changes require Alembic migrations. PostgreSQL/PostGIS persistence must remain durable across restarts.

## 7. Security and Privacy Baseline

Never commit secrets, `.env` files, uploaded citizen evidence, database dumps, or provider credentials. Do not expose BHASHINI, Cloudinary, database, or future AI keys to the frontend. Validate uploads, text length, coordinates, enum values, and pagination inputs server-side.

## 8. Test and Build Gate

Before completion, run the smallest useful set of checks for the changed area. For broad changes, run:

- `npm run format:check`
- `npm run lint`
- `npm test`
- `npm run build`
- `cd mana-hyderabad-backend && .venv/bin/pytest`

Database-backed tests may skip when local PostGIS is unavailable, but this must be reported.

## 9. Phase Discipline

Do not add future-phase capabilities unless explicitly requested. In particular, keep LLM extraction, speech, computer vision, pgvector duplicate detection, authentication, and production deployment changes scoped to their own phases.

## 10. Documentation Is Part of Delivery

Any user-visible or operator-visible behavior change must update README, backend README, specs, or user documentation as appropriate. Spec Kit artifacts should be updated before or alongside implementation when a new phase starts.

## Current Phase Map

- Phase 1: Frontend prototype
- Phase 2: FastAPI backend foundation
- Phase 3: PostgreSQL/PostGIS persistence
- Phase 4: Frontend-backend integration
- Phase 5: File uploads
- Phase 6: Interactive mapping and geospatial features
- Phase 7: Multilingual translation support
- Next recommended phase: Speech input using BHASHINI ASR
