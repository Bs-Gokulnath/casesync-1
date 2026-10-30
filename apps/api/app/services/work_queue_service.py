from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.complaint import Complaint
from app.models.enums import UserRole
from app.models.institution import Institution
from app.models.user import User
from app.repositories.pagination import paginate
from app.schemas.common import Page
from app.schemas.complaint import ComplaintOut
from app.services.sla_service import CLOSED_STATUSES


def _scope_statement(user: User):
    stmt = select(Complaint).where(Complaint.is_deleted.is_(False))
    if user.role is UserRole.BUREAU_OFFICER and user.bureau_id is not None:
        stmt = stmt.where(Complaint.bureau_id == user.bureau_id)
    elif user.role is UserRole.REGIONAL_OFFICER and user.region_id is not None:
        stmt = stmt.join(Institution, Institution.id == Complaint.institution_id).where(
            Institution.region_id == user.region_id
        )
    return stmt


def mine(db: Session, user: User, *, page: int, page_size: int) -> Page[ComplaintOut]:
    stmt = (
        select(Complaint)
        .where(Complaint.is_deleted.is_(False), Complaint.assigned_officer_id == user.id)
        .where(Complaint.status.notin_(CLOSED_STATUSES))
        .order_by(Complaint.expected_disposal_date.asc().nulls_last())
    )
    return paginate(db, stmt, page=page, page_size=page_size, mapper=ComplaintOut.model_validate)


def bureau_queue(db: Session, user: User, *, page: int, page_size: int) -> Page[ComplaintOut]:
    stmt = (
        _scope_statement(user)
        .where(Complaint.status.notin_(CLOSED_STATUSES))
        .order_by(Complaint.expected_disposal_date.asc().nulls_last())
    )
    return paginate(db, stmt, page=page, page_size=page_size, mapper=ComplaintOut.model_validate)


def overdue(db: Session, user: User, *, page: int, page_size: int) -> Page[ComplaintOut]:
    stmt = (
        _scope_statement(user)
        .where(
            Complaint.status.notin_(CLOSED_STATUSES),
            Complaint.expected_disposal_date.is_not(None),
            Complaint.expected_disposal_date < date.today(),
        )
        .order_by(Complaint.expected_disposal_date.asc())
    )
    return paginate(db, stmt, page=page, page_size=page_size, mapper=ComplaintOut.model_validate)


def unassigned(db: Session, user: User, *, page: int, page_size: int) -> Page[ComplaintOut]:
    stmt = (
        _scope_statement(user)
        .where(
            Complaint.status.notin_(CLOSED_STATUSES),
            Complaint.assigned_officer_id.is_(None),
        )
        .order_by(Complaint.received_date.asc())
    )
    return paginate(db, stmt, page=page, page_size=page_size, mapper=ComplaintOut.model_validate)
