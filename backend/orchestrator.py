"""
Orchestrator
Coordinates all agents and logs execution flow
Main execution engine for the platform
"""

import logging
import uuid
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orchestrates the execution of multiple agents
    Manages request flow, logging, and coordination
    """

    def __init__(self, database, rag_manager):
        """
        Initialize orchestrator
        database: Database instance
        rag_manager: RAGManager instance
        """
        self.database = database
        self.rag_manager = rag_manager
        self.agents = {}
        self.trace_logs = {}

    def register_agent(self, agent_name: str, agent):
        """Register an agent"""
        self.agents[agent_name] = agent
        logger.info(f"Registered agent: {agent_name}")

    def generate_quiz(self, user_id: str, topic: str = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a quiz for a user
        Orchestrates: RAGAgent -> DifficultyAgent -> StoryAgent -> QuizAgent
        
        Flow:
        1. Get user profile from DB
        2. Get context from RAG for topic
        3. Analyze user difficulty level
        4. Generate personalized story
        5. Generate quiz questions
        6. Log all steps
        """

        request_id = str(uuid.uuid4())
        step = 0

        try:
            # Initialize trace
            self._log_trace(request_id, step, "Orchestrator", "Quiz Generation Started", "pending", {
                "user_id": user_id,
                "topic": topic
            })

            # Step 1: Get user profile with retry logic
            step += 1
            self._log_trace(request_id, step, "Database", "Fetching User Profile", "in_progress", {})
            
            # Try to get user with retry logic (in case of timing issues)
            user = None
            max_retries = 3
            for attempt in range(max_retries):
                user = self.database.get_user(user_id)
                if user:
                    break
                if attempt < max_retries - 1:
                    logger.warning(f"User {user_id} not found on attempt {attempt + 1}, retrying...")
                    import time
                    time.sleep(0.3)
            
            if not user:
                # Try to create a default user if not found (emergency fallback)
                logger.warning(f"User {user_id} not found, attempting to create default user as fallback")
                from backend.db.models import User
                try:
                    default_user = User(
                        user_id=user_id,
                        name=user_id,  # Use user_id as name if user not found
                        age=10,
                        hobbies="learning"
                    )
                    self.database.create_user(default_user)
                    user = self.database.get_user(user_id)
                    if not user:
                        raise ValueError(f"Failed to create default user {user_id}")
                    logger.info(f"Created default user {user_id} with fallback name")
                except Exception as e:
                    logger.error(f"Failed to create default user: {e}")
                    raise ValueError(f"User {user_id} not found in the system. Please register first or contact support.")
            
            user_profile = {
                "user_id": user.user_id,
                "name": user.name,
                "age": user.age,
                "hobbies": user.hobbies,
                "level": user.level,
                "points": user.points
            }
            
            self._log_trace(request_id, step, "Database", "User Profile Retrieved", "completed", {
                "user_name": user.name,
                "user_age": user.age
            })

            # Step 2: Get RAG context
            step += 1
            self._log_trace(request_id, step, "RAGAgent", "Retrieving Knowledge Base", "in_progress", {
                "query": topic or "financial education"
            })
            
            rag_agent = self.agents.get("RAGAgent")
            rag_result = rag_agent.execute(
                query=topic or "financial education",
                top_k=3
            ) if rag_agent else {"status": "skipped", "context": ""}
            
            rag_context = rag_result.get("context", "")
            
            self._log_trace(request_id, step, "RAGAgent", "Knowledge Retrieved", "completed", {
                "documents_found": rag_result.get("results_count", 0)
            })

            # Step 3: Determine difficulty
            step += 1
            self._log_trace(request_id, step, "DifficultyAgent", "Analyzing Difficulty", "in_progress", {})
            
            quiz_history = self.database.get_user_quiz_history(user_id)
            difficulty_agent = self.agents.get("DifficultyAgent")
            difficulty_result = difficulty_agent.execute(
                user_performance={"quiz_history": [
                    {"score": q.score} for q in quiz_history  # score is already percentage (0-100)
                ]},
                user_profile=user_profile,
                topic=topic
            ) if difficulty_agent else {"recommended_difficulty": "medium"}
            
            difficulty = difficulty_result.get("recommended_difficulty", "medium")
            
            self._log_trace(request_id, step, "DifficultyAgent", "Difficulty Determined", "completed", {
                "recommended_difficulty": difficulty,
                "reasoning": difficulty_result.get("reasoning")
            })

            # Step 4: Generate story
            step += 1
            self._log_trace(request_id, step, "StoryAgent", "Generating Story", "in_progress", {})
            
            story_agent = self.agents.get("StoryAgent")
            story_result = story_agent.execute(
                user_profile=user_profile,
                topic=topic or "money basics",
                difficulty=difficulty,
                rag_context=rag_context
            ) if story_agent else {"story": ""}
            
            story = story_result.get("story", "")
            
            self._log_trace(request_id, step, "StoryAgent", "Story Generated", "completed", {
                "story_length": len(story)
            })

            # Step 5: Generate quiz
            step += 1
            self._log_trace(request_id, step, "QuizAgent", "Generating Questions", "in_progress", {
                "topic": topic,
                "difficulty": difficulty
            })
            
            # Prepare enriched user profile with quiz history for personalization
            enriched_profile = user_profile.copy()
            enriched_profile["quiz_history"] = [
                {
                    "topic": q.topic if hasattr(q, 'topic') else "",
                    "percentage": q.score if hasattr(q, 'score') and isinstance(q.score, (int, float)) else 0,
                    "difficulty": q.difficulty if hasattr(q, 'difficulty') else "medium"
                }
                for q in quiz_history[-5:]  # Last 5 quizzes for context
            ]
            
            quiz_agent = self.agents.get("QuizAgent")
            quiz_result = quiz_agent.execute(
                topic=topic or "money basics",
                difficulty=difficulty,
                num_questions=5,
                rag_context=rag_context,
                user_profile=enriched_profile,
                database=self.database,  # Pass database for answer history
                user_id=user_id  # Pass user_id to fetch their answered questions
            ) if quiz_agent else {"questions": []}
            
            questions = quiz_result.get("questions", [])
            
            self._log_trace(request_id, step, "QuizAgent", "Questions Generated", "completed", {
                "num_questions": len(questions)
            })

            # Final logging
            step += 1
            self._log_trace(request_id, step, "Orchestrator", "Quiz Generation Completed", "completed", {
                "quiz_id": request_id,
                "total_steps": step
            })

            return {
                "status": "success",
                "request_id": request_id,
                "user_id": user_id,
                "user_name": user.name,
                "topic": topic or "money basics",
                "difficulty": difficulty,
                "story": story,
                "questions": questions,
                "total_questions": len(questions),
                "trace_steps": step
            }

        except Exception as e:
            logger.error(f"Error in quiz generation: {e}")
            self._log_trace(request_id, step + 1, "Orchestrator", "Error", "failed", {}, error=str(e))
            
            return {
                "status": "error",
                "error": str(e),
                "request_id": request_id,
                "trace_steps": step
            }

    def evaluate_quiz(self, user_id: str, questions: List[Dict], answers: List[int], 
                     topic: str = None, difficulty: str = "medium", **kwargs) -> Dict[str, Any]:
        """
        Evaluate quiz answers and update gamification
        Orchestrates: EvaluatorAgent -> GamificationAgent -> Database
        
        Flow:
        1. Evaluate answers
        2. Calculate gamification rewards
        3. Update user stats in DB
        4. Log steps
        """

        request_id = str(uuid.uuid4())
        step = 0

        try:
            self._log_trace(request_id, step, "Orchestrator", "Quiz Evaluation Started", "pending", {
                "user_id": user_id,
                "num_questions": len(questions)
            })

            # Step 1: Get user
            step += 1
            user = self.database.get_user(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Step 2: Evaluate
            step += 1
            self._log_trace(request_id, step, "EvaluatorAgent", "Evaluating Answers", "in_progress", {})
            
            evaluator_agent = self.agents.get("EvaluatorAgent")
            eval_result = evaluator_agent.execute(
                questions=questions,
                answers=answers,
                user_profile={
                    "name": user.name,
                    "age": user.age
                }
            ) if evaluator_agent else {}
            
            score = eval_result.get("score", 0)
            percentage = eval_result.get("percentage", 0)
            feedback = eval_result.get("feedback", "")
            
            self._log_trace(request_id, step, "EvaluatorAgent", "Evaluation Complete", "completed", {
                "score": score,
                "percentage": percentage
            })

            # Step 3: Gamification
            step += 1
            self._log_trace(request_id, step, "GamificationAgent", "Processing Rewards", "in_progress", {})
            
            quiz_history = self.database.get_user_quiz_history(user_id, limit=100)
            
            gamification_agent = self.agents.get("GamificationAgent")
            gamification_result = gamification_agent.execute(
                event_type="quiz_completed",
                user_id=user_id,
                quiz_score=percentage,
                quizzes_completed=len(quiz_history) + 1,
                current_points=user.points,
                current_level=user.level
            ) if gamification_agent else {}
            
            points_earned = gamification_result.get("points_earned", 0)
            badges_earned = gamification_result.get("badges_earned", [])
            new_level = gamification_result.get("current_level", user.level)
            leveled_up = gamification_result.get("leveled_up", False)
            
            self._log_trace(request_id, step, "GamificationAgent", "Rewards Calculated", "completed", {
                "points_earned": points_earned,
                "badges_earned": len(badges_earned),
                "level": new_level,
                "leveled_up": leveled_up
            })

            # Step 4: Update database
            step += 1
            self._log_trace(request_id, step, "Database", "Updating User Stats", "in_progress", {})
            
            # Build detailed responses JSON with question data
            responses_list = []
            for i, question in enumerate(questions):
                user_answer_idx = answers[i] if i < len(answers) else -1
                user_answer_text = ""
                correct_answer_text = ""
                is_correct = False
                
                if user_answer_idx >= 0 and user_answer_idx < len(question.get("options", [])):
                    user_answer_text = question["options"][user_answer_idx]
                    # Determine correct answer
                    correct_idx = question.get("correct_answer", -1)
                    if correct_idx >= 0 and correct_idx < len(question.get("options", [])):
                        correct_answer_text = question["options"][correct_idx]
                        is_correct = (user_answer_idx == correct_idx)
                
                responses_list.append({
                    "question": question.get("question", ""),
                    "topic": topic,
                    "difficulty": difficulty,
                    "user_answer": user_answer_text,
                    "correct_answer": correct_answer_text,
                    "is_correct": is_correct,
                    "options": question.get("options", [])
                })
            
            responses_json = json.dumps(responses_list)
            
            # Save quiz attempt to history
            from backend.db.models import QuizAttempt
            quiz_attempt = QuizAttempt(
                attempt_id=str(uuid.uuid4()),
                user_id=user_id,
                quiz_id=request_id,
                topic=topic,
                difficulty=difficulty,
                score=int(percentage),  # Save as percentage (0-100)
                max_score=len(questions),
                time_taken_seconds=0,
                answered_questions=len(answers),
                correct_answers=eval_result.get("correct_count", 0),
                responses=responses_json,  # Save detailed responses
                created_at=datetime.now().isoformat()
            )
            self.database.create_quiz_attempt(quiz_attempt)
            
            # Update points and level
            self.database.update_user_points(user_id, points_earned)
            self.database.update_user_level(user_id, new_level)
            
            # Add badges
            for badge in badges_earned:
                self.database.add_badge(user_id, badge["name"])
            
            self._log_trace(request_id, step, "Database", "User Stats Updated", "completed", {
                "points_updated": points_earned,
                "level_updated": new_level
            })

            # Step 5: Complete
            step += 1
            self._log_trace(request_id, step, "Orchestrator", "Quiz Evaluation Completed", "completed", {
                "total_steps": step
            })

            return {
                "status": "success",
                "request_id": request_id,
                "user_id": user_id,
                "score": score,
                "percentage": percentage,
                "feedback": feedback,
                "points_earned": points_earned,
                "badges_earned": badges_earned,
                "new_level": new_level,
                "leveled_up": leveled_up,
                "question_feedback": eval_result.get("question_feedback", []),
                "trace_steps": step
            }

        except Exception as e:
            logger.error(f"Error in quiz evaluation: {e}")
            self._log_trace(request_id, step + 1, "Orchestrator", "Error", "failed", {}, error=str(e))
            
            return {
                "status": "error",
                "error": str(e),
                "request_id": request_id,
                "trace_steps": step
            }

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics and progress"""
        try:
            user = self.database.get_user(user_id)
            if not user:
                return {"status": "error", "error": "User not found"}

            quiz_history = self.database.get_user_quiz_history(user_id)
            avg_score = self.database.get_user_average_score(user_id)
            gamification_stats = self.database.get_user_gamification_stats(user_id)

            return {
                "status": "success",
                "user_id": user_id,
                "name": user.name,
                "age": user.age,
                "level": user.level,
                "points": user.points,
                "badges": user.badges.split(",") if user.badges else [],
                "quizzes_completed": len(quiz_history),
                "average_score": avg_score,
                "recent_quizzes": [
                    {
                        "topic": q.topic,
                        "difficulty": q.difficulty,
                        "score": q.score,
                        "percentage": (q.score / q.max_score * 100) if q.max_score > 0 else 0,
                        "date": q.created_at
                    } for q in quiz_history[:5]
                ]
            }

        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {"status": "error", "error": str(e)}

    def get_trace_logs(self, request_id: str) -> Dict[str, Any]:
        """Get trace logs for a request"""
        try:
            logs = self.database.get_trace_logs(request_id)
            
            return {
                "status": "success",
                "request_id": request_id,
                "logs": [
                    {
                        "step": log.step_number,
                        "agent": log.agent_name,
                        "status": log.status,
                        "timestamp": log.created_at,
                        "input": log.input_data,
                        "output": log.output_data,
                        "error": log.error_message
                    } for log in logs
                ]
            }

        except Exception as e:
            logger.error(f"Error getting trace logs: {e}")
            return {"status": "error", "error": str(e)}

    def _log_trace(self, request_id: str, step: int, agent_name: str, 
                   status_msg: str, status: str, data: Dict = None, error: str = None):
        """Log a trace entry"""
        from .db.models import TraceLog

        try:
            trace_id = f"{request_id}_{step}"
            log = TraceLog(
                trace_id=trace_id,
                request_id=request_id,
                agent_name=agent_name,
                step_number=step,
                status=status,
                input_data=str(data) if data else "",
                output_data=None,
                error_message=error
            )
            self.database.create_trace_log(log)
        except Exception as e:
            logger.error(f"Error logging trace: {e}")
