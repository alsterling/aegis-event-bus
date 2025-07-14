# app/endpoints.py
import json, structlog, datetime as dt
from uuid import uuid4
from fastapi import APIRouter, Depends
import paho.mqtt.publish as mqtt_publish
from sqlmodel import Session, select

from .db import get_session
from .models import AuditLog
from . import schemas, security
from .archivist import create_job_folders, DATA_ROOT

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.get("/", tags=["Status"])
def read_root():
    return {"status": "Aegis Event Bus is online"}

@router.post("/job", response_model=schemas.Job, tags=["Jobs"])
def create_new_job(
    session: Session = Depends(get_session),
    current_user: dict = Depends(security.get_current_user),
):
    job_id = f"FC-{uuid4()}"
    create_job_folders(job_id, DATA_ROOT)

    entry = AuditLog(job_id=job_id, action="job.created")
    session.add(entry)
    session.commit()
    session.refresh(entry)

    try:
        mqtt_publish.single(
            "aegis/job/created",
            payload=json.dumps({"job_id": job_id, "timestamp": entry.timestamp.isoformat()}),
            hostname="mosquitto",
            port=1883,
        )
    except Exception as e:
        logger.warning("mqtt.publish_failed", job_id=job_id, err=str(e))

    return {"job_id": job_id}

@router.get("/jobs", response_model=list[schemas.AuditLog], tags=["Jobs"])
def list_recent_jobs(
    session: Session = Depends(get_session),
    limit: int = 20,
    current_user: dict = Depends(security.get_current_user),
):
    stmt = (
        select(AuditLog)
        .where(AuditLog.action == "job.created")
        .order_by(AuditLog.id.desc())
        .limit(limit)
    )
    return session.exec(stmt).all()
