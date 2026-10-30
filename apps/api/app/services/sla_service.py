from datetime import date

from app.models.complaint import Complaint
from app.models.enums import ComplaintStatus

CLOSED_STATUSES = {ComplaintStatus.DISPOSED}


def is_overdue(complaint: Complaint, *, today: date | None = None) -> bool:
    if complaint.status in CLOSED_STATUSES:
        return False
    if complaint.expected_disposal_date is None:
        return False
    return complaint.expected_disposal_date < (today or date.today())


def days_until_due(complaint: Complaint, *, today: date | None = None) -> int | None:
    if complaint.expected_disposal_date is None:
        return None
    return (complaint.expected_disposal_date - (today or date.today())).days


def is_approaching_deadline(
    complaint: Complaint, *, warning_days: int = 3, today: date | None = None
) -> bool:
    if complaint.status in CLOSED_STATUSES:
        return False
    days_left = days_until_due(complaint, today=today)
    if days_left is None:
        return False
    return 0 <= days_left <= warning_days
