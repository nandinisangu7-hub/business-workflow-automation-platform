"""
Alembic's environment script.

Two things worth an interviewer's attention here:

1. `target_metadata = Base.metadata`, and `app.models` is imported before
   that line runs. This is what lets `alembic revision --autogenerate`
   compare the live database schema against your SQLAlchemy models and
   generate a diff — without the import, autogenerate would see an empty
   metadata object and think every table needs to be dropped.

2. The database URL comes from `app.core.config.settings.DATABASE_URL`,
   not from a hardcoded value in alembic.ini. That means migrations always
   run against whatever database the app itself is configured to use
   (same env var, same .env file) — dev, CI, and production migrations
   all go through the same config path as the app, which is the whole
   point of centralizing settings in Phase 1.
"""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.base import Base

# Import every model module so Base.metadata is fully populated before
# Alembic inspects it (see app/models/__init__.py docstring for why).
import app.models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate SQL scripts without a live DB connection (`alembic upgrade --sql`)."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection — the normal path."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
