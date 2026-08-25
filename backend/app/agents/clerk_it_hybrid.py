"""Clerk+IT Hybrid agent: handles tickets, access issues, case metrics, change requests."""

import json
from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.models import Ticket, TicketStatus, TicketCategory, Case, CaseStatus, ChangeRequest
from app.work_orders.models import WorkOrder, WorkOrderQueue, WorkOrderType


class ClerkITHybridAgent(BaseAgent):
    name = "clerk_it_hybrid"
    queue = WorkOrderQueue.CLERK_OPS

    def execute(self, db: Session, wo: WorkOrder) -> tuple[list[str], list[dict], str]:
        if wo.type == WorkOrderType.TICKET_ACCESS_RESOLUTION:
            return self._resolve_access_tickets(db)
        elif wo.type == WorkOrderType.CASE_DISPOSITION_METRICS:
            return self._case_metrics(db)
        elif wo.type == WorkOrderType.CHANGE_REQUEST_DRAFT:
            return self._draft_change_request(db)
        return ["no_op"], [], "Unhandled work order type"

    def _resolve_access_tickets(self, db: Session):
        access_tickets = (
            db.query(Ticket)
            .filter(Ticket.category == TicketCategory.ACCESS, Ticket.status == TicketStatus.OPEN)
            .limit(3)
            .all()
        )
        actions = []
        for t in access_tickets:
            t.status = TicketStatus.RESOLVED
            from datetime import datetime
            t.resolved_at = datetime.utcnow()
            actions.append(f"resolved_ticket:{t.id}:{t.title}")
        db.commit()
        count = len(access_tickets)
        return actions, [], f"Resolved {count} access tickets"

    def _case_metrics(self, db: Session):
        cases = db.query(Case).all()
        by_month: dict[str, list] = defaultdict(list)
        for c in cases:
            by_month[c.filing_date.strftime("%Y-%m")].append(c)
        summary = []
        for month, cs in sorted(by_month.items())[-3:]:
            disposed = sum(1 for c in cs if c.status in {CaseStatus.DISPOSED, CaseStatus.DISMISSED, CaseStatus.PAID})
            summary.append(f"{month}: {len(cs)} total, {disposed} disposed")
        actions = ["computed_case_disposition_metrics"]
        return actions, [], f"Case metrics: {'; '.join(summary)}"

    def _draft_change_request(self, db: Session):
        crs = db.query(ChangeRequest).all()
        if crs:
            cr = crs[0]
            actions = [f"reviewed_change_request:{cr.id}:{cr.title}"]
            return actions, [], f"Reviewed CR: {cr.title}"
        return ["no_pending_change_requests"], [], "No change requests to review"
