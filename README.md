# MoneyTales - Financial Education for Kids 💰

A full-stack AI-powered platform teaching financial literacy through personalized quizzes, adaptive difficulty, and gamification.

---

## 🎯 Quick Overview

**What it does:**
- Kids take personalized quizzes with AI-generated stories
- Difficulty adapts based on their performance
- Earn points, badges, and level up
- Track progress on a leaderboard

**Key Components:**
- **6 AI Agents** working together
- **RAG Knowledge Base** for content retrieval
- **FastAPI Backend** with SQLite database
- **Streamlit Frontend** for user interface

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.8+
pip
```

### Installation & Running

**1. Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Backend runs at: `http://localhost:8000`

**2. Frontend Setup:**
```bash
# From project root
streamlit run frontend/streamlit_app.py
```
Frontend opens at: `http://localhost:8501`

### Environment Configuration

Create `.env` file in project root:
```bash
OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://oai.stg.azure.backbase.eu
AZURE_DEPLOYMENT_NAME=gpt-4o
GEMINI_API_KEY=your_key_here
```

⚠️ **Important:** `.env` is in `.gitignore` - never commit credentials to GitHub

---

## 🏗️ Complete System Architecture

### End-to-End Quiz Generation Flow

```
┌─────────────────────────────────────────────────────────────┐
│ USER (Streamlit Frontend)                                   │
│ "I want to take a quiz on saving money"                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │ FastAPI Router               │
            │ POST /api/quiz/generate      │
            │ {user_id, topic}             │
            └──────────────┬───────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────────┐
        │ ORCHESTRATOR (Main Coordinator)              │
        │ - Receives request                           │
        │ - Generates request_id for tracing           │
        │ - Calls agents in sequence                   │
        │ - Logs each step for debugging               │
        └──────────────┬───────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬─────────────────┐
        │              │              │                 │
        ▼              ▼              ▼                 ▼
   ┌─────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐
   │DATABASE │  │RAG AGENT     │  │DIFFICULTY   │  │STORY     │
   │         │  │              │  │AGENT        │  │AGENT     │
   │Fetches: │  │Searches for: │  │Analyzes:    │  │Generates:│
   │- User   │  │"saving"      │  │- Quiz       │  │Personal- │
   │- Profile   │  │content    │  │  history    │  │ized      │
   │- Age    │  │Returns:      │  │- Recent     │  │narrative │
   │- Quiz   │  │- 3 chunks    │  │  scores     │  │for:      │
   │  history   │  │  about     │  │Recommends:  │  │- 10yo    │
   │- Avg    │  │  saving      │  │- Level:     │  │- Gaming  │
   │  score  │  │- Context     │  │  MEDIUM     │  │  interest│
   └────┬────┘  └────┬──────────┘  └────┬────────┘  └────┬─────┘
        │            │                  │                │
        │ Returns:   │ Returns:         │ Returns:      │ Returns:
        │ {         │ {                │ {             │ {
        │  age:10,  │  chunks: [...]   │  difficulty:  │  story:
        │  hobbies: │ }                │  "medium"     │  "Alex's
        │  gaming   │                  │ }             │   Money
        │ }         │                  │               │   Adv."
        └───────────┼──────────────────┼───────────────┘
                    │                  │
                    ▼                  ▼
            ┌─────────────────────────────────┐
            │ QUIZ AGENT                      │
            │                                 │
            │ Generates 5 questions:          │
            │ - Level: MEDIUM                 │
            │ - Topic: Saving Money           │
            │ - Multiple choice (4 options)   │
            │ - With explanations             │
            │                                 │
            │ Example Q:                      │
            │ "Why is saving important?"      │
            │ A) To buy toys                  │
            │ B) To use for future goals ✓    │
            │ C) To show off                  │
            │ D) No reason                    │
            └──────────────┬──────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
        ┌───────▼──────┐    ┌─────────▼──────┐
        │Question 1    │    │Question 2      │
        │"What is..."  │    │"Why should...? │
        └───────┬──────┘    └─────────┬──────┘
                │                     │
                └──────────┬──────────┘
                           │
            ┌──────────────▼───────────────┐
            │ RESPONSE TO FRONTEND         │
            │                              │
            │ {                            │
            │   "request_id": "uuid123",   │
            │   "story": "Alex's story...",│
            │   "questions": [Q1, Q2, ...],│
            │   "difficulty": "medium",    │
            │   "topic": "saving money"    │
            │ }                            │
            └──────────────┬───────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Frontend    │
                    │ Displays    │
                    │ Story +     │
                    │ Questions   │
                    └─────────────┘
```

