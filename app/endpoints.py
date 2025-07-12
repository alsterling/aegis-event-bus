# app/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import sqlite3
from uuid import uuid4
import datetime
import json
import paho.mqtt.publish as mqtt_publish
import structlog

from .database import get_db_connection
from . import schemas, security
from .archivist import create_job_folders, DATA_ROOT

# Initialize the logger for this file
logger = structlog.get_logger(__name__)
router = APIRouter()

@router.post("/token", tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = security.get_user(form_data.username)
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = datetime.timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/", tags=["Status"])
def read_root():
    """A simple endpoint to check if the service is online."""
    logger.info("status.checked", endpoint="/")
    return {"status": "Aegis Event Bus is online"}

@router.post("/job", response_model=schemas.Job, tags=["Jobs"])
def create_new_job(current_user: dict = Depends(security.get_current_user)):
    """Creates a Job-ID, folder, DB log, and publishes an MQTT event."""
    logger.info("job.create.started")
    job_id = f"FC-{uuid4()}"
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    
    create_job_folders(job_id=job_id, base_path=DATA_ROOT)
    logger.info("job.folders.created", job_id=job_id)
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
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
    finally:
        conn.close()
    
    event_payload = {"job_id": job_id, "timestamp": timestamp}
    try:
        mqtt_publish.single(
            topic="aegis/job/created",
            payload=json.dumps(event_payload),
            hostname="localhost", port=1883
        )
        logger.info("job.event.published", job_id=job_id)
    except Exception as e:
        logger.warning("job.event.publish_failed", job_id=job_id, error=str(e))
        
    logger.info("job.create.success", job_id=job_id)
    return {"job_id": job_id}

@router.get("/jobs", tags=["Jobs"])
def list_recent_jobs(limit: int = 20, current_user: dict = Depends(security.get_current_user)):
    """Returns a list of the most recent jobs from the audit log."""
    logger.info("jobs.list.requested", limit=limit)
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        sql_query = "SELECT * FROM audit_log WHERE action='job.created' ORDER BY id DESC LIMIT ?"
        rows = cursor.execute(sql_query, (limit,)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()