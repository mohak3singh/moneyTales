"""
Quiz Router
Endpoints for generating quizzes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Request models
class QuizGenerateRequest(BaseModel):
    user_id: str
    topic: str = "money basics"
    num_questions: Optional[int] = 5

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


def setup_quiz_router(orchestrator):
    """Setup quiz routes with orchestrator dependency"""

    @router.post("/generate")
    async def generate_quiz(request: QuizGenerateRequest) -> Dict[str, Any]:
        """
        Generate a personalized quiz for a user
        
        Flow:
        1. Orchestrator fetches user profile
        2. RAGAgent retrieves knowledge context
        3. DifficultyAgent recommends level based on history
        4. StoryAgent generates story
        5. QuizAgent creates questions
        
        Returns: Story, Questions, Metadata with automatic difficulty
        """
        try:
            result = orchestrator.generate_quiz(
                request.user_id, 
                request.topic,
                num_questions=request.num_questions
            )
            
            if result.get("status") == "error":
                raise HTTPException(status_code=400, detail=result.get("error"))
            
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/trace/{request_id}")
    async def get_trace(request_id: str) -> Dict[str, Any]:
        """
        Get trace logs for a quiz generation request
        Shows step-by-step execution of all agents
        """
        try:
            result = orchestrator.get_trace_logs(request_id)
            
            if result.get("status") == "error":
                raise HTTPException(status_code=404, detail="Request not found")
            
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
