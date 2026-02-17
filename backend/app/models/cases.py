from datetime import datetime, date
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SqlEnum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CaseStatus(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    DISPOSED = "disposed"
    DISMISSED = "dismissed"
    DEFERRED = "deferred"
    WARRANT = "warrant"
    PAID = "paid"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    defendant_name: Mapped[str] = mapped_column(String(128))
    charge_type: Mapped[str] = mapped_column(String(128))
    status: Mapped[CaseStatus] = mapped_column(SqlEnum(CaseStatus), index=True)
    court: Mapped[str] = mapped_column(String(64))
    courtroom: Mapped[str | None] = mapped_column(String(64), nullable=True)
    clerk: Mapped[str | None] = mapped_column(String(128), nullable=True)
    judge: Mapped[str | None] = mapped_column(String(128), nullable=True)

    filing_date: Mapped[date] = mapped_column(Date, index=True)
    hearing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    disposition_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    fine_amount: Mapped[float] = mapped_column(Float, default=0.0)
    amount_paid: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def case_age_days(self) -> int:
        return (date.today() - self.filing_date).days

    def time_to_disposition_days(self) -> int | None:
        if not self.disposition_date:
            return None
        return (self.disposition_date - self.filing_date).days

