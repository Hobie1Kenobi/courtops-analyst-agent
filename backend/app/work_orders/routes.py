from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.work_orders.models import WorkOrder, WorkOrderStatus
from app.work_orders.service import get_kpis


router = APIRouter(prefix="/work-orders", tags=["work-orders"])


class WorkOrderRead(BaseModel):
    id: int
    type: str
    status: str
    queue: str
    priority: int
    assigned_agent: str | None = None
    completion_note: str | None = None
    sim_phase: str | None = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[WorkOrderRead])
def list_work_orders(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(WorkOrder).order_by(WorkOrder.created_at.desc()).limit(200)
    if status:
        q = q.filter(WorkOrder.status == status)
    return [WorkOrderRead.model_validate(wo) for wo in q.all()]


@router.get("/kpis")
def kpis(db: Session = Depends(get_db)):
    return get_kpis(db)
