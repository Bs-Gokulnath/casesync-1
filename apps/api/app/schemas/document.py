from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    complaint_id: int
    file_name: str
    content_type: str
    size_bytes: int
    uploaded_by: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}
