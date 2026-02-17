from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Patch
from app.schemas.patches import PatchRead


router = APIRouter(prefix="/patches", tags=["patches"])


@router.get("/", response_model=List[PatchRead])
def list_patches(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> List[Patch]:
    return db.query(Patch).order_by(Patch.requested_date.desc()).limit(200).all()

