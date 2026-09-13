from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.enums import RequestStatus, UserRole
from app.models.request import WorkflowRequest
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardSummary(BaseModel):
    total: int
    pending: int
    assigned: int
    in_progress: int
    approved: int
    rejected: int
    completed: int
    cancelled: int


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(WorkflowRequest.status, func.count().label("n")).group_by(WorkflowRequest.status)

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
    # ADMIN sees all — no filter

    counts: dict[str, int] = {s.value: 0 for s in RequestStatus}
    for status, n in db.execute(stmt).all():
        counts[status.value] = n

    return DashboardSummary(
        total=sum(counts.values()),
        pending=counts["pending"],
        assigned=counts["assigned"],
        in_progress=counts["in_progress"],
        approved=counts["approved"],
        rejected=counts["rejected"],
        completed=counts["completed"],
        cancelled=counts["cancelled"],
    )
