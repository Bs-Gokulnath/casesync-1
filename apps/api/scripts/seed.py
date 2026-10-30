"""Deterministic, fictional demo data for local development ONLY.

Refuses to run against app_env=production. Safe to re-run: every row is
looked up by its natural/unique key first ("get or create"), so re-running
updates nothing and creates nothing twice.

Usage (from apps/api, with the venv active and Postgres up):
    python scripts/seed.py
"""

import sys
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.base import utcnow
from app.db.session import SessionLocal
from app.models.complaint import CaseActionHistory, CaseAssignment, CaseStatusHistory, Complaint
from app.models.enums import (
    CaseActionType,
    ComplaintPriority,
    ComplaintSource,
    ComplaintStatus,
    OverlapAlertStatus,
    UserRole,
)
from app.models.institution import Institution
from app.models.overlap import OverlapAlert, OverlapAlertCase
from app.models.reference import Bureau, ComplaintCategory, Region, SLAPolicy
from app.models.user import User
from app.security.passwords import hash_password

DEMO_PASSWORD_SUFFIX = "Demo@12345"


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def get_or_create(db: Session, model, defaults: dict | None = None, **lookup):
    instance = db.query(model).filter_by(**lookup).one_or_none()
    if instance is not None:
        return instance, False
    instance = model(**{**lookup, **(defaults or {})})
    db.add(instance)
    db.flush()
    return instance, True


def seed_reference_data(db: Session) -> dict:
    regions = {}
    for code, name in [
        ("NR", "Northern Region"),
        ("WR", "Western Region"),
        ("SR", "Southern Region"),
    ]:
        regions[code], _ = get_or_create(db, Region, code=code, defaults={"name": name})

    bureaus = {}
    for code, name in [
        ("RB-DEL", "Regional Bureau - Delhi"),
        ("PGRC", "Public Grievance Redressal Cell"),
        ("RB-MUM", "Regional Bureau - Mumbai"),
    ]:
        bureaus[code], _ = get_or_create(db, Bureau, code=code, defaults={"name": name})

    categories = {}
    for code, name in [
        ("FEE", "Fee Refund / Overcharging"),
        ("ADM", "Admission Irregularity"),
        ("FAC", "Faculty / Infrastructure Shortage"),
        ("RAG", "Ragging / Student Safety"),
        ("OTH", "Other"),
    ]:
        categories[code], _ = get_or_create(
            db, ComplaintCategory, code=code, defaults={"name": name}
        )

    sla_defaults = {
        ComplaintPriority.CRITICAL: 7,
        ComplaintPriority.HIGH: 15,
        ComplaintPriority.MEDIUM: 30,
        ComplaintPriority.LOW: 45,
    }
    for priority, days in sla_defaults.items():
        get_or_create(
            db,
            SLAPolicy,
            category_id=None,
            priority=priority,
            defaults={"days_to_resolve": days, "warning_days_before": 3},
        )

    db.flush()
    return {"regions": regions, "bureaus": bureaus, "categories": categories}


def seed_users(db: Session, bureaus: dict, regions: dict) -> dict:
    users = {}
    specs = [
        ("admin", "System Administrator", UserRole.SYSTEM_ADMIN, None, None),
        ("management", "Senior Management", UserRole.SENIOR_MANAGEMENT, None, None),
        ("rb.officer", "Regional Bureau Officer (Delhi)", UserRole.BUREAU_OFFICER, "RB-DEL", None),
        ("pgrc.officer", "PGRC Officer", UserRole.BUREAU_OFFICER, "PGRC", None),
        ("regional.officer", "Regional Officer (North)", UserRole.REGIONAL_OFFICER, None, "NR"),
        ("auditor", "Compliance Auditor", UserRole.AUDITOR, None, None),
    ]
    for key, full_name, role, bureau_code, region_code in specs:
        email = f"{key}@aictecasewatch-demo.org"
        user, _ = get_or_create(
            db,
            User,
            email=email,
            defaults={
                "employee_code": f"EMP-{key.upper().replace('.', '-')}",
                "full_name": full_name,
                "password_hash": hash_password(DEMO_PASSWORD_SUFFIX),
                "role": role,
                "bureau_id": bureaus[bureau_code].id if bureau_code else None,
                "region_id": regions[region_code].id if region_code else None,
                "is_active": True,
            },
        )
        users[key] = user
    db.flush()
    return users


