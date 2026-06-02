# Mana Hyderabad Deployment

This document captures the production deployment wiring for Mana Hyderabad without storing credentials.

## Current Deployment Status

- Deployment mode: Mode B, deployment preparation only.
- Frontend URL: https://mana-hyderabad.vercel.app/
- Backend URL: pending Render service URL.
- Backend health-check URL: pending Render service URL.
- Swagger URL: pending Render service URL.
- Frontend host: Vercel.
- Backend host: Render Web Service.
- Database provider: Render PostgreSQL.
- File-storage provider: Cloudinary when credentials are configured; photo upload should remain optional.
- Backend root directory: `mana-hyderabad-backend`.
- Backend entry point: `app.main:app`.
- Health-check path: `/api/health`.

## Render Blueprint

The repository includes `render.yaml` with:

- PostgreSQL database: `mana-hyderabad-db`
- FastAPI web service: `mana-hyderabad-api`
- Root directory: `mana-hyderabad-backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health-check path: `/api/health`

Use the blueprint when creating the Render resources, or create the same resources manually in the Render dashboard.

## Manual Render Setup

1. Open Render and create a PostgreSQL database named `mana-hyderabad-db`.
2. Create a Web Service named `mana-hyderabad-api`.
3. Connect the Git repository.
4. Set the root directory to:

   ```text
   mana-hyderabad-backend
   ```

5. Set the build command:

   ```bash
   pip install -r requirements.txt
   ```

6. Set the start command:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

7. Set the health-check path:

   ```text
   /api/health
   ```

## Required Backend Environment Variables

Set these in Render. Do not commit values.

```env
DATABASE_URL=<Render internal PostgreSQL connection string>
FRONTEND_ORIGINS=https://mana-hyderabad.vercel.app
ENABLE_TRANSLATION=false
ENABLE_SPEECH_INPUT=false
ENABLE_TTS_RESPONSES=false
ENABLE_LLM_ANALYSIS=false
ENABLE_DUPLICATE_DETECTION=false
ENABLE_VISION_ANALYSIS=false
ENABLE_RULE_FALLBACK=true
```

Optional services can be enabled later only after real credentials are configured:

```env
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
BHASHINI_USER_ID=
BHASHINI_API_KEY=
BHASHINI_PIPELINE_ID=
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=
EMBEDDING_MODEL=
VISION_ALLOWED_IMAGE_HOSTS=res.cloudinary.com
```

## Database Extensions

After the Render database exists, open a database shell and run:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
```

Verify:

```sql
SELECT extname
FROM pg_extension
WHERE extname IN ('postgis', 'vector');
```

Expected rows:

```text
postgis
vector
```

Verify PostGIS:

```sql
SELECT PostGIS_Version();
```

## Migrations and Seed Data

From a Render shell in `mana-hyderabad-api`, run:

```bash
alembic upgrade head
alembic current
```

Seed demo data only after migrations succeed:

```bash
python -m app.seed
```

The seed command is designed for development/demo data. Avoid reseeding if the production database already contains real submissions.

Rollback one migration if needed:

```bash
alembic downgrade -1
```

## Vercel Frontend Wiring

After Render creates the backend URL, set this Vercel production environment variable:

```env
NEXT_PUBLIC_API_BASE_URL=<PUBLIC_RENDER_BACKEND_URL>
NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=false
NEXT_PUBLIC_MAP_STYLE_URL=https://demotiles.maplibre.org/style.json
NEXT_PUBLIC_ENABLE_SPEECH_INPUT=false
NEXT_PUBLIC_ENABLE_TTS_RESPONSES=false
```

Do not add backend secrets to Vercel.

Trigger a new Vercel production deployment after saving the environment variables.

## Public Verification Checklist

Replace `<PUBLIC_RENDER_BACKEND_URL>` with the actual Render URL.

```bash
curl <PUBLIC_RENDER_BACKEND_URL>/api/health
```

Expected:

```json
{ "status": "ok" }
```

Open:

```text
<PUBLIC_RENDER_BACKEND_URL>/docs
```

Check core endpoints:

```bash
curl <PUBLIC_RENDER_BACKEND_URL>/api/admin/analytics
curl <PUBLIC_RENDER_BACKEND_URL>/api/admin/map-points
```

Submit a smoke-test complaint:

```bash
curl -X POST "<PUBLIC_RENDER_BACKEND_URL>/api/complaints" \
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
    "analysisSource": "MANUAL",
    "requiresHumanVerification": true
  }'
```

Track the returned reference ID:

```bash
curl "<PUBLIC_RENDER_BACKEND_URL>/api/complaints/<REFERENCE_ID>"
```

## CORS

Production CORS origin:

```env
FRONTEND_ORIGINS=https://mana-hyderabad.vercel.app
```

Keep localhost origins only in local development. Do not use `*` in production unless explicitly accepted as a temporary emergency measure.

## Known Limitations

- Public backend URL is still pending until the Render service is created.
- Public database extension status cannot be verified until the Render PostgreSQL database exists.
- Public citizen/admin flows cannot be verified until Vercel is configured with `NEXT_PUBLIC_API_BASE_URL`.
- Optional AI, speech, duplicate-detection, and vision services are disabled for the first public backend deployment unless provider credentials are added.
- Image upload requires Cloudinary credentials before it can work publicly.

## Remaining Human Action

Create the Render database and web service, run extensions and migrations, copy the resulting Render URL, then set `NEXT_PUBLIC_API_BASE_URL` in Vercel and redeploy.
