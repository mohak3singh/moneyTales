"""
Evaluator Agent
Evaluates quiz answers and provides feedback
"""

import logging
from typing import Dict, List, Any
from .base_agent import Agent

logger = logging.getLogger(__name__)


class EvaluatorAgent(Agent):
    """Evaluates quiz responses and generates feedback"""

    def __init__(self):
        super().__init__("EvaluatorAgent")

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Evaluate quiz answers
        
        Args:
            questions: List[dict] - quiz questions with correct answers
            answers: List[int] - user's answers (indices)
            user_profile: dict - for personalized feedback
        
        Returns:
            dict with score, feedback, and areas for improvement
        """
        try:
            questions = kwargs.get("questions", [])
            answers = kwargs.get("answers", [])
            user_profile = kwargs.get("user_profile", {})

            self.log_execution("Quiz Evaluation", "started", {
                "user": user_profile.get("name"),
                "total_questions": len(questions)
            })

            if not questions or not answers:
                return {
                    "status": "error",
                    "error": "Missing questions or answers",
                    "agent": self.name
                }

            # Calculate score
            score_info = self._calculate_score(questions, answers)
            
            # Generate feedback
            feedback = self._generate_feedback(questions, answers, score_info, user_profile)

            return {
                "status": "success",
                "score": score_info["score"],
                "max_score": score_info["max_score"],
                "percentage": score_info["percentage"],
                "correct_count": score_info["correct_count"],
                "feedback": feedback,
                "question_feedback": self._get_question_feedback(questions, answers),
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"Error in EvaluatorAgent: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }

    def _calculate_score(self, questions: List[dict], answers: List[int]) -> Dict[str, Any]:
        """Calculate quiz score"""

        correct_count = 0
        max_score = len(questions)

        for i, question in enumerate(questions):
            if i < len(answers):
                correct_answer = question.get("correct_answer", -1)
                if answers[i] == correct_answer:
                    correct_count += 1

        percentage = (correct_count / max_score * 100) if max_score > 0 else 0

        return {
            "correct_count": correct_count,
            "max_score": max_score,
            "score": int(percentage),  # Score is the percentage value (0-100)
            "percentage": percentage
        }

    def _generate_feedback(
        self, questions: List[dict], answers: List[int], 
        score_info: dict, user_profile: dict
    ) -> str:
        """Generate personalized feedback"""

        name = user_profile.get("name", "Student")
        percentage = score_info["percentage"]

        if percentage == 100:
            feedback = f"🌟 Amazing work, {name}! Perfect score! You've mastered this topic!"
        elif percentage >= 80:
            feedback = f"👏 Great job, {name}! You got {score_info['correct_count']}/{score_info['max_score']} correct. Keep going!"
        elif percentage >= 60:
            feedback = f"📚 Good effort, {name}! You got {score_info['correct_count']}/{score_info['max_score']} correct. Review the explanations to improve."
        elif percentage >= 40:
            feedback = f"💪 Nice try, {name}! You got {score_info['correct_count']}/{score_info['max_score']} correct. Let's review and try again!"
        else:
            feedback = f"🎯 {name}, this is a learning opportunity! You got {score_info['correct_count']}/{score_info['max_score']} correct. Review the material and give it another shot!"

        return feedback

    def _get_question_feedback(self, questions: List[dict], answers: List[int]) -> List[dict]:
        """Generate feedback for each question"""

        feedback_list = []

        for i, question in enumerate(questions):
            correct_answer = question.get("correct_answer", -1)
            is_correct = i < len(answers) and answers[i] == correct_answer
            
            user_answer_text = ""
            if i < len(answers):
                options = question.get("options", [])
                if answers[i] < len(options):
                    user_answer_text = options[answers[i]]

            correct_answer_text = question.get("options", [])[correct_answer] if correct_answer >= 0 else ""

            feedback_list.append({
                "question_id": question.get("question_id", f"q_{i}"),
                "question": question.get("question", ""),
                "is_correct": is_correct,
                "user_answer": user_answer_text,
                "correct_answer": correct_answer_text,
                "explanation": question.get("explanation", ""),
                "status": "✅ Correct!" if is_correct else "❌ Incorrect"
            })

        return feedback_list
