from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.complaint import CaseRelationship, CaseStatusHistory, Complaint
from app.models.enums import ComplaintPriority, ComplaintStatus, UserRole
from app.models.user import User
from app.repositories import complaint_repository
from app.repositories.pagination import paginate
from app.schemas.common import Page
from app.schemas.complaint import ComplaintCreate, ComplaintOut, ComplaintUpdate, RelationshipCreate
from app.schemas.history import ActionHistoryEntry, StatusHistoryEntry, TimelineEntry
from app.services import audit_service, overlap_service


class ScopeError(Exception):
    """Raised when a caller's role requires a bureau/region they didn't provide or may not use."""


class RelatedComplaintNotFoundError(Exception):
    pass


class SelfRelationshipError(Exception):
    pass


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _region_scope_for(user: User) -> int | None:
    return user.region_id if user.role is UserRole.REGIONAL_OFFICER else None


def _bureau_scope_for(user: User) -> int | None:
    return user.bureau_id if user.role is UserRole.BUREAU_OFFICER else None


def list_complaints(
    db: Session,
    *,
    current_user: User,
    status: ComplaintStatus | None,
    bureau_id: int | None,
    priority: ComplaintPriority | None,
    category_id: int | None,
    institution_id: int | None,
    assigned_officer_id: int | None,
    q: str | None,
    received_from: date | None,
    received_to: date | None,
    page: int,
    page_size: int,
) -> Page[ComplaintOut]:
    scoped_bureau = _bureau_scope_for(current_user) or bureau_id
    scoped_region = _region_scope_for(current_user)

    stmt = complaint_repository.search_statement(
        status=status,
        bureau_id=scoped_bureau,
        priority=priority,
        category_id=category_id,
        institution_id=institution_id,
        assigned_officer_id=assigned_officer_id,
        region_id=scoped_region,
        q=q,
        received_from=received_from,
        received_to=received_to,
    )
    return paginate(db, stmt, page=page, page_size=page_size, mapper=ComplaintOut.model_validate)


def get_complaint(db: Session, complaint_id: int) -> ComplaintOut | None:
    complaint = complaint_repository.get_by_id(db, complaint_id)
    if complaint is None or complaint.is_deleted:
        return None
    return ComplaintOut.model_validate(complaint)


def create_complaint(db: Session, payload: ComplaintCreate, *, current_user: User) -> ComplaintOut:
    bureau_id = _bureau_scope_for(current_user) or payload.bureau_id
    if bureau_id is None:
        raise ScopeError("bureau_id is required for this role")

    received_date = payload.received_date or date.today()
    days_to_resolve = complaint_repository.sla_days_to_resolve(
        db, category_id=payload.category_id, priority=payload.priority
    )
    expected_disposal_date = (
        received_date + timedelta(days=days_to_resolve) if days_to_resolve else None
    )

    complaint = Complaint(
        case_reference=complaint_repository.next_case_reference(db, received_date.year),
        institution_id=payload.institution_id,
        category_id=payload.category_id,
        subject=payload.subject,
        normalized_subject=_normalize(payload.subject),
        description=payload.description,
        source=payload.source,
        priority=payload.priority,
        status=ComplaintStatus.RECEIVED,
        bureau_id=bureau_id,
        assigned_officer_id=None,
        received_date=received_date,
        expected_disposal_date=expected_disposal_date,
        next_action_note=payload.next_action_note,
        created_by=current_user.id,
    )
    complaint_repository.create(db, complaint)
    db.add(
        CaseStatusHistory(
            complaint_id=complaint.id,
            from_status=None,
            to_status=ComplaintStatus.RECEIVED,
            actor_id=current_user.id,
            reason="Complaint registered",
        )
    )
    audit_service.record(
        db,
        actor_id=current_user.id,
        action="complaint.create",
        entity_type="complaint",
        entity_id=str(complaint.id),
        after={"case_reference": complaint.case_reference, "bureau_id": bureau_id},
    )
    db.commit()
    overlap_service.scan_institution(db, complaint.institution_id)
    return ComplaintOut.model_validate(complaint)


