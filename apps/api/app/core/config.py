from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg://casesync:change-me-dev-only@localhost:5432/casesync"

    session_secret: str = "change-me-generate-a-long-random-value"
    session_cookie_name: str = "casesync_session"
    csrf_cookie_name: str = "casesync_csrf"
    session_ttl_hours: int = 12
    cookie_secure: bool = False

    allowed_origins: str = "http://localhost:3000"

    upload_storage_dir: str = "./storage/uploads"
    max_upload_mb: int = 10

    overlap_match_threshold: float = 0.55

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def upload_storage_path(self) -> Path:
        path = Path(self.upload_storage_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
