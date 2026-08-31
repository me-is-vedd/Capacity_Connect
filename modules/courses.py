"""
Courses module for CapacityConnect.
Handles course management, course competencies, and course content.
"""
from modules.db import get_connection

def get_all_courses(status: str = None) -> list[dict]:
    """Get all courses, optionally filtered by status."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if status:
            cursor.execute("""
                SELECT course_id, title, description, instructor, difficulty, duration, status
                FROM courses WHERE status = ? ORDER BY title
            """, (status,))
        else:
            cursor.execute("""
                SELECT course_id, title, description, instructor, difficulty, duration, status
                FROM courses ORDER BY title
            """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_course_by_id(course_id: int) -> dict | None:
    """Get course details by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT course_id, title, description, instructor, difficulty, duration, status
            FROM courses WHERE course_id = ?
        """, (course_id,))
        row = cursor.fetchone()
        if not row:
            return None
        course = dict(row)

        # Get competencies addressed by this course
        cursor.execute("""
            SELECT c.competency_id, c.name, cc.target_level
            FROM course_competencies cc
            JOIN competencies c ON cc.competency_id = c.competency_id
            WHERE cc.course_id = ?
        """, (course_id,))
        course['competencies'] = [dict(r) for r in cursor.fetchall()]

        # Get assessments for this course
        cursor.execute("""
            SELECT assessment_id, title, passing_score
            FROM assessments
            WHERE course_id = ?
        """, (course_id,))
        course['assessments'] = [dict(r) for r in cursor.fetchall()]

        return course
    finally:
        conn.close()

def create_course(title: str, description: str, instructor: str, difficulty: str,
                  duration: str, status: str = "draft") -> int:
    """Create a new course."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO courses (title, description, instructor, difficulty, duration, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, instructor, difficulty, duration, status))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def update_course(course_id: int, **kwargs) -> bool:
    """Update course fields."""
    allowed_fields = ['title', 'description', 'instructor', 'difficulty', 'duration', 'status']
    fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
    if not fields:
        return False

    conn = get_connection()
    try:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        values = list(fields.values()) + [course_id]
        cursor.execute(f"UPDATE courses SET {set_clause} WHERE course_id = ?", values)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_course(course_id: int) -> bool:
    """Delete a course."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def add_competency_to_course(course_id: int, competency_id: int, target_level: int) -> bool:
    """Map a competency to a course with target level."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO course_competencies (course_id, competency_id, target_level)
            VALUES (?, ?, ?)
        """, (course_id, competency_id, target_level))
        conn.commit()
        return True
    finally:
        conn.close()

def remove_competency_from_course(course_id: int, competency_id: int) -> bool:
    """Remove a competency from a course."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM course_competencies WHERE course_id = ? AND competency_id = ?", (course_id, competency_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_course_competencies(course_id: int) -> list[dict]:
    """Get competencies for a specific course."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.competency_id, c.name, c.description, cc.target_level
            FROM course_competencies cc
            JOIN competencies c ON cc.competency_id = c.competency_id
            WHERE cc.course_id = ?
        """, (course_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_courses_for_competency(competency_id: int) -> list[dict]:
    """Get courses that address a specific competency."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.course_id, c.title, c.description, c.instructor, c.difficulty, c.duration, cc.target_level
            FROM course_competencies cc
            JOIN courses c ON cc.course_id = c.course_id
            WHERE cc.competency_id = ? AND c.status = 'published'
            ORDER BY cc.target_level
        """, (competency_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_published_courses() -> list[dict]:
    """Get all published courses."""
    return get_all_courses(status='published')

def get_course_enrollment_count(course_id: int) -> int:
    """Get number of users enrolled in a course."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user_courses WHERE course_id = ?", (course_id,))
        return cursor.fetchone()[0]
    finally:
        conn.close()

def get_course_completion_rate(course_id: int) -> float:
    """Get completion rate for a course."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user_courses WHERE course_id = ?", (course_id,))
        total = cursor.fetchone()[0]
        if total == 0:
            return 0.0
        cursor.execute("SELECT COUNT(*) FROM user_courses WHERE course_id = ? AND status = 'completed'", (course_id,))
        completed = cursor.fetchone()[0]
        return round((completed / total) * 100, 1)
    finally:
        conn.close()