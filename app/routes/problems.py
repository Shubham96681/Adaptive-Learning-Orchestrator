from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel, Field
from app.models.problem import Problem, ProblemCreate, ProblemUpdate
from app.services.problem_service import problem_service
import uuid
import os

router = APIRouter(prefix="/api/problems", tags=["problems"])


@router.get("", response_model=List[Problem], status_code=status.HTTP_200_OK)
async def get_problems():
    """Get all problems."""
    return problem_service.get_all()


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_problems_stats():
    """Get statistics about loaded problems."""
    all_problems = problem_service.get_all()
    topics = {}
    difficulty_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    for problem in all_problems:
        # Count by topic
        topics[problem.topic] = topics.get(problem.topic, 0) + 1
        # Count by difficulty
        if 1 <= problem.difficulty <= 5:
            difficulty_distribution[problem.difficulty] += 1
    
    return {
        "total_problems": len(all_problems),
        "topics": topics,
        "difficulty_distribution": difficulty_distribution
    }


@router.get("/{problem_id}", response_model=Problem, status_code=status.HTTP_200_OK)
async def get_problem(problem_id: str):
    """Get a problem by ID."""
    problem = problem_service.get_by_id(problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with ID {problem_id} not found"
        )
    return problem


@router.post("", response_model=Problem, status_code=status.HTTP_201_CREATED)
async def create_problem(problem_data: ProblemCreate):
    """Create a new problem."""
    problem = problem_service.create(problem_data.model_dump())
    return problem


@router.put("/{problem_id}", response_model=Problem, status_code=status.HTTP_200_OK)
async def update_problem(problem_id: str, problem_data: ProblemUpdate):
    """Update an existing problem."""
    update_dict = problem_data.model_dump(exclude_unset=True)
    problem = problem_service.update(problem_id, update_dict)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with ID {problem_id} not found"
        )
    return problem


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(problem_id: str):
    """Delete a problem by ID."""
    success = problem_service.delete(problem_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with ID {problem_id} not found"
        )
    return None


class LoadProblemsRequest(BaseModel):
    """Request model for loading problems from JSON file."""
    file_path: str = Field(..., description="Path to JSON file containing problems")
    clear_existing: bool = Field(default=False, description="Whether to clear existing problems before loading")


@router.post("/load", status_code=status.HTTP_200_OK)
async def load_problems(request: LoadProblemsRequest):
    """
    Load problems from a JSON file.
    
    The JSON file should be an array of problem objects with:
    - id (string)
    - text (string)
    - topic (string)
    - difficulty (int, 1-5)
    - estimated_time_to_solve_minutes (int)
    """
    try:
        if request.clear_existing:
            cleared = problem_service.clear_all()
        
        loaded_count = problem_service.load_from_json(request.file_path)
        
        return {
            "message": f"Successfully loaded {loaded_count} problems",
            "loaded_count": loaded_count,
            "cleared_existing": request.clear_existing
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading problems: {str(e)}"
        )

