# Gemini 2.5 Flash API Integration Guide

## Where to Add the Gemini API Key

The system reads the Gemini API key from an **environment variable** called `GEMINI_API_KEY`. You need to set this in ONE of these ways:

### Option 1: Using .env File (Recommended for Development)
```bash
# Create or edit a .env file in the project root
echo 'GEMINI_API_KEY=your-actual-api-key-here' > /Users/mohak@backbase.com/Projects/Internal\ hackathon/MoneyTales/.env

# Make sure your backend loads .env (using python-dotenv)
```

### Option 2: Set as Environment Variable Before Running
```bash
# Linux/Mac
export GEMINI_API_KEY="your-actual-api-key-here"

# Then start the backend
cd /Users/mohak@backbase.com/Projects/Internal\ hackathon/MoneyTales
python3 -m uvicorn backend.main:app --port 8000
```

### Option 3: Set in Docker/Production Environment
```dockerfile
ENV GEMINI_API_KEY=your-actual-api-key-here
```

---

## How to Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Create API Key"**
3. Select or create a Google Cloud project
4. Copy your API key
5. **Keep it secret!** Don't commit it to Git

---

## What the Gemini API Key Does

Once you set `GEMINI_API_KEY`, it enables **THREE features** in MoneyTales:

### 1️⃣ **Personalized Quiz Question Generation** (QuizAgent)
**Location:** `backend/agents/quiz_agent.py` (lines 97-167)

**What it does:**
- When a user generates a quiz, instead of using pre-built question templates, Gemini creates **custom questions** based on:
  - The user's **age** (questions are age-appropriate)
  - The **topic** selected (Money Basics, Saving, etc.)
  - The user's **quiz history** (avoids repeating previous topics)
  - The **difficulty level** (Easy/Medium/Hard)

**Example Flow:**
```
User clicks "Generate Quiz" for "Money Basics" → 
QuizAgent checks if GEMINI_AVAILABLE → 
If YES: Calls _generate_questions_with_gemini() →
  - Sends prompt to Gemini 2.5 Flash
  - Gets personalized questions back
  - Returns 5 unique, tailored questions

If NO: Falls back to pre-built templates
```

**Code Location:**
```python
# backend/agents/quiz_agent.py lines 50-78
if GEMINI_AVAILABLE:
    try:
        questions = self._generate_questions_with_gemini(
            topic, difficulty, num_questions, user_profile
        )
```

**Impact:** Quiz feels more personalized and relevant to each student

---

### 2️⃣ **Intelligent Difficulty Adjustment** (TopicSuggester)
**Location:** `backend/services/topic_suggester.py` (lines 165-205)

**What it does:**
- After a student submits a quiz, Gemini analyzes their **performance history** and recommends the next difficulty level with personalized feedback
- Uses the `analyze_performance_with_gemini()` method

**Example:**
```
Student scores 40% on a Medium quiz →
Submit Router calls analyze_performance_with_gemini() →
Gemini analyzes: "Previous avg was 55%, this is lower. Student struggling." →
Recommends: EASY difficulty
Feedback: "💪 Nice try! You scored 40%. Let's strengthen the basics!"
Insight: "Don't worry, practice makes perfect. Start with easier questions..."
```

**Code Location:**
```python
# backend/routers/submit_router.py lines 56-75
if topic_suggester:
    try:
        analysis = topic_suggester.analyze_performance_with_gemini(
            history_list, percentage, max_score, next_difficulty
        )
```

**Impact:** Adaptive learning - difficulty adjusts based on student performance

---

### 3️⃣ **Age-Appropriate Topic Recommendations** (TopicSuggester)
**Location:** `backend/services/topic_suggester.py` (lines 30-73)

**What it does:**
- When suggesting topics to a student, Gemini generates age-appropriate recommendations
- Ensures 8-year-olds don't see investing topics, and 16-year-olds don't see basic concepts

**Example:**
```
User age: 10 years old →
TopicSuggester.get_topics_for_age(10) →
Gemini recommends: [
  "Saving Money",
  "Pocket Money Management", 
  "Basic Money Concepts",
  "Earning Money",
  "Banking Basics"
]

vs.

User age: 17 years old →
Gemini recommends: [
  "Stock Market Basics",
  "Investing for Teens",
  "Credit Scores",
  "Budgeting Strategies",
  "Financial Goals"
]
```

**Code Location:**
```python
# backend/services/topic_suggester.py lines 33-73
def get_topics_for_age(self, age: int, previous_topics: List[str] = None):
    if not self.model:
        return self._get_default_topics(age)
    # Uses Gemini to generate topics
```

**Impact:** Curriculum is personalized to student's age/maturity

---

## System Architecture

### With Gemini API Key Set ✅
```
User generates quiz
    ↓
QuizAgent._generate_questions_with_gemini()
    ↓
[Sends prompt to Gemini 2.5 Flash API]
    ↓
Gets personalized questions
    ↓
Returns unique, tailored questions
```

