"""Phase 10 integration tests: search, filtering, sorting, and pagination."""
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
def _fk(dbapi_conn, _):
    dbapi_conn.cursor().execute("PRAGMA foreign_keys=ON")


def _make_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    def override_db():
        db = Session()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override_db
    return TestClient(app), engine


def _token(client, email, password="correct-horse"):
    return client.post("/api/v1/auth/login", data={"username": email, "password": password}).json()["access_token"]


def _headers(client, email):
    return {"Authorization": f"Bearer {_token(client, email)}"}


# ── Requests: search ──────────────────────────────────────────────────────────

def test_requests_search_by_title():
    client, engine = _make_client()
    try:
        client.post("/api/v1/auth/register", json={"email": "emp@s.com", "full_name": "Emp", "password": "correct-horse"})
        h = _headers(client, "emp@s.com")
        client.post("/api/v1/requests", headers=h, json={"title": "Laptop replacement", "description": "Battery dead"})
        client.post("/api/v1/requests", headers=h, json={"title": "Office chair", "description": "Back pain"})

        resp = client.get("/api/v1/requests?search=laptop", headers=h)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["title"] == "Laptop replacement"
    finally:
        app.dependency_overrides.clear(); engine.dispose()


def test_requests_search_by_description():
    client, engine = _make_client()
    try:
        client.post("/api/v1/auth/register", json={"email": "emp2@s.com", "full_name": "Emp2", "password": "correct-horse"})
        h = _headers(client, "emp2@s.com")
        client.post("/api/v1/requests", headers=h, json={"title": "Request A", "description": "urgent keyboard issue"})
        client.post("/api/v1/requests", headers=h, json={"title": "Request B", "description": "routine supply order"})

        resp = client.get("/api/v1/requests?search=keyboard", headers=h)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
    finally:
        app.dependency_overrides.clear(); engine.dispose()


# ── Requests: filter by status ────────────────────────────────────────────────

def test_requests_filter_by_status():
    client, engine = _make_client()
    try:
        client.post("/api/v1/auth/register", json={"email": "mgr@s.com", "full_name": "Mgr", "password": "correct-horse"})
        client.post("/api/v1/auth/register", json={"email": "emp3@s.com", "full_name": "Emp3", "password": "correct-horse"})
        emp_h = _headers(client, "emp3@s.com")
        mgr_h = _headers(client, "mgr@s.com")

        r1 = client.post("/api/v1/requests", headers=emp_h, json={"title": "Req1", "description": "desc"})
        r2 = client.post("/api/v1/requests", headers=emp_h, json={"title": "Req2", "description": "desc"})
        assert r1.status_code == 201 and r2.status_code == 201

        # Cancel one request
        client.post(f"/api/v1/requests/{r1.json()['id']}/cancel", headers=emp_h)

        # Admin sees all; use mgr to see both (mgr is not yet assigned, but as admin-like test use emp's own view)
        pending = client.get("/api/v1/requests?status=pending", headers=emp_h)
        assert pending.status_code == 200
        assert pending.json()["total"] == 1

        cancelled = client.get("/api/v1/requests?status=cancelled", headers=emp_h)
        assert cancelled.json()["total"] == 1
    finally:
        app.dependency_overrides.clear(); engine.dispose()


# ── Requests: filter by priority ─────────────────────────────────────────────

def test_requests_filter_by_priority():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    shared_db = Session()
    app.dependency_overrides[get_db] = lambda: (yield shared_db)
    client = TestClient(app)
    try:
        client.post("/api/v1/auth/register", json={"email": "emp4@s.com", "full_name": "Emp4", "password": "correct-horse"})
        h = _headers(client, "emp4@s.com")
        client.post("/api/v1/requests", headers=h, json={"title": "High prio", "description": "Battery dead", "priority": "high"})
        client.post("/api/v1/requests", headers=h, json={"title": "Low prio", "description": "Routine order", "priority": "low"})

        resp = client.get("/api/v1/requests?priority=high", headers=h)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert resp.json()["items"][0]["priority"] == "high"
    finally:
        shared_db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_requests_pagination():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    shared_db = Session()
    app.dependency_overrides[get_db] = lambda: (yield shared_db)
    client = TestClient(app)
    try:
        client.post("/api/v1/auth/register", json={"email": "emp5@s.com", "full_name": "Emp5", "password": "correct-horse"})
        h = _headers(client, "emp5@s.com")
        for i in range(5):
            client.post("/api/v1/requests", headers=h, json={"title": f"Request {i}", "description": "Test description"})

        page1 = client.get("/api/v1/requests?page=1&page_size=2", headers=h)
        assert page1.status_code == 200
        body = page1.json()
        assert body["total"] == 5
        assert body["total_pages"] == 3
        assert len(body["items"]) == 2
        assert body["page"] == 1

        page2 = client.get("/api/v1/requests?page=2&page_size=2", headers=h)
        assert len(page2.json()["items"]) == 2

        page3 = client.get("/api/v1/requests?page=3&page_size=2", headers=h)
        assert len(page3.json()["items"]) == 1
    finally:
        shared_db.close(); app.dependency_overrides.clear(); engine.dispose()


