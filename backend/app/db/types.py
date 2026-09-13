"""
A UUID column type that works on both PostgreSQL (production/Docker) and
SQLite (fast in-memory unit tests).

WHY THIS EXISTS:
SQLAlchemy's dialect-specific `postgresql.UUID` only exists for Postgres.
If models imported that directly, every test would need a real Postgres
instance to run — which defeats the purpose of fast, isolated unit tests.

This TypeDecorator stores a genuine PostgreSQL UUID column when the engine
is Postgres, and transparently falls back to a 36-character string
(the standard hyphenated UUID text form) on SQLite, converting to/from
Python's `uuid.UUID` either way. Application code never needs to know
which database it's talking to — it always works with `uuid.UUID` objects.

This is a well-known SQLAlchemy recipe, not a novel invention; documented
here at github.com/sqlalchemy/sqlalchemy under "Backend-agnostic GUID Type".
"""
import uuid

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value
