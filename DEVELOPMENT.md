# MoneyTales Development Guide 🚀

Guide for developers extending and customizing MoneyTales.

---

## 🏗️ Architecture Overview

```
Request Flow:
┌──────────────┐
│   Frontend   │ (Streamlit)
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────────────┐
│   FastAPI Router     │ (quiz_router, submit_router, gamification_router)
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────┐
│    Orchestrator              │ (Coordinates agents & logs)
└──────┬───────────────────────┘
       │
       ├─→ RAGAgent (Get context)
       ├─→ DifficultyAgent (Assess level)
       ├─→ StoryAgent (Generate story)
       ├─→ QuizAgent (Generate questions)
       ├─→ EvaluatorAgent (Grade answers)
       └─→ GamificationAgent (Calculate rewards)
       │
       ▼
┌──────────────────────────────┐
│    Database (SQLite)         │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│    RAG System                │ (PDFs → Chunks → Vectors)
└──────────────────────────────┘
```

---

## 👨‍💻 Developer Workflow

### 1. Setting Up Development Environment

```bash
# Clone and setup
git clone <repo>
cd MoneyTales
chmod +x setup.sh make_executable.sh
./setup.sh

# Activate venv
cd backend
source venv/bin/activate

# Install dev tools
pip install -r requirements.txt
pip install pytest black flake8
```

### 2. Code Style & Formatting

```bash
# Format code with black
black backend/

# Check code quality
flake8 backend/

# Run tests
pytest backend/tests/
```

### 3. Running in Development Mode

```bash
# Backend with auto-reload
cd backend
python main.py  # uvicorn auto-reloads on file changes

# Frontend with fast refresh
streamlit run frontend/streamlit_app.py
```

---

## 🧠 Agent Development Guide

### Understanding the Agent Base Class

```python
# base_agent.py
class Agent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.agent_id = str(uuid.uuid4())
    
    @abstractmethod
    def execute(self, **kwargs) -> dict:
        """All agents must implement execute()"""
        pass
```

### Creating a New Agent

**Example: Create a TranslationAgent**

1. Create `backend/agents/translation_agent.py`:

```python
from .base_agent import Agent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TranslationAgent(Agent):
    """Translate quiz questions to other languages"""
    
    def __init__(self):
        super().__init__("TranslationAgent")
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Translate content
        
        Args:
            text: str - text to translate
            target_language: str - language code (e.g., 'es', 'fr')
        
        Returns:
            dict with translated text
        """
        try:
            text = kwargs.get("text", "")
            target_language = kwargs.get("target_language", "es")
            
            self.log_execution("Translation", "started", {
                "language": target_language,
                "text_length": len(text)
            })
            
            # Your translation logic here
            translated = self._translate(text, target_language)
            
            return {
                "status": "success",
                "original": text,
                "translated": translated,
                "language": target_language,
                "agent": self.name
            }
        
        except Exception as e:
            logger.error(f"Error in TranslationAgent: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }
    
    def _translate(self, text: str, language: str) -> str:
        """Implement translation logic"""
        # Could use Google Translate API, etc.
        return text
```

2. Register in `backend/main.py`:

```python
from agents.translation_agent import TranslationAgent

# In lifespan function:
orchestrator.register_agent("TranslationAgent", TranslationAgent())
```

3. Use in orchestrator or routers

### Agent Best Practices

✅ **DO:**
- Always inherit from `Agent` base class
- Implement `execute(**kwargs) -> dict`
- Return `{"status": "success", ...}` or `{"status": "error", ...}`
- Log execution with `self.log_execution()`
- Validate input parameters
- Handle exceptions gracefully

❌ **DON'T:**
- Make blocking network calls without timeout
- Modify database directly (go through orchestrator)
- Return raw exceptions to frontend
- Skip error handling
- Make assumptions about input data

---

## 🎯 Adding New Quiz Topics

### 1. Add Questions to QuizAgent

Edit `backend/agents/quiz_agent.py`:

```python
def _easy_questions(self, topic: str) -> List[Dict[str, Any]]:
    """Generate easy difficulty questions"""
    
    if "investing" in topic.lower():
        return [
            {
                "question_id": "invest_easy_001",
                "question": "What does it mean to invest?",
                "type": "multiple_choice",
                "options": [
                    "Putting money into something with hope of returns",
                    "Saving money under your bed",
                    "Spending money on toys",
                    "Losing money"
                ],
                "correct_answer": 0,
                "explanation": "Investing means buying assets hoping they increase in value."
            },
            # Add more questions...
        ]
    
    # Return existing questions for other topics
    return self._default_easy_questions()
```

### 2. Add Context to RAG

Add content to `data/text/financial_concepts.txt`:

```
INVESTING BASICS
================

What is an investment?
An investment is using money to buy something that might grow in value 
or produce income over time.

Types of investments:
- Stocks: Own part of a company
- Bonds: Loan money at interest
- Real Estate: Buy property
- Savings Account: Earn interest
```

### 3. Test New Topic

```bash
# Start backend and frontend
# In frontend, select new topic
# Verify questions and story are personalized
```

---

## 📊 Database Schema & Operations

### Adding a New Table

1. Update `backend/db/models.py`:

```python
@dataclass
class Achievement:
    """User achievements"""
    achievement_id: str
    user_id: str
    achievement_type: str
    points_reward: int
    unlocked_at: str = None
```

2. Create table in `backend/db/database.py`:

```python
def init_db(self):
    # ... existing tables ...
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            achievement_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            achievement_type TEXT NOT NULL,
            points_reward INTEGER NOT NULL,
            unlocked_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
```

3. Add CRUD operations:

```python
def create_achievement(self, achievement: Achievement) -> bool:
    """Create achievement record"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO achievements 
            (achievement_id, user_id, achievement_type, points_reward, unlocked_at)
            VALUES (?, ?, ?, ?, ?)
        """, (achievement.achievement_id, achievement.user_id, 
              achievement.achievement_type, achievement.points_reward, 
              achievement.unlocked_at))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error creating achievement: {e}")
        return False
```

---

## 🔌 Adding API Endpoints

### Create New Router

`backend/routers/achievements_router.py`:

```python
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/api/achievements", tags=["achievements"])

def setup_achievements_router(orchestrator, database):
    """Setup achievement routes"""
    
    @router.get("/{user_id}")
    async def get_achievements(user_id: str) -> Dict[str, Any]:
        """Get user's achievements"""
        try:
            # Get achievements from database
            # Return formatted response
            return {"status": "success", "achievements": [...]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
```

### Register Router in main.py

```python
from routers.achievements_router import setup_achievements_router

# In startup function:
achievements_router = setup_achievements_router(orchestrator, db)
app.include_router(achievements_router)
```

---

## 🧪 Testing Guide

### Unit Testing an Agent

`backend/tests/test_agents.py`:

```python
import pytest
from backend.agents.quiz_agent import QuizAgent

def test_quiz_generation():
    """Test quiz agent generates questions"""
    agent = QuizAgent()
    
    result = agent.execute(
        topic="saving money",
        difficulty="easy",
        num_questions=5,
        rag_context="",
        user_profile={"name": "Alex", "age": 10}
    )
    
    assert result["status"] == "success"
    assert len(result["questions"]) == 5
    assert result["difficulty"] == "easy"

def test_quiz_validation():
    """Test quiz validation"""
    agent = QuizAgent()
    
    result = agent.execute(
        num_questions=-1  # Invalid
    )
    
    assert result["status"] == "error"
```

### Running Tests

```bash
cd backend
pytest tests/ -v  # Verbose output
pytest tests/test_agents.py::test_quiz_generation  # Single test
pytest --cov=agents tests/  # With coverage
```

---

## 🚀 Performance Optimization

### 1. Caching

Add caching to RAG searches:

```python
from functools import lru_cache

class RAGManager:
    @lru_cache(maxsize=128)
    def search(self, query: str, top_k: int = 5):
        """Cached search for repeated queries"""
        return self.vector_store.search(query, top_k)
```

### 2. Database Optimization

```python
# Add indexes for frequently queried columns
cursor.execute("CREATE INDEX idx_user_id ON quiz_attempts(user_id)")
cursor.execute("CREATE INDEX idx_created_at ON quiz_attempts(created_at)")
```

### 3. Asynchronous Operations

Upgrade quiz generation to async:

```python
# In routers/quiz_router.py
from concurrent.futures import ThreadPoolExecutor

@router.post("/generate/async")
async def generate_quiz_async(user_id: str, topic: str):
    """Non-blocking quiz generation"""
    executor = ThreadPoolExecutor()
    
    # Run orchestration in background
    result = await asyncio.get_event_loop().run_in_executor(
        executor,
        lambda: orchestrator.generate_quiz(user_id, topic)
    )
    
    return result
```

---

## 🔐 Security Considerations

### 1. Input Validation

```python
from pydantic import BaseModel, Field

class QuizRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=50)
    topic: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('topic')
    def topic_must_be_valid(cls, v):
        valid_topics = ["money basics", "saving", ...]
        if v.lower() not in valid_topics:
            raise ValueError('Invalid topic')
        return v
```

### 2. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/generate")
@limiter.limit("10/minute")  # Max 10 requests per minute
async def generate_quiz(request: Request, ...):
    pass
```

### 3. Authentication (Future)

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.post("/generate")
async def generate_quiz(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Validate token
    pass
```

---

## 📈 Scaling Considerations

### 1. Horizontal Scaling

- Separate database into dedicated service
- Use Redis for caching
- Deploy backend with load balancer
- Use cloud storage for PDFs

### 2. Database Migration

```python
# Use Alembic for migrations
# alembic revision -m "Add new table"
# alembic upgrade head
```

### 3. Vector Store Upgrade

```python
# Replace simple store with FAISS
from faiss import IndexFlatL2

class FAISSVectorStore:
    def __init__(self, dimension=384):
        self.index = IndexFlatL2(dimension)
```

---

## 🐛 Debugging Tips

### 1. Enable Detailed Logging

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Access Trace Logs

```
Visit: http://localhost:8000/api/quiz/trace/{request_id}
Shows all agent execution steps
```

### 3. Database Inspection

```bash
# Open SQLite database
sqlite3 backend/moneytales.db

# View tables
.tables

# Query data
SELECT * FROM users LIMIT 5;
SELECT * FROM quiz_attempts WHERE user_id='child_001';
```

### 4. API Testing

```bash
# Test endpoint with curl
curl -X POST http://localhost:8000/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"child_001","topic":"saving"}'

# Or use Python requests
import requests
response = requests.post(
    "http://localhost:8000/api/quiz/generate",
    json={"user_id": "child_001", "topic": "saving"}
)
print(response.json())
```

---

## 📚 Code Conventions

### File Organization

```
backend/
├── agents/           # Agent implementations
├── db/              # Database layer
├── services/        # Business logic services
├── rag/             # RAG system
├── routers/         # API route handlers
├── tests/           # Test files
├── utils/           # Utility functions (optional)
├── main.py          # Entry point
└── orchestrator.py  # Core orchestration
```

### Naming Conventions

```python
# Classes: PascalCase
class QuizAgent:
    pass

# Functions/methods: snake_case
def generate_quiz():
    pass

# Constants: UPPER_CASE
MAX_QUESTIONS = 10
DEFAULT_DIFFICULTY = "medium"

# Private methods: _snake_case
def _internal_method():
    pass
```

### Docstring Format

```python
def execute(self, **kwargs) -> Dict[str, Any]:
    """
    Short description.
    
    Longer description with details about what the method does,
    how it works, and important notes.
    
    Args:
        param1 (str): Description of param1
        param2 (int): Description of param2
    
    Returns:
        Dict[str, Any]: Description of return value
        
    Raises:
        ValueError: When something goes wrong
    """
    pass
```

---

## 🔄 Contribution Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-agent
   ```

2. **Make changes**
   - Write tests first (TDD)
   - Implement feature
   - Format code: `black backend/`

3. **Test thoroughly**
   ```bash
   pytest backend/tests/
   ```

4. **Commit & push**
   ```bash
   git add .
   git commit -m "Add new agent with tests"
   git push origin feature/new-agent
   ```

5. **Create pull request**
   - Include description
   - Link any issues
   - Wait for review

---

## 📖 Useful Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- Streamlit Docs: https://docs.streamlit.io/
- Python Best Practices: https://pep8.org/
- SQLite Query Guide: https://www.sqlite.org/
- pytest Documentation: https://docs.pytest.org/

---

**Happy Coding! 🚀**
