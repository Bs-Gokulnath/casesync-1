from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.institution import Institution, InstitutionAlias


def get_by_id(db: Session, institution_id: int) -> Institution | None:
    return db.get(Institution, institution_id)


def get_by_code(db: Session, institution_code: str) -> Institution | None:
    return db.scalar(select(Institution).where(Institution.institution_code == institution_code))


def get_by_aicte_id(db: Session, aicte_permanent_id: str) -> Institution | None:
    return db.scalar(
        select(Institution).where(Institution.aicte_permanent_id == aicte_permanent_id)
    )


def search_statement(
    *,
    q: str | None = None,
    region_id: int | None = None,
    is_active: bool | None = None,
):
    stmt = select(Institution).order_by(Institution.name)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(Institution.normalized_name.ilike(like))
    if region_id is not None:
        stmt = stmt.where(Institution.region_id == region_id)
    if is_active is not None:
        stmt = stmt.where(Institution.is_active == is_active)
    return stmt


def next_institution_code(db: Session) -> str:
    max_id = db.scalar(select(func.max(Institution.id))) or 0
    return f"INST-{max_id + 1:04d}"


def create(db: Session, institution: Institution) -> Institution:
    db.add(institution)
    db.flush()
    return institution


def add_alias(db: Session, alias: InstitutionAlias) -> InstitutionAlias:
    db.add(alias)
    db.flush()
    return alias


def list_aliases(db: Session, institution_id: int) -> list[InstitutionAlias]:
    return list(
        db.scalars(
            select(InstitutionAlias).where(InstitutionAlias.institution_id == institution_id)
        )
    )
