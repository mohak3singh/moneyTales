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
        
        Returns: Complete profile, achievements, progress with rank
        """
        try:
            result = orchestrator.get_user_stats(user_id)
            
            if result.get("status") == "error":
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get user rank based on users.points (source of truth)
            conn = database.get_connection()
            cursor = conn.cursor()
            
            # Use ROW_NUMBER to get the user's actual position in the ranking
            cursor.execute("""
                WITH ranked_users AS (
                    SELECT 
                        user_id,
                        points,
                        ROW_NUMBER() OVER (ORDER BY points DESC) as position
                    FROM users
                )
                SELECT position
                FROM ranked_users
                WHERE user_id = ?
            """, (user_id,))
            
            position_result = cursor.fetchone()
            rank = position_result["position"] if position_result else 1
            
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"DEBUG: User {user_id} - Query result: {position_result}, Rank: {rank}")
            
            conn.close()
            
            result["rank"] = rank
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/leaderboard")
    async def get_leaderboard(limit: int = 10) -> Dict[str, Any]:
        """
        Get top users by points (leaderboard)
        
        Returns: Top users ranked by points with stats
        """
        try:
            # Query database for top users with their stats
            conn = database.get_connection()
            cursor = conn.cursor()
            
            # Get top users by points with all their stats
            cursor.execute("""
                SELECT 
                    u.user_id,
                    u.name,
                    u.level,
                    u.points as total_points,
                    COUNT(DISTINCT qa.attempt_id) as quizzes_completed,
                    COALESCE(AVG(CAST(qa.score AS FLOAT)), 0) as avg_score
                FROM users u
                LEFT JOIN quiz_attempts qa ON u.user_id = qa.user_id
                GROUP BY u.user_id, u.name, u.level, u.points
                ORDER BY total_points DESC, quizzes_completed DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            leaderboard = []
            
            for idx, row in enumerate(rows, 1):
                leaderboard.append({
                    "rank": idx,
                    "user_id": row["user_id"],
                    "name": row["name"],
                    "level": row["level"],
                    "points": int(row["total_points"]),
                    "quizzes_completed": int(row["quizzes_completed"]),
                    "average_score": round(float(row["avg_score"]), 2) if row["avg_score"] else 0
                })
            
            conn.close()
            
            return {
                "status": "success",
                "leaderboard": leaderboard
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
