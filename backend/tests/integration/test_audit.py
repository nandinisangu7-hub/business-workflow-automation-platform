"""Integration tests for the audit log API."""
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
from app.services.audit import AuditService
import app.models as _models  # noqa: F401


@event.listens_for(Engine, "connect")
def _fk(dbapi_conn, _):
    dbapi_conn.cursor().execute("PRAGMA foreign_keys=ON")


def _setup():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    shared_db = Session()
    app.dependency_overrides[get_db] = lambda: (yield shared_db)
    return TestClient(app), shared_db, engine


def _headers(client, email):
    token = client.post("/api/v1/auth/login", data={"username": email, "password": "correct-horse"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_list_audit_logs():
    client, db, engine = _setup()
    try:
        admin = User(email="admin@a.com", full_name="Admin", hashed_password=hash_password("correct-horse"), role=UserRole.ADMIN)
        db.add(admin); db.commit()
        AuditService(db).record(actor_id=admin.id, action="test_action", entity_type="user", entity_id=admin.id)
        db.commit()

        resp = client.get("/api/v1/audit-logs", headers=_headers(client, "admin@a.com"))
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert any(entry["action"] == "test_action" for entry in body["items"])
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_non_admin_cannot_access_audit_logs():
    client, db, engine = _setup()
    try:
        emp = User(email="emp@a.com", full_name="Emp", hashed_password=hash_password("correct-horse"), role=UserRole.EMPLOYEE)
        db.add(emp); db.commit()

        resp = client.get("/api/v1/audit-logs", headers=_headers(client, "emp@a.com"))
        assert resp.status_code == 403
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_audit_logs_filter_by_entity_type():
    client, db, engine = _setup()
    try:
        admin = User(email="admin2@a.com", full_name="Admin2", hashed_password=hash_password("correct-horse"), role=UserRole.ADMIN)
        db.add(admin); db.commit()

        svc = AuditService(db)
        svc.record(actor_id=admin.id, action="request_created", entity_type="request", entity_id="req-1")
        svc.record(actor_id=admin.id, action="user_role_changed", entity_type="user", entity_id=admin.id)
        db.commit()

        h = _headers(client, "admin2@a.com")
        resp = client.get("/api/v1/audit-logs?entity_type=request", headers=h)
        assert resp.status_code == 200
        assert all(entry["entity_type"] == "request" for entry in resp.json()["items"])

        resp2 = client.get("/api/v1/audit-logs?entity_type=user", headers=h)
        assert all(entry["entity_type"] == "user" for entry in resp2.json()["items"])
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_audit_logs_filter_by_entity_id():
    client, db, engine = _setup()
    try:
        admin = User(email="admin3@a.com", full_name="Admin3", hashed_password=hash_password("correct-horse"), role=UserRole.ADMIN)
        db.add(admin); db.commit()

        svc = AuditService(db)
        svc.record(actor_id=admin.id, action="action_a", entity_type="request", entity_id="target-id")
        svc.record(actor_id=admin.id, action="action_b", entity_type="request", entity_id="other-id")
        db.commit()

        resp = client.get("/api/v1/audit-logs?entity_id=target-id", headers=_headers(client, "admin3@a.com"))
        assert resp.status_code == 200
        assert all(entry["entity_id"] == "target-id" for entry in resp.json()["items"])
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()
