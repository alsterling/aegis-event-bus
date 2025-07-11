# app/endpoints.py
from fastapi import APIRouter, Depends
from uuid import uuid4
import datetime
import json
import paho.mqtt.publish as mqtt_publish
import structlog
from sqlalchemy.orm import Session

# Import get_db (the SQLAlchemy session dependency)
from .database import get_db
from . import schemas, models
from .archivist import create_job_folders, DATA_ROOT

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.get("/", tags=["Status"])
def read_root():
    return {"status": "Aegis Event Bus is online"}

@router.post("/job", response_model=schemas.Job, tags=["Jobs"])
def create_new_job(db: Session = Depends(get_db)):
    job_id = f"FC-{uuid4()}"
    # SQLAlchemy expects datetime objects, not strings
    timestamp = datetime.datetime.now(datetime.UTC)
    
    create_job_folders(job_id=job_id, base_path=DATA_ROOT)
    
    # Use SQLAlchemy ORM instead of raw SQL
    new_log = models.AuditLog(
        job_id=job_id,
        action="job.created",
        timestamp=timestamp
    )
    db.add(new_log)
    db.commit() # Saves the new log to the database
    
    try:
        # Convert timestamp to string ISO format for the MQTT payload
        event_payload = {"job_id": job_id, "timestamp": timestamp.isoformat()}
        mqtt_publish.single(
            topic="aegis/job/created",
            payload=json.dumps(event_payload),
            hostname="localhost", port=1883
        )
    except Exception as e:
        logger.warning("job.event.publish_failed", error=str(e))

    return {"job_id": job_id}

@router.get("/jobs", tags=["Jobs"])
def list_recent_jobs(db: Session = Depends(get_db), limit: int = 20):
    # Use SQLAlchemy ORM query
    jobs = db.query(models.AuditLog).filter(
        models.AuditLog.action == "job.created"
    ).order_by(models.AuditLog.id.desc()).limit(limit).all()
    return jobs