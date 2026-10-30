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


def _setup(db: Session):
    region = make_region(db)
    bureau_a = make_bureau(db, code="RB-DEL", name="Regional Bureau - Delhi")
    bureau_b = make_bureau(db, code="PGRC", name="PGRC")
    category = make_category(db)
    make_sla_policy(db, priority=ComplaintPriority.MEDIUM, days_to_resolve=30)
    institution = make_institution(db, region_id=region.id)
    officer_a = make_user(
        db, email="a@aictecasewatch-demo.org", role=UserRole.BUREAU_OFFICER, bureau_id=bureau_a.id
    )
    officer_b = make_user(
        db, email="b@aictecasewatch-demo.org", role=UserRole.BUREAU_OFFICER, bureau_id=bureau_b.id
    )
    return bureau_a, bureau_b, category, institution, officer_a, officer_b


def test_creating_similar_complaint_in_another_bureau_raises_an_open_alert(
    client: TestClient, db: Session, login_as
) -> None:
    _, _, category, institution, _, _ = _setup(db)

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

    alerts = client.get("/api/v1/overlaps", params={"institution_id": institution.id})
    assert alerts.status_code == 200
    body = alerts.json()
    assert body["total"] == 1
    alert = body["items"][0]
    assert alert["status"] == "open"
    assert len(alert["case_ids"]) == 2


def test_unrelated_complaints_same_institution_do_not_raise_an_alert(
    client: TestClient, db: Session, login_as
) -> None:
    _, _, category, institution, _, _ = _setup(db)
    category_2 = make_category(db, code="RAG", name="Ragging")

    csrf_a = login_as("a@aictecasewatch-demo.org", "Correct-Horse-1")
    client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Shortage of qualified faculty in mechanical department",
            "description": "Faculty-to-student ratio below AICTE norms in Mechanical department.",
        },
        headers={"X-CSRF-Token": csrf_a},
    )

    csrf_b = login_as("b@aictecasewatch-demo.org", "Correct-Horse-1")
    client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category_2.id,
            "subject": "Anonymous complaint about a hostel safety incident",
            "description": "Unrelated hostel ragging and safety complaint.",
        },
        headers={"X-CSRF-Token": csrf_b},
    )

    alerts = client.get("/api/v1/overlaps", params={"institution_id": institution.id})
    assert alerts.status_code == 200
    assert alerts.json()["total"] == 0


def test_decision_requires_overlap_decide_permission_and_never_mutates_cases(
    client: TestClient, db: Session, login_as
) -> None:
    _, _, category, institution, _, _ = _setup(db)

    csrf_a = login_as("a@aictecasewatch-demo.org", "Correct-Horse-1")
    first = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Excess tuition fee charged beyond approved ceiling",
            "description": "Students report tuition fees above the AICTE-approved ceiling.",
        },
        headers={"X-CSRF-Token": csrf_a},
    ).json()

    csrf_b = login_as("b@aictecasewatch-demo.org", "Correct-Horse-1")
    second = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Tuition fee charged beyond approved ceiling at same institute",
            "description": "Parent grievance about tuition fee exceeding the approved ceiling.",
        },
        headers={"X-CSRF-Token": csrf_b},
    ).json()

    alerts = client.get("/api/v1/overlaps", params={"institution_id": institution.id}).json()
    alert_id = alerts["items"][0]["id"]

    # bureau officers are case handlers and DO hold overlap:decide in this permission matrix
    decision = client.post(
        f"/api/v1/overlaps/{alert_id}/decision",
        json={
            "status": "confirmed",
            "reason": "Same underlying fee issue; bureaus will coordinate",
        },
        headers={"X-CSRF-Token": csrf_b},
    )
    assert decision.status_code == 200
    assert decision.json()["status"] == "confirmed"

    # deciding never changes the underlying complaints' own status
    first_after = client.get(f"/api/v1/complaints/{first['id']}").json()
    second_after = client.get(f"/api/v1/complaints/{second['id']}").json()
    assert first_after["status"] == "received"
    assert second_after["status"] == "received"


def test_auditor_cannot_decide_an_overlap_alert(client: TestClient, db: Session, login_as) -> None:
    _, _, category, institution, _, _ = _setup(db)
    make_user(db, email="auditor@aictecasewatch-demo.org", role=UserRole.AUDITOR)

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

    auditor_csrf = login_as("auditor@aictecasewatch-demo.org", "Correct-Horse-1")
    alerts = client.get("/api/v1/overlaps", params={"institution_id": institution.id}).json()
    alert_id = alerts["items"][0]["id"]

    response = client.post(
        f"/api/v1/overlaps/{alert_id}/decision",
        json={"status": "dismissed", "reason": "Auditors should not be able to do this"},
        headers={"X-CSRF-Token": auditor_csrf},
    )
    assert response.status_code == 403
