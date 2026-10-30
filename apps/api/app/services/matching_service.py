"""Deterministic, explainable signals for cross-bureau overlap detection.

Every signal is a simple, auditable rule — no opaque model, no external AI
call. Scores are a weighted sum of signals that fired, always returned
alongside a human-readable rationale so a reviewer can see exactly why two
cases were flagged, per the brief's "recommended human review" requirement.
"""

from dataclasses import dataclass, field
from datetime import date

SAME_CATEGORY_WEIGHT = 0.30
SUBJECT_SIMILARITY_WEIGHT = 0.50
DATE_PROXIMITY_WEIGHT = 0.20
DATE_PROXIMITY_WINDOW_DAYS = 30


@dataclass(frozen=True)
class MatchCandidate:
    complaint_id: int
    category_id: int
    normalized_subject: str
    received_date: date
    bureau_id: int


@dataclass(frozen=True)
class MatchResult:
    score: float
    signals: dict[str, bool | float] = field(default_factory=dict)
    rationale: str = ""


def _jaccard(a: str, b: str) -> float:
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def compute_match(a: MatchCandidate, b: MatchCandidate) -> MatchResult:
    if a.bureau_id == b.bureau_id:
        return MatchResult(score=0.0, signals={"same_bureau": True}, rationale="Same bureau")

    same_category = a.category_id == b.category_id
    similarity = _jaccard(a.normalized_subject, b.normalized_subject)
    date_gap_days = abs((a.received_date - b.received_date).days)
    date_close = date_gap_days <= DATE_PROXIMITY_WINDOW_DAYS

    score = 0.0
    reasons = ["same institution"]
    if same_category:
        score += SAME_CATEGORY_WEIGHT
        reasons.append("same category")
    if similarity > 0:
        score += SUBJECT_SIMILARITY_WEIGHT * similarity
        if similarity >= 0.5:
            reasons.append(f"similar complaint text ({similarity:.0%} word overlap)")
    if date_close:
        score += DATE_PROXIMITY_WEIGHT
        reasons.append(f"received within {DATE_PROXIMITY_WINDOW_DAYS} days of each other")

    rationale = "; ".join(reasons).capitalize() + "."
    return MatchResult(
        score=round(score, 3),
        signals={
            "same_institution": True,
            "same_category": same_category,
            "subject_similarity": round(similarity, 3),
            "received_within_window_days": date_close,
            "date_gap_days": date_gap_days,
        },
        rationale=rationale,
    )
