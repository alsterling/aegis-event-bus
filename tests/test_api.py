# tests/test_api.py
from fastapi.testclient import TestClient
import paho.mqtt.publish as mqtt_publish
from sqlmodel import Session, select
from app.models import AuditLog


def test_read_root_endpoint(client: TestClient):
    assert client.get("/").status_code == 200


def test_unauthenticated_routes(client: TestClient):
    assert client.post("/job").status_code == 401
    assert client.get("/jobs").status_code == 401


def test_auth_and_workflow(monkeypatch, client: TestClient, session: Session):
    token = client.post(
        "/token", data={"username": "testuser", "password": "testpassword"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    monkeypatch.setattr(mqtt_publish, "single", lambda *a, **k: None)
    job_id = client.post("/job", headers=headers).json()["job_id"]

    db_row = session.exec(select(AuditLog).where(AuditLog.job_id == job_id)).one()
    assert db_row.action == "job.created"

    jobs = client.get("/jobs", headers=headers).json()
    assert jobs[0]["job_id"] == job_id
