"""Phase-based event generator that creates work orders.

Full-day mode generates a realistic municipal court workload:
~30-40 work orders per phase, ~100+ for a complete shift.
"""

from sqlalchemy.orm import Session

from app.work_orders.models import WorkOrderType
from app.work_orders.service import create_work_order


PHASE_WORK_ORDERS_FULL: dict[str, list[tuple[WorkOrderType, int, int]]] = {
    "morning_intake": [
        (WorkOrderType.TICKET_ACCESS_RESOLUTION, 2, 6),
        (WorkOrderType.CASE_DISPOSITION_METRICS, 4, 2),
        (WorkOrderType.CHANGE_REQUEST_DRAFT, 6, 2),
        (WorkOrderType.SLA_SWEEP_ESCALATION, 3, 3),
        (WorkOrderType.INVENTORY_COMPLIANCE_CHECK, 5, 1),
        (WorkOrderType.TICKET_ACCESS_RESOLUTION, 3, 4),
        (WorkOrderType.CASE_DISPOSITION_METRICS, 5, 1),
        (WorkOrderType.PATCH_RECORD_CREATE, 4, 2),
    ],
    "midday_it_ops": [
        (WorkOrderType.SLA_SWEEP_ESCALATION, 1, 5),
        (WorkOrderType.INVENTORY_COMPLIANCE_CHECK, 2, 4),
        (WorkOrderType.PATCH_RECORD_CREATE, 3, 5),
        (WorkOrderType.TICKET_ACCESS_RESOLUTION, 5, 3),
        (WorkOrderType.SLA_SWEEP_ESCALATION, 2, 3),
        (WorkOrderType.INVENTORY_COMPLIANCE_CHECK, 3, 2),
        (WorkOrderType.PATCH_RECORD_CREATE, 4, 3),
        (WorkOrderType.CASE_DISPOSITION_METRICS, 5, 1),
        (WorkOrderType.CHANGE_REQUEST_DRAFT, 6, 1),
    ],
    "endofday_monthend_audit": [
        (WorkOrderType.REVENUE_AT_RISK_FTA, 1, 3),
        (WorkOrderType.MONTHLY_OPS_PACKAGE, 2, 2),
        (WorkOrderType.AUDIT_LOG_SCAN, 3, 4),
        (WorkOrderType.CHANGE_REQUEST_DRAFT, 5, 2),
        (WorkOrderType.REVENUE_AT_RISK_FTA, 2, 2),
        (WorkOrderType.AUDIT_LOG_SCAN, 4, 3),
        (WorkOrderType.MONTHLY_OPS_PACKAGE, 3, 1),
        (WorkOrderType.SLA_SWEEP_ESCALATION, 4, 2),
        (WorkOrderType.CASE_DISPOSITION_METRICS, 5, 1),
    ],
}


def generate_phase_work_orders(db: Session, phase: str) -> list[int]:
    wo_defs = PHASE_WORK_ORDERS_FULL.get(phase, [])
    created_ids = []
    for wo_type, priority, count in wo_defs:
        for _ in range(count):
            wo = create_work_order(
                db,
                wo_type=wo_type,
                priority=priority,
                sla_minutes=30,
                sim_phase=phase,
            )
            created_ids.append(wo.id)
    return created_ids
