"""
Importing every model module here (even though nothing below uses the
names directly) is what makes `Base.metadata` aware of every table.

Both Alembic's autogenerate and `Base.metadata.create_all()` (used in
tests) walk `Base.metadata.tables`, which is only populated for a model
class once its module has actually been imported and the class body has
executed. If a model existed but was never imported anywhere, Alembic
would silently produce a migration that DROPS its table (because it looks
missing) even though the model file is right there. This file exists
specifically to prevent that class of bug.
"""
from app.models.audit_log import AuditLog
from app.models.assignment import RequestAssignment
from app.models.category import RequestCategory
from app.models.comment import RequestComment
from app.models.notification import Notification
from app.models.request import WorkflowRequest
from app.models.status_history import RequestStatusHistory
from app.models.user import User

__all__ = [
    "AuditLog",
    "RequestAssignment",
    "RequestCategory",
    "RequestComment",
    "Notification",
    "WorkflowRequest",
    "RequestStatusHistory",
    "User",
]
