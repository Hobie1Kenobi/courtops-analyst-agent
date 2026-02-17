# Deploying CourtOps Analyst Agent

Ways to run the full app in the cloud so others can use it without cloning the repo. All steps below use the terminal where possible; free-tier options are listed first.

---

## Option 1: Fly.io (fully terminal-driven)

You can do everything from the terminal with the [Fly CLI](https://fly.io/docs/hub/installation/).

### 1. Install Fly CLI and sign in

```bash
# Windows (PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Then log in (opens browser once)
fly auth login
```

### 2. Create Postgres and Redis (free tiers)

```bash
# From repo root
cd backend

# Create Postgres (free; one per org)
fly postgres create --name courtops-db --region ord

# Create Redis (Upstash free tier, via Fly)
fly redis create --name courtops-redis --region ord
```

When prompted, note the connection strings. For Postgres, attach the app so you get `DATABASE_URL`:

```bash
fly postgres attach courtops-db
```

Use the same app name as your backend app (e.g. `courtops-backend`). If the backend app does not exist yet, create it first (step 3), then run attach again.

### 3. Launch and deploy backend

```bash
# From backend/
fly launch --no-deploy --copy-config --name courtops-backend
```

Edit `fly.toml` if you changed the app name. Set secrets (use the URLs from step 2):

```bash
fly secrets set DATABASE_URL="postgres://..." REDIS_URL="redis://..." JWT_SECRET="your-random-secret"
fly deploy
```

Tables are created on first backend start. Seed demo data once (e.g. via Fly console):

```bash
fly ssh console -C "python -m app.seed_demo_data"
```

### 4. Launch and deploy frontend

```bash
# From repo root
cd frontend

fly launch --no-deploy --copy-config --name courtops-frontend
fly secrets set NEXT_PUBLIC_API_BASE_URL="https://courtops-backend.fly.dev"
fly deploy
```

### 5. Open the app

- Frontend: `https://courtops-frontend.fly.dev`
- Backend API: `https://courtops-backend.fly.dev`
- Login: `supervisor` / `password` (after seed has run)

### Optional: Celery worker on Fly

To run background tasks (e.g. monthly reports) you can run a worker as a separate Fly app:

- Add a `fly.toml` in the repo that uses the same backend image but `CMD` runs `celery -A app.celery_app.celery_app worker --loglevel=INFO`.
- Set the same `DATABASE_URL`, `REDIS_URL`, and `JWT_SECRET` as the backend.
- This uses an extra Fly machine (free tier has a limited number).

---

## Option 2: Render (one-time dashboard, then terminal)

Render has a free Postgres (90 days), free Redis, and free web/worker tiers. The first time you connect the repo you use the dashboard; after that you can deploy from the terminal with the [Render CLI](https://render.com/docs/cli).

### 1. One-time setup in the dashboard

1. Go to [dashboard.render.com](https://dashboard.render.com) and sign in (e.g. with GitHub).
2. **New → Blueprint**. Connect the repo `Hobie1Kenobi/courtops-analyst-agent` and set the path to **render.yaml** (root).
3. Apply the Blueprint. Render will create: Postgres, Redis, backend web service, frontend web service, Celery worker.
4. In the **backend** service, copy the generated **JWT_SECRET** (or set your own). Optionally set the same value on the **courtops-worker** service so tokens stay valid across restarts.

### 2. Deploy from terminal (after CLI install)

```bash
# Install Render CLI (see https://render.com/docs/cli)
# Then link and deploy:
render deploy
```

You can also trigger deploys by pushing to the connected branch; no terminal needed for that.

### 3. Run migrations and seed

Use the Shell tab for the **courtops-backend** service in the dashboard, or use a one-off job if you add one:

```bash
python -m app.seed_demo_data
```

---

## Option 3: Railway (terminal-first with CLI)

[Railway](https://railway.app) has a CLI and free-tier limits. You can create a project and add Postgres + Redis from the CLI, then deploy the backend and frontend (each as a service). See [Railway CLI docs](https://docs.railway.app/develop/cli); the flow is similar to Fly: `railway login`, `railway init`, add Postgres/Redis plugins, set `DATABASE_URL` and `REDIS_URL`, then `railway up` for each service.

---

## Environment summary

| Variable | Backend | Frontend | Worker |
|----------|---------|----------|--------|
| `DATABASE_URL` | ✓ | — | ✓ |
| `REDIS_URL` | ✓ | — | ✓ |
| `JWT_SECRET` | ✓ | — | — |
| `NEXT_PUBLIC_API_BASE_URL` | — | ✓ (backend URL) | — |

For local Docker, the repo uses `postgres_*` and `redis_url` in `.env`; in production, set `DATABASE_URL` and `REDIS_URL` so the same code works on Fly, Render, and Railway.
