import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger("MedicalApp.Database")

class DBManager:
    """Manages SQLite database initialization, connection, and queries."""
    
    def __init__(self, db_path: str = None):
        """Initializes database path and creates tables if they do not exist."""
        if db_path is None:
            # Place database in the same directory as db_manager.py
            db_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(db_dir, "medical_analysis.db")
        else:
            self.db_path = db_path
            
        self._initialize_database()

    def get_connection(self):
        """Returns a connection to the SQLite database with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _initialize_database(self):
        """Creates database tables if they do not exist."""
        logger.info(f"Initializing database at: {self.db_path}")
        if self.db_path != ":memory:":
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Reports Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_type TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
                );
            """)
            
            # ExtractedParameters Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ExtractedParameters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    parameter_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    extracted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES Reports(id) ON DELETE CASCADE
                );
            """)
            
            # AnalysisResults Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS AnalysisResults (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    parameter_id INTEGER NOT NULL,
                    classification TEXT NOT NULL,
                    reference_range TEXT NOT NULL,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES Reports(id) ON DELETE CASCADE,
                    FOREIGN KEY (parameter_id) REFERENCES ExtractedParameters(id) ON DELETE CASCADE
                );
            """)
            
            # History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS History (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    report_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
                    FOREIGN KEY (report_id) REFERENCES Reports(id) ON DELETE CASCADE
                );
            """)
            
            conn.commit()
        logger.info("Database initialized successfully.")

    # --- User Management Operations ---
    
    def create_user(self, username: str, email: str, password_hash: str) -> int:
        """Inserts a new user. Returns the user's ID or -1 if failed."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username.lower().strip(), email.lower().strip(), password_hash)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logger.warning(f"Failed to create user (username/email exists): {e}")
            return -1
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return -1

    def get_user_by_username(self, username: str):
        """Retrieves user row by username."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Users WHERE username = ?", (username.lower().strip(),))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error fetching user by username: {e}")
            return None

    def get_user_by_email(self, email: str):
        """Retrieves user row by email."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Users WHERE email = ?", (email.lower().strip(),))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            return None

    def get_user_by_id(self, user_id: int):
        """Retrieves user row by user_id."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            return None

    # --- Report Management Operations ---

    def add_report(self, user_id: int, file_path: str, file_type: str) -> int:
        """Adds a report entry. Returns the report ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Reports (user_id, file_path, file_type) VALUES (?, ?, ?)",
                    (user_id, file_path, file_type)
                )
                report_id = cursor.lastrowid
                
                # Log to History
                cursor.execute(
                    "INSERT INTO History (user_id, report_id, action) VALUES (?, ?, ?)",
                    (user_id, report_id, "Uploaded Report")
                )
                conn.commit()
                return report_id
        except Exception as e:
            logger.error(f"Error adding report: {e}")
            return -1

    def delete_report(self, report_id: int, user_id: int) -> bool:
        """Deletes a report and cascaded entities. Logs action to history first if possible."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Fetch details before deleting for audit trail or logs
                cursor.execute("SELECT file_path FROM Reports WHERE id = ? AND user_id = ?", (report_id, user_id))
                report = cursor.fetchone()
                if not report:
                    return False
                
                # We need to log deletion. Note: since history references report_id with a foreign key,
                # if we have ON DELETE CASCADE, the history records referencing this report_id will be deleted.
                # To log deletion, we might want to log it as a general log or just let cascade delete it.
                # Let's perform cascade delete:
                cursor.execute("DELETE FROM Reports WHERE id = ? AND user_id = ?", (report_id, user_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting report {report_id}: {e}")
            return False

    def get_user_reports(self, user_id: int):
        """Gets all reports for a user."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Reports WHERE user_id = ? ORDER BY upload_date DESC", (user_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching user reports: {e}")
            return []

    def get_report_by_id(self, report_id: int, user_id: int):
        """Gets a report by ID for security checks."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Reports WHERE id = ? AND user_id = ?", (report_id, user_id))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error fetching report: {e}")
            return None

    # --- Parameter and Analysis Operations ---

    def add_extracted_parameter(self, report_id: int, name: str, value: float, unit: str) -> int:
        """Inserts an extracted parameter."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO ExtractedParameters (report_id, parameter_name, value, unit) VALUES (?, ?, ?, ?)",
                    (report_id, name, value, unit)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding parameter: {e}")
            return -1

    def add_analysis_result(self, report_id: int, parameter_id: int, classification: str, reference_range: str) -> int:
        """Inserts an analysis result."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO AnalysisResults (report_id, parameter_id, classification, reference_range) VALUES (?, ?, ?, ?)",
                    (report_id, parameter_id, classification, reference_range)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding analysis result: {e}")
            return -1

    def get_report_analysis_details(self, report_id: int):
        """Retrieves all parameters and classifications for a specific report."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.id as parameter_id, p.parameter_name, p.value, p.unit, p.extracted_date,
                           a.id as analysis_id, a.classification, a.reference_range
                    FROM ExtractedParameters p
                    LEFT JOIN AnalysisResults a ON p.id = a.parameter_id
                    WHERE p.report_id = ?
                    ORDER BY p.parameter_name ASC
                """, (report_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching analysis details: {e}")
            return []

    # --- History Auditing with Search & Filter ---

    def add_history_entry(self, user_id: int, report_id: int, action: str):
        """Manually records an action in history."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO History (user_id, report_id, action) VALUES (?, ?, ?)",
                    (user_id, report_id, action)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error adding history entry: {e}")

    def query_history(self, user_id: int, search_query: str = None, filter_status: str = None, start_date: str = None, end_date: str = None):
        """
        Retrieves historical reports matching search queries and filter options.
        Filters by:
        - search_query (matches filename in file_path, parameter_name, or action)
        - filter_status (matches classification: e.g. Normal, Critical, High, Low)
        - date ranges (YYYY-MM-DD)
        """
        try:
            query = """
                SELECT DISTINCT r.id as report_id, r.file_path, r.upload_date, r.file_type
                FROM Reports r
                LEFT JOIN ExtractedParameters p ON r.id = p.report_id
                LEFT JOIN AnalysisResults a ON p.id = a.parameter_id
                WHERE r.user_id = ?
            """
            params = [user_id]

            if search_query:
                query += " AND (r.file_path LIKE ? OR p.parameter_name LIKE ?)"
                like_term = f"%{search_query}%"
                params.extend([like_term, like_term])

            if filter_status:
                query += " AND a.classification = ?"
                params.append(filter_status)

            if start_date:
                query += " AND r.upload_date >= ?"
                params.append(f"{start_date} 00:00:00")

            if end_date:
                query += " AND r.upload_date <= ?"
                params.append(f"{end_date} 23:59:59")

            query += " ORDER BY r.upload_date DESC"

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error querying history: {e}")
            return []

    # --- Dashboard Metric Analytics ---

    def get_dashboard_summary(self, user_id: int):
        """Returns summary statistics for the dashboard dashboard."""
        stats = {
            "total_reports": 0,
            "critical_parameters": 0,
            "health_score": 100
        }
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total reports
                cursor.execute("SELECT COUNT(*) FROM Reports WHERE user_id = ?", (user_id,))
                stats["total_reports"] = cursor.fetchone()[0]
                
                if stats["total_reports"] == 0:
                    return stats
                
                # Count critical/high classifications in recent reports
                # Let's count how many parameters are Critical, High, Low, or Normal in the user's latest report
                cursor.execute("SELECT id FROM Reports WHERE user_id = ? ORDER BY upload_date DESC LIMIT 1", (user_id,))
                latest_report = cursor.fetchone()
                if latest_report:
                    latest_id = latest_report[0]
                    cursor.execute("""
                        SELECT classification, COUNT(*) 
                        FROM AnalysisResults 
                        WHERE report_id = ? 
                        GROUP BY classification
                    """, (latest_id,))
                    class_counts = dict(cursor.fetchall())
                    
                    critical = class_counts.get("Critical", 0)
                    high = class_counts.get("High", 0)
                    low = class_counts.get("Low", 0)
                    normal = class_counts.get("Normal", 0)
                    
                    stats["critical_parameters"] = critical
                    
                    # Calculate a simple health score:
                    # Start at 100.
                    # Critical counts as -15 points each.
                    # High/Low counts as -5 points each.
                    # Normal counts as +0 points.
                    # Minimum score = 10.
                    total_p = critical + high + low + normal
                    if total_p > 0:
                        score = 100 - (critical * 20) - (high * 8) - (low * 5)
                        stats["health_score"] = max(10, min(100, score))
                    else:
                        stats["health_score"] = 100
                        
            return stats
        except Exception as e:
            logger.error(f"Error fetching dashboard summary: {e}")
            return stats

    def get_parameter_trends(self, user_id: int, parameter_name: str):
        """Retrieves values and dates for a specific parameter for line chart trends."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.value, r.upload_date
                    FROM ExtractedParameters p
                    JOIN Reports r ON p.report_id = r.id
                    WHERE r.user_id = ? AND LOWER(p.parameter_name) = LOWER(?)
                    ORDER BY r.upload_date ASC
                """, (user_id, parameter_name))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching parameter trends: {e}")
            return []
