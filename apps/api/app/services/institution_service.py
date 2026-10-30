from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.complaint import Complaint
from app.models.enums import ComplaintStatus
from app.models.institution import Institution
from app.repositories import institution_repository
from app.repositories.pagination import paginate
from app.schemas.common import Page
from app.schemas.institution import (
    InstitutionCreate,
    InstitutionDetail,
    InstitutionOut,
    InstitutionUpdate,
)
from app.services import audit_service

OPEN_STATUSES = {
    ComplaintStatus.RECEIVED,
    ComplaintStatus.UNDER_REVIEW,
    ComplaintStatus.UNDER_PROCESS,
    ComplaintStatus.PENDING_INFORMATION,
    ComplaintStatus.ESCALATED,
}


class DuplicateInstitutionError(Exception):
    pass


def _normalize(name: str) -> str:
    return " ".join(name.lower().split())


def list_institutions(
    db: Session,
    *,
    q: str | None,
    region_id: int | None,
    is_active: bool | None,
    page: int,
    page_size: int,
) -> Page[InstitutionOut]:
    stmt = institution_repository.search_statement(q=q, region_id=region_id, is_active=is_active)
    return paginate(db, stmt, page=page, page_size=page_size, mapper=InstitutionOut.model_validate)


def get_detail(db: Session, institution_id: int) -> InstitutionDetail | None:
    institution = institution_repository.get_by_id(db, institution_id)
    if institution is None:
        return None

    total = db.scalar(
        select(func.count(Complaint.id)).where(Complaint.institution_id == institution_id)
    )
    open_count = db.scalar(
        select(func.count(Complaint.id)).where(
            Complaint.institution_id == institution_id,
            Complaint.status.in_(OPEN_STATUSES),
        )
    )
    return InstitutionDetail(
        **InstitutionOut.model_validate(institution).model_dump(),
        total_complaint_count=total or 0,
        open_complaint_count=open_count or 0,
    )


def create_institution(db: Session, payload: InstitutionCreate, *, actor_id: int) -> InstitutionOut:
    if payload.aicte_permanent_id:
        existing = institution_repository.get_by_aicte_id(db, payload.aicte_permanent_id)
        if existing is not None:
            raise DuplicateInstitutionError(
                f"AICTE Permanent ID {payload.aicte_permanent_id} is already registered "
                f"to institution {existing.institution_code}"
            )

    institution = Institution(
        institution_code=institution_repository.next_institution_code(db),
        aicte_permanent_id=payload.aicte_permanent_id,
        name=payload.name,
        normalized_name=_normalize(payload.name),
        address=payload.address,
        region_id=payload.region_id,
        contact_email=payload.contact_email,
        contact_phone=payload.contact_phone,
        is_active=True,
    )
    institution_repository.create(db, institution)
    audit_service.record(
        db,
        actor_id=actor_id,
        action="institution.create",
        entity_type="institution",
        entity_id=str(institution.id),
        after={"name": institution.name, "institution_code": institution.institution_code},
    )
    db.commit()
    return InstitutionOut.model_validate(institution)


def update_institution(
    db: Session, institution_id: int, payload: InstitutionUpdate, *, actor_id: int
) -> InstitutionOut | None:
    institution = institution_repository.get_by_id(db, institution_id)
    if institution is None:
        return None

    before = InstitutionOut.model_validate(institution).model_dump(mode="json")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        institution.name = data["name"]
        institution.normalized_name = _normalize(data["name"])
    for field in ("aicte_permanent_id", "address", "region_id", "contact_email", "contact_phone"):
        if field in data:
            setattr(institution, field, data[field])

    db.flush()
    after = InstitutionOut.model_validate(institution).model_dump(mode="json")
    audit_service.record(
        db,
        actor_id=actor_id,
        action="institution.update",
        entity_type="institution",
        entity_id=str(institution.id),
        before=before,
        after=after,
    )
    db.commit()
    return InstitutionOut.model_validate(institution)


def set_status(
    db: Session, institution_id: int, *, is_active: bool, reason: str, actor_id: int
) -> InstitutionOut | None:
    institution = institution_repository.get_by_id(db, institution_id)
    if institution is None:
        return None

    before_active = institution.is_active
    institution.is_active = is_active
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="institution.status_change",
        entity_type="institution",
        entity_id=str(institution.id),
        before={"is_active": before_active},
        after={"is_active": is_active, "reason": reason},
    )
    db.commit()
    return InstitutionOut.model_validate(institution)
