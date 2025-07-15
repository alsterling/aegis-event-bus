# app/endpoints.py
from fastapi import APIRouter, Depends, Query
from uuid import uuid4
import json
import structlog
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
    create_job_folders(job_id=job_id, base_path=DATA_ROOT)

    with session:
        entry = AuditLog(job_id=job_id, action="job.created")
        session.add(entry)
        session.commit()
        session.refresh(entry)

    try:
        event_payload = {"job_id": job_id, "timestamp": entry.timestamp.isoformat()}
        mqtt_publish.single(
            "aegis/job/created",
            payload=json.dumps(event_payload),
            hostname="mosquitto",
            port=1883,
        )
    except Exception as e:
        logger.warning("mqtt.publish_failed", job_id=job_id, err=str(e))

    return {"job_id": job_id}


@router.get("/jobs", response_model=schemas.JobsPage, tags=["Jobs"])
def list_recent_jobs(
    session: Session = Depends(get_session),
    cursor: int | None = Query(
        default=None, description="ID of the last row from the previous page"
    ),
    limit: int = Query(default=20, le=100),
    _: dict = Depends(security.get_current_user),
):
    stmt = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
    if cursor:
        stmt = stmt.where(AuditLog.id < cursor)

    rows = session.exec(stmt).all()

    next_cursor = rows[-1].id if len(rows) == limit else None
    return {"items": rows, "next_cursor": next_cursor}
