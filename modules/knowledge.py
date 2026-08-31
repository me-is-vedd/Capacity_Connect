"""
Knowledge Hub module for CapacityConnect.
Handles knowledge resources, contributions, search, and categorization.
"""
from modules.db import get_connection

def get_all_knowledge_resources(status: str = None, category: str = None,
                                 department: str = None, competency_id: int = None) -> list[dict]:
    """Get knowledge resources with optional filters."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT kr.resource_id, kr.title, kr.description, kr.category, kr.department,
                   kr.author_id, kr.file_path, kr.status, kr.created_at,
                   u.name as author_name
            FROM knowledge_resources kr
            LEFT JOIN users u ON kr.author_id = u.user_id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND kr.status = ?"
            params.append(status)
        if category:
            query += " AND kr.category = ?"
            params.append(category)
        if department:
            query += " AND kr.department = ?"
            params.append(department)
        if competency_id:
            query += """
                AND kr.resource_id IN (
                    SELECT resource_id FROM resource_competencies WHERE competency_id = ?
                )
            """
            params.append(competency_id)

        query += " ORDER BY kr.created_at DESC"

        cursor.execute(query, params)
        resources = [dict(row) for row in cursor.fetchall()]

        # Add competencies for each resource
        for resource in resources:
            cursor.execute("""
                SELECT c.competency_id, c.name
                FROM resource_competencies rc
                JOIN competencies c ON rc.competency_id = c.competency_id
                WHERE rc.resource_id = ?
            """, (resource['resource_id'],))
            resource['competencies'] = [dict(r) for r in cursor.fetchall()]

        return resources
    finally:
        conn.close()

def get_knowledge_resource(resource_id: int) -> dict | None:
    """Get a knowledge resource by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT kr.resource_id, kr.title, kr.description, kr.category, kr.department,
                   kr.author_id, kr.file_path, kr.status, kr.created_at,
                   u.name as author_name
            FROM knowledge_resources kr
            LEFT JOIN users u ON kr.author_id = u.user_id
            WHERE kr.resource_id = ?
        """, (resource_id,))
        resource = cursor.fetchone()
        if not resource:
            return None

        resource = dict(resource)

        # Get competencies
        cursor.execute("""
            SELECT c.competency_id, c.name
            FROM resource_competencies rc
            JOIN competencies c ON rc.competency_id = c.competency_id
            WHERE rc.resource_id = ?
        """, (resource_id,))
        resource['competencies'] = [dict(r) for r in cursor.fetchall()]

        return resource
    finally:
        conn.close()

def create_knowledge_resource(title: str, description: str, category: str,
                               department: str, author_id: int, file_path: str = None,
                               competency_ids: list = None, status: str = "draft") -> int:
    """Create a new knowledge resource."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO knowledge_resources (title, description, category, department,
                                              author_id, file_path, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, description, category, department, author_id, file_path, status))
        resource_id = cursor.lastrowid

        # Add competency mappings
        if competency_ids:
            for comp_id in competency_ids:
                cursor.execute("""
                    INSERT INTO resource_competencies (resource_id, competency_id)
                    VALUES (?, ?)
                """, (resource_id, comp_id))

        conn.commit()
        return resource_id
    finally:
        conn.close()

def update_knowledge_resource(resource_id: int, **kwargs) -> bool:
    """Update a knowledge resource."""
    allowed_fields = ['title', 'description', 'category', 'department', 'file_path', 'status']
    fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
    if not fields:
        return False

    conn = get_connection()
    try:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        values = list(fields.values()) + [resource_id]
        cursor.execute(f"UPDATE knowledge_resources SET {set_clause} WHERE resource_id = ?", values)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_knowledge_resource(resource_id: int) -> bool:
    """Delete a knowledge resource."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM knowledge_resources WHERE resource_id = ?", (resource_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def add_competency_to_resource(resource_id: int, competency_id: int) -> bool:
    """Add a competency mapping to a resource."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO resource_competencies (resource_id, competency_id)
            VALUES (?, ?)
        """, (resource_id, competency_id))
        conn.commit()
        return True
    finally:
        conn.close()

def remove_competency_from_resource(resource_id: int, competency_id: int) -> bool:
    """Remove a competency mapping from a resource."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resource_competencies WHERE resource_id = ? AND competency_id = ?", (resource_id, competency_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def search_knowledge_resources(query: str, category: str = None,
                                department: str = None, competency_id: int = None) -> list[dict]:
    """Search knowledge resources by keyword."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        sql = """
            SELECT kr.resource_id, kr.title, kr.description, kr.category, kr.department,
                   kr.author_id, kr.file_path, kr.status, kr.created_at,
                   u.name as author_name
            FROM knowledge_resources kr
            LEFT JOIN users u ON kr.author_id = u.user_id
            WHERE kr.status = 'published'
            AND (kr.title LIKE ? OR kr.description LIKE ?)
        """
        search_term = f"%{query}%"
        params = [search_term, search_term]

        if category:
            sql += " AND kr.category = ?"
            params.append(category)
        if department:
            sql += " AND kr.department = ?"
            params.append(department)
        if competency_id:
            sql += """
                AND kr.resource_id IN (
                    SELECT resource_id FROM resource_competencies WHERE competency_id = ?
                )
            """
            params.append(competency_id)

        sql += " ORDER BY kr.created_at DESC"

        cursor.execute(sql, params)
        resources = [dict(row) for row in cursor.fetchall()]

        # Add competencies for each resource
        for resource in resources:
            cursor.execute("""
                SELECT c.competency_id, c.name
                FROM resource_competencies rc
                JOIN competencies c ON rc.competency_id = c.competency_id
                WHERE rc.resource_id = ?
            """, (resource['resource_id'],))
            resource['competencies'] = [dict(r) for r in cursor.fetchall()]

        return resources
    finally:
        conn.close()

def get_categories() -> list[str]:
    """Get all distinct categories."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM knowledge_resources WHERE category IS NOT NULL ORDER BY category")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

def get_departments() -> list[str]:
    """Get all distinct departments."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT department FROM knowledge_resources WHERE department IS NOT NULL ORDER BY department")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

def get_content_types() -> list[str]:
    """Get all distinct content types (categories)."""
    return get_categories()

def approve_knowledge_resource(resource_id: int) -> bool:
    """Approve a knowledge resource for publication."""
    return update_knowledge_resource(resource_id, status='published')

def reject_knowledge_resource(resource_id: int) -> bool:
    """Reject a knowledge resource (set back to draft)."""
    return update_knowledge_resource(resource_id, status='draft')

def submit_for_review(resource_id: int) -> bool:
    """Submit a resource for review."""
    return update_knowledge_resource(resource_id, status='pending_review')