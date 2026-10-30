from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.user import User


def get_by_email(db: DBSession, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_by_id(db: DBSession, user_id: int) -> User | None:
    return db.get(User, user_id)
