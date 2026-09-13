"""
`audit_logs` — the append-only system-of-record for "who did what, when."

DESIGN NOTE — why `entity_id` is a plain string, not a foreign key:
Audit logs need to outlive the things they describe. If a user is later
deleted (or a request is purged after a long retention period), a real
foreign key would either block that deletion or cascade-delete the audit
trail that was supposed to survive it — the opposite of what audit logs
are for. Storing `entity_id` as a string (the UUID's text form) keeps the
audit table independent of the lifecycle of everything else, at the cost
of the database no longer being able to enforce that the ID refers to a
row that still exists. That's a deliberate trade-off for this table only.

`previous_value` / `new_value` are JSON so the same table can describe a
status change (`{"status": "pending"}` → `{"status": "assigned"}`), a role
change, or any other kind of event, without a different column per action
type. No route or service is ever permitted to UPDATE or DELETE a row
here — only INSERT and SELECT (enforced in the service layer in Phase 6,
since the database itself doesn't have a clean way to forbid UPDATE at
the row level without triggers, which would be overkill here).
"""
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        # Admin audit views filter by "what happened to this exact
        # entity" (e.g. one request's full history) very frequently.
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    # Nullable: a small number of actions (e.g. a failed login for an
    # email that doesn't exist) have no authenticated user to attribute.
    user_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    previous_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # 45 = max IPv6 text length
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User")
