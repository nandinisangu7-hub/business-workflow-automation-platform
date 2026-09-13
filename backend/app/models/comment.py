"""
`request_comments` — free-text discussion thread on a request, used by
both employees and managers during processing (Phase 4/9).
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID


class RequestComment(Base):
    __tablename__ = "request_comments"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("requests.id"), nullable=False, index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request = relationship("WorkflowRequest", back_populates="comments")
    author = relationship("User", back_populates="comments")
