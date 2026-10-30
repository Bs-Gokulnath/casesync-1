from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DBSession

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import Session as UserSession
from app.models.user import User
from app.security.permissions import Permission, role_has_permission
from app.security.sessions import csrf_tokens_match
from app.services import auth_service

settings = get_settings()


def get_current_session(
    request: Request, db: DBSession = Depends(get_db)
) -> tuple[User, UserSession]:
    raw_token = request.cookies.get(settings.session_cookie_name)
    if not raw_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    resolved = auth_service.resolve_session(db, raw_token)
    if resolved is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
    return resolved


def get_current_user(
    session_pair: tuple[User, UserSession] = Depends(get_current_session),
) -> User:
    return session_pair[0]


def require_csrf(
    request: Request,
    session_pair: tuple[User, UserSession] = Depends(get_current_session),
) -> None:
    _, session = session_pair
    submitted = request.headers.get("X-CSRF-Token")
    if not csrf_tokens_match(submitted, session.csrf_token):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Invalid or missing CSRF token")


def require_permission(permission: Permission) -> Callable[[User], User]:
    def checker(user: User = Depends(get_current_user)) -> User:
        if not role_has_permission(user.role, permission):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return checker


def client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None
