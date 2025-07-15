# tests/test_api.py
from fastapi.testclient import TestClient
import paho.mqtt.publish as mqtt_publish
from sqlmodel import Session, select

from app.models import AuditLog


def test_read_root_endpoint(client: TestClient):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "Aegis Event Bus is online"}


def test_unauthenticated_routes(client: TestClient):
    assert client.post("/job").status_code == 401
    assert client.get("/jobs").status_code == 401


def test_auth_and_workflow(monkeypatch, client: TestClient, session: Session):
    # ── 1. obtain JWT ─────────────────────────────────────────────
    token = client.post(
        "/token", data={"username": "testuser", "password": "testpassword"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ── 2. suppress real MQTT publish ────────────────────────────
    monkeypatch.setattr(mqtt_publish, "single", lambda *a, **k: None)

    # ── 3. create a job ──────────────────────────────────────────
    job_id = client.post("/job", headers=headers).json()["job_id"]

    # ── 4. verify row in DB via SQLModel ─────────────────────────
    db_row = session.exec(select(AuditLog).where(AuditLog.job_id == job_id)).one()
    assert db_row.action == "job.created"

    # ── 5. list jobs & confirm ──────────────────────────────────
    jobs_page = client.get("/jobs", headers=headers).json()
    assert jobs_page["items"][0]["job_id"] == job_id
