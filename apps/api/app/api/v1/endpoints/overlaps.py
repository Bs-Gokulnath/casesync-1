from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import require_csrf, require_permission
from app.db.session import get_db
from app.models.enums import OverlapAlertStatus
from app.models.user import User
from app.schemas.common import Page
from app.schemas.overlap import OverlapAlertDetail, OverlapAlertOut, OverlapDecisionRequest
from app.security.permissions import Permission
from app.services import overlap_service
from app.services.overlap_service import OverlapAlertNotFoundError

router = APIRouter(prefix="/overlaps", tags=["overlaps"])


@router.get("", response_model=Page[OverlapAlertOut])
def list_overlap_alerts(
    status_: OverlapAlertStatus | None = Query(default=None, alias="status"),
    institution_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.OVERLAP_READ)),
) -> Page[OverlapAlertOut]:
    return overlap_service.list_alerts(
        db, status=status_, institution_id=institution_id, page=page, page_size=page_size
    )


@router.get("/{alert_id}", response_model=OverlapAlertDetail)
def get_overlap_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.OVERLAP_READ)),
) -> OverlapAlertDetail:
    detail = overlap_service.get_detail(db, alert_id)
    if detail is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Overlap alert not found")
    return detail


@router.post("/{alert_id}/decision", response_model=OverlapAlertOut)
def decide_overlap_alert(
    alert_id: int,
    payload: OverlapDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.OVERLAP_DECIDE)),
    _csrf: None = Depends(require_csrf),
) -> OverlapAlertOut:
    if payload.status is OverlapAlertStatus.OPEN:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="A decision must be confirmed, dismissed or resolved",
        )
    try:
        return overlap_service.decide(
            db, alert_id, new_status=payload.status, reason=payload.reason, actor=user
        )
    except OverlapAlertNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
