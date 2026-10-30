from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.base import utcnow
from app.models.complaint import Complaint
from app.models.enums import NotificationType, OverlapAlertStatus
from app.models.user import User
from app.repositories import overlap_repository
from app.repositories.pagination import paginate
from app.schemas.common import Page
from app.schemas.overlap import OverlapAlertDetail, OverlapAlertOut
from app.services import audit_service, notification_service
from app.services.matching_service import MatchCandidate, compute_match
from app.services.sla_service import CLOSED_STATUSES

settings = get_settings()


class OverlapAlertNotFoundError(Exception):
    pass


def _candidate(complaint: Complaint) -> MatchCandidate:
    return MatchCandidate(
        complaint_id=complaint.id,
        category_id=complaint.category_id,
        normalized_subject=complaint.normalized_subject,
        received_date=complaint.received_date,
        bureau_id=complaint.bureau_id,
    )


def scan_institution(db: Session, institution_id: int) -> list[int]:
    """Compare every open complaint for this institution pairwise across bureaus.

    Creates a new OPEN OverlapAlert for any pair scoring at/above the
    configured threshold that isn't already linked by an existing alert.
    Returns the ids of any newly created alerts. Never touches the
    complaints themselves — purely additive, reviewable data.
    """
    open_complaints = list(
        db.scalars(
            select(Complaint).where(
                Complaint.institution_id == institution_id,
                Complaint.is_deleted.is_(False),
                Complaint.status.notin_(CLOSED_STATUSES),
            )
        )
    )
    created_alert_ids: list[int] = []
    for i, complaint_a in enumerate(open_complaints):
        for complaint_b in open_complaints[i + 1 :]:
            if complaint_a.bureau_id == complaint_b.bureau_id:
                continue
            result = compute_match(_candidate(complaint_a), _candidate(complaint_b))
            if result.score < settings.overlap_match_threshold:
                continue

            existing = overlap_repository.find_open_alert_for_pair(
                db,
                institution_id=institution_id,
                complaint_id_a=complaint_a.id,
                complaint_id_b=complaint_b.id,
            )
            if existing is not None:
                continue

            alert = overlap_repository.create_alert(
                db,
                institution_id=institution_id,
                complaint_ids=[complaint_a.id, complaint_b.id],
                matching_signals=result.signals,
                confidence_score=result.score,
                rationale=result.rationale,
            )
            created_alert_ids.append(alert.id)
            for bureau_id in {complaint_a.bureau_id, complaint_b.bureau_id}:
                notification_service.notify_bureau(
                    db,
                    bureau_id=bureau_id,
                    type_=NotificationType.OVERLAP_ALERT,
                    title="Potential overlapping case detected",
                    message=result.rationale,
                    related_overlap_alert_id=alert.id,
                )

    if created_alert_ids:
        db.commit()
    return created_alert_ids


def list_alerts(
    db: Session,
    *,
    status: OverlapAlertStatus | None,
    institution_id: int | None,
    page: int,
    page_size: int,
) -> Page[OverlapAlertOut]:
    stmt = overlap_repository.search_statement(status=status, institution_id=institution_id)
    return paginate(
        db,
        stmt,
        page=page,
        page_size=page_size,
        mapper=lambda alert: OverlapAlertOut(
            **OverlapAlertOut.model_validate(alert).model_dump(exclude={"case_ids"}),
            case_ids=overlap_repository.case_ids_for_alert(db, alert.id),
        ),
    )


def get_detail(db: Session, alert_id: int) -> OverlapAlertDetail | None:
    alert = overlap_repository.get_by_id(db, alert_id)
    if alert is None:
        return None
    case_ids = overlap_repository.case_ids_for_alert(db, alert_id)
    return OverlapAlertDetail(
        **OverlapAlertOut.model_validate(alert).model_dump(exclude={"case_ids"}),
        case_ids=case_ids,
    )


def decide(
    db: Session,
    alert_id: int,
    *,
    new_status: OverlapAlertStatus,
    reason: str,
    actor: User,
) -> OverlapAlertOut:
    alert = overlap_repository.get_by_id(db, alert_id)
    if alert is None:
        raise OverlapAlertNotFoundError(f"Overlap alert {alert_id} not found")

    before_status = alert.status
    alert.status = new_status
    alert.decided_by = actor.id
    alert.decision_reason = reason
    alert.decided_at = utcnow()
    db.flush()

    audit_service.record(
        db,
        actor_id=actor.id,
        action="overlap.decision",
        entity_type="overlap_alert",
        entity_id=str(alert.id),
        before={"status": before_status.value},
        after={"status": new_status.value, "reason": reason},
    )
    db.commit()
    case_ids = overlap_repository.case_ids_for_alert(db, alert.id)
    return OverlapAlertOut(
        **OverlapAlertOut.model_validate(alert).model_dump(exclude={"case_ids"}),
        case_ids=case_ids,
    )
