from collections.abc import Callable
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.schemas.common import Page


def select_count(stmt: Select) -> Select:
    """A COUNT(*) over the statement's own result set, FROM/JOINs/WHERE intact.

    `stmt.with_only_columns(func.count())` looks equivalent but silently
    drops the FROM clause whenever the replaced columns carry no column
    reference (which a bare `func.count()` never does), so the query
    becomes `SELECT count(*)` with no FROM — a constant 1, regardless of
    how many rows actually match. Wrapping the original statement as a
    subquery keeps every join/filter and counts its rows correctly.
    """
    return select(func.count()).select_from(stmt.order_by(None).subquery())


def paginate(
    db: Session,
    stmt: Select,
    *,
    page: int,
    page_size: int,
    mapper: Callable[[Any], Any],
) -> Page:
    total = db.scalar(select_count(stmt)) or 0
    rows = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    items = [mapper(row) for row in rows]
    return Page(items=items, total=total, page=page, page_size=page_size)
