"""
Recommendations module for CapacityConnect.
Handles personalized learning recommendations based on competency gaps.
"""
from modules.db import get_connection
from modules.competencies import get_skill_gaps
from modules.courses import get_course_by_id, get_courses_for_competency

def get_recommendations_for_user(user_id: int, max_recommendations: int = 5) -> list[dict]:
    """
    Generate personalized course recommendations based on competency gaps.
    Uses rule-based logic as specified in PRD.
    """
    # Get skill gaps for the user
    gaps = get_skill_gaps(user_id)

    # Get completed courses for the user
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT course_id FROM user_courses
            WHERE user_id = ? AND status IN ('completed', 'in_progress', 'enrolled')
        """, (user_id,))
        completed_course_ids = {row['course_id'] for row in cursor.fetchall()}
    finally:
        conn.close()

    recommendations = []

    # For each gap (sorted by priority), find relevant courses
    for gap in gaps:
        if gap['gap'] <= 0:
            continue  # No gap, skip

        competency_id = gap['competency_id']
        courses = get_courses_for_competency(competency_id)

        for course in courses:
            if course['course_id'] in completed_course_ids:
                continue  # Skip already enrolled/completed courses

            # Check if course already in recommendations
            if any(r['course_id'] == course['course_id'] for r in recommendations):
                continue

            # Build recommendation
            rec = {
                'course_id': course['course_id'],
                'title': course['title'],
                'description': course['description'],
                'instructor': course['instructor'],
                'difficulty': course['difficulty'],
                'duration': course['duration'],
                'target_competency': gap['name'],
                'target_competency_gap': gap['gap'],
                'target_competency_required': gap['required_level'],
                'target_competency_current': gap['current_level'],
                'reason': f"Addresses {gap['name']} competency gap ({gap['current_level']}/{gap['required_level']})",
                'improves_competencies': [gap['name']]
            }

            recommendations.append(rec)

            if len(recommendations) >= max_recommendations:
                break

        if len(recommendations) >= max_recommendations:
            break

    return recommendations

def get_learning_path_for_user(user_id: int) -> list[dict]:
    """
    Get the organized learning path for a user.
    Returns courses in sequence order with completion status.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ulp.course_id, ulp.sequence_order, ulp.is_completed,
                   c.title, c.description, c.instructor, c.difficulty, c.duration
            FROM user_learning_path ulp
            JOIN courses c ON ulp.course_id = c.course_id
            WHERE ulp.user_id = ?
            ORDER BY ulp.sequence_order
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def add_course_to_learning_path(user_id: int, course_id: int, sequence_order: int = None) -> bool:
    """Add a course to user's learning path."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # If sequence_order not provided, append to end
        if sequence_order is None:
            cursor.execute("""
                SELECT COALESCE(MAX(sequence_order), 0) + 1
                FROM user_learning_path WHERE user_id = ?
            """, (user_id,))
            sequence_order = cursor.fetchone()[0]

        cursor.execute("""
            INSERT OR REPLACE INTO user_learning_path (user_id, course_id, sequence_order, is_completed)
            VALUES (?, ?, ?, 0)
        """, (user_id, course_id, sequence_order))
        conn.commit()
        return True
    finally:
        conn.close()

def mark_learning_path_complete(user_id: int, course_id: int) -> bool:
    """Mark a course in learning path as completed."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_learning_path
            SET is_completed = 1
            WHERE user_id = ? AND course_id = ?
        """, (user_id, course_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def generate_learning_path_from_gaps(user_id: int) -> list[dict]:
    """
    Auto-generate a learning path based on competency gaps.
    Returns list of courses in recommended order.
    """
    recommendations = get_recommendations_for_user(user_id, max_recommendations=10)

    # Add to learning path
    for i, rec in enumerate(recommendations):
        add_course_to_learning_path(user_id, rec['course_id'], i + 1)

    return get_learning_path_for_user(user_id)

def get_competency_based_recommendations(user_id: int, competency_id: int) -> list[dict]:
    """Get course recommendations for a specific competency gap."""
    courses = get_courses_for_competency(competency_id)

    # Get user's completed/enrolled courses
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT course_id FROM user_courses
            WHERE user_id = ? AND status IN ('completed', 'in_progress', 'enrolled')
        """, (user_id,))
        enrolled = {row['course_id'] for row in cursor.fetchall()}
    finally:
        conn.close()

    recommendations = []
    for course in courses:
        if course['course_id'] not in enrolled:
            rec = dict(course)
            rec['reason'] = f"Improves {course['name']} competency"
            recommendations.append(rec)

    return recommendations