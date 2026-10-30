from datetime import datetime

from pydantic import BaseModel

from app.models.enums import NotificationType


class NotificationOut(BaseModel):
    id: int
    user_id: int | None
    bureau_id: int | None
    type: NotificationType
    title: str
    message: str
    related_complaint_id: int | None
    related_overlap_alert_id: int | None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
