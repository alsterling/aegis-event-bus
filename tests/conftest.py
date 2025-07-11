# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.database import get_db, Base # Import Base from your database module

# Use an in-memory SQLite database for tests. Using a file ensures it persists
# across requests within the same test function if needed.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    # This is the crucial fix: It creates the tables in the test database
    # BEFORE the test runs.
    Base.metadata.create_all(bind=engine)
    
    # This function provides the clean test database session to the app
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    # Apply the override
    app.dependency_overrides[get_db] = override_get_db
    
    # Provide the test client for the test to use
    yield TestClient(app)
    
    # Clean up after the test: Clear the override and drop all tables
    # so the next test starts with a completely clean slate.
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)