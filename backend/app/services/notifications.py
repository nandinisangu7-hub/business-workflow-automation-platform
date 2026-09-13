"""
Notification service — creates in-app notifications for workflow events.

Every public method corresponds to one business event. The service is
called from request_service and workflow_service BEFORE the surrounding
transaction commits, so a notification is always created atomically with
the event that triggered it.

Notification types (used by the frontend for icons/filtering):
  request_created   — sent to managers when a new request arrives
  request_assigned  — sent to the requester when their request is assigned
  request_updated   — sent to the assignee when a pending request is edited
  status_changed    — generic transition notification to the requester
  request_approved  — sent to the requester on approval
  request_rejected  — sent to the requester on rejection
  request_completed — sent to the requester on completion
"""
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.notification import Notification
from app.models.request import WorkflowRequest
from app.models.user import User


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _notify(self, recipient_id: uuid.UUID, type_: str, title: str, message: str) -> Notification:
        n = Notification(recipient_id=recipient_id, type=type_, title=title, message=message)
        self.db.add(n)
        return n

    def _managers_and_admins(self) -> list[User]:
        return list(self.db.scalars(
            select(User).where(User.role.in_([UserRole.MANAGER, UserRole.ADMIN]), User.is_active.is_(True))
        ))

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def on_request_created(self, request: WorkflowRequest) -> None:
        """Notify all managers/admins that a new request needs attention."""
        for recipient in self._managers_and_admins():
            self._notify(
                recipient.id,
                "request_created",
                "New request submitted",
                f"A new request '{request.title}' has been submitted and is awaiting assignment.",
            )

    def on_request_assigned(self, request: WorkflowRequest) -> None:
        """Notify the requester that their request has been assigned."""
        self._notify(
            request.requester_id,
            "request_assigned",
            "Your request has been assigned",
            f"Your request '{request.title}' has been assigned and is now being processed.",
        )

    def on_status_changed(self, request: WorkflowRequest, new_status: str) -> None:
        """Notify the requester of a status change (approved/rejected/completed)."""
        messages = {
            "approved": ("Your request has been approved", f"Your request '{request.title}' has been approved."),
            "rejected": ("Your request has been rejected", f"Your request '{request.title}' has been rejected."),
            "completed": ("Your request has been completed", f"Your request '{request.title}' has been completed."),
            "in_progress": ("Work has started on your request", f"Work has started on your request '{request.title}'."),
        }
        if new_status not in messages:
            return
        title, message = messages[new_status]
        type_map = {
            "approved": "request_approved",
            "rejected": "request_rejected",
            "completed": "request_completed",
            "in_progress": "status_changed",
        }
        self._notify(request.requester_id, type_map[new_status], title, message)

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def list_for_user(self, user_id: uuid.UUID) -> list[Notification]:
        return list(self.db.scalars(
            select(Notification)
            .where(Notification.recipient_id == user_id)
            .order_by(Notification.created_at.desc())
        ))

    def unread_count(self, user_id: uuid.UUID) -> int:
        from sqlalchemy import func
        result = self.db.scalar(
            select(func.count()).select_from(Notification).where(
                Notification.recipient_id == user_id,
                Notification.is_read.is_(False),
            )
        )
        return result or 0

    def mark_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification | None:
        n = self.db.get(Notification, notification_id)
        if n and n.recipient_id == user_id:
            n.is_read = True
            self.db.commit()
            self.db.refresh(n)
        return n

    def mark_all_read(self, user_id: uuid.UUID) -> int:
        notifications = list(self.db.scalars(
            select(Notification).where(
                Notification.recipient_id == user_id,
                Notification.is_read.is_(False),
            )
        ))
        for n in notifications:
            n.is_read = True
        self.db.commit()
        return len(notifications)
