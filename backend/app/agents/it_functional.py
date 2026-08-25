"""IT Functional Analyst agent: SLA sweeps, inventory compliance, patch management."""

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.models import (
    Device, DeviceStatus, Patch, PatchStatus, PatchType,
    Ticket, TicketPriority, TicketStatus,
)
from app.work_orders.models import WorkOrder, WorkOrderQueue, WorkOrderType


class ITFunctionalAgent(BaseAgent):
    name = "it_functional_analyst"
    queue = WorkOrderQueue.IT_OPS

    def execute(self, db: Session, wo: WorkOrder) -> tuple[list[str], list[dict], str]:
        if wo.type == WorkOrderType.SLA_SWEEP_ESCALATION:
            return self._sla_sweep(db)
        elif wo.type == WorkOrderType.INVENTORY_COMPLIANCE_CHECK:
            return self._inventory_check(db)
        elif wo.type == WorkOrderType.PATCH_RECORD_CREATE:
            return self._create_patches(db)
        elif wo.type == WorkOrderType.TICKET_ACCESS_RESOLUTION:
            return self._handle_ticket(db)
        return ["no_op"], [], "Unhandled"

    def _sla_sweep(self, db: Session):
        open_tickets = db.query(Ticket).filter(
            Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
        ).all()
        overdue = [t for t in open_tickets if t.is_overdue()]
        actions = []
        for t in overdue[:5]:
            t.priority = TicketPriority.HIGH
            actions.append(f"escalated_ticket:{t.id}")
        db.commit()
        return actions, [], f"SLA sweep: {len(overdue)} overdue, escalated {len(actions)}"

    def _inventory_check(self, db: Session):
        devices = db.query(Device).filter(Device.status == DeviceStatus.IN_SERVICE).all()
        flagged = []
        for d in devices:
            if d.is_warranty_expiring_within_days(30):
                flagged.append(f"warranty_expiring:{d.asset_tag}")
            if d.last_patch_date and (date.today() - d.last_patch_date).days > 60:
                flagged.append(f"patch_overdue:{d.asset_tag}")
        return flagged[:10], [], f"Inventory check: {len(flagged)} issues found"

    def _create_patches(self, db: Session):
        devices = db.query(Device).filter(Device.status == DeviceStatus.IN_SERVICE).all()
        created = 0
        actions = []
        for d in devices[:3]:
            if d.last_patch_date and (date.today() - d.last_patch_date).days > 60:
                patch = Patch(
                    title=f"Security Update - {d.asset_tag}",
                    type=PatchType.DEVICE, status=PatchStatus.REQUESTED,
                    device_asset_tag=d.asset_tag,
                    requested_date=date.today(),
                    scheduled_date=date.today() + timedelta(days=7),
                    change_log=f"Auto-created by IT Functional Analyst for {d.asset_tag}",
                )
                db.add(patch)
                actions.append(f"created_patch:{d.asset_tag}")
                created += 1
        db.commit()
        return actions, [], f"Created {created} patch records"

    def _handle_ticket(self, db: Session):
        ticket = db.query(Ticket).filter(Ticket.status == TicketStatus.OPEN).first()
        if ticket:
            ticket.status = TicketStatus.IN_PROGRESS
            db.commit()
            return [f"ticket_in_progress:{ticket.id}"], [], f"Picked up ticket #{ticket.id}"
        return ["no_tickets"], [], "No open tickets"
