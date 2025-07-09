# tests/conftest.py
import pytest
import sqlite3

@pytest.fixture
def test_db_conn():
    """Creates a temporary, in-memory SQLite database for a test."""
    # ":memory:" tells SQLite to create the DB in RAM, not a file
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # We still need to create the table for each test
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE audit_log (
      id        INTEGER PRIMARY KEY AUTOINCREMENT,
      job_id    TEXT NOT NULL,
      action    TEXT NOT NULL,
      timestamp TEXT NOT NULL
    )""")
    conn.commit()

    yield conn  # This is where the test runs

    # After the test is done, the connection is closed
    conn.close()