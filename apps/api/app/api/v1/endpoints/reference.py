from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.reference import Bureau, ComplaintCategory, Region
from app.models.user import User
from app.schemas.reference import BureauOut, ComplaintCategoryOut, OfficerOut, RegionOut
from app.security.permissions import Permission

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/bureaus", response_model=list[BureauOut], dependencies=[Depends(get_current_user)])
def list_bureaus(db: Session = Depends(get_db)) -> list[Bureau]:
    return list(db.scalars(select(Bureau).where(Bureau.is_active.is_(True)).order_by(Bureau.name)))


@router.get("/regions", response_model=list[RegionOut], dependencies=[Depends(get_current_user)])
def list_regions(db: Session = Depends(get_db)) -> list[Region]:
    return list(db.scalars(select(Region).where(Region.is_active.is_(True)).order_by(Region.name)))


@router.get(
    "/categories",
    response_model=list[ComplaintCategoryOut],
    dependencies=[Depends(get_current_user)],
)
def list_categories(db: Session = Depends(get_db)) -> list[ComplaintCategory]:
    return list(
        db.scalars(
            select(ComplaintCategory)
            .where(ComplaintCategory.is_active.is_(True))
            .order_by(ComplaintCategory.name)
        )
    )


@router.get("/officers", response_model=list[OfficerOut])
def list_officers(
    bureau_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.COMPLAINT_ASSIGN)),
) -> list[User]:
    return list(
        db.scalars(
            select(User)
            .where(
                User.bureau_id == bureau_id,
                User.role == UserRole.BUREAU_OFFICER,
                User.is_active.is_(True),
            )
            .order_by(User.full_name)
        )
    )
