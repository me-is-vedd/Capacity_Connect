"""
Competencies module for CapacityConnect.
Handles competency management, role mapping, user competencies, and gap analysis.
"""
from modules.db import get_connection

def get_all_competencies() -> list[dict]:
    """Get all competencies."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT competency_id, name, description FROM competencies ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_competency_by_id(competency_id: int) -> dict | None:
    """Get competency by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT competency_id, name, description FROM competencies WHERE competency_id = ?", (competency_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def create_competency(name: str, description: str = "") -> int:
    """Create a new competency."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO competencies (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def update_competency(competency_id: int, name: str = None, description: str = None) -> bool:
    """Update a competency."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fields = {}
        if name is not None:
            fields['name'] = name
        if description is not None:
            fields['description'] = description
        if not fields:
            return False
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        values = list(fields.values()) + [competency_id]
        cursor.execute(f"UPDATE competencies SET {set_clause} WHERE competency_id = ?", values)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_competency(competency_id: int) -> bool:
    """Delete a competency."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM competencies WHERE competency_id = ?", (competency_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_role_competencies(role_name: str) -> list[dict]:
    """Get competencies required for a specific role with required levels."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rc.competency_id, rc.required_level, c.name, c.description
            FROM role_competencies rc
            JOIN competencies c ON rc.competency_id = c.competency_id
            WHERE rc.role_name = ?
            ORDER BY rc.required_level DESC
        """, (role_name,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_all_roles() -> list[str]:
    """Get all distinct roles that have competencies mapped."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT role_name FROM role_competencies ORDER BY role_name")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

def map_competency_to_role(role_name: str, competency_id: int, required_level: int) -> bool:
    """Map a competency to a role with required level."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO role_competencies (role_name, competency_id, required_level)
            VALUES (?, ?, ?)
        """, (role_name, competency_id, required_level))
        conn.commit()
        return True
    finally:
        conn.close()

def remove_competency_from_role(role_name: str, competency_id: int) -> bool:
    """Remove a competency from a role."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM role_competencies WHERE role_name = ? AND competency_id = ?", (role_name, competency_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_user_competencies(user_id: int) -> list[dict]:
    """Get all competencies for a specific user with current levels."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT uc.competency_id, uc.current_level, uc.last_assessed, c.name, c.description
            FROM user_competencies uc
            JOIN competencies c ON uc.competency_id = c.competency_id
            WHERE uc.user_id = ?
            ORDER BY c.name
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_user_competency(user_id: int, competency_id: int) -> dict | None:
    """Get a specific competency for a user."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT uc.current_level, uc.last_assessed, c.name, c.description
            FROM user_competencies uc
            JOIN competencies c ON uc.competency_id = c.competency_id
            WHERE uc.user_id = ? AND uc.competency_id = ?
        """, (user_id, competency_id))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def update_user_competency(user_id: int, competency_id: int, current_level: int) -> bool:
    """Update a user's competency level."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT OR REPLACE INTO user_competencies (user_id, competency_id, current_level, last_assessed)
            VALUES (?, ?, ?, ?)
        """, (user_id, competency_id, current_level, now))
        conn.commit()
        return True
    finally:
        conn.close()

def get_skill_gaps(user_id: int) -> list[dict]:
    """
    Calculate skill gaps for a user based on their role requirements.
    Returns list of competencies with gap analysis.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Get user's role
        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        role = cursor.fetchone()
        if not role:
            return []
        role_name = role[0]

        # Get required competencies for role
        cursor.execute("""
            SELECT rc.competency_id, rc.required_level, c.name, c.description
            FROM role_competencies rc
            JOIN competencies c ON rc.competency_id = c.competency_id
            WHERE rc.role_name = ?
        """, (role_name,))
        required_rows = cursor.fetchall()
        req_dict = {row['competency_id']: dict(row) for row in required_rows}

        # Get user's current competencies
        cursor.execute("""
            SELECT uc.competency_id, uc.current_level, c.name, c.description
            FROM user_competencies uc
            JOIN competencies c ON uc.competency_id = c.competency_id
            WHERE uc.user_id = ?
        """, (user_id,))
        current_rows = cursor.fetchall()
        curr_dict = {row['competency_id']: dict(row) for row in current_rows}

        # Calculate gaps
        gaps = []
        all_comp_ids = set(req_dict.keys()) | set(curr_dict.keys())
        
        for comp_id in all_comp_ids:
            if comp_id in req_dict:
                name = req_dict[comp_id]['name']
                desc = req_dict[comp_id]['description']
                required_level = req_dict[comp_id]['required_level']
            else:
                name = curr_dict[comp_id]['name']
                desc = curr_dict[comp_id]['description']
                required_level = 0  # Not required for role
                
            current_level = curr_dict.get(comp_id, {}).get('current_level', 1)
            gap = required_level - current_level

            if gap <= 0:
                status = "No Gap"
            elif gap == 1:
                status = "Low"
            elif gap == 2:
                status = "Medium"
            else:
                status = "Critical"

            gaps.append({
                'competency_id': comp_id,
                'name': name,
                'description': desc,
                'required_level': required_level,
                'current_level': current_level,
                'gap': gap,
                'status': status
            })

        # Sort by gap descending (critical first), then by name
        gaps.sort(key=lambda x: (x['gap'], x['name']), reverse=True)
        return gaps
    finally:
        conn.close()

def get_competency_level_label(level: int) -> str:
    """Get text label for competency level."""
    labels = {
        1: "Awareness",
        2: "Basic",
        3: "Proficient",
        4: "Advanced",
        5: "Expert"
    }
    return labels.get(level, str(level))

def get_gap_status_badge(gap: int) -> dict:
    """Get badge style for gap status."""
    if gap <= 0:
        return {'label': 'No Gap', 'color': 'green'}
    elif gap == 1:
        return {'label': 'Low', 'color': 'yellow'}
    elif gap == 2:
        return {'label': 'Medium', 'color': 'orange'}
    else:
        return {'label': 'Critical', 'color': 'red'}