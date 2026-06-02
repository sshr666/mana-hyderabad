# Feature Specification: Mana Hyderabad Civic Complaint Platform

**Feature Branch**: `main`
**Created**: 2026-06-02
**Status**: Implemented baseline, active enhancement
**Input**: Existing Mana Hyderabad hackathon project and team request to integrate Spec Kit.

## User Scenarios and Testing

### Primary User Story

A Hyderabad resident can report a civic issue in English, Telugu, Hindi, Urdu, or mixed-language text, add location and optional photo evidence, receive a reference ID, and track the complaint. A municipal administrator can view, filter, map, update, and analyze stored complaints.

### Acceptance Scenarios

1. Given a citizen opens the app, when they select a language and enter a complaint, then the system analyzes the complaint and asks only for missing details.
2. Given a citizen submits a complaint with coordinates, when submission succeeds, then PostgreSQL stores the record and PostGIS stores the geography point.
3. Given a complaint has a photo URL, when an admin opens the complaint detail page, then the image appears with a field-verification note.
4. Given complaints exist near one another, when an admin opens map or detail views, then nearby complaints and hotspots can be displayed.
5. Given a non-English complaint, when analysis runs, then original text remains unchanged and normalized English text is stored separately.

### Edge Cases

- Backend unavailable: frontend shows clear errors and does not silently use mock data unless explicitly enabled.
- GPS denied: citizen can manually enter landmark or choose a map point.
- Map tiles unavailable: manual location submission remains available.
- Translation provider unavailable: complaint submission still works with fallback normalization and human-verification note.
- Photo upload unavailable: citizen can skip photo.

## Requirements

### Functional Requirements

- **FR-001**: Citizens can submit complaints for sanitation, drainage, waterlogging, roads, street lights, water supply, traffic, public health, and other issues.
- **FR-002**: Citizens can provide complaint text, optional photo, coordinates, landmark, and preferred language.
- **FR-003**: Citizens receive a human-readable reference ID and can track status.
- **FR-004**: Admins can view complaint list, detail, analytics, map markers, nearby complaints, and hotspots.
- **FR-005**: Admins can update status, priority, department, assigned team, landmark, locality, ward fields, and internal notes.
- **FR-006**: Dynamic citizen complaint text can be language-detected and normalized to English while preserving original text.
- **FR-007**: Machine translation and AI-assisted analysis must be labeled as requiring human verification.

### Data Requirements

- **DR-001**: Store `original_text` and `normalized_english_text` separately.
- **DR-002**: Store `original_language` and `detected_language` when available.
- **DR-003**: Store coordinates as latitude/longitude and PostGIS geography point when present.
- **DR-004**: Store Cloudinary secure URL in `photo_url`; do not store raw file bytes in PostgreSQL.
- **DR-005**: Reference IDs must be unique, readable, and category-prefixed.

### Non-Functional Requirements

- **NFR-001**: Citizen pages are mobile-first and multilingual.
- **NFR-002**: Admin pages prioritize desktop operational density.
- **NFR-003**: Backend errors must be safe and not expose secrets or raw stack traces.
- **NFR-004**: App must pass frontend build and relevant backend tests before release.
- **NFR-005**: Locality names and reference IDs must not be translated or corrupted.

## Success Criteria

- **SC-001**: A complaint submitted through the frontend is persisted in PostgreSQL and visible in admin views.
- **SC-002**: Admin status changes persist after page refresh.
- **SC-003**: Map endpoints return coordinate-bearing complaints and nearby search returns distance in metres.
- **SC-004**: Non-English analysis returns detected language, normalized English text, and a translated or fallback citizen reply.
- **SC-005**: Repository contains Spec Kit artifacts that guide future phases.

## Assumptions

- BHASHINI credentials may not be available in local development; fallback behavior is required.
- Docker/PostGIS may be unavailable on some contributor machines; DB-backed tests can skip with a clear message.
- Authentication is a later phase and is not part of the current MVP baseline.
