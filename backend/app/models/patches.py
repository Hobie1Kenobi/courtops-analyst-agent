from datetime import datetime, date
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SqlEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PatchType(str, Enum):
    APPLICATION = "application"
    DEVICE = "device"


class PatchStatus(str, Enum):
    REQUESTED = "requested"
    SCHEDULED = "scheduled"
    TESTED = "tested"
    DEPLOYED = "deployed"
    VERIFIED = "verified"


class Patch(Base):
    __tablename__ = "patches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    type: Mapped[PatchType] = mapped_column(SqlEnum(PatchType), index=True)
    status: Mapped[PatchStatus] = mapped_column(SqlEnum(PatchStatus), index=True)
    target_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device_asset_tag: Mapped[str | None] = mapped_column(String(64), nullable=True)

    requested_date: Mapped[date] = mapped_column(Date)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deployed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    verified_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    testing_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_log: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

