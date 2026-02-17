## Requirements Traceability Matrix

This matrix maps representative Municipal Court Functional Analyst responsibilities (based on public job descriptions) to the features implemented in the **CourtOps Analyst Agent** project.

> Note: This project uses only public and synthetic data and does **not** integrate with any proprietary court systems.

| # | Responsibility / Duty (Paraphrased) | Implementation (Module / Screen / Job) |
|---|-------------------------------------|-----------------------------------------|
| 1 | Provide end‑user support and triage for municipal court applications and related hardware. | **Help Desk / Tickets** pages (Tickets navigation), `tickets` API; `Ticket` model; CourtOps Agent daily SLA checks. |
| 2 | Monitor and report on service levels, escalating incidents that exceed SLA targets. | SLA fields on `Ticket` (due time, resolution time); supervisor SLA dashboard (Tickets view); daily Celery job `run_daily_checks` for overdue escalation. |
| 3 | Maintain and update knowledge base articles and common issue playbooks. | Ticket auto‑triage suggestions (Access / Known error flows) surfaced in Tickets UI and API (planned enrichment in help desk endpoints). |
| 4 | Analyze court case throughput, backlog, and disposition trends. | `Case` model with status and disposition dates; Cases dashboard; SQL views (planned) for backlog and disposition metrics; Monthly operations report. |
| 5 | Monitor case age to ensure statutory timelines are met. | `case_age_days` and `time_to_disposition_days` methods; Cases UI filters; monthly and daily agent checks for approaching thresholds. |
| 6 | Prepare recurring operational reports for court leadership. | Reports page (Monthly Operational Report); Celery monthly report job `run_monthly_reports`; generated bundles under `reports/YYYY-MM/`. |
| 7 | Ensure data quality and integrity of court systems; identify anomalies. | Data quality checks in weekly Celery job (planned rules for missing fields and invalid transitions); audit event tracking and anomaly detection tests. |
| 8 | Maintain inventory of court hardware and peripherals assigned to staff. | `Device` model and Inventory page; asset tag, location, assigned user, and status fields; audit trail via record‑edit audit events. |
| 9 | Track hardware lifecycle, warranty dates, and patch compliance. | Warranty and last patch fields on `Device`; inventory compliance widgets; daily courtops agent checks for expiring / non‑compliant devices. |
| 10 | Coordinate and document application and device patching and upgrades. | `Patch` model with lifecycle statuses; Patches page and calendar concept; weekly job for patch verification reminders and change logs. |
| 11 | Document testing activities, checklists, and verification for changes. | Testing notes and change_log on `Patch`; change log generation planned in weekly jobs; related views on Patches screen. |
| 12 | Gather and document business requirements and change requests. | `ChangeRequest` model; Change Requests page; workflow fields for current process, proposed change, and impact sections. |
| 13 | Produce functional specifications, SOP updates, and release notes for approved changes. | Auto‑generated Markdown docs under `docs/generated/` (functional spec, SOP update, release notes) based on Change Request data (to be wired to backend job). |
| 14 | Administer and validate security roles and permissions for users. | RBAC based on `UserRole` (Clerk, Analyst, IT Support, Supervisor, Read‑only); protected endpoints using role checks in `api.deps`. |
| 15 | Monitor user access, logins, and sensitive operations for audit purposes. | `AuditEvent` model; login / report export / role change / record edit events; Audit report on Reports page and monthly audit report generation. |
| 16 | Identify and report suspicious activity such as repeated failed logins or bulk changes. | Daily agent user‑activity checks (planned implementation against `AuditEvent`); unit tests for anomaly detection rules. |
| 17 | Provide management with high‑level dashboards summarizing operations and risk. | Dashboard landing page widgets (cases throughput, SLA, inventory compliance, patch posture, audit highlights, change requests). |
| 18 | Coordinate with IT on incidents involving access, hardware, and application performance. | Ticket categories (Application / Hardware / Access) and IT Support role; auto‑triage rules recommending RBAC and password workflows. |
| 19 | Support import/export and reporting from the court case system. | Simulated “Incode‑like” case system using `Case` model; reports and CSV exports from Reports page; SQL views and custom query builder. |
| 20 | Ensure compliance with policy and security requirements for court data. | RBAC enforcement, audit logging, and basic rate limiting for login (planned enhancement); monthly audit and compliance reports. |

