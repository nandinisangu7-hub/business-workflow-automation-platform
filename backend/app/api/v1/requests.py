import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.v1.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.category import RequestCategory
from app.models.enums import RequestPriority, RequestStatus, UserRole
from app.models.request import WorkflowRequest
from app.models.user import User
from app.schemas.requests import (
    CategoryCreate, CategoryRead, CommentCreate, CommentRead,
    RequestCreate, RequestRead, RequestUpdate,
)
from app.services.requests import RequestService
from pydantic import BaseModel
from typing import Any

router = APIRouter(tags=["requests"])


class PaginatedRequests(BaseModel):
    items: list[RequestRead]
    page: int
    page_size: int
    total: int
    total_pages: int


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryRead])
def categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return list(db.scalars(
        select(RequestCategory)
        .where(RequestCategory.is_active.is_(True))
        .order_by(RequestCategory.name)
    ))


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    category = RequestCategory(**payload.model_dump())
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="A category with this name already exists")
    db.refresh(category)
    return category


# ── Requests list with search / filter / pagination ───────────────────────────

@router.get("/requests", response_model=PaginatedRequests)
def list_requests(
    search: str | None = Query(default=None, max_length=200),
    status_filter: RequestStatus | None = Query(default=None, alias="status"),
    priority: RequestPriority | None = Query(default=None),
    category_id: uuid.UUID | None = Query(default=None),
    assignee_id: uuid.UUID | None = Query(default=None),
    requester_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(WorkflowRequest).order_by(WorkflowRequest.created_at.desc())

    # Visibility scoping
    if user.role == UserRole.EMPLOYEE:
        stmt = stmt.where(WorkflowRequest.requester_id == user.id)
    elif user.role == UserRole.MANAGER:
        stmt = stmt.where(
            or_(
                WorkflowRequest.requester_id == user.id,
                WorkflowRequest.assignee_id == user.id,
                WorkflowRequest.requester.has(User.manager_id == user.id),
            )
        )
    # ADMIN sees all

    # Filters
    if search:
        term = f"%{search}%"
        stmt = stmt.where(
            or_(
                WorkflowRequest.title.ilike(term),
                WorkflowRequest.description.ilike(term),
            )
        )
    if status_filter:
        stmt = stmt.where(WorkflowRequest.status == status_filter)
    if priority:
        stmt = stmt.where(WorkflowRequest.priority == priority)
    if category_id:
        stmt = stmt.where(WorkflowRequest.category_id == category_id)
    if assignee_id:
        stmt = stmt.where(WorkflowRequest.assignee_id == assignee_id)
    if requester_id:
        stmt = stmt.where(WorkflowRequest.requester_id == requester_id)

    # Count total before pagination
    from sqlalchemy import func
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    total_pages = max(1, (total + page_size - 1) // page_size)

    items = list(db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)))
    return PaginatedRequests(
        items=items, page=page, page_size=page_size,
        total=total, total_pages=total_pages,
    )


# ── Single request CRUD ───────────────────────────────────────────────────────

@router.post("/requests", response_model=RequestRead, status_code=status.HTTP_201_CREATED)
def create_request(payload: RequestCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return RequestService(db).create(payload, user)


@router.get("/requests/{request_id}", response_model=RequestRead)
def get_request(request_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return RequestService(db).get(request_id, user)


@router.patch("/requests/{request_id}", response_model=RequestRead)
def update_request(request_id: uuid.UUID, payload: RequestUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = RequestService(db)
    return svc.update(svc.get(request_id, user), payload, user)


@router.post("/requests/{request_id}/cancel", response_model=RequestRead)
def cancel_request(request_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = RequestService(db)
    return svc.cancel(svc.get(request_id, user), user)


# ── Comments ──────────────────────────────────────────────────────────────────

@router.post("/requests/{request_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def add_comment(request_id: uuid.UUID, payload: CommentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = RequestService(db)
    return svc.add_comment(svc.get(request_id, user), payload, user)


@router.get("/requests/{request_id}/comments", response_model=list[CommentRead])
def list_comments(request_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = RequestService(db)
    return svc.list_comments(svc.get(request_id, user))
