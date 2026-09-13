from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import get_db
from app.main import app
import app.models as models  # noqa: F401


def test_employee_can_create_comment_on_and_cancel_own_pending_request():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine); Session = sessionmaker(bind=engine)
    def override_db():
        db = Session()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    try:
        payload = {"email": "employee@example.com", "full_name": "Employee User", "password": "correct-horse"}
        assert client.post("/api/v1/auth/register", json=payload).status_code == 201
        token = client.post("/api/v1/auth/login", data={"username": payload["email"], "password": payload["password"]}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        created = client.post("/api/v1/requests", headers=headers, json={"title": "Laptop replacement", "description": "The battery no longer holds charge."})
        assert created.status_code == 201
        request_id = created.json()["id"]
        assert client.get("/api/v1/requests", headers=headers).json()["items"][0]["id"] == request_id
        assert client.post(f"/api/v1/requests/{request_id}/comments", headers=headers, json={"body": "Asset tag: A-123"}).status_code == 201
        cancelled = client.post(f"/api/v1/requests/{request_id}/cancel", headers=headers)
        assert cancelled.status_code == 200 and cancelled.json()["status"] == "cancelled"
    finally:
        app.dependency_overrides.clear(); engine.dispose()
