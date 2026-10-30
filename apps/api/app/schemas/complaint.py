from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import (
    CaseRelationshipType,
    ComplaintPriority,
    ComplaintSource,
    ComplaintStatus,
)


class ComplaintCreate(BaseModel):
    institution_id: int
    category_id: int
    subject: str = Field(min_length=3, max_length=300)
    description: str = Field(min_length=10)
    source: ComplaintSource = ComplaintSource.PORTAL
    priority: ComplaintPriority = ComplaintPriority.MEDIUM
    bureau_id: int | None = None
    received_date: date | None = None
    next_action_note: str | None = None


class ComplaintUpdate(BaseModel):
    subject: str | None = Field(default=None, min_length=3, max_length=300)
    description: str | None = Field(default=None, min_length=10)
    category_id: int | None = None
    priority: ComplaintPriority | None = None
    next_action_note: str | None = None


class ComplaintOut(BaseModel):
    id: int
    case_reference: str
    institution_id: int
    category_id: int
    subject: str
    description: str
    source: ComplaintSource
    priority: ComplaintPriority
    status: ComplaintStatus
    bureau_id: int
    assigned_officer_id: int | None
    received_date: date
    expected_disposal_date: date | None
    last_action_at: datetime | None
    last_action_note: str | None
    next_action_note: str | None
    disposal_note: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RelationshipCreate(BaseModel):
    related_complaint_id: int
    relationship_type: CaseRelationshipType


class RelationshipOut(BaseModel):
    id: int
    complaint_id: int
    related_complaint_id: int
    relationship_type: CaseRelationshipType
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}
