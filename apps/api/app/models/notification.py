from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, pg_enum, utcnow
from app.models.enums import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, default=None)
    bureau_id: Mapped[int | None] = mapped_column(ForeignKey("bureaus.id"), default=None)
    type: Mapped[NotificationType] = mapped_column(pg_enum(NotificationType, "notification_type"))
    title: Mapped[str] = mapped_column(String(300))
    message: Mapped[str] = mapped_column(String(1000))
    related_complaint_id: Mapped[int | None] = mapped_column(
        ForeignKey("complaints.id"), default=None
    )
    related_overlap_alert_id: Mapped[int | None] = mapped_column(
        ForeignKey("overlap_alerts.id"), default=None
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
