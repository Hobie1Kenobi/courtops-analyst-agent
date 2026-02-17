from datetime import datetime, date
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SqlEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class DeviceStatus(str, Enum):
    IN_SERVICE = "in_service"
    IN_REPAIR = "in_repair"
    RETIRED = "retired"
    LOST = "lost"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_tag: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(64))
    location: Mapped[str] = mapped_column(String(128))
    assigned_user: Mapped[str | None] = mapped_column(String(128), nullable=True)
    warranty_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_patch_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[DeviceStatus] = mapped_column(SqlEnum(DeviceStatus), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_warranty_expiring_within_days(self, days: int) -> bool:
        if not self.warranty_end:
            return False
        return (self.warranty_end - date.today()).days <= days

