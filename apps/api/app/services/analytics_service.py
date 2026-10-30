import csv
import io
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.complaint import Complaint
from app.models.institution import Institution
from app.models.overlap import OverlapAlert
from app.models.reference import Bureau, ComplaintCategory, Region
from app.schemas.analytics import AnalyticsSummary, CountByKey
from app.services.sla_service import CLOSED_STATUSES

# Leading characters that spreadsheet apps interpret as the start of a
# formula. Prefixing with a single quote neutralizes them without changing
# what a human sees when they open the file.
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def sanitize_csv_cell(value: str) -> str:
    if value and value[0] in _FORMULA_PREFIXES:
        return "'" + value
    return value


def _base_filtered_statement(
    *,
    date_from: date | None,
    date_to: date | None,
    bureau_id: int | None,
    region_id: int | None,
    category_id: int | None,
):
    stmt = select(Complaint).where(Complaint.is_deleted.is_(False))
    if date_from is not None:
        stmt = stmt.where(Complaint.received_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Complaint.received_date <= date_to)
    if bureau_id is not None:
        stmt = stmt.where(Complaint.bureau_id == bureau_id)
    if category_id is not None:
        stmt = stmt.where(Complaint.category_id == category_id)
    if region_id is not None:
        stmt = stmt.join(Institution, Institution.id == Complaint.institution_id).where(
            Institution.region_id == region_id
        )
    return stmt


def _group_counts(
    db: Session, stmt, group_col, label_map: dict[int, str] | None = None
) -> list[CountByKey]:
    sub = stmt.subquery()
    rows = db.execute(
        select(sub.c[group_col.name], func.count()).group_by(sub.c[group_col.name])
    ).all()
    results = []
    for raw_key, count in rows:
        key = raw_key.value if hasattr(raw_key, "value") else raw_key
        label = (
            label_map.get(raw_key, str(key)) if label_map else str(key).replace("_", " ").title()
        )
        results.append(CountByKey(key=str(key), label=label, count=count))
    return sorted(results, key=lambda r: -r.count)


def get_summary(
    db: Session,
    *,
    date_from: date | None,
    date_to: date | None,
    bureau_id: int | None,
    region_id: int | None,
    category_id: int | None,
) -> AnalyticsSummary:
    base = _base_filtered_statement(
        date_from=date_from,
        date_to=date_to,
        bureau_id=bureau_id,
        region_id=region_id,
        category_id=category_id,
    )

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0

    bureau_names = {b.id: b.name for b in db.scalars(select(Bureau))}
    category_names = {c.id: c.name for c in db.scalars(select(ComplaintCategory))}
    region_names = {r.id: r.name for r in db.scalars(select(Region))}

    by_status = _group_counts(db, base, Complaint.status)
    by_bureau = _group_counts(db, base, Complaint.bureau_id, bureau_names)
    by_category = _group_counts(db, base, Complaint.category_id, category_names)
    by_priority = _group_counts(db, base, Complaint.priority)
    by_region = _region_counts(db, base, region_names)

    overdue_count = (
        db.scalar(
            select(func.count()).select_from(
                base.where(
                    Complaint.status.notin_(CLOSED_STATUSES),
                    Complaint.expected_disposal_date.is_not(None),
                    Complaint.expected_disposal_date < date.today(),
                ).subquery()
            )
        )
        or 0
    )

    disposed_count = sum(c.count for c in by_status if c.key == "disposed")
    disposal_rate = round(disposed_count / total, 3) if total else 0.0

    overlap_rows = db.execute(
        select(OverlapAlert.status, func.count()).group_by(OverlapAlert.status)
    ).all()
    overlap_by_status = [
        CountByKey(key=status.value, label=status.value.capitalize(), count=count)
        for status, count in overlap_rows
    ]

    return AnalyticsSummary(
        total=total,
        by_status=by_status,
        by_bureau=by_bureau,
        by_region=by_region,
        by_category=by_category,
        by_priority=by_priority,
        overdue_count=overdue_count,
        disposed_count=disposed_count,
        disposal_rate=disposal_rate,
        overlap_by_status=overlap_by_status,
    )


def _region_counts(db: Session, base_stmt, region_names: dict[int, str]) -> list[CountByKey]:
    stmt = (
        base_stmt.join(Institution, Institution.id == Complaint.institution_id)
        .with_only_columns(Institution.region_id, func.count())
        .group_by(Institution.region_id)
    )
    rows = db.execute(stmt).all()
    results = [
        CountByKey(
            key=str(region_id), label=region_names.get(region_id, str(region_id)), count=count
        )
        for region_id, count in rows
    ]
    return sorted(results, key=lambda r: -r.count)


def export_complaints_csv(
    db: Session,
    *,
    date_from: date | None,
    date_to: date | None,
    bureau_id: int | None,
    region_id: int | None,
    category_id: int | None,
) -> str:
    stmt = _base_filtered_statement(
        date_from=date_from,
        date_to=date_to,
        bureau_id=bureau_id,
        region_id=region_id,
        category_id=category_id,
    ).order_by(Complaint.received_date.desc())

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "case_reference",
            "institution_id",
            "category_id",
            "subject",
            "priority",
            "status",
            "bureau_id",
            "received_date",
            "expected_disposal_date",
        ]
    )
    for complaint in db.scalars(stmt):
        writer.writerow(
            [
                sanitize_csv_cell(complaint.case_reference),
                complaint.institution_id,
                complaint.category_id,
                sanitize_csv_cell(complaint.subject),
                complaint.priority.value,
                complaint.status.value,
                complaint.bureau_id,
                complaint.received_date.isoformat(),
                (
                    complaint.expected_disposal_date.isoformat()
                    if complaint.expected_disposal_date
                    else ""
                ),
            ]
        )
    return buffer.getvalue()
