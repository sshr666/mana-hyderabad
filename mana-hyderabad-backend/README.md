# Mana Hyderabad Backend

FastAPI backend foundation for the Mana Hyderabad civic complaint platform.

This phase implements PostgreSQL/PostGIS-backed complaint storage, human-readable reference IDs, tracking, admin filtering, status updates, map points, nearby complaint radius search, locality and ward grouping, basic hotspot detection, Cloudinary image uploads, multilingual translation support, speech input scaffolding, Alembic migrations, seed data, and pytest coverage.

It intentionally does not include LLMs, computer vision, authentication, or pgvector semantic search yet.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## Environment Variables

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/mana_hyderabad
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
CLOUDINARY_UPLOAD_FOLDER=mana-hyderabad/complaints
MAX_UPLOAD_SIZE_MB=8
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp
ENABLE_SPEECH_INPUT=true
ENABLE_TTS_RESPONSES=false
BHASHINI_ASR_PIPELINE_ID=
BHASHINI_TTS_PIPELINE_ID=
BHASHINI_SPEECH_CONFIG_URL=
BHASHINI_SPEECH_TIMEOUT_SECONDS=30
BHASHINI_SPEECH_MAX_RETRIES=2
BHASHINI_SPEECH_CACHE_TTL_SECONDS=3600
MAX_AUDIO_SIZE_MB=10
MAX_AUDIO_DURATION_SECONDS=120
ALLOWED_AUDIO_TYPES=audio/webm,audio/wav,audio/mpeg,audio/mp4,audio/ogg
ENABLE_LLM_ANALYSIS=true
LLM_PROVIDER=openai_compatible
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
LLM_TIMEOUT_SECONDS=20
LLM_MAX_RETRIES=2
LLM_TEMPERATURE=0
LLM_MAX_OUTPUT_TOKENS=800
ENABLE_RULE_FALLBACK=true
ENABLE_LLM_JSON_MODE=true
```

Credentials are loaded through `app/config.py`; do not hardcode them in Python files.

## Verify Health

[http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

```bash
curl http://127.0.0.1:8000/api/health
```

## Swagger Docs

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Database Verification

```bash
psql -h localhost -U postgres -d mana_hyderabad
```

```sql
SELECT PostGIS_Version();
```

## Migration Commands

```bash
alembic upgrade head
alembic downgrade -1
```

Initial migration:

```text
20260530_0001_create_complaints
```

The migration enables:

- `postgis`
- `pgcrypto`
- `complaints` table
- unique reference ID index
- category, priority, status, locality, created-at indexes
- GIST spatial index on `location`

## API Endpoints

```text
GET    /api/health
POST   /api/complaints/analyse
POST   /api/complaints
GET    /api/complaints/{reference_id}
GET    /api/admin/complaints
PATCH  /api/admin/complaints/{reference_id}
GET    /api/admin/map-points
GET    /api/admin/nearby-complaints
GET    /api/admin/hotspots
GET    /api/admin/analytics
POST   /api/uploads/images
DELETE /api/uploads/images
POST   /api/translation/detect-language
POST   /api/translation/translate
POST   /api/speech/transcribe
POST   /api/speech/synthesize
```

## LLM Analysis Flow

Complaint analysis uses the multilingual normalization layer and a configurable OpenAI-compatible LLM endpoint:

```text
Citizen complaint
→ translation
→ normalized English
→ LLM structured extraction
→ Pydantic validation
→ deterministic safety guardrails
→ keyword fallback when needed
→ frontend review
```

The LLM is advisory only. Every response is marked as requiring field verification. The model cannot resolve complaints, promise response times, merge duplicates, permanently assign teams, or write directly to the database without validation.

## LLM Provider Setup

Configure either a hosted OpenAI-compatible API or a local instruct model exposed through an OpenAI-compatible endpoint:

```env
ENABLE_LLM_ANALYSIS=true
LLM_PROVIDER=openai_compatible
LLM_API_KEY=
LLM_BASE_URL=http://127.0.0.1:11434
LLM_MODEL=
LLM_TIMEOUT_SECONDS=20
LLM_MAX_RETRIES=2
LLM_TEMPERATURE=0
LLM_MAX_OUTPUT_TOKENS=800
ENABLE_RULE_FALLBACK=true
ENABLE_LLM_JSON_MODE=true
```

`LLM_API_KEY` is optional for local endpoints that do not require authentication. Never expose it to the frontend.

Safety behavior:

- Complaint text is treated as untrusted data.
- LLM output must be strict JSON and pass Pydantic validation.
- Unknown categories, priorities, departments, malformed JSON, empty responses, timeouts, 429s, and 5xx responses fall back to deterministic keyword rules.
- Guardrails can raise priority or correct departments for electrical hazards, open manholes, severe flooding, contaminated drinking water, and garbage blocking drains.
- Emergency priority is never reduced automatically.

## Map Setup

From the frontend root, configure the MapLibre style URL:

```env
NEXT_PUBLIC_MAP_STYLE_URL=https://demotiles.maplibre.org/style.json
```

The default development style is suitable for local demos. Add a production tile provider before public deployment if required by your usage limits.

## Citizen Location Features

- Use current location only after the citizen clicks the button.
- Choose a point on the map.
- Drag the marker to refine coordinates.
- Enter a landmark manually at all times.
- Submit landmark-only complaints when GPS is unavailable.
- Permission denial and timeout states show friendly fallback guidance.

## Admin Map Features

- Live complaint markers from `/api/admin/map-points`.
- MapLibre GeoJSON source with marker clustering.
- Category, priority, and status filters.
- Reset and refresh controls.
- Hotspot overlay from `/api/admin/hotspots`.
- Optional heatmap view using live complaint points.
- Fallback complaint list when map data is unavailable.

## Future Geospatial Layers

TODO: Add GHMC ward boundary GeoJSON for point-in-polygon ward assignment.

TODO: Add recurring-hotspot fields such as `firstReportedAt`, `latestReportedAt`, `repeatedComplaintCount`, `averageResolutionTime`, and `recurrenceWindowDays`.

TODO: Add drainage risk-zone overlays using flood-prone areas, nala boundaries, rainfall layers, and complaint density.

## Cloudinary Setup

1. Create a Cloudinary account.
2. Copy `.env.example` to `.env`.
3. Add `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET`.
4. Keep `CLOUDINARY_UPLOAD_FOLDER=mana-hyderabad/complaints` unless you want a different folder.
5. Restart FastAPI after changing environment variables.

Never expose `CLOUDINARY_API_SECRET` to the frontend. Browser uploads go to FastAPI first, and FastAPI uploads to Cloudinary.

## Quick API Test

Submit:

```bash
curl -X POST http://127.0.0.1:8000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{
    "originalText": "Garbage is blocking the drain near Madhapur Metro.",
    "normalizedEnglishText": "Garbage is blocking the drain near Madhapur Metro.",
    "originalLanguage": "en",
    "detectedLanguage": "en",
    "category": "SANITATION",
    "subcategory": "GARBAGE_BLOCKING_DRAIN",
    "department": "MULTI_DEPARTMENT",
    "priority": "HIGH",
    "latitude": 17.4483,
    "longitude": 78.3915,
    "landmark": "Near Madhapur Metro",
    "locality": "Madhapur",
    "requiresHumanVerification": true,
    "analysisSource": "MANUAL"
  }'
