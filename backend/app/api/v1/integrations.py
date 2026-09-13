"""
Integration endpoints — expose external API results to the frontend.

Currently: public holiday check for a given date.
The frontend uses this when a user sets a due_date on a request, to show
a warning if the date is a public holiday.
"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.api.v1.dependencies import get_current_user
from app.integrations.holidays import check_due_date_holiday
from app.models.user import User

router = APIRouter(prefix="/integrations", tags=["integrations"])


class HolidayCheckResponse(BaseModel):
    date: date
    country_code: str
    is_holiday: bool
    holiday_name: str | None
    api_available: bool


@router.get("/holiday-check", response_model=HolidayCheckResponse, summary="Check if a date is a public holiday")
def holiday_check(
    check_date: date = Query(..., description="Date to check in YYYY-MM-DD format"),
    country_code: str = Query(default="US", min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code"),
    _: User = Depends(get_current_user),
):
    """
    Check whether a given date is a public holiday in the specified country.
    Used by the frontend to warn users when setting due dates.
    Returns api_available=false if the external service is unreachable.
    """
    result = check_due_date_holiday(check_date, country_code)
    return HolidayCheckResponse(
        date=check_date,
        country_code=country_code,
        is_holiday=result.is_holiday,
        holiday_name=result.holiday_name,
        api_available=result.available,
    )
