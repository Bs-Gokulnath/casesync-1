from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.complaint import ComplaintOut
from app.security.permissions import Permission
from app.services import work_queue_service

router = APIRouter(prefix="/work-queue", tags=["work-queue"])


@router.get("/mine", response_model=Page[ComplaintOut])
def my_queue(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.WORKQUEUE_READ)),
) -> Page[ComplaintOut]:
    return work_queue_service.mine(db, user, page=page, page_size=page_size)


@router.get("/bureau", response_model=Page[ComplaintOut])
def bureau_queue(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.WORKQUEUE_READ)),
) -> Page[ComplaintOut]:
    return work_queue_service.bureau_queue(db, user, page=page, page_size=page_size)


@router.get("/overdue", response_model=Page[ComplaintOut])
def overdue_queue(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.WORKQUEUE_READ)),
) -> Page[ComplaintOut]:
    return work_queue_service.overdue(db, user, page=page, page_size=page_size)


@router.get("/unassigned", response_model=Page[ComplaintOut])
def unassigned_queue(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.WORKQUEUE_READ)),
) -> Page[ComplaintOut]:
    return work_queue_service.unassigned(db, user, page=page, page_size=page_size)
