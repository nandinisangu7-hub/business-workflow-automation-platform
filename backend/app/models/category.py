"""
`request_categories` — a small lookup table (IT Equipment, Software
Access, Leave, Expense Reimbursement, Purchase Request, General Service).

Unlike UserRole, this genuinely IS a table rather than an enum: admins can
manage categories at runtime (add/rename/retire one) per the spec's admin
capabilities, so the set of values is not fixed at code-deploy time the
way roles are.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID


class RequestCategory(Base):
    __tablename__ = "request_categories"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    requests = relationship("WorkflowRequest", back_populates="category")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RequestCategory {self.name}>"
