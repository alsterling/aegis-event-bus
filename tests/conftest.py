# tests/conftest.py  — final working snippet
import os
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool          # ← added
from app import models                          # registers AuditLog
import app.db as db
from app.main import app

# ---------- shared in-memory engine ----------
engine = create_engine(
    "sqlite://",                                # positional arg first
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,                       # one global connection
)
db.engine = engine                              # app uses this engine
# ---------------------------------------------

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    db.get_session = lambda: session
    yield TestClient(app)
