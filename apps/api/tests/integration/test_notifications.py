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


def test_assignment_notifies_the_officer(client: TestClient, db: Session, login_as) -> None:
    region = make_region(db)
    bureau = make_bureau(db)
    category = make_category(db)
    make_sla_policy(db, priority=ComplaintPriority.MEDIUM, days_to_resolve=30)
    institution = make_institution(db, region_id=region.id)
    make_user(
        db,
        email="creator@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=bureau.id,
    )
    officer = make_user(
        db,
        email="officer@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=bureau.id,
    )
    csrf = login_as("creator@aictecasewatch-demo.org", "Correct-Horse-1")

    complaint = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Notification test complaint",
            "description": "A complaint used to verify assignment notifications.",
        },
        headers={"X-CSRF-Token": csrf},
    ).json()

    client.post(
        f"/api/v1/complaints/{complaint['id']}/assign",
        json={"officer_id": officer.id},
        headers={"X-CSRF-Token": csrf},
    )

    officer_csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")
    notifications = client.get("/api/v1/notifications").json()
    assert notifications["total"] == 1
    assert notifications["items"][0]["type"] == "assignment"
    assert notifications["items"][0]["is_read"] is False

    notif_id = notifications["items"][0]["id"]
    mark = client.post(
        f"/api/v1/notifications/{notif_id}/read", headers={"X-CSRF-Token": officer_csrf}
    )
    assert mark.status_code == 200

    after = client.get("/api/v1/notifications").json()
    assert after["items"][0]["is_read"] is True


def test_overlap_alert_notifies_both_bureaus(client: TestClient, db: Session, login_as) -> None:
    region = make_region(db)
    bureau_a = make_bureau(db, code="RB-DEL", name="Regional Bureau - Delhi")
    bureau_b = make_bureau(db, code="PGRC", name="PGRC")
    category = make_category(db)
    make_sla_policy(db, priority=ComplaintPriority.MEDIUM, days_to_resolve=30)
    institution = make_institution(db, region_id=region.id)
    make_user(
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
            "subject": "Excess tuition fee charged beyond approved ceiling",
            "description": "Students report tuition fees above the AICTE-approved ceiling.",
        },
        headers={"X-CSRF-Token": csrf_a},
    )
    csrf_b = login_as("b@aictecasewatch-demo.org", "Correct-Horse-1")
    client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Tuition fee charged beyond approved ceiling at same institute",
            "description": "Parent grievance about tuition fee exceeding the approved ceiling.",
        },
        headers={"X-CSRF-Token": csrf_b},
    )

    login_as("a@aictecasewatch-demo.org", "Correct-Horse-1")
    notifications_a = client.get("/api/v1/notifications").json()
    assert any(n["type"] == "overlap_alert" for n in notifications_a["items"])

    login_as("b@aictecasewatch-demo.org", "Correct-Horse-1")
    notifications_b = client.get("/api/v1/notifications").json()
    assert any(n["type"] == "overlap_alert" for n in notifications_b["items"])
