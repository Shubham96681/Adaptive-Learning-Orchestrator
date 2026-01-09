from typing import List
from app.models.student import StudentProfile
from app.models.assessment import AssessmentPlan, AssessmentRequest, TopicRule


class AssessmentPlanner:
    """Planner that generates assessment plans based on student profile and request."""
    
    def generate_plan(
        self,
        student_profile: StudentProfile,
        assessment_request: AssessmentRequest
    ) -> AssessmentPlan:
        """
        Generate an assessment plan based on student profile and request.
        
        This planner analyzes:
        - Mastered topics (to avoid or use for review)
        - Learning goals (to prioritize)
        - Current level (to set difficulty)
        - Pedagogical strategy (to determine approach)
        """
        strategy = assessment_request.pedagogical_strategy or "REVIEW"
        time_limit = assessment_request.max_total_time_minutes
        
        # Determine base difficulty from mastered topics and learning goals
        # If student has many mastered topics, assume higher level
        base_difficulty = 2  # Default
        if len(student_profile.mastered_topics) > 3:
            base_difficulty = 3
        if len(student_profile.mastered_topics) > 5:
            base_difficulty = 4
        
        # Generate topic rules based on strategy
        topic_rules = self._generate_topic_rules(
            student_profile=student_profile,
            assessment_request=assessment_request,
            base_difficulty=base_difficulty,
            strategy=strategy
        )
        
        # Generate reasoning log
        reasoning_log = self._generate_reasoning_log(
            student_profile=student_profile,
            assessment_request=assessment_request,
            strategy=strategy,
            topic_rules=topic_rules,
            time_limit=time_limit
        )
        
        return AssessmentPlan(
            strategy=strategy,
            topic_rules=topic_rules,
            time_limit_minutes=time_limit,
            reasoning_log=reasoning_log
        )
    
    def _generate_topic_rules(
        self,
        student_profile: StudentProfile,
        assessment_request: AssessmentRequest,
        base_difficulty: int,
        strategy: str
    ) -> List[TopicRule]:
        """Generate topic rules based on strategy and student profile."""
        topic_rules = []
        
        # Determine topics to focus on based on strategy
        if strategy == "REVIEW":
            # REVIEW: Focus on mastered topics to reinforce learning
            target_topics = student_profile.mastered_topics[:3] if student_profile.mastered_topics else student_profile.learning_goals[:2]
            for topic in target_topics:
                # Review at current or slightly higher difficulty
                difficulty_range = (base_difficulty, min(5, base_difficulty + 1))
                question_count = 4
                topic_rules.append(TopicRule(
                    topic=topic,
                    difficulty_range=difficulty_range,
                    question_count=question_count
                ))
        
        elif strategy == "NEW_TOPIC_INTRODUCTION":
            # NEW_TOPIC_INTRODUCTION: Focus on learning goals, start easier
            target_topics = student_profile.learning_goals[:3] if student_profile.learning_goals else ["general"]
            for i, topic in enumerate(target_topics):
                # Start easier for new topics, gradually increase
                difficulty_min = max(1, base_difficulty - 1)
                difficulty_max = min(5, base_difficulty + i)
                question_count = 5
                topic_rules.append(TopicRule(
                    topic=topic,
                    difficulty_range=(difficulty_min, difficulty_max),
                    question_count=question_count
                ))
        
        elif strategy == "CHALLENGE":
            # CHALLENGE: Mix mastered and new topics at higher difficulty
            all_topics = list(set(student_profile.mastered_topics + student_profile.learning_goals))[:3]
            if not all_topics:
                all_topics = ["general"]
            for topic in all_topics:
                # Challenge at higher difficulty
                difficulty_range = (min(4, base_difficulty + 1), 5)
                question_count = 4
                topic_rules.append(TopicRule(
                    topic=topic,
                    difficulty_range=difficulty_range,
                    question_count=question_count
                ))
        
        else:
            # Default: Balanced approach using learning goals
            target_topics = student_profile.learning_goals[:2] if student_profile.learning_goals else ["general"]
            for topic in target_topics:
                difficulty_range = (max(1, base_difficulty - 1), min(5, base_difficulty + 1))
                question_count = 5
                topic_rules.append(TopicRule(
                    topic=topic,
                    difficulty_range=difficulty_range,
                    question_count=question_count
                ))
        
        return topic_rules
    
    def _generate_reasoning_log(
        self,
        student_profile: StudentProfile,
        assessment_request: AssessmentRequest,
        strategy: str,
        topic_rules: List[TopicRule],
        time_limit: int
    ) -> str:
        """Generate a detailed reasoning log explaining the plan."""
        log_parts = [
            f"Assessment Plan Reasoning:",
            f"- Strategy: {strategy}",
            f"- Student ID: {student_profile.id}",
            f"- Mastered Topics: {', '.join(student_profile.mastered_topics) or 'None'}",
            f"- Learning Goals: {', '.join(student_profile.learning_goals) or 'None'}",
            f"- Time Limit: {time_limit} minutes",
            f"- Topics Selected: {len(topic_rules)}",
        ]
        
        for rule in topic_rules:
            log_parts.append(
                f"  * {rule.topic}: {rule.question_count} questions, "
                f"difficulty {rule.difficulty_range[0]}-{rule.difficulty_range[1]}"
            )
        
        if strategy == "REVIEW":
            log_parts.append(
                "- Approach: Reviewing mastered topics to reinforce learning"
            )
        elif strategy == "NEW_TOPIC_INTRODUCTION":
            log_parts.append(
                "- Approach: Introducing new topics at appropriate difficulty level"
            )
        elif strategy == "CHALLENGE":
            log_parts.append(
                "- Approach: Challenging student with higher difficulty problems"
            )
        
        return "\n".join(log_parts)


# Global instance
assessment_planner = AssessmentPlanner()

