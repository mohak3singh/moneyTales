"""
Topics Router
Endpoints for getting topics from educational PDFs based on age
Topics are extracted from curriculum content for the appropriate class level
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(prefix="/api/topics", tags=["topics"])


class TopicsRequest(BaseModel):
    user_id: str
    age: int


def setup_topics_router(database, topic_suggester):
    """Setup topics routes with topic_suggester dependency"""

    @router.post("/suggestions")
    async def get_topic_suggestions(request: TopicsRequest) -> Dict[str, Any]:
        """
        Get topic suggestions based on user age
        Topics are extracted from the educational PDF for the appropriate class level
        
        Flow:
        1. Map age to appropriate class (6th-10th)
        2. Extract topics from that class's PDF
        3. Exclude previously covered topics
        4. Return top 5 topics
        """
        try:
            # Get user's previous topics
            previous_attempts = database.get_user_quiz_attempts(request.user_id)
            previous_topics = list(set([attempt.topic for attempt in previous_attempts]))
            
            # Get suggestions from PDF-based topic suggester
            topics = topic_suggester.get_topics_for_age(request.age, previous_topics)
            
            print(f"[TopicsRouter] Returned topics for age {request.age}: {topics}")
            
            # Get class information
            class_info = topic_suggester.pdf_extractor.get_class_info(request.age)
            
            return {
                "status": "success",
                "user_id": request.user_id,
                "age": request.age,
                "class": class_info.get("class"),
                "age_range": class_info.get("age_range"),
                "topics": topics,
                "previous_topics_count": len(previous_topics),
                "source": "PDF"  # Topics are from PDF, not Gemini
            }

        except Exception as e:
            print(f"[TopicsRouter] ERROR: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return router
