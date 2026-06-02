# Data Model: Mana Hyderabad Platform

## Complaint

Represents one citizen-submitted civic issue.

### Identity

- `id`: UUID primary key
- `reference_id`: unique human-readable ID, for example `HYD-SAN-0142`

### Citizen Text

- `original_text`: original message exactly as submitted
- `normalized_english_text`: translated or normalized English text
- `original_language`: selected language code, one of `en`, `te`, `hi`, `ur`
- `detected_language`: detected language or mixed language label, such as `te-en`

### Classification

- `category`: enum such as `SANITATION`, `DRAINAGE`, `WATERLOGGING`, `ROADS`, `OTHER`
- `subcategory`: operational subtype
- `department`: suggested or assigned department
- `priority`: `LOW`, `MEDIUM`, `HIGH`, or `EMERGENCY`
- `status`: `SUBMITTED`, `UNDER_REVIEW`, `ASSIGNED`, `IN_PROGRESS`, or `RESOLVED`

### Geospatial

- `latitude`: nullable float
- `longitude`: nullable float
- `location`: nullable PostGIS `GEOGRAPHY(Point, 4326)`
- `landmark`: citizen-provided landmark
- `locality`: Hyderabad locality name
- `ward_name`: optional future ward label
- `ward_number`: optional future ward number

### Media and Admin

- `photo_url`: Cloudinary secure URL for primary complaint image
- `assigned_team`: optional admin field team
- `internal_note`: admin-only note

### AI and Verification

- `analysis_source`: `FALLBACK_RULES`, `LLM`, or `MANUAL`
- `requires_human_verification`: boolean
- `reasoning_summary`: short operational explanation only

### Audit

- `created_at`
- `updated_at`

## Future Entities

These are intentionally not implemented yet:

- `ComplaintImage`: for multiple photos per complaint
- `CitizenProfile`: for authenticated users
- `OfficerProfile`: for admin/field roles
- `WardBoundary`: GeoJSON or PostGIS polygon mapping
- `DuplicateCandidate`: pgvector-backed semantic duplicate workflow
- `SpeechTranscript`: BHASHINI ASR input metadata
