"""Tests for the external API integration (holiday check)."""
import pytest
from unittest.mock import patch, MagicMock

from app.integrations.holidays import check_due_date_holiday, HolidayCheckResult
from app.core.config import settings

from datetime import date


def test_holiday_check_disabled_returns_no_holiday(monkeypatch):
    """When HOLIDAY_API_ENABLED is False, no HTTP call is made and result is non-holiday."""
    monkeypatch.setattr(settings, "HOLIDAY_API_ENABLED", False)
    result = check_due_date_holiday(date(2025, 12, 25))
    assert result.is_holiday is False
    assert result.available is True


def test_holiday_check_detects_holiday(monkeypatch):
    """When the API returns a matching holiday, is_holiday is True."""
    monkeypatch.setattr(settings, "HOLIDAY_API_ENABLED", True)
    mock_holidays = [
        {"date": "2025-12-25", "localName": "Christmas Day", "name": "Christmas Day"},
        {"date": "2025-01-01", "localName": "New Year's Day", "name": "New Year's Day"},
    ]
    with patch("app.integrations.holidays._fetch_holidays", return_value=mock_holidays):
        result = check_due_date_holiday(date(2025, 12, 25), "US")
    assert result.is_holiday is True
    assert result.holiday_name == "Christmas Day"
    assert result.available is True


def test_holiday_check_non_holiday_date(monkeypatch):
    """A regular working day returns is_holiday=False."""
    monkeypatch.setattr(settings, "HOLIDAY_API_ENABLED", True)
    mock_holidays = [{"date": "2025-12-25", "localName": "Christmas Day", "name": "Christmas Day"}]
    with patch("app.integrations.holidays._fetch_holidays", return_value=mock_holidays):
        result = check_due_date_holiday(date(2025, 6, 15), "US")
    assert result.is_holiday is False
    assert result.available is True


def test_holiday_check_timeout_returns_unavailable(monkeypatch):
    """A timeout returns available=False without raising."""
    import httpx
    monkeypatch.setattr(settings, "HOLIDAY_API_ENABLED", True)
    with patch("app.integrations.holidays._fetch_holidays", side_effect=httpx.TimeoutException("timeout")):
        result = check_due_date_holiday(date(2025, 12, 25), "US")
    assert result.available is False
    assert result.is_holiday is False


def test_holiday_check_http_error_returns_unavailable(monkeypatch):
    """An HTTP error (e.g. 500) returns available=False without raising."""
    import httpx
    monkeypatch.setattr(settings, "HOLIDAY_API_ENABLED", True)
    mock_response = MagicMock()
    mock_response.status_code = 500
    with patch("app.integrations.holidays._fetch_holidays", side_effect=httpx.HTTPStatusError("error", request=MagicMock(), response=mock_response)):
        result = check_due_date_holiday(date(2025, 12, 25), "US")
    assert result.available is False


def test_holiday_api_endpoint_requires_auth():
    """The holiday check endpoint requires authentication."""
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/v1/integrations/holiday-check?check_date=2025-12-25")
    assert response.status_code == 401


def test_holiday_api_endpoint_returns_result(monkeypatch):
    """Authenticated request to holiday check returns correct shape."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from fastapi.testclient import TestClient
    from app.db.base import Base
    from app.db.session import get_db
    from app.main import app
    import app.models as _m  # noqa

    monkeypatch.setattr(settings, "HOLIDAY_API_ENABLED", False)

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    try:
        client.post("/api/v1/auth/register", json={"email": "u@example.com", "full_name": "User", "password": "correct-horse"})
        token = client.post("/api/v1/auth/login", data={"username": "u@example.com", "password": "correct-horse"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/api/v1/integrations/holiday-check?check_date=2025-12-25&country_code=US", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["date"] == "2025-12-25"
        assert body["country_code"] == "US"
        assert "is_holiday" in body
        assert "api_available" in body
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
