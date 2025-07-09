from fastapi import FastAPI
from uuid import uuid4
import sqlite3
from pathlib import Path
import datetime
import os                
from dotenv import load_dotenv 

load_dotenv() # This command reads your .env file


# Get config from the .env file, with a fallback default
APP_NAME = os.getenv("APP_NAME", "Default App Title")
DB_PATH  = Path(os.getenv("DB_PATH", "default.db"))

# --- 1. Database Setup ---
# This creates a simple database file in your project folder.
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
# This command creates the table if it doesn't already exist.
cursor.execute("""
CREATE TABLE IF NOT EXISTS audit_log (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id    TEXT NOT NULL,
  action    TEXT NOT NULL,
  timestamp TEXT NOT NULL
)""")
conn.commit()

# --- 2. FastAPI Application ---
# This creates your main application object.
app = FastAPI(title=APP_NAME)

# --- 3. API Endpoints (The "Doors" to your service) ---
@app.get("/")
def read_root():
    """A simple endpoint to check if the service is online."""
    return {"status": "Aegis Event Bus is online"}

@app.post("/job")
def create_new_job():
    """Creates a new Job-ID and logs it to the audit database."""
    # Generate a unique Job ID
    job_id = f"FC-{uuid4()}"

    # Log the creation event to the database
    timestamp = datetime.datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO audit_log (job_id, action, timestamp) VALUES (?, ?, ?)",
        (job_id, "job.created", timestamp)
    )
    conn.commit()

    # Return the new Job ID to the user
    return {"job_id": job_id}