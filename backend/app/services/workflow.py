import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assignment import RequestAssignment
from app.models.enums import RequestStatus, UserRole
from app.models.request import WorkflowRequest
from app.models.status_history import RequestStatusHistory
from app.models.user import User


class WorkflowService:
    _transitions = {
        RequestStatus.PENDING: {RequestStatus.ASSIGNED, RequestStatus.CANCELLED},
        RequestStatus.ASSIGNED: {RequestStatus.IN_PROGRESS},
        RequestStatus.IN_PROGRESS: {RequestStatus.APPROVED, RequestStatus.REJECTED},
        RequestStatus.APPROVED: {RequestStatus.COMPLETED},
    }

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _is_manager_or_admin(user: User) -> bool:
        return user.role in {UserRole.MANAGER, UserRole.ADMIN}

    def assign(self, request: WorkflowRequest, assignee_id: uuid.UUID, actor: User) -> WorkflowRequest:
        if not self._is_manager_or_admin(actor):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only managers and administrators can assign requests")
        if request.status not in {RequestStatus.PENDING, RequestStatus.ASSIGNED}:
            raise HTTPException(status.HTTP_409_CONFLICT, "Only pending or assigned requests can be assigned")
        assignee = self.db.get(User, assignee_id)
        if not assignee or not assignee.is_active:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Assignee is unavailable")
        old_status = request.status
        request.assignee_id = assignee.id
        request.status = RequestStatus.ASSIGNED
        self.db.add(RequestAssignment(request_id=request.id, assignee_id=assignee.id, assigned_by_id=actor.id))
        if old_status != RequestStatus.ASSIGNED:
            self._record_status(request, old_status, RequestStatus.ASSIGNED, actor.id, "Request assigned")
        self.db.commit()
        self.db.refresh(request)
        return request

    def transition(self, request: WorkflowRequest, target: RequestStatus, actor: User, note: str | None) -> WorkflowRequest:
        if target == RequestStatus.CANCELLED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Use the cancellation endpoint for cancellations")
        allowed = self._transitions.get(request.status, set())
        if target not in allowed:
            raise HTTPException(status.HTTP_409_CONFLICT, f"Cannot transition from {request.status.value} to {target.value}")
        if target == RequestStatus.IN_PROGRESS and actor.id != request.assignee_id and not self._is_manager_or_admin(actor):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the assignee, manager, or administrator can start work")
        if target in {RequestStatus.APPROVED, RequestStatus.REJECTED} and not self._is_manager_or_admin(actor):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only managers and administrators can approve or reject requests")
        if target == RequestStatus.COMPLETED and actor.id != request.assignee_id and not self._is_manager_or_admin(actor):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the assignee, manager, or administrator can complete requests")
        old_status = request.status
        request.status = target
        if target == RequestStatus.COMPLETED:
            request.completed_at = datetime.now(timezone.utc)
        self._record_status(request, old_status, target, actor.id, note)
        self.db.commit()
        self.db.refresh(request)
        return request

    def history(self, request: WorkflowRequest) -> list[RequestStatusHistory]:
        return list(self.db.scalars(select(RequestStatusHistory).where(RequestStatusHistory.request_id == request.id).order_by(RequestStatusHistory.changed_at)))

    def _record_status(self, request: WorkflowRequest, old: RequestStatus | None, new: RequestStatus, actor_id: uuid.UUID, note: str | None) -> None:
        self.db.add(RequestStatusHistory(request_id=request.id, from_status=old, to_status=new, changed_by_id=actor_id, note=note))
