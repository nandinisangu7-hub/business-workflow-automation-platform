import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditService:
    """Append-only audit writer; callers own the surrounding transaction."""

    def __init__(self, db: Session):
        self.db = db

    def record(self, *, actor_id: uuid.UUID | None, action: str, entity_type: str, entity_id: uuid.UUID | str, previous: dict[str, Any] | None = None, new: dict[str, Any] | None = None, details: dict[str, Any] | None = None) -> AuditLog:
        entry = AuditLog(user_id=actor_id, action=action, entity_type=entity_type, entity_id=str(entity_id), previous_value=previous, new_value=new, details=details)
        self.db.add(entry)
        return entry

    def list(
        self,
        *,
        entity_type: str | None = None,
        entity_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AuditLog], int]:
        from sqlalchemy import func
        statement = select(AuditLog).order_by(AuditLog.created_at.desc())
        if entity_type:
            statement = statement.where(AuditLog.entity_type == entity_type)
        if entity_id:
            statement = statement.where(AuditLog.entity_id == entity_id)
        total = self.db.scalar(select(func.count()).select_from(statement.subquery())) or 0
        items = list(self.db.scalars(statement.offset(offset).limit(limit)))
        return items, total
