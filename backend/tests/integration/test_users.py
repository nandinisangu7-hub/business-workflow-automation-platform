"""Integration tests for the users management API."""
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


def _token(client, email):
    return client.post("/api/v1/auth/login", data={"username": email, "password": "correct-horse"}).json()["access_token"]


def _headers(client, email):
    return {"Authorization": f"Bearer {_token(client, email)}"}


def test_admin_can_list_all_users():
    client, db, engine = _setup()
    try:
        admin = User(email="admin@u.com", full_name="Admin", hashed_password=hash_password("correct-horse"), role=UserRole.ADMIN)
        emp = User(email="emp@u.com", full_name="Emp", hashed_password=hash_password("correct-horse"), role=UserRole.EMPLOYEE)
        db.add_all([admin, emp]); db.commit()

        resp = client.get("/api/v1/users", headers=_headers(client, "admin@u.com"))
        assert resp.status_code == 200
        emails = [u["email"] for u in resp.json()["items"]]
        assert "admin@u.com" in emails
        assert "emp@u.com" in emails
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_employee_cannot_list_users():
    client, db, engine = _setup()
    try:
        db.add(User(email="emp2@u.com", full_name="Emp", hashed_password=hash_password("correct-horse"), role=UserRole.EMPLOYEE))
        db.commit()
        resp = client.get("/api/v1/users", headers=_headers(client, "emp2@u.com"))
        assert resp.status_code == 403
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_user_can_get_own_profile():
    client, db, engine = _setup()
    try:
        emp = User(email="self@u.com", full_name="Self", hashed_password=hash_password("correct-horse"), role=UserRole.EMPLOYEE)
        db.add(emp); db.commit()

        h = _headers(client, "self@u.com")
        resp = client.get(f"/api/v1/users/{emp.id}", headers=h)
        assert resp.status_code == 200
        assert resp.json()["email"] == "self@u.com"
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_employee_cannot_get_other_user_profile():
    client, db, engine = _setup()
    try:
        emp = User(email="emp3@u.com", full_name="Emp3", hashed_password=hash_password("correct-horse"), role=UserRole.EMPLOYEE)
        other = User(email="other2@u.com", full_name="Other", hashed_password=hash_password("correct-horse"), role=UserRole.EMPLOYEE)
        db.add_all([emp, other]); db.commit()

        h = _headers(client, "emp3@u.com")
        resp = client.get(f"/api/v1/users/{other.id}", headers=h)
        assert resp.status_code == 403
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_admin_can_patch_user_role():
    client, db, engine = _setup()
    try:
        admin = User(email="admin2@u.com", full_name="Admin2", hashed_password=hash_password("correct-horse"), role=UserRole.ADMIN)
        emp = User(email="promote@u.com", full_name="Promote", hashed_password=hash_password("correct-horse"), role=UserRole.EMPLOYEE)
        db.add_all([admin, emp]); db.commit()

        resp = client.patch(
            f"/api/v1/users/{emp.id}",
            headers=_headers(client, "admin2@u.com"),
            json={"role": "manager"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "manager"
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_non_admin_cannot_patch_user():
    client, db, engine = _setup()
    try:
        mgr = User(email="mgr@u.com", full_name="Mgr", hashed_password=hash_password("correct-horse"), role=UserRole.MANAGER)
        emp = User(email="target@u.com", full_name="Target", hashed_password=hash_password("correct-horse"), role=UserRole.EMPLOYEE)
        db.add_all([mgr, emp]); db.commit()

        resp = client.patch(
            f"/api/v1/users/{emp.id}",
            headers=_headers(client, "mgr@u.com"),
            json={"role": "admin"},
        )
        assert resp.status_code == 403
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()


def test_get_nonexistent_user_returns_404():
    client, db, engine = _setup()
    try:
        admin = User(email="admin3@u.com", full_name="Admin3", hashed_password=hash_password("correct-horse"), role=UserRole.ADMIN)
        db.add(admin); db.commit()

        import uuid
        resp = client.get(f"/api/v1/users/{uuid.uuid4()}", headers=_headers(client, "admin3@u.com"))
        assert resp.status_code == 404
    finally:
        db.close(); app.dependency_overrides.clear(); engine.dispose()
