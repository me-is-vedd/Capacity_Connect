import sqlite3
import os
import sys
from pathlib import Path

# Path to capacityconnect.db (located in application root)
DB_PATH = Path(__file__).resolve().parent.parent / "capacityconnect.db"

def get_connection():
    """Returns a SQLite connection object with Row factory enabled.
    Initializes the DB on the first run if it doesn't exist (e.g. cloud deployment).
    """
    if not DB_PATH.exists():
        # Add root dir to sys.path so we can import create_database
        root_dir = str(Path(__file__).resolve().parent.parent)
        if root_dir not in sys.path:
            sys.path.append(root_dir)
        import create_database
        create_database.main()
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn