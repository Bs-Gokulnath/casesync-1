from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.complaint import CaseActionHistory, CaseRelationship, CaseStatusHistory, Complaint
from app.models.enums import ComplaintPriority, ComplaintStatus
from app.models.institution import Institution
from app.models.reference import SLAPolicy


def get_by_id(db: Session, complaint_id: int) -> Complaint | None:
    return db.get(Complaint, complaint_id)


def status_history(db: Session, complaint_id: int) -> list[CaseStatusHistory]:
    return list(
        db.scalars(
            select(CaseStatusHistory)
            .where(CaseStatusHistory.complaint_id == complaint_id)
            .order_by(CaseStatusHistory.created_at)
        )
    )


def action_history(db: Session, complaint_id: int) -> list[CaseActionHistory]:
    return list(
        db.scalars(
            select(CaseActionHistory)
            .where(CaseActionHistory.complaint_id == complaint_id)
            .order_by(CaseActionHistory.created_at)
        )
    )


def relationships_for(db: Session, complaint_id: int) -> list[CaseRelationship]:
    return list(
        db.scalars(select(CaseRelationship).where(CaseRelationship.complaint_id == complaint_id))
    )


def relationship_exists(db: Session, complaint_id: int, related_complaint_id: int) -> bool:
    return (
        db.scalar(
            select(CaseRelationship.id).where(
                CaseRelationship.complaint_id == complaint_id,
                CaseRelationship.related_complaint_id == related_complaint_id,
            )
        )
        is not None
    )


def create_relationship(db: Session, relationship: CaseRelationship) -> CaseRelationship:
    db.add(relationship)
    db.flush()
    return relationship


def create(db: Session, complaint: Complaint) -> Complaint:
    db.add(complaint)
    db.flush()
    return complaint


def next_case_reference(db: Session, year: int) -> str:
    prefix = f"CW-{year}-"
    count = db.scalar(
        select(func.count(Complaint.id)).where(Complaint.case_reference.like(f"{prefix}%"))
    )
    return f"{prefix}{(count or 0) + 1:05d}"


def sla_days_to_resolve(
    db: Session, *, category_id: int, priority: ComplaintPriority
) -> int | None:
    specific = db.scalar(
        select(SLAPolicy.days_to_resolve).where(
            SLAPolicy.category_id == category_id, SLAPolicy.priority == priority
        )
    )
    if specific is not None:
        return specific
    return db.scalar(
        select(SLAPolicy.days_to_resolve).where(
            SLAPolicy.category_id.is_(None), SLAPolicy.priority == priority
        )
    )


def search_statement(
    *,
    status: ComplaintStatus | None = None,
    bureau_id: int | None = None,
    priority: ComplaintPriority | None = None,
    category_id: int | None = None,
    institution_id: int | None = None,
    assigned_officer_id: int | None = None,
    region_id: int | None = None,
    q: str | None = None,
    received_from: date | None = None,
    received_to: date | None = None,
) -> Select:
    stmt = select(Complaint).where(Complaint.is_deleted.is_(False))
    if region_id is not None:
        stmt = stmt.join(Institution, Institution.id == Complaint.institution_id).where(
            Institution.region_id == region_id
        )
    if status is not None:
        stmt = stmt.where(Complaint.status == status)
    if bureau_id is not None:
        stmt = stmt.where(Complaint.bureau_id == bureau_id)
    if priority is not None:
        stmt = stmt.where(Complaint.priority == priority)
    if category_id is not None:
        stmt = stmt.where(Complaint.category_id == category_id)
    if institution_id is not None:
        stmt = stmt.where(Complaint.institution_id == institution_id)
    if assigned_officer_id is not None:
        stmt = stmt.where(Complaint.assigned_officer_id == assigned_officer_id)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            (Complaint.normalized_subject.ilike(like)) | (Complaint.case_reference.ilike(like))
        )
    if received_from is not None:
        stmt = stmt.where(Complaint.received_date >= received_from)
    if received_to is not None:
        stmt = stmt.where(Complaint.received_date <= received_to)
    return stmt.order_by(Complaint.received_date.desc(), Complaint.id.desc())
