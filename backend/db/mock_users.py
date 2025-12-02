"""
Mock User Data Generator
Creates test users with various profiles for development
"""

from .models import User
from .database import Database


MOCK_USERS = [
    {
        "user_id": "child_001",
        "name": "Alex",
        "age": 10,
        "hobbies": "video games, drawing, soccer"
    },
    {
        "user_id": "child_002",
        "name": "Sam",
        "age": 12,
        "hobbies": "reading, science, music"
    },
    {
        "user_id": "child_003",
        "name": "Jordan",
        "age": 8,
        "hobbies": "anime, coding, lego"
    },
    {
        "user_id": "child_004",
        "name": "Casey",
        "age": 11,
        "hobbies": "basketball, art, mathematics"
    },
]


def seed_mock_users(db: Database):
    """Seed database with mock users"""
    for user_data in MOCK_USERS:
        user = User(
            user_id=user_data["user_id"],
            name=user_data["name"],
            age=user_data["age"],
            hobbies=user_data["hobbies"]
        )
        db.create_user(user)
        print(f"Created user: {user.name} ({user.user_id})")


def get_mock_user_profile(user_id: str) -> dict:
    """Get mock user profile for personalization"""
    for user in MOCK_USERS:
        if user["user_id"] == user_id:
            return user
    return None
