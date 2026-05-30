# Mana Hyderabad Backend

FastAPI backend foundation for the Mana Hyderabad civic complaint platform.

This phase implements PostgreSQL/PostGIS-backed complaint storage, human-readable reference IDs, tracking, admin filtering, status updates, map points, nearby complaint radius search, locality and ward grouping, basic hotspot detection, Alembic migrations, seed data, and pytest coverage.

It intentionally does not include LLMs, translation APIs, speech processing, computer vision, authentication, cloud file storage, or pgvector semantic search yet.

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
```

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
```

The script checks health, submits a complaint, retrieves it, updates status, lists admin complaints, fetches map points, runs nearby search, fetches hotspots, and prints analytics keys.

## Frontend Integration

From the frontend root, set:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

The backend uses camelCase JSON aliases expected by the frontend, including `referenceId`, `originalText`, `normalizedEnglishText`, `photoUrl`, `wardNumber`, `createdAt`, and `updatedAt`.

## Remaining Limitations

- No authentication or role-based access yet.
- No file upload endpoint yet; `photoUrl` is stored as a string.
- No LLM, translation, ASR/TTS, computer vision, or vector duplicate detection yet.
- Hotspot detection is intentionally simple: locality-category grouping with configurable thresholds.
- Ward analysis stores supplied ward fields only. GeoJSON point-in-polygon ward mapping is a future integration point.
