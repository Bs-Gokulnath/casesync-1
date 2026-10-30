from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.models.complaint import CaseActionHistory, CaseAssignment, CaseStatusHistory, Complaint
from app.models.enums import CaseActionType, ComplaintStatus, NotificationType
from app.models.user import User
from app.repositories import complaint_repository
from app.schemas.complaint import ComplaintOut
from app.services import audit_service, notification_service, overlap_service

ALLOWED_TRANSITIONS: dict[ComplaintStatus, frozenset[ComplaintStatus]] = {
    ComplaintStatus.RECEIVED: frozenset(
        {ComplaintStatus.UNDER_REVIEW, ComplaintStatus.TRANSFERRED}
    ),
    ComplaintStatus.UNDER_REVIEW: frozenset(
        {
            ComplaintStatus.UNDER_PROCESS,
            ComplaintStatus.PENDING_INFORMATION,
            ComplaintStatus.TRANSFERRED,
            ComplaintStatus.ESCALATED,
            ComplaintStatus.DISPOSED,
        }
    ),
    ComplaintStatus.UNDER_PROCESS: frozenset(
        {
            ComplaintStatus.PENDING_INFORMATION,
            ComplaintStatus.TRANSFERRED,
            ComplaintStatus.ESCALATED,
            ComplaintStatus.DISPOSED,
        }
    ),
    ComplaintStatus.PENDING_INFORMATION: frozenset(
        {
            ComplaintStatus.UNDER_PROCESS,
            ComplaintStatus.TRANSFERRED,
            ComplaintStatus.ESCALATED,
            ComplaintStatus.DISPOSED,
        }
    ),
    ComplaintStatus.TRANSFERRED: frozenset({ComplaintStatus.UNDER_REVIEW}),
    ComplaintStatus.ESCALATED: frozenset({ComplaintStatus.UNDER_PROCESS, ComplaintStatus.DISPOSED}),
    ComplaintStatus.DISPOSED: frozenset(),  # reopen() handles the only forward exit, separately
}


class ComplaintNotFoundError(Exception):
    pass


class IllegalTransitionError(Exception):
    def __init__(self, from_status: ComplaintStatus, to_status: ComplaintStatus):
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"Cannot move a case from {from_status.value} to {to_status.value}")


def is_transition_allowed(from_status: ComplaintStatus, to_status: ComplaintStatus) -> bool:
    return to_status in ALLOWED_TRANSITIONS.get(from_status, frozenset())


def _get_or_raise(db: Session, complaint_id: int) -> Complaint:
    complaint = complaint_repository.get_by_id(db, complaint_id)
    if complaint is None or complaint.is_deleted:
        raise ComplaintNotFoundError(f"Complaint {complaint_id} not found")
    return complaint


def _record_status_change(
    db: Session,
    complaint: Complaint,
    to_status: ComplaintStatus,
    *,
    actor: User,
    reason: str | None,
) -> None:
    db.add(
        CaseStatusHistory(
            complaint_id=complaint.id,
            from_status=complaint.status,
            to_status=to_status,
            actor_id=actor.id,
            reason=reason,
        )
    )
    complaint.status = to_status
    complaint.last_action_at = utcnow()
    if reason:
        complaint.last_action_note = reason


def transition(
    db: Session, complaint_id: int, to_status: ComplaintStatus, *, actor: User, reason: str | None
) -> ComplaintOut:
    complaint = _get_or_raise(db, complaint_id)
    if not is_transition_allowed(complaint.status, to_status):
        raise IllegalTransitionError(complaint.status, to_status)

    before_status = complaint.status
    _record_status_change(db, complaint, to_status, actor=actor, reason=reason)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor.id,
        action="complaint.transition",
        entity_type="complaint",
        entity_id=str(complaint.id),
        before={"status": before_status.value},
        after={"status": to_status.value, "reason": reason},
    )
    db.commit()
    return ComplaintOut.model_validate(complaint)


def transfer(
    db: Session, complaint_id: int, *, to_bureau_id: int, reason: str, actor: User
) -> ComplaintOut:
    complaint = _get_or_raise(db, complaint_id)
    if not is_transition_allowed(complaint.status, ComplaintStatus.TRANSFERRED):
        raise IllegalTransitionError(complaint.status, ComplaintStatus.TRANSFERRED)

    from_bureau_id = complaint.bureau_id
    before_status = complaint.status
    _record_status_change(db, complaint, ComplaintStatus.TRANSFERRED, actor=actor, reason=reason)
    complaint.bureau_id = to_bureau_id
    complaint.assigned_officer_id = None
    _unassign_current(db, complaint.id)

    db.add(
        CaseActionHistory(
            complaint_id=complaint.id,
            action_type=CaseActionType.TRANSFER,
            actor_id=actor.id,
            from_bureau_id=from_bureau_id,
            to_bureau_id=to_bureau_id,
            reason=reason,
        )
    )
    notification_service.notify_bureau(
        db,
        bureau_id=to_bureau_id,
        type_=NotificationType.TRANSFER,
        title=f"Case {complaint.case_reference} transferred to your bureau",
        message=reason,
        related_complaint_id=complaint.id,
    )
    db.flush()
    audit_service.record(
        db,
        actor_id=actor.id,
        action="complaint.transfer",
        entity_type="complaint",
        entity_id=str(complaint.id),
        before={"status": before_status.value, "bureau_id": from_bureau_id},
        after={"status": ComplaintStatus.TRANSFERRED.value, "bureau_id": to_bureau_id},
    )
    db.commit()
    overlap_service.scan_institution(db, complaint.institution_id)
    return ComplaintOut.model_validate(complaint)


