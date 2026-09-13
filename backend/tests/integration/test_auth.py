from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.dependencies import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models.enums import UserRole
from app.models.user import User
import app.models as models  # noqa: F401


def make_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    def override_db():
        db = Session()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override_db
    return TestClient(app), Session, engine


def test_register_login_and_me():
    client, _, engine = make_client()
    try:
        registered = client.post("/api/v1/auth/register", json={"email": "new@example.com", "full_name": "New User", "password": "correct-horse"})
        assert registered.status_code == 201
        assert "hashed_password" not in registered.json()
        login = client.post("/api/v1/auth/login", data={"username": "new@example.com", "password": "correct-horse"})
        assert login.status_code == 200
        me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
        assert me.status_code == 200
        assert me.json()["email"] == "new@example.com"
    finally:
        app.dependency_overrides.clear(); engine.dispose()


def test_invalid_credentials_and_duplicate_email_are_rejected():
    client, _, engine = make_client()
    try:
        payload = {"email": "duplicate@example.com", "full_name": "Duplicate User", "password": "correct-horse"}
        assert client.post("/api/v1/auth/register", json=payload).status_code == 201
        assert client.post("/api/v1/auth/register", json=payload).status_code == 409
        assert client.post("/api/v1/auth/login", data={"username": payload["email"], "password": "wrong-password"}).status_code == 401
    finally:
        app.dependency_overrides.clear(); engine.dispose()
