from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reference import Bureau, ComplaintCategory, Region, SLAPolicy
from app.models.user import User
from app.schemas.admin import (
    BureauCreate,
    BureauUpdate,
    CategoryCreate,
    CategoryUpdate,
    RegionCreate,
    RegionUpdate,
    SLAPolicyCreate,
    SLAPolicyUpdate,
    UserCreate,
    UserUpdate,
)
from app.security.passwords import hash_password
from app.services import audit_service


def list_bureaus(db: Session) -> list[Bureau]:
    return list(db.scalars(select(Bureau).order_by(Bureau.name)))


def create_bureau(db: Session, payload: BureauCreate, *, actor_id: int) -> Bureau:
    bureau = Bureau(code=payload.code, name=payload.name, description=payload.description)
    db.add(bureau)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="admin.bureau.create",
        entity_type="bureau",
        entity_id=str(bureau.id),
        after={"code": bureau.code, "name": bureau.name},
    )
    db.commit()
    return bureau


def update_bureau(
    db: Session, bureau_id: int, payload: BureauUpdate, *, actor_id: int
) -> Bureau | None:
    bureau = db.get(Bureau, bureau_id)
    if bureau is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(bureau, field, value)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="admin.bureau.update",
        entity_type="bureau",
        entity_id=str(bureau.id),
        after=data,
    )
    db.commit()
    return bureau


def list_regions(db: Session) -> list[Region]:
    return list(db.scalars(select(Region).order_by(Region.name)))


def create_region(db: Session, payload: RegionCreate, *, actor_id: int) -> Region:
    region = Region(code=payload.code, name=payload.name)
    db.add(region)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="admin.region.create",
        entity_type="region",
        entity_id=str(region.id),
        after={"code": region.code, "name": region.name},
    )
    db.commit()
    return region


def update_region(
    db: Session, region_id: int, payload: RegionUpdate, *, actor_id: int
) -> Region | None:
    region = db.get(Region, region_id)
    if region is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(region, field, value)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="admin.region.update",
        entity_type="region",
        entity_id=str(region.id),
        after=data,
    )
    db.commit()
    return region


def list_categories(db: Session) -> list[ComplaintCategory]:
    return list(db.scalars(select(ComplaintCategory).order_by(ComplaintCategory.name)))


def create_category(db: Session, payload: CategoryCreate, *, actor_id: int) -> ComplaintCategory:
    category = ComplaintCategory(
        code=payload.code, name=payload.name, description=payload.description
    )
    db.add(category)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="admin.category.create",
        entity_type="complaint_category",
        entity_id=str(category.id),
        after={"code": category.code, "name": category.name},
    )
    db.commit()
    return category


def update_category(
    db: Session, category_id: int, payload: CategoryUpdate, *, actor_id: int
) -> ComplaintCategory | None:
    category = db.get(ComplaintCategory, category_id)
    if category is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(category, field, value)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="admin.category.update",
        entity_type="complaint_category",
        entity_id=str(category.id),
        after=data,
    )
    db.commit()
    return category


def list_sla_policies(db: Session) -> list[SLAPolicy]:
    return list(db.scalars(select(SLAPolicy).order_by(SLAPolicy.priority)))


def create_sla_policy(db: Session, payload: SLAPolicyCreate, *, actor_id: int) -> SLAPolicy:
    policy = SLAPolicy(
        category_id=payload.category_id,
        priority=payload.priority,
        days_to_resolve=payload.days_to_resolve,
        warning_days_before=payload.warning_days_before,
    )
    db.add(policy)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="admin.sla_policy.create",
        entity_type="sla_policy",
        entity_id=str(policy.id),
        after={"priority": policy.priority.value, "days_to_resolve": policy.days_to_resolve},
    )
    db.commit()
    return policy


def update_sla_policy(
    db: Session, policy_id: int, payload: SLAPolicyUpdate, *, actor_id: int
) -> SLAPolicy | None:
    policy = db.get(SLAPolicy, policy_id)
    if policy is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(policy, field, value)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="admin.sla_policy.update",
        entity_type="sla_policy",
        entity_id=str(policy.id),
        after=data,
    )
    db.commit()
    return policy


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.full_name)))


class DuplicateUserError(Exception):
    pass


def create_user(db: Session, payload: UserCreate, *, actor_id: int) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise DuplicateUserError(f"A user with email {payload.email} already exists")

    user = User(
        employee_code=payload.employee_code,
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        bureau_id=payload.bureau_id,
        region_id=payload.region_id,
        is_active=True,
    )
    db.add(user)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="admin.user.create",
        entity_type="user",
        entity_id=str(user.id),
        after={"email": user.email, "role": user.role.value},
    )
    db.commit()
    return user


def update_user(db: Session, user_id: int, payload: UserUpdate, *, actor_id: int) -> User | None:
    user = db.get(User, user_id)
    if user is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    before = {"role": user.role.value, "is_active": user.is_active}
    for field, value in data.items():
        setattr(user, field, value)
    db.flush()
    audit_service.record(
        db,
        actor_id=actor_id,
        action="admin.user.update",
        entity_type="user",
        entity_id=str(user.id),
        before=before,
        after=data,
    )
    db.commit()
    return user
