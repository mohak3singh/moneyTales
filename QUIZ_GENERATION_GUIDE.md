# Topic-Based Quiz Generation - Implementation Summary

## Overview
The quiz generation system has been enhanced to create questions specific to the selected topic using PDF content and Gemini API.

## Flow Diagram
```
User Selects Topic from Dropdown
         ↓
Topic from PDF (e.g., "Introduction to Banking")
         ↓
Extract Topic-Specific PDF Content
(get_content_for_topic searches PDF for topic keywords)
         ↓
Pass to Gemini with:
- Topic keywords for focus
- Topic-specific PDF content (up to 3500 chars)
- User age (for vocabulary level)
- User hobbies (for personalization)
         ↓
Gemini Generates Questions
- Based ONLY on provided PDF content
- Appropriate for user's age
- Focused on topic keywords
- Varied correct answer positions
- With educational explanations
         ↓
Return to Frontend
Questions ready for user to answer
```

## Key Components

### 1. Topic Selection (Frontend)
- User sees topics extracted from PDF
- Topics are age-appropriate (based on class PDF)
- Example: Age 12 → Class 7th → Topics like "Introduction to Banking", "Income Tax", etc.

### 2. PDF Content Extraction
**File**: `backend/services/pdf_content_extractor.py`
**Method**: `get_content_for_topic(age, topic)`

Features:
- Extracts keywords from topic name
- Searches PDF line-by-line for keyword matches
- Collects surrounding context (2 previous lines + 10 following lines)
- Two-level matching (direct match + partial match)
- Returns up to 4000 characters of relevant content

Example:
```
Topic: "Introduction to Banking"
Keywords: ["introduction", "banking"]
Extracted Content: All sections mentioning banking with context
```

### 3. Question Generation with Gemini
**File**: `backend/services/pdf_question_generator.py`
**Method**: `_generate_with_gemini()`

Enhanced Prompt Features:
- **Topic Keywords**: Emphasizes keywords from selected topic
- **Age Context**: Provides learning level (Beginner/Intermediate/Advanced)
- **Vocabulary Level**: Simple/Intermediate/Advanced based on age
- **PDF-Based**: Explicitly requires questions from provided content
- **Personalization**: Incorporates user hobbies
- **Validation**: Ensures correct answer positions vary

Gemini Parameters:
```
- Model: gemini-2.5-flash
- Input: PDF content + topic + age + hobbies
- Output: 5 multiple-choice questions with explanations
- Token limit: ~3500 chars for PDF content
```

## Age-Appropriate Configuration

| Age Range | Learning Level | Vocabulary | Example Topics |
|-----------|----------------|-----------|-----------------|
| <12       | Beginner       | Simple    | Saving Money, Banking Basics |
| 12-14     | Intermediate   | Moderate  | Income Tax, Interest Rates |
| 14+       | Advanced       | Technical | Investment, Insurance Policies |

## Setup Requirements

### To Use with Gemini API:
```bash
export GEMINI_API_KEY='your-api-key-here'
```

Without this key, the system will:
- ✅ Extract PDF topics correctly
- ✅ Extract topic-specific content from PDF
- ❌ Cannot generate questions (falls back with empty list)

## Question Quality Assurance

Each generated question is validated for:
1. ✅ Question text exists and is meaningful
2. ✅ Exactly 4 options provided
3. ✅ Correct answer position is valid (0-3)
4. ✅ Explanation is provided
5. ✅ Content matches provided PDF material

## Testing

Run the test script to verify the flow:
```bash
python3 /tmp/test_topic_based_quiz.py
```

Expected output:
- ✅ PDF content extracted for topic
- ⚠️ Gemini availability message (depends on API key)
- Questions generated if Gemini is available

## Example Workflow

**User Action**: Selects "Introduction to Banking" (Age 12)

**System Processing**:
1. Gets Class_7th PDF (age 12 → class 7)
2. Searches for "introduction" + "banking"
3. Extracts 4000 chars of relevant content
4. Sends to Gemini with prompt:
   - Topic: "Introduction to Banking"
   - Keywords: "introduction, banking"
   - Age Level: Intermediate
   - PDF Content: Banking-related sections
5. Gemini generates 5 questions about banking

**Result**: User gets 5 questions specifically about banking concepts from their class curriculum

## Files Modified

1. **backend/services/pdf_content_extractor.py**
   - Improved `get_content_for_topic()` method
   - Better keyword matching
   - Context-aware extraction

2. **backend/services/pdf_question_generator.py**
   - Enhanced `_generate_with_gemini()` method
   - Topic keyword extraction
   - Age-appropriate prompting
   - Better JSON parsing and validation
   - Added helper methods for age context

## Next Steps (Optional Enhancements)

1. Cache frequently accessed PDF content for faster generation
2. Add question difficulty validation
3. Implement fallback question generation using RAG if Gemini fails
4. Track question quality metrics
5. Allow teachers to review/approve generated questions

## Troubleshooting

**Issue**: Questions not related to topic
- **Solution**: Check that `get_content_for_topic()` is finding relevant content

**Issue**: Gemini timeout
- **Solution**: Reduce PDF content size or use smaller num_questions

**Issue**: JSON parsing errors
- **Solution**: Check Gemini response format; may need to adjust prompt

**Issue**: Age-inappropriate questions
- **Solution**: Verify age is correct; check age context settings

