from datetime import datetime, timedelta

from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus


def test_ticket_sla_due_date():
    created_at = datetime(2024, 1, 1, 8, 0, 0)
    ticket = Ticket(
        id=1,
        title="Test",
        description="Test SLA",
        category=TicketCategory.APPLICATION,
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        requester_id=1,
        assignee_id=2,
        created_at=created_at,
    )
    ticket.set_due_from_sla()
    assert ticket.due_at == created_at + timedelta(hours=ticket.compute_sla_hours())

