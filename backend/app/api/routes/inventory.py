from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Device
from app.schemas.inventory import DeviceRead


router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/", response_model=List[DeviceRead])
def list_devices(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> List[Device]:
    return db.query(Device).order_by(Device.asset_tag).all()

