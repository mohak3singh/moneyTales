"""
Database Models for Financial Education Platform
Tracks: Users, Quiz History, Gamification, Trace Logs
"""

import sqlite3
from datetime import datetime
from enum import Enum
from dataclasses import dataclass


class Badge(Enum):
    """Gamification badges"""
    FIRST_QUIZ = "First Quiz Completed"
    PERFECT_SCORE = "Perfect Score"
    STREAK_5 = "5-Quiz Streak"
    FINANCIAL_PRO = "Financial Pro"
    CURIOUS_MIND = "Curious Mind (10+ quizzes)"


@dataclass
class User:
    """User profile with personalization data"""
    user_id: str
    name: str
    age: int
    hobbies: str  # comma-separated
    level: int = 1
    points: int = 0
    badges: str = ""  # comma-separated badge names
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class QuizAttempt:
    """Quiz history tracking"""
    attempt_id: str
    user_id: str
    quiz_id: str
    topic: str
    difficulty: str  # easy, medium, hard
    score: int
    max_score: int
    time_taken_seconds: int
    answered_questions: int
    correct_answers: int
    responses: str = ""  # JSON string of user responses
    feedback: str = ""  # Feedback message for user
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class GamificationEvent:
    """Track points and level-ups"""
    event_id: str
    user_id: str
    event_type: str  # quiz_completed, badge_earned, level_up
    points_awarded: int
    badge_name: str = None
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class TraceLog:
    """Trace logs for orchestrator and agent execution"""
    trace_id: str
    request_id: str
    agent_name: str
    step_number: int
    status: str  # pending, in_progress, completed, failed
    input_data: str
    output_data: str = None
    error_message: str = None
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
