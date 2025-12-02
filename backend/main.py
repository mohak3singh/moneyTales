"""
FastAPI Main Application
Entry point for the Financial Education backend
"""

import logging
import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Load environment variables from .env file
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database
from backend.db.database import Database
from backend.db.mock_users import seed_mock_users

# Import RAG
from backend.rag import RAGManager

# Import orchestrator
from backend.orchestrator import Orchestrator

# Import agents
from backend.agents.base_agent import Agent
from backend.agents.story_agent import StoryAgent
from backend.agents.quiz_agent import QuizAgent
from backend.agents.difficulty_agent import DifficultyAgent
from backend.agents.rag_agent import RAGAgent
from backend.agents.evaluator_agent import EvaluatorAgent
from backend.agents.gamification_agent import GamificationAgent

# Import services
from backend.services.topic_suggester import TopicSuggester

# Import routers
from backend.routers.quiz_router import setup_quiz_router
from backend.routers.submit_router import setup_submit_router
from backend.routers.gamification_router import setup_gamification_router
from backend.routers.auth_router import setup_auth_router
from backend.routers.topics_router import setup_topics_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
db = None
rag_manager = None
orchestrator = None
topic_suggester = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown
    Initializes database, RAG, and agents on startup
    """
    global db, rag_manager, orchestrator, topic_suggester
    
    logger.info("🚀 Starting MoneyTales Backend...")
    
    # Initialize database
    logger.info("📦 Initializing database...")
    db = Database()
    
    # Seed mock users if database is empty
    try:
        user = db.get_user("child_001")
        if not user:
            logger.info("📝 Seeding mock users...")
            seed_mock_users(db)
    except Exception as e:
        logger.error(f"Error seeding users: {e}")
    
    # Initialize RAG system
    logger.info("🧠 Initializing RAG system...")
    rag_manager = RAGManager()
    try:
        chunk_count = rag_manager.initialize()
        logger.info(f"✅ RAG initialized with {chunk_count} document chunks")
    except Exception as e:
        logger.error(f"Error initializing RAG: {e}")
        rag_manager = RAGManager()  # Use empty RAG as fallback
    
    # Initialize topic suggester
    logger.info("📚 Initializing topic suggester...")
    topic_suggester = TopicSuggester()
    
    # Initialize orchestrator
    logger.info("🎭 Initializing orchestrator...")
    orchestrator = Orchestrator(db, rag_manager)
    
    # Register agents
    orchestrator.register_agent("StoryAgent", StoryAgent())
    orchestrator.register_agent("QuizAgent", QuizAgent())
    orchestrator.register_agent("DifficultyAgent", DifficultyAgent())
    orchestrator.register_agent("RAGAgent", RAGAgent(rag_manager))
    orchestrator.register_agent("EvaluatorAgent", EvaluatorAgent())
    orchestrator.register_agent("GamificationAgent", GamificationAgent())
    
    logger.info("✅ All agents registered!")
    
    # Setup routes
    logger.info("📍 Setting up API routes...")
    quiz_router = setup_quiz_router(orchestrator)
    app.include_router(quiz_router)
    
    submit_router = setup_submit_router(orchestrator, db, topic_suggester)
    app.include_router(submit_router)
    
    gamification_router = setup_gamification_router(orchestrator, db)
    app.include_router(gamification_router)
    
    auth_router = setup_auth_router(db)
    app.include_router(auth_router)
    
    topics_router = setup_topics_router(db, topic_suggester)
    app.include_router(topics_router)
    
    logger.info("✅ All routes registered!")
    logger.info("🎉 MoneyTales Backend Ready!")
    
    yield  # Application runs here
    
    # Cleanup
    logger.info("🛑 Shutting down MoneyTales Backend...")


# Create FastAPI app
app = FastAPI(
    title="MoneyTales API",
    description="Financial Education Platform for Kids",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "status": "success",
        "message": "MoneyTales Financial Education API",
        "version": "1.0.0",
        "endpoints": {
            "quiz": "/api/quiz/generate",
            "submit": "/api/submit/answers",
            "gamification": "/api/gamification/stats/{user_id}",
            "trace": "/api/quiz/trace/{request_id}",
            "docs": "/docs"
        }
    }


# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if db else "disconnected",
        "rag": "initialized" if rag_manager else "not initialized",
        "orchestrator": "ready" if orchestrator else "not ready"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
