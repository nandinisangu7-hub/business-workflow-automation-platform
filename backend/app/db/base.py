"""
Shared SQLAlchemy declarative base.

Every ORM model (User, WorkflowRequest, AuditLog, ...) created from Phase 2
onward will inherit from this `Base`. Keeping it in its own tiny module
(rather than defining it inside, say, models/user.py) avoids circular
imports: models import Base from here, and Alembic's env.py imports Base
from here too, without needing to import any specific model module first.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
