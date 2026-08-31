"""
Analytics module for CapacityConnect.
Provides organization-level competency analytics, gap summaries, and training reports.
"""
from modules.db import get_connection

def get_org_capacity_metrics() -> dict:
    """Get high-level organization capacity metrics."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Total employees
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
        total_employees = cursor.fetchone()[0]

        # Active learners (users enrolled in at least one course or completed one)
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_courses")
        active_learners = cursor.fetchone()[0]

        # Total courses
        cursor.execute("SELECT COUNT(*) FROM courses WHERE status = 'published'")
        total_courses = cursor.fetchone()[0]

        # Total resources in Knowledge Hub
        cursor.execute("SELECT COUNT(*) FROM knowledge_resources WHERE status = 'published'")
        total_resources = cursor.fetchone()[0]

        # Calculate average overall competency score across all employees
        cursor.execute("""
            SELECT u.user_id, u.role, rc.competency_id, rc.required_level, COALESCE(uc.current_level, 1) as current_level
            FROM users u
            JOIN role_competencies rc ON u.role = rc.role_name
            LEFT JOIN user_competencies uc ON u.user_id = uc.user_id AND rc.competency_id = uc.competency_id
            WHERE u.is_admin = 0
        """)
        all_comps = cursor.fetchall()

        if all_comps:
            total_req = sum([r['required_level'] for r in all_comps])
            total_curr = sum([r['current_level'] for r in all_comps])
            avg_competency_pct = round((total_curr / total_req) * 100) if total_req > 0 else 0
        else:
            avg_competency_pct = 0

        # Calculate active critical gaps
        # A gap is critical if gap = required_level - current_level >= 2
        cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT rc.required_level - COALESCE(uc.current_level, 1) as gap
                FROM users u
                JOIN role_competencies rc ON u.role = rc.role_name
                LEFT JOIN user_competencies uc ON u.user_id = uc.user_id AND rc.competency_id = uc.competency_id
                WHERE u.is_admin = 0
            ) WHERE gap >= 2
        """)
        critical_gaps_count = cursor.fetchone()[0]

        return {
            'total_employees': total_employees,
            'active_learners': active_learners,
            'total_courses': total_courses,
            'total_resources': total_resources,
            'avg_competency_pct': avg_competency_pct,
            'critical_gaps_count': critical_gaps_count
        }
    finally:
        conn.close()

def get_top_skill_gaps(limit: int = 5) -> list[dict]:
    """
    Get top competencies where gaps exist, sorted by severity/volume.
    Useful for horizontal gap analysis bar charts.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Let's assess gaps for all employees
        cursor.execute("""
            SELECT c.name as competency_name,
                   rc.required_level - COALESCE(uc.current_level, 1) as gap
            FROM users u
            JOIN role_competencies rc ON u.role = rc.role_name
            JOIN competencies c ON rc.competency_id = c.competency_id
            LEFT JOIN user_competencies uc ON u.user_id = uc.user_id AND rc.competency_id = uc.competency_id
            WHERE u.is_admin = 0
        """)
        rows = cursor.fetchall()

        # Calculate frequency and weight of positive gaps
        gaps_summary = {}
        for row in rows:
            gap = row['gap']
            name = row['competency_name']
            if gap > 0:
                if name not in gaps_summary:
                    gaps_summary[name] = {'total_gap': 0, 'count': 0, 'critical_count': 0}
                gaps_summary[name]['total_gap'] += gap
                gaps_summary[name]['count'] += 1
                if gap >= 2:
                    gaps_summary[name]['critical_count'] += 1

        # Format and sort
        formatted_gaps = []
        for name, data in gaps_summary.items():
            # Percentage of affected employees (gaps > 0)
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
            total_emp = cursor.fetchone()[0] or 1
            pct_affected = round((data['count'] / total_emp) * 100)

            formatted_gaps.append({
                'competency': name,
                'total_gap_score': data['total_gap'],
                'count_affected': data['count'],
                'critical_count': data['critical_count'],
                'pct_affected': pct_affected
            })

        # Sort by percentage affected first, then total severity
        formatted_gaps.sort(key=lambda x: (x['pct_affected'], x['total_gap_score']), reverse=True)
        return formatted_gaps[:limit]
    finally:
        conn.close()

def get_department_competency_averages() -> list[dict]:
    """Get average competency percentage grouped by department."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.department, rc.required_level, COALESCE(uc.current_level, 1) as current_level
            FROM users u
            JOIN role_competencies rc ON u.role = rc.role_name
            LEFT JOIN user_competencies uc ON u.user_id = uc.user_id AND rc.competency_id = uc.competency_id
            WHERE u.is_admin = 0 AND u.department IS NOT NULL
        """)
        rows = cursor.fetchall()

        # Group data by department
        dept_data = {}
        for row in rows:
            dept = row['department']
            if dept not in dept_data:
                dept_data[dept] = {'req': 0, 'curr': 0}
            dept_data[dept]['req'] += row['required_level']
            dept_data[dept]['curr'] += row['current_level']

        # Calculate averages
        averages = []
        for dept, scores in dept_data.items():
            avg_pct = round((scores['curr'] / scores['req']) * 100) if scores['req'] > 0 else 0
            averages.append({
                'department': dept,
                'avg_competency_pct': avg_pct
            })

        averages.sort(key=lambda x: x['avg_competency_pct'], reverse=True)
        return averages
    finally:
        conn.close()

def get_training_demand_by_competency() -> list[dict]:
    """Get counts of course enrollments addressing specific competencies."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.name as competency_name, COUNT(uc.user_id) as enrollment_count
            FROM user_courses uc
            JOIN course_competencies cc ON uc.course_id = cc.course_id
            JOIN competencies c ON cc.competency_id = c.competency_id
            GROUP BY c.name
            ORDER BY enrollment_count DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_improvement_analytics() -> dict:
    """Get metrics on competency improvements after training/assessments."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Analyze users who completed a course vs their current competency level improvement
        # In a fully-blown system we would track competency history.
        # For our seed/hackathon prototype, we can calculate the percentage of users with 'No Gap' status
        cursor.execute("""
            SELECT u.user_id, rc.competency_id, rc.required_level, COALESCE(uc.current_level, 1) as current_level
            FROM users u
            JOIN role_competencies rc ON u.role = rc.role_name
            LEFT JOIN user_competencies uc ON u.user_id = uc.user_id AND rc.competency_id = uc.competency_id
            WHERE u.is_admin = 0
        """)
        all_comps = cursor.fetchall()

        total = len(all_comps)
        improved_or_met = 0
        for r in all_comps:
            if r['current_level'] >= r['required_level']:
                improved_or_met += 1

        pct_met = round((improved_or_met / total) * 100) if total > 0 else 0

        # Average assessment scores
        cursor.execute("SELECT AVG(score) FROM results")
        avg_score = round(cursor.fetchone()[0] or 0)

        # Course completion count
        cursor.execute("SELECT COUNT(*) FROM user_courses WHERE status = 'completed'")
        completed_count = cursor.fetchone()[0]

        return {
            'pct_requirements_met': pct_met,
            'avg_assessment_score': avg_score,
            'completed_courses_count': completed_count
        }
    finally:
        conn.close()