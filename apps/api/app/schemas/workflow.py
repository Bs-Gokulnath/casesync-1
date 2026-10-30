from pydantic import BaseModel, Field

from app.models.enums import ComplaintStatus


class TransitionRequest(BaseModel):
    to_status: ComplaintStatus
    reason: str | None = Field(default=None, max_length=1000)


class TransferRequest(BaseModel):
    to_bureau_id: int
    reason: str = Field(min_length=3, max_length=1000)


class EscalateRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)


class DisposeRequest(BaseModel):
    disposal_note: str = Field(min_length=3, max_length=2000)


class ReopenRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)


class AssignRequest(BaseModel):
    officer_id: int
