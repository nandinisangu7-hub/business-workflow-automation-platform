import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notifications import NotificationRead, NotificationSummary
from app.services.notifications import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return NotificationService(db).list_for_user(user.id)


@router.get("/unread-count", response_model=NotificationSummary)
def unread_count(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return NotificationSummary(unread_count=NotificationService(db).unread_count(user.id))


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_read(notification_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = NotificationService(db).mark_read(notification_id, user.id)
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return n


@router.post("/read-all", response_model=NotificationSummary)
def mark_all_read(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    count = NotificationService(db).mark_all_read(user.id)
    return NotificationSummary(unread_count=0)
