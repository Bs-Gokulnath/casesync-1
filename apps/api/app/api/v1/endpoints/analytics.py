from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary
from app.security.permissions import Permission
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(
    date_from: date | None = None,
    date_to: date | None = None,
    bureau_id: int | None = None,
    region_id: int | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.ANALYTICS_READ)),
) -> AnalyticsSummary:
    return analytics_service.get_summary(
        db,
        date_from=date_from,
        date_to=date_to,
        bureau_id=bureau_id,
        region_id=region_id,
        category_id=category_id,
    )


@router.get("/export.csv")
def export_csv(
    date_from: date | None = None,
    date_to: date | None = None,
    bureau_id: int | None = None,
    region_id: int | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.ANALYTICS_EXPORT)),
) -> Response:
    csv_content = analytics_service.export_complaints_csv(
        db,
        date_from=date_from,
        date_to=date_to,
        bureau_id=bureau_id,
        region_id=region_id,
        category_id=category_id,
    )
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=complaints-export.csv"},
    )
