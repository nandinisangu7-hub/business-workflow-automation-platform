"""
Phase 2 tests.

These prove the ORM layer itself is correct, independent of any API route
or business logic (neither exists yet). Specifically:
  - required constraints are actually enforced (unique email)
  - enum columns actually reject invalid values
  - relationships defined with back_populates resolve both directions
    correctly (e.g. request.requester AND user.created_requests)
  - the self-referential manager/direct_reports relationship works
  - append-only history tables (status_history) preserve insertion order
"""
import uuid

import pytest
from sqlalchemy.exc import IntegrityError, StatementError

from app.models.category import RequestCategory
from app.models.enums import RequestPriority, RequestStatus, UserRole
from app.models.notification import Notification
from app.models.request import WorkflowRequest
from app.models.status_history import RequestStatusHistory
from app.models.user import User


def make_user(email="employee@example.com", role=UserRole.EMPLOYEE, **kwargs) -> User:
    return User(
        email=email,
        full_name=kwargs.pop("full_name", "Test User"),
        hashed_password="not-a-real-hash",  # hashing arrives in Phase 3
        role=role,
        **kwargs,
    )


def test_create_user_persists_with_defaults(db_session):
    user = make_user()
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter_by(email="employee@example.com").one()
    assert fetched.role == UserRole.EMPLOYEE
    assert fetched.is_active is True  # default
    assert isinstance(fetched.id, uuid.UUID)  # GUID type round-trips correctly


def test_duplicate_email_is_rejected(db_session):
    db_session.add(make_user(email="dup@example.com"))
    db_session.commit()

    db_session.add(make_user(email="dup@example.com"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_invalid_role_value_is_rejected(db_session):
    user = make_user()
    db_session.add(user)
    db_session.commit()

    # Bypassing the enum's Python type on purpose, to prove the column
    # itself — not just application code — refuses an out-of-range value.
    user.role = "superuser"
    with pytest.raises((StatementError, LookupError, ValueError)):
        db_session.commit()


def test_manager_direct_report_relationship_both_directions(db_session):
    manager = make_user(email="manager@example.com", role=UserRole.MANAGER)
    db_session.add(manager)
    db_session.flush()  # assigns manager.id without a full commit

    employee = make_user(email="report@example.com", manager_id=manager.id)
    db_session.add(employee)
    db_session.commit()

    assert employee.manager.email == "manager@example.com"
    assert manager.direct_reports[0].email == "report@example.com"


def test_workflow_request_relationships_resolve_both_directions(db_session):
    requester = make_user(email="requester@example.com")
    category = RequestCategory(name="IT Equipment")
    db_session.add_all([requester, category])
    db_session.flush()

    request = WorkflowRequest(
        title="New laptop",
        description="Need a laptop for onboarding",
        category_id=category.id,
        requester_id=requester.id,
        priority=RequestPriority.HIGH,
    )
    db_session.add(request)
    db_session.commit()

    assert request.status == RequestStatus.PENDING  # column default applied
    assert request.category.name == "IT Equipment"
    assert request.requester.email == "requester@example.com"
    assert category.requests[0].title == "New laptop"
    assert requester.created_requests[0].title == "New laptop"


def test_status_history_preserves_chronological_order(db_session):
    requester = make_user(email="chrono@example.com")
    db_session.add(requester)
    db_session.flush()

    request = WorkflowRequest(
        title="Expense reimbursement",
        description="Client dinner",
        requester_id=requester.id,
    )
    db_session.add(request)
    db_session.flush()

    db_session.add(
        RequestStatusHistory(
            request_id=request.id,
            from_status=None,
            to_status=RequestStatus.PENDING,
            changed_by_id=requester.id,
        )
    )
    db_session.add(
        RequestStatusHistory(
            request_id=request.id,
            from_status=RequestStatus.PENDING,
            to_status=RequestStatus.ASSIGNED,
            changed_by_id=requester.id,
        )
    )
    db_session.commit()
    db_session.refresh(request)

    history = request.status_history
    assert [h.to_status for h in history] == [RequestStatus.PENDING, RequestStatus.ASSIGNED]
    assert history[0].from_status is None  # creation event has no "previous" status


def test_notification_recipient_relationship(db_session):
    recipient = make_user(email="notify-me@example.com")
    db_session.add(recipient)
    db_session.flush()

    db_session.add(
        Notification(
            recipient_id=recipient.id,
            type="request_assigned",
            title="A request was assigned to you",
            message="You've been assigned 'New laptop'.",
        )
    )
    db_session.commit()
    db_session.refresh(recipient)

    assert recipient.notifications[0].is_read is False  # default
    assert recipient.notifications[0].type == "request_assigned"
