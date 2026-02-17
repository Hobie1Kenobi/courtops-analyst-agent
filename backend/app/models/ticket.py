from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TicketCategory(str, Enum):
    APPLICATION = "application"
    HARDWARE = "hardware"
    ACCESS = "access"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[TicketCategory] = mapped_column(SqlEnum(TicketCategory), index=True)
    priority: Mapped[TicketPriority] = mapped_column(SqlEnum(TicketPriority), index=True)
    status: Mapped[TicketStatus] = mapped_column(SqlEnum(TicketStatus), index=True, default=TicketStatus.OPEN)

    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    requester = relationship("User", foreign_keys=[requester_id])
    assignee = relationship("User", foreign_keys=[assignee_id])

    def is_overdue(self) -> bool:
        return self.due_at is not None and self.status not in {
            TicketStatus.RESOLVED,
            TicketStatus.CLOSED,
        } and datetime.utcnow() > self.due_at

    def compute_sla_hours(self) -> int:
        """Simple SLA hours based on priority."""
        mapping = {
            TicketPriority.LOW: 72,
            TicketPriority.MEDIUM: 48,
            TicketPriority.HIGH: 24,
            TicketPriority.CRITICAL: 4,
        }
        return mapping[self.priority]

    def set_due_from_sla(self) -> None:
        hours = self.compute_sla_hours()
        self.due_at = self.created_at + timedelta(hours=hours)

