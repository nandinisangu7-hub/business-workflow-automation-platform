"""
Shared pytest fixtures for backend tests.

WHY IN-MEMORY SQLITE HERE, WHEN THE APP USES POSTGRES:
Unit tests for model behavior (relationships, constraints, defaults)
don't need a real Postgres server — they need a database that enforces
the same *relational* rules (foreign keys, uniqueness) fast enough to run
hundreds of times per second. An in-memory SQLite database, created fresh
per test function, gives full isolation (no test can see another test's
data) with effectively zero setup cost.

The trade-off, stated plainly: SQLite does NOT enforce everything
Postgres does out of the box (foreign keys are off by default — enabled
below — and it has no native ENUM type, no native UUID type). That's
exactly why `app/db/types.py`'s GUID type exists, and why Phase 12's
Docker Compose will also stand up integration tests against a real
Postgres container before this project is considered done. Unit tests
here answer "is my ORM model and relationship logic correct?" — a
separate, later suite answers "does this behave identically on the real
database engine?"
"""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
import app.models  # noqa: F401  — populate Base.metadata with every table


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _):
    # SQLite ignores FOREIGN KEY constraints unless this pragma is set on
    # every new connection. Without it, tests that check "does deleting a
    # referenced row fail?" would pass for the wrong reason.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
