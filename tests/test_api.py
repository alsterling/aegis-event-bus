# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app
from app.database import initialize_db, DB_PATH
import paho.mqtt.publish as mqtt_publish
import os

client = TestClient(app)

def setup_test_database():
    """A helper function to create a clean database for each test."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    initialize_db()

def test_read_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Aegis Event Bus is online"}

def test_create_and_list_job_workflow(monkeypatch):
    """Tests the full workflow of creating and then listing a job."""
    # Ensure a clean slate before this test runs
    setup_test_database()
    
    # Mock the MQTT publish call
    monkeypatch.setattr(mqtt_publish, "single", lambda *args, **kwargs: None)

    # Step 1: Create a new job
    r_create = client.post("/job")
    assert r_create.status_code == 200
    new_job_id = r_create.json()["job_id"]

    # Step 2: List jobs and verify the new job is present
    r_list = client.get("/jobs")
    assert r_list.status_code == 200
    jobs_list = r_list.json()
    assert len(jobs_list) == 1
    assert jobs_list[0]["job_id"] == new_job_id