from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.change_requests import ChangeRequestStatus


class ChangeRequestBase(BaseModel):
    title: str
    requested_by: str
    current_process: str
    proposed_change: str
    impact_users: str
    impact_data: str
    impact_security: str
    status: ChangeRequestStatus


class ChangeRequestCreate(ChangeRequestBase):
    pass


class ChangeRequestRead(ChangeRequestBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

