from pydantic import BaseModel, Field
from typing import Optional


class Problem(BaseModel):
    """Problem model for the learning system."""
    id: str = Field(..., description="Unique problem identifier")
    text: str = Field(..., description="Problem text/question")
    topic: str = Field(..., description="Topic category")
    difficulty: int = Field(..., ge=1, le=5, description="Difficulty level (1-5)")
    estimated_time_to_solve_minutes: int = Field(..., ge=1, description="Estimated time to solve in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "problem-123",
                "text": "Solve the integral: ∫x²dx",
                "topic": "calculus",
                "difficulty": 3,
                "time_to_solve_minutes": 10
            }
        }


class ProblemCreate(BaseModel):
    """Request model for creating a problem."""
    text: str = Field(..., min_length=1, description="Problem text/question")
    topic: str = Field(..., min_length=1, description="Topic category")
    difficulty: int = Field(..., ge=1, le=5, description="Difficulty level (1-5)")
    estimated_time_to_solve_minutes: int = Field(..., ge=1, description="Estimated time to solve in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Solve the integral: ∫x²dx",
                "topic": "calculus",
                "difficulty": 3,
                "estimated_time_to_solve_minutes": 10
            }
        }


class ProblemUpdate(BaseModel):
    """Request model for updating a problem."""
    text: Optional[str] = Field(None, min_length=1, description="Problem text/question")
    topic: Optional[str] = Field(None, min_length=1, description="Topic category")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="Difficulty level (1-5)")
    estimated_time_to_solve_minutes: Optional[int] = Field(None, ge=1, description="Estimated time to solve in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Solve the integral: ∫x²dx",
                "topic": "calculus",
                "difficulty": 4,
                "estimated_time_to_solve_minutes": 12
            }
        }

