import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict

class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID; user_id: uuid.UUID | None; action: str; entity_type: str; entity_id: str
    previous_value: dict[str, Any] | None; new_value: dict[str, Any] | None; details: dict[str, Any] | None; created_at: datetime
