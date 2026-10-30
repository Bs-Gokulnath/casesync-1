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


def test_summary_and_csv_export_reflect_real_data(
    client: TestClient, db: Session, login_as
) -> None:
    region = make_region(db)
    bureau = make_bureau(db)
    category = make_category(db)
    make_sla_policy(db, priority=ComplaintPriority.MEDIUM, days_to_resolve=30)
    institution = make_institution(db, region_id=region.id)
    make_user(
        db,
        email="officer@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=bureau.id,
    )
    make_user(db, email="admin@aictecasewatch-demo.org", role=UserRole.SYSTEM_ADMIN)
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")

    client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "=cmd|'/c calc'!A1 formula-looking subject",
            "description": "A complaint with a subject crafted to look like a spreadsheet formula.",
        },
        headers={"X-CSRF-Token": csrf},
    )

    login_as("admin@aictecasewatch-demo.org", "Correct-Horse-1")
    summary = client.get("/api/v1/analytics/summary")
    assert summary.status_code == 200
    body = summary.json()
    assert body["total"] == 1
    assert any(row["key"] == "received" for row in body["by_status"])

    export = client.get("/api/v1/analytics/export.csv")
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("text/csv")
    # The formula-looking subject must be neutralized with a leading quote,
    # never appear as a bare cell starting with "=" (which Excel/Sheets
    # would execute as a formula).
    assert ",=cmd" not in export.text
    assert "'=cmd" in export.text


def test_analytics_export_requires_permission(client: TestClient, db: Session, login_as) -> None:
    make_user(db, email="auditor@aictecasewatch-demo.org", role=UserRole.AUDITOR)
    login_as("auditor@aictecasewatch-demo.org", "Correct-Horse-1")

    response = client.get("/api/v1/analytics/export.csv")
    assert response.status_code == 403
