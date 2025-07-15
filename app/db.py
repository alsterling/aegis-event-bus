# app/db.py
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "sqlite:///eventbus.db")
IS_SQLITE = DB_URL.startswith("sqlite")

engine = create_engine(
    DB_URL,
    echo=False,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
)


def init_db() -> None:
    """Create tables only for SQLite.  In Postgres we rely on Alembic."""
    if IS_SQLITE:
        SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
