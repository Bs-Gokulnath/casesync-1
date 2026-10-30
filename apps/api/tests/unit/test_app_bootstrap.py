from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def test_settings_load_with_defaults() -> None:
    settings = get_settings()
    assert settings.session_cookie_name == "casesync_session"
    assert settings.allowed_origins_list == ["http://localhost:3000"]


def test_openapi_schema_is_served() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "AICTE CaseWatch API"
