from pydantic import BaseModel, Field
from typing import List, Optional


class StudentProfile(BaseModel):
    """Student profile containing learning information."""
    id: str = Field(..., description="Unique student identifier")
    mastered_topics: List[str] = Field(default_factory=list, description="List of topics the student has mastered")
    learning_goals: List[str] = Field(default_factory=list, description="List of learning goals for the student")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "student-123",
                "mastered_topics": ["Basic Arithmetic", "Fractions"],
                "learning_goals": ["Introduction to Algebra", "Geometry Fundamentals"]
            }
        }

