from pydantic import BaseModel, EmailStr, Field

from app.models.enums import ComplaintPriority, UserRole


class BureauCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=2, max_length=200)
    description: str | None = None


class BureauUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class RegionCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=2, max_length=200)


class RegionUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class CategoryCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=2, max_length=200)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class SLAPolicyCreate(BaseModel):
    category_id: int | None = None
    priority: ComplaintPriority
    days_to_resolve: int = Field(gt=0)
    warning_days_before: int = Field(ge=0, default=3)


class SLAPolicyUpdate(BaseModel):
    days_to_resolve: int | None = Field(default=None, gt=0)
    warning_days_before: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class UserCreate(BaseModel):
    employee_code: str = Field(min_length=2, max_length=32)
    full_name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole
    bureau_id: int | None = None
    region_id: int | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    bureau_id: int | None = None
    region_id: int | None = None
    is_active: bool | None = None


class UserAdminOut(BaseModel):
    id: int
    employee_code: str
    full_name: str
    email: str
    role: UserRole
    bureau_id: int | None
    region_id: int | None
    is_active: bool

    model_config = {"from_attributes": True}


class BureauAdminOut(BaseModel):
    id: int
    code: str
    name: str
    description: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class RegionAdminOut(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool

    model_config = {"from_attributes": True}


class CategoryAdminOut(BaseModel):
    id: int
    code: str
    name: str
    description: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class SLAPolicyOut(BaseModel):
    id: int
    category_id: int | None
    priority: ComplaintPriority
    days_to_resolve: int
    warning_days_before: int
    is_active: bool

    model_config = {"from_attributes": True}