```

Nearby search:

```bash
curl "http://127.0.0.1:8000/api/admin/nearby-complaints?latitude=17.4483&longitude=78.3915&radius_meters=200&category=SANITATION"
```

Hotspots:

```bash
curl "http://127.0.0.1:8000/api/admin/hotspots?radius_meters=300&min_complaints=3"
```

Map points with filters:

```bash
curl "http://127.0.0.1:8000/api/admin/map-points?category=SANITATION&priority=HIGH"
```

Upload image:

```bash
curl -X POST "http://127.0.0.1:8000/api/uploads/images" \
  -H "accept: application/json" \
  -F "file=@test-assets/sample-garbage.jpg"
```

## Seed Data

```bash
python -m app.seed
```

The seed inserts 20+ realistic Hyderabad complaints across Madhapur, Gachibowli, Hitech City, Charminar, Kukatpally, Ameerpet, Jubilee Hills, Begumpet, Secunderabad, Kondapur, Banjara Hills, Mehdipatnam, Tolichowki, Miyapur, and Tarnaka.

The data includes sanitation clusters, drainage/waterlogging clusters, pothole clusters, isolated complaints, multiple languages, ward fields, and valid coordinates.

## Safe Development Reset

Development only:

```bash
python -m app.seed --reset
```

For a full database reset:

```bash
alembic downgrade -1
alembic upgrade head
python -m app.seed
```

## Test

```bash
pytest
```

Database-backed tests require PostgreSQL/PostGIS to be running and migrations applied. If the database is unavailable, those tests are skipped with a setup hint.

## Run Verification Script

Start the API first:

```bash
uvicorn app.main:app --reload
```

Then run:

```bash
python scripts/verify_database_flow.py
python scripts/verify_geospatial_flow.py
python scripts/verify_upload_flow.py
python scripts/verify_translation_flow.py
python scripts/verify_speech_flow.py
python scripts/verify_llm_analysis_flow.py
```

The database script checks health, submits a complaint, retrieves it, updates status, lists admin complaints, fetches map points, runs nearby search, fetches hotspots, and prints analytics keys.

The upload script posts `test-assets/sample-garbage.jpg` to `/api/uploads/images`, submits a complaint with the returned `photoUrl`, retrieves the complaint, and verifies the stored `photoUrl`.

## Translation Architecture

Dynamic citizen text uses a backend-only translation layer:

```text
Citizen text
→ language detection
→ locality preservation
→ BHASHINI translation when configured
→ English normalization
→ complaint analysis
→ translated citizen reply
```

Supported languages for Phase 7:

- English (`en`)
- Telugu (`te`)
- Hindi (`hi`)
- Urdu (`ur`)
- Mixed-language input such as Telugu-English and Hindi-English
- Romanised input with best-effort heuristics

Static frontend labels remain in `messages/*.json`. BHASHINI is used only for dynamic citizen-generated or backend-generated text.

## BHASHINI Setup

Add the provider configuration to `.env`:

```env
TRANSLATION_PROVIDER=bhashini
ENABLE_TRANSLATION=true
TRANSLATION_TIMEOUT_SECONDS=20
TRANSLATION_MAX_RETRIES=2
BHASHINI_USER_ID=
BHASHINI_API_KEY=
BHASHINI_PIPELINE_ID=
BHASHINI_CONFIG_URL=
BHASHINI_CACHE_TTL_SECONDS=3600
ENABLE_INDIC_TRANS2_FALLBACK=false
INDIC_TRANS2_BASE_URL=
INDIC_TRANS2_TIMEOUT_SECONDS=30
```

Do not expose BHASHINI credentials to the frontend. If BHASHINI is unavailable or not configured, complaint submission still works: the original text is preserved, best-effort English normalization is attempted, and the response is marked as fallback/human-verification required.

Translation endpoints:

- `POST /api/translation/detect-language`
- `POST /api/translation/translate`

## Speech Architecture

Speech input uses the existing multilingual complaint pipeline:

```text
Microphone
→ browser MediaRecorder
→ FastAPI multipart upload
→ BHASHINI ASR
→ editable transcript
→ translation
→ complaint analysis
→ complaint submission
```

Optional spoken responses are disabled by default:

```text
Citizen reply
→ BHASHINI TTS
→ Listen to Response
```

Typed complaint input always remains available. If microphone permission is denied, the browser does not support `MediaRecorder`, or BHASHINI ASR is unavailable, citizens can type the complaint manually.

## BHASHINI Speech Setup

Add speech configuration to `.env`:

```env
ENABLE_SPEECH_INPUT=true
ENABLE_TTS_RESPONSES=false
BHASHINI_ASR_PIPELINE_ID=
BHASHINI_TTS_PIPELINE_ID=
BHASHINI_SPEECH_CONFIG_URL=
BHASHINI_SPEECH_TIMEOUT_SECONDS=30
BHASHINI_SPEECH_MAX_RETRIES=2
BHASHINI_SPEECH_CACHE_TTL_SECONDS=3600
MAX_AUDIO_SIZE_MB=10
MAX_AUDIO_DURATION_SECONDS=120
ALLOWED_AUDIO_TYPES=audio/webm,audio/wav,audio/mpeg,audio/mp4,audio/ogg
```

Reuse `BHASHINI_USER_ID` and `BHASHINI_API_KEY`. Do not expose BHASHINI credentials to the frontend.

Browser notes:

- Microphone access is requested only after the citizen clicks record.
- Localhost works for development; deployed microphone access normally requires HTTPS.
- Recording formats vary by browser. The frontend tries WEBM/Opus, WEBM, MP4, then OGG.
- TTS does not autoplay. Citizens must click `Listen to Response`.

Speech endpoints:

- `POST /api/speech/transcribe`
- `POST /api/speech/synthesize`

## Upload Validation

- Accepts JPEG, PNG, and WEBP only.
- Rejects empty files.
- Rejects malformed images using Pillow.
- Rejects files larger than `MAX_UPLOAD_SIZE_MB`.
- Stores only the Cloudinary `secure_url` in PostgreSQL as `photo_url`.
- Does not store raw file bytes in PostgreSQL.

## Frontend Manual QA

Desktop:

1. Open `/report`.
2. Select an image.
3. Confirm preview appears.
4. Upload the image.
5. Replace image.
6. Remove image.
7. Skip image.
8. Submit complaint.
9. Track complaint.
10. Open admin complaint detail and confirm the image appears.

Mobile:

1. Open `/report`.
2. Tap `Take a Photo`.
3. Capture an image where camera capture is supported.
4. Confirm preview appears.
5. Upload and submit complaint.
6. Verify the admin complaint image display.

## Frontend Integration

From the frontend root, set:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

The backend uses camelCase JSON aliases expected by the frontend, including `referenceId`, `originalText`, `normalizedEnglishText`, `photoUrl`, `wardNumber`, `createdAt`, and `updatedAt`.

## Remaining Limitations

- No authentication or role-based access yet.
- No computer vision or vector duplicate detection yet.
- LLM output requires human verification and can misunderstand ambiguous complaints.
- Fallback keyword rules remain active and may be less nuanced than model analysis.
- Admin summaries are stored in the existing concise `reasoning_summary` field until a dedicated migration is added.
- No automatic resolution, duplicate merge, response-time promise, or permanent team assignment is performed by AI.
- BHASHINI ASR/TTS require configured provider pipelines; automated tests mock provider calls.
- Machine translation requires human verification. Romanised and mixed-language input is best effort until provider-backed translation is configured.
- One primary image per complaint for the MVP. Multiple images can be added later with a separate image table.
- Hotspot detection is intentionally simple: locality-category grouping with configurable thresholds.
- Ward analysis stores supplied ward fields only. GeoJSON point-in-polygon ward mapping is a future integration point.
