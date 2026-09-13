"""Integration tests for the notification system."""
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.enums import UserRole
from app.models.user import User
import app.models as _models  # noqa: F401


@event.listens_for(Engine, "connect")
def _fk_pragma(dbapi_conn, _):
    dbapi_conn.cursor().execute("PRAGMA foreign_keys=ON")


def _setup():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    shared_db = Session()

    def override_db():
        yield shared_db

    app.dependency_overrides[get_db] = override_db
    return TestClient(app), shared_db, engine


def test_notifications_created_on_workflow_events():
    client, db, engine = _setup()
    try:
        # Create manager and employee directly in DB with correct roles
        manager = User(email="mgr@n.com", full_name="Manager", hashed_password=hash_password("correct-horse"), role=UserRole.MANAGER)
        employee = User(email="emp@n.com", full_name="Employee", hashed_password=hash_password("correct-horse"), role=UserRole.EMPLOYEE)
        db.add_all([manager, employee])
        db.flush()  # get manager.id before setting employee.manager_id
        employee.manager_id = manager.id
        db.commit()

        mgr_token = client.post("/api/v1/auth/login", data={"username": "mgr@n.com", "password": "correct-horse"}).json()["access_token"]
        emp_token = client.post("/api/v1/auth/login", data={"username": "emp@n.com", "password": "correct-horse"}).json()["access_token"]
        mgr_headers = {"Authorization": f"Bearer {mgr_token}"}
        emp_headers = {"Authorization": f"Bearer {emp_token}"}

        # Employee creates a request → manager should get a notification
        req = client.post("/api/v1/requests", headers=emp_headers, json={"title": "New laptop", "description": "Battery dead"})
        assert req.status_code == 201
        request_id = req.json()["id"]

        mgr_notifications = client.get("/api/v1/notifications", headers=mgr_headers).json()
        assert any(n["type"] == "request_created" for n in mgr_notifications)

        # Manager assigns → employee should get a notification
        assign = client.post(f"/api/v1/requests/{request_id}/assign", headers=mgr_headers, json={"assignee_id": str(manager.id)})
        assert assign.status_code == 200

        emp_notifications = client.get("/api/v1/notifications", headers=emp_headers).json()
        assert any(n["type"] == "request_assigned" for n in emp_notifications)

        # Check unread count
        count = client.get("/api/v1/notifications/unread-count", headers=emp_headers).json()
        assert count["unread_count"] >= 1

        # Mark individual notification read
        notif_id = emp_notifications[0]["id"]
        patched = client.patch(f"/api/v1/notifications/{notif_id}/read", headers=emp_headers)
        assert patched.status_code == 200
        assert patched.json()["is_read"] is True

        # Mark all read
        client.post("/api/v1/notifications/read-all", headers=emp_headers)
        count_after = client.get("/api/v1/notifications/unread-count", headers=emp_headers).json()
        assert count_after["unread_count"] == 0

    finally:
        db.close()
        app.dependency_overrides.clear()
        engine.dispose()
