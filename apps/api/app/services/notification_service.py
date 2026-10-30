from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.enums import NotificationType
from app.models.notification import Notification
from app.models.user import User
from app.repositories.pagination import paginate
from app.schemas.common import Page
from app.schemas.notification import NotificationOut


def notify_user(
    db: Session,
    *,
    user_id: int,
    type_: NotificationType,
    title: str,
    message: str,
    related_complaint_id: int | None = None,
    related_overlap_alert_id: int | None = None,
) -> None:
    db.add(
        Notification(
            user_id=user_id,
            bureau_id=None,
            type=type_,
            title=title,
            message=message,
            related_complaint_id=related_complaint_id,
            related_overlap_alert_id=related_overlap_alert_id,
        )
    )


def notify_bureau(
    db: Session,
    *,
    bureau_id: int,
    type_: NotificationType,
    title: str,
    message: str,
    related_complaint_id: int | None = None,
    related_overlap_alert_id: int | None = None,
) -> None:
    db.add(
        Notification(
            user_id=None,
            bureau_id=bureau_id,
            type=type_,
            title=title,
            message=message,
            related_complaint_id=related_complaint_id,
            related_overlap_alert_id=related_overlap_alert_id,
        )
    )


def list_for_user(
    db: Session, user: User, *, unread_only: bool, page: int, page_size: int
) -> Page[NotificationOut]:
    conditions = [Notification.user_id == user.id]
    if user.bureau_id is not None:
        conditions.append(Notification.bureau_id == user.bureau_id)

    stmt = select(Notification).where(or_(*conditions)).order_by(Notification.created_at.desc())
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    return paginate(db, stmt, page=page, page_size=page_size, mapper=NotificationOut.model_validate)


def mark_read(db: Session, notification_id: int) -> bool:
    notification = db.get(Notification, notification_id)
    if notification is None:
        return False
    notification.is_read = True
    db.commit()
    return True


def mark_all_read(db: Session, user: User) -> int:
    conditions = [Notification.user_id == user.id]
    if user.bureau_id is not None:
        conditions.append(Notification.bureau_id == user.bureau_id)

    rows = db.scalars(
        select(Notification).where(or_(*conditions), Notification.is_read.is_(False))
    ).all()
    for row in rows:
        row.is_read = True
    db.commit()
    return len(rows)
