# app/database.py
import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = Path(os.getenv("DB_PATH", "eventbus.db"))

def get_db_connection():
    """This function will be our dependency. It provides the real database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
      id        INTEGER PRIMARY KEY AUTOINCREMENT,
      job_id    TEXT NOT NULL,
      action    TEXT NOT NULL,
      timestamp TEXT NOT NULL
    )""")
    conn.commit()