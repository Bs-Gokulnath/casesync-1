from collections.abc import Generator
from urllib.parse import urlsplit, urlunsplit

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.session import get_db
from app.main import app
from app.models import Base

settings = get_settings()


def _test_database_url() -> str:
    """The dev database name with a `_test` suffix, isolated from seeded demo data."""
    parts = urlsplit(settings.database_url)
    test_path = parts.path.rstrip("/") + "_test"
    return urlunsplit((parts.scheme, parts.netloc, test_path, parts.query, parts.fragment))


def _ensure_database_exists(url: str) -> None:
    parts = urlsplit(url)
    dbname = parts.path.lstrip("/")
    admin_url = urlunsplit((parts.scheme, parts.netloc, "/postgres", parts.query, parts.fragment))

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", future=True)
    try:
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": dbname}
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{dbname}"'))
    finally:
        admin_engine.dispose()


@pytest.fixture(scope="session")
def db_engine():
    test_url = _test_database_url()
    _ensure_database_exists(test_url)
    engine = create_engine(test_url, future=True)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db(db_engine) -> Generator[Session]:
    """A session bound to a single connection/transaction, rolled back after each test."""
    connection = db_engine.connect()
    outer_transaction = connection.begin()
    session_factory = sessionmaker(
        bind=connection, join_transaction_mode="create_savepoint", future=True
    )
    session = session_factory()

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient]:
    def _get_db_override() -> Generator[Session]:
        yield db

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def login_as(client: TestClient):
    def _login(email: str, password: str) -> str:
        response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert response.status_code == 200, response.text
        return client.cookies.get(settings.csrf_cookie_name) or ""

    return _login
