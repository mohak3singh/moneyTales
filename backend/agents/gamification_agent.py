"""
Gamification Agent
Manages points, badges, levels, and rewards
"""

import logging
from typing import Dict, Any, List
from .base_agent import Agent

logger = logging.getLogger(__name__)


class GamificationAgent(Agent):
    """Handles gamification logic: points, badges, levels"""

    def __init__(self):
        super().__init__("GamificationAgent")
        
        # Configuration
        self.points_per_quiz = 10
        self.points_per_perfect = 50
        self.points_per_badge = 100
        self.level_threshold = 500  # Points needed per level

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Process gamification events
        
        Args:
            event_type: str - type of event (quiz_completed, badge_earned, etc)
            user_id: str - user identifier
            quiz_score: float - quiz percentage (if applicable)
            quizzes_completed: int - total quizzes done
            current_points: int - current user points
            current_level: int - current user level
        
        Returns:
            dict with points earned, badges unlocked, level ups
        """
        try:
            event_type = kwargs.get("event_type", "quiz_completed")
            user_id = kwargs.get("user_id", "")
            quiz_score = kwargs.get("quiz_score", 0)
            quizzes_completed = kwargs.get("quizzes_completed", 0)
            current_points = kwargs.get("current_points", 0)
            current_level = kwargs.get("current_level", 1)

            self.log_execution("Gamification Processing", "started", {
                "event_type": event_type,
                "user_id": user_id
            })

            # Calculate points
            points_earned = self._calculate_points(event_type, quiz_score)

            # Check for new badges
            badges_earned = self._check_badges(
                event_type, quizzes_completed, quiz_score
            )

            # Check for level up
            new_total_points = current_points + points_earned
            new_level, leveled_up = self._check_level_up(
                new_total_points, current_level
            )

            return {
                "status": "success",
                "event_type": event_type,
                "points_earned": points_earned,
                "total_points": new_total_points,
                "badges_earned": badges_earned,
                "current_level": new_level,
                "leveled_up": leveled_up,
                "level_progress": self._get_level_progress(new_total_points, new_level),
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"Error in GamificationAgent: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }

    def _calculate_points(self, event_type: str, quiz_score: float = 0) -> int:
        """Calculate points for an event"""

        points = 0

        if event_type == "quiz_completed":
            # Base points + bonus for score
            points = self.points_per_quiz
            
            # Bonus for high scores
            if quiz_score == 100:
                points += self.points_per_perfect
            elif quiz_score >= 80:
                points += 20
            elif quiz_score >= 60:
                points += 10

        elif event_type == "badge_earned":
            points = self.points_per_badge

        elif event_type == "daily_streak":
            points = 50

        return points

    def _check_badges(
        self, event_type: str, quizzes_completed: int, quiz_score: float
    ) -> List[Dict[str, Any]]:
        """
        Check if user earned any badges
        Badges: First Quiz, Perfect Score, 5-Quiz Streak, etc
        """

        badges = []

        if event_type == "quiz_completed":
            # First Quiz badge
            if quizzes_completed == 1:
                badges.append({
                    "badge_id": "FIRST_QUIZ",
                    "name": "First Quiz Completed",
                    "description": "You took your first financial quiz!",
                    "icon": "🎯"
                })

            # Perfect Score badge
            if quiz_score == 100:
                badges.append({
                    "badge_id": "PERFECT_SCORE",
                    "name": "Perfect Score",
                    "description": "You got 100% on a quiz!",
                    "icon": "⭐"
                })

            # Streaks
            if quizzes_completed == 5:
                badges.append({
                    "badge_id": "STREAK_5",
                    "name": "5-Quiz Streak",
                    "description": "You completed 5 quizzes!",
                    "icon": "🔥"
                })

            if quizzes_completed == 10:
                badges.append({
                    "badge_id": "CURIOUS_MIND",
                    "name": "Curious Mind",
                    "description": "You completed 10 quizzes!",
                    "icon": "🧠"
                })

            if quizzes_completed == 20:
                badges.append({
                    "badge_id": "FINANCIAL_PRO",
                    "name": "Financial Pro",
                    "description": "You completed 20 quizzes - you're a pro!",
                    "icon": "🏆"
                })

        return badges

    def _check_level_up(
        self, total_points: int, current_level: int
    ) -> tuple[int, bool]:
        """
        Check if user should level up
        Returns: (new_level, leveled_up: bool)
        """

        new_level = current_level
        points_for_next_level = self.level_threshold * current_level

        if total_points >= points_for_next_level:
            new_level = (total_points // self.level_threshold) + 1

        leveled_up = new_level > current_level

        return new_level, leveled_up

    def _get_level_progress(self, total_points: int, current_level: int) -> Dict[str, Any]:
        """Get progress towards next level"""

        current_level_threshold = self.level_threshold * (current_level - 1)
        next_level_threshold = self.level_threshold * current_level

        points_in_level = total_points - current_level_threshold
        points_needed = next_level_threshold - current_level_threshold

        progress_percentage = (points_in_level / points_needed * 100) if points_needed > 0 else 0

        return {
            "current_level": current_level,
            "points_in_level": max(0, points_in_level),
            "points_needed": max(0, points_needed),
            "progress_percentage": progress_percentage
        }
