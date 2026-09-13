from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.v1.dependencies import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.audit import AuditLogRead
from app.services.audit import AuditService

router = APIRouter(prefix="/audit-logs", tags=["audit"])

@router.get("", response_model=list[AuditLogRead])
def list_audit_logs(entity_type: str | None = Query(default=None, max_length=50), entity_id: str | None = Query(default=None, max_length=36), db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.ADMIN))):
    return AuditService(db).list(entity_type=entity_type, entity_id=entity_id)
