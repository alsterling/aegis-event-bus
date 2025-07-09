# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db_connection
import paho.mqtt.publish as mqtt_publish
import sqlite3

# This is our test database fixture from conftest.py
# We are telling the app: "For these tests, whenever someone asks for get_db_connection,
# give them this test_db_conn instead."
def get_test_db_connection():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE audit_log (
      id        INTEGER PRIMARY KEY AUTOINCREMENT,
      job_id    TEXT NOT NULL,
      action    TEXT NOT NULL,
      timestamp TEXT NOT NULL
    )""")
    conn.commit()
    return conn

app.dependency_overrides[get_db_connection] = get_test_db_connection

client = TestClient(app)

def test_read_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Aegis Event Bus is online"}

def test_create_and_list_job_workflow(monkeypatch):
    monkeypatch.setattr(mqtt_publish, "single", lambda *args, **kwargs: None)

    r_create = client.post("/job")
    assert r_create.status_code == 200
    new_job_id = r_create.json()["job_id"]

    r_list = client.get("/jobs")
    assert r_list.status_code == 200
    jobs_list = r_list.json()
    assert new_job_id in [job["job_id"] for job in jobs_list]