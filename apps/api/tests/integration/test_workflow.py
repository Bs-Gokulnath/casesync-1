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


def _create_complaint(client: TestClient, db: Session, csrf: str) -> dict:
    region = make_region(db)
    make_sla_policy(db, priority=ComplaintPriority.MEDIUM, days_to_resolve=30)
    category = make_category(db)
    institution = make_institution(db, region_id=region.id)

    response = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Lifecycle test complaint",
            "description": "A complaint used to exercise the full workflow lifecycle.",
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 201
    return response.json()


def _officer(db: Session) -> tuple:
    bureau = make_bureau(db)
    officer = make_user(
        db,
        email="officer@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=bureau.id,
    )
    return bureau, officer


def test_full_lifecycle_review_process_dispose(client: TestClient, db: Session, login_as) -> None:
    _officer(db)
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")
    complaint = _create_complaint(client, db, csrf)
    complaint_id = complaint["id"]

    review = client.post(
        f"/api/v1/complaints/{complaint_id}/transition",
        json={"to_status": "under_review"},
        headers={"X-CSRF-Token": csrf},
    )
    assert review.status_code == 200
    assert review.json()["status"] == "under_review"

    process = client.post(
        f"/api/v1/complaints/{complaint_id}/transition",
        json={"to_status": "under_process"},
        headers={"X-CSRF-Token": csrf},
    )
    assert process.status_code == 200

    disposed = client.post(
        f"/api/v1/complaints/{complaint_id}/dispose",
        json={"disposal_note": "Issue resolved and refund processed."},
        headers={"X-CSRF-Token": csrf},
    )
    assert disposed.status_code == 200
    assert disposed.json()["status"] == "disposed"
    assert disposed.json()["disposal_note"] == "Issue resolved and refund processed."


def test_cannot_skip_straight_from_received_to_disposed(
    client: TestClient, db: Session, login_as
) -> None:
    _officer(db)
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")
    complaint = _create_complaint(client, db, csrf)

    response = client.post(
        f"/api/v1/complaints/{complaint['id']}/dispose",
        json={"disposal_note": "Not allowed yet"},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 409


def test_transfer_moves_bureau_and_clears_assignment(
    client: TestClient, db: Session, login_as
) -> None:
    _officer(db)
    target_bureau = make_bureau(db, code="PGRC", name="PGRC")
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")
    complaint = _create_complaint(client, db, csrf)

    transfer = client.post(
        f"/api/v1/complaints/{complaint['id']}/transfer",
        json={"to_bureau_id": target_bureau.id, "reason": "Jurisdiction belongs to PGRC"},
        headers={"X-CSRF-Token": csrf},
    )
    assert transfer.status_code == 200
    body = transfer.json()
    assert body["status"] == "transferred"
    assert body["bureau_id"] == target_bureau.id
    assert body["assigned_officer_id"] is None


def test_reopen_requires_system_admin_permission(client: TestClient, db: Session, login_as) -> None:
    bureau, _ = _officer(db)
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")
    complaint = _create_complaint(client, db, csrf)

    client.post(
        f"/api/v1/complaints/{complaint['id']}/transition",
        json={"to_status": "under_review"},
        headers={"X-CSRF-Token": csrf},
    )
    disposed = client.post(
        f"/api/v1/complaints/{complaint['id']}/dispose",
        json={"disposal_note": "Closed."},
        headers={"X-CSRF-Token": csrf},
    )
    assert disposed.status_code == 200

    forbidden = client.post(
        f"/api/v1/complaints/{complaint['id']}/reopen",
        json={"reason": "Bureau officer should not be able to do this"},
        headers={"X-CSRF-Token": csrf},
    )
    assert forbidden.status_code == 403

    make_user(db, email="admin@aictecasewatch-demo.org", role=UserRole.SYSTEM_ADMIN)
    admin_csrf = login_as("admin@aictecasewatch-demo.org", "Correct-Horse-1")
    allowed = client.post(
        f"/api/v1/complaints/{complaint['id']}/reopen",
        json={"reason": "New evidence submitted by the complainant"},
        headers={"X-CSRF-Token": admin_csrf},
    )
    assert allowed.status_code == 200
    assert allowed.json()["status"] == "under_review"


def test_assign_sets_officer_and_bureau_officer_can_assign_within_their_bureau(
    client: TestClient, db: Session, login_as
) -> None:
    bureau, officer = _officer(db)
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")
    complaint = _create_complaint(client, db, csrf)

    response = client.post(
        f"/api/v1/complaints/{complaint['id']}/assign",
        json={"officer_id": officer.id},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 200
    assert response.json()["assigned_officer_id"] == officer.id
