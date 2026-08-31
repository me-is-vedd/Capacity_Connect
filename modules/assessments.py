"""
Assessments module for CapacityConnect.
Handles assessments, questions, and results.
"""
from modules.db import get_connection

def get_assessment_by_id(assessment_id: int) -> dict | None:
    """Get assessment by ID with questions."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT assessment_id, course_id, title, passing_score
            FROM assessments WHERE assessment_id = ?
        """, (assessment_id,))
        assessment = cursor.fetchone()
        if not assessment:
            return None

        assessment = dict(assessment)

        # Get questions
        cursor.execute("""
            SELECT question_id, question, options, correct_answer
            FROM questions WHERE assessment_id = ?
        """, (assessment_id,))
        assessment['questions'] = [dict(row) for row in cursor.fetchall()]

        return assessment
    finally:
        conn.close()

def get_assessments_for_course(course_id: int) -> list[dict]:
    """Get all assessments for a course."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT assessment_id, course_id, title, passing_score
            FROM assessments WHERE course_id = ?
        """, (course_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def create_assessment(course_id: int, title: str, passing_score: int = 70) -> int:
    """Create a new assessment for a course."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assessments (course_id, title, passing_score)
            VALUES (?, ?, ?)
        """, (course_id, title, passing_score))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def update_assessment(assessment_id: int, title: str = None, passing_score: int = None) -> bool:
    """Update an assessment."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fields = {}
        if title is not None:
            fields['title'] = title
        if passing_score is not None:
            fields['passing_score'] = passing_score
        if not fields:
            return False
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        values = list(fields.values()) + [assessment_id]
        cursor.execute(f"UPDATE assessments SET {set_clause} WHERE assessment_id = ?", values)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_assessment(assessment_id: int) -> bool:
    """Delete an assessment."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assessments WHERE assessment_id = ?", (assessment_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def add_question(assessment_id: int, question: str, options: list, correct_answer: int) -> int:
    """Add a question to an assessment. Options should be a list of strings."""
    import json
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO questions (assessment_id, question, options, correct_answer)
            VALUES (?, ?, ?, ?)
        """, (assessment_id, question, json.dumps(options), correct_answer))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def update_question(question_id: int, question: str = None, options: list = None, correct_answer: int = None) -> bool:
    """Update a question."""
    import json
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fields = {}
        if question is not None:
            fields['question'] = question
        if options is not None:
            fields['options'] = json.dumps(options)
        if correct_answer is not None:
            fields['correct_answer'] = correct_answer
        if not fields:
            return False
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        values = list(fields.values()) + [question_id]
        cursor.execute(f"UPDATE questions SET {set_clause} WHERE question_id = ?", values)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_question(question_id: int) -> bool:
    """Delete a question."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE question_id = ?", (question_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def submit_assessment_result(user_id: int, assessment_id: int, answers: list[int]) -> dict:
    """
    Submit assessment answers and calculate score.
    Returns result with score, passed status, and competency updates.
    """
    import json
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Get correct answers
        cursor.execute("""
            SELECT question_id, correct_answer
            FROM questions WHERE assessment_id = ?
            ORDER BY question_id
        """, (assessment_id,))
        correct_answers = {row['question_id']: row['correct_answer'] for row in cursor.fetchall()}

        if not correct_answers:
            return {'error': 'No questions found for this assessment'}

        # Calculate score
        total_questions = len(correct_answers)
        correct_count = 0
        for q_id, user_answer in zip(correct_answers.keys(), answers):
            if user_answer == correct_answers[q_id]:
                correct_count += 1

        score = round((correct_count / total_questions) * 100)

        # Check if passed
        cursor.execute("SELECT passing_score FROM assessments WHERE assessment_id = ?", (assessment_id,))
        passing_score = cursor.fetchone()['passing_score']
        passed = score >= passing_score

        # Save result
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO results (user_id, assessment_id, score, date)
            VALUES (?, ?, ?, ?)
        """, (user_id, assessment_id, score, now))

        conn.commit()

        return {
            'score': score,
            'passed': passed,
            'total_questions': total_questions,
            'correct_answers': correct_count,
            'passing_score': passing_score
        }
    finally:
        conn.close()

def get_user_results(user_id: int) -> list[dict]:
    """Get all assessment results for a user."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.result_id, r.assessment_id, r.score, r.date, a.title as assessment_title, a.passing_score
            FROM results r
            JOIN assessments a ON r.assessment_id = a.assessment_id
            WHERE r.user_id = ?
            ORDER BY r.date DESC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_user_result_for_assessment(user_id: int, assessment_id: int) -> dict | None:
    """Get a user's latest result for a specific assessment."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.result_id, r.assessment_id, r.score, r.date, a.title as assessment_title, a.passing_score
            FROM results r
            JOIN assessments a ON r.assessment_id = a.assessment_id
            WHERE r.user_id = ? AND r.assessment_id = ?
            ORDER BY r.date DESC
            LIMIT 1
        """, (user_id, assessment_id))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_assessment_stats(assessment_id: int) -> dict:
    """Get statistics for an assessment."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as total_attempts,
                   AVG(score) as avg_score,
                   MAX(score) as max_score,
                   MIN(score) as min_score,
                   SUM(CASE WHEN score >= (SELECT passing_score FROM assessments WHERE assessment_id = ?) THEN 1 ELSE 0 END) as passed_count
            FROM results WHERE assessment_id = ?
        """, (assessment_id, assessment_id))
        row = cursor.fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()