import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import RequestPriority, RequestStatus

class RequestCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3, max_length=10000)
    category_id: uuid.UUID | None = None
    priority: RequestPriority = RequestPriority.MEDIUM
    due_date: datetime | None = None

class RequestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=3, max_length=10000)
    category_id: uuid.UUID | None = None
    priority: RequestPriority | None = None
    due_date: datetime | None = None

class RequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID; title: str; description: str; category_id: uuid.UUID | None
    requester_id: uuid.UUID; assignee_id: uuid.UUID | None; priority: RequestPriority; status: RequestStatus
    created_at: datetime; updated_at: datetime; due_date: datetime | None; completed_at: datetime | None

class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=10000)

class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID; request_id: uuid.UUID; author_id: uuid.UUID; body: str; created_at: datetime

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID; name: str; description: str | None; is_active: bool; created_at: datetime
