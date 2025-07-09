# app/database.py

import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv

# --- Configuration Setup ---
load_dotenv()
DB_PATH = Path(os.getenv("DB_PATH", "default.db"))

# --- Database Helper Functions ---
def get_db_connection():
    """Creates and returns a new database connection."""
    # check_same_thread=False is needed for FastAPI testing with SQLite
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def initialize_db():
    """Creates the database table if it doesn't already exist."""
    print("Attempting to initialize the database...")
    try:
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
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")