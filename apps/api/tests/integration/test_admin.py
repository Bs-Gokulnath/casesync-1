import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from tests.fixtures.factories import make_user

pytestmark = pytest.mark.integration


def test_system_admin_can_create_a_bureau(client: TestClient, db: Session, login_as) -> None:
    make_user(db, email="admin@aictecasewatch-demo.org", role=UserRole.SYSTEM_ADMIN)
    csrf = login_as("admin@aictecasewatch-demo.org", "Correct-Horse-1")

    response = client.post(
        "/api/v1/admin/bureaus",
        json={"code": "RB-CHE", "name": "Regional Bureau - Chennai"},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 201
    assert response.json()["code"] == "RB-CHE"

    listing = client.get("/api/v1/admin/bureaus")
    assert listing.status_code == 200
    assert any(b["code"] == "RB-CHE" for b in listing.json())


def test_bureau_officer_cannot_manage_admin_resources(
    client: TestClient, db: Session, login_as
) -> None:
    make_user(db, email="officer@aictecasewatch-demo.org", role=UserRole.BUREAU_OFFICER)
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")

    response = client.post(
        "/api/v1/admin/bureaus",
        json={"code": "RB-XXX", "name": "Should not work"},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 403


def test_admin_can_create_and_deactivate_a_user(client: TestClient, db: Session, login_as) -> None:
    make_user(db, email="admin2@aictecasewatch-demo.org", role=UserRole.SYSTEM_ADMIN)
    csrf = login_as("admin2@aictecasewatch-demo.org", "Correct-Horse-1")

    created = client.post(
        "/api/v1/admin/users",
        json={
            "employee_code": "EMP-NEW",
            "full_name": "New Officer",
            "email": "new.officer@aictecasewatch-demo.org",
            "password": "Correct-Horse-1",
            "role": "auditor",
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert created.status_code == 201
    user_id = created.json()["id"]

    deactivated = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"is_active": False},
        headers={"X-CSRF-Token": csrf},
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "new.officer@aictecasewatch-demo.org", "password": "Correct-Horse-1"},
    )
    assert login_response.status_code == 401
