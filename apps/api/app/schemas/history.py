from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.models.enums import CaseActionType, ComplaintStatus


class StatusHistoryEntry(BaseModel):
    kind: Literal["status_change"] = "status_change"
    from_status: ComplaintStatus | None
    to_status: ComplaintStatus
    actor_id: int
    actor_name: str
    reason: str | None
    created_at: datetime


class ActionHistoryEntry(BaseModel):
    kind: Literal["action"] = "action"
    action_type: CaseActionType
    actor_id: int
    actor_name: str
    from_bureau_id: int | None
    to_bureau_id: int | None
    reason: str | None
    note: str | None
    created_at: datetime


TimelineEntry = StatusHistoryEntry | ActionHistoryEntry
