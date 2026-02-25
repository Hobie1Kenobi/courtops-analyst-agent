"""Phase-based event generator that creates work orders."""

from sqlalchemy.orm import Session

from app.work_orders.models import WorkOrderType
from app.work_orders.service import create_work_order


PHASE_WORK_ORDERS: dict[str, list[tuple[WorkOrderType, int]]] = {
    "morning_intake": [
        (WorkOrderType.TICKET_ACCESS_RESOLUTION, 2),
        (WorkOrderType.CASE_DISPOSITION_METRICS, 4),
        (WorkOrderType.CHANGE_REQUEST_DRAFT, 6),
        (WorkOrderType.SLA_SWEEP_ESCALATION, 5),
    ],
    "midday_it_ops": [
        (WorkOrderType.SLA_SWEEP_ESCALATION, 1),
        (WorkOrderType.INVENTORY_COMPLIANCE_CHECK, 2),
        (WorkOrderType.PATCH_RECORD_CREATE, 3),
        (WorkOrderType.TICKET_ACCESS_RESOLUTION, 5),
    ],
    "endofday_monthend_audit": [
        (WorkOrderType.REVENUE_AT_RISK_FTA, 1),
        (WorkOrderType.MONTHLY_OPS_PACKAGE, 2),
        (WorkOrderType.AUDIT_LOG_SCAN, 3),
        (WorkOrderType.CHANGE_REQUEST_DRAFT, 5),
    ],
}


def generate_phase_work_orders(db: Session, phase: str) -> list[int]:
    wo_defs = PHASE_WORK_ORDERS.get(phase, [])
    created_ids = []
    for wo_type, priority in wo_defs:
        wo = create_work_order(
            db,
            wo_type=wo_type,
            priority=priority,
            sla_minutes=20,
            sim_phase=phase,
        )
        created_ids.append(wo.id)
    return created_ids