### Answer Submission & Evaluation Flow

```
┌─────────────────────────────────────────┐
│ USER SUBMITS ANSWERS                    │
│ Answered 4 out of 5 correctly (80%)     │
└──────────────────────┬──────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ FastAPI Router               │
        │ POST /api/submit/answers     │
        │ {user_id, answers, questions}│
        └──────────────┬───────────────┘
                       │
                       ▼
      ┌────────────────────────────────────┐
      │ EVALUATOR AGENT                    │
      │                                    │
      │ - Compare user answers to correct  │
      │ - Calculate score: 4/5 = 80%       │
      │ - Generate feedback for each:      │
      │   Q1: "Correct! ✓"                 │
      │   Q2: "Great explanation!"         │
      │   Q3: "Close! Think about..."      │
      └──────────────┬─────────────────────┘
                     │
                     ▼
      ┌────────────────────────────────────┐
      │ GAMIFICATION AGENT                 │
      │                                    │
      │ Calculate Points:                  │
      │ - Base: +10 points                 │
      │ - Score 80%: +20 bonus             │
      │ - Total: +30 points ✓              │
      │                                    │
      │ Check Achievements:                │
      │ - First Quiz? No                   │
      │ - Perfect score? No                │
      │ - Level up? Not yet                │
      │ - Badges earned? None              │
      └──────────────┬─────────────────────┘
                     │
                     ▼
      ┌────────────────────────────────────┐
      │ DATABASE UPDATES                   │
      │                                    │
      │ - Save quiz attempt (80% score)    │
      │ - Update user.points: +30          │
      │ - Update user.level: check         │
      │ - Log gamification event           │
      └──────────────┬─────────────────────┘
                     │
                     ▼
      ┌────────────────────────────────────┐
      │ DIFFICULTY AGENT (for next quiz)   │
      │                                    │
      │ Analyzes: 80% score                │
      │ Decision: Score ≥ 80%              │
      │ Next difficulty: HARD ↑            │
      │ (User progressed!)                 │
      └──────────────┬─────────────────────┘
                     │
                     ▼
      ┌────────────────────────────────────┐
      │ RESPONSE TO FRONTEND               │
      │                                    │
      │ {                                  │
      │   "score": 80,                     │
      │   "percentage": 80.0,              │
      │   "feedback": "Excellent work!",   │
      │   "points_earned": 30,             │
      │   "total_points": 380,             │
      │   "level": 0,                      │
      │   "badges_earned": [],             │
      │   "leveled_up": false,             │
      │   "next_difficulty": "hard"        │
      │ }                                  │
      └──────────────┬─────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │ Frontend    │
              │ Shows:      │
              │ - Score 80% │
              │ - +30 pts   │
              │ - Feedback  │
              │ - Buttons   │
              │   for       │
              │   retake    │
              └─────────────┘
```

---

## 🤖 Six AI Agents: Detailed Breakdown

### 1. **StoryAgent** - Narrative Generation
**Purpose:** Creates engaging, age-appropriate stories to introduce quiz topics

**Input:**
- User profile (age, interests/hobbies, name)
- Topic (e.g., "saving money")
- Difficulty level (easy/medium/hard)

**Process:**
1. Personalizes story around user's interests
2. Simplifies language for age group
3. Creates relatable characters & scenarios
4. Adjusts complexity based on difficulty

**Output:**
- 200-300 word engaging story
- Example: "Alex's Money Adventure"

**Example for 10-year-old gamer:**
```
"🌟 Alex's Gaming Prize Challenge 🌟
You want to save for a gaming tournament! 
Every chore = $5 earned...
[Story continues with gaming themes]
```

---

### 2. **QuizAgent** - Question Generation
**Purpose:** Creates multiple-choice questions aligned with story & topic

