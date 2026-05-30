# Mana Hyderabad Backend

FastAPI backend foundation for the Mana Hyderabad civic complaint platform.

This version provides complaint submission, reference ID generation, tracking, admin list filters, admin updates, analytics, map points, PostGIS storage, Alembic migrations, and seed data. It intentionally does not include LLMs, translation APIs, computer vision, authentication, or duplicate vector search yet.

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

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

## Environment Variables

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/mana_hyderabad
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## API Endpoints

```text
POST   /api/complaints/analyse
POST   /api/complaints
GET    /api/complaints/{reference_id}
GET    /api/admin/complaints
PATCH  /api/admin/complaints/{reference_id}
GET    /api/admin/analytics
GET    /api/admin/map-points
GET    /api/health
```

## Quick API Test

Analyse:

```bash
curl -X POST http://127.0.0.1:8000/api/complaints/analyse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Road pe bahut waterlogging hai near Gachibowli signal",
    "language": "hi",
    "photoUrl": null,
    "latitude": null,
    "longitude": null
  }'
```

Submit:

```bash
curl -X POST http://127.0.0.1:8000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{
    "originalText": "Road pe bahut waterlogging hai near Gachibowli signal",
    "normalizedEnglishText": "There is waterlogging near Gachibowli signal.",
    "originalLanguage": "hi",
    "category": "WATERLOGGING",
    "subcategory": "ROAD_WATERLOGGING",
    "priority": "MEDIUM",
    "latitude": 17.4401,
    "longitude": 78.3489,
    "landmark": "Gachibowli signal",
    "photoUrl": null
  }'
```

Track:

```bash
curl http://127.0.0.1:8000/api/complaints/HYD-SAN-0142
```

Admin:

```bash
curl http://127.0.0.1:8000/api/admin/complaints
curl http://127.0.0.1:8000/api/admin/analytics
curl http://127.0.0.1:8000/api/admin/map-points
```

Update:

```bash
curl -X PATCH http://127.0.0.1:8000/api/admin/complaints/HYD-SAN-0142 \
  -H "Content-Type: application/json" \
  -d '{"status": "ASSIGNED", "assignedTeam": "Ward 107 Sanitation Crew"}'
```

## Notes for Frontend Integration

The backend uses camelCase JSON aliases where the current frontend mock API already expects them, for example `referenceId`, `originalText`, `normalizedEnglishText`, `photoUrl`, `createdAt`, and `updatedAt`.

The frontend should replace mock calls in `lib/api-client.ts` with HTTP calls to this backend base URL.

## Remaining Limitations

- No authentication or role-based access yet.
- No file upload endpoint yet; `photoUrl` is stored as a string.
- No LLM, translation, ASR/TTS, computer vision, or vector duplicate detection yet.
- `possibleDuplicates` returns `0` by design for this backend foundation.
- Reference IDs are generated per category by current row counts; production should use a sequence table or transaction-safe counter under heavier concurrency.