# ── Users: search and filter ──────────────────────────────────────────────────

def test_users_search_by_name():
    client, engine = _make_client()
    try:
        engine2 = engine
        Session = sessionmaker(bind=engine2)
        db = Session()
        from app.core.security import hash_password as hp
        db.add(User(email="alice@u.com", full_name="Alice Smith", hashed_password=hp("correct-horse"), role=UserRole.EMPLOYEE))
        db.add(User(email="bob@u.com", full_name="Bob Jones", hashed_password=hp("correct-horse"), role=UserRole.ADMIN))
        db.commit()
        db.close()

        h = _headers(client, "bob@u.com")
        resp = client.get("/api/v1/users?search=alice", headers=h)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert resp.json()["items"][0]["email"] == "alice@u.com"
    finally:
        app.dependency_overrides.clear(); engine.dispose()


def test_users_filter_by_role():
    client, engine = _make_client()
    try:
        Session = sessionmaker(bind=engine)
        db = Session()
        from app.core.security import hash_password as hp
        db.add(User(email="admin@r.com", full_name="Admin", hashed_password=hp("correct-horse"), role=UserRole.ADMIN))
        db.add(User(email="mgr@r.com", full_name="Manager", hashed_password=hp("correct-horse"), role=UserRole.MANAGER))
        db.add(User(email="emp@r.com", full_name="Employee", hashed_password=hp("correct-horse"), role=UserRole.EMPLOYEE))
        db.commit(); db.close()

        h = _headers(client, "admin@r.com")
        resp = client.get("/api/v1/users?role=manager", headers=h)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert resp.json()["items"][0]["role"] == "manager"
    finally:
        app.dependency_overrides.clear(); engine.dispose()


def test_users_pagination():
    client, engine = _make_client()
    try:
        Session = sessionmaker(bind=engine)
        db = Session()
        from app.core.security import hash_password as hp
        admin = User(email="admin@p.com", full_name="Admin", hashed_password=hp("correct-horse"), role=UserRole.ADMIN)
        db.add(admin)
        for i in range(4):
            db.add(User(email=f"user{i}@p.com", full_name=f"User {i}", hashed_password=hp("correct-horse"), role=UserRole.EMPLOYEE))
        db.commit(); db.close()

        h = _headers(client, "admin@p.com")
        resp = client.get("/api/v1/users?page=1&page_size=2", headers=h)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 5
        assert body["total_pages"] == 3
        assert len(body["items"]) == 2
    finally:
        app.dependency_overrides.clear(); engine.dispose()


# ── Audit logs: pagination ────────────────────────────────────────────────────

def test_audit_logs_pagination():
    client, engine = _make_client()
    try:
        Session = sessionmaker(bind=engine)
        db = Session()
        from app.core.security import hash_password as hp
        from app.services.audit import AuditService
        admin = User(email="admin@al.com", full_name="Admin", hashed_password=hp("correct-horse"), role=UserRole.ADMIN)
        db.add(admin); db.commit()
        svc = AuditService(db)
        for i in range(5):
            svc.record(actor_id=admin.id, action=f"action_{i}", entity_type="request", entity_id=f"req-{i}")
        db.commit(); db.close()

        h = _headers(client, "admin@al.com")
        resp = client.get("/api/v1/audit-logs?page=1&page_size=2", headers=h)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 5
        assert body["total_pages"] == 3
        assert len(body["items"]) == 2
    finally:
        app.dependency_overrides.clear(); engine.dispose()
