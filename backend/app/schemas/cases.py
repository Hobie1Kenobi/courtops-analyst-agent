from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.models.cases import CaseStatus


class CaseBase(BaseModel):
    case_number: str
    defendant_name: str
    charge_type: str
    status: CaseStatus
    court: str
    courtroom: Optional[str] = None
    clerk: Optional[str] = None
    judge: Optional[str] = None
    filing_date: date
    hearing_date: Optional[date] = None
    disposition_date: Optional[date] = None
    fine_amount: float
    amount_paid: float


class CaseCreate(CaseBase):
    pass


class CaseRead(CaseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    outstanding_balance: Optional[float] = None
    days_overdue: Optional[int] = None

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, **kwargs):
        inst = super().model_validate(obj, **kwargs)
        if hasattr(obj, "outstanding_balance") and callable(obj.outstanding_balance):
            inst.outstanding_balance = obj.outstanding_balance()
        elif hasattr(obj, "outstanding_balance"):
            inst.outstanding_balance = obj.outstanding_balance
        if hasattr(obj, "days_overdue") and callable(obj.days_overdue):
            inst.days_overdue = obj.days_overdue()
        elif hasattr(obj, "days_overdue"):
            inst.days_overdue = obj.days_overdue
        return inst


class CaseMetrics(BaseModel):
    month: str
    total_cases: int
    disposed_cases: int
    non_disposed_cases: int
    disposed_pct: float
    avg_case_age_days: float
    avg_time_to_disposition_days: Optional[float] = None

