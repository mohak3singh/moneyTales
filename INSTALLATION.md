# MoneyTales Installation & Setup Guide 📚

Complete step-by-step guide to get MoneyTales running on your machine.

---

## 📋 Prerequisites

Before you start, ensure you have:
- **Python 3.8+** installed (`python3 --version`)
- **pip** package manager
- **Git** (optional, for version control)
- ~500 MB disk space
- Terminal/Command Prompt access

---

## 🚀 Installation Steps

### Step 1: Clone or Navigate to Project

```bash
# Navigate to the MoneyTales directory
cd /path/to/MoneyTales
```

### Step 2: Create Python Virtual Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

**What is a virtual environment?**
A virtual environment isolates Python dependencies for this project from your system Python, preventing conflicts.

### Step 3: Install Dependencies

```bash
# Make sure you're in backend directory with venv activated
pip install --upgrade pip
pip install -r requirements.txt
```

**What gets installed?**
- FastAPI & Uvicorn (backend framework)
- Pydantic (data validation)
- NumPy (numerical computing)
- pytest (testing)
- And development tools

This should take 2-3 minutes. You'll see packages being downloaded and installed.

### Step 4: Verify Installation

```bash
# Test that everything installed correctly
python -c "import fastapi; print('✅ FastAPI installed')"
python -c "import streamlit; print('✅ Streamlit installed')"
python -c "import numpy; print('✅ NumPy installed')"
```

---

## 🏃 Running the Application

### Starting the Backend

```bash
# From backend directory with venv activated
python main.py
```

You should see:
```
🚀 Starting MoneyTales Backend...
📦 Initializing database...
📝 Seeding mock users...
🧠 Initializing RAG system...
✅ RAG initialized with X document chunks
🎭 Initializing orchestrator...
✅ All agents registered!
🎉 MoneyTales Backend Ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Backend is ready when you see:** `Uvicorn running on http://0.0.0.0:8000`

### Starting the Frontend (in a NEW terminal)

```bash
# From project root (NOT backend directory)
# Make sure you DON'T have venv activated in this terminal
streamlit run frontend/streamlit_app.py
```

You should see:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Click the link or navigate to `http://localhost:8501` in your browser.

---

## ✅ Verification Checklist

After starting both backend and frontend:

- [ ] Backend running at `http://localhost:8000`
- [ ] Frontend running at `http://localhost:8501`
- [ ] Can see API docs at `http://localhost:8000/docs`
- [ ] Frontend loads with "MoneyTales" title
- [ ] Can select a user profile
- [ ] Can click "Generate Quiz" button

### Test the API

In a new terminal, test the backend:

```bash
# Check health
curl http://localhost:8000/health

# Should respond with:
# {"status":"healthy","database":"connected","rag":"initialized","orchestrator":"ready"}
```

---

## 🎮 First Quiz Walkthrough

1. **Open Frontend**: Go to `http://localhost:8501`

2. **Select User Profile**
   - Choose one of the 4 test users
   - Click "Enter as Selected User"

3. **Take a Quiz**
   - Go to "Take Quiz" section
   - Choose a topic (e.g., "Money Basics")
   - Choose difficulty (e.g., "Medium")
   - Click "Generate Quiz"

4. **See What Happens**
   - Backend processes your request through all agents
   - Story is generated personalized to the user
   - 5 quiz questions appear
   - Answer the questions
   - Click "Submit Answers"

5. **Check Results**
   - See your score and feedback
   - View points earned
   - Check for badges and level-ups
   - See personalized feedback for each question

---

## 📊 Testing Different Scenarios

### Scenario 1: Low Performer
- User: Alex (child_001)
- Select difficulty: "Medium"
- Intentionally answer wrong (click different options)
- Expected: Easy difficulty recommended next time

### Scenario 2: High Performer
- User: Sam (child_002)
- Select difficulty: "Easy"
- Try to answer all correctly
- Expected: Hard difficulty recommended next time

### Scenario 3: Perfect Score
- User: Jordan (child_003)
- Answer all questions correctly
- Expected: "Perfect Score" badge

