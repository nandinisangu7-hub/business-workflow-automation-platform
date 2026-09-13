import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import UserRead
from app.services.audit import AuditService

router = APIRouter(prefix="/users", tags=["users"])


class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None
    role: UserRole | None = None


class PaginatedUsers(BaseModel):
    items: list[UserRead]
    page: int
    page_size: int
    total: int
    total_pages: int


@router.get("", response_model=PaginatedUsers)
def list_users(
    search: str | None = Query(default=None, max_length=200),
    role: UserRole | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    from sqlalchemy import func
    stmt = select(User).order_by(User.full_name)
    if search:
        term = f"%{search}%"
        stmt = stmt.where(or_(User.full_name.ilike(term), User.email.ilike(term)))
    if role:
        stmt = stmt.where(User.role == role)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    total_pages = max(1, (total + page_size - 1) // page_size)
    items = list(db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)))
    return PaginatedUsers(items=items, page=page, page_size=page_size, total=total, total_pages=total_pages)


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER) and current_user.id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    changes = payload.model_dump(exclude_unset=True)
    old_role = user.role
    for k, v in changes.items():
        setattr(user, k, v)
    if "role" in changes and changes["role"] != old_role:
        AuditService(db).record(
            actor_id=current_user.id,
            action="user_role_changed",
            entity_type="user",
            entity_id=user.id,
            previous={"role": old_role.value},
            new={"role": user.role.value},
        )
    db.commit()
    db.refresh(user)
    return user
