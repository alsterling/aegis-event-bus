# app/endpoints.py

from fastapi import APIRouter
from uuid import uuid4
import datetime
from .database import get_db_connection
from . import schemas # <-- 1. IMPORT your new schemas file

router = APIRouter()

@router.get("/")
def read_root():
    """A simple endpoint to check if the service is online."""
    return {"status": "Aegis Event Bus is online"}

#  2. ADD THE RETURN TYPE HINT HERE 👇
@router.post("/job", response_model=schemas.Job)
def create_new_job() -> schemas.Job:
    """Creates a new Job-ID and logs it to the audit database."""
    job_id = f"FC-{uuid4()}"
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    
    conn = get_db_connection()
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
    
    return {"job_id": job_id}