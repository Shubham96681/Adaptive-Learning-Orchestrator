from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import assessments, problems
from app.services.problem_service import problem_service
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Load problem set if it exists and database is empty
    from app.services.database import db
    
    # Check if database has any problems
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM problems")
    existing_count = cursor.fetchone()[0]
    conn.close()
    
    if existing_count == 0:
        # Database is empty, try to load from JSON
        problem_set_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ProblemSet (2) (3).json")
        if os.path.exists(problem_set_path):
            try:
                count = problem_service.load_from_json(problem_set_path)
                print(f"✓ Loaded {count} problems from problem set into SQLite database")
            except Exception as e:
                print(f"⚠ Warning: Could not load problem set: {e}")
        else:
            print(f"ℹ Problem set file not found at: {problem_set_path}")
            print("  You can load problems manually via POST /api/problems/load")
    else:
        print(f"✓ Database already contains {existing_count} problems")
    
    yield
    
    # Shutdown (if needed)
    pass


app = FastAPI(
    title="Adaptive Learning Orchestrator",
    description="Production-ready FastAPI application implementing Planner-Executor architecture for adaptive learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for production use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assessments.router)
app.include_router(problems.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Adaptive Learning Orchestrator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

