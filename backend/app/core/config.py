"""
Centralized application configuration.

WHY THIS FILE EXISTS:
Every other module imports `settings` from here instead of calling
os.environ.get(...) directly. That gives us three things:
  1. One place to see every configurable value the app depends on.
  2. Type validation and coercion (e.g. ACCESS_TOKEN_EXPIRE_MINUTES is
     guaranteed to be an int, not a string that "looks like" a number).
  3. A single object (`settings`) that can be overridden in tests without
     touching real environment variables (see tests/conftest.py in a later
     phase).

Values are read from a `.env` file in local dev and from real environment
variables in Docker / CI / production. `.env` itself is git-ignored --
`.env.example` documents which keys must be set.
"""
from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    PROJECT_NAME: str = "Business Workflow Automation Platform"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # --- Security / Auth (used starting Phase 3) ---
    SECRET_KEY: str = "dev-only-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Database ---
    DATABASE_URL: str = "postgresql+psycopg2://workflow:workflow@localhost:5432/workflow_db"

    # --- CORS: which frontend origins may call this API ---
    # Annotated with NoDecode: by default, pydantic-settings tries to
    # JSON-decode any env var mapped to a list[str] field BEFORE our own
    # validator below ever runs -- so a plain comma-separated string like
    # Docker Compose passes (BACKEND_CORS_ORIGINS=http://a,http://b) fails
    # with a SettingsError before the CSV-splitting logic gets a chance to
    # handle it. NoDecode tells pydantic-settings to skip its own decoding
    # for this field and hand the raw string straight to our validator.
    # This bug only surfaces when the value actually comes from a real OS
    # environment variable (Docker/CI) -- not from a Python default or a
    # value set directly in a test -- which is exactly why it was not caught
    # until Docker Compose was actually run end-to-end.
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    # --- Pagination defaults (used starting Phase 4/10) ---
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # --- External API integration (Phase 8) ---
    # Set to False in tests/offline environments to skip real HTTP calls.
    HOLIDAY_API_ENABLED: bool = True
    # ISO 3166-1 alpha-2 country code for public holiday checks.
    HOLIDAY_COUNTRY_CODE: str = "US"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_csv_origins(cls, value):
        # Lets BACKEND_CORS_ORIGINS be set in .env as a comma-separated
        # string (BACKEND_CORS_ORIGINS=http://a.com,http://b.com) while
        # still accepting a real list if set programmatically (e.g. tests).
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Cached so the .env file is parsed once per process, not per import."""
    return Settings()


settings = get_settings()
