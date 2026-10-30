import hashlib
import secrets
from datetime import datetime, timedelta

from app.db.base import utcnow

SESSION_TOKEN_BYTES = 32
CSRF_TOKEN_BYTES = 32


def generate_session_token() -> str:
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(CSRF_TOKEN_BYTES)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def session_expiry(ttl_hours: int) -> datetime:
    return utcnow() + timedelta(hours=ttl_hours)


def csrf_tokens_match(submitted: str | None, expected: str) -> bool:
    if not submitted:
        return False
    return secrets.compare_digest(submitted, expected)
