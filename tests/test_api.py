# tests/test_api.py

from fastapi.testclient import TestClient
from app.main import app
import paho.mqtt.publish as mqtt_publish

client = TestClient(app)

def test_read_root_endpoint():
    """Tests if the main GET / endpoint is working."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Aegis Event Bus is online"}

def test_create_and_list_job_workflow(monkeypatch):
    """
    Tests the full workflow:
    1. A job is created successfully via POST /job.
    2. The new job appears in the list from GET /jobs.
    """
    # Mock the MQTT publish call to prevent real network requests during tests
    monkeypatch.setattr(mqtt_publish, "single", lambda *args, **kwargs: None)

    # Step 1: Create a new job
    r_create = client.post("/job")
    assert r_create.status_code == 200
    data = r_create.json()
    assert "job_id" in data
    new_job_id = data["job_id"]

    # Step 2: List jobs and verify the new job is present
    r_list = client.get("/jobs")
    assert r_list.status_code == 200
    jobs_list = r_list.json()
    assert isinstance(jobs_list, list)
    assert len(jobs_list) > 0
    # Check if our new job_id is in the list of returned jobs
    assert new_job_id in [job["job_id"] for job in jobs_list]