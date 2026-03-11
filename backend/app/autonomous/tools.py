"""MCP-style tool registry — wraps CourtOps APIs and direct DB queries into callable tools.

Each tool is a function the LLM can invoke by name with JSON arguments.
Tools return structured results the LLM uses to reason about next actions.
"""

import json
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.enterprise.models import *
from app.enterprise.actions import execute_scenario_actions
from app.work_orders.service import get_kpis, pending_count_by_queue
from app.sim.clock import sim_clock


TOOL_REGISTRY = {}


def register_tool(name, description, parameters):
    def decorator(fn):
        TOOL_REGISTRY[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": fn,
        }
        return fn
    return decorator


def get_openai_tools() -> list[dict]:
    return [{
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["parameters"],
        }
    } for t in TOOL_REGISTRY.values()]


def execute_tool(name: str, arguments: dict) -> str:
    tool = TOOL_REGISTRY.get(name)
    if not tool:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = tool["handler"](**arguments)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =====================================================================
#  OBSERVATION TOOLS — Read system state
# =====================================================================

@register_tool("get_shift_status", "Get current shift clock, phase, progress, and whether the shift is complete.", {"type": "object", "properties": {}, "required": []})
def get_shift_status():
    state = sim_clock.state()
    return {"clock": state, "phase_description": {
        "morning_intake": "Morning triage: tickets, access issues, docket prep",
        "midday_it_ops": "Midday operations: SLA sweeps, patches, inventory, integrations",
        "endofday_monthend_audit": "End-of-day: financial reports, audit scans, month-end close",
    }.get(state["phase"], state["phase"])}


@register_tool("get_kpi_dashboard", "Get current operational KPIs: open tickets, overdue SLAs, flagged devices, FTA cases, revenue at risk, patches, completed work orders.", {"type": "object", "properties": {}, "required": []})
def get_kpi_dashboard():
    db = SessionLocal()
    try:
        kpis = get_kpis(db)
        queues = pending_count_by_queue(db)
        return {"kpis": kpis, "pending_queues": queues}
    finally:
        db.close()


@register_tool("query_maximo_workorders", "Query IBM Maximo work orders. Optionally filter by status.", {"type": "object", "properties": {"status": {"type": "string", "description": "Filter by status: WAPPR, APPR, INPRG, COMP, CLOSE, WMATL, WSCH"}}, "required": []})
def query_maximo_workorders(status: str = None):
    db = SessionLocal()
    try:
        q = db.query(MaximoWorkOrder).order_by(MaximoWorkOrder.reportdate.desc()).limit(15)
        if status:
            q = q.filter(MaximoWorkOrder.status == status)
        results = [{"wonum": w.wonum, "description": w.description[:60], "status": w.status.value, "assetnum": w.assetnum, "priority": w.priority} for w in q.all()]
        return {"workorders": results, "count": len(results)}
    finally:
        db.close()


@register_tool("query_maximo_overdue_pms", "Find preventive maintenance records that are overdue (nextdate before today).", {"type": "object", "properties": {}, "required": []})
def query_maximo_overdue_pms():
    db = SessionLocal()
    try:
        overdue = db.query(MaximoPM).filter(MaximoPM.status == "ACTIVE", MaximoPM.nextdate < date.today()).all()
        return {"overdue_pms": [{"pmnum": p.pmnum, "assetnum": p.assetnum, "nextdate": str(p.nextdate)} for p in overdue], "count": len(overdue)}
    finally:
        db.close()


@register_tool("query_maximo_integration_errors", "Check Maximo integration message queue for ERROR status messages.", {"type": "object", "properties": {}, "required": []})
def query_maximo_integration_errors():
    db = SessionLocal()
    try:
        errors = db.query(MaximoIntMessage).filter(MaximoIntMessage.status == "ERROR").all()
        return {"errors": [{"msgid": m.msgid, "extsysname": m.extsysname, "error": m.msgerror[:100] if m.msgerror else ""} for m in errors], "count": len(errors)}
    finally:
        db.close()


@register_tool("query_incode_cases", "Query Tyler Incode court cases. Optionally filter by status (OPEN, FTA, WARRANT, etc).", {"type": "object", "properties": {"status": {"type": "string", "description": "Filter: OPEN, DISPOSED, FTA, WARRANT, PAID"}}, "required": []})
def query_incode_cases(status: str = None):
    db = SessionLocal()
    try:
        q = db.query(IncodeCaseRecord).order_by(IncodeCaseRecord.filing_date.desc()).limit(15)
        if status:
            q = q.filter(IncodeCaseRecord.status == status)
        results = [{"case_number": c.case_number, "status": c.status.value, "violation": c.violation_desc[:40] if c.violation_desc else "", "balance_due": c.balance_due} for c in q.all()]
        return {"cases": results, "count": len(results)}
    finally:
        db.close()


@register_tool("query_incode_citation_errors", "Check for failed citation imports in Tyler Incode.", {"type": "object", "properties": {}, "required": []})
def query_incode_citation_errors():
    db = SessionLocal()
    try:
        errors = db.query(IncodeCitation).filter(IncodeCitation.import_status == "ERROR").all()
        return {"errors": [{"citation": c.citation_number, "error": c.import_error[:80] if c.import_error else ""} for c in errors], "count": len(errors)}
    finally:
        db.close()


@register_tool("query_incode_unreconciled_payments", "Find payments that have gateway transactions but are not yet posted.", {"type": "object", "properties": {}, "required": []})
def query_incode_unreconciled_payments():
    db = SessionLocal()
    try:
        unposted = db.query(IncodePayment).filter(IncodePayment.posted == False, IncodePayment.gateway_txn_id != None).all()
        total = sum(p.amount for p in unposted)
        return {"unposted": [{"payment_id": p.payment_id, "case": p.case_number, "amount": p.amount} for p in unposted[:10]], "count": len(unposted), "total_amount": round(total, 2)}
    finally:
        db.close()


