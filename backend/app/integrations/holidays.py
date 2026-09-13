"""
Public Holiday Integration — Nager.Date API

WHY THIS INTEGRATION:
When a manager sets a due date on a request, it's useful to know if that
date falls on a public holiday (the assignee won't be working). This
integration calls the free, no-auth-required Nager.Date API to check.

WHAT THIS DEMONSTRATES:
- HTTP client with timeout
- Response validation
- Error handling (timeout, HTTP errors, malformed JSON)
- Logging of integration failures
- Configuration via environment variables (country code)
- A mock/fallback path for tests (HOLIDAY_API_ENABLED=false)
- Clean separation: this module is never imported by route handlers directly

API: https://date.nager.at/api/v3/PublicHolidays/{year}/{countryCode}
No API key required. Rate limit: reasonable for internal use.

INTERVIEW TALKING POINTS:
- Why not call this from the route handler? Because route handlers should
  only parse HTTP and delegate — mixing external API calls there makes
  routes hard to test and violates single responsibility.
- Why httpx? It's already in requirements.txt (used by pytest/HTTPX tests)
  and supports both sync and async. We use sync here to keep the service
  layer synchronous, consistent with the rest of the codebase.
- What if the API is down? We log the failure and return an empty list —
  the request workflow continues normally. A holiday check is advisory,
  not a hard gate.
"""
import logging
from datetime import date
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_BASE_URL = "https://date.nager.at/api/v3"
_TIMEOUT_SECONDS = 5.0


class HolidayCheckResult:
    def __init__(self, is_holiday: bool, holiday_name: str | None, available: bool):
        self.is_holiday = is_holiday
        self.holiday_name = holiday_name
        self.available = available  # False when the API call failed


def _fetch_holidays(year: int, country_code: str) -> list[dict[str, Any]]:
    """Fetch public holidays for a given year and country. Raises on failure."""
    url = f"{_BASE_URL}/PublicHolidays/{year}/{country_code}"
    with httpx.Client(timeout=_TIMEOUT_SECONDS) as client:
        response = client.get(url)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise ValueError(f"Unexpected response shape from holiday API: {type(data)}")
        return data


def check_due_date_holiday(due_date: date, country_code: str | None = None) -> HolidayCheckResult:
    """
    Check whether `due_date` is a public holiday in the configured country.

    Returns HolidayCheckResult with:
      - is_holiday: True if the date is a public holiday
      - holiday_name: the holiday's name if is_holiday is True
      - available: False if the API call failed (caller should treat as advisory)
    """
    if not settings.HOLIDAY_API_ENABLED:
        # Test/offline mode: skip the real API call
        return HolidayCheckResult(is_holiday=False, holiday_name=None, available=True)

    effective_country = country_code or settings.HOLIDAY_COUNTRY_CODE
    try:
        holidays = _fetch_holidays(due_date.year, effective_country)
    except httpx.TimeoutException:
        logger.warning("Holiday API timed out for %s/%s", due_date.year, effective_country)
        return HolidayCheckResult(is_holiday=False, holiday_name=None, available=False)
    except httpx.HTTPStatusError as exc:
        logger.warning("Holiday API returned HTTP %s for %s/%s", exc.response.status_code, due_date.year, effective_country)
        return HolidayCheckResult(is_holiday=False, holiday_name=None, available=False)
    except (ValueError, Exception) as exc:
        logger.warning("Holiday API integration error: %s", exc)
        return HolidayCheckResult(is_holiday=False, holiday_name=None, available=False)

    due_str = due_date.isoformat()
    for holiday in holidays:
        if isinstance(holiday, dict) and holiday.get("date") == due_str:
            return HolidayCheckResult(is_holiday=True, holiday_name=holiday.get("localName"), available=True)

    return HolidayCheckResult(is_holiday=False, holiday_name=None, available=True)
