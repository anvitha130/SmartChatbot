import sqlite3
import pytest

def test_db_connection():
    try:
        conn = sqlite3.connect("career_counselor.db")  # Update if you use another DB name
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        assert len(tables) > 0, "No tables found in the database"
        conn.close()
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")