### Without Gemini API Key ❌
```
User generates quiz
    ↓
QuizAgent checks GEMINI_AVAILABLE = False
    ↓
Falls back to _generate_questions()
    ↓
Uses pre-built question templates
    ↓
Returns same questions to every student
```

---

## Code Snippets Showing the Integration

### 1. Reading the API Key
```python
# backend/agents/quiz_agent.py line 18
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
else:
    GEMINI_AVAILABLE = False
```

### 2. Using Gemini for Question Generation
```python
# backend/agents/quiz_agent.py lines 97-117
def _generate_questions_with_gemini(self, topic, difficulty, num_questions, user_profile):
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""Generate {num_questions} questions about "{topic}"
    for a {user_profile.get('age')}-year-old student..."""
    
    response = model.generate_content(prompt)
    result = json.loads(response.text.strip())
    return result.get("questions", [])
```

### 3. Fallback Logic
```python
# backend/agents/quiz_agent.py lines 60-73
if GEMINI_AVAILABLE:
    try:
        questions = self._generate_questions_with_gemini(...)
    except Exception as e:
        logger.warning("Gemini failed, using templates")
        questions = self._generate_questions(...)  # Fallback
else:
    questions = self._generate_questions(...)  # Default
```

---

## What Happens When You Set the Key

### Logs You'll See:
```
✅ Gemini API initialized
Generated personalized questions using Gemini for topic: Money Basics
```

### API Calls Made:
- **Quiz Generation:** ~2-5 seconds (Gemini generates questions)
- **Performance Analysis:** ~1-3 seconds (Gemini analyzes history)
- **Topic Suggestion:** ~1-2 seconds (Gemini suggests age-appropriate topics)

### Performance Impact:
- With key: Quiz generation takes 2-5 seconds longer (due to API call)
- Without key: Instant (uses pre-built templates)

---

## Verification Checklist

After setting `GEMINI_API_KEY`, verify it's working:

```bash
# 1. Check if key is set
echo $GEMINI_API_KEY

# 2. Start backend
cd /Users/mohak@backbase.com/Projects/Internal\ hackathon/MoneyTales
export GEMINI_API_KEY="your-key-here"
python3 -m uvicorn backend.main:app --port 8000

# 3. Check logs
tail -f /tmp/backend.log | grep -i gemini

# You should see: "✅ Gemini API initialized"

# 4. Test quiz generation
curl -X POST http://localhost:8000/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","topic":"Money Basics"}'

# 5. Check response
# Should have "questions" array with unique, detailed questions
```

---

## Security Best Practices

❌ **DON'T DO THIS:**
```bash
# Never hardcode the key
GEMINI_API_KEY = "AIzaSyD..."  # ❌ WRONG!
```

✅ **DO THIS:**
```bash
# Use environment variables
export GEMINI_API_KEY="your-key"

# Or use .env file
# .env
GEMINI_API_KEY=your-key-here
```

✅ **For Production:**
```bash
# Use environment variables from your deployment platform
# (AWS Secrets Manager, Azure Key Vault, etc.)
```

---

## Troubleshooting

### Issue: "GEMINI_API_KEY not set"
```bash
# Solution: Check if key is exported
echo $GEMINI_API_KEY

# If empty, set it
export GEMINI_API_KEY="your-api-key"
```

### Issue: Gemini questions look same every time
```bash
# Possible causes:
# 1. API key not set (falling back to templates)
# 2. Gemini API rate limited (falls back to templates)
# 3. Network issue

# Solution: Check logs
tail -f /tmp/backend.log | grep -i "Gemini\|Template"
```

### Issue: Questions generation is slow
```bash
# Expected: 2-5 seconds with Gemini
# Normal behavior!

# If > 10 seconds: Check network/API rate limits
# Check Gemini API dashboard for quota issues
```

---

## Summary Table

| Feature | Without API Key | With API Key |
|---------|-----------------|--------------|
| **Quiz Questions** | Pre-built templates (same for all) | Personalized via Gemini (unique) |
| **Difficulty Adjustment** | Basic rules (fixed logic) | AI-powered (analyzes history) |
| **Topic Suggestions** | Default by age group | Gemini-generated (personalized) |
| **Generation Speed** | Instant | 2-5 seconds (API call) |
| **Student Experience** | Generic | Highly personalized |
| **Learning Effectiveness** | Good | Excellent |

---

## Next Steps

1. **Get your Gemini API key** from [aistudio.google.com](https://aistudio.google.com/app/apikey)
2. **Set the environment variable:** `export GEMINI_API_KEY="your-key"`
3. **Restart the backend**
4. **Take a quiz** and see personalized questions!

---

*For more details on the fixes, see `FIXES_SUMMARY.md`*