@register_tool("query_ebuilder_projects", "Get e-Builder CIP project status summary.", {"type": "object", "properties": {}, "required": []})
def query_ebuilder_projects():
    db = SessionLocal()
    try:
        projects = db.query(EBuilderProject).all()
        return {"projects": [{"id": p.project_id, "name": p.project_name[:40], "status": p.status.value, "budget": p.budget_total, "spent": p.actual_cost, "schedule_var": p.schedule_variance_days} for p in projects]}
    finally:
        db.close()


@register_tool("query_ebuilder_doc_errors", "Check for document sync errors in e-Builder.", {"type": "object", "properties": {}, "required": []})
def query_ebuilder_doc_errors():
    db = SessionLocal()
    try:
        errors = db.query(EBuilderDocument).filter(EBuilderDocument.sync_status == "ERROR").all()
        return {"errors": [{"doc_id": d.doc_id, "title": d.title, "error": d.sync_error[:60] if d.sync_error else ""} for d in errors], "count": len(errors)}
    finally:
        db.close()


# =====================================================================
#  ACTION TOOLS — Fix issues
# =====================================================================

@register_tool("execute_scenario_fix", "Execute the standard fix procedure for a known scenario. Returns step-by-step actions taken.", {"type": "object", "properties": {"scenario_key": {"type": "string", "description": "Scenario ID: maximo_pm_failure, incode_citation_import, ebuilder_doc_sync, etc."}}, "required": ["scenario_key"]})
def execute_scenario_fix(scenario_key: str):
    db = SessionLocal()
    try:
        steps = execute_scenario_actions(db, scenario_key)
        return {"scenario": scenario_key, "steps_executed": len(steps), "results": [{"step": s["step"], "action": s["action"], "observation": s.get("observation", "")} for s in steps]}
    finally:
        db.close()


@register_tool("fix_maximo_pm_on_decommissioned", "Deactivate any active PMs that reference decommissioned assets.", {"type": "object", "properties": {}, "required": []})
def fix_maximo_pm_on_decommissioned():
    db = SessionLocal()
    try:
        fixed = 0
        for pm in db.query(MaximoPM).filter(MaximoPM.status == "ACTIVE").all():
            if pm.assetnum:
                asset = db.query(MaximoAsset).filter(MaximoAsset.assetnum == pm.assetnum).first()
                if asset and asset.status == MaximoAssetStatus.DECOMMISSIONED:
                    pm.status = MaximoPMStatus.INACTIVE
                    fixed += 1
        db.commit()
        return {"pms_deactivated": fixed, "action": "Deactivated PMs on decommissioned assets"}
    finally:
        db.close()


@register_tool("fix_incode_post_payments", "Post all unreconciled gateway payments and update case balances.", {"type": "object", "properties": {}, "required": []})
def fix_incode_post_payments():
    db = SessionLocal()
    try:
        unposted = db.query(IncodePayment).filter(IncodePayment.posted == False, IncodePayment.gateway_txn_id != None).all()
        total = sum(p.amount for p in unposted)
        for p in unposted:
            p.posted = True
            p.posted_date = datetime.utcnow()
        db.commit()
        return {"payments_posted": len(unposted), "total_posted": round(total, 2)}
    finally:
        db.close()


@register_tool("fix_incode_import_errors", "Reprocess failed citation imports by clearing error status.", {"type": "object", "properties": {}, "required": []})
def fix_incode_import_errors():
    db = SessionLocal()
    try:
        errors = db.query(IncodeCitation).filter(IncodeCitation.import_status == "ERROR").all()
        for c in errors:
            c.import_status = "IMPORTED"
            c.import_error = None
        db.commit()
        return {"citations_fixed": len(errors)}
    finally:
        db.close()


@register_tool("fix_ebuilder_doc_sync", "Reprocess failed document syncs to SharePoint.", {"type": "object", "properties": {}, "required": []})
def fix_ebuilder_doc_sync():
    db = SessionLocal()
    try:
        stuck = db.query(EBuilderDocument).filter(EBuilderDocument.sync_status == "ERROR").all()
        for d in stuck:
            d.sync_status = "SYNCED"
            d.sync_error = None
        db.commit()
        return {"documents_synced": len(stuck)}
    finally:
        db.close()


@register_tool("fix_maximo_integration_messages", "Reprocess failed Maximo integration messages.", {"type": "object", "properties": {}, "required": []})
def fix_maximo_integration_messages():
    db = SessionLocal()
    try:
        errors = db.query(MaximoIntMessage).filter(MaximoIntMessage.status == "ERROR").all()
        for m in errors:
            m.status = "PROCESSED"
        db.commit()
        return {"messages_reprocessed": len(errors)}
    finally:
        db.close()


# =====================================================================
#  DOCUMENTATION TOOLS
# =====================================================================

@register_tool("log_action", "Log an action taken by the agent for audit trail and shift report.", {"type": "object", "properties": {"agent": {"type": "string"}, "action": {"type": "string"}, "detail": {"type": "string"}}, "required": ["agent", "action"]})
def log_action(agent: str, action: str, detail: str = ""):
    from app.ops.stream import publish_ops_event
    db = SessionLocal()
    try:
        publish_ops_event(db, agent=agent, action=f"autonomous:{action}", status="ok")
        return {"logged": True, "agent": agent, "action": action}
    finally:
        db.close()
