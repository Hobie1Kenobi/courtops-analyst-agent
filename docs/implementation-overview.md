## Implementation Overview

This document summarizes the concrete implementation work completed for the **CourtOps Analyst Agent** project, complementing the high-level description in `README.md`.

### Backend (FastAPI) Implementation

- **Core app and configuration**
  - `app/main.py` – FastAPI app factory, CORS, health endpoint, router registration.
  - `app/core/config.py` – Environment-driven settings (Postgres, Redis, JWT).
  - `app/db/session.py` – SQLAlchemy engine, session factory, and declarative `Base`.

- **Domain models (`app/models/`)**
  - `user.py` – `User` with `UserRole` enum (Clerk, Analyst, IT Support, Supervisor, Read-only).
  - `audit.py` – `AuditEvent` with `AuditAction` (login success/failure, role change, record edit, report export).
  - `ticket.py` – Help desk `Ticket` with category, priority, status, SLA helper methods and `set_due_from_sla`.
  - `inventory.py` – `Device` for hardware inventory, including warranty and patch dates with helper `is_warranty_expiring_within_days`.
  - `cases.py` – `Case` with `CaseStatus`, filing/disposition dates, and helpers for case age and time-to-disposition.
  - `patches.py` – `Patch` representing application/device patches with lifecycle statuses and key dates.
  - `change_requests.py` – `ChangeRequest` with workflow fields and `ChangeRequestStatus`.

- **Auth & security**
  - `app/core/security.py` – Password hashing (bcrypt), JWT creation/verification.
  - `app/schemas/user.py` – Pydantic models for user/token payloads.
  - `app/api/deps.py` – `get_current_user` (JWT-based) and `require_role` helpers for RBAC enforcement.
  - `app/api/routes/auth.py` – `/auth/token` endpoint issuing JWTs (password grant).

- **API routes**
  - `tickets.py` – CRUD-style listing, creation, update, and SLA summary for help desk tickets.
  - `cases.py` – Listing recent cases and `/cases/metrics/monthly` aggregation over in-app data.
  - `inventory.py` – Device listing for inventory/compliance views.
  - `patches.py` – Listing of patches for patch lifecycle UI.
  - `change_requests.py` – List/create change requests plus `/change-requests/{id}/generate-docs` to produce documentation artifacts.
  - `reports.py` – Reporting endpoints:
    - `/reports/monthly` – discover monthly bundles under `reports/YYYY-MM`.
    - `/reports/monthly/{period}/pdf` – download the main PDF.
    - `/reports/custom-query.csv` – limited "Crystal Reports style" CSV export for `cases`, `tickets`, or `devices`.

- **Schemas (`app/schemas/`)**
  - `ticket.py`, `cases.py`, `inventory.py`, `patches.py`, `change_requests.py` – Strongly-typed request/response models.

### CourtOps Agent & Background Jobs

- **Celery configuration**
  - `app/celery_app.py` – Celery app pointing at Redis with beat schedules for:
    - Daily (`run_daily_checks`)
    - Weekly (`run_weekly_checks`)
    - Monthly (`run_monthly_reports`)

- **Daily checks (`app/tasks/daily_checks.py`)**
  - Finds tickets in `OPEN`/`IN_PROGRESS` that are overdue based on SLA due date.
  - Flags devices with warranty expiring within 30 days or last patch older than 90 days.
  - Loads recent `AuditEvent` records and applies login anomaly rules to detect bursts of failed logins.

- **Weekly checks (`app/tasks/weekly_checks.py`)**
  - Identifies patches deployed at least 7 days ago but not yet verified (for follow-up reminders).
  - Runs simple case data-quality rules (e.g., disposition date present but non-disposed status).

- **Monthly reports (`app/tasks/monthly_reports.py` + `app/services/reporting.py`)**
  - Loads all `Case`, `Ticket`, and `Device` records.
  - Generates a concise PDF monthly operations report using ReportLab into `reports/YYYY-MM/`.
  - Writes a small text summary file alongside the PDF describing the generated bundle.

- **Audit rules (`app/services/audit_rules.py`)**
  - Implements `detect_repeated_failed_logins` for spotting suspicious bursts of failed login attempts within a rolling time window.

### Reporting & Data Layer

- **SQL views**
  - `app/db/views.sql` – Defines `vw_monthly_case_metrics` for monthly case metrics (total, disposed vs non-disposed, average case age).

- **Public Data Connector (`app/services/public_data_connector.py`)**
  - Downloads a public Somerville, MA traffic citations CSV dataset to `data/cache/`.
  - Stores a simple metadata sidecar (source URL, timestamp, license reference) for reproducibility.

### Documentation Generation

- **Docs generator service (`app/services/docs_generator.py`)**
  - For a given `ChangeRequest`, writes three Markdown documents under `docs/generated/`:
    - Functional Specification
    - SOP Update
    - Release Notes
  - Exposed via `/change-requests/{id}/generate-docs` for use in the Change Requests workflow.

### Seeding & Tests

- **Seed script (`app/seed_demo_data.py`)**
  - Creates demo users for all RBAC roles with password `password`.
  - Generates 3–6 months of synthetic cases, tickets (with varied priorities/statuses and computed SLAs), devices, patches, and change requests.

- **Unit tests (`backend/tests/`)**
  - `test_sla_calculation.py` – Verifies due-date calculation from ticket priority-based SLA hours.
  - `test_case_time_to_disposition.py` – Verifies case time-to-disposition computation.
  - `test_audit_anomalies.py` – Validates the repeated failed-login anomaly detection behavior.

### Frontend (Next.js) Implementation

- **App structure**
  - `app/layout.tsx` – Global layout with navigation for Dashboard, Cases, Tickets, Inventory, Patches, Reports, Change Requests, Admin, and Job Mapping.
  - `app/page.tsx` – Dashboard with high-level cards aligned to court operations, help desk, inventory, patches, audit, and change requests.

- **Major pages**
  - `app/cases/page.tsx` – Cases dashboard placeholder describing metrics and backlog views powered by the `/cases` APIs.
  - `app/tickets/page.tsx` – Help desk view scaffold describing categories, priorities, SLA clocks, and triage.
  - `app/inventory/page.tsx` – Inventory summary, highlighting compliance and risk concepts.
  - `app/patches/page.tsx` – Patch lifecycle/calendar view description.
  - `app/reports/page.tsx` – Tiles for monthly operations, audit, SLA/inventory, and a custom query builder tied to backend reporting endpoints.
  - `app/change-requests/page.tsx` – Requirements/change request workflow description and generated docs.
  - `app/admin/page.tsx` – Admin/security narrative for RBAC and auditing.
  - `app/mapping/page.tsx` – Job Responsibilities Mapping summary pointing to the full matrix in `docs/requirements-traceability-matrix.md`.

- **UI utilities**
  - `components/ui/card.tsx` – Simple shadcn-style card component (container, header, title, content).
  - `components/utils/cn.ts` – Tailwind/className merging helper used by UI components.

