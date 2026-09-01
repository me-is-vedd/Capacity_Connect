"""
Users module for CapacityConnect.
Handles user profiles, course enrollment, and progress tracking.
"""
from modules.db import get_connection
from modules.auth import hash_password
from modules.auth import hash_password

def get_user_profile(user_id: int) -> dict | None:
    """Get full profile of a user, including completed courses and summaries."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, name, email, department, role, designation, experience, is_admin
            FROM users WHERE user_id = ?
        """, (user_id,))
        user = cursor.fetchone()
        if not user:
            return None

        profile = dict(user)

        # Get completed courses count and active courses count
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM user_courses
            WHERE user_id = ?
            GROUP BY status
        """, (user_id,))
        courses = cursor.fetchall()

        profile['completed_courses'] = 0
        profile['active_courses'] = 0
        for entry in courses:
            if entry['status'] == 'completed':
                profile['completed_courses'] = entry['count']
            elif entry['status'] in ('enrolled', 'in_progress'):
                profile['active_courses'] += entry['count']

        # Get overall competency progress
        # Formula: (Sum of current levels / Sum of required levels) for the user's role
        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        role = cursor.fetchone()[0]

        cursor.execute("""
            SELECT rc.competency_id, rc.required_level, COALESCE(uc.current_level, 1) as current_level
            FROM role_competencies rc
            LEFT JOIN user_competencies uc
              ON rc.competency_id = uc.competency_id AND uc.user_id = ?
            WHERE rc.role_name = ?
        """, (user_id, role))

        comp_data = cursor.fetchall()
        if comp_data:
            total_required = sum([r['required_level'] for r in comp_data])
            total_current = sum([r['current_level'] for r in comp_data])
            profile['overall_competency_pct'] = round((total_current / total_required) * 100)
        else:
            profile['overall_competency_pct'] = 0

        return profile
    finally:
        conn.close()

def enroll_in_course(user_id: int, course_id: int) -> bool:
    """Enroll a user in a course."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Check if already enrolled
        cursor.execute("SELECT 1 FROM user_courses WHERE user_id = ? AND course_id = ?", (user_id, course_id))
        if cursor.fetchone():
            return True

        cursor.execute("""
            INSERT INTO user_courses (user_id, course_id, status, progress)
            VALUES (?, ?, 'enrolled', 0)
        """, (user_id, course_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def update_course_progress(user_id: int, course_id: int, progress: int) -> bool:
    """Update progress for an enrolled course."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        status = 'in_progress'
        completion_date = None
        if progress >= 100:
            progress = 100
            status = 'completed'
            import datetime
            completion_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            UPDATE user_courses
            SET progress = ?, status = ?, completion_date = COALESCE(completion_date, ?)
            WHERE user_id = ? AND course_id = ?
        """, (progress, status, completion_date, user_id, course_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_user_courses(user_id: int) -> list[dict]:
    """Get list of courses enrolled by a user with progress details."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.course_id, c.title, c.description, c.instructor, c.difficulty, c.duration,
                   uc.enrollment_date, uc.completion_date, uc.progress, uc.status
            FROM user_courses uc
            JOIN courses c ON uc.course_id = c.course_id
            WHERE uc.user_id = ?
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_all_users() -> list[dict]:
    """Get all users from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def update_user(user_id: int, updates: dict) -> bool:
    """Update user fields."""
    if not updates:
        return True
    conn = get_connection()
    try:
        cursor = conn.cursor()
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values())
        values.append(user_id)
        cursor.execute(f"UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", values)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating user: {e}")
        return False
    finally:
        conn.close()

def delete_user(user_id: int) -> bool:
    """Delete a user."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()

def add_user(user_data: dict) -> bool:
    """Add a new user."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Ensure password_hash is provided, else set a default
        if 'password_hash' not in user_data:
            user_data['password_hash'] = hash_password("default123")
            
        columns = ", ".join(user_data.keys())
        placeholders = ", ".join("?" for _ in user_data)
        values = list(user_data.values())
        
        cursor.execute(f"INSERT INTO users ({columns}) VALUES ({placeholders})", values)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False
    finally:
        conn.close()