**Input:**
- Topic & difficulty
- Story context (what was covered)
- Knowledge from RAG system

**Process:**
1. Generates 5 questions at correct difficulty
2. Creates 4 multiple-choice options
3. Marks correct answer
4. Easy: "What is...?", "Define..."
5. Medium: "Why...?", "How...?"
6. Hard: "Compare...", "Analyze..."

**Output:**
```json
{
  "question": "Why is saving money important?",
  "options": ["Reason 1", "Reason 2", "Reason 3", "Reason 4"],
  "correct_answer": 1,
  "difficulty": "medium",
  "explanation": "Saving helps achieve future goals..."
}
```

---

### 3. **DifficultyAgent** - Performance Analysis
**Purpose:** Determines quiz difficulty based on user performance

**Input:**
- User's quiz history
- Recent scores
- Age of user

**Process:**
1. Analyzes most recent quiz score
2. Applies thresholds:
   - Score < 50% → Easy (needs help)
   - Score 50-80% → Medium (progressing)
   - Score ≥ 80% → Hard (advanced)
3. New users start at "medium"

**Output:**
```python
recommended_difficulty = "hard"  # User ready for challenge
```

**Example:**
```
User's Recent Scores:
- Quiz 1: 40% → Next: Easy
- Quiz 2: 65% → Next: Medium
- Quiz 3: 85% → Next: Hard ✓
```

---

### 4. **RAGAgent** - Knowledge Retrieval
**Purpose:** Fetches relevant content from knowledge base

**Input:**
- Query (e.g., "saving money")
- Topic

**Process:**
1. Searches vector store for relevant chunks
2. Ranks by semantic similarity
3. Returns top 3 most relevant pieces
4. Provides context to other agents

**Output:**
```
[
  {chunk: "Saving is putting money aside...", similarity: 0.92},
  {chunk: "Benefits of savings...", similarity: 0.87},
  {chunk: "How to save effectively...", similarity: 0.84}
]
```

---

### 5. **EvaluatorAgent** - Answer Grading
**Purpose:** Grades quiz responses & provides feedback

**Input:**
- Questions with correct answers
- User's submitted answers
- Question details

**Process:**
1. Compares each answer to correct
2. Calculates score (correct/total)
3. Generates personalized feedback
4. Explains why answers were right/wrong

**Output:**
```json
{
  "score": 4,
  "max_score": 5,
  "percentage": 80.0,
  "feedback": [
    "Q1: Correct! ✓",
    "Q2: Almost! Think about...",
    "Q3: Great reasoning!",
    "Q4: Good catch!",
    "Q5: Let's review this one..."
  ]
}
```

---

### 6. **GamificationAgent** - Rewards System
**Purpose:** Manages points, badges, levels, and achievements

**Input:**
- Quiz score (percentage)
- User's current progress
- Quiz history

**Process:**
1. Calculates base points (+10)
2. Adds score bonuses:
   - 80%+ score: +20
   - 100% score: +50
3. Checks badge conditions:
   - First Quiz? → "First Quiz Badge"
   - 100% score? → "Perfect Score"
   - 5 quizzes completed? → "5-Quiz Streak"
4. Checks level thresholds:
   - Every 500 points = +1 level

**Output:**
```json
{
  "points_earned": 30,
  "total_points": 380,
  "level": 0,
  "next_level_in": 120,
  "badges_earned": [],
  "new_badges": [],
  "leveled_up": false,
  "position_in_leaderboard": 4
}
```

---

## 📊 Difficulty System Deep Dive

### Difficulty Thresholds
```
EASY:   Score < 50%     (Struggling, needs simpler content)
MEDIUM: Score 50-80%    (Learning, steady progress)
HARD:   Score ≥ 80%     (Mastering, ready for challenge)
```

### Question Characteristics

| Level | Question Type | Example | Length |
|-------|---------------|---------|--------|
| **Easy** | Recall/Definition | "What is saving?" | Short |
| **Medium** | Application | "How can you save money?" | Medium |
| **Hard** | Analysis/Synthesis | "Compare saving vs spending..." | Long |

