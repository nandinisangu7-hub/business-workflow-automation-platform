"""
`request_status_history` — append-only record of every status change.

`from_status` is nullable because the very first row for a request (its
creation, PENDING) has no "previous" status. Phase 5's workflow service
will be the only writer here, inserting exactly one row per accepted
transition — this table IS the workflow timeline shown on the request
detail page (Phase 9/20).
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID
from app.models.enums import RequestStatus


class RequestStatusHistory(Base):
    __tablename__ = "request_status_history"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("requests.id"), nullable=False, index=True)
    from_status: Mapped[RequestStatus | None] = mapped_column(
        Enum(RequestStatus, name="request_status", validate_strings=True), nullable=True
    )
    to_status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus, name="request_status", validate_strings=True), nullable=False)
    changed_by_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request = relationship("WorkflowRequest", back_populates="status_history")
    changed_by = relationship("User")
