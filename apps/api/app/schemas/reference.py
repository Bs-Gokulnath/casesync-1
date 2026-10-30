from pydantic import BaseModel


class BureauOut(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool

    model_config = {"from_attributes": True}


class RegionOut(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool

    model_config = {"from_attributes": True}


class ComplaintCategoryOut(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool

    model_config = {"from_attributes": True}


class OfficerOut(BaseModel):
    id: int
    employee_code: str
    full_name: str
    bureau_id: int | None

    model_config = {"from_attributes": True}
