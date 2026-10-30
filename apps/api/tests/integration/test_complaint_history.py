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


def test_history_records_creation_transition_and_transfer(
    client: TestClient, db: Session, login_as
) -> None:
    region = make_region(db)
    bureau_a = make_bureau(db, code="RB-DEL", name="Regional Bureau - Delhi")
    bureau_b = make_bureau(db, code="PGRC", name="PGRC")
    category = make_category(db)
    make_sla_policy(db, priority=ComplaintPriority.MEDIUM, days_to_resolve=30)
    institution = make_institution(db, region_id=region.id)
    make_user(
        db,
        email="officer@aictecasewatch-demo.org",
        role=UserRole.BUREAU_OFFICER,
        bureau_id=bureau_a.id,
    )
    csrf = login_as("officer@aictecasewatch-demo.org", "Correct-Horse-1")

    created = client.post(
        "/api/v1/complaints",
        json={
            "institution_id": institution.id,
            "category_id": category.id,
            "subject": "History test complaint",
            "description": "A complaint used to verify the timeline endpoint.",
        },
        headers={"X-CSRF-Token": csrf},
    ).json()

    client.post(
        f"/api/v1/complaints/{created['id']}/transition",
        json={"to_status": "under_review", "reason": "Starting review"},
        headers={"X-CSRF-Token": csrf},
    )
    client.post(
        f"/api/v1/complaints/{created['id']}/transfer",
        json={"to_bureau_id": bureau_b.id, "reason": "Wrong jurisdiction"},
        headers={"X-CSRF-Token": csrf},
    )

    history = client.get(f"/api/v1/complaints/{created['id']}/history")
    assert history.status_code == 200
    entries = history.json()

    kinds = [e["kind"] for e in entries]
    assert kinds.count("status_change") == 3  # received, under_review, transferred
    assert kinds.count("action") == 1  # the transfer action record
    assert entries == sorted(entries, key=lambda e: e["created_at"])
