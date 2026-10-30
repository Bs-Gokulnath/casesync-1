import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import ComplaintPriority, UserRole
from tests.fixtures.factories import (
    make_bureau,
    make_category,
    make_institution,
    make_region,
    make_sla_policy,
    make_user,
)

pytestmark = pytest.mark.integration


def _setup_common(db: Session):
    region = make_region(db)
    bureau_a = make_bureau(db, code="RB-DEL", name="Regional Bureau - Delhi")
    bureau_b = make_bureau(db, code="PGRC", name="PGRC")
    category = make_category(db)
    make_sla_policy(db, priority=ComplaintPriority.MEDIUM, days_to_resolve=30)
    institution = make_institution(db, region_id=region.id)
    return region, bureau_a, bureau_b, category, institution


def test_bureau_officer_create_is_scoped_to_their_bureau(client: TestClient, db: Session, login_as):
    _, bureau_a, bureau_b, category, institution = _setup_common(db)
    make_user(
        db,
        email="officer@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=bureau_a.id,
    )
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")

    response = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Excess tuition fee charged",
            "description": "Fees above the AICTE-approved ceiling were charged to students.",
            "bureau_id": bureau_b.id,  # attempt to pick a different bureau than their own
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["bureau_id"] == bureau_a.id  # server ignores client-supplied bureau_id
    assert body["status"] == "received"
    assert body["case_reference"].startswith("CW-")
    assert body["expected_disposal_date"] is not None


def test_bureau_officer_only_sees_their_bureau_complaints(
    client: TestClient, db: Session, login_as
):
    _, bureau_a, bureau_b, category, institution = _setup_common(db)
    officer_a = make_user(
        db, email="a@aictecasewatch-demo.org", role=UserRole.BUREAU_OFFICER, bureau_id=bureau_a.id
    )
    make_user(
        db, email="b@aictecasewatch-demo.org", role=UserRole.BUREAU_OFFICER, bureau_id=bureau_b.id
    )

    csrf_a = login_as("a@aictecasewatch-demo.org", "Correct-Horse-1")
    client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Bureau A complaint",
            "description": "A complaint that belongs to bureau A only.",
        },
        headers={"X-CSRF-Token": csrf_a},
    )

    csrf_b = login_as("b@aictecasewatch-demo.org", "Correct-Horse-1")
    client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Bureau B complaint",
            "description": "A complaint that belongs to bureau B only.",
        },
        headers={"X-CSRF-Token": csrf_b},
    )

    login_as("a@aictecasewatch-demo.org", "Correct-Horse-1")
    listing = client.get("/api/v1/complaints")
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 1
    assert body["items"][0]["bureau_id"] == officer_a.bureau_id


def test_regional_officer_requires_explicit_bureau(client: TestClient, db: Session, login_as):
    region, bureau_a, _, category, institution = _setup_common(db)
    make_user(
        db,
        email="regional@aictecasewatch-demo.org",
        role=UserRole.REGIONAL_OFFICER,
        region_id=region.id,
    )
    csrf = login_as("regional@aictecasewatch-demo.org", "Correct-Horse-1")

    missing_bureau = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Needs a bureau",
            "description": "Regional officers must name the handling bureau explicitly.",
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert missing_bureau.status_code == 400

    with_bureau = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Has a bureau now",
            "description": "Regional officer explicitly names the RB-Delhi bureau.",
            "bureau_id": bureau_a.id,
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert with_bureau.status_code == 201
    assert with_bureau.json()["bureau_id"] == bureau_a.id


def test_auditor_cannot_create_complaint(client: TestClient, db: Session, login_as):
    _, _, _, category, institution = _setup_common(db)
    make_user(db, email="auditor@aictecasewatch-demo.org", role=UserRole.AUDITOR)
    csrf = login_as("auditor@aictecasewatch-demo.org", "Correct-Horse-1")

    response = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Should be rejected",
            "description": "Auditors are read-only and must not create complaints.",
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 403