def seed_institutions(db: Session, regions: dict) -> dict:
    institutions = {}
    specs = [
        ("INST-0001", "AICTE-1001-CS", "Delta Institute of Technology", "NR"),
        ("INST-0002", "AICTE-1002-CS", "Meridian College of Engineering", "WR"),
        ("INST-0003", "AICTE-1003-CS", "Sunrise Polytechnic", "SR"),
    ]
    for code, aicte_id, name, region_code in specs:
        inst, _ = get_or_create(
            db,
            Institution,
            institution_code=code,
            defaults={
                "aicte_permanent_id": aicte_id,
                "name": name,
                "normalized_name": normalize(name),
                "address": f"{name} Campus, {regions[region_code].name}",
                "region_id": regions[region_code].id,
                "is_active": True,
            },
        )
        institutions[code] = inst
    db.flush()
    return institutions


def _create_complaint_with_history(
    db: Session,
    *,
    case_reference: str,
    institution_id: int,
    category_id: int,
    bureau_id: int,
    created_by_id: int,
    assigned_officer_id: int | None,
    subject: str,
    description: str,
    priority: ComplaintPriority,
    status: ComplaintStatus,
    received_days_ago: int,
    expected_disposal_in_days: int | None,
    disposal_note: str | None = None,
) -> Complaint:
    existing = db.query(Complaint).filter_by(case_reference=case_reference).one_or_none()
    if existing is not None:
        return existing

    received_date = date.today() - timedelta(days=received_days_ago)
    expected_disposal_date = (
        date.today() + timedelta(days=expected_disposal_in_days)
        if expected_disposal_in_days is not None
        else None
    )

    complaint = Complaint(
        case_reference=case_reference,
        institution_id=institution_id,
        category_id=category_id,
        subject=subject,
        normalized_subject=normalize(subject),
        description=description,
        source=ComplaintSource.PORTAL,
        priority=priority,
        status=status,
        bureau_id=bureau_id,
        assigned_officer_id=assigned_officer_id,
        received_date=received_date,
        expected_disposal_date=expected_disposal_date,
        disposal_note=disposal_note,
        created_by=created_by_id,
    )
    db.add(complaint)
    db.flush()

    db.add(
        CaseStatusHistory(
            complaint_id=complaint.id,
            from_status=None,
            to_status=ComplaintStatus.RECEIVED,
            actor_id=created_by_id,
            reason="Complaint registered",
        )
    )
    if status is not ComplaintStatus.RECEIVED:
        db.add(
            CaseStatusHistory(
                complaint_id=complaint.id,
                from_status=ComplaintStatus.RECEIVED,
                to_status=status,
                actor_id=assigned_officer_id or created_by_id,
                reason="Seeded demo progression",
            )
        )

    if assigned_officer_id is not None:
        db.add(
            CaseAssignment(
                complaint_id=complaint.id,
                officer_id=assigned_officer_id,
                bureau_id=bureau_id,
                assigned_by=created_by_id,
                is_current=status is not ComplaintStatus.DISPOSED,
            )
        )
    db.flush()
    return complaint


