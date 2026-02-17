from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.models.patches import PatchStatus, PatchType


class PatchBase(BaseModel):
    title: str
    type: PatchType
    status: PatchStatus
    target_version: Optional[str] = None
    device_asset_tag: Optional[str] = None
    requested_date: date
    scheduled_date: Optional[date] = None
    deployed_date: Optional[date] = None
    verified_date: Optional[date] = None
    testing_notes: Optional[str] = None
    change_log: Optional[str] = None


class PatchCreate(PatchBase):
    pass


class PatchRead(PatchBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

