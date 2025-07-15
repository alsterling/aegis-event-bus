"""
Alembic migration environment.
Keeps DATABASE_URL in sync with .env and exposes SQLModel metadata.
"""

from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

load_dotenv()  # .env → env vars
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL not set")

# ——— Alembic config ————————————————————————————————————————————
config = context.config
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name:
    fileConfig(config.config_file_name)

# ——— Import models so Alembic can autogenerate ————————————
from sqlmodel import SQLModel  # noqa: E402

target_metadata = SQLModel.metadata
# ——————————————————————————————————————————————————————————————


def run_migrations_offline() -> None:
    """Run migrations without a DB connection (generates SQL)."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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
