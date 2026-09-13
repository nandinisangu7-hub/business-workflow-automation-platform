import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    recipient_id: uuid.UUID
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime


class NotificationSummary(BaseModel):
    unread_count: int
