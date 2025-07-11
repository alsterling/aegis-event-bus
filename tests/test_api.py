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
    """
    Tests the full workflow of creating and then listing a job
    by first logging in to get an access token.
    """
    # Step 1: Log in to get a token
    login_data = {"username": "testuser", "password": "testpassword"}
    r_token = client.post("/token", data=login_data)
    assert r_token.status_code == 200
    access_token = r_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Mock the MQTT publish call
    monkeypatch.setattr(mqtt_publish, "single", lambda *args, **kwargs: None)

    # Step 2: Create a new job using the token
    r_create = client.post("/job", headers=headers)
    assert r_create.status_code == 200
    new_job_id = r_create.json()["job_id"]

    # Step 3: List jobs using the token and verify the new job is present
    r_list = client.get("/jobs", headers=headers)
    assert r_list.status_code == 200
    jobs_list = r_list.json()
    assert len(jobs_list) == 1
    assert jobs_list[0]["job_id"] == new_job_id

def test_create_job_fails_without_auth(client: TestClient):
    """Tests that POST /job returns a 401 Unauthorized error without a token."""
    response = client.post("/job")
    assert response.status_code == 401

def test_list_jobs_fails_without_auth(client: TestClient):
    """Tests that GET /jobs returns a 401 Unauthorized error without a token."""
    response = client.get("/jobs")
    assert response.status_code == 401

def test_login_and_use_protected_endpoint(client: TestClient):
    """Tests the full login flow and accessing a protected route."""
    # Step 1: Log in to get a token
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    # Note: we use `data=` for form data, not `json=`
    r_token = client.post("/token", data=login_data)
    assert r_token.status_code == 200
    token_data = r_token.json()
    assert "access_token" in token_data

    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 2: Use the token to access the protected /jobs endpoint
    r_jobs = client.get("/jobs", headers=headers)
    assert r_jobs.status_code == 200