# MoneyTales - Financial Education for Kids 💰

A comprehensive, hackathon-ready platform for teaching financial literacy to children through personalized AI agents, interactive quizzes, and gamification.

## 🎯 Project Overview

**MoneyTales** is a full-stack educational platform that combines:
- **6 Specialized AI Agents** for content generation, evaluation, and personalization
- **RAG (Retrieval-Augmented Generation)** knowledge base powered by financial education PDFs
- **FastAPI Backend** with SQLite persistence
- **Streamlit Frontend** for an engaging user experience
- **Gamification System** with points, badges, and levels

### Core Concept
Kids learn financial concepts through:
1. 📖 **Personalized Stories** tailored to their age and interests
2. 🎯 **Adaptive Quizzes** that adjust difficulty based on performance
3. 🏆 **Gamification** that rewards engagement and learning
4. 📊 **Progress Tracking** to monitor improvements

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (Streamlit)                      │
│     - User profiles • Quiz interface • Progress tracking    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 API LAYER (FastAPI)                         │
│   /generateQuiz • /submitAnswers • /getPoints • /trace     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR (Request Coordinator)             │
│      - Routes requests through agents                       │
│      - Logs execution steps for debugging                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ RAGAgent │  │  Story   │  │ QuizGen  │
  │(Retrieve)│  │Agent     │  │Agent     │
  └──────────┘  └──────────┘  └──────────┘
        │              │              │
        ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ Difficulty│ │Evaluator │  │ Gamifi   │
  │Agent     │  │Agent     │  │cation    │
  └──────────┘  └──────────┘  └──────────┘
        │              │              │
        └──────────────┼──────────────┘
                       ▼
        ┌─────────────────────────────┐
        │   DATABASE (SQLite)         │
        │ - Users • Quizzes • Points  │
        │ - Badges • Trace Logs       │
        └─────────────────────────────┘
        
        ┌─────────────────────────────┐
        │   RAG SYSTEM                │
        │ - PDFs → Text → Chunks      │
        │ - Vector Store (FAISS MVP)  │
        │ - Semantic Search           │
        └─────────────────────────────┘
```

---

## 📁 Project Structure

```
MoneyTales/
├── backend/
│   ├── agents/                    # 6 AI Agents
│   │   ├── base_agent.py         # Base agent class
│   │   ├── story_agent.py        # Story generation (personalized narratives)
│   │   ├── quiz_agent.py         # Quiz generation (multiple choice questions)
│   │   ├── difficulty_agent.py   # Difficulty assessment & recommendation
│   │   ├── rag_agent.py          # Knowledge base retrieval
│   │   ├── evaluator_agent.py    # Answer evaluation & feedback
│   │   └── gamification_agent.py # Points, badges, levels
│   ├── db/
│   │   ├── models.py             # Data classes (User, QuizAttempt, etc)
│   │   ├── database.py           # SQLite ORM-like interface
│   │   └── mock_users.py         # Test data
│   ├── services/
│   │   ├── pdf_ingestion.py      # PDF to text conversion
│   │   ├── chunker.py            # Document chunking (section-aware)
│   │   └── vectorstore.py        # Vector embeddings & search
│   ├── rag/
│   │   └── __init__.py           # RAGManager orchestration
│   ├── routers/
│   │   ├── quiz_router.py        # /generateQuiz, /trace endpoints
│   │   ├── submit_router.py      # /submitAnswers endpoint
│   │   └── gamification_router.py # /getPoints, /stats endpoints
│   ├── orchestrator.py           # Main request coordinator
│   ├── main.py                   # FastAPI application
│   └── requirements.txt          # Python dependencies
├── frontend/
│   └── streamlit_app.py          # Streamlit UI
├── data/
│   ├── pdfs/                     # Place PDFs here
│   ├── text/                     # Extracted text files
│   └── embeddings/               # Vector embeddings
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### 1. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Backend

```bash
# From backend directory
python main.py
```

The FastAPI server will start at `http://localhost:8000`

Check health: `http://localhost:8000/health`
API docs: `http://localhost:8000/docs`

### 3. Run Frontend

```bash
# From project root
streamlit run frontend/streamlit_app.py
```

The Streamlit app will open at `http://localhost:8501`

---

## 📚 API Endpoints

