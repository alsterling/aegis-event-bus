# app/endpoints.py
from fastapi import APIRouter, Depends
from uuid import uuid4
import datetime
import sqlite3
import json
import paho.mqtt.publish as mqtt_publish
import structlog

from .database import get_db_connection
from . import schemas
from .archivist import create_job_folders, DATA_ROOT

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.get("/", tags=["Status"])
def read_root():
    """A simple endpoint to check if the service is online."""
    return {"status": "Aegis Event Bus is online"}

@router.post("/job", response_model=schemas.Job, tags=["Jobs"])
def create_new_job(conn: sqlite3.Connection = Depends(get_db_connection)):
    """Creates a Job-ID, folder, DB log, and publishes an MQTT event."""
    logger.info("job.create.started")
    job_id = f"FC-{uuid4()}"
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    
    create_job_folders(job_id=job_id, base_path=DATA_ROOT)
    logger.info("job.folders.created", job_id=job_id)
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO audit_log (job_id, action, timestamp) VALUES (?, ?, ?)",
            (job_id, "job.created", timestamp)
        )
        conn.commit()
        logger.info("job.db.logged", job_id=job_id)
    except Exception as e:
        conn.rollback()
        logger.error("job.db.log_failed", job_id=job_id, error=str(e))
        raise e
    
    event_payload = {"job_id": job_id, "timestamp": timestamp}
    try:
        mqtt_publish.single(
            topic="aegis/job/created",
            payload=json.dumps(event_payload),
            hostname="localhost",
            port=1883
        )
        logger.info("job.event.published", job_id=job_id)
    except Exception as e:
        logger.warning("job.event.publish_failed", job_id=job_id, error=str(e))

    # This line is now correctly indented to be inside the function
    logger.info("job.created.success", job_id=job_id)
    return {"job_id": job_id}

@router.get("/jobs", tags=["Jobs"])
def list_recent_jobs(conn: sqlite3.Connection = Depends(get_db_connection), limit: int = 20):
    """Returns a list of the most recent jobs from the audit log."""
    logger.info("jobs.list.requested", limit=limit)
    cursor = conn.cursor()
    try:
        rows = cursor.execute(
            "SELECT job_id, timestamp FROM audit_log WHERE action='job.created' ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()