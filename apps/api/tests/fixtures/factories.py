from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.institution import Institution
from app.models.reference import Bureau, ComplaintCategory, Region, SLAPolicy
from app.models.user import User
from app.security.passwords import hash_password


def make_region(db: Session, code: str = "NR", name: str = "Northern Region") -> Region:
    region = Region(code=code, name=name, is_active=True)
    db.add(region)
    db.flush()
    return region


def make_bureau(db: Session, code: str = "RB-DEL", name: str = "Regional Bureau - Delhi") -> Bureau:
    bureau = Bureau(code=code, name=name, is_active=True)
    db.add(bureau)
    db.flush()
    return bureau


def make_category(db: Session, code: str = "FEE", name: str = "Fee Refund") -> ComplaintCategory:
    category = ComplaintCategory(code=code, name=name, is_active=True)
    db.add(category)
    db.flush()
    return category


def make_sla_policy(
    db: Session, *, priority, days_to_resolve: int = 15, category_id: int | None = None
) -> SLAPolicy:
    policy = SLAPolicy(
        category_id=category_id,
        priority=priority,
        days_to_resolve=days_to_resolve,
        warning_days_before=3,
        is_active=True,
    )
    db.add(policy)
    db.flush()
    return policy


def make_institution(
    db: Session, *, region_id: int, name: str = "Delta Institute of Technology"
) -> Institution:
    institution = Institution(
        institution_code=f"INST-{name[:4].upper()}",
        name=name,
        normalized_name=name.lower(),
        region_id=region_id,
        is_active=True,
    )
    db.add(institution)
    db.flush()
    return institution


def make_user(
    db: Session,
    *,
    email: str = "user@aictecasewatch-demo.org",
    role: UserRole = UserRole.BUREAU_OFFICER,
    bureau_id: int | None = None,
    region_id: int | None = None,
    password: str = "Correct-Horse-1",
) -> User:
    user = User(
        employee_code=f"EMP-{email.split('@')[0].upper()}",
        full_name="Test User",
        email=email,
        password_hash=hash_password(password),
        role=role,
        bureau_id=bureau_id,
        region_id=region_id,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user
