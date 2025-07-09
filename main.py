from fastapi import FastAPI
from uuid import uuid4
import sqlite3
from pathlib import Path
import datetime
import os
from dotenv import load_dotenv

# --- 1. Configuration Setup ---
load_dotenv()
APP_NAME = os.getenv("APP_NAME", "Default App Title")
# IMPORTANT: We define the path, but we do NOT connect yet.
DB_PATH = Path(os.getenv("DB_PATH", "default.db"))

# --- 2. Database Helper Functions ---
def get_db_connection():
    """Creates and returns a new database connection."""
    # check_same_thread=False is needed for FastAPI testing with SQLite
    conn = sqlite3.connect(DB_PATH, check_same_thread=False) 
    return conn

def initialize_db():
    """Creates the database table if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
      id        INTEGER PRIMARY KEY AUTOINCREMENT,
      job_id    TEXT NOT NULL,
      action    TEXT NOT NULL,
      timestamp TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()

# --- 3. FastAPI Application ---
app = FastAPI(title=APP_NAME)

# Initialize the database when the application starts
initialize_db()

# --- 4. API Endpoints ---
@app.get("/")
def read_root():
    """A simple endpoint to check if the service is online."""
    return {"status": "Aegis Event Bus is online"}

@app.post("/job")
def create_new_job():
    """Creates a new Job-ID and logs it to the audit database."""
    job_id = f"FC-{uuid4()}"
    # Use datetime.UTC as recommended by the warning message
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    
    # Get a fresh database connection for this specific request
    conn = get_db_connection() 
    cursor = conn.cursor()
    
    try:
        # Log the creation event to the database
        cursor.execute(
            "INSERT INTO audit_log (job_id, action, timestamp) VALUES (?, ?, ?)",
            (job_id, "job.created", timestamp)
        )
        conn.commit()
    except Exception as e:
        # If anything goes wrong, roll back the change
        conn.rollback()
        raise e
    finally:
        # ALWAYS close the connection when the work is done
        conn.close() 
    
    return {"job_id": job_id}