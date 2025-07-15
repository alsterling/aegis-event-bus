# tests/test_pagination.py
from fastapi.testclient import TestClient
import paho.mqtt.publish as mqtt_publish
from sqlmodel import Session, delete
from app.models import AuditLog


def _login_and_get_headers(client: TestClient):
    """Helper function to log in and get auth headers."""
    data = {"username": "testuser", "password": "testpassword"}
    token = client.post("/token", data=data).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_jobs_pagination(client: TestClient, session: Session, monkeypatch):
    """Tests that the /jobs endpoint correctly paginates results."""
    headers = _login_and_get_headers(client)
    monkeypatch.setattr(mqtt_publish, "single", lambda *a, **k: None)

    # Clean the DB and create 3 new jobs
    session.exec(delete(AuditLog))
    session.commit()
    for _ in range(3):
        client.post("/job", headers=headers)

    # --- Test First Page ---
    page1_response = client.get("/jobs?limit=2", headers=headers)
    assert page1_response.status_code == 200
    page1 = page1_response.json()

    assert len(page1["items"]) == 2
    assert page1["next_cursor"] is not None
    assert page1["items"][0]["id"] == 3  # Should be the newest job
    assert page1["items"][1]["id"] == 2

    # --- Test Second Page ---
    cursor = page1["next_cursor"]
    page2_response = client.get(f"/jobs?limit=2&cursor={cursor}", headers=headers)
    assert page2_response.status_code == 200
    page2 = page2_response.json()

    assert len(page2["items"]) == 1  # Only one job left
    assert page2["next_cursor"] is None  # Should be the last page
    assert page2["items"][0]["id"] == 1
