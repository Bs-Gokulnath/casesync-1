from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import OverlapAlertStatus


class OverlapAlertOut(BaseModel):
    id: int
    institution_id: int
    matching_signals: dict[str, Any]
    confidence_score: float
    rationale: str
    status: OverlapAlertStatus
    decided_by: int | None
    decision_reason: str | None
    decided_at: datetime | None
    created_at: datetime
    case_ids: list[int] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class OverlapAlertDetail(OverlapAlertOut):
    pass


class OverlapDecisionRequest(BaseModel):
    status: OverlapAlertStatus
    reason: str = Field(min_length=3, max_length=1000)
