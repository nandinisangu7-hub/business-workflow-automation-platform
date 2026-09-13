import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.v1.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.category import RequestCategory
from app.models.enums import UserRole
from app.models.request import WorkflowRequest
from app.models.user import User
from app.schemas.requests import CategoryCreate, CategoryRead, CommentCreate, CommentRead, RequestCreate, RequestRead, RequestUpdate
from app.services.requests import RequestService

router = APIRouter(tags=["requests"])
@router.get("/categories", response_model=list[CategoryRead])
def categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)): return list(db.scalars(select(RequestCategory).where(RequestCategory.is_active.is_(True)).order_by(RequestCategory.name)))
@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.ADMIN))):
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
@router.get("/requests", response_model=list[RequestRead])
def list_requests(db: Session = Depends(get_db), user: User = Depends(get_current_user)): return RequestService(db).list_visible(user)
@router.post("/requests", response_model=RequestRead, status_code=status.HTTP_201_CREATED)
def create_request(payload: RequestCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)): return RequestService(db).create(payload, user)
@router.get("/requests/{request_id}", response_model=RequestRead)
def get_request(request_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)): return RequestService(db).get(request_id, user)
@router.patch("/requests/{request_id}", response_model=RequestRead)
def update_request(request_id: uuid.UUID, payload: RequestUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)): return RequestService(db).update(RequestService(db).get(request_id, user), payload, user)
@router.post("/requests/{request_id}/cancel", response_model=RequestRead)
def cancel_request(request_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)): return RequestService(db).cancel(RequestService(db).get(request_id, user), user)
@router.post("/requests/{request_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def add_comment(request_id: uuid.UUID, payload: CommentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)): return RequestService(db).add_comment(RequestService(db).get(request_id, user), payload, user)
@router.get("/requests/{request_id}/comments", response_model=list[CommentRead])
def list_comments(request_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = RequestService(db)
    return service.list_comments(service.get(request_id, user))