### Quiz Generation
**POST** `/api/quiz/generate`
```json
{
  "user_id": "child_001",
  "topic": "saving money"
}
```
**Response:**
```json
{
  "request_id": "uuid",
  "story": "...",
  "questions": [...],
  "difficulty": "medium"
}
```

### Submit Answers
**POST** `/api/submit/answers`
```json
{
  "user_id": "child_001",
  "questions": [...],
  "answers": [0, 1, 2, ...],
  "topic": "saving money",
  "difficulty": "medium"
}
```
**Response:**
```json
{
  "score": 80,
  "percentage": 80.0,
  "feedback": "...",
  "points_earned": 30,
  "badges_earned": [...],
  "new_level": 2,
  "leveled_up": true
}
```

### Get User Points
**GET** `/api/gamification/points/{user_id}`

**Response:**
```json
{
  "points": 350,
  "level": 2,
  "badges": ["First Quiz", "5-Quiz Streak"],
  "quizzes_completed": 6
}
```

### Get User Stats
**GET** `/api/gamification/stats/{user_id}`

### Trace Logs
**GET** `/api/quiz/trace/{request_id}`

Shows step-by-step execution of all agents for debugging

---

## 🎮 Features

### 1. **AI Agents** (6 Specialized)
| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **StoryAgent** | Generate personalized stories | User profile, topic, difficulty | Engaging narrative |
| **QuizAgent** | Create quiz questions | Topic, difficulty, context | 5 multiple-choice Qs |
| **DifficultyAgent** | Assess user performance | Quiz history, age | Recommended difficulty |
| **RAGAgent** | Retrieve knowledge | Query | Relevant context |
| **EvaluatorAgent** | Grade answers | Questions, answers | Score, feedback |
| **GamificationAgent** | Manage rewards | Performance | Points, badges, levels |

### 2. **Gamification System**
- **Points**: Earned per quiz (10 base + bonuses for high scores)
- **Badges**: First Quiz, Perfect Score, 5-Quiz Streak, Financial Pro
- **Levels**: Progress through levels with point milestones
- **Leaderboard**: Top performers ranked by points

### 3. **Adaptive Learning**
- Difficulty adjusts based on quiz performance
- Content personalized to age and interests (hobbies)
- Progress tracking with average score calculation
- Historical quiz data for pattern analysis

### 4. **RAG Knowledge Base**
- Sample financial education content embedded
- Semantic chunking (section-aware)
- Vector search for relevant context
- Fallback handling for missing PDFs

### 5. **Database Features**
- User profiles with personalization data
- Complete quiz history
- Gamification events logging
- Request trace logs for debugging

---

## 📖 Usage Example

### Story for 10-year-old interested in gaming:

```
"🌟 Alex's Money Adventure 🌟

Hi Alex! Today, let's learn about saving money with a fun story!

Imagine Alex wants to save money for a gaming tournament prize pool.

💡 The Challenge:
You have $10. Your goal is to save enough money in 3 months to buy something special for $30.

📖 The Story:
Every week, Alex does chores and earns $5. Instead of spending it all on snacks, 
Alex decides to put the money in a special jar.

Week 1: $5 saved
Week 2: $10 saved (total)
Week 3: $15 saved (total)
Week 4: $20 saved (total) ✨

🎉 Success! Alex reached the goal and bought the gaming tournament tickets!
"
```

---

## 🔧 Configuration

### Mock Users (for testing)
Located in `backend/db/mock_users.py`:
- child_001: Alex, 10 years (gaming, drawing, soccer)
- child_002: Sam, 12 years (reading, science, music)
- child_003: Jordan, 8 years (anime, coding, lego)
- child_004: Casey, 11 years (basketball, art, math)

### Difficulty Thresholds
```python
Easy: < 40% average score
Medium: 40-70% average score
Hard: > 70% average score
```

### Points System
```python
Quiz Completed: 10 points
80% Score: +20 bonus
100% Score: +50 bonus
Badge Earned: 100 points
Daily Streak: 50 points
```

---

## 🧠 How Agents Work

### Example: Quiz Generation Flow

```
1. USER REQUEST
   └─> /api/quiz/generate (user_id=child_001, topic="saving money")

2. ORCHESTRATOR receives request
   └─> Generates request_id for tracking

3. DATABASE AGENT
   └─> Fetches user profile (age 10, hobbies: gaming)
   └─> Retrieves quiz history (6 previous quizzes, avg 75%)

4. RAG AGENT
   └─> Searches vector store for "saving money"
   └─> Retrieves 3 most relevant chunks from knowledge base

5. DIFFICULTY AGENT
   └─> Analyzes 75% average score
   └─> Recommends: "medium" difficulty

6. STORY AGENT
   └─> Takes user profile (10-year-old, gaming fan)
   └─> Takes topic ("saving money")
   └─> Takes difficulty ("medium")
   └─> Generates: Personalized story about saving for gaming prize

7. QUIZ AGENT
   └─> Generates 5 medium-difficulty questions about saving
   └─> Includes explanations for learning

8. ORCHESTRATOR logs all steps
   └─> Saves trace logs for debugging

9. RESPONSE sent to frontend
   └─> Story + Questions + Metadata
```

---

## 🔄 Answer Submission & Evaluation Flow

```
1. USER SUBMITS ANSWERS
   └─> POST /api/submit/answers

2. EVALUATOR AGENT
   └─> Compares answers to correct answers
   └─> Calculates score (e.g., 4/5 = 80%)
   └─> Generates personalized feedback

3. GAMIFICATION AGENT
   └─> Calculates points (10 + 20 bonus)
   └─> Checks for badge achievements
   └─> Determines level progression

4. DATABASE UPDATES
   └─> Quiz attempt recorded
   └─> User points updated (+30)
   └─> Badges added if earned
   └─> Level updated if threshold reached

5. RESPONSE to frontend
   └─> Score, feedback, points, badges, level-up status
   └─> Question-by-question feedback
```

---

## 📊 Trace Logs Example

Access `/api/quiz/trace/{request_id}` to see:

```
Step 1: Database - Fetching User Profile (completed)
Step 2: RAGAgent - Retrieving Knowledge Base (completed)
  └─ Found 3 documents on "saving money"
Step 3: DifficultyAgent - Analyzing Difficulty (completed)
  └─ Recommended: medium
Step 4: StoryAgent - Generating Story (completed)
  └─ Story length: 450 characters
Step 5: QuizAgent - Generating Questions (completed)
  └─ Generated 5 questions
Step 6: Orchestrator - Quiz Generation Completed (completed)
  └─ Total steps: 6
```

---

## 🛠️ Development

### Adding a New Agent

1. Create agent in `backend/agents/new_agent.py`:
```python
from .base_agent import Agent

class NewAgent(Agent):
    def __init__(self):
        super().__init__("NewAgent")
    
    def execute(self, **kwargs) -> dict:
        # Implementation
        return {"status": "success", ...}
```

2. Register in `backend/main.py`:
```python
orchestrator.register_agent("NewAgent", NewAgent())
```

3. Use in orchestrator workflows

### Adding a New Quiz Topic

Edit `backend/agents/quiz_agent.py` and add to question banks:

```python
def _easy_questions(self, topic: str):
    # Add new topic questions
```

---

## 🚨 Troubleshooting

### Backend won't start
- Check port 8000 is available
- Install all requirements: `pip install -r requirements.txt`
- Verify Python 3.8+

### Frontend can't connect to backend
- Ensure backend is running on `localhost:8000`
- Check CORS is enabled in FastAPI
- Look for connection errors in browser console

### Database errors
- Delete `moneytales.db` to reset
- Run `seed_mock_users()` to recreate test data

### RAG not working
- Check `data/text/` has files
- Verify PDF ingestion created sample content
- Vector store needs at least one document

---

## 📈 Future Enhancements

- [ ] Real OpenAI embeddings for better RAG
- [ ] Add real PDF processing (PyPDF2, pdfplumber)
- [ ] Authentication & multi-user support
- [ ] Parent dashboard for monitoring progress
- [ ] Mobile app version
- [ ] Multiplayer challenges & team competitions
- [ ] Community content uploads
- [ ] AI-generated difficulty on-the-fly
- [ ] FAISS for production-grade vector search
- [ ] Caching layer for performance

---

## 📝 License

This project is created for educational purposes.

---

## 👥 Team

Built for hackathon: **Financial Education for Kids**

---

## 📞 Support

For issues or questions:
1. Check trace logs at `/api/quiz/trace/{request_id}`
2. Review API docs at `/docs`
3. Check backend logs for errors

---

**Happy Learning! 🎓💰**
