from datetime import date, timedelta

from app.models.complaint import Complaint
from app.models.enums import ComplaintPriority, ComplaintSource, ComplaintStatus
from app.services.sla_service import is_approaching_deadline, is_overdue


def _complaint(*, status: ComplaintStatus, expected_disposal_date) -> Complaint:
    return Complaint(
        case_reference="CW-TEST-00001",
        institution_id=1,
        category_id=1,
        subject="x",
        normalized_subject="x",
        description="x",
        source=ComplaintSource.PORTAL,
        priority=ComplaintPriority.MEDIUM,
        status=status,
        bureau_id=1,
        received_date=date.today() - timedelta(days=10),
        expected_disposal_date=expected_disposal_date,
        created_by=1,
    )


def test_overdue_when_past_expected_disposal_date_and_still_open() -> None:
    today = date(2026, 1, 20)
    complaint = _complaint(
        status=ComplaintStatus.UNDER_PROCESS, expected_disposal_date=date(2026, 1, 10)
    )
    assert is_overdue(complaint, today=today)


def test_not_overdue_when_disposed_even_if_past_due_date() -> None:
    today = date(2026, 1, 20)
    complaint = _complaint(
        status=ComplaintStatus.DISPOSED, expected_disposal_date=date(2026, 1, 10)
    )
    assert not is_overdue(complaint, today=today)


def test_not_overdue_without_an_expected_disposal_date() -> None:
    complaint = _complaint(status=ComplaintStatus.UNDER_REVIEW, expected_disposal_date=None)
    assert not is_overdue(complaint, today=date.today())


def test_approaching_deadline_within_warning_window() -> None:
    today = date(2026, 1, 10)
    complaint = _complaint(
        status=ComplaintStatus.UNDER_REVIEW, expected_disposal_date=date(2026, 1, 12)
    )
    assert is_approaching_deadline(complaint, warning_days=3, today=today)


def test_not_approaching_deadline_when_far_in_the_future() -> None:
    today = date(2026, 1, 1)
    complaint = _complaint(
        status=ComplaintStatus.UNDER_REVIEW, expected_disposal_date=date(2026, 2, 1)
    )
    assert not is_approaching_deadline(complaint, warning_days=3, today=today)
