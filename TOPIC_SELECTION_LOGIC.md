# Current Topic Selection Logic - How Topics Are Generated

## Overview
Topics are currently being generated **ONLY based on user's AGE**, not hobbies. Here's the complete flow:

---

## Current Flow

### 1. **Topic Generation (Age-Based Only)**

**File**: `backend/services/topic_suggester.py` (Lines 31-67)

```
User Age → Topic Suggester → Gemini API → Age-Appropriate Topics
```

**Logic:**
```python
def get_topics_for_age(self, age: int, previous_topics: List[str] = None) -> List[str]:
    """
    Generates 5 topics based on age using Gemini 2.5 Flash
    
    Age Groups:
    - age < 12:   Basic money concepts (young child)
    - 12-15:      Money management & budgeting (teen)
    - 16-18:      Investing & earning (advanced teen)
    - 18+:        Advanced financial planning (adult)
    
    Parameters:
    - age: The user's age (ONLY this is used)
    - previous_topics: List of topics already covered (for variety, NOT for personalization)
    """
```

**Gemini Prompt** (Lines 50-63):
```
"Based on the user's age of {age} years, suggest 5 appropriate financial literacy topics"

Guidelines consider:
- Age-appropriate content
- Practical financial skills
- Progressive complexity
- Topics they haven't covered yet
```

### 2. **Fallback Default Topics** (Lines 74-91)

If Gemini fails, uses hardcoded defaults:

```python
Age < 13:       ["Saving Money", "Pocket Money Management", "Basic Money Concepts", "Earning Money", "Banking Basics"]
Age 13-17:      ["Budgeting Basics", "Saving Money", "Earning & Part-time Jobs", "Credit & Debit", "Financial Goals"]
Age 18+:        ["Investing Basics", "Stock Market", "Budgeting & Planning", "Taxes & Income", "Financial Goals"]
```

### 3. **Frontend Topic Selection** (Lines 635-652)

**File**: `frontend/streamlit_app.py`

```python
# Load topics based on age
response = requests.post(
    f"{API_BASE_URL}/topics/suggestions",
    json={
        "user_id": user_id,
        "age": user_age  # ← ONLY AGE is sent
        # ❌ Hobbies are NOT included here
    }
)

# Topics loaded from backend
available_topics = response.json().get("topics", [])

# User selects a topic from the dropdown
topic = st.selectbox("📚 Choose a Topic:", available_topics)

# Generate quiz with selected topic
requests.post(
    f"{API_BASE_URL}/quiz/generate",
    json={
        "user_id": user_id,
        "topic": topic  # ← Topics sent to quiz generation
    }
)
```

### 4. **Quiz Generation** (Uses the Topic)

**File**: `backend/orchestrator.py` (Line 37)

```python
def generate_quiz(self, user_id: str, topic: str = None, **kwargs):
    """
    Receives topic selected by user (which is age-based)
    Passes topic to all agents for question generation
    """
    # Topic is used by:
    # - RAGAgent: Searches knowledge base for context
    # - StoryAgent: Creates story relevant to topic
    # - QuizAgent: Generates questions about the topic
```

---

## Where Hobbies Are Currently Used

**File**: `backend/agents/quiz_agent.py` (Lines 115-120)

Hobbies are used **ONLY for question personalization**, not topic selection:

```python
user_hobbies = user_profile.get("hobbies", "learning")

# Gemini prompt includes:
prompt = f"""
STUDENT PROFILE:
- Name: {user_name}
- Age: {user_age} years old
- Hobbies/Interests: {hobbies}  ← Used to make questions relatable
"""

# Example: If student loves gaming
# Question might be: "Your favorite game costs $50. You have $30..."
# Instead of: "Sarah buys a book for $50..."
```

---

## Current Limitations

| Aspect | Current | Expected |
|--------|---------|----------|
| **Topic Selection** | Age-based only ❌ | Should include hobbies ❌ |
| **Example** | 12yo gets: "Budgeting, Saving" | 12yo who loves gaming should get: "Gaming Economy, Digital Purchases, In-Game Currency" |
| **Hobbies Used** | Only for question wording | Should influence topic selection too |
| **Personalization** | Shallow (just question wording) | Deep (topics + questions + difficulty) |

---

## Code Path Summary

```
User Registration (Stores: age + hobbies)
    ↓
User Login
    ↓
Explore Page
    ↓
Topic API Call:
  - Input: user_id + AGE ONLY ❌
  - Process: Gemini generates topics based on age
  - Output: 5 age-appropriate topics
    ↓
User Selects Topic (from age-based list)
    ↓
Quiz Generation:
  - Topic is passed to orchestrator
  - Hobbies are used ONLY for question wording
  - Quiz questions are personalized in language, not in content
    ↓
Quiz Display (Different question wording based on hobbies)
```

---

## What's Stored in Database

**User Profile** (`users` table):
```sql
user_id (string)
name (string)
age (int)           ← Used for topic selection
hobbies (string)    ← Currently unused for topics
level (int)
points (int)
```

---

## Recommendation for Enhancement

To make topics hobby-based, you would need to:

1. **Modify `/topics/suggestions` endpoint**
   ```python
   # Pass hobbies to topic_suggester
   topics = topic_suggester.get_topics_for_age_and_hobbies(age, hobbies)
   ```

2. **Update TopicSuggester.get_topics_for_age()**
   ```python
   def get_topics_for_age_and_hobbies(self, age: int, hobbies: str):
       # Create Gemini prompt that includes both age AND hobbies
       prompt = f"""
       User Profile:
       - Age: {age}
       - Hobbies: {hobbies}
       
       Suggest financial topics that:
       1. Are age-appropriate
       2. Relate to their hobbies
       """
   ```

3. **Examples of hobby-based topics**:
   - **Gaming**: "Gaming Economy", "Digital Currency", "In-Game Purchases"
   - **Sports**: "Sports Equipment Budget", "Sponsorship Money", "Athlete Earnings"
   - **Music**: "Music Equipment Investment", "Concert Budgeting", "Artist Revenue"
   - **Art**: "Art Supplies Budgeting", "Selling Your Art", "Creative Income"

---

## Current Topic Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ USER REGISTRATION                                           │
│ Input: name, age, hobbies                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ TOPIC SUGGESTION API (/api/topics/suggestions)              │
│ Receives: user_id, AGE ONLY                                 │
│ Hobbies NOT sent ❌                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ GEMINI API                                                   │
│ Prompt: "Based on age {age}, suggest 5 topics"              │
│ Hobbies NOT included ❌                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ AGE-BASED TOPICS RETURNED                                   │
│ Example: ["Budgeting", "Saving", "Credit", ...]             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ USER SELECTS TOPIC FROM LIST                                │
│ No hobby consideration                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ QUIZ GENERATION (/api/quiz/generate)                        │
│ Receives: user_id, topic                                    │
│ Fetches user profile (including hobbies)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ QUESTION GENERATION (QuizAgent)                             │
│ Gemini prompt includes hobbies:                             │
│ "Personalize questions using their hobbies"                 │
│ Example: Same topic, but gaming-themed questions            │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

✅ **What Works**:
- Topics are age-appropriate
- Questions are personalized by hobbies (in wording)
- Difficulty adjusts based on performance

❌ **What's Missing**:
- Hobbies don't influence **which topics** are suggested
- User always gets generic age-based topics
- No hobby-relevant topic suggestions
- 12-year-old gamer gets same topics as 12-year-old bookworm

**Impact**: System is partially personalized, but could be much better by including hobbies in topic selection.
