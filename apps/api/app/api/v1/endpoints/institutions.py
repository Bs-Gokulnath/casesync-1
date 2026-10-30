from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import require_csrf, require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.institution import (
    InstitutionCreate,
    InstitutionDetail,
    InstitutionOut,
    InstitutionStatusUpdate,
    InstitutionUpdate,
)
from app.security.permissions import Permission
from app.services import institution_service
from app.services.institution_service import DuplicateInstitutionError

router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.get("", response_model=Page[InstitutionOut])
def list_institutions(
    q: str | None = None,
    region_id: int | None = None,
    is_active: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.INSTITUTION_READ)),
) -> Page[InstitutionOut]:
    return institution_service.list_institutions(
        db, q=q, region_id=region_id, is_active=is_active, page=page, page_size=page_size
    )


@router.post("", response_model=InstitutionOut, status_code=status.HTTP_201_CREATED)
def create_institution(
    payload: InstitutionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.INSTITUTION_WRITE)),
    _csrf: None = Depends(require_csrf),
) -> InstitutionOut:
    try:
        return institution_service.create_institution(db, payload, actor_id=user.id)
    except DuplicateInstitutionError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{institution_id}", response_model=InstitutionDetail)
def get_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.INSTITUTION_READ)),
) -> InstitutionDetail:
    detail = institution_service.get_detail(db, institution_id)
    if detail is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Institution not found")
    return detail


@router.patch("/{institution_id}", response_model=InstitutionOut)
def update_institution(
    institution_id: int,
    payload: InstitutionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.INSTITUTION_WRITE)),
    _csrf: None = Depends(require_csrf),
) -> InstitutionOut:
    updated = institution_service.update_institution(db, institution_id, payload, actor_id=user.id)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Institution not found")
    return updated


@router.patch("/{institution_id}/status", response_model=InstitutionOut)
def update_institution_status(
    institution_id: int,
    payload: InstitutionStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.INSTITUTION_STATUS)),
    _csrf: None = Depends(require_csrf),
) -> InstitutionOut:
    updated = institution_service.set_status(
        db,
        institution_id,
        is_active=payload.is_active,
        reason=payload.reason,
        actor_id=user.id,
    )
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Institution not found")
    return updated
