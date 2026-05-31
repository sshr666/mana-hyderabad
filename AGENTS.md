# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Shape

Mana Hyderabad is a civic-tech monorepo.

- Frontend: Next.js App Router at the repository root.
- Backend: FastAPI application in `mana-hyderabad-backend/`.
- Database: PostgreSQL with PostGIS via `mana-hyderabad-backend/docker-compose.yml`.
- Frontend API boundary: `lib/api-client.ts`.
- Backend API routers: `mana-hyderabad-backend/app/api/`.

## Rules for Agents

- Do not commit `.env`, `.env.local`, API keys, uploaded citizen data, or database dumps.
- Keep frontend API calls isolated in `lib/api-client.ts`.
- Keep backend SQLAlchemy queries in repository/service layers, not route handlers.
- Do not add LLM, translation, speech, computer vision, pgvector, or authentication unless the task explicitly asks for that phase.
- Preserve the existing UI and routes unless a user request requires a focused change.
- Treat AI analysis and uploaded images as requiring human verification.
- Use migrations for database schema changes.
- Run relevant tests before reporting completion.

## Useful Commands

Frontend:

```bash
npm install
npm run dev
npm run build
npm test
```

Backend:

```bash
cd mana-hyderabad-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d
alembic upgrade head
pytest
```

## Local URLs

- Frontend: `http://127.0.0.1:3000`
- Backend health: `http://127.0.0.1:8000/api/health`
- Swagger docs: `http://127.0.0.1:8000/docs`