def seed_complaints(db: Session, refs: dict, users: dict, institutions: dict) -> dict:
    bureaus = refs["bureaus"]
    categories = refs["categories"]
    complaints = {}

    # Scenario 1: same institution, open cases in two bureaus (RB + PGRC) -> overlap candidate
    complaints["rb_open"] = _create_complaint_with_history(
        db,
        case_reference="CW-2026-00001",
        institution_id=institutions["INST-0001"].id,
        category_id=categories["FEE"].id,
        bureau_id=bureaus["RB-DEL"].id,
        created_by_id=users["rb.officer"].id,
        assigned_officer_id=users["rb.officer"].id,
        subject="Excess tuition fee charged for 2025 batch",
        description="Students report tuition fees above the AICTE-approved ceiling.",
        priority=ComplaintPriority.HIGH,
        status=ComplaintStatus.UNDER_REVIEW,
        received_days_ago=10,
        expected_disposal_in_days=5,
    )
    complaints["pgrc_open"] = _create_complaint_with_history(
        db,
        case_reference="CW-2026-00002",
        institution_id=institutions["INST-0001"].id,
        category_id=categories["FEE"].id,
        bureau_id=bureaus["PGRC"].id,
        created_by_id=users["pgrc.officer"].id,
        assigned_officer_id=users["pgrc.officer"].id,
        subject="Fee overcharge grievance - same institute",
        description="A parent grievance about tuition fee exceeding the approved slab.",
        priority=ComplaintPriority.HIGH,
        status=ComplaintStatus.UNDER_REVIEW,
        received_days_ago=8,
        expected_disposal_in_days=7,
    )

    # Scenario 2: confirmed duplicate (same institute, near-identical subject, two bureaus)
    complaints["dup_a"] = _create_complaint_with_history(
        db,
        case_reference="CW-2026-00003",
        institution_id=institutions["INST-0002"].id,
        category_id=categories["ADM"].id,
        bureau_id=bureaus["RB-MUM"].id,
        created_by_id=users["rb.officer"].id,
        assigned_officer_id=users["rb.officer"].id,
        subject="Admissions made beyond sanctioned intake capacity",
        description="Reports of admissions exceeding sanctioned intake for CSE branch.",
        priority=ComplaintPriority.CRITICAL,
        status=ComplaintStatus.UNDER_PROCESS,
        received_days_ago=20,
        expected_disposal_in_days=-2,
    )
    complaints["dup_b"] = _create_complaint_with_history(
        db,
        case_reference="CW-2026-00004",
        institution_id=institutions["INST-0002"].id,
        category_id=categories["ADM"].id,
        bureau_id=bureaus["PGRC"].id,
        created_by_id=users["pgrc.officer"].id,
        assigned_officer_id=users["pgrc.officer"].id,
        subject="Admission beyond sanctioned intake capacity - CSE branch",
        description="Grievance about CSE admissions beyond the sanctioned intake limit.",
        priority=ComplaintPriority.CRITICAL,
        status=ComplaintStatus.UNDER_PROCESS,
        received_days_ago=18,
        expected_disposal_in_days=-1,
    )

    # Scenario 3: dismissed false positive (same institute, unrelated issues)
    complaints["fp_a"] = _create_complaint_with_history(
        db,
        case_reference="CW-2026-00005",
        institution_id=institutions["INST-0003"].id,
        category_id=categories["FAC"].id,
        bureau_id=bureaus["RB-DEL"].id,
        created_by_id=users["rb.officer"].id,
        assigned_officer_id=users["rb.officer"].id,
        subject="Shortage of qualified faculty in Mechanical dept",
        description="Faculty-to-student ratio below AICTE norms in Mechanical department.",
        priority=ComplaintPriority.MEDIUM,
        status=ComplaintStatus.UNDER_REVIEW,
        received_days_ago=5,
        expected_disposal_in_days=25,
    )
    complaints["fp_b"] = _create_complaint_with_history(
        db,
        case_reference="CW-2026-00006",
        institution_id=institutions["INST-0003"].id,
        category_id=categories["RAG"].id,
        bureau_id=bureaus["PGRC"].id,
        created_by_id=users["pgrc.officer"].id,
        assigned_officer_id=users["pgrc.officer"].id,
        subject="Anonymous complaint about a hostel safety incident",
        description="Unrelated hostel ragging/safety complaint, coincidentally same institute.",
        priority=ComplaintPriority.HIGH,
        status=ComplaintStatus.UNDER_REVIEW,
        received_days_ago=4,
        expected_disposal_in_days=11,
    )

    # Scenario 4: transferred case
    complaints["transferred"] = _create_complaint_with_history(
        db,
        case_reference="CW-2026-00007",
        institution_id=institutions["INST-0001"].id,
        category_id=categories["OTH"].id,
        bureau_id=bureaus["PGRC"].id,
        created_by_id=users["pgrc.officer"].id,
        assigned_officer_id=users["pgrc.officer"].id,
        subject="Jurisdiction dispute over affiliation complaint",
        description="Complaint filed with PGRC, transferred to RB-Delhi for jurisdiction.",
        priority=ComplaintPriority.LOW,
        status=ComplaintStatus.TRANSFERRED,
        received_days_ago=15,
        expected_disposal_in_days=30,
    )
    db.add(
        CaseActionHistory(
            complaint_id=complaints["transferred"].id,
            action_type=CaseActionType.TRANSFER,
            actor_id=users["pgrc.officer"].id,
            from_bureau_id=bureaus["PGRC"].id,
            to_bureau_id=bureaus["RB-DEL"].id,
            reason="Matter falls under Regional Bureau jurisdiction",
        )
    )

    # Scenario 5: disposed case
    complaints["disposed"] = _create_complaint_with_history(
        db,
        case_reference="CW-2026-00008",
        institution_id=institutions["INST-0002"].id,
        category_id=categories["FEE"].id,
        bureau_id=bureaus["RB-MUM"].id,
        created_by_id=users["rb.officer"].id,
        assigned_officer_id=users["rb.officer"].id,
        subject="Refund of caution deposit delayed beyond policy",
        description="Student caution deposit refund delayed beyond the institute's own policy.",
        priority=ComplaintPriority.MEDIUM,
        status=ComplaintStatus.DISPOSED,
        received_days_ago=40,
        expected_disposal_in_days=None,
        disposal_note="Institute refunded the caution deposit with interest; grievance resolved.",
    )
    db.add(
        CaseActionHistory(
            complaint_id=complaints["disposed"].id,
            action_type=CaseActionType.DISPOSE,
            actor_id=users["rb.officer"].id,
            reason=None,
            note="Refund confirmed by institute finance office; case closed.",
        )
    )

    db.flush()
    return complaints


