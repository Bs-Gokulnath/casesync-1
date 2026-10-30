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


def _setup(db: Session) -> dict:
    region = make_region(db)
    make_sla_policy(db, priority=ComplaintPriority.MEDIUM, days_to_resolve=30)
    category = make_category(db)
    institution = make_institution(db, region_id=region.id)
    bureau = make_bureau(db)
    return {"institution": institution, "category": category, "bureau": bureau}


def _create_complaint(client: TestClient, ctx: dict, csrf: str, subject: str) -> dict:
    response = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": ctx["institution"].id,
            "category_id": ctx["category"].id,
            "subject": subject,
            "description": "A complaint used to verify explicit case relationships.",
        },
        headers={"X-CSRF-Token": csrf},
    )
    return response.json()


def test_relating_two_complaints_is_symmetric(client: TestClient, db: Session, login_as) -> None:
    ctx = _setup(db)
    make_user(
        db,
        email="officer@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=ctx["bureau"].id,
    )
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")

    a = _create_complaint(client, ctx, csrf, "First complaint")
    b = _create_complaint(client, ctx, csrf, "Second, likely duplicate complaint")

    response = client.post(
        f"/api/v1/complaints/{a['id']}/relationships",
        json={"related_complaint_id": b["id"], "relationship_type": "duplicate"},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 201

    forward = client.get(f"/api/v1/complaints/{a['id']}/relationships").json()
    assert any(r["related_complaint_id"] == b["id"] for r in forward)

    backward = client.get(f"/api/v1/complaints/{b['id']}/relationships").json()
    assert any(r["related_complaint_id"] == a["id"] for r in backward)


def test_cannot_relate_a_complaint_to_itself(client: TestClient, db: Session, login_as) -> None:
    ctx = _setup(db)
    make_user(
        db,
        email="officer2@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=ctx["bureau"].id,
    )
    csrf = login_as("officer2@aictecasewatch-demo.org", "Correct-Horse-1")
    a = _create_complaint(client, ctx, csrf, "Self-relation test complaint")

    response = client.post(
        f"/api/v1/complaints/{a['id']}/relationships",
        json={"related_complaint_id": a["id"], "relationship_type": "related"},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 400


def test_auditor_cannot_create_relationships(client: TestClient, db: Session, login_as) -> None:
    ctx = _setup(db)
    make_user(
        db,
        email="officer3@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=ctx["bureau"].id,
    )
    csrf = login_as("officer3@aictecasewatch-demo.org", "Correct-Horse-1")
    a = _create_complaint(client, ctx, csrf, "Complaint A")
    b = _create_complaint(client, ctx, csrf, "Complaint B")

    make_user(db, email="auditor@aictecasewatch-demo.org", role=UserRole.AUDITOR)
    auditor_csrf = login_as("auditor@aictecasewatch-demo.org", "Correct-Horse-1")

    response = client.post(
        f"/api/v1/complaints/{a['id']}/relationships",
        json={"related_complaint_id": b["id"], "relationship_type": "related"},
        headers={"X-CSRF-Token": auditor_csrf},
    )
    assert response.status_code == 403
