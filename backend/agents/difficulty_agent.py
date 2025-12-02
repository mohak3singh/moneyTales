"""
Difficulty Agent
Analyzes user performance and recommends difficulty levels
"""

import logging
from typing import Dict, Any
from .base_agent import Agent

logger = logging.getLogger(__name__)


class DifficultyAgent(Agent):
    """Determines optimal difficulty level for quizzes"""

    def __init__(self):
        super().__init__("DifficultyAgent")
        self.easy_threshold = 0.4
        self.medium_threshold = 0.7

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Determine recommended difficulty based on performance
        
        Args:
            user_performance: dict with quiz history
            user_profile: dict with age and experience
            topic: str - the topic being assessed
        
        Returns:
            dict with recommended difficulty and reasoning
        """
        try:
            user_performance = kwargs.get("user_performance", {})
            user_profile = kwargs.get("user_profile", {})
            topic = kwargs.get("topic", "general")

            self.log_execution("Difficulty Assessment", "started", {
                "user": user_profile.get("name"),
                "topic": topic
            })

            # Analyze performance
            difficulty = self._recommend_difficulty(user_performance, user_profile)

            return {
                "status": "success",
                "recommended_difficulty": difficulty,
                "reasoning": self._get_reasoning(difficulty, user_performance),
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"Error in DifficultyAgent: {e}")
            return {
                "status": "error",
                "recommended_difficulty": "medium",
                "error": str(e),
                "agent": self.name
            }

    def _recommend_difficulty(self, user_performance: dict, user_profile: dict) -> str:
        """
        Recommend difficulty based on:
        - Quiz history and scores
        - Age and experience level
        - Performance trends
        """

        age = user_profile.get("age", 10)
        quiz_history = user_performance.get("quiz_history", [])

        # If no history, use age to determine starting difficulty
        if not quiz_history:
            return self._age_based_difficulty(age)

        # Use most recent quiz score for immediate next quiz
        # This ensures difficulty changes right after quiz submission
        if len(quiz_history) > 0:
            most_recent_score = quiz_history[0].get("score", 0)  # quiz_history is ordered DESC
            normalized_score = most_recent_score / 100 if most_recent_score > 1 else most_recent_score
            
            # Recommend based on most recent score for immediate feedback
            if normalized_score < 0.5:  # Less than 50%
                return "easy"
            elif normalized_score < 0.8:  # 50-80%
                return "medium"
            else:  # 80% and above
                return "hard"
        
        return self._age_based_difficulty(age)

    def _age_based_difficulty(self, age: int) -> str:
        """Determine starting difficulty based on age"""
        # New users always start with medium difficulty
        # This allows them to experience balanced challenges
        # as they progress, difficulty will adjust based on performance
        return "medium"

    def _get_reasoning(self, difficulty: str, user_performance: dict) -> str:
        """Generate reasoning for difficulty recommendation"""

        quiz_history = user_performance.get("quiz_history", [])

        if not quiz_history:
            return "Starting with recommended difficulty based on age and experience level."

        recent_quizzes = quiz_history[-5:]
        avg_score = sum(q.get("score", 0) for q in recent_quizzes) / len(recent_quizzes)

        if difficulty == "easy":
            return f"Your average score is {avg_score:.0f}%. Easy questions will help build confidence and foundation."
        elif difficulty == "medium":
            return f"Your average score is {avg_score:.0f}%. Medium questions provide a good challenge for growth."
        else:
            return f"Your average score is {avg_score:.0f}%. Hard questions will push your learning forward!"
