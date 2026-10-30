from app.models.enums import ComplaintStatus
from app.services.workflow_service import is_transition_allowed


def test_received_can_move_to_under_review_or_be_transferred() -> None:
    assert is_transition_allowed(ComplaintStatus.RECEIVED, ComplaintStatus.UNDER_REVIEW)
    assert is_transition_allowed(ComplaintStatus.RECEIVED, ComplaintStatus.TRANSFERRED)
    assert not is_transition_allowed(ComplaintStatus.RECEIVED, ComplaintStatus.DISPOSED)


def test_disposed_is_a_dead_end_for_ordinary_transitions() -> None:
    for status in ComplaintStatus:
        assert not is_transition_allowed(ComplaintStatus.DISPOSED, status)


def test_escalated_can_only_resume_processing_or_be_disposed() -> None:
    assert is_transition_allowed(ComplaintStatus.ESCALATED, ComplaintStatus.UNDER_PROCESS)
    assert is_transition_allowed(ComplaintStatus.ESCALATED, ComplaintStatus.DISPOSED)
    assert not is_transition_allowed(ComplaintStatus.ESCALATED, ComplaintStatus.TRANSFERRED)
    assert not is_transition_allowed(ComplaintStatus.ESCALATED, ComplaintStatus.RECEIVED)


def test_transferred_case_must_be_reviewed_again_by_the_new_bureau() -> None:
    assert is_transition_allowed(ComplaintStatus.TRANSFERRED, ComplaintStatus.UNDER_REVIEW)
    assert not is_transition_allowed(ComplaintStatus.TRANSFERRED, ComplaintStatus.DISPOSED)


def test_every_open_status_can_eventually_reach_disposed() -> None:
    open_statuses = [
        ComplaintStatus.UNDER_REVIEW,
        ComplaintStatus.UNDER_PROCESS,
        ComplaintStatus.PENDING_INFORMATION,
        ComplaintStatus.ESCALATED,
    ]
    for status in open_statuses:
        assert is_transition_allowed(status, ComplaintStatus.DISPOSED)
