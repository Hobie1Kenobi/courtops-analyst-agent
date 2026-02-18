# Daily Ops Robust Preset – Phase 1 and Phase 2 Reference

This document is the single reference for implementing the **daily_ops_robust** preset (a more complete "day in the life" of a Municipal Court Functional Analyst). Use it when adding the new preset in agent mode.

The existing **daily_ops_demo** preset remains unchanged. This preset runs **next to** it as a second option in the Agent Console.

---

## Phase 1 – Robust Preset (Current Tools + mark_patch_status)

### Scope

- Add preset `daily_ops_robust` with a longer goal script and **11** required tools (the current 10 plus `mark_patch_status`).
- No new agent tools. Backend route and frontend button only.

### Required tools (11)

Same as `DAILY_OPS_REQUIRED_TOOLS` in [backend/app/api/routes/agent.py](backend/app/api/routes/agent.py), **plus**:

- `mark_patch_status`

Ordered list for implementation:

1. refresh_public_dataset  
2. triage_tickets  
3. sla_sweep  
4. escalate_overdue_tickets  
5. inventory_compliance_check  
6. generate_monthly_operations_report  
7. generate_revenue_at_risk_report  
8. generate_audit_report  
9. create_change_request  
10. generate_change_request_docs  
11. **mark_patch_status**

### Goal text (Phase 1)

Use this as `DAILY_OPS_ROBUST_GOAL` in the agent route. The agent must call all 11 tools before returning a final summary; completion enforcement will use the 11-tool list.

```
Run the full daily operations robust preset. Do the following in order:

1. Refresh the public dataset cache (source_id: somerville). If it times out, continue.

2. Help desk: Triage tickets (triage_tickets), then resolve as many access-issue tickets as practical (resolve_ticket). Run SLA sweep (sla_sweep), then escalate all overdue tickets (escalate_overdue_tickets).

3. Inventory and patch lifecycle: Run inventory compliance check (inventory_compliance_check). For each out-of-compliance device create a patch record (create_patch_record) as practical. For at least one patch record you just created, call mark_patch_status with status "scheduled" so the patch lifecycle is demonstrated.

4. Reporting: Generate the monthly operations report (generate_monthly_operations_report). Generate the Revenue at Risk (FTA) report (generate_revenue_at_risk_report). Generate the monthly audit report (generate_audit_report).

5. Change management: Create a change request with title "New ordinance requires new disposition code", requested_by "Court Manager", current_process "Manual disposition codes in legacy system", proposed_change "Add new disposition code to case management for ordinance compliance.", and where applicable impact_users, impact_data, impact_security. Then call generate_change_request_docs with the change_request_id returned from create_change_request.

6. Closing: List all artifact paths (reports/YYYY-MM/..., docs/generated/...). End with recommended next steps (e.g. review audit_report.txt for failed-login anomalies; share Revenue at Risk report with collections; follow up on escalated tickets). Do not provide this final summary until all 11 required tools have been called.

Required tool sequence (you must call each before finishing): refresh_public_dataset, triage_tickets, sla_sweep, escalate_overdue_tickets, inventory_compliance_check, generate_monthly_operations_report, generate_revenue_at_risk_report, generate_audit_report, create_change_request, generate_change_request_docs, mark_patch_status.
```

### Implementation steps (Phase 1)

1. In [backend/app/api/routes/agent.py](backend/app/api/routes/agent.py):
   - Define `DAILY_OPS_ROBUST_GOAL` (string above).
   - Define `DAILY_OPS_ROBUST_REQUIRED_TOOLS` (list of 11 tool names above).
   - In the `/run` handler, add a branch: if `body.preset == "daily_ops_robust"`, set `goal = DAILY_OPS_ROBUST_GOAL` and `require_completion_tools = DAILY_OPS_ROBUST_REQUIRED_TOOLS`.
   - Ensure `AgentRunRequest.preset` accepts `"daily_ops_robust"` (e.g. `preset: str | None` already allows any string).