### Scenario 4: 5 Quiz Streak
- Complete 5 consecutive quizzes with any score
- Expected: "5-Quiz Streak" badge and bonus points

---

## 🔍 Debugging Tips

### Backend Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process using port 8000 if needed
kill -9 <PID>
```

### Frontend Can't Connect to Backend
- Ensure backend is running (check `http://localhost:8000`)
- Check browser console for CORS errors (F12)
- Verify both are running in parallel

### Database Issues
```bash
# Reset database
rm backend/moneytales.db
python main.py  # Recreates database with fresh mock users
```

### Virtual Environment Not Activating
```bash
# macOS/Linux - make script executable
chmod +x backend/venv/bin/activate

# Try with absolute path
source /full/path/to/MoneyTales/backend/venv/bin/activate
```

### Import Errors
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

---

## 📁 Project Structure After Installation

```
MoneyTales/
├── backend/
│   ├── venv/                    # Virtual environment (created)
│   ├── moneytales.db           # SQLite database (created)
│   ├── agents/
│   ├── db/
│   ├── services/
│   ├── rag/
│   ├── routers/
│   ├── orchestrator.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── streamlit_app.py
├── data/
│   ├── pdfs/
│   ├── text/                   # Sample content created here
│   └── embeddings/            # Vector store created here
├── README.md
└── INSTALLATION.md
```

---

## 🔧 Configuration Options

### Change Backend Port
Edit `backend/main.py`:
```python
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,  # Change this
        ...
    )
```

### Change Frontend Port
```bash
streamlit run frontend/streamlit_app.py --server.port=8080
```

### Update API Base URL
Edit `frontend/streamlit_app.py`:
```python
API_BASE_URL = "http://localhost:9000/api"  # Change this
```

---

## 🚀 Optional: Using the Convenience Scripts

### Using setup.sh (macOS/Linux)

```bash
chmod +x setup.sh
./setup.sh
```

This automatically sets up the virtual environment and installs dependencies.

### Using run.sh (macOS/Linux)

```bash
chmod +x run.sh
./run.sh
```

This starts both backend and frontend (requires separate terminals).

---

## 📚 Next Steps After Installation

1. **Explore API Documentation**
   - Visit `http://localhost:8000/docs`
   - Try the endpoints interactively

2. **Check Trace Logs**
   - After taking a quiz, note the `request_id`
   - Go to `/api/quiz/trace/{request_id}` to see agent execution

3. **Review Code**
   - Start with `backend/main.py` to understand flow
   - Check `backend/orchestrator.py` to see agent coordination
   - Review individual agents in `backend/agents/`

4. **Customize**
   - Add new quiz topics in `backend/agents/quiz_agent.py`
   - Modify gamification rules in `backend/agents/gamification_agent.py`
   - Customize UI in `frontend/streamlit_app.py`

---

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | Run `pip install -r requirements.txt` with venv activated |
| `Port 8000 already in use` | Kill existing process: `lsof -i :8000 \| grep LISTEN` then `kill -9 <PID>` |
| `Cannot connect to backend from frontend` | Ensure backend is running, check `http://localhost:8000/health` |
| `Database locked error` | Close other instances and delete `moneytales.db` |
| `venv not activating` | Use full path or `python -m venv` instead |
| `streamlit: command not found` | Install with `pip install streamlit` |

---

## 📞 Support

If you encounter issues:

1. **Check logs** - Backend prints detailed logs
2. **Test API** - Use `curl` or Postman to test endpoints
3. **Review trace logs** - Visit `/api/quiz/trace/{request_id}`
4. **Check database** - Delete `moneytales.db` to reset

---

## 🎓 Learning Resources

### Understanding the Architecture
- Backend runs as FastAPI web server
- Frontend communicates via HTTP API
- RAG system handles knowledge retrieval
- Agents coordinate complex workflows
- SQLite stores user data locally

### Key Files to Review
1. `backend/main.py` - Application entry point
2. `backend/orchestrator.py` - Agent coordination
3. `backend/agents/` - Individual agent implementations
4. `frontend/streamlit_app.py` - User interface

---

**You're all set! Happy learning! 🎓💰**
