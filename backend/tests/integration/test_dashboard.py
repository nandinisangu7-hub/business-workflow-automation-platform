"""Integration tests for the dashboard summary endpoint."""
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


def _setup():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    shared_db = Session()
    app.dependency_overrides[get_db] = lambda: (yield shared_db)
    return TestClient(app), shared_db, engine


def _token(client, email, password="correct-horse"):
    return client.post("/api/v1/auth/login", data={"username": email, "password": password}).json()["access_token"]


def _headers(client, email):
    return {"Authorization": f"Bearer {_token(client, email)}"}


def test_dashboard_summary_shape():
    client, db, engine = _setup()
    try:
        db.add(User(email="emp@d.com", full_name="Emp", hashed_password=hash_password("correct-horse"), role=UserRole.EMPLOYEE))
        db.commit()
        resp = client.get("/api/v1/dashboard/summary", headers=_headers(client, "emp@d.com"))
        assert resp.status_code == 200
        body = resp.json()
        for key in ("total", "pending", "assigned", "in_progress", "approved", "rejected", "completed", "cancelled"):
            assert key in body
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_dashboard_employee_only_sees_own_requests():
    # Use per-call session (same pattern as test_auth) so API writes are visible
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    def override_db():
        db = Session()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    try:
        client.post("/api/v1/auth/register", json={"email": "emp2@d.com", "full_name": "Emp2", "password": "correct-horse"})
        client.post("/api/v1/auth/register", json={"email": "other@d.com", "full_name": "Other", "password": "correct-horse"})

        emp_h = _headers(client, "emp2@d.com")
        other_h = _headers(client, "other@d.com")

        r1 = client.post("/api/v1/requests", headers=emp_h, json={"title": "Request One", "description": "Description one"})
        r2 = client.post("/api/v1/requests", headers=emp_h, json={"title": "Request Two", "description": "Description two"})
        r3 = client.post("/api/v1/requests", headers=other_h, json={"title": "Request Three", "description": "Description three"})
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r3.status_code == 201

        summary = client.get("/api/v1/dashboard/summary", headers=emp_h).json()
        assert summary["total"] == 2
        assert summary["pending"] == 2
        assert summary["pending"] == 2
    finally:
        app.dependency_overrides.clear(); engine.dispose()


def test_dashboard_requires_auth():
    client, db, engine = _setup()
    try:
        assert client.get("/api/v1/dashboard/summary").status_code == 401
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()
