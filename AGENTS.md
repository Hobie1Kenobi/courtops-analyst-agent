# AGENTS.md

## Cursor Cloud specific instructions

### Architecture

CourtOps Analyst Agent is a full-stack app: **FastAPI** backend (Python 3.11) + **Next.js 14** frontend (Node 20). PostgreSQL 15 and Redis 7 are required infrastructure. See `README.md` for full feature list and demo script.

### Running services locally (outside Docker Compose)

Docker containers for **PostgreSQL** and **Redis** must be started first:

```bash
sudo dockerd &>/tmp/dockerd.log &
sudo docker start courtops-db courtops-redis 2>/dev/null || \
  (sudo docker run -d --name courtops-db -e POSTGRES_USER=courtops -e POSTGRES_PASSWORD=courtops_password -e POSTGRES_DB=courtops_db -p 5432:5432 postgres:15 && \
   sudo docker run -d --name courtops-redis -p 6379:6379 redis:7)
```

**Backend** (from `/workspace/backend`):

```bash
source venv/bin/activate
POSTGRES_HOST=localhost REDIS_URL=redis://localhost:6379/0 uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend** (from `/workspace/frontend`):

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 20
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

### Key gotchas

- The `.env` file must set `POSTGRES_HOST=localhost` (not `db`) when running outside Docker Compose. The default config in `.env.example` uses `db` which is the Docker Compose service name.
- The `REDIS_URL` must also point to `localhost` when running locally.
- Backend uses `Base.metadata.create_all()` at startup to create tables — no Alembic migrations to run.
- To seed demo data: `cd backend && source venv/bin/activate && POSTGRES_HOST=localhost REDIS_URL=redis://localhost:6379/0 python -m app.seed_demo_data`
- Demo users: `supervisor`, `analyst`, `clerk`, `itsupport`, `readonly` — all with password `password`.
- The `POST /tickets/` endpoint has a pre-existing bug where `created_at` is None for new tickets (the model doesn't set a default). This does not affect listing or other endpoints.
- ESLint requires a `.eslintrc.json` config file in `frontend/` to avoid interactive prompts from `next lint`. If missing, create it with `{"extends": "next/core-web-vitals"}`.

### Testing

- **Backend tests**: `cd backend && source venv/bin/activate && POSTGRES_HOST=localhost REDIS_URL=redis://localhost:6379/0 pytest tests/ -v`
- **Frontend lint**: `cd frontend && npx next lint`
- Backend tests are pure unit tests (no DB required) covering SLA calculation, audit anomalies, and case time-to-disposition.

### Celery workers (optional)

Only needed for background agent tasks. Not required for basic API/UI testing.

```bash
cd backend && source venv/bin/activate
celery -A app.celery_app.celery_app worker --loglevel=INFO
```
