import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from tests.fixtures.factories import make_bureau, make_region, make_user

pytestmark = pytest.mark.integration


def test_create_and_fetch_institution(client: TestClient, db: Session, login_as) -> None:
    region = make_region(db)
    make_user(db, email="admin@aictecasewatch-demo.org", role=UserRole.SYSTEM_ADMIN)
    csrf_token = login_as("admin@aictecasewatch-demo.org", "Correct-Horse-1")

    create_response = client.post(
        "/api/v1/institutions",
        json={"name": "Delta Institute of Technology", "region_id": region.id},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["institution_code"].startswith("INST-")
    assert created["is_active"] is True

    detail_response = client.get(f"/api/v1/institutions/{created['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["total_complaint_count"] == 0
    assert detail["open_complaint_count"] == 0


def test_duplicate_aicte_id_is_rejected(client: TestClient, db: Session, login_as) -> None:
    region = make_region(db)
    make_user(db, email="admin2@aictecasewatch-demo.org", role=UserRole.SYSTEM_ADMIN)
    csrf_token = login_as("admin2@aictecasewatch-demo.org", "Correct-Horse-1")

    payload = {
        "name": "Meridian College of Engineering",
        "region_id": region.id,
        "aicte_permanent_id": "AICTE-9999",
    }
    first = client.post("/api/v1/institutions", json=payload, headers={"X-CSRF-Token": csrf_token})
    assert first.status_code == 201

    second = client.post("/api/v1/institutions", json=payload, headers={"X-CSRF-Token": csrf_token})
    assert second.status_code == 409


def test_auditor_cannot_create_institution(client: TestClient, db: Session, login_as) -> None:
    region = make_region(db)
    make_user(db, email="auditor@aictecasewatch-demo.org", role=UserRole.AUDITOR)
    csrf_token = login_as("auditor@aictecasewatch-demo.org", "Correct-Horse-1")

    response = client.post(
        "/api/v1/institutions",
        json={"name": "Sunrise Polytechnic", "region_id": region.id},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 403


def test_create_requires_csrf_header(client: TestClient, db: Session, login_as) -> None:
    region = make_region(db)
    make_user(db, email="admin3@aictecasewatch-demo.org", role=UserRole.SYSTEM_ADMIN)
    login_as("admin3@aictecasewatch-demo.org", "Correct-Horse-1")

    response = client.post(
        "/api/v1/institutions", json={"name": "No CSRF College", "region_id": region.id}
    )
    assert response.status_code == 403


def test_list_institutions_supports_search(client: TestClient, db: Session, login_as) -> None:
    region = make_region(db)
    make_bureau(db)
    make_user(db, email="admin4@aictecasewatch-demo.org", role=UserRole.SYSTEM_ADMIN)
    csrf_token = login_as("admin4@aictecasewatch-demo.org", "Correct-Horse-1")

    client.post(
        "/api/v1/institutions",
        json={"name": "Zenith School of Mines", "region_id": region.id},
        headers={"X-CSRF-Token": csrf_token},
    )
    client.post(
        "/api/v1/institutions",
        json={"name": "Alpha Institute of Design", "region_id": region.id},
        headers={"X-CSRF-Token": csrf_token},
    )

    response = client.get("/api/v1/institutions", params={"q": "zenith"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Zenith School of Mines"


def test_list_total_reflects_every_matching_row_not_just_one(
    client: TestClient, db: Session, login_as
) -> None:
    """Regression test for a real bug: the shared pagination count query
    once used `stmt.with_only_columns(func.count())`, which silently drops
    the FROM clause and always reports total=1 no matter how many rows
    actually match. Every other test here happened to create exactly one
    matching row, so none of them caught it.
    """
    region = make_region(db)
    make_user(db, email="admin5@aictecasewatch-demo.org", role=UserRole.SYSTEM_ADMIN)
    csrf_token = login_as("admin5@aictecasewatch-demo.org", "Correct-Horse-1")

    for name in ["Institute One", "Institute Two", "Institute Three"]:
        client.post(
            "/api/v1/institutions",
            json={"name": name, "region_id": region.id},
            headers={"X-CSRF-Token": csrf_token},
        )

    response = client.get("/api/v1/institutions")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3
