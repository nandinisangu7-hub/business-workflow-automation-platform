"""
`requests` — the central table of the whole platform.

DESIGN NOTE — why `assignee_id` lives here AND there's a separate
`request_assignments` table:
`assignee_id` is a denormalized "current assignee" pointer, kept on the
request itself so that "show me all requests assigned to me" is a single
indexed WHERE clause, not a subquery into a history table. The
`request_assignments` table (models/assignment.py) is the full append-only
history of every assignment/reassignment event. This is the same pattern
used for status: `status` is the current value, `request_status_history`
is the full timeline. Denormalize the "current" value for read speed,
keep a normalized history table for auditability — a genuinely useful
interview talking point about a real trade-off (write complexity vs.
read simplicity), not just an arbitrary choice.

`status` itself is deliberately NOT validated for legal transitions at the
model layer — that enforcement is Phase 5's job, in the service layer,
where it can return a meaningful 409 Conflict with an explanation instead
of a bare database constraint violation.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID
from app.models.enums import RequestPriority, RequestStatus


class WorkflowRequest(Base):
    __tablename__ = "requests"
    __table_args__ = (
        # Composite index: the request list page filters by status AND
        # priority together far more often than either alone (Phase 4/10).
        Index("ix_requests_status_priority", "status", "priority"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("request_categories.id"), nullable=True
    )
    requester_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=True, index=True
    )

    priority: Mapped[RequestPriority] = mapped_column(
        Enum(RequestPriority, name="request_priority", validate_strings=True), default=RequestPriority.MEDIUM, nullable=False
    )
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, name="request_status", validate_strings=True), default=RequestStatus.PENDING, nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    category = relationship("RequestCategory", back_populates="requests")
    requester = relationship("User", foreign_keys=[requester_id], back_populates="created_requests")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_requests")

    assignments = relationship(
        "RequestAssignment", back_populates="request", order_by="RequestAssignment.assigned_at"
    )
    comments = relationship(
        "RequestComment", back_populates="request", order_by="RequestComment.created_at"
    )
    status_history = relationship(
        "RequestStatusHistory", back_populates="request", order_by="RequestStatusHistory.changed_at"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<WorkflowRequest {self.title!r} [{self.status.value}]>"
