"""
Gamification Router
Endpoints for user points, badges, levels, and leaderboard
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


def setup_gamification_router(orchestrator, database):
    """Setup gamification routes"""

    @router.get("/points/{user_id}")
    async def get_points(user_id: str) -> Dict[str, Any]:
        """
        Get user's current points and stats
        
        Returns: Points, Level, Progress, Recent Achievements
        """
        try:
            result = orchestrator.get_user_stats(user_id)
            
            if result.get("status") == "error":
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "status": "success",
                "user_id": user_id,
                "points": result.get("points", 0),
                "level": result.get("level", 1),
                "badges": result.get("badges", []),
                "quizzes_completed": result.get("quizzes_completed", 0),
                "average_score": result.get("average_score", 0)
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/stats/{user_id}")
    async def get_stats(user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user statistics
        
        Returns: Complete profile, achievements, progress
        """
        try:
            result = orchestrator.get_user_stats(user_id)
            
            if result.get("status") == "error":
                raise HTTPException(status_code=404, detail="User not found")
            
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/leaderboard")
    async def get_leaderboard(limit: int = 10) -> Dict[str, Any]:
        """
        Get top users by points (leaderboard)
        
        Returns: Top users ranked by points
        """
        try:
            # For MVP, return mock leaderboard
            # In production, query database for top users
            return {
                "status": "success",
                "leaderboard": [
                    {"rank": 1, "name": "Alex", "points": 850, "level": 3, "badges": 5},
                    {"rank": 2, "name": "Sam", "points": 720, "level": 3, "badges": 4},
                    {"rank": 3, "name": "Jordan", "points": 650, "level": 2, "badges": 3},
                ]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
