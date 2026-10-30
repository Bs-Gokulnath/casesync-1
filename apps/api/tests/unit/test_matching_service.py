from datetime import date

from app.services.matching_service import MatchCandidate, compute_match


def _candidate(
    *, complaint_id: int, category_id: int, subject: str, received_date: date, bureau_id: int
) -> MatchCandidate:
    return MatchCandidate(
        complaint_id=complaint_id,
        category_id=category_id,
        normalized_subject=subject,
        received_date=received_date,
        bureau_id=bureau_id,
    )


def test_same_bureau_never_scores_as_an_overlap() -> None:
    a = _candidate(
        complaint_id=1,
        category_id=1,
        subject="excess tuition fee charged",
        received_date=date(2026, 1, 1),
        bureau_id=1,
    )
    b = _candidate(
        complaint_id=2,
        category_id=1,
        subject="excess tuition fee charged",
        received_date=date(2026, 1, 1),
        bureau_id=1,
    )
    result = compute_match(a, b)
    assert result.score == 0.0


def test_near_identical_subject_across_bureaus_scores_high() -> None:
    a = _candidate(
        complaint_id=1,
        category_id=1,
        subject="admissions made beyond sanctioned intake capacity",
        received_date=date(2026, 1, 1),
        bureau_id=1,
    )
    b = _candidate(
        complaint_id=2,
        category_id=1,
        subject="admission beyond sanctioned intake capacity cse branch",
        received_date=date(2026, 1, 3),
        bureau_id=2,
    )
    result = compute_match(a, b)
    assert result.score >= 0.55
    assert result.signals["same_category"] is True
    assert "institution" in result.rationale.lower()


def test_unrelated_subjects_same_institution_score_low() -> None:
    a = _candidate(
        complaint_id=1,
        category_id=1,
        subject="shortage of qualified faculty in mechanical dept",
        received_date=date(2026, 1, 1),
        bureau_id=1,
    )
    b = _candidate(
        complaint_id=2,
        category_id=2,
        subject="anonymous complaint about a hostel safety incident",
        received_date=date(2026, 6, 1),
        bureau_id=2,
    )
    result = compute_match(a, b)
    assert result.score < 0.55


def test_distant_received_dates_do_not_get_the_proximity_bonus() -> None:
    a = _candidate(
        complaint_id=1,
        category_id=1,
        subject="fee refund delayed",
        received_date=date(2026, 1, 1),
        bureau_id=1,
    )
    b = _candidate(
        complaint_id=2,
        category_id=1,
        subject="fee refund delayed",
        received_date=date(2026, 8, 1),
        bureau_id=2,
    )
    result = compute_match(a, b)
    assert result.signals["received_within_window_days"] is False