### Cache Strategy
- Questions cached by: `{topic}_{user_age}_{difficulty}`
- Prevents same question reuse
- Different difficulties = different cache

---

## 📁 Project Structure

```
backend/
├── agents/
│   ├── base_agent.py           # Base class for all agents
│   ├── story_agent.py          # Narrative generation
│   ├── quiz_agent.py           # Question generation
│   ├── difficulty_agent.py     # Performance analysis
│   ├── rag_agent.py            # Knowledge retrieval
│   ├── evaluator_agent.py      # Answer grading
│   └── gamification_agent.py   # Rewards system
├── db/
│   ├── database.py             # SQLite operations
│   ├── models.py               # Data classes
│   └── mock_users.py           # Test data
├── services/
│   ├── pdf_ingestion.py        # PDF extraction
│   ├── chunker.py              # Text chunking
│   ├── vectorstore.py          # Vector embeddings
│   ├── pdf_content_extractor.py # PDF parsing
│   ├── pdf_question_generator.py # Question generation
│   ├── topic_suggester.py      # Topic recommendations
│   └── data_cleaner.py         # Data cleaning
├── routers/
│   ├── quiz_router.py          # Quiz endpoints
│   ├── submit_router.py        # Answer submission
│   ├── auth_router.py          # User authentication
│   ├── gamification_router.py  # Points & leaderboard
│   └── topics_router.py        # Topic suggestions
├── rag/
│   └── __init__.py             # RAG orchestration
├── orchestrator.py             # Main coordinator
├── main.py                     # FastAPI application
└── requirements.txt            # Dependencies

frontend/
└── streamlit_app.py            # User interface

data/
├── pdfs/                       # Educational PDFs
├── text/                       # Extracted text
└── embeddings/                 # Vector store
```

---

## 📚 API Endpoints Reference

| Endpoint | Method | Purpose | Input |
|----------|--------|---------|-------|
| `/api/auth/register` | POST | Create user | name, age, hobbies |
| `/api/auth/login` | POST | User login | username, password |
| `/api/quiz/generate` | POST | Create quiz | user_id, topic |
| `/api/submit/answers` | POST | Submit answers | user_id, answers |
| `/api/gamification/stats/{user_id}` | GET | User rank | user_id |
| `/api/gamification/leaderboard` | GET | Top 10 | limit=10 |
| `/api/quiz/trace/{request_id}` | GET | Debug logs | request_id |
| `/api/topics/suggestions` | POST | Topic ideas | user_id |

---

## 🎮 Complete Gamification System

### Points Breakdown
```
Per Quiz:
  - Completion:     +10 pts
  - 50-79% score:   +10 pts
  - 80-99% score:   +20 pts
  - 100% score:     +50 pts
  
Badges:
  - First Quiz:     1 point
  - Perfect Score:  Unlock when 100%
  - 5-Quiz Streak:  After 5 consecutive quizzes
  - Financial Pro:  After 10 quizzes
  
Total = Base + Score Bonus
```

### Level Progression
```
Points Required for Levels:
- Level 0: 0-499 pts (Start)
- Level 1: 500-999 pts
- Level 2: 1000-1499 pts
- Level 3: 1500+ pts

Example:
Current: 380 pts (Level 0)
After quiz: +30 pts = 410 pts (Still Level 0)
(Need 90 more for Level 1)
```

---

## 💾 Database Design

### Users Table
```
user_id (PK)
name
age
hobbies (comma-separated)
level
points
badges (comma-separated)
created_at
```

### Quiz Attempts Table
```
attempt_id (PK)
user_id (FK)
quiz_id
topic
difficulty
score
max_score
time_taken_seconds
answered_questions
correct_answers
created_at
```

### Gamification Events Table
```
event_id (PK)
user_id (FK)
event_type (QUIZ_COMPLETED, BADGE_EARNED, etc)
points_awarded
created_at
```

### Trace Logs Table
```
log_id (PK)
request_id
step_number
agent_name
status
duration_ms
created_at
```

---

## 🔄 Complete Request Lifecycle Example

### Scenario: 10-year-old gamer takes first quiz

```
1. USER REGISTERS
   Name: Alex
   Age: 10
   Interests: Gaming, Drawing
   
2. USER CLICKS "TAKE QUIZ"
   Topic: "Saving Money"
   
3. BACKEND PROCESSES:
   
   Step 1: DATABASE
   ├─ Fetches: Alex's profile
   ├─ Quiz history: [] (none yet)
   └─ Avg score: N/A
   
   Step 2: RAG AGENT
   ├─ Searches: "saving money"
   ├─ Returns: 3 content chunks
   └─ Total context: 2000 chars
   
   Step 3: DIFFICULTY AGENT
   ├─ Analyzes: First quiz
   ├─ Decision: First time? Use MEDIUM
   └─ Difficulty: MEDIUM
   
   Step 4: STORY AGENT
   ├─ Creates: Gaming-themed story
   ├─ Topic: Saving for gaming tournament
   ├─ Age: Simplified for 10-year-old
   └─ Result: 250-word personalized story
   
   Step 5: QUIZ AGENT
   ├─ Generates: 5 medium-level questions
   ├─ Topics: All about saving money
   ├─ Format: Multiple choice with explanations
   └─ Result: 5 questions ready
   
   Step 6: ORCHESTRATOR
   ├─ Logs: All steps completed
   ├─ Time: 2.5 seconds
   └─ Status: SUCCESS
   
4. FRONTEND DISPLAYS
   ├─ Story: "Alex's Gaming Prize"
   ├─ 5 Questions about saving
   └─ Submit button
   
5. USER ANSWERS: 4/5 correct (80%)
   
6. BACKEND EVALUATES
   
   Step 1: EVALUATOR AGENT
   ├─ Score: 4/5 = 80%
   ├─ Feedback: Generated for each question
   └─ Result: 80% score calculated
   
   Step 2: GAMIFICATION AGENT
   ├─ Points: 10 (base) + 20 (80% bonus) = 30
   ├─ Badges: None yet
   ├─ Level: Still Level 0 (30/500)
   └─ Result: +30 points
   
   Step 3: DATABASE UPDATES
   ├─ Save: Quiz attempt (80% score)
   ├─ Update: User points (30)
   ├─ Update: User level (0)
   └─ Status: SAVED
   
   Step 4: DIFFICULTY AGENT
   ├─ Next quiz analysis: 80% score
   ├─ Threshold check: ≥ 80% = HARD
   ├─ Decision: Next quiz = HARD
   └─ Reasoning: User ready to progress
   
7. RESPONSE SENT
   {
     "score": 80,
     "points_earned": 30,
     "total_points": 30,
     "level": 0,
     "next_difficulty": "hard",
     "badges_earned": ["First Quiz"],
     "leaderboard_position": 3
   }
   
8. FRONTEND SHOWS
   ├─ "Great job! 80%!"
   ├─ "+30 points"
   ├─ "🎖️ First Quiz Badge!"
   ├─ Leaderboard position: 3
   └─ "Next quiz will be HARD"
```

---

## ✅ Key Features

- ✅ **6 AI Agents** with specialized roles
- ✅ **Adaptive Difficulty** based on performance
- ✅ **Gamification** with points, badges, levels
- ✅ **RAG System** for knowledge retrieval
- ✅ **Leaderboard** with real-time rankings
- ✅ **User Authentication** with login/register
- ✅ **Request Tracing** for debugging
- ✅ **Azure OpenAI GPT-4o** integration
- ✅ **SQLite Database** for persistence
- ✅ **Streamlit Frontend** for UI

---

## 🛠️ Quick Development Commands

```bash
# Start backend
cd backend && python main.py

# Start frontend
streamlit run frontend/streamlit_app.py

# View API documentation
http://localhost:8000/docs

# Check system health
curl http://localhost:8000/health

# View trace logs
http://localhost:8000/api/quiz/trace/{request_id}
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `lsof -i :8000` then kill process |
| No module found | `pip install -r requirements.txt` |
| Database locked | Delete `moneytales.db` and restart |
| Frontend won't connect | Ensure backend running on `localhost:8000` |

---

## 📝 License

Educational project - Financial Education Hackathon

---

**🚀 Ready to teach kids about money! Start here and let the agents do the work!**
