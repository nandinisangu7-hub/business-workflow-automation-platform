"""
Database connectivity.

`engine` is the single, process-wide connection pool to PostgreSQL.
`get_db()` is a FastAPI dependency: for every incoming request, FastAPI
calls this generator, hands the yielded Session to the route (or, from
Phase 2 onward, to whatever repository the route delegates to), and then
runs the `finally` block to close the session — even if the request raised
an exception. This is the standard SQLAlchemy + FastAPI request-scoped
session pattern.

`pool_pre_ping=True` makes the pool test a connection before handing it
out, so a database restart (common in local Docker dev) doesn't surface as
a confusing "connection already closed" error on the next request.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
