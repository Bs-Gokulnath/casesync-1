from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, pg_enum, utcnow
from app.models.enums import (
    CaseActionType,
    CaseRelationshipType,
    ComplaintPriority,
    ComplaintSource,
    ComplaintStatus,
)


class Complaint(TimestampMixin, Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_reference: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("complaint_categories.id"))
    subject: Mapped[str] = mapped_column(String(300))
    normalized_subject: Mapped[str] = mapped_column(String(300), index=True)
    description: Mapped[str] = mapped_column(Text)
    source: Mapped[ComplaintSource] = mapped_column(pg_enum(ComplaintSource, "complaint_source"))
    priority: Mapped[ComplaintPriority] = mapped_column(
        pg_enum(ComplaintPriority, "complaint_priority")
    )
    status: Mapped[ComplaintStatus] = mapped_column(
        pg_enum(ComplaintStatus, "complaint_status"), index=True
    )
    bureau_id: Mapped[int] = mapped_column(ForeignKey("bureaus.id"), index=True)
    assigned_officer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), index=True, default=None
    )
    received_date: Mapped[date] = mapped_column(Date)
    expected_disposal_date: Mapped[date | None] = mapped_column(Date, default=None, index=True)
    last_action_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    last_action_note: Mapped[str | None] = mapped_column(Text, default=None)
    next_action_note: Mapped[str | None] = mapped_column(Text, default=None)
    disposal_note: Mapped[str | None] = mapped_column(Text, default=None)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))


class CaseAssignment(Base):
    __tablename__ = "case_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), index=True)
    officer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    bureau_id: Mapped[int] = mapped_column(ForeignKey("bureaus.id"))
    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    unassigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)


class CaseStatusHistory(Base):
    __tablename__ = "case_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), index=True)
    from_status: Mapped[ComplaintStatus | None] = mapped_column(
        pg_enum(ComplaintStatus, "complaint_status"), default=None
    )
    to_status: Mapped[ComplaintStatus] = mapped_column(pg_enum(ComplaintStatus, "complaint_status"))
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CaseActionHistory(Base):
    __tablename__ = "case_action_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), index=True)
    action_type: Mapped[CaseActionType] = mapped_column(pg_enum(CaseActionType, "case_action_type"))
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    from_bureau_id: Mapped[int | None] = mapped_column(ForeignKey("bureaus.id"), default=None)
    to_bureau_id: Mapped[int | None] = mapped_column(ForeignKey("bureaus.id"), default=None)
    reason: Mapped[str | None] = mapped_column(Text, default=None)
    note: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CaseRelationship(Base):
    __tablename__ = "case_relationships"
    __table_args__ = (
        UniqueConstraint("complaint_id", "related_complaint_id", name="uq_case_relationship"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), index=True)
    related_complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), index=True)
    relationship_type: Mapped[CaseRelationshipType] = mapped_column(
        pg_enum(CaseRelationshipType, "case_relationship_type")
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