def get_timeline(db: Session, complaint_id: int) -> list[TimelineEntry]:
    status_rows = complaint_repository.status_history(db, complaint_id)
    action_rows = complaint_repository.action_history(db, complaint_id)

    actor_ids = {row.actor_id for row in status_rows} | {row.actor_id for row in action_rows}
    actor_names = {
        user.id: user.full_name for user in db.query(User).filter(User.id.in_(actor_ids)).all()
    }

    status_entries: list[TimelineEntry] = [
        StatusHistoryEntry(
            from_status=h.from_status,
            to_status=h.to_status,
            actor_id=h.actor_id,
            actor_name=actor_names.get(h.actor_id, "Unknown user"),
            reason=h.reason,
            created_at=h.created_at,
        )
        for h in status_rows
    ]
    action_entries: list[TimelineEntry] = [
        ActionHistoryEntry(
            action_type=h.action_type,
            actor_id=h.actor_id,
            actor_name=actor_names.get(h.actor_id, "Unknown user"),
            from_bureau_id=h.from_bureau_id,
            to_bureau_id=h.to_bureau_id,
            reason=h.reason,
            note=h.note,
            created_at=h.created_at,
        )
        for h in action_rows
    ]
    return sorted(status_entries + action_entries, key=lambda entry: entry.created_at)


def update_complaint(
    db: Session, complaint_id: int, payload: ComplaintUpdate, *, current_user: User
) -> ComplaintOut | None:
    complaint = complaint_repository.get_by_id(db, complaint_id)
    if complaint is None or complaint.is_deleted:
        return None

    before = ComplaintOut.model_validate(complaint).model_dump(mode="json")
    data = payload.model_dump(exclude_unset=True)
    if "subject" in data:
        complaint.subject = data["subject"]
        complaint.normalized_subject = _normalize(data["subject"])
    for field in ("description", "category_id", "priority", "next_action_note"):
        if field in data:
            setattr(complaint, field, data[field])

    db.flush()
    after = ComplaintOut.model_validate(complaint).model_dump(mode="json")
    audit_service.record(
        db,
        actor_id=current_user.id,
        action="complaint.update",
        entity_type="complaint",
        entity_id=str(complaint.id),
        before=before,
        after=after,
    )
    db.commit()
    return ComplaintOut.model_validate(complaint)


def get_relationships(db: Session, complaint_id: int) -> list[CaseRelationship]:
    return complaint_repository.relationships_for(db, complaint_id)


def create_relationship(
    db: Session, complaint_id: int, payload: RelationshipCreate, *, current_user: User
) -> CaseRelationship:
    if payload.related_complaint_id == complaint_id:
        raise SelfRelationshipError("A complaint cannot be related to itself")

    complaint = complaint_repository.get_by_id(db, complaint_id)
    related = complaint_repository.get_by_id(db, payload.related_complaint_id)
    if complaint is None or complaint.is_deleted or related is None or related.is_deleted:
        raise RelatedComplaintNotFoundError("One of the complaints was not found")

    relationship = complaint_repository.create_relationship(
        db,
        CaseRelationship(
            complaint_id=complaint_id,
            related_complaint_id=payload.related_complaint_id,
            relationship_type=payload.relationship_type,
            created_by=current_user.id,
        ),
    )
    # Kept symmetric at the service layer: one logical link, two readable
    # directions (see docs/DATABASE.md).
    if not complaint_repository.relationship_exists(db, payload.related_complaint_id, complaint_id):
        complaint_repository.create_relationship(
            db,
            CaseRelationship(
                complaint_id=payload.related_complaint_id,
                related_complaint_id=complaint_id,
                relationship_type=payload.relationship_type,
                created_by=current_user.id,
            ),
        )

    audit_service.record(
        db,
        actor_id=current_user.id,
        action="complaint.relate",
        entity_type="complaint",
        entity_id=str(complaint_id),
        after={
            "related_complaint_id": payload.related_complaint_id,
            "relationship_type": payload.relationship_type.value,
        },
    )
    db.commit()
    return relationship
