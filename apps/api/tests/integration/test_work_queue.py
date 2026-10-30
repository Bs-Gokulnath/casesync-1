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


def test_mine_only_shows_complaints_assigned_to_me(
    client: TestClient, db: Session, login_as
) -> None:
    region = make_region(db)
    bureau = make_bureau(db)
    category = make_category(db)
    make_sla_policy(db, priority=ComplaintPriority.MEDIUM, days_to_resolve=30)
    institution = make_institution(db, region_id=region.id)
    officer_a = make_user(
        db, email="a@aictecasewatch-demo.org", role=UserRole.BUREAU_OFFICER, bureau_id=bureau.id
    )
    make_user(
        db, email="b@aictecasewatch-demo.org", role=UserRole.BUREAU_OFFICER, bureau_id=bureau.id
    )
    csrf = login_as("a@aictecasewatch-demo.org", "Correct-Horse-1")

    complaint = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "Work queue test complaint",
            "description": "A complaint used to verify work-queue scoping.",
        },
        headers={"X-CSRF-Token": csrf},
    ).json()
    client.post(
        f"/api/v1/complaints/{complaint['id']}/assign",
        json={"officer_id": officer_a.id},
        headers={"X-CSRF-Token": csrf},
    )

    mine = client.get("/api/v1/work-queue/mine")
    assert mine.status_code == 200
    assert mine.json()["total"] == 1

    login_as("b@aictecasewatch-demo.org", "Correct-Horse-1")
    others = client.get("/api/v1/work-queue/mine")
    assert others.json()["total"] == 0

    unassigned = client.get("/api/v1/work-queue/unassigned")
    assert unassigned.json()["total"] == 0  # the one complaint in this bureau is now assigned
