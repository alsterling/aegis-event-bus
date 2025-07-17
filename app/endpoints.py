# app/endpoints.py
from uuid import uuid4
import json, os, structlog, datetime as dt
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, text
import paho.mqtt.publish as mqtt_publish

from .db import get_session
from .models import AuditLog
from . import schemas, security
from .archivist import create_job_folders, DATA_ROOT

router = APIRouter()
log = structlog.get_logger(__name__)

MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))


@router.get("/healthz", include_in_schema=False)
def health_check(session: Session = Depends(get_session)):
    """A simple health check endpoint that pings the database."""
    # This correctly wraps the raw SQL in the text() function
    session.exec(text("SELECT 1"))
    return {"status": "ok"}


@router.get("/", tags=["Status"])
def read_root():
    return {"status": "Aegis Event Bus is online"}


@router.post("/job", response_model=schemas.Job, tags=["Jobs"])
def create_new_job(
    session: Session = Depends(get_session),
    _: dict = Depends(security.get_current_user),
):
    job_id = f"FC-{uuid4()}"
    create_job_folders(job_id=job_id, base_path=DATA_ROOT)

    with session:
        entry = AuditLog(job_id=job_id, action="job.created")
        session.add(entry)
        session.commit()
        session.refresh(entry)

    payload = {"job_id": job_id, "timestamp": entry.timestamp.isoformat()}
    try:
        mqtt_publish.single(
            topic="aegis/job/created",
            payload=json.dumps(payload),
            hostname=MQTT_HOST,
            port=MQTT_PORT,
            tls={"ca_certs": "./mosquitto/certs/ca.crt"},
        )
    except Exception as exc:
        log.warning("mqtt.publish_failed", job_id=job_id, err=str(exc))

    return {"job_id": job_id}


@router.get("/jobs", response_model=schemas.JobsPage, tags=["Jobs"])
def list_recent_jobs(
    session: Session = Depends(get_session),
    cursor: int | None = Query(None, description="last row id from prev page"),
    limit: int = Query(20, le=100),
    _: dict = Depends(security.get_current_user),
):
    stmt = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
    if cursor:
        stmt = stmt.where(AuditLog.id < cursor)

    rows = session.exec(stmt).all()

    next_cursor = rows[-1].id if len(rows) == limit else None
    return {"items": rows, "next_cursor": next_cursor}