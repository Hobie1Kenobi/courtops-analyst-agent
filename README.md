CourtOps Analyst Agent (Municipal Court Functional Analyst Portfolio)
====================================================================

This repository contains a full-stack demonstration system that simulates the work of a Municipal Court Functional Analyst in a city government. It is intentionally generic and **does not use any proprietary city data**. Where real public data is used, it is pulled from public open-data portals; the rest is realistic synthetic data.

The project is designed as a **portfolio-quality** system that shows end-to-end capabilities across:

- Help desk / work orders
- Court operations metrics and reporting
- Data quality and audit trails
- Hardware inventory and lifecycle tracking
- Patch /upgrade management
- Requirements and change requests with documentation outputs
- Security roles, RBAC, and user activity auditing

## High-level Architecture

- **Frontend**: Next.js (App Router) + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Background Jobs**: Celery + Redis
- **Auth**: JWT-based authentication with role-based access control (RBAC)
- **Reporting**:
  - SQL views for monthly metrics
  - PDF exports generated on the backend using a server-side PDF library
  - CSV exports for custom queries
- **Data Connector**: Public Data Connector module for downloading and caching public datasets under `data/cache/`.

Top-level layout:

- `backend/` – FastAPI application, models, APIs, Celery worker, seed scripts, tests
- `frontend/` – Next.js frontend application (dashboard + workflows)
- `docs/` – Documentation, including Requirements Traceability Matrix
- `docs/generated/` – Auto-generated functional specs, SOP updates, and release notes
- `reports/` – Generated monthly report bundles (PDF + CSV + JSON summaries)
- `data/cache/` – Cached public datasets with simple version metadata

## Core Features (Overview)

**1) Help Desk / Work Orders**

- Ticket creation with categorization (application, hardware, access), priority, SLA, assignee, and status.
- Auto-triage rules via the CourtOps Agent:
  - Access issues suggest RBAC check + password reset workflow.
  - Known error signatures map to KB articles.
  - Overdue SLA tickets are escalated to supervisors.
- SLA dashboard for supervisors; queues for analysts and IT support.

**2) Hardware Inventory**

- Track devices: asset tag, type, location, assigned user, warranty date, last patch date, status.
- Full audit log of changes to inventory records.
- Alerts for expiring warranties, missing patches, and out-of-compliance devices.

**3) Court Case Operations Metrics**

- Simulated “Incode-like” court case system: synthetic cases with statuses, dispositions, hearings, fines, and payments.
- Metrics:
  - Case age and time-to-disposition.
  - Disposed vs non-disposed percentages by month.
  - Backlog trend line.
  - Cases approaching configurable statutory thresholds.
- Dashboards with filters by date, charge type, clerk, court, and status.

**4) Security & User Audit**

- RBAC roles:
  - Clerk
  - Analyst
  - IT Support
  - Supervisor
  - Read-only (management/council)
- Audit every critical action (login, report export, role changes, record edits).
- Monthly audit report showing:
  - Repeated failed logins
  - Bulk record edits
  - Off-hours exports
  - Sensitive report accesses

**5) Patch / Upgrade Management**

- Track both application and device patches.
- Patch lifecycle: requested → scheduled → tested → deployed → verified.
- Testing checklist and notes per patch.
- Agent automatically generates change logs and sends verification reminders.
- Patch calendar and change notes UI.

**6) Requirements / Change Requests & Documentation**

- Workflow for requirement analysis:
  - Request intake
  - Current process description
  - Proposed change
  - Impact analysis (users, data, security)
  - Approval status
- Auto-generated documentation (Markdown) saved under `docs/generated/`:
  - Functional specification
  - SOP update
  - Release notes
- Documentation browser in the UI.

**7) Reporting**

- Reports page with:
  - Monthly operational report
  - Audit report
  - SLA report
  - Inventory compliance report
  - Custom query builder (limited “Crystal Reports style”) with field and filter selection; exports CSV.
- Backed by SQL views defined in the backend.

**8) CourtOps Agent**

