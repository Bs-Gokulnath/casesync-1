from datetime import datetime

from pydantic import BaseModel, Field


class InstitutionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=300)
    aicte_permanent_id: str | None = Field(default=None, max_length=64)
    address: str | None = Field(default=None, max_length=500)
    region_id: int
    contact_email: str | None = None
    contact_phone: str | None = Field(default=None, max_length=32)


class InstitutionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=300)
    aicte_permanent_id: str | None = Field(default=None, max_length=64)
    address: str | None = Field(default=None, max_length=500)
    region_id: int | None = None
    contact_email: str | None = None
    contact_phone: str | None = Field(default=None, max_length=32)


class InstitutionStatusUpdate(BaseModel):
    is_active: bool
    reason: str = Field(min_length=3, max_length=500)


class InstitutionOut(BaseModel):
    id: int
    institution_code: str
    aicte_permanent_id: str | None
    name: str
    address: str | None
    region_id: int
    contact_email: str | None
    contact_phone: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InstitutionDetail(InstitutionOut):
    open_complaint_count: int
    total_complaint_count: int
