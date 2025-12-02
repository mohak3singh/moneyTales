"""
Submit Router
Endpoints for submitting and evaluating quiz answers
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/submit", tags=["submit"])


class QuizSubmission(BaseModel):
    """Quiz submission schema"""
    user_id: str
    questions: List[Dict[str, Any]]
    answers: List[int]
    topic: str = "money basics"
    time_taken_seconds: int = 0


def setup_submit_router(orchestrator, database, topic_suggester=None):
    """Setup submit routes with orchestrator and database dependency"""

    @router.post("/answers")
    async def submit_answers(submission: QuizSubmission) -> Dict[str, Any]:
        """
        Submit quiz answers for evaluation
        
        Flow:
        1. EvaluatorAgent grades the quiz
        2. Analyze performance history using Gemini
        3. GamificationAgent calculates rewards
        4. Store responses and calculate next difficulty
        5. Database updated with score, points, badges
        6. Returns personalized feedback with recommended difficulty
        
        Returns: Score, Feedback, Points Earned, Badges, Next Difficulty, etc
        """
        try:
            result = orchestrator.evaluate_quiz(
                user_id=submission.user_id,
                questions=submission.questions,
                answers=submission.answers,
                topic=submission.topic
            )
            
            if result.get("status") == "error":
                raise HTTPException(status_code=400, detail=result.get("error"))
            
            # Extract score information (score is now percentage 0-100)
            percentage = result.get("percentage", 0)
            score = result.get("score", 0)
            max_score = result.get("max_score", len(submission.questions))
            
            # Determine next difficulty based on percentage score
            if percentage >= 80:
                next_difficulty = "hard"
                feedback = f"🏆 Excellent work! You scored {percentage:.0f}%! You're ready for harder challenges!"
                insight = "Keep practicing to maintain your excellent performance!"
            elif percentage >= 50:
                next_difficulty = "medium"
                feedback = f"👍 Good job! You scored {percentage:.0f}%. You're making progress!"
                insight = "Keep practicing to improve further!"
            else:
                # Score < 50% - decrease difficulty
                next_difficulty = "easy"
                feedback = f"💪 Nice try! You scored {percentage:.0f}%. Let's strengthen the basics!"
                insight = "Don't worry, practice makes perfect. Start with easier questions to build your foundation!"
            
            # Try to enhance with Gemini if available
            if topic_suggester:
                try:
                    quiz_history = database.get_user_quiz_history(submission.user_id, limit=10)
                    history_list = []
                    for q in quiz_history:
                        try:
                            hist_percentage = q.score if hasattr(q, 'score') and isinstance(q.score, (int, float)) else 0
                            history_list.append({
                                "topic": q.topic if hasattr(q, 'topic') else submission.topic,
                                "percentage": hist_percentage
                            })
                        except:
                            pass
                    
                    # Get personalized analysis from Gemini
                    analysis = topic_suggester.analyze_performance_with_gemini(
                        history_list, percentage, max_score, next_difficulty
                    )
                    if analysis.get("success"):
                        next_difficulty = analysis.get("next_difficulty", next_difficulty)
                        feedback = analysis.get("feedback", feedback)
                        insight = analysis.get("insight", insight)
                except Exception as e:
                    logger.warning(f"Could not enhance feedback with Gemini: {e}")
            
            # Store responses
            responses_json = json.dumps({
                "questions": [{"q": q.get("question", ""), "a": submission.answers[i] if i < len(submission.answers) else -1} 
                             for i, q in enumerate(submission.questions)]
            })
            
            # Update result with recommendations
            result["next_difficulty"] = next_difficulty
            result["feedback_message"] = feedback
            result["insight"] = insight
            
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
