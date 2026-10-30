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
            "subject": "Document test complaint",
            "description": "A complaint used to verify document upload/download.",
        },
        headers={"X-CSRF-Token": csrf},
    )
    return response.json()


def test_upload_and_download_a_document(client: TestClient, db: Session, login_as) -> None:
    bureau = make_bureau(db)
    make_user(
        db,
        email="officer@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=bureau.id,
    )
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")
    complaint = _create_complaint(client, db, csrf)

    upload = client.post(
        f"/api/v1/complaints/{complaint['id']}/documents",
        files={"file": ("evidence.pdf", b"%PDF-1.4 fake pdf content", "application/pdf")},
        headers={"X-CSRF-Token": csrf},
    )
    assert upload.status_code == 201
    doc = upload.json()
    assert doc["file_name"] == "evidence.pdf"

    listing = client.get(f"/api/v1/complaints/{complaint['id']}/documents")
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    download = client.get(f"/api/v1/complaints/{complaint['id']}/documents/{doc['id']}")
    assert download.status_code == 200
    assert download.content == b"%PDF-1.4 fake pdf content"


def test_rejects_disallowed_file_type(client: TestClient, db: Session, login_as) -> None:
    bureau = make_bureau(db)
    make_user(
        db,
        email="officer2@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=bureau.id,
    )
    csrf = login_as("officer2@aictecasewatch-demo.org", "Correct-Horse-1")
    complaint = _create_complaint(client, db, csrf)

    response = client.post(
        f"/api/v1/complaints/{complaint['id']}/documents",
        files={"file": ("script.exe", b"MZ fake binary", "application/x-msdownload")},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 400


def test_auditor_cannot_upload_but_can_read(client: TestClient, db: Session, login_as) -> None:
    bureau = make_bureau(db)
    make_user(
        db,
        email="officer3@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=bureau.id,
    )
    csrf = login_as("officer3@aictecasewatch-demo.org", "Correct-Horse-1")
    complaint = _create_complaint(client, db, csrf)

    make_user(db, email="auditor@aictecasewatch-demo.org", role=UserRole.AUDITOR)
    auditor_csrf = login_as("auditor@aictecasewatch-demo.org", "Correct-Horse-1")

    upload = client.post(
        f"/api/v1/complaints/{complaint['id']}/documents",
        files={"file": ("evidence.pdf", b"%PDF-1.4", "application/pdf")},
        headers={"X-CSRF-Token": auditor_csrf},
    )
    assert upload.status_code == 403

    listing = client.get(f"/api/v1/complaints/{complaint['id']}/documents")
    assert listing.status_code == 200
