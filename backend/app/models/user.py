"""
The `users` table.

`manager_id` is a self-referential foreign key: a User can point to
another User as their manager. This is what lets Phase 4's "team
dashboard" query work later ("show me all requests created by people who
report to me") without a separate org-chart table.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Hashing happens in Phase 3 (core/security.py). This column simply
    # guarantees we NEVER have a plaintext password column to begin with.
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role", validate_strings=True), default=UserRole.EMPLOYEE, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    manager_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    manager: Mapped["User | None"] = relationship("User", remote_side=[id], back_populates="direct_reports")
    direct_reports: Mapped[list["User"]] = relationship("User", back_populates="manager")

    created_requests = relationship(
        "WorkflowRequest", foreign_keys="WorkflowRequest.requester_id", back_populates="requester"
    )
    assigned_requests = relationship(
        "WorkflowRequest", foreign_keys="WorkflowRequest.assignee_id", back_populates="assignee"
    )
    comments = relationship("RequestComment", back_populates="author")
    notifications = relationship("Notification", back_populates="recipient")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email} ({self.role.value})>"
