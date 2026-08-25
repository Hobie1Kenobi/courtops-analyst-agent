import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.db.session import Base


class WorkOrderType(str, enum.Enum):
    TICKET_ACCESS_RESOLUTION = "ticket_access_resolution"
    SLA_SWEEP_ESCALATION = "sla_sweep_escalation"
    INVENTORY_COMPLIANCE_CHECK = "inventory_compliance_check"
    PATCH_RECORD_CREATE = "patch_record_create"
    CASE_DISPOSITION_METRICS = "case_disposition_metrics"
    REVENUE_AT_RISK_FTA = "revenue_at_risk_fta"
    MONTHLY_OPS_PACKAGE = "monthly_ops_package"
    AUDIT_LOG_SCAN = "audit_log_scan"
    CHANGE_REQUEST_DRAFT = "change_request_draft"


class WorkOrderStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkOrderQueue(str, enum.Enum):
    CLERK_OPS = "clerk_ops"
    IT_OPS = "it_ops"
    FINANCE_AUDIT = "finance_audit"


QUEUE_ROUTING: dict[WorkOrderType, WorkOrderQueue] = {
    WorkOrderType.TICKET_ACCESS_RESOLUTION: WorkOrderQueue.CLERK_OPS,
    WorkOrderType.SLA_SWEEP_ESCALATION: WorkOrderQueue.IT_OPS,
    WorkOrderType.INVENTORY_COMPLIANCE_CHECK: WorkOrderQueue.IT_OPS,
    WorkOrderType.PATCH_RECORD_CREATE: WorkOrderQueue.IT_OPS,
    WorkOrderType.CASE_DISPOSITION_METRICS: WorkOrderQueue.CLERK_OPS,
    WorkOrderType.REVENUE_AT_RISK_FTA: WorkOrderQueue.FINANCE_AUDIT,
    WorkOrderType.MONTHLY_OPS_PACKAGE: WorkOrderQueue.FINANCE_AUDIT,
    WorkOrderType.AUDIT_LOG_SCAN: WorkOrderQueue.FINANCE_AUDIT,
    WorkOrderType.CHANGE_REQUEST_DRAFT: WorkOrderQueue.CLERK_OPS,
}


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(WorkOrderType), nullable=False, index=True)
    status = Column(Enum(WorkOrderStatus), nullable=False, default=WorkOrderStatus.PENDING, index=True)
    queue = Column(Enum(WorkOrderQueue), nullable=False, index=True)
    priority = Column(Integer, nullable=False, default=5)
    sla_due = Column(DateTime, nullable=True)
    assigned_agent = Column(String, nullable=True)
    evidence_ids = Column(Text, nullable=True)
    actions_taken = Column(Text, nullable=True)
    artifacts = Column(Text, nullable=True)
    audit_event_id = Column(Integer, nullable=True)
    completion_note = Column(Text, nullable=True)
    sim_phase = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
