from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session as DBSession

from app.api.v1.deps import client_ip, get_current_session, require_csrf
from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import Session as UserSession
from app.models.user import User
from app.schemas.auth import LoginRequest, UserProfile
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _set_auth_cookies(response: Response, *, session_token: str, csrf_token: str) -> None:
    max_age = settings.session_ttl_hours * 3600
    response.set_cookie(
        settings.session_cookie_name,
        session_token,
        max_age=max_age,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        max_age=max_age,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.session_cookie_name, path="/")
    response.delete_cookie(settings.csrf_cookie_name, path="/")


@router.post("/login", response_model=UserProfile)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: DBSession = Depends(get_db),
) -> UserProfile:
    user = auth_service.authenticate(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    result = auth_service.login(
        db,
        user=user,
        ttl_hours=settings.session_ttl_hours,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    _set_auth_cookies(response, session_token=result.session_token, csrf_token=result.csrf_token)
    return UserProfile(
        id=user.id,
        employee_code=user.employee_code,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        bureau_id=user.bureau_id,
        region_id=user.region_id,
        permissions=auth_service.permissions_for(user),
    )


@router.post("/logout", dependencies=[Depends(require_csrf)])
def logout(
    request: Request,
    response: Response,
    db: DBSession = Depends(get_db),
    session_pair: tuple[User, UserSession] = Depends(get_current_session),
) -> dict:
    user, _ = session_pair
    raw_token = request.cookies[settings.session_cookie_name]
    auth_service.logout(db, raw_token=raw_token, actor_id=user.id, ip_address=client_ip(request))
    _clear_auth_cookies(response)
    return {"status": "ok"}


@router.get("/me", response_model=UserProfile)
def me(session_pair: tuple[User, UserSession] = Depends(get_current_session)) -> UserProfile:
    user, _ = session_pair
    return UserProfile(
        id=user.id,
        employee_code=user.employee_code,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        bureau_id=user.bureau_id,
        region_id=user.region_id,
        permissions=auth_service.permissions_for(user),
    )
