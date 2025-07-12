# tests/test_api.py
from fastapi.testclient import TestClient
import paho.mqtt.publish as mqtt_publish
from app.main import app
from app.database import initialize_db, DB_PATH
import os

client = TestClient(app)

def setup_test_database():
    """A helper function to create a clean database for each test."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    initialize_db()

def test_read_root_endpoint():
    """Tests the public root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Aegis Event Bus is online"}

def test_create_job_fails_without_auth():
    """Tests that POST /job returns 401 Unauthorized without a token."""
    setup_test_database()
    response = client.post("/job")
    assert response.status_code == 401

def test_list_jobs_fails_without_auth():
    """Tests that GET /jobs returns 401 Unauthorized without a token."""
    setup_test_database()
    response = client.get("/jobs")
    assert response.status_code == 401

def test_login_and_use_protected_endpoints(monkeypatch):
    """Tests the full login flow and accessing protected routes."""
    setup_test_database()
    monkeypatch.setattr(mqtt_publish, "single", lambda *args, **kwargs: None)

    # Step 1: Log in to get a token
    login_data = {"username": "testuser", "password": "testpassword"}
    r_token = client.post("/token", data=login_data)
    assert r_token.status_code == 200
    token_data = r_token.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 2: Use the token to create a job
    r_create = client.post("/job", headers=headers)
    assert r_create.status_code == 200
    new_job_id = r_create.json()["job_id"]

    # Step 3: Use the token to list jobs and verify the new job is present
    r_list = client.get("/jobs", headers=headers)
    assert r_list.status_code == 200
    jobs_list = r_list.json()
    assert len(jobs_list) == 1
    assert jobs_list[0]["job_id"] == new_job_id