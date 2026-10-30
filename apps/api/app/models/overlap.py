from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, pg_enum
from app.models.enums import OverlapAlertStatus


class OverlapAlert(TimestampMixin, Base):
    __tablename__ = "overlap_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), index=True)
    matching_signals: Mapped[dict] = mapped_column(JSONB)
    confidence_score: Mapped[float] = mapped_column(Numeric(4, 3))
    rationale: Mapped[str] = mapped_column(Text)
    status: Mapped[OverlapAlertStatus] = mapped_column(
        pg_enum(OverlapAlertStatus, "overlap_alert_status"), index=True
    )
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), default=None)
    decision_reason: Mapped[str | None] = mapped_column(Text, default=None)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)


class OverlapAlertCase(Base):
    __tablename__ = "overlap_alert_cases"
    __table_args__ = (
        UniqueConstraint("overlap_alert_id", "complaint_id", name="uq_overlap_alert_case"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    overlap_alert_id: Mapped[int] = mapped_column(ForeignKey("overlap_alerts.id"), index=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), index=True)
