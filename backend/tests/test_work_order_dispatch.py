"""Test work order dispatch routes to correct queues."""

from app.work_orders.models import (
    QUEUE_ROUTING,
    WorkOrderQueue,
    WorkOrderType,
)


def test_queue_routing_completeness():
    for wo_type in WorkOrderType:
        assert wo_type in QUEUE_ROUTING, f"{wo_type} has no queue routing"


def test_clerk_ops_routing():
    assert QUEUE_ROUTING[WorkOrderType.TICKET_ACCESS_RESOLUTION] == WorkOrderQueue.CLERK_OPS
    assert QUEUE_ROUTING[WorkOrderType.CASE_DISPOSITION_METRICS] == WorkOrderQueue.CLERK_OPS
    assert QUEUE_ROUTING[WorkOrderType.CHANGE_REQUEST_DRAFT] == WorkOrderQueue.CLERK_OPS


def test_it_ops_routing():
    assert QUEUE_ROUTING[WorkOrderType.SLA_SWEEP_ESCALATION] == WorkOrderQueue.IT_OPS
    assert QUEUE_ROUTING[WorkOrderType.INVENTORY_COMPLIANCE_CHECK] == WorkOrderQueue.IT_OPS
    assert QUEUE_ROUTING[WorkOrderType.PATCH_RECORD_CREATE] == WorkOrderQueue.IT_OPS


def test_finance_audit_routing():
    assert QUEUE_ROUTING[WorkOrderType.REVENUE_AT_RISK_FTA] == WorkOrderQueue.FINANCE_AUDIT
    assert QUEUE_ROUTING[WorkOrderType.MONTHLY_OPS_PACKAGE] == WorkOrderQueue.FINANCE_AUDIT
    assert QUEUE_ROUTING[WorkOrderType.AUDIT_LOG_SCAN] == WorkOrderQueue.FINANCE_AUDIT
