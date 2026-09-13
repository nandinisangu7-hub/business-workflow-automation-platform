"""
Phase 1 test.

This is intentionally the only test for now — there is no domain logic to
test yet. Its job is to prove two things an interviewer might ask about:

1. The FastAPI app object imports cleanly (settings load, no circular
   imports between core/db/main).
2. The process actually serves an HTTP request end-to-end via TestClient,
   which drives the app the same way a real ASGI server would, without
   needing a running server or a database.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "service" in body


def test_openapi_schema_is_served():
    # If any router or schema is misconfigured, OpenAPI generation fails
    # loudly here rather than silently at /docs.
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"]
