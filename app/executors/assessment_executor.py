from typing import List
from app.models.assessment import AssessmentPlan, SelectedProblem, ExecutorOutput
from app.services.problem_service import problem_service


class AssessmentExecutor:
    """Executor that selects problems based on the assessment plan."""
    
    def execute(self, assessment_plan: AssessmentPlan) -> ExecutorOutput:
        """
        Execute the assessment plan by selecting appropriate problems.
        
        The executor:
        1. Queries problems based on topic rules
        2. Filters by difficulty range
        3. Ensures total time <= time_limit
        4. Returns selected problems
        """
        selected_problems: List[SelectedProblem] = []
        total_time = 0
        
        # Process each topic rule
        for topic_rule in assessment_plan.topic_rules:
            # Get problems matching topic and difficulty
            available_problems = problem_service.get_by_topic_and_difficulty(
                topic=topic_rule.topic,
                difficulty_min=topic_rule.difficulty_range[0],
                difficulty_max=topic_rule.difficulty_range[1]
            )
            
            # Select problems up to the required count
            remaining_slots = topic_rule.question_count
            remaining_time = assessment_plan.time_limit_minutes - total_time
            
            for problem in available_problems:
                if remaining_slots <= 0:
                    break
                
                # Check if adding this problem would exceed time limit
                if total_time + problem.estimated_time_to_solve_minutes > assessment_plan.time_limit_minutes:
                    continue
                
                # Add problem to selection
                selected_problems.append(SelectedProblem(
                    id=problem.id,
                    text=problem.text,
                    topic=problem.topic,
                    difficulty=problem.difficulty,
                    estimated_time_to_solve_minutes=problem.estimated_time_to_solve_minutes
                ))
                
                total_time += problem.estimated_time_to_solve_minutes
                remaining_slots -= 1
        
        return ExecutorOutput(
            selected_problems=selected_problems,
            total_estimated_time=total_time
        )


# Global instance
assessment_executor = AssessmentExecutor()

