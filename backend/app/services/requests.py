import uuid
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.models.category import RequestCategory
from app.models.comment import RequestComment
from app.models.enums import RequestStatus, UserRole
from app.models.request import WorkflowRequest
from app.models.user import User
from app.services.audit import AuditService
from app.schemas.requests import CommentCreate, RequestCreate, RequestUpdate

class RequestService:
    def __init__(self, db: Session):
        self.db = db
    def permitted(self, request: WorkflowRequest, user: User) -> bool:
        return user.role == UserRole.ADMIN or request.requester_id == user.id or request.assignee_id == user.id or request.requester.manager_id == user.id
    def get(self, request_id: uuid.UUID, user: User) -> WorkflowRequest:
        request = self.db.get(WorkflowRequest, request_id)
        if not request:
            raise HTTPException(404, "Request not found")
        if not self.permitted(request, user):
            raise HTTPException(403, "You do not have access to this request")
        return request
    def create(self, payload: RequestCreate, user: User) -> WorkflowRequest:
        if payload.category_id:
            category = self.db.get(RequestCategory, payload.category_id)
            if not category or not category.is_active: raise HTTPException(422, "Category is unavailable")
        request = WorkflowRequest(**payload.model_dump(), requester_id=user.id)
        self.db.add(request)
        self.db.flush()
        AuditService(self.db).record(actor_id=user.id, action="request_created", entity_type="request", entity_id=request.id, new={"status": request.status.value})
        self.db.commit()
        self.db.refresh(request)
        return request
    def update(self, request: WorkflowRequest, payload: RequestUpdate, user: User) -> WorkflowRequest:
        if request.requester_id != user.id or request.status != RequestStatus.PENDING:
            raise HTTPException(403, "Only the requester may edit a pending request")
        changes = payload.model_dump(exclude_unset=True)
        if "category_id" in changes and changes["category_id"]:
            category = self.db.get(RequestCategory, changes["category_id"])
            if not category or not category.is_active:
                raise HTTPException(422, "Category is unavailable")
        for key, value in changes.items():
            setattr(request, key, value)
        AuditService(self.db).record(actor_id=user.id, action="request_updated", entity_type="request", entity_id=request.id, details={"fields": sorted(changes)})
        self.db.commit()
        self.db.refresh(request)
        return request
    def cancel(self, request: WorkflowRequest, user: User) -> WorkflowRequest:
        if request.requester_id != user.id or request.status != RequestStatus.PENDING:
            raise HTTPException(409, "Only a pending request can be cancelled by its requester")
        request.status = RequestStatus.CANCELLED
        AuditService(self.db).record(actor_id=user.id, action="request_cancelled", entity_type="request", entity_id=request.id, previous={"status": RequestStatus.PENDING.value}, new={"status": RequestStatus.CANCELLED.value})
        self.db.commit()
        self.db.refresh(request)
        return request
    def list_visible(self, user: User) -> list[WorkflowRequest]:
        statement = select(WorkflowRequest).order_by(WorkflowRequest.created_at.desc())
        if user.role == UserRole.ADMIN:
            return list(self.db.scalars(statement))
        visible_to_user = or_(WorkflowRequest.requester_id == user.id, WorkflowRequest.assignee_id == user.id)
        if user.role == UserRole.MANAGER:
            visible_to_user = or_(visible_to_user, WorkflowRequest.requester.has(User.manager_id == user.id))
        return list(self.db.scalars(statement.where(visible_to_user)))
    def add_comment(self, request: WorkflowRequest, payload: CommentCreate, user: User) -> RequestComment:
        body = payload.body.strip()
        if not body:
            raise HTTPException(422, "Comment cannot be blank")
        comment = RequestComment(request_id=request.id, author_id=user.id, body=body)
        self.db.add(comment)
        self.db.flush()
        AuditService(self.db).record(actor_id=user.id, action="comment_created", entity_type="request_comment", entity_id=comment.id, details={"request_id": str(request.id)})
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def list_comments(self, request: WorkflowRequest) -> list[RequestComment]:
        return list(self.db.scalars(select(RequestComment).where(RequestComment.request_id == request.id).order_by(RequestComment.created_at)))
