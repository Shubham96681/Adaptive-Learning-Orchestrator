from fastapi import APIRouter, HTTPException, status
from app.models.student import StudentProfile
from app.models.assessment import (
    AssessmentRequest,
    AssessmentResponse,
    PlannerOutput
)
from app.planners.assessment_planner import assessment_planner
from app.executors.assessment_executor import assessment_executor
import uuid

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.post("/generate", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def generate_assessment(
    student_profile: StudentProfile,
    assessment_request: AssessmentRequest
):
    """
    Generate an assessment using Planner-Executor architecture.
    
    1. Planner analyzes student profile and request to create AssessmentPlan
    2. Executor uses the plan to select appropriate problems
    3. Returns assessment with both planner and executor outputs
    """
    try:
        # Step 1: Planner generates assessment plan
        assessment_plan = assessment_planner.generate_plan(
            student_profile=student_profile,
            assessment_request=assessment_request
        )
        
        planner_output = PlannerOutput(
            assessment_plan=assessment_plan,
            reasoning_log=assessment_plan.reasoning_log
        )
        
        # Step 2: Executor selects problems based on plan
        executor_output = assessment_executor.execute(assessment_plan)
        
        # Step 3: Generate assessment ID
        assessment_id = str(uuid.uuid4())
        
        # Step 4: Return response
        return AssessmentResponse(
            assessment_id=assessment_id,
            planner_output=planner_output,
            executor_output=executor_output
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating assessment: {str(e)}"
        )

