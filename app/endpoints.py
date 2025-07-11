# app/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import uuid4
import datetime
import json
import paho.mqtt.publish as mqtt_publish
import structlog

from .database import get_db
from . import schemas, models, security
from .archivist import create_job_folders, DATA_ROOT

logger = structlog.get_logger(__name__)
router = APIRouter()

# --- NEW: Authentication Endpoint ---
@router.post("/token", tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = security.get_user(form_data.username)
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- Existing Endpoints (Now Protected) ---
@router.get("/", tags=["Status"])
def read_root():
    return {"status": "Aegis Event Bus is online"}

@router.post("/job", response_model=schemas.Job, tags=["Jobs"])
def create_new_job(db: Session = Depends(get_db), current_user: dict = Depends(security.get_current_user)):
    # This endpoint is now protected. The code will only run if a valid token is provided.
    job_id = f"FC-{uuid4()}"
    timestamp = datetime.datetime.now(datetime.UTC)
    create_job_folders(job_id=job_id, base_path=DATA_ROOT)

    new_log = models.AuditLog(job_id=job_id, action="job.created", timestamp=timestamp)
    db.add(new_log)
    db.commit()

    # ... (MQTT logic is unchanged)

    return {"job_id": job_id}

@router.get("/jobs", tags=["Jobs"])
def list_recent_jobs(db: Session = Depends(get_db), limit: int = 20, current_user: dict = Depends(security.get_current_user)):
    # This endpoint is also now protected
    jobs = db.query(models.AuditLog).filter(models.AuditLog.action == "job.created").order_by(models.AuditLog.id.desc()).limit(limit).all()
    return jobs