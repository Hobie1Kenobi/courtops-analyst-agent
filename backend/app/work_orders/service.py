import json
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.work_orders.models import (
    QUEUE_ROUTING,
    WorkOrder,
    WorkOrderQueue,
    WorkOrderStatus,
    WorkOrderType,
)


def create_work_order(
    db: Session,
    wo_type: WorkOrderType,
    priority: int = 5,
    sla_minutes: int = 30,
    evidence_ids: list[str] | None = None,
    sim_phase: str | None = None,
) -> WorkOrder:
    wo = WorkOrder(
        type=wo_type,
        status=WorkOrderStatus.PENDING,
        queue=QUEUE_ROUTING[wo_type],
        priority=priority,
        sla_due=datetime.utcnow() + timedelta(minutes=sla_minutes),
        evidence_ids=json.dumps(evidence_ids or []),
        sim_phase=sim_phase,
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    return wo


def claim_work_order(db: Session, queue: WorkOrderQueue, agent_name: str) -> WorkOrder | None:
    wo = (
        db.query(WorkOrder)
        .filter(
            WorkOrder.queue == queue,
            WorkOrder.status == WorkOrderStatus.PENDING,
        )
        .order_by(WorkOrder.priority.asc(), WorkOrder.created_at.asc())
        .first()
    )
    if wo is None:
        return None
    wo.status = WorkOrderStatus.ASSIGNED
    wo.assigned_agent = agent_name
    db.commit()
    db.refresh(wo)
    return wo


def complete_work_order(
    db: Session,
    wo: WorkOrder,
    actions: list[str],
    artifacts: list[dict] | None = None,
    note: str = "",
) -> WorkOrder:
    wo.status = WorkOrderStatus.COMPLETED
    wo.actions_taken = json.dumps(actions)
    wo.artifacts = json.dumps(artifacts or [])
    wo.completion_note = note
    db.commit()
    db.refresh(wo)
    return wo


def fail_work_order(db: Session, wo: WorkOrder, note: str = "") -> WorkOrder:
    wo.status = WorkOrderStatus.FAILED
    wo.completion_note = note
    db.commit()
    db.refresh(wo)
    return wo


def pending_count_by_queue(db: Session) -> dict[str, int]:
    results = {}
    for q in WorkOrderQueue:
        count = db.query(WorkOrder).filter(
            WorkOrder.queue == q,
            WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.ASSIGNED]),
        ).count()
        results[q.value] = count
    return results


def get_kpis(db: Session) -> dict:
    from app.models import Ticket, TicketStatus, Device, Case, CaseStatus, Patch
    open_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.OPEN).count()
    overdue_tickets = sum(1 for t in db.query(Ticket).filter(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])).all() if t.is_overdue())
    devices_flagged = sum(1 for d in db.query(Device).all() if d.is_warranty_expiring_within_days(30) or (d.last_patch_date and (datetime.utcnow().date() - d.last_patch_date).days > 60))
    fta_cases = db.query(Case).filter(Case.status.in_([CaseStatus.FTA, CaseStatus.WARRANT])).count()
    revenue_at_risk = sum(c.outstanding_balance() for c in db.query(Case).filter(Case.status.in_([CaseStatus.FTA, CaseStatus.WARRANT])).all())
    patches_created = db.query(Patch).count()
    completed_wos = db.query(WorkOrder).filter(WorkOrder.status == WorkOrderStatus.COMPLETED).count()
    return {
        "open_tickets": open_tickets,
        "overdue_slas": overdue_tickets,
        "devices_flagged": devices_flagged,
        "fta_cases": fta_cases,
        "revenue_at_risk": round(revenue_at_risk, 2),
        "patches_created": patches_created,
        "work_orders_completed": completed_wos,
    }
