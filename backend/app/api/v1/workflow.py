import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.requests import RequestRead
from app.schemas.workflow import AssignmentCreate, StatusHistoryRead, TransitionCreate
from app.services.requests import RequestService
from app.services.workflow import WorkflowService

router = APIRouter(tags=["workflow"])


@router.post("/requests/{request_id}/assign", response_model=RequestRead)
def assign_request(request_id: uuid.UUID, payload: AssignmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    request = RequestService(db).get(request_id, user)
    return WorkflowService(db).assign(request, payload.assignee_id, user)


@router.post("/requests/{request_id}/transition", response_model=RequestRead)
def transition_request(request_id: uuid.UUID, payload: TransitionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    request = RequestService(db).get(request_id, user)
    return WorkflowService(db).transition(request, payload.status, user, payload.note)


@router.get("/requests/{request_id}/history", response_model=list[StatusHistoryRead])
def request_history(request_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    request = RequestService(db).get(request_id, user)
    return WorkflowService(db).history(request)
