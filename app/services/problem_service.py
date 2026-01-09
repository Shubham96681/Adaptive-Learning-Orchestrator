from typing import List, Optional, Dict
from app.models.problem import Problem
import uuid
import json
import os
from pathlib import Path
from app.services.database import db


class ProblemService:
    """Service for managing problems with SQLite database."""
    
    def __init__(self):
        """Initialize problem service with database."""
        self.db = db
    
    def get_all(self) -> List[Problem]:
        """Get all problems."""
        results = self.db.execute_query("SELECT * FROM problems")
        return [self._row_to_problem(row) for row in results]
    
    def get_by_id(self, problem_id: str) -> Optional[Problem]:
        """Get a problem by ID."""
        results = self.db.execute_query(
            "SELECT * FROM problems WHERE id = ?",
            (problem_id,)
        )
        if results:
            return self._row_to_problem(results[0])
        return None
    
    def create(self, problem_data: dict) -> Problem:
        """Create a new problem."""
        problem_id = str(uuid.uuid4())
        problem = Problem(
            id=problem_id,
            **problem_data
        )
        
        self.db.execute_update(
            """INSERT INTO problems (id, text, topic, difficulty, estimated_time_to_solve_minutes)
               VALUES (?, ?, ?, ?, ?)""",
            (
                problem.id,
                problem.text,
                problem.topic,
                problem.difficulty,
                problem.estimated_time_to_solve_minutes
            )
        )
        
        return problem
    
    def update(self, problem_id: str, problem_data: dict) -> Optional[Problem]:
        """Update an existing problem."""
        existing = self.get_by_id(problem_id)
        if not existing:
            return None
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        if "text" in problem_data:
            update_fields.append("text = ?")
            values.append(problem_data["text"])
        if "topic" in problem_data:
            update_fields.append("topic = ?")
            values.append(problem_data["topic"])
        if "difficulty" in problem_data:
            update_fields.append("difficulty = ?")
            values.append(problem_data["difficulty"])
        if "estimated_time_to_solve_minutes" in problem_data:
            update_fields.append("estimated_time_to_solve_minutes = ?")
            values.append(problem_data["estimated_time_to_solve_minutes"])
        
        if not update_fields:
            return existing
        
        values.append(problem_id)
        query = f"UPDATE problems SET {', '.join(update_fields)} WHERE id = ?"
        
        self.db.execute_update(query, tuple(values))
        
        return self.get_by_id(problem_id)
    
    def delete(self, problem_id: str) -> bool:
        """Delete a problem by ID."""
        affected = self.db.execute_update(
            "DELETE FROM problems WHERE id = ?",
            (problem_id,)
        )
        return affected > 0
    
    def get_by_topic_and_difficulty(
        self,
        topic: str,
        difficulty_min: int,
        difficulty_max: int
    ) -> List[Problem]:
        """Get problems filtered by topic and difficulty range."""
        results = self.db.execute_query(
            """SELECT * FROM problems 
               WHERE topic = ? AND difficulty >= ? AND difficulty <= ?
               ORDER BY difficulty, id""",
            (topic, difficulty_min, difficulty_max)
        )
        return [self._row_to_problem(row) for row in results]
    
    def get_by_topic(self, topic: str) -> List[Problem]:
        """Get all problems for a specific topic."""
        results = self.db.execute_query(
            "SELECT * FROM problems WHERE topic = ? ORDER BY difficulty, id",
            (topic,)
        )
        return [self._row_to_problem(row) for row in results]
    
    def load_from_json(self, file_path: str) -> int:
        """
        Load problems from a JSON file into the database.
        
        Args:
            file_path: Path to the JSON file containing problems
            
        Returns:
            Number of problems loaded
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Problem set file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            problems_data = json.load(f)
        
        loaded_count = 0
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            for problem_data in problems_data:
                try:
                    # Validate and create Problem model
                    problem = Problem(**problem_data)
                    
                    # Check if problem already exists
                    cursor.execute("SELECT id FROM problems WHERE id = ?", (problem.id,))
                    if cursor.fetchone():
                        continue  # Skip if already exists
                    
                    # Insert problem
                    cursor.execute(
                        """INSERT INTO problems (id, text, topic, difficulty, estimated_time_to_solve_minutes)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            problem.id,
                            problem.text,
                            problem.topic,
                            problem.difficulty,
                            problem.estimated_time_to_solve_minutes
                        )
                    )
                    loaded_count += 1
                except Exception as e:
                    # Skip invalid problems but continue loading
                    print(f"Warning: Skipped invalid problem: {e}")
                    continue
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        
        return loaded_count
    
    def clear_all(self) -> int:
        """
        Clear all problems from storage.
        
        Returns:
            Number of problems cleared
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM problems")
        count = cursor.fetchone()[0]
        cursor.execute("DELETE FROM problems")
        conn.commit()
        conn.close()
        return count
    
    def _row_to_problem(self, row) -> Problem:
        """Convert database row to Problem model."""
        return Problem(
            id=row["id"],
            text=row["text"],
            topic=row["topic"],
            difficulty=row["difficulty"],
            estimated_time_to_solve_minutes=row["estimated_time_to_solve_minutes"]
        )


# Global instance
problem_service = ProblemService()
