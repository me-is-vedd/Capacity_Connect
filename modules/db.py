import sqlite3
import os
from pathlib import Path

# Path to capacityconnect.db (located in application root)
DB_PATH = Path(__file__).resolve().parent.parent / "capacityconnect.db"

def get_connection():
    """Returns a SQLite connection object with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn