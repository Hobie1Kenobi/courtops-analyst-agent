from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models import (
    ChangeRequest,
    Device,
    Patch,
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)
from app.models.change_requests import ChangeRequestStatus
from app.models.patches import PatchStatus, PatchType
from app.services.audit_log import log_agent_tool
from app.services.docs_generator import generate_change_request_docs
from app.services.public_data_connector import download_somerville_citations
from app.services.reporting import (
    ensure_report_dir,
    generate_audit_report,
    run_monthly_report,
    run_revenue_at_risk_report,
)

REPORT_ROOT = Path(__file__).resolve().parents[2] / "reports"
DOCS_GENERATED = Path(__file__).resolve().parents[2] / "docs" / "generated"

TOOL_WHITELIST = frozenset({
    "refresh_public_dataset",
    "triage_tickets",
    "resolve_ticket",
    "sla_sweep",
    "escalate_overdue_tickets",
    "inventory_compliance_check",
    "create_patch_record",
    "mark_patch_status",
    "generate_monthly_operations_report",
    "generate_revenue_at_risk_report",
    "generate_audit_report",
    "create_change_request",
    "generate_change_request_docs",
})

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "refresh_public_dataset",
            "description": "Refresh the public data cache. Use source_id 'somerville' for Somerville traffic citations.",
            "parameters": {
                "type": "object",
                "properties": {"source_id": {"type": "string", "description": "Dataset source, e.g. somerville"}},
                "required": ["source_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "triage_tickets",
            "description": "List open help desk tickets; identifies access issues for triage.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "resolve_ticket",
            "description": "Mark a ticket as resolved by id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "resolution_note": {"type": "string"},
                },
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sla_sweep",
            "description": "List tickets that are overdue (past SLA due date).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_overdue_tickets",
            "description": "Escalate overdue open tickets by setting priority to HIGH.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inventory_compliance_check",
            "description": "List devices out of compliance (warranty expiring in 30 days or last patch > 90 days ago).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_patch_record",
            "description": "Create a new patch record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "patch_type": {"type": "string", "enum": ["application", "device"]},
                    "target_version": {"type": "string"},
                    "device_asset_tag": {"type": "string"},
                },
                "required": ["title", "patch_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mark_patch_status",
            "description": "Update a patch status (requested, scheduled, tested, deployed, verified).",
            "parameters": {
                "type": "object",
                "properties": {
                    "patch_id": {"type": "integer"},
                    "status": {"type": "string", "enum": ["requested", "scheduled", "tested", "deployed", "verified"]},
                },
                "required": ["patch_id", "status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_monthly_operations_report",
            "description": "Generate the monthly municipal court operations report bundle (PDF + summary) under reports/YYYY-MM.",
            "parameters": {
                "type": "object",
                "properties": {"period": {"type": "string", "description": "YYYY-MM, optional"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_revenue_at_risk_report",
            "description": "Generate Revenue at Risk (FTA) PDF under reports/YYYY-MM.",
            "parameters": {
                "type": "object",
                "properties": {"period": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_audit_report",
            "description": "Generate monthly audit report (text) under reports/YYYY-MM.",
            "parameters": {
                "type": "object",
                "properties": {"period": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_change_request",
            "description": "Create a change request record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "requested_by": {"type": "string"},
                    "current_process": {"type": "string"},
                    "proposed_change": {"type": "string"},
                    "impact_users": {"type": "string"},
                    "impact_data": {"type": "string"},
                    "impact_security": {"type": "string"},
                },
                "required": ["title", "requested_by", "current_process", "proposed_change"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_change_request_docs",
            "description": "Generate functional spec, SOP update, and release notes for a change request under docs/generated.",
            "parameters": {
                "type": "object",
                "properties": {"change_request_id": {"type": "integer"}},
                "required": ["change_request_id"],
            },
        },
    },
]


def run_tool(
    db: Session,
    user_id: int | None,
    tool_name: str,
    arguments: dict[str, Any],
    dry_run: bool = False,
) -> dict[str, Any]:
    if tool_name not in TOOL_WHITELIST:
        return {"success": False, "error": f"Tool not whitelisted: {tool_name}"}
    if dry_run:
        log_agent_tool(db, user_id, tool_name, arguments, "dry_run: no execution")
        return {"success": True, "dry_run": True, "message": "No changes made (dry run)."}

    try:
        result = _execute_tool(db, tool_name, arguments)
        summary = str(result)[:500]
        log_agent_tool(db, user_id, tool_name, arguments, summary)
        return {"success": True, "result": result}
    except Exception as e:
        err_msg = str(e)[:500]
        log_agent_tool(db, user_id, tool_name, arguments, f"error: {err_msg}")
        return {"success": False, "error": str(e)}


def _execute_tool(db: Session, tool_name: str, args: dict[str, Any]) -> Any:
    today = date.today()

    if tool_name == "refresh_public_dataset":
        source_id = (args.get("source_id") or "somerville").strip().lower()
        if source_id != "somerville":
            return {"message": f"Unknown source_id: {source_id}. Only somerville is supported."}
        path = download_somerville_citations(force=True)
        return {"path": str(path), "source_id": source_id}

    if tool_name == "triage_tickets":
        open_tickets = (
            db.query(Ticket)
            .filter(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .order_by(Ticket.created_at.desc())
            .limit(50)
            .all()
        )
        access_issues = [t for t in open_tickets if t.category == TicketCategory.ACCESS]
        return {
            "open_count": len(open_tickets),
            "access_issues": [{"id": t.id, "title": t.title} for t in access_issues],
        }

    if tool_name == "resolve_ticket":
        tid = int(args["ticket_id"])
        ticket = db.get(Ticket, tid)
        if not ticket:
            return {"error": "Ticket not found"}
        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = datetime.utcnow()
        db.add(ticket)
        db.commit()
        return {"ticket_id": tid, "status": "resolved"}

    if tool_name == "sla_sweep":
        overdue = [
            t
            for t in db.query(Ticket)
            .filter(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .all()
            if t.is_overdue()
        ]
        return {"overdue_count": len(overdue), "ticket_ids": [t.id for t in overdue]}

    if tool_name == "escalate_overdue_tickets":
        overdue = [
            t
            for t in db.query(Ticket)
            .filter(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .all()
            if t.is_overdue()
        ]
        for t in overdue:
            t.priority = TicketPriority.HIGH
            db.add(t)
        db.commit()
        return {"escalated_count": len(overdue), "ticket_ids": [t.id for t in overdue]}

    if tool_name == "inventory_compliance_check":
        risky = []
        for d in db.query(Device).all():
            if d.is_warranty_expiring_within_days(30):
                risky.append({"asset_tag": d.asset_tag, "reason": "warranty_expiring"})
            elif d.last_patch_date and (today - d.last_patch_date).days > 90:
                risky.append({"asset_tag": d.asset_tag, "reason": "patch_overdue"})
        return {"out_of_compliance_count": len(risky), "devices": risky}

    if tool_name == "create_patch_record":
        pt = (args.get("patch_type") or "application").lower()
        patch_type = PatchType.DEVICE if pt == "device" else PatchType.APPLICATION
        p = Patch(
            title=args["title"],
            type=patch_type,
            status=PatchStatus.REQUESTED,
            target_version=args.get("target_version"),
            device_asset_tag=args.get("device_asset_tag"),
            requested_date=today,
            scheduled_date=today + timedelta(days=7),
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        return {"patch_id": p.id, "title": p.title}

    if tool_name == "mark_patch_status":
        pid = int(args["patch_id"])
        st = (args.get("status") or "deployed").lower()
        status_map = {
            "requested": PatchStatus.REQUESTED,
            "scheduled": PatchStatus.SCHEDULED,
            "tested": PatchStatus.TESTED,
            "deployed": PatchStatus.DEPLOYED,
            "verified": PatchStatus.VERIFIED,
        }
        status = status_map.get(st)
        if not status:
            return {"error": f"Invalid status: {st}"}
        patch = db.get(Patch, pid)
        if not patch:
            return {"error": "Patch not found"}
        patch.status = status
        if status == PatchStatus.DEPLOYED and not patch.deployed_date:
            patch.deployed_date = today
        if status == PatchStatus.VERIFIED:
            patch.verified_date = today
        db.add(patch)
        db.commit()
        return {"patch_id": pid, "status": st}

    if tool_name == "generate_monthly_operations_report":
        period = (args.get("period") or today.strftime("%Y-%m")).strip()
        run_monthly_report(db, period=period)
        report_dir = REPORT_ROOT / period
        return {"period": period, "path": f"reports/{period}/", "files": list(report_dir.iterdir()) if report_dir.exists() else []}

    if tool_name == "generate_revenue_at_risk_report":
        period = (args.get("period") or today.strftime("%Y-%m")).strip()
        run_revenue_at_risk_report(db, period=period)
        return {"period": period, "path": f"reports/{period}/revenue_at_risk_fta.pdf"}

    if tool_name == "generate_audit_report":
        period = (args.get("period") or today.strftime("%Y-%m")).strip()
        path = generate_audit_report(db, period=period)
        try:
            rel = path.relative_to(REPORT_ROOT.parent)
        except ValueError:
            rel = path
        return {"period": period, "path": str(rel)}

    if tool_name == "create_change_request":
        cr = ChangeRequest(
            title=args["title"],
            requested_by=args["requested_by"],
            current_process=args.get("current_process") or "",
            proposed_change=args["proposed_change"],
            impact_users=args.get("impact_users") or "",
            impact_data=args.get("impact_data") or "",
            impact_security=args.get("impact_security") or "",
            status=ChangeRequestStatus.DRAFT,
        )
        db.add(cr)
        db.commit()
        db.refresh(cr)
        return {"change_request_id": cr.id, "title": cr.title}

    if tool_name == "generate_change_request_docs":
        crid = int(args["change_request_id"])
        cr = db.get(ChangeRequest, crid)
        if not cr:
            return {"error": "Change request not found"}
        paths = generate_change_request_docs(cr)
        return {"change_request_id": crid, "paths": [str(p.relative_to(DOCS_GENERATED.parent)) for p in paths.values()]}

    return {"error": f"Unknown tool: {tool_name}"}
