"""Database initialization and connection management."""
import sqlite3
import os
from pathlib import Path
from typing import Optional


class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Default to project root
            project_root = Path(__file__).parent.parent.parent
            db_path = os.path.join(project_root, "problems.db")
        
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database and tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create problems table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty INTEGER NOT NULL CHECK (difficulty >= 1 AND difficulty <= 5),
                estimated_time_to_solve_minutes INTEGER NOT NULL CHECK (estimated_time_to_solve_minutes > 0)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_topic_difficulty 
            ON problems(topic, difficulty)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_topic 
            ON problems(topic)
        """)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        # Return rows as dictionaries for easier access
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute a SELECT query and return results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def execute_update(self, query: str, params: tuple = ()):
        """Execute an INSERT/UPDATE/DELETE query."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        return affected_rows


# Global database instance
db = Database()

