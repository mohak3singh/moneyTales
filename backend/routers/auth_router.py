"""
Authentication Router
Endpoints for user registration and authentication
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from pathlib import Path
import json
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Path to store user credentials - use absolute path
PROJECT_ROOT = Path(__file__).parent.parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "backend" / "data" / "credentials.json"


class RegisterRequest(BaseModel):
    """User registration request"""
    user_id: str
    name: str
    age: int
    hobbies: str
    username: str
    password: str


class LoginRequest(BaseModel):
    """User login request"""
    username: str
    password: str


def load_credentials() -> Dict[str, Any]:
    """Load credentials from file"""
    try:
        if CREDENTIALS_FILE.exists():
            with open(CREDENTIALS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading credentials: {e}")
    return {}


def save_credentials(credentials: Dict[str, Any]):
    """Save credentials to file"""
    try:
        CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f, indent=2)
    except Exception as e:
        print(f"Error saving credentials: {e}")


def setup_auth_router(database):
    """Setup authentication routes"""

    @router.post("/register")
    async def register_user(request: RegisterRequest) -> Dict[str, Any]:
        """
        Register a new user
        
        Input:
        - name: User's full name
        - age: User's age
        - hobbies: User's hobbies (comma-separated)
        - username: Username for login
        - password: User's password
        
        Returns: Success message and user_id
        """
        try:
            from backend.db.models import User
            import logging
            import time
            logger = logging.getLogger(__name__)
            
            logger.info(f"Registering user: {request.name} with user_id: {request.user_id}")
            
            # Create new user in database FIRST
            user = User(
                user_id=request.user_id,
                name=request.name,
                age=request.age,
                hobbies=request.hobbies
            )
            success = database.create_user(user)
            
            if not success:
                raise Exception(f"Failed to create user in database")
            
            logger.info(f"User {request.user_id} created in database successfully")
            
            # Verify user was created by fetching from database (with multiple retries)
            max_retries = 5
            verify_user = None
            for attempt in range(max_retries):
                verify_user = database.get_user(request.user_id)
                if verify_user:
                    logger.info(f"User verified in database on attempt {attempt + 1}: {verify_user.name}")
                    break
                if attempt < max_retries - 1:
                    logger.warning(f"User verification failed on attempt {attempt + 1}/{max_retries}, retrying...")
                    time.sleep(0.3)
            
            if not verify_user:
                logger.error(f"User verification failed after {max_retries} attempts")
                raise Exception(f"User verification failed - user {request.user_id} not found in database after creation. Please try again.")
            
            logger.info(f"User verified in database: {verify_user.name}")
            
            # Save credentials AFTER database confirmation
            credentials = load_credentials()
            credentials[request.username.lower()] = {
                "user_id": request.user_id,
                "name": request.name,
                "password": request.password,
                "age": request.age
            }
            save_credentials(credentials)
            logger.info(f"Credentials saved for username: {request.username.lower()}")
            
            return {
                "status": "success",
                "message": f"User {request.name} registered successfully",
                "user_id": request.user_id,
                "name": request.name,
                "age": request.age
            }

        except HTTPException:
            raise
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Registration error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/login")
    async def login_user(request: LoginRequest) -> Dict[str, Any]:
        """
        Validate user login credentials
        
        Input:
        - username: Username
        - password: Password
        
        Returns: User info if credentials valid
        """
        try:
            credentials = load_credentials()
            
            username_lower = request.username.lower()
            
            if username_lower not in credentials:
                raise HTTPException(status_code=401, detail="Username not found")
            
            user_creds = credentials[username_lower]
            
            if user_creds["password"] != request.password:
                raise HTTPException(status_code=401, detail="Incorrect password")
            
            return {
                "status": "success",
                "user_id": user_creds["user_id"],
                "name": user_creds["name"],
                "age": user_creds["age"],
                "message": f"Welcome {user_creds['name']}!"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/credentials")
    async def get_all_credentials() -> Dict[str, Any]:
        """Get all credentials (for initialization only)"""
        credentials = load_credentials()
        return {
            "status": "success",
            "credentials": credentials
        }

    return router
