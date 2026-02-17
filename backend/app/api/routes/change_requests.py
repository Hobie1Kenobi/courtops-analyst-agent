from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import ChangeRequest
from app.schemas.change_requests import ChangeRequestCreate, ChangeRequestRead
from app.services.docs_generator import generate_change_request_docs


router = APIRouter(prefix="/change-requests", tags=["change_requests"])


@router.get("/", response_model=List[ChangeRequestRead])
def list_change_requests(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> List[ChangeRequest]:
    return db.query(ChangeRequest).order_by(ChangeRequest.created_at.desc()).all()


@router.post("/", response_model=ChangeRequestRead)
def create_change_request(
    data: ChangeRequestCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ChangeRequest:
    cr = ChangeRequest(**data.model_dump())
    db.add(cr)
    db.commit()
    db.refresh(cr)
    return cr


@router.post("/{change_request_id}/generate-docs")
def generate_docs_endpoint(
    change_request_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict:
    cr = db.get(ChangeRequest, change_request_id)
    if not cr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change request not found")
    paths = generate_change_request_docs(cr)
    # Return relative paths for UI consumption
    return {name: str(path.relative_to(path.parents[2])) for name, path in paths.items()}


