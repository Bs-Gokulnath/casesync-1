from sqlalchemy import select

from app.models.reference import Region
from app.repositories.pagination import select_count


def test_select_count_preserves_the_from_clause() -> None:
    """Regression test: `stmt.with_only_columns(func.count())` silently drops
    the FROM clause (func.count() carries no column reference for
    SQLAlchemy to infer it from), making every paginated list report
    total=1 regardless of actual row count. select_count must not do that.
    """
    stmt = select(Region).where(Region.is_active.is_(True))
    count_stmt = select_count(stmt)
    compiled = str(count_stmt)
    assert "FROM" in compiled.upper()
    assert "regions" in compiled.lower()
