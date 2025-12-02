"""
PDF-Based Question Generator
Generates quiz questions based on content from educational PDFs
Uses both PDF content and Gemini API for question generation
"""

import logging
import os
from typing import List, Dict, Any, Optional
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

from .pdf_content_extractor import PDFContentExtractor

logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY and GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)


class PDFBasedQuestionGenerator:
    """Generates questions based on PDF content"""
    
    def __init__(self):
        """Initialize question generator"""
        self.pdf_extractor = PDFContentExtractor()
        self.model = None
        
        if GEMINI_API_KEY and GEMINI_AVAILABLE:
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            logger.info("✅ PDF-Based Question Generator initialized with Gemini")
        else:
            logger.warning("⚠️  Gemini not available, will use PDF content only")
    
    def generate_questions_for_topic(
        self,
        age: int,
        topic: str,
        num_questions: int = 5,
        user_hobbies: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions for a topic based on PDF content
        
        Args:
            age: User's age (determines which PDF to use)
            topic: Topic to generate questions about
            num_questions: Number of questions to generate
            user_hobbies: User's hobbies for personalization
        
        Returns:
            List of question dictionaries with options and explanations
        """
        try:
            # Step 1: Get PDF content for the topic
            pdf_content = self.pdf_extractor.get_content_for_topic(age, topic)
            
            if not pdf_content:
                logger.warning(f"No PDF content found for topic: {topic}")
                pdf_content = self.pdf_extractor.get_full_class_content(age)
                if not pdf_content:
                    logger.error(f"No PDF content available for age {age}")
                    return []
            
            logger.info(f"Retrieved {len(pdf_content)} chars of PDF content for topic: {topic}")
            
            # Step 2: Generate questions using Gemini + PDF content
            if self.model:
                questions = self._generate_with_gemini(
                    topic=topic,
                    pdf_content=pdf_content,
                    num_questions=num_questions,
                    age=age,
                    hobbies=user_hobbies
                )
            else:
                logger.warning("Gemini not available, cannot generate questions")
                questions = []
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions for topic {topic}: {e}")
            return []
    
    def _generate_with_gemini(
        self,
        topic: str,
        pdf_content: str,
        num_questions: int,
        age: int,
        hobbies: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Use Gemini to generate questions based on PDF content and topic keywords
        
        Args:
            topic: Topic to generate questions about
            pdf_content: Extracted content from PDF
            num_questions: Number of questions to generate
            age: User's age
            hobbies: User's hobbies
        
        Returns:
            List of generated questions
        """
        try:
            # Truncate PDF content to fit in token limit (keeping it focused on topic)
            pdf_content = pdf_content[:3500]
            
            # Extract keywords from topic for emphasis
            topic_keywords = [word.lower() for word in topic.split() if len(word) > 3]
            keywords_str = ", ".join(topic_keywords)
            
            # Age-appropriate vocabulary and difficulty
            age_context = self._get_age_context(age)
            
            hobbies_context = ""
            if hobbies:
                hobbies_context = f"\nStudent's hobbies/interests: {hobbies}\nWhere possible, relate examples to their interests."
            
            prompt = f"""You are an expert financial education teacher creating questions for students. 
Your task is to generate {num_questions} multiple-choice questions about the topic: "{topic}"

TOPIC KEYWORDS TO FOCUS ON: {keywords_str}

CURRICULUM CONTENT (from the student's class textbook):
{pdf_content}

STUDENT PROFILE:
- Age: {age} years old
- {age_context}{hobbies_context}

REQUIREMENTS:
1. Generate questions BASED DIRECTLY on the curriculum content provided
2. Focus on the topic keywords: {keywords_str}
3. Questions should be appropriate for age {age} - use {self._get_vocabulary_level(age)} vocabulary
4. Each question must test understanding of the topic, not just memorization
5. Provide 4 options for each question
6. Correct answer position must vary (not always position 0)
7. Include accurate, educational explanations for each answer
8. Questions should help reinforce learning from the PDF content

IMPORTANT CONSTRAINTS:
- Return ONLY valid JSON - no markdown, no code blocks, no explanation text before or after JSON
- Do NOT include questions not covered in the curriculum content
- Do NOT make up information not in the PDF
- All options must be plausible but only one correct

JSON FORMAT (return EXACTLY this structure):
{{
    "questions": [
        {{
            "question_id": "q_1",
            "question": "Clear, focused question about the topic?",
            "type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 1,
            "explanation": "Clear explanation of why this is correct, referencing the curriculum"
        }},
        {{
            "question_id": "q_2",
            "question": "Another question?",
            "type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 2,
            "explanation": "Explanation referencing the curriculum content"
        }}
    ]
}}

Now generate the {num_questions} questions:"""
            
            logger.info(f"Sending Gemini request for topic: {topic}, age: {age}")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.rstrip("```").strip()
            
            logger.info(f"Gemini response received, parsing JSON...")
            
            # Parse JSON response
            questions_data = json.loads(response_text)
            questions = questions_data.get("questions", [])
            
            logger.info(f"Parsed {len(questions)} questions from Gemini response")
            
            # Validate and clean questions
            validated = []
            for i, q in enumerate(questions):
                try:
                    if (q.get("question") and 
                        q.get("options") and 
                        len(q.get("options", [])) == 4 and
                        "correct_answer" in q and
                        q.get("explanation")):
                        
                        # Ensure correct_answer is valid
                        if q["correct_answer"] < 0 or q["correct_answer"] >= 4:
                            q["correct_answer"] = min(q["correct_answer"], 3)
                        
                        # Ensure question_id exists
                        if not q.get("question_id"):
                            q["question_id"] = f"q_{i+1}"
                        
                        validated.append(q)
                except Exception as e:
                    logger.warning(f"Skipping malformed question: {e}")
                    continue
            
            logger.info(f"✅ Generated and validated {len(validated)} questions for topic: {topic}")
            return validated
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}, response: {response_text[:200]}")
            return []
        except Exception as e:
            logger.error(f"Error generating questions with Gemini: {e}", exc_info=True)
            return []
    
    def _get_age_context(self, age: int) -> str:
        """Get age-appropriate context for the prompt"""
        if age < 12:
            return "Learning level: Beginner - basic concepts and definitions"
        elif age < 14:
            return "Learning level: Intermediate - understanding relationships and applications"
        else:
            return "Learning level: Advanced - critical thinking and analysis"
    
    def _get_vocabulary_level(self, age: int) -> str:
        """Get appropriate vocabulary level for age"""
        if age < 12:
            return "simple, everyday"
        elif age < 14:
            return "intermediate, moderately technical"
        else:
            return "advanced, technical and formal"
    
    def get_class_and_topics_for_age(self, age: int) -> Dict[str, Any]:
        """
        Get class information and topics for a given age
        
        Args:
            age: User's age
        
        Returns:
            Dictionary with class info and available topics
        """
        try:
            class_info = self.pdf_extractor.get_class_info(age)
            topics = self.pdf_extractor.get_topics_for_age(age)
            
            return {
                "class": class_info.get("class"),
                "age_range": class_info.get("age_range"),
                "pdf_exists": class_info.get("pdf_exists"),
                "topics": topics,
                "total_topics": len(topics)
            }
        except Exception as e:
            logger.error(f"Error getting class info: {e}")
            return {
                "class": None,
                "age_range": None,
                "pdf_exists": False,
                "topics": [],
                "total_topics": 0
            }
