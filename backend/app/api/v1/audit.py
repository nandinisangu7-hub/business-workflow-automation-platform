from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.v1.dependencies import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.audit import AuditLogRead
from app.services.audit import AuditService

router = APIRouter(prefix="/audit-logs", tags=["audit"])


class PaginatedAuditLogs(BaseModel):
    items: list[AuditLogRead]
    page: int
    page_size: int
    total: int
    total_pages: int


@router.get("", response_model=PaginatedAuditLogs)
def list_audit_logs(
    entity_type: str | None = Query(default=None, max_length=50),
    entity_id: str | None = Query(default=None, max_length=36),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    items, total = AuditService(db).list(
        entity_type=entity_type,
        entity_id=entity_id,
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    total_pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedAuditLogs(
        items=items, page=page, page_size=page_size,
        total=total, total_pages=total_pages,
    )
