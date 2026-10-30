from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.models.audit import AuditEvent
from app.models.user import User
from app.repositories.pagination import paginate
from app.schemas.audit import AuditEventOut
from app.schemas.common import Page
from app.security.permissions import Permission

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=Page[AuditEventOut])
def list_audit_events(
    entity_type: str | None = None,
    entity_id: str | None = None,
    actor_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.AUDIT_READ)),
) -> Page[AuditEventOut]:
    stmt = select(AuditEvent).order_by(AuditEvent.created_at.desc())
    if entity_type:
        stmt = stmt.where(AuditEvent.entity_type == entity_type)
    if entity_id:
        stmt = stmt.where(AuditEvent.entity_id == entity_id)
    if actor_id is not None:
        stmt = stmt.where(AuditEvent.actor_id == actor_id)
    if date_from is not None:
        stmt = stmt.where(AuditEvent.created_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(AuditEvent.created_at <= date_to)

    return paginate(db, stmt, page=page, page_size=page_size, mapper=AuditEventOut.model_validate)
