from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session as DBSession

from app.models.user import Session as UserSession


def create(
    db: DBSession,
    *,
    user_id: int,
    token_hash: str,
    csrf_token: str,
    expires_at: datetime,
    now: datetime,
    user_agent: str | None,
    ip_address: str | None,
) -> UserSession:
    session = UserSession(
        user_id=user_id,
        token_hash=token_hash,
        csrf_token=csrf_token,
        expires_at=expires_at,
        last_seen_at=now,
        created_at=now,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    db.add(session)
    db.flush()
    return session


def get_by_token_hash(db: DBSession, token_hash: str) -> UserSession | None:
    return db.scalar(select(UserSession).where(UserSession.token_hash == token_hash))


def delete_by_token_hash(db: DBSession, token_hash: str) -> None:
    db.execute(delete(UserSession).where(UserSession.token_hash == token_hash))


def touch(db: DBSession, session: UserSession, now: datetime) -> None:
    session.last_seen_at = now
