from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.models.inventory import DeviceStatus


class DeviceBase(BaseModel):
  asset_tag: str
  type: str
  location: str
  assigned_user: Optional[str] = None
  warranty_end: Optional[date] = None
  last_patch_date: Optional[date] = None
  status: DeviceStatus


class DeviceCreate(DeviceBase):
  pass


class DeviceRead(DeviceBase):
  id: int
  created_at: datetime
  updated_at: datetime

  class Config:
    from_attributes = True

