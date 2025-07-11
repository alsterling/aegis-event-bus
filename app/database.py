# app/database.py
import sqlite3
from pathlib import Path
import os
import structlog
from dotenv import load_dotenv

load_dotenv()

logger = structlog.get_logger(__name__)
DB_PATH = Path(os.getenv("DB_PATH", "eventbus.db"))

def get_db_connection():
    """Creates and returns a new database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """Creates the database table if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
          id        INTEGER PRIMARY KEY AUTOINCREMENT,
          job_id    TEXT NOT NULL,
          action    TEXT NOT NULL,
          timestamp TEXT NOT NULL
        )""")
        conn.commit()
        logger.info("database.initialize.success", db_path=str(DB_PATH))
    except Exception as e:
        logger.error("database.initialize.failed", error=str(e))
    finally:
        conn.close()