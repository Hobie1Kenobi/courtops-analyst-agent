from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ChangeRequestStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class ChangeRequest(Base):
    __tablename__ = "change_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    requested_by: Mapped[str] = mapped_column(String(128))
    current_process: Mapped[str] = mapped_column(Text)
    proposed_change: Mapped[str] = mapped_column(Text)
    impact_users: Mapped[str] = mapped_column(Text)
    impact_data: Mapped[str] = mapped_column(Text)
    impact_security: Mapped[str] = mapped_column(Text)
    status: Mapped[ChangeRequestStatus] = mapped_column(SqlEnum(ChangeRequestStatus), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

