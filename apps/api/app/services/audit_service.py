from typing import Any

from sqlalchemy.orm import Session as DBSession

from app.models.audit import AuditEvent


def record(
    db: DBSession,
    *,
    actor_id: int | None,
    action: str,
    entity_type: str,
    entity_id: str,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> None:
    """Append one audit row in the caller's transaction. Never updated or deleted afterwards."""
    db.add(
        AuditEvent(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_json=before,
            after_json=after,
            ip_address=ip_address,
        )
    )
