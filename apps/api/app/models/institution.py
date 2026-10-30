from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Institution(TimestampMixin, Base):
    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(primary_key=True)
    institution_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    aicte_permanent_id: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True, default=None
    )
    name: Mapped[str] = mapped_column(String(300))
    normalized_name: Mapped[str] = mapped_column(String(300), index=True)
    address: Mapped[str | None] = mapped_column(String(500), default=None)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"))
    contact_email: Mapped[str | None] = mapped_column(String(255), default=None)
    contact_phone: Mapped[str | None] = mapped_column(String(32), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class InstitutionAlias(Base):
    __tablename__ = "institution_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), index=True)
    alias_name: Mapped[str] = mapped_column(String(300))
    normalized_alias: Mapped[str] = mapped_column(String(300), index=True)
