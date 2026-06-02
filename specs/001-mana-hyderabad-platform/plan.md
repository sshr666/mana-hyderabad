# Implementation Plan: Mana Hyderabad Civic Complaint Platform

**Branch**: `main`
**Spec**: `specs/001-mana-hyderabad-platform/spec.md`
**Date**: 2026-06-02

## Summary

Mana Hyderabad is implemented as a small monorepo with a Next.js frontend and FastAPI backend. The current baseline supports live complaint submission, PostgreSQL/PostGIS persistence, uploads, geospatial admin views, and multilingual translation scaffolding. Spec Kit is integrated through `.specify/` project memory and `specs/` artifacts for future phase planning.

## Constitution Check

- Civic usefulness: Complaint reporting, tracking, mapping, and admin triage are the core workflows.
- Original data preservation: Original text and normalized English text are separate fields.
- Human verification: Translation/image/analysis outputs are treated as assistive.
- Accessibility: Citizen flow is mobile-first with manual fallbacks for GPS/photo/map.
- Security/privacy: Secrets remain backend-only; `.env` files are ignored.
- Test/build gate: Frontend and backend checks are documented and runnable.

## Technical Context

- Frontend: Next.js App Router, TypeScript, Tailwind CSS, shadcn-style components, next-intl, MapLibre GL JS, Recharts.
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic.
- Database: PostgreSQL with PostGIS geography point storage.
- Uploads: Cloudinary through backend-only upload endpoint.
- Translation: BHASHINI provider abstraction with safe fallback and IndicTrans2 stub.
- Tests: Vitest smoke tests and pytest backend tests.

## Implementation Scope

### In Scope

- Spec Kit project memory and templates.
- Baseline feature spec, plan, task list, research notes, data model notes.
- README and agent guidance updates for Spec Kit usage.

### Out of Scope

- Running `specify init` against the existing repo if the CLI is not installed.
- Adding new app functionality beyond Spec Kit artifacts.
- Adding speech, LLM extraction, computer vision, pgvector, authentication, or production deployment.

## Data Model

Primary model: `Complaint`.

Key fields:

- `reference_id`
- `original_text`
- `normalized_english_text`
- `original_language`
- `detected_language`
- `category`
- `subcategory`
- `priority`
- `status`
- `latitude`
- `longitude`
- `location`
- `landmark`
- `locality`
- `ward_name`
- `ward_number`
- `photo_url`
- `department`
- `assigned_team`
- `internal_note`
- `analysis_source`
- `requires_human_verification`

## API Contract

Existing API groups:

- `/api/health`
- `/api/complaints/*`
- `/api/admin/*`
- `/api/uploads/images`
- `/api/translation/*`

Spec Kit does not change API contracts. Future phases should update `spec.md`, `plan.md`, and `tasks.md` before implementation.

## Risks and Mitigations

- CLI drift: The repo stores project-local Spec Kit artifacts even if a contributor has no CLI installed.
- Artifact staleness: Future phase tasks must update the matching spec files.
- Over-scoping: Constitution explicitly blocks future-phase features unless requested.

## Validation Plan

- Confirm `.specify/memory/constitution.md` exists.
- Confirm `specs/001-mana-hyderabad-platform/` contains `spec.md`, `plan.md`, `tasks.md`, `research.md`, and `data-model.md`.
- Run `npm run format:check`.
- Run `npm run build`.