def escalate(db: Session, complaint_id: int, *, reason: str, actor: User) -> ComplaintOut:
    complaint = _get_or_raise(db, complaint_id)
    if not is_transition_allowed(complaint.status, ComplaintStatus.ESCALATED):
        raise IllegalTransitionError(complaint.status, ComplaintStatus.ESCALATED)

    before_status = complaint.status
    _record_status_change(db, complaint, ComplaintStatus.ESCALATED, actor=actor, reason=reason)
    db.add(
        CaseActionHistory(
            complaint_id=complaint.id,
            action_type=CaseActionType.ESCALATE,
            actor_id=actor.id,
            reason=reason,
        )
    )
    notification_service.notify_bureau(
        db,
        bureau_id=complaint.bureau_id,
        type_=NotificationType.ESCALATION,
        title=f"Case {complaint.case_reference} escalated",
        message=reason,
        related_complaint_id=complaint.id,
    )
    db.flush()
    audit_service.record(
        db,
        actor_id=actor.id,
        action="complaint.escalate",
        entity_type="complaint",
        entity_id=str(complaint.id),
        before={"status": before_status.value},
        after={"status": ComplaintStatus.ESCALATED.value, "reason": reason},
    )
    db.commit()
    return ComplaintOut.model_validate(complaint)


def dispose(db: Session, complaint_id: int, *, disposal_note: str, actor: User) -> ComplaintOut:
    complaint = _get_or_raise(db, complaint_id)
    if not is_transition_allowed(complaint.status, ComplaintStatus.DISPOSED):
        raise IllegalTransitionError(complaint.status, ComplaintStatus.DISPOSED)

    before_status = complaint.status
    _record_status_change(db, complaint, ComplaintStatus.DISPOSED, actor=actor, reason=None)
    complaint.disposal_note = disposal_note
    _unassign_current(db, complaint.id)

    db.add(
        CaseActionHistory(
            complaint_id=complaint.id,
            action_type=CaseActionType.DISPOSE,
            actor_id=actor.id,
            note=disposal_note,
        )
    )
    db.flush()
    audit_service.record(
        db,
        actor_id=actor.id,
        action="complaint.dispose",
        entity_type="complaint",
        entity_id=str(complaint.id),
        before={"status": before_status.value},
        after={"status": ComplaintStatus.DISPOSED.value, "disposal_note": disposal_note},
    )
    db.commit()
    return ComplaintOut.model_validate(complaint)


def reopen(db: Session, complaint_id: int, *, reason: str, actor: User) -> ComplaintOut:
    complaint = _get_or_raise(db, complaint_id)
    if complaint.status is not ComplaintStatus.DISPOSED:
        raise IllegalTransitionError(complaint.status, ComplaintStatus.UNDER_REVIEW)

    _record_status_change(db, complaint, ComplaintStatus.UNDER_REVIEW, actor=actor, reason=reason)
    complaint.disposal_note = None
    db.add(
        CaseActionHistory(
            complaint_id=complaint.id,
            action_type=CaseActionType.REOPEN,
            actor_id=actor.id,
            reason=reason,
        )
    )
    db.flush()
    audit_service.record(
        db,
        actor_id=actor.id,
        action="complaint.reopen",
        entity_type="complaint",
        entity_id=str(complaint.id),
        before={"status": ComplaintStatus.DISPOSED.value},
        after={"status": ComplaintStatus.UNDER_REVIEW.value, "reason": reason},
    )
    db.commit()
    return ComplaintOut.model_validate(complaint)


def _unassign_current(db: Session, complaint_id: int) -> None:
    current = db.scalars(
        select(CaseAssignment).where(
            CaseAssignment.complaint_id == complaint_id, CaseAssignment.is_current.is_(True)
        )
    ).all()
    for assignment in current:
        assignment.is_current = False
        assignment.unassigned_at = utcnow()


def assign(db: Session, complaint_id: int, *, officer_id: int, actor: User) -> ComplaintOut:
    complaint = _get_or_raise(db, complaint_id)
    before_officer = complaint.assigned_officer_id
    _unassign_current(db, complaint.id)

    complaint.assigned_officer_id = officer_id
    db.add(
        CaseAssignment(
            complaint_id=complaint.id,
            officer_id=officer_id,
            bureau_id=complaint.bureau_id,
            assigned_by=actor.id,
            is_current=True,
        )
    )
    db.add(
        CaseActionHistory(
            complaint_id=complaint.id,
            action_type=CaseActionType.ASSIGN,
            actor_id=actor.id,
            note=f"Assigned to officer {officer_id}",
        )
    )
    notification_service.notify_user(
        db,
        user_id=officer_id,
        type_=NotificationType.ASSIGNMENT,
        title=f"Case {complaint.case_reference} assigned to you",
        message=complaint.subject,
        related_complaint_id=complaint.id,
    )
    db.flush()
    audit_service.record(
        db,
        actor_id=actor.id,
        action="complaint.assign",
        entity_type="complaint",
        entity_id=str(complaint.id),
        before={"assigned_officer_id": before_officer},
        after={"assigned_officer_id": officer_id},
    )
    db.commit()
    return ComplaintOut.model_validate(complaint)
