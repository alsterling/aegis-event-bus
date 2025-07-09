# app/endpoints.py
from fastapi import APIRouter, Depends
from uuid import uuid4
import datetime
import json
import paho.mqtt.publish as mqtt_publish
import sqlite3
from .database import get_db_connection
from . import schemas
from .archivist import create_job_folders, DATA_ROOT

# This is the router that will hold all our API endpoints
router = APIRouter()

@router.get("/", tags=["Status"])
def read_root():
    """A simple endpoint to check if the service is online."""
    return {"status": "Aegis Event Bus is online"}

@router.post("/job", response_model=schemas.Job, tags=["Jobs"])
def create_new_job(conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Creates a new Job-ID, creates its folder structure, logs it to the
    database, and publishes a "job.created" event to the MQTT broker.
    """
    job_id = f"FC-{uuid4()}"
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    
    # --- Step 1: Create the physical folder structure ---
    # This call is now correct, passing the required base_path.
    create_job_folders(job_id=job_id, base_path=DATA_ROOT)
    
    # --- Step 2: Log the job to the audit database ---
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO audit_log (job_id, action, timestamp) VALUES (?, ?, ?)",
            (job_id, "job.created", timestamp)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
        
    # --- Step 3: Publish the event to the MQTT broker ---
    event_payload = { "job_id": job_id, "timestamp": timestamp }
    try:
        mqtt_publish.single(
            topic="aegis/job/created",
            payload=json.dumps(event_payload),
            hostname="localhost",
            port=1883
        )
    except Exception as e:
        # If MQTT fails, we don't want the whole request to fail.
        # We just print a warning to the server logs.
        print(f"WARNING: Could not publish to MQTT broker. Error: {e}")

    return {"job_id": job_id}

@router.get("/jobs", tags=["Jobs"])
def list_recent_jobs(limit: int = 20):
    """Returns a list of the most recent jobs from the audit log."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT job_id, timestamp FROM audit_log "
            "WHERE action='job.created' ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        # Convert the database rows into a list of dictionaries
        return [dict(row) for row in rows]
    finally:
        conn.close()