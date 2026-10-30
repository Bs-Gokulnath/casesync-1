from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.enums import OverlapAlertStatus
from app.models.overlap import OverlapAlert, OverlapAlertCase


def find_open_alert_for_pair(
    db: Session, *, institution_id: int, complaint_id_a: int, complaint_id_b: int
) -> OverlapAlert | None:
    alerts_for_a = select(OverlapAlertCase.overlap_alert_id).where(
        OverlapAlertCase.complaint_id == complaint_id_a
    )
    alerts_for_b = select(OverlapAlertCase.overlap_alert_id).where(
        OverlapAlertCase.complaint_id == complaint_id_b
    )
    shared_alert_id = db.scalar(
        select(OverlapAlertCase.overlap_alert_id)
        .where(
            OverlapAlertCase.overlap_alert_id.in_(alerts_for_a),
            OverlapAlertCase.overlap_alert_id.in_(alerts_for_b),
        )
        .limit(1)
    )
    if shared_alert_id is None:
        return None
    alert = db.get(OverlapAlert, shared_alert_id)
    if alert is not None and alert.institution_id == institution_id:
        return alert
    return None


def create_alert(
    db: Session,
    *,
    institution_id: int,
    complaint_ids: list[int],
    matching_signals: dict,
    confidence_score: float,
    rationale: str,
) -> OverlapAlert:
    alert = OverlapAlert(
        institution_id=institution_id,
        matching_signals=matching_signals,
        confidence_score=confidence_score,
        rationale=rationale,
        status=OverlapAlertStatus.OPEN,
    )
    db.add(alert)
    db.flush()
    for complaint_id in complaint_ids:
        db.add(OverlapAlertCase(overlap_alert_id=alert.id, complaint_id=complaint_id))
    db.flush()
    return alert


def get_by_id(db: Session, alert_id: int) -> OverlapAlert | None:
    return db.get(OverlapAlert, alert_id)


def case_ids_for_alert(db: Session, alert_id: int) -> list[int]:
    return list(
        db.scalars(
            select(OverlapAlertCase.complaint_id).where(
                OverlapAlertCase.overlap_alert_id == alert_id
            )
        )
    )


def search_statement(*, status=None, institution_id: int | None = None) -> Select:
    stmt = select(OverlapAlert).order_by(OverlapAlert.created_at.desc())
    if status is not None:
        stmt = stmt.where(OverlapAlert.status == status)
    if institution_id is not None:
        stmt = stmt.where(OverlapAlert.institution_id == institution_id)
    return stmt
