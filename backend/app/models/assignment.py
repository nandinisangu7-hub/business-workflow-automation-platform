"""
`request_assignments` — append-only history of every assignment event.

Recorded every time a manager/admin assigns or reassigns a request (Phase
5 will be the only code path that ever inserts here). Never updated or
deleted, which is what "audit trail" means in practice: you can always
answer "who assigned this to whom, and who made that call?" for any point
in the request's life, not just the current state.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID


class RequestAssignment(Base):
    __tablename__ = "request_assignments"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("requests.id"), nullable=False, index=True)
    assignee_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    assigned_by_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request = relationship("WorkflowRequest", back_populates="assignments")
    assignee = relationship("User", foreign_keys=[assignee_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
