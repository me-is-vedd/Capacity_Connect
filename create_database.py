#!/usr/bin/env python3
"""
CapacityConnect Database Setup Script

Creates SQLite database with all tables defined in the PRD:
- users
- competencies
- role_competencies
- user_competencies
- courses
- course_competencies
- assessments
- questions
- results
- knowledge_resources
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "capacityconnect.db"

def get_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables(conn):
    """Create all tables as per PRD schema."""
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT,
            role TEXT,
            designation TEXT,
            experience TEXT,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Competencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competencies (
            competency_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Role Competencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS role_competencies (
            role_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT NOT NULL,
            competency_id INTEGER NOT NULL,
            required_level INTEGER NOT NULL CHECK (required_level BETWEEN 1 AND 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competency_id) REFERENCES competencies(competency_id)
        )
    """)

    # User Competencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_competencies (
            user_id INTEGER NOT NULL,
            competency_id INTEGER NOT NULL,
            current_level INTEGER NOT NULL CHECK (current_level BETWEEN 1 AND 5),
            last_assessed TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, competency_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (competency_id) REFERENCES competencies(competency_id)
        )
    """)

    # Courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            instructor TEXT,
            difficulty TEXT CHECK (difficulty IN ('Beginner', 'Intermediate', 'Advanced')),
            duration TEXT,
            status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Course Competencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_competencies (
            course_id INTEGER NOT NULL,
            competency_id INTEGER NOT NULL,
            target_level INTEGER NOT NULL CHECK (target_level BETWEEN 1 AND 5),
            PRIMARY KEY (course_id, competency_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id),
            FOREIGN KEY (competency_id) REFERENCES competencies(competency_id)
        )
    """)

    # Assessments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            title TEXT NOT NULL,
            passing_score INTEGER DEFAULT 70 CHECK (passing_score BETWEEN 0 AND 100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)

    # Questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,  -- JSON array of options
            correct_answer INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id)
        )
    """)

    # Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            assessment_id INTEGER NOT NULL,
            score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id)
        )
    """)

    # Knowledge Resources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_resources (
            resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            department TEXT,
            author_id INTEGER,
            file_path TEXT,
            status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'pending_review', 'approved', 'published')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(user_id)
        )
    """)

    # Knowledge Resource Competencies (many-to-many)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resource_competencies (
            resource_id INTEGER NOT NULL,
            competency_id INTEGER NOT NULL,
            PRIMARY KEY (resource_id, competency_id),
            FOREIGN KEY (resource_id) REFERENCES knowledge_resources(resource_id),
            FOREIGN KEY (competency_id) REFERENCES competencies(competency_id)
        )
    """)

    # User Course Enrollment
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_courses (
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_date TIMESTAMP,
            progress INTEGER DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
            status TEXT DEFAULT 'enrolled' CHECK (status IN ('enrolled', 'in_progress', 'completed', 'dropped')),
            PRIMARY KEY (user_id, course_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)

    # User Learning Path
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_learning_path (
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            sequence_order INTEGER NOT NULL,
            is_completed BOOLEAN DEFAULT 0,
            PRIMARY KEY (user_id, course_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)

    conn.commit()
    print("All tables created successfully!")

def seed_data(conn):
    """Seed database with initial demo data."""
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        print("Database already seeded, skipping...")
        return

    import bcrypt
    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Insert demo users
    demo_users = [
        (1, "Alex Johnson", "alex.johnson@company.com", "Analytics", "Environmental Data Analyst", "Data Analyst", "3 years", hash_password("demo123"), 0),
        (2, "Sarah Chen", "sarah.chen@company.com", "Analytics", "Environmental Data Analyst", "Senior Data Analyst", "5 years", hash_password("demo123"), 0),
        (3, "Michael Torres", "michael.torres@company.com", "Engineering", "Software Engineer", "Backend Developer", "4 years", hash_password("demo123"), 0),
        (4, "Admin User", "admin@company.com", "Management", "Administrator", "System Admin", "8 years", hash_password("admin123"), 1),
        (5, "Priya Sharma", "priya.sharma@company.com", "Engineering", "Software Engineer", "Frontend Developer", "2 years", hash_password("demo123"), 0),
        (6, "David Miller", "david.miller@company.com", "Management", "Product Manager", "Product Manager", "6 years", hash_password("demo123"), 0),
        (7, "Lisa Wang", "lisa.wang@company.com", "Analytics", "Environmental Data Analyst", "Junior Data Analyst", "1 year", hash_password("demo123"), 0),
    ]

    cursor.executemany("""
        INSERT INTO users (user_id, name, email, department, role, designation, experience, password_hash, is_admin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, demo_users)

    # Insert competencies
    competencies = [
        ("Python", "Python programming language for data analysis and automation"),
        ("Data Analysis", "Statistical analysis and data interpretation techniques"),
        ("GIS", "Geographic Information Systems and spatial analysis"),
        ("Statistics", "Statistical methods and probability theory"),
        ("Environmental Science", "Environmental science principles and applications"),
        ("Report Writing", "Technical and business report writing"),
        ("Data Visualization", "Creating effective data visualizations and dashboards"),
        ("Machine Learning", "Machine learning algorithms and model deployment"),
        ("SQL", "Structured Query Language for database management"),
        ("Project Management", "Project planning, execution, and monitoring"),
    ]

    cursor.executemany("""
        INSERT INTO competencies (name, description)
        VALUES (?, ?)
    """, competencies)

    # Insert role competencies for Environmental Data Analyst
    role_competencies = [
        ("Environmental Data Analyst", 1, 4),  # Python - Level 4
        ("Environmental Data Analyst", 2, 4),  # Data Analysis - Level 4
        ("Environmental Data Analyst", 3, 3),  # GIS - Level 3
        ("Environmental Data Analyst", 4, 3),  # Statistics - Level 3
        ("Environmental Data Analyst", 5, 4),  # Environmental Science - Level 4
        ("Environmental Data Analyst", 6, 3),  # Report Writing - Level 3
        ("Software Engineer", 1, 4),           # Python - Level 4
        ("Software Engineer", 8, 3),           # Machine Learning - Level 3
        ("Software Engineer", 9, 4),           # SQL - Level 4
        ("Software Engineer", 7, 3),           # Data Visualization - Level 3
    ]

    cursor.executemany("""
        INSERT INTO role_competencies (role_name, competency_id, required_level)
        VALUES (?, ?, ?)
    """, role_competencies)

    # Insert user competencies for demo users
    user_competencies = [
        # Alex Johnson (user_id=1) - Environmental Data Analyst
        (1, 1, 2, "2024-01-15 10:00:00"),  # Python: 2
        (1, 2, 2, "2024-01-15 10:00:00"),  # Data Analysis: 2
        (1, 3, 4, "2024-01-15 10:00:00"),  # GIS: 4
        (1, 4, 2, "2024-01-15 10:00:00"),  # Statistics: 2
        (1, 5, 4, "2024-01-15 10:00:00"),  # Environmental Science: 4
        (1, 6, 3, "2024-01-15 10:00:00"),  # Report Writing: 3

        # Sarah Chen (user_id=2) - Environmental Data Analyst
        (2, 1, 3, "2024-01-20 10:00:00"),  # Python: 3
        (2, 2, 3, "2024-01-20 10:00:00"),  # Data Analysis: 3
        (2, 3, 3, "2024-01-20 10:00:00"),  # GIS: 3
        (2, 4, 3, "2024-01-20 10:00:00"),  # Statistics: 3
        (2, 5, 4, "2024-01-20 10:00:00"),  # Environmental Science: 4
        (2, 6, 4, "2024-01-20 10:00:00"),  # Report Writing: 4

        # Michael Torres (user_id=3) - Software Engineer
        (3, 1, 4, "2024-02-01 10:00:00"),  # Python: 4
        (3, 8, 3, "2024-02-01 10:00:00"),  # Machine Learning: 3
        (3, 9, 4, "2024-02-01 10:00:00"),  # SQL: 4
        (3, 7, 2, "2024-02-01 10:00:00"),  # Data Visualization: 2
    ]

    cursor.executemany("""
        INSERT INTO user_competencies (user_id, competency_id, current_level, last_assessed)
        VALUES (?, ?, ?, ?)
    """, user_competencies)

    # Insert courses
    courses = [
        ("Python for Data Analysis", "Comprehensive Python course focused on data analysis using pandas, numpy, and visualization libraries", "Dr. Emily Watson", "Intermediate", "6 hours", "published"),
        ("Statistics Fundamentals", "Core statistical concepts for data analysis including probability, distributions, hypothesis testing", "Prof. James Anderson", "Beginner", "8 hours", "published"),
        ("Advanced Data Analysis", "Advanced techniques in data analysis including regression, time series, and multivariate analysis", "Dr. Emily Watson", "Advanced", "10 hours", "published"),
        ("GIS for Environmental Data", "Geographic Information Systems applied to environmental data analysis", "Dr. Robert Kim", "Intermediate", "5 hours", "published"),
        ("Environmental Report Writing", "Technical writing for environmental reports and assessments", "Ms. Lisa Chen", "Beginner", "4 hours", "published"),
        ("Data Visualization with Python", "Creating effective visualizations using matplotlib, seaborn, and plotly", "Dr. Emily Watson", "Intermediate", "5 hours", "published"),
        ("Introduction to Machine Learning", "Fundamentals of machine learning algorithms and applications", "Prof. James Anderson", "Advanced", "12 hours", "published"),
    ]

    cursor.executemany("""
        INSERT INTO courses (title, description, instructor, difficulty, duration, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, courses)

    # Insert course competencies
    course_competencies = [
        (1, 1, 3),  # Python for Data Analysis -> Python Level 3
        (1, 2, 3),  # Python for Data Analysis -> Data Analysis Level 3
        (1, 4, 2),  # Python for Data Analysis -> Statistics Level 2
        (2, 4, 3),  # Statistics Fundamentals -> Statistics Level 3
        (3, 2, 4),  # Advanced Data Analysis -> Data Analysis Level 4
        (3, 4, 3),  # Advanced Data Analysis -> Statistics Level 3
        (4, 3, 3),  # GIS for Environmental Data -> GIS Level 3
        (5, 6, 3),  # Environmental Report Writing -> Report Writing Level 3
        (6, 7, 3),  # Data Visualization with Python -> Data Visualization Level 3
        (6, 1, 2),  # Data Visualization with Python -> Python Level 2
        (7, 8, 3),  # Introduction to Machine Learning -> Machine Learning Level 3
        (7, 1, 3),  # Introduction to Machine Learning -> Python Level 3
    ]

    cursor.executemany("""
        INSERT INTO course_competencies (course_id, competency_id, target_level)
        VALUES (?, ?, ?)
    """, course_competencies)

    # Insert assessments
    assessments = [
        (1, "Python for Data Analysis Assessment", 70),
        (2, "Statistics Fundamentals Assessment", 70),
        (3, "Advanced Data Analysis Assessment", 75),
        (4, "GIS for Environmental Data Assessment", 70),
        (5, "Environmental Report Writing Assessment", 70),
        (None, "Python Competency Assessment", 0),  # Onboarding Assessment
    ]

    cursor.executemany("""
        INSERT INTO assessments (course_id, title, passing_score)
        VALUES (?, ?, ?)
    """, assessments)

    # Insert questions (sample questions for each assessment)
    import json
    questions = [
        # Assessment 1: Python for Data Analysis
        (1, 1, "Which pandas function is used to read a CSV file?", json.dumps(["pd.read_csv()", "pd.read_excel()", "pd.read_json()", "pd.read_sql()"]), 0),
        (2, 1, "What does df.head() return?", json.dumps(["First 5 rows", "Last 5 rows", "Column names", "Data types"]), 0),
        (3, 1, "How do you select a column in pandas?", json.dumps(["df.column", "df['column']", "df.column()", "Both A and B"]), 3),

        # Assessment 2: Statistics Fundamentals
        (4, 2, "What is the mean of [2, 4, 6, 8]?", json.dumps(["4", "5", "6", "7"]), 1),
        (5, 2, "Which measure is most affected by outliers?", json.dumps(["Mean", "Median", "Mode", "Range"]), 0),
        (6, 2, "What does a p-value < 0.05 indicate?", json.dumps(["Strong evidence against null hypothesis", "Strong evidence for null hypothesis", "No conclusion possible", "Data is normal"]), 0),

        # Assessment 3: Advanced Data Analysis
        (7, 3, "What is the purpose of cross-validation?", json.dumps(["Prevent overfitting", "Speed up training", "Reduce data size", "Increase accuracy"]), 0),
        (8, 3, "Which regression handles multicollinearity best?", json.dumps(["Linear Regression", "Ridge Regression", "Simple Regression", "Polynomial Regression"]), 1),

        # Assessment 4: GIS
        (9, 4, "What coordinate system does GPS use?", json.dumps(["UTM", "WGS84", "State Plane", "Mercator"]), 1),
        (10, 4, "What is a shapefile?", json.dumps(["A raster format", "A vector format", "A database", "An image format"]), 1),

        # Assessment 5: Report Writing
        (11, 5, "What should an executive summary include?", json.dumps(["All technical details", "Key findings and recommendations", "Raw data tables", "Methodology only"]), 1),

        # Assessment 6: Python Competency Assessment (Onboarding)
        (12, 6, "Which of the following is the correct syntax for creating a list in Python?", json.dumps(["{1, 2, 3}", "[1, 2, 3]", "(1, 2, 3)", "<1, 2, 3>"]), 1),
        (13, 6, "What will be the output of the following code?\nx = 10\ny = 3\nprint(x // y)", json.dumps(["3.33", "3", "4", "1"]), 1),
        (14, 6, "Which keyword is used to define a function in Python?", json.dumps(["function", "define", "def", "func"]), 2),
        (15, 6, "What will be the output of the following code?\nnumbers = [1, 2, 3, 4, 5]\nprint(numbers[2])", json.dumps(["1", "2", "3", "4"]), 2),
        (16, 6, "What will be the output of the following code?\nx = 5\nif x > 3:\n    print('Yes')\nelse:\n    print('No')", json.dumps(["Yes", "No", "5", "Error"]), 0),
    ]

    cursor.executemany("""
        INSERT INTO questions (question_id, assessment_id, question, options, correct_answer)
        VALUES (?, ?, ?, ?, ?)
    """, questions)

    # Insert some results
    results = [
        (1, 1, 65, "2024-01-20 14:00:00"),
        (1, 2, 55, "2024-01-25 14:00:00"),
        (2, 1, 82, "2024-01-22 14:00:00"),
        (2, 2, 78, "2024-01-27 14:00:00"),
        (3, 1, 90, "2024-02-05 14:00:00"),
    ]

    cursor.executemany("""
        INSERT INTO results (user_id, assessment_id, score, date)
        VALUES (?, ?, ?, ?)
    """, results)

    # Insert knowledge resources
    knowledge_resources = [
        (1, "Environmental Data Analysis Guidelines", "Best practices for analyzing environmental data", "Guidelines", "Analytics", 4, "/docs/env_data_guidelines.pdf", "published"),
        (2, "Case Study: River Water Quality Analysis", "Complete case study on river water quality monitoring", "Case Study", "Analytics", 2, "/docs/river_water_quality.pdf", "published"),
        (3, "Python Data Analysis Best Practices", "Tutorial on efficient Python data analysis workflows", "Tutorial", "Analytics", 4, "/docs/python_best_practices.pdf", "published"),
        (4, "GIS Data Standards", "Organizational standards for GIS data collection and management", "Guidelines", "Engineering", 4, "/docs/gis_standards.pdf", "published"),
        (5, "Statistical Methods Reference", "Quick reference for common statistical methods", "Reference", "Analytics", 2, "/docs/stats_reference.pdf", "published"),
    ]

    cursor.executemany("""
        INSERT INTO knowledge_resources (resource_id, title, description, category, department, author_id, file_path, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, knowledge_resources)

    # Insert resource competencies
    resource_competencies = [
        (1, 2), (1, 4), (1, 5),  # Env Data Analysis Guidelines
        (2, 2), (2, 3), (2, 5),  # River Water Quality Case Study
        (3, 1), (3, 2), (3, 7),  # Python Best Practices
        (4, 3), (4, 5),          # GIS Data Standards
        (5, 4), (5, 2),          # Statistical Methods Reference
    ]

    cursor.executemany("""
        INSERT INTO resource_competencies (resource_id, competency_id)
        VALUES (?, ?)
    """, resource_competencies)

    # Insert user course enrollments
    user_courses = [
        (1, 1, "2024-01-15", None, 30, "in_progress"),   # Alex - Python for Data Analysis
        (1, 2, "2024-01-15", None, 10, "enrolled"),      # Alex - Statistics Fundamentals
        (2, 1, "2024-01-20", "2024-02-01", 100, "completed"),  # Sarah - Python for Data Analysis
        (2, 2, "2024-01-20", "2024-02-05", 100, "completed"),  # Sarah - Statistics Fundamentals
        (2, 3, "2024-02-06", None, 40, "in_progress"),   # Sarah - Advanced Data Analysis
        (3, 6, "2024-02-01", None, 20, "enrolled"),      # Michael - Data Visualization
        (3, 7, "2024-02-01", None, 0, "enrolled"),       # Michael - Intro to ML
    ]

    cursor.executemany("""
        INSERT INTO user_courses (user_id, course_id, enrollment_date, completion_date, progress, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, user_courses)

    # Insert learning paths
    learning_path = [
        (1, 1, 1, 0),  # Alex - Python for Data Analysis - Step 1
        (1, 2, 2, 0),  # Alex - Statistics Fundamentals - Step 2
        (1, 3, 3, 0),  # Alex - Advanced Data Analysis - Step 3
        (1, 5, 4, 0),  # Alex - Environmental Report Writing - Step 4
        (2, 1, 1, 1),  # Sarah - Python for Data Analysis - Step 1 (completed)
        (2, 2, 2, 1),  # Sarah - Statistics Fundamentals - Step 2 (completed)
        (2, 3, 3, 0),  # Sarah - Advanced Data Analysis - Step 3
    ]

    cursor.executemany("""
        INSERT INTO user_learning_path (user_id, course_id, sequence_order, is_completed)
        VALUES (?, ?, ?, ?)
    """, learning_path)

    conn.commit()
    print("Demo data seeded successfully!")

def main():
    """Main function to create database and seed data."""
    print(f"Creating database at: {DB_PATH}")

    # Remove existing database if it exists
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("Removed existing database")

    conn = get_connection()
    try:
        create_tables(conn)
        seed_data(conn)
        print("\nDatabase setup complete!")
        print(f"Database location: {DB_PATH}")

        # Verify tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\nTables created ({len(tables)}):")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} rows")

    finally:
        conn.close()

if __name__ == "__main__":
    main()