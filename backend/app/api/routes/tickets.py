from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models import Ticket, TicketStatus, User, UserRole
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdate


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/", response_model=List[TicketRead])
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Ticket]:
    # For now, all authenticated users can list tickets.
    return db.query(Ticket).order_by(Ticket.created_at.desc()).limit(200).all()


@router.post("/", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    ticket = Ticket(
        title=data.title,
        description=data.description,
        category=data.category,
        priority=data.priority,
        status=TicketStatus.OPEN,
        requester_id=current_user.id,
        assignee_id=data.assignee_id,
    )
    ticket.set_due_from_sla()
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Simple permission rule: requester, assignee, analyst, IT, or supervisor may update
    if (
        current_user.id not in {ticket.requester_id, ticket.assignee_id}
        and current_user.role
        not in {UserRole.ANALYST, UserRole.IT_SUPPORT, UserRole.SUPERVISOR}
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update ticket")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)

    if data.status in {TicketStatus.RESOLVED, TicketStatus.CLOSED} and ticket.resolved_at is None:
        from datetime import datetime as dt

        ticket.resolved_at = dt.utcnow()

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/sla/summary", tags=["tickets"])
def sla_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.SUPERVISOR)),
) -> dict:
    total = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status != TicketStatus.CLOSED).count()
    overdue = (
        db.query(Ticket)
        .filter(
            Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
        )
        .all()
    )
    overdue_count = sum(1 for t in overdue if t.is_overdue())
    return {
        "total": total,
        "open": open_tickets,
        "overdue": overdue_count,
    }

