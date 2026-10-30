from dataclasses import dataclass

from sqlalchemy.orm import Session as DBSession

from app.db.base import utcnow
from app.models.user import Session as UserSession
from app.models.user import User
from app.repositories import session_repository, user_repository
from app.security.passwords import verify_password
from app.security.permissions import ROLE_PERMISSIONS
from app.security.sessions import (
    generate_csrf_token,
    generate_session_token,
    hash_token,
    session_expiry,
)
from app.services import audit_service


@dataclass(frozen=True)
class LoginResult:
    user: User
    session_token: str
    csrf_token: str
    expires_at_ts: float


def authenticate(db: DBSession, email: str, password: str) -> User | None:
    user = user_repository.get_by_email(db, email)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def login(
    db: DBSession,
    *,
    user: User,
    ttl_hours: int,
    user_agent: str | None,
    ip_address: str | None,
) -> LoginResult:
    raw_token = generate_session_token()
    csrf_token = generate_csrf_token()
    now = utcnow()
    expires_at = session_expiry(ttl_hours)

    session_repository.create(
        db,
        user_id=user.id,
        token_hash=hash_token(raw_token),
        csrf_token=csrf_token,
        expires_at=expires_at,
        now=now,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    audit_service.record(
        db,
        actor_id=user.id,
        action="auth.login",
        entity_type="user",
        entity_id=str(user.id),
        ip_address=ip_address,
    )
    db.commit()
    return LoginResult(
        user=user,
        session_token=raw_token,
        csrf_token=csrf_token,
        expires_at_ts=expires_at.timestamp(),
    )


def logout(db: DBSession, *, raw_token: str, actor_id: int, ip_address: str | None) -> None:
    session_repository.delete_by_token_hash(db, hash_token(raw_token))
    audit_service.record(
        db,
        actor_id=actor_id,
        action="auth.logout",
        entity_type="user",
        entity_id=str(actor_id),
        ip_address=ip_address,
    )
    db.commit()


def resolve_session(db: DBSession, raw_token: str) -> tuple[User, UserSession] | None:
    session = session_repository.get_by_token_hash(db, hash_token(raw_token))
    if session is None:
        return None
    if session.expires_at <= utcnow():
        return None
    user = user_repository.get_by_id(db, session.user_id)
    if user is None or not user.is_active:
        return None
    session_repository.touch(db, session, utcnow())
    db.commit()
    return user, session


def permissions_for(user: User) -> list[str]:
    return sorted(p.value for p in ROLE_PERMISSIONS.get(user.role, frozenset()))
