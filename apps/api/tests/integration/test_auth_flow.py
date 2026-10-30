import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.enums import UserRole
from app.models.user import User
from app.security.passwords import hash_password

pytestmark = pytest.mark.integration
settings = get_settings()


def _create_user(db: Session, *, email: str = "officer@aictecasewatch-demo.org") -> User:
    user = User(
        employee_code="EMP-0001",
        full_name="Test Officer",
        email=email,
        password_hash=hash_password("Correct-Horse-1"),
        role=UserRole.BUREAU_OFFICER,
        bureau_id=None,
        region_id=None,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def test_login_sets_cookies_and_me_returns_profile(client: TestClient, db: Session) -> None:
    _create_user(db)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "officer@aictecasewatch-demo.org", "password": "Correct-Horse-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "officer@aictecasewatch-demo.org"
    assert "complaint:create" in body["permissions"]
    assert settings.session_cookie_name in response.cookies
    assert settings.csrf_cookie_name in response.cookies

    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "officer@aictecasewatch-demo.org"


def test_login_rejects_wrong_password(client: TestClient, db: Session) -> None:
    _create_user(db, email="officer2@aictecasewatch-demo.org")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "officer2@aictecasewatch-demo.org", "password": "wrong"},
    )
    assert response.status_code == 401


def test_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_logout_requires_csrf_header(client: TestClient, db: Session) -> None:
    _create_user(db, email="officer3@aictecasewatch-demo.org")
    client.post(
        "/api/v1/auth/login",
        json={"email": "officer3@aictecasewatch-demo.org", "password": "Correct-Horse-1"},
    )

    no_csrf_response = client.post("/api/v1/auth/logout")
    assert no_csrf_response.status_code == 403

    csrf_token = client.cookies.get(settings.csrf_cookie_name)
    ok_response = client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf_token or ""})
    assert ok_response.status_code == 200

    after_logout = client.get("/api/v1/auth/me")
    assert after_logout.status_code == 401
