from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, require_csrf
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.notification import NotificationOut
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=Page[NotificationOut])
def list_notifications(
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Page[NotificationOut]:
    return notification_service.list_for_user(
        db, user, unread_only=unread_only, page=page, page_size=page_size
    )


@router.post("/{notification_id}/read", dependencies=[Depends(require_csrf)])
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    if not notification_service.mark_read(db, notification_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return {"status": "ok"}


@router.post("/read-all", dependencies=[Depends(require_csrf)])
def mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    count = notification_service.mark_all_read(db, user)
    return {"status": "ok", "marked": count}
