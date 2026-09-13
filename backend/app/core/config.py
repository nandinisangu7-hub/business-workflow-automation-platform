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
variables in Docker / CI / production. `.env` itself is git-ignored —
`.env.example` documents which keys must be set.
"""
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # --- Pagination defaults (used starting Phase 4/10) ---
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

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