2. In [frontend/app/agent/page.tsx](frontend/app/agent/page.tsx):
   - Add a second preset button, e.g. "Run daily_ops_robust preset", that calls `handleRun("daily_ops_robust")` (same pattern as the existing "Run daily_ops_demo preset" which calls `handleRun("daily_ops_demo")`).

3. No changes to [backend/app/agent/orchestrator.py](backend/app/agent/orchestrator.py) or [backend/app/agent/tools.py](backend/app/agent/tools.py) for Phase 1.

---

## Phase 2 – Optional New Tools and Preset Update

Phase 2 extends the robust preset with two new agent tools and updates the robust goal and required-tools list. Implement only if you want the agent to perform case-metrics review and custom CSV export as part of the robust run.

### New tools to add

| Tool name | Description | Backend basis |
|-----------|-------------|---------------|
| **get_case_metrics** | Return a short summary of case metrics: monthly totals, disposed vs non-disposed, average case age, FTA count if available. | [backend/app/api/routes/cases.py](backend/app/api/routes/cases.py) `monthly_metrics()` and Case model; agent tool calls same logic, returns summary dict. |
| **generate_custom_query_csv** | Generate a Crystal Reports–style CSV for an entity (cases, tickets, or devices) and write to `reports/{period}/` or return path. | [backend/app/api/routes/reports.py](backend/app/api/routes/reports.py) `custom_query_csv()`; agent tool invokes the same query logic, writes to a file under REPORT_ROOT, returns path. |

### Implementation steps (Phase 2)

1. **backend/app/agent/tools.py**
   - Add `get_case_metrics` and `generate_custom_query_csv` to `TOOL_WHITELIST`.
   - Add corresponding entries to `OPENAI_TOOLS` (parameters: e.g. optional `period` for get_case_metrics; `entity` and optional `period` for generate_custom_query_csv).
   - In `_execute_tool`, implement:
     - `get_case_metrics`: Query cases, group by month (reuse logic from `monthly_metrics` or call the same service), return a short summary (e.g. last 3 months totals, disposed_pct, avg_case_age_days). Optionally include FTA count from Case.status.
     - `generate_custom_query_csv`: Build CSV in memory (same as `custom_query_csv`), write to `REPORT_ROOT / period / f"{entity}_export.csv"`, ensure_report_dir(period), return path.

2. **backend/app/api/routes/agent.py**
   - Update `DAILY_OPS_ROBUST_GOAL` to add:
     - After step 1 (refresh): "Call get_case_metrics and note backlog/summary for the current period."
     - After step 4 (reporting): "Call generate_custom_query_csv for entity cases (and optionally tickets) for leadership export."
   - Add the two new tool names to `DAILY_OPS_ROBUST_REQUIRED_TOOLS` (13 tools total: original 11 + get_case_metrics + generate_custom_query_csv). Order: list get_case_metrics early (e.g. after refresh), and generate_custom_query_csv after the three report generators.

3. **Orchestrator**
   - No change; it already uses the required-tools list passed from the route.

4. **Frontend**
   - No change for Phase 2; the same "Run daily_ops_robust preset" button sends the preset name; backend supplies the updated goal and required list.

### Phase 2 required tools (13)

1. refresh_public_dataset  
2. get_case_metrics  
3. triage_tickets  
4. sla_sweep  
5. escalate_overdue_tickets  
6. inventory_compliance_check  
7. generate_monthly_operations_report  
8. generate_revenue_at_risk_report  
9. generate_audit_report  
10. generate_custom_query_csv  
11. create_change_request  
12. generate_change_request_docs  
13. mark_patch_status  

(Order can be adjusted so get_case_metrics is near the start and generate_custom_query_csv after the three reports.)

---

## Summary

| Phase | What changes | Required tools |
|-------|----------------|----------------|
| Phase 1 | New preset + robust goal + 11th tool (mark_patch_status) | 11 |
| Phase 2 | Two new tools (get_case_metrics, generate_custom_query_csv); robust goal and list updated | 13 |

Keep **daily_ops_demo** unchanged (10 tools, existing goal). Use this document when implementing or referring the agent to the robust preset.
