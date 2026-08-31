"""
Auth module for CapacityConnect.
Handles user authentication and session management with bcrypt.
"""
import bcrypt
from modules.db import get_connection

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except:
        return False

def get_user_by_email(email: str):
    """Retrieve a user record by email."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()

def authenticate_user(email: str, password: str):
    """Authenticate user with email and password."""
    user = get_user_by_email(email)
    if user and verify_password(password, user['password_hash']):
        return user
    return None

def get_user_by_id(user_id: int):
    """Get user by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()