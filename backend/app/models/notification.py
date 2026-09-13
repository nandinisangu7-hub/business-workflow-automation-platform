"""
`notifications` — in-app notifications (Phase 7 will define the service
that creates these; this is just the storage shape).

`type` is a plain string rather than an enum: notification types are an
internal categorization ("request_assigned", "request_approved", ...) used
mostly for icon/filtering in the UI, and new types will likely be added
as the platform grows without needing a schema migration each time —
unlike UserRole, getting this wrong has no security implication.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        # The most common query is "give me this user's unread
        # notifications" — index the pair, not just recipient_id alone.
        Index("ix_notifications_recipient_unread", "recipient_id", "is_read"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    recipient_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recipient = relationship("User", back_populates="notifications")
