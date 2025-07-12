# app/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from uuid import uuid4
import datetime
import json
import paho.mqtt.publish as mqtt_publish
import sqlite3

from .database import get_db_connection
from . import schemas, security
from .archivist import create_job_folders, DATA_ROOT

router = APIRouter()

@router.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
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
    return {"status": "Aegis Event Bus is online"}

@router.post("/job", response_model=schemas.Job, tags=["Jobs"])
def create_new_job(current_user: dict = Depends(security.get_current_user)):
    job_id = f"FC-{uuid4()}"
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    
    create_job_folders(job_id=job_id, base_path=DATA_ROOT)
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_log (job_id, action, timestamp) VALUES (?, ?, ?)",
            (job_id, "job.created", timestamp)
        )
        conn.commit()
    finally:
        conn.close()

    try:
        event_payload = {"job_id": job_id, "timestamp": timestamp}
        mqtt_publish.single("aegis/job/created", payload=json.dumps(event_payload), hostname="localhost", port=1883)
    except Exception:
        pass

    return {"job_id": job_id}

@router.get("/jobs", tags=["Jobs"])
def list_recent_jobs(limit: int = 20, current_user: dict = Depends(security.get_current_user)):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        sql_query = "SELECT * FROM audit_log WHERE action='job.created' ORDER BY id DESC LIMIT ?"
        rows = cursor.execute(sql_query, (limit,)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()