from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User, UserRole
from app.agent.orchestrator import run_agent
from app.core.config import settings


router = APIRouter(prefix="/agent", tags=["agent"])

DAILY_OPS_DEMO_GOAL = """Run the full daily operations demo. Do the following in order:

1. Refresh the public dataset cache (source_id: somerville). If it times out, continue.
2. Triage help desk tickets (triage_tickets), then resolve as many access-issue tickets as practical with resolve_ticket (turn limit may apply).
3. Run SLA sweep (sla_sweep), then escalate all overdue tickets (escalate_overdue_tickets).
4. Run inventory compliance check (inventory_compliance_check). For each out-of-compliance device create a patch record (create_patch_record) as practical (turn limit may apply).
5. Generate the monthly municipal court operations report bundle (generate_monthly_operations_report). Do not skip this step.
6. Generate the Revenue at Risk (FTA) report (generate_revenue_at_risk_report).
7. Generate the monthly audit report (generate_audit_report).
8. Create a change request with title "New ordinance requires new disposition code", requested_by "Court Manager", current_process "Manual disposition codes in legacy system", and proposed_change "Add new disposition code to case management for ordinance compliance." Then immediately call generate_change_request_docs with the change_request_id returned from create_change_request. Do not skip generate_change_request_docs.

Required tool sequence (you must call each of these before finishing): refresh_public_dataset, triage_tickets, sla_sweep, escalate_overdue_tickets, inventory_compliance_check, generate_monthly_operations_report, generate_revenue_at_risk_report, generate_audit_report, create_change_request, generate_change_request_docs. You will be reminded to call any missing tools until all are done. After each step, report any artifact paths (reports/YYYY-MM/..., docs/generated/...). End with a short summary only after all required tools have been called."""

DAILY_OPS_REQUIRED_TOOLS = [
    "refresh_public_dataset",
    "triage_tickets",
    "sla_sweep",
    "escalate_overdue_tickets",
    "inventory_compliance_check",
    "generate_monthly_operations_report",
    "generate_revenue_at_risk_report",
    "generate_audit_report",
    "create_change_request",
    "generate_change_request_docs",
]

DAILY_OPS_ROBUST_GOAL = """Run the full daily operations robust preset. Do the following in order:

1. Refresh the public dataset cache (source_id: somerville). If it times out, continue. Call get_case_metrics and note backlog/summary for the current period.

2. Help desk: Triage tickets (triage_tickets), then resolve as many access-issue tickets as practical (resolve_ticket). Run SLA sweep (sla_sweep), then escalate all overdue tickets (escalate_overdue_tickets).

3. Inventory and patch lifecycle: Run inventory compliance check (inventory_compliance_check). For each out-of-compliance device create a patch record (create_patch_record) as practical. For at least one patch record you just created, call mark_patch_status with status "scheduled" so the patch lifecycle is demonstrated.

4. Reporting: Generate the monthly operations report (generate_monthly_operations_report). Generate the Revenue at Risk (FTA) report (generate_revenue_at_risk_report). Generate the monthly audit report (generate_audit_report). Call generate_custom_query_csv for entity cases (and optionally tickets) for leadership export.

5. Change management: Create a change request with title "New ordinance requires new disposition code", requested_by "Court Manager", current_process "Manual disposition codes in legacy system", proposed_change "Add new disposition code to case management for ordinance compliance.", and where applicable impact_users, impact_data, impact_security. Then call generate_change_request_docs with the change_request_id returned from create_change_request.

6. Closing: List all artifact paths (reports/YYYY-MM/..., docs/generated/...). End with recommended next steps (e.g. review audit_report.txt for failed-login anomalies; share Revenue at Risk report with collections; follow up on escalated tickets). Do not provide this final summary until all 13 required tools have been called.

Required tool sequence (you must call each before finishing): refresh_public_dataset, get_case_metrics, triage_tickets, sla_sweep, escalate_overdue_tickets, inventory_compliance_check, generate_monthly_operations_report, generate_revenue_at_risk_report, generate_audit_report, generate_custom_query_csv, create_change_request, generate_change_request_docs, mark_patch_status."""

DAILY_OPS_ROBUST_REQUIRED_TOOLS = [
    "refresh_public_dataset",
    "get_case_metrics",
    "triage_tickets",
    "sla_sweep",
    "escalate_overdue_tickets",
    "inventory_compliance_check",
    "generate_monthly_operations_report",
    "generate_revenue_at_risk_report",
    "generate_audit_report",
    "generate_custom_query_csv",
    "create_change_request",
    "generate_change_request_docs",
    "mark_patch_status",
]


class AgentRunRequest(BaseModel):
    goal: str = ""
    mode: str = "demo"
    dry_run: bool = True
    preset: str | None = "daily_ops_demo"


class AgentRunResponse(BaseModel):
    summary: str
    actions_taken: list[dict[str, Any]]
    artifact_paths: list[str]
    dry_run: bool


def _can_run_agent(user: User, dry_run: bool) -> bool:
    if user.role in (UserRole.ANALYST, UserRole.IT_SUPPORT, UserRole.SUPERVISOR):
        return True
    if user.role == UserRole.READ_ONLY and dry_run:
        return True
    return False


@router.post("/run", response_model=AgentRunResponse)
def agent_run(
    body: AgentRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgentRunResponse:
    if not _can_run_agent(current_user, body.dry_run):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Analyst, IT Support, or Supervisor can run the agent with dry_run=false. Read-only may run with dry_run=true only.",
        )
    goal = body.goal.strip() if body.goal else ""
    require_completion_tools = None
    if body.preset == "daily_ops_demo":
        goal = DAILY_OPS_DEMO_GOAL
        require_completion_tools = DAILY_OPS_REQUIRED_TOOLS
    elif body.preset == "daily_ops_robust":
        goal = DAILY_OPS_ROBUST_GOAL
        require_completion_tools = DAILY_OPS_ROBUST_REQUIRED_TOOLS
    if not goal:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="goal or preset required")
    result = run_agent(
        db=db,
        user_id=current_user.id,
        goal=goal,
        mode=body.mode,
        dry_run=body.dry_run,
        require_completion_tools=require_completion_tools,
    )
    return AgentRunResponse(
        summary=result["summary"],
        actions_taken=result["actions_taken"],
        artifact_paths=result.get("artifact_paths", []),
        dry_run=result["dry_run"],
    )


@router.get("/status")
def agent_status() -> dict[str, str]:
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "model": settings.ollama_model,
    }
