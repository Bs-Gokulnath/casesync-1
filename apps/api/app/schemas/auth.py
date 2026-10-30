from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: int
    employee_code: str
    full_name: str
    email: str
    role: UserRole
    bureau_id: int | None
    region_id: int | None
    permissions: list[str]

    model_config = {"from_attributes": True}
