# tests/test_api.py
from fastapi.testclient import TestClient
import paho.mqtt.publish as mqtt_publish

# We rely on the 'client' fixture provided automatically by conftest.py

def test_read_root_endpoint(client: TestClient):
    """Tests if the main GET / endpoint is working."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Aegis Event Bus is online"}

def test_create_and_list_job_workflow(monkeypatch, client: TestClient):
    """Tests creating a job and then seeing it in the jobs list."""
    
    # Mock the MQTT publish call
    monkeypatch.setattr(mqtt_publish, "single", lambda *args, **kwargs: None)

    # Step 1: Create a job
    r_create = client.post("/job")
    assert r_create.status_code == 200
    new_job_id = r_create.json()["job_id"]

    # Step 2: List jobs and verify the new job is there
    r_list = client.get("/jobs")
    assert r_list.status_code == 200
    jobs_list = r_list.json()
    
    # Since we are using SQLAlchemy, the response is a list of objects, 
    # so we access attributes directly, not keys.
    assert len(jobs_list) == 1
    assert jobs_list[0]['job_id'] == new_job_id