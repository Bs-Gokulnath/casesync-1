from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import require_csrf, require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import (
    BureauAdminOut,
    BureauCreate,
    BureauUpdate,
    CategoryAdminOut,
    CategoryCreate,
    CategoryUpdate,
    RegionAdminOut,
    RegionCreate,
    RegionUpdate,
    SLAPolicyCreate,
    SLAPolicyOut,
    SLAPolicyUpdate,
    UserAdminOut,
    UserCreate,
    UserUpdate,
)
from app.security.permissions import Permission
from app.services import admin_service
from app.services.admin_service import DuplicateUserError

router = APIRouter(prefix="/admin", tags=["admin"])
_admin_only = [Depends(require_permission(Permission.ADMIN_MANAGE))]


@router.get("/bureaus", response_model=list[BureauAdminOut], dependencies=_admin_only)
def list_bureaus(db: Session = Depends(get_db)) -> list:
    return admin_service.list_bureaus(db)


@router.post(
    "/bureaus",
    response_model=BureauAdminOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf)],
)
def create_bureau(
    payload: BureauCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.ADMIN_MANAGE)),
):
    return admin_service.create_bureau(db, payload, actor_id=user.id)


@router.patch(
    "/bureaus/{bureau_id}", response_model=BureauAdminOut, dependencies=[Depends(require_csrf)]
)
def update_bureau(
    bureau_id: int,
    payload: BureauUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.ADMIN_MANAGE)),
):
    updated = admin_service.update_bureau(db, bureau_id, payload, actor_id=user.id)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Bureau not found")
    return updated


@router.get("/regions", response_model=list[RegionAdminOut], dependencies=_admin_only)
def list_regions(db: Session = Depends(get_db)) -> list:
    return admin_service.list_regions(db)


@router.post(
    "/regions",
    response_model=RegionAdminOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf)],
)
def create_region(
    payload: RegionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.ADMIN_MANAGE)),
):
    return admin_service.create_region(db, payload, actor_id=user.id)


@router.patch(
    "/regions/{region_id}", response_model=RegionAdminOut, dependencies=[Depends(require_csrf)]
)
def update_region(
    region_id: int,
    payload: RegionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.ADMIN_MANAGE)),
):
    updated = admin_service.update_region(db, region_id, payload, actor_id=user.id)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Region not found")
    return updated


@router.get("/categories", response_model=list[CategoryAdminOut], dependencies=_admin_only)
def list_categories(db: Session = Depends(get_db)) -> list:
    return admin_service.list_categories(db)


@router.post(
    "/categories",
    response_model=CategoryAdminOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf)],
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.ADMIN_MANAGE)),
):
    return admin_service.create_category(db, payload, actor_id=user.id)


@router.patch(
    "/categories/{category_id}",
    response_model=CategoryAdminOut,
    dependencies=[Depends(require_csrf)],
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.ADMIN_MANAGE)),
):
    updated = admin_service.update_category(db, category_id, payload, actor_id=user.id)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found")
    return updated


@router.get("/sla-policies", response_model=list[SLAPolicyOut], dependencies=_admin_only)
def list_sla_policies(db: Session = Depends(get_db)) -> list:
    return admin_service.list_sla_policies(db)


@router.post(
    "/sla-policies",
    response_model=SLAPolicyOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf)],
)
def create_sla_policy(
    payload: SLAPolicyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.ADMIN_MANAGE)),
):
    return admin_service.create_sla_policy(db, payload, actor_id=user.id)


@router.patch(
    "/sla-policies/{policy_id}", response_model=SLAPolicyOut, dependencies=[Depends(require_csrf)]
)
def update_sla_policy(
    policy_id: int,
    payload: SLAPolicyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.ADMIN_MANAGE)),
):
    updated = admin_service.update_sla_policy(db, policy_id, payload, actor_id=user.id)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="SLA policy not found")
    return updated


@router.get("/users", response_model=list[UserAdminOut], dependencies=_admin_only)
def list_users(db: Session = Depends(get_db)) -> list:
    return admin_service.list_users(db)


@router.post(
    "/users",
    response_model=UserAdminOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf)],
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.ADMIN_MANAGE)),
):
    try:
        return admin_service.create_user(db, payload, actor_id=user.id)
    except DuplicateUserError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch("/users/{user_id}", response_model=UserAdminOut, dependencies=[Depends(require_csrf)])
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.ADMIN_MANAGE)),
):
    updated = admin_service.update_user(db, user_id, payload, actor_id=user.id)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated
