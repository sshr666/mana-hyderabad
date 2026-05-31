# Mana Hyderabad Backend

FastAPI backend foundation for the Mana Hyderabad civic complaint platform.

This phase implements PostgreSQL/PostGIS-backed complaint storage, human-readable reference IDs, tracking, admin filtering, status updates, map points, nearby complaint radius search, locality and ward grouping, basic hotspot detection, Cloudinary image uploads, Alembic migrations, seed data, and pytest coverage.

It intentionally does not include LLMs, translation APIs, speech processing, computer vision, authentication, or pgvector semantic search yet.

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
```

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
python scripts/verify_upload_flow.py
```

The database script checks health, submits a complaint, retrieves it, updates status, lists admin complaints, fetches map points, runs nearby search, fetches hotspots, and prints analytics keys.

The upload script posts `test-assets/sample-garbage.jpg` to `/api/uploads/images`, submits a complaint with the returned `photoUrl`, retrieves the complaint, and verifies the stored `photoUrl`.

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
- No LLM, translation, ASR/TTS, computer vision, or vector duplicate detection yet.
- One primary image per complaint for the MVP. Multiple images can be added later with a separate image table.
- Hotspot detection is intentionally simple: locality-category grouping with configurable thresholds.
- Ward analysis stores supplied ward fields only. GeoJSON point-in-polygon ward mapping is a future integration point.
