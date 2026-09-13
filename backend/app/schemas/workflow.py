import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RequestStatus


class AssignmentCreate(BaseModel):
    assignee_id: uuid.UUID


class TransitionCreate(BaseModel):
    status: RequestStatus
    note: str | None = Field(default=None, max_length=500)


class StatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    from_status: RequestStatus | None
    to_status: RequestStatus
    changed_by_id: uuid.UUID
    note: str | None
    changed_at: datetime
