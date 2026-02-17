from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.ticket import TicketCategory, TicketPriority, TicketStatus


class TicketBase(BaseModel):
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority


class TicketCreate(TicketBase):
    assignee_id: Optional[int] = None


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assignee_id: Optional[int] = None


class TicketRead(TicketBase):
    id: int
    status: TicketStatus
    requester_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    due_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

