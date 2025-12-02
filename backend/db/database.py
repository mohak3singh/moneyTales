"""
SQLite Database Manager
Handles all database operations for users, quizzes, gamification, and traces
"""

import sqlite3
import json
import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from .models import User, QuizAttempt, GamificationEvent, TraceLog

logger = logging.getLogger(__name__)

# Database path - in project root
DB_PATH = Path(__file__).parent.parent.parent / "moneytales.db"


class Database:
    """SQLite Database Manager"""

    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = db_path or str(DB_PATH)
        self.init_db()

    def get_connection(self):
        """Get database connection with proper settings for concurrent access"""
        conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def init_db(self):
        """Create all tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                hobbies TEXT,
                level INTEGER DEFAULT 1,
                points INTEGER DEFAULT 0,
                badges TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)

        # Quiz attempts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                attempt_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                quiz_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                score INTEGER NOT NULL,
                max_score INTEGER NOT NULL,
                time_taken_seconds INTEGER NOT NULL,
                answered_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                responses TEXT DEFAULT '',
                feedback TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # Gamification events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gamification_events (
                event_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                points_awarded INTEGER NOT NULL,
                badge_name TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # Trace logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trace_logs (
                trace_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                status TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
        
        # Run migrations for any missing columns
        self._migrate_db()
    
    def _migrate_db(self):
        """Add any missing columns to existing tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if responses column exists in quiz_attempts
            cursor.execute("PRAGMA table_info(quiz_attempts)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if "responses" not in columns:
                logger.info("Adding 'responses' column to quiz_attempts table")
                cursor.execute("ALTER TABLE quiz_attempts ADD COLUMN responses TEXT DEFAULT ''")
            
            if "feedback" not in columns:
                logger.info("Adding 'feedback' column to quiz_attempts table")
                cursor.execute("ALTER TABLE quiz_attempts ADD COLUMN feedback TEXT DEFAULT ''")
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Migration error (may be expected if columns already exist): {e}")

    # ==================== USER OPERATIONS ====================

    def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, name, age, hobbies, level, points, badges, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user.user_id, user.name, user.age, user.hobbies, user.level, user.points, user.badges, user.created_at))
            conn.commit()
            conn.close()
            logger.info(f"User {user.user_id} created")
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return User(
                    user_id=row["user_id"],
                    name=row["name"],
                    age=row["age"],
                    hobbies=row["hobbies"],
                    level=row["level"],
                    points=row["points"],
                    badges=row["badges"],
                    created_at=row["created_at"]
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def update_user_points(self, user_id: str, points_delta: int) -> bool:
        """Update user points"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET points = points + ? WHERE user_id = ?
            """, (points_delta, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating user points: {e}")
            return False

    def update_user_level(self, user_id: str, new_level: int) -> bool:
        """Update user level"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET level = ? WHERE user_id = ?
            """, (new_level, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating user level: {e}")
            return False

    def add_badge(self, user_id: str, badge_name: str) -> bool:
        """Add badge to user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get current badges
            cursor.execute("SELECT badges FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            current_badges = row["badges"].split(",") if row["badges"] else []
            
            # Add if not exists
            if badge_name not in current_badges:
                current_badges.append(badge_name)
                new_badges = ",".join(current_badges)
                cursor.execute("""
                    UPDATE users SET badges = ? WHERE user_id = ?
                """, (new_badges, user_id))
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding badge: {e}")
            return False

    # ==================== QUIZ OPERATIONS ====================

    def create_quiz_attempt(self, attempt: QuizAttempt) -> bool:
        """Record a quiz attempt"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quiz_attempts 
                (attempt_id, user_id, quiz_id, topic, difficulty, score, max_score, 
                 time_taken_seconds, answered_questions, correct_answers, responses, feedback, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (attempt.attempt_id, attempt.user_id, attempt.quiz_id, attempt.topic,
                  attempt.difficulty, attempt.score, attempt.max_score, 
                  attempt.time_taken_seconds, attempt.answered_questions, 
                  attempt.correct_answers, attempt.responses or "", attempt.feedback or "", attempt.created_at))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating quiz attempt: {e}")
            return False

    def get_user_quiz_history(self, user_id: str, limit: int = 10) -> List[QuizAttempt]:
        """Get user's quiz history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM quiz_attempts WHERE user_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            conn.close()

            attempts = []
            for row in rows:
                try:
                    # Handle optional fields that might not exist
                    responses = ""
                    feedback = ""
                    try:
                        responses = row["responses"] if row["responses"] else ""
                    except (KeyError, TypeError, IndexError):
                        pass
                    try:
                        feedback = row["feedback"] if row["feedback"] else ""
                    except (KeyError, TypeError, IndexError):
                        pass
                    
                    attempt = QuizAttempt(
                        attempt_id=row["attempt_id"] if "attempt_id" in row.keys() else str(uuid.uuid4()),
                        user_id=row["user_id"] if "user_id" in row.keys() else user_id,
                        quiz_id=row["quiz_id"] if "quiz_id" in row.keys() else "",
                        topic=row["topic"] if "topic" in row.keys() else "",
                        difficulty=row["difficulty"] if "difficulty" in row.keys() else "medium",
                        score=row["score"] if "score" in row.keys() else 0,
                        max_score=row["max_score"] if "max_score" in row.keys() else 5,
                        time_taken_seconds=row["time_taken_seconds"] if "time_taken_seconds" in row.keys() else 0,
                        answered_questions=row["answered_questions"] if "answered_questions" in row.keys() else 0,
                        correct_answers=row["correct_answers"] if "correct_answers" in row.keys() else 0,
                        responses=responses,
                        feedback=feedback,
                        created_at=row["created_at"] if "created_at" in row.keys() else ""
                    )
                    attempts.append(attempt)
                except Exception as row_error:
                    logger.warning(f"Error processing quiz history row: {row_error}, skipping row")
                    continue
            return attempts
        except Exception as e:
            logger.error(f"Error getting quiz history: {e}")
            return []

    def get_user_quiz_attempts(self, user_id: str) -> List[QuizAttempt]:
        """Get all quiz attempts by user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quiz_attempts WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            rows = cursor.fetchall()
            conn.close()

            attempts = []
            for row in rows:
                try:
                    # Handle optional fields that might not exist
                    responses = ""
                    feedback = ""
                    try:
                        responses = row["responses"] if row["responses"] else ""
                    except (KeyError, TypeError, IndexError):
                        pass
                    try:
                        feedback = row["feedback"] if row["feedback"] else ""
                    except (KeyError, TypeError, IndexError):
                        pass
                    
                    attempt = QuizAttempt(
                        attempt_id=row["attempt_id"] if "attempt_id" in row.keys() else str(uuid.uuid4()),
                        user_id=row["user_id"] if "user_id" in row.keys() else user_id,
                        quiz_id=row["quiz_id"] if "quiz_id" in row.keys() else "",
                        topic=row["topic"] if "topic" in row.keys() else "",
                        difficulty=row["difficulty"] if "difficulty" in row.keys() else "medium",
                        score=row["score"] if "score" in row.keys() else 0,
                        max_score=row["max_score"] if "max_score" in row.keys() else 5,
                        time_taken_seconds=row["time_taken_seconds"] if "time_taken_seconds" in row.keys() else 0,
                        answered_questions=row["answered_questions"] if "answered_questions" in row.keys() else 0,
                        correct_answers=row["correct_answers"] if "correct_answers" in row.keys() else 0,
                        responses=responses,
                        feedback=feedback,
                        created_at=row["created_at"] if "created_at" in row.keys() else ""
                    )
                    attempts.append(attempt)
                except Exception as row_error:
                    logger.warning(f"Error processing quiz attempt row: {row_error}, skipping row")
                    continue
            return attempts
        except Exception as e:
            logger.error(f"Error getting quiz attempts: {e}")
            return []

    def get_user_average_score(self, user_id: str) -> float:
        """Get user's average quiz score"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(CAST(score AS FLOAT)) as avg_score
                FROM quiz_attempts WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            conn.close()
            avg_score = row["avg_score"] if row and row["avg_score"] is not None else 0
            return round(float(avg_score), 2)
        except Exception as e:
            logger.error(f"Error getting average score: {e}")
            return 0

    # ==================== GAMIFICATION OPERATIONS ====================

    def create_gamification_event(self, event: GamificationEvent) -> bool:
        """Log a gamification event"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO gamification_events 
                (event_id, user_id, event_type, points_awarded, badge_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event.event_id, event.user_id, event.event_type, 
                  event.points_awarded, event.badge_name, event.created_at))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating gamification event: {e}")
            return False

    def get_user_gamification_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's gamification stats"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get total points
            cursor.execute("""
                SELECT SUM(points_awarded) as total_points FROM gamification_events 
                WHERE user_id = ?
            """, (user_id,))
            points = cursor.fetchone()["total_points"] or 0
            
            # Get badges
            cursor.execute("""
                SELECT DISTINCT badge_name FROM gamification_events 
                WHERE user_id = ? AND badge_name IS NOT NULL
            """, (user_id,))
            badges = [row["badge_name"] for row in cursor.fetchall()]
            
            # Get user level
            cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            level = cursor.fetchone()["level"]
            
            conn.close()
            return {"points": points, "badges": badges, "level": level}
        except Exception as e:
            logger.error(f"Error getting gamification stats: {e}")
            return {}

    # ==================== TRACE LOG OPERATIONS ====================

    def create_trace_log(self, log: TraceLog) -> bool:
        """Create a trace log entry"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Use INSERT OR IGNORE to skip duplicates
            cursor.execute("""
                INSERT OR IGNORE INTO trace_logs 
                (trace_id, request_id, agent_name, step_number, status, input_data, output_data, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (log.trace_id, log.request_id, log.agent_name, log.step_number,
                  log.status, log.input_data, log.output_data, log.error_message, log.created_at))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating trace log: {e}")
            return False

    def get_trace_logs(self, request_id: str) -> List[TraceLog]:
        """Get all trace logs for a request"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM trace_logs WHERE request_id = ? 
                ORDER BY step_number ASC
            """, (request_id,))
            rows = cursor.fetchall()
            conn.close()

            logs = []
            for row in rows:
                logs.append(TraceLog(
                    trace_id=row["trace_id"],
                    request_id=row["request_id"],
                    agent_name=row["agent_name"],
                    step_number=row["step_number"],
                    status=row["status"],
                    input_data=row["input_data"],
                    output_data=row["output_data"],
                    error_message=row["error_message"],
                    created_at=row["created_at"]
                ))
            return logs
        except Exception as e:
            logger.error(f"Error getting trace logs: {e}")
            return []

    def update_trace_log_status(self, trace_id: str, status: str, 
                               output_data: str = None, error_message: str = None) -> bool:
        """Update trace log status"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE trace_logs SET status = ?, output_data = ?, error_message = ? 
                WHERE trace_id = ?
            """, (status, output_data, error_message, trace_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating trace log: {e}")
            return False

    def get_correctly_answered_questions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get questions the user has answered correctly
        Returns a list of dicts with question details
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get all quiz attempts for user with responses
            cursor.execute("""
                SELECT responses, topic, difficulty FROM quiz_attempts 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit * 5))  # Get more to account for filtering
            
            rows = cursor.fetchall()
            conn.close()
            
            correctly_answered = []
            seen_questions = set()
            
            for row in rows:
                try:
                    responses_text = row["responses"] if row["responses"] else ""
                    if not responses_text:
                        continue
                        
                    responses_data = json.loads(responses_text)
                    if not isinstance(responses_data, list):
                        continue
                    
                    for response in responses_data:
                        # Only add if user answered correctly
                        if response.get("is_correct", False):
                            question_text = response.get("question", "")
                            if question_text and question_text not in seen_questions:
                                correctly_answered.append({
                                    "question": question_text,
                                    "topic": response.get("topic", row["topic"]),
                                    "difficulty": response.get("difficulty", row["difficulty"]),
                                    "correct_answer": response.get("correct_answer", ""),
                                    "options": response.get("options", [])
                                })
                                seen_questions.add(question_text)
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    logger.debug(f"Could not parse responses for attempt: {e}")
                    continue
            
            return correctly_answered[:limit]
        except Exception as e:
            logger.error(f"Error getting correctly answered questions: {e}")
            return []