def seed_overlap_alerts(db: Session, users: dict, institutions: dict, complaints: dict) -> None:
    def ensure_alert(
        institution_id, case_ids, status, score, rationale, decided_by=None, reason=None
    ):
        existing = (
            db.query(OverlapAlert)
            .filter_by(institution_id=institution_id, rationale=rationale)
            .one_or_none()
        )
        if existing is not None:
            return
        alert = OverlapAlert(
            institution_id=institution_id,
            matching_signals={"same_institution": True, "rationale": rationale},
            confidence_score=score,
            rationale=rationale,
            status=status,
            decided_by=decided_by.id if decided_by else None,
            decision_reason=reason,
            decided_at=utcnow() if decided_by else None,
        )
        db.add(alert)
        db.flush()
        for case_id in case_ids:
            db.add(OverlapAlertCase(overlap_alert_id=alert.id, complaint_id=case_id))

    # Open alert: same institution, same category, two bureaus, needs human review
    ensure_alert(
        institutions["INST-0001"].id,
        [complaints["rb_open"].id, complaints["pgrc_open"].id],
        OverlapAlertStatus.OPEN,
        0.72,
        "Same institution and category (Fee Refund) open concurrently in RB-Delhi and PGRC.",
    )

    # Confirmed duplicate
    ensure_alert(
        institutions["INST-0002"].id,
        [complaints["dup_a"].id, complaints["dup_b"].id],
        OverlapAlertStatus.CONFIRMED,
        0.91,
        "Near-identical subject text and same category across RB-Mumbai and PGRC.",
        decided_by=users["management"],
        reason="Confirmed as the same admissions-capacity issue; bureaus asked to coordinate.",
    )

    # Dismissed false positive
    ensure_alert(
        institutions["INST-0003"].id,
        [complaints["fp_a"].id, complaints["fp_b"].id],
        OverlapAlertStatus.DISMISSED,
        0.58,
        "Same institution flagged, but subjects concern unrelated departments/issues.",
        decided_by=users["rb.officer"],
        reason="Faculty shortage and hostel safety are unrelated matters; false positive.",
    )
    db.flush()


def main() -> None:
    settings = get_settings()
    if settings.is_production:
        print("Refusing to seed demo data: APP_ENV=production.", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        refs = seed_reference_data(db)
        users = seed_users(db, refs["bureaus"], refs["regions"])
        institutions = seed_institutions(db, refs["regions"])
        complaints = seed_complaints(db, refs, users, institutions)
        seed_overlap_alerts(db, users, institutions, complaints)
        db.commit()
        print("Seed complete. Demo users (all share the password 'Demo@12345'):")
        for user in users.values():
            print(f"  {user.email}  ({user.role.value})")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