- Celery-based background worker that runs scheduled jobs:
  - **Daily**:
    - SLA overdue scans and escalations
    - Inventory compliance checks
    - Suspicious user activity detection
  - **Weekly**:
    - Patch verification reminders
    - Data quality checks (missing fields, invalid transitions)
  - **Monthly**:
    - Generate monthly court operations report package (PDF + CSV + summary JSON)
    - Save reports to `reports/YYYY-MM/`
    - Expose report links through the Reports UI.

## Running Locally (Quick Start)

Prerequisites:

- Docker + Docker Compose
- (Optional) Node.js 20+ and Python 3.11+ if you want to run services without Docker

### 1. Clone and configure

```bash
git clone <your-repo-url> courtops-analyst-agent
cd courtops-analyst-agent
cp .env.example .env
```

Update values in `.env` as needed (JWT secret, DB URL, etc.).

### 2. Start with Docker Compose

```bash
docker compose up --build
```

This will start:

- `frontend` – Next.js web UI
- `backend` – FastAPI API service
- `db` – PostgreSQL
- `redis` – Redis broker for Celery
- `worker` – Celery worker
- `scheduler` – Celery beat scheduler for CourtOps Agent jobs

Once everything is healthy:

- Frontend: `http://localhost:3000`
- Backend API + docs: `http://localhost:8000/docs`

### 3. Seed demo data

If not automatically run on first startup, you can execute:

```bash
docker compose exec backend bash -c "python -m app.seed_demo_data"
```

This creates:

- Demo users and RBAC roles
- 3–6 months of synthetic court cases, tickets, inventory, and patches
- Sample audit events and change requests

## Deploying the app

To run the full stack in the cloud (e.g. for a shareable demo) using free-tier hosts, see **[docs/DEPLOY.md](docs/DEPLOY.md)**. It includes:

- **Fly.io** – Fully terminal-driven: install Fly CLI, create Postgres and Redis, deploy backend and frontend from the repo.
- **Render** – One-time Blueprint setup in the dashboard, then deploy from the terminal with the Render CLI.
- **Railway** – Terminal-first with the Railway CLI.

## Testing

To run backend unit tests (SLA, metrics, audit rules):

```bash
docker compose exec backend pytest
```

## Frontend Overview

Main navigation:

- **Dashboard** – High-level metrics, alerts, and links into workflows
- **Cases** – Case metrics, filters, and details
- **Tickets** – Help desk tickets, SLA statuses, and triage
- **Inventory** – Hardware inventory + compliance indicators
- **Patches** – Patch lifecycle and calendar
- **Reports** – Standard reports and custom query builder
- **Change Requests** – Requirements workflow and generated docs
- **Admin** – User management, roles, and audit logs
- **Job Responsibilities Mapping** – Requirements Traceability Matrix view

The UI follows a clean, government-friendly look: neutral colors, solid contrast, clear typography, and minimal decoration.

## Requirements Traceability Matrix

A detailed **Requirements Traceability Matrix** linking job responsibilities from the City of Corpus Christi Municipal Court Functional Analyst position to system features, screens, and background jobs is provided in:

- `docs/requirements-traceability-matrix.md`

## Demo Script (5-minute walkthrough)

1. **Login as Supervisor**
   - Show RBAC-protected navigation and audit logging of login.
2. **Dashboard**
   - Point out case backlog trend, SLA summary, and patch status widgets.
3. **Help Desk / Tickets**
   - Create a new “Access Issue” ticket; show auto-triage suggestions and SLA clock.
   - Mark an old ticket as resolved and show SLA outcome.
4. **Cases**
   - Filter by date and status; highlight case age and time-to-disposition columns.
   - Open a case and show audit trail of edits.
5. **Inventory & Patches**
   - Show devices out of compliance and upcoming warranty expirations.
   - Open a patch record and walk through its lifecycle notes.
6. **Reports**
   - Open the Monthly Operational Report; download PDF.
   - Show audit report highlighting suspicious patterns.
   - Use the custom query builder to export a CSV.
7. **Change Requests**
   - Create a new change request; demonstrate generated functional spec and SOP update in `docs/generated/`.
8. **Job Responsibilities Mapping**
   - Open the mapping page and show how each duty is backed by specific modules and reports.

## License and Data Sources

- This project is intended as a **portfolio and demonstration** system.
- It uses **only public datasets** (via the Public Data Connector) and synthetic data.
- No proprietary municipal court data (including Corpus Christi) is used.

