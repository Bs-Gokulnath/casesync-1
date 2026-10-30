import enum
from datetime import UTC, datetime
from typing import TypeVar

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

E = TypeVar("E", bound=enum.Enum)


def utcnow() -> datetime:
    return datetime.now(UTC)


def pg_enum(enum_cls: type[E], name: str) -> SAEnum:
    """A Postgres ENUM column type backed by a str Enum's values, not member names."""
    return SAEnum(enum_cls, name=name, values_callable=lambda e: [m.value for m in e])


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
