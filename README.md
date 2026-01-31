Adaptive Learning Orchestrator

A production-ready FastAPI application for generating adaptive learning assessments using a Planner–Executor architecture.
The system cleanly separates decision-making from execution, making it scalable, testable, and LLM-ready by design.

🚀 Overview

The Adaptive Learning Orchestrator creates personalized assessments based on a student’s knowledge, learning goals, and pedagogical strategy.

It follows a simple but powerful idea:

Plan first. Execute second.

🧠 Planner decides what the assessment should look like

🛠 Executor builds the assessment by selecting suitable problems

This separation allows future AI/LLM integration without changing the core system.

🏗 Architecture
Planner–Executor Pattern
Component	Responsibility
Planner	Converts student intent and strategy into a structured assessment plan
Executor	Follows the plan and selects matching problems

The two components communicate through a strict contract called AssessmentPlan.

🧠 Planner

📍 app/planners/assessment_planner.py

Role:
Transforms student data and pedagogical intent into a concrete, machine-readable plan.

Input

Student profile (ID, mastered topics, learning goals)

Assessment request (strategy, time limit)

Output

AssessmentPlan containing:

Teaching strategy

Topic rules (topic, difficulty range, question count)

Time limit

Human-readable reasoning

Supported Strategies

REVIEW – Reinforce mastered topics

NEW_TOPIC_INTRODUCTION – Introduce new topics gradually

CHALLENGE – Mix topics with higher difficulty

Key Characteristics

No database access

Pure decision logic

Deterministic and easy to replace with LLM reasoning

🛠 Executor

📍 app/executors/assessment_executor.py

Role:
Executes the assessment plan exactly as provided.

Input

AssessmentPlan

Output

Selected problems

Total estimated time

Key Characteristics

No strategic decision-making

Enforces time and difficulty constraints

Interacts with the problem database

📜 AssessmentPlan (Contract)

The AssessmentPlan is the contract between the Planner and Executor.

{
  "strategy": "NEW_TOPIC_INTRODUCTION",
  "topic_rules": [
    {
      "topic": "Calculus",
      "difficulty_range": [1, 2],
      "question_count": 5
    }
  ],
  "time_limit_minutes": 60,
  "reasoning_log": "Explanation of planning decisions"
}


Why this matters

Clear separation of responsibilities

Easy validation and debugging

Ideal for future LLM integration

Extensible without breaking existing logic

🔌 LLM-Ready Design

This architecture supports AI integration without refactoring:

Replace the Planner with an LLM

Use LLMs only for reasoning explanations

Enhance problem selection with AI logic

All without changing the Executor or API layer.

🗄 Data & Storage
Current

SQLite database (problems.db)

Indexed by topic and difficulty

Persistent across restarts

Scalable Path

Swap SQLite with PostgreSQL or MongoDB

Add Redis for caching

No changes required in Planner or Executor logic

📁 Project Structure
app/
 ├── main.py
 ├── models/
 │    ├── student.py
 │    ├── assessment.py
 │    └── problem.py
 ├── planners/
 │    └── assessment_planner.py
 ├── executors/
 │    └── assessment_executor.py
 ├── routes/
 │    ├── assessments.py
 │    └── problems.py
 └── services/
      └── problem_service.py

⚙ Installation
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

▶ Running the App
uvicorn app.main:app --reload


Available at

API: http://localhost:8000

Docs: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

📡 API Endpoints
Generate Assessment

POST /api/assessments/generate

Request

{
  "student_profile": {
    "id": "student-123",
    "mastered_topics": ["Arithmetic"],
    "learning_goals": ["Calculus"]
  },
  "assessment_request": {
    "pedagogical_strategy": "NEW_TOPIC_INTRODUCTION",
    "max_total_time_minutes": 60
  }
}


Response

Assessment plan with reasoning

Selected problems

Total estimated time

🎯 Design Principles

Clear separation of planning and execution

Typed contracts using Pydantic

Service-layer abstraction for data access

UUIDs for secure, scalable IDs

Built for extensibility and AI adoption

🔮 Future Enhancements

LLM-powered planner

PostgreSQL / MongoDB support

Redis caching

Learning analytics

Real-time difficulty adjustment

Multi-subject support

📄 License

This project is part of a coding challenge and is provided as-is.