import pytest
from fastapi import HTTPException

from app.models.enums import RequestStatus, UserRole
from app.models.request import WorkflowRequest
from app.models.user import User
from app.services.workflow import WorkflowService


def make_user(email: str, role: UserRole) -> User:
    return User(email=email, full_name=email, hashed_password="not-used", role=role)


def workflow_fixture(db_session):
    manager = make_user("manager@example.com", UserRole.MANAGER)
    employee = make_user("employee@example.com", UserRole.EMPLOYEE)
    requester = make_user("requester@example.com", UserRole.EMPLOYEE)
    db_session.add_all([manager, employee, requester])
    db_session.flush()
    request = WorkflowRequest(title="Laptop", description="Need a laptop", requester_id=requester.id)
    db_session.add(request)
    db_session.commit()
    return WorkflowService(db_session), request, manager, employee, requester


def test_valid_workflow_records_status_history(db_session):
    service, request, manager, employee, _ = workflow_fixture(db_session)
    service.assign(request, employee.id, manager)
    service.transition(request, RequestStatus.IN_PROGRESS, employee, "Started")
    service.transition(request, RequestStatus.APPROVED, manager, "Approved")
    completed = service.transition(request, RequestStatus.COMPLETED, employee, "Delivered")

    assert completed.status == RequestStatus.COMPLETED
    assert completed.completed_at is not None
    assert [entry.to_status for entry in service.history(request)] == [
        RequestStatus.ASSIGNED,
        RequestStatus.IN_PROGRESS,
        RequestStatus.APPROVED,
        RequestStatus.COMPLETED,
    ]


def test_invalid_or_unauthorized_workflow_actions_are_rejected(db_session):
    service, request, manager, employee, requester = workflow_fixture(db_session)
    with pytest.raises(HTTPException) as invalid:
        service.transition(request, RequestStatus.APPROVED, manager, None)
    assert invalid.value.status_code == 409
    with pytest.raises(HTTPException) as unauthorized:
        service.assign(request, employee.id, requester)
    assert unauthorized.value.status_code == 403
    service.assign(request, employee.id, manager)
    service.transition(request, RequestStatus.IN_PROGRESS, employee, None)
    with pytest.raises(HTTPException) as employee_approval:
        service.transition(request, RequestStatus.APPROVED, employee, None)
    assert employee_approval.value.status_code == 403
