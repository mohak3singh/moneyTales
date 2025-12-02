"""
Topic Suggester Service using GPT-4o API
Suggests financial topics based on user age and PDF content from educational materials
"""

import logging
import os
import json
from typing import List, Dict, Any

try:
    from openai import AzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False

from .pdf_content_extractor import PDFContentExtractor

logger = logging.getLogger(__name__)

# Configure Azure OpenAI (GPT-4o) as PRIMARY LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")


class TopicSuggester:
    """Suggests topics based on PDF content and user age using GPT-4o"""
    
    def __init__(self):
        """Initialize GPT-4o client and PDF extractor"""
        self.model = None
        if OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_AVAILABLE:
            try:
                self.model = AzureOpenAI(
                    api_key=OPENAI_API_KEY,
                    api_version="2024-02-15-preview",
                    azure_endpoint=AZURE_OPENAI_ENDPOINT
                )
                logger.info("✅ Azure OpenAI (GPT-4o) initialized for topic suggestion")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure OpenAI: {e}")
                self.model = None
        else:
            missing_vars = []
            if not OPENAI_API_KEY:
                missing_vars.append("OPENAI_API_KEY")
            if not AZURE_OPENAI_ENDPOINT:
                missing_vars.append("AZURE_OPENAI_ENDPOINT")
            if not AZURE_OPENAI_AVAILABLE:
                missing_vars.append("openai library")
            
            vars_str = ", ".join(missing_vars) if missing_vars else "unknown"
            logger.warning(f"⚠️  Azure OpenAI (GPT-4o) not available. Missing: {vars_str}")
            logger.warning(f"📖 See AZURE_OPENAI_SETUP.md for configuration instructions")
            logger.info("ℹ️  Will use PDF-based topic extraction")
        
        # Initialize PDF content extractor
        self.pdf_extractor = PDFContentExtractor()
        logger.info("✅ PDF Content Extractor initialized")
    
    def get_topics_for_age(self, age: int, previous_topics: List[str] = None) -> List[str]:
        """
        Get recommended financial topics based on user age using ONLY PDF content extraction
        No LLM or hardcoded topics - pure PDF extraction only
        
        Flow:
        1. Extract topics directly from the class PDF that matches user's age
        2. Filter and clean the raw PDF topics
        3. Exclude previously covered topics
        
        Args:
            age: User's age
            previous_topics: Topics already covered by the user
        
        Returns:
            List of recommended topics from PDF only
        """
        try:
            # Step 1: Get topics from PDF for user's age/class
            pdf_topics = self.pdf_extractor.get_topics_for_age(age)
            
            logger.info(f"[TopicSuggester] Extracted {len(pdf_topics)} raw topics from PDF for age {age}: {pdf_topics[:3] if pdf_topics else 'NONE'}")
            
            # Step 2: Filter and clean the raw PDF topics (remove metadata)
            cleaned_topics = self._filter_raw_topics(pdf_topics, age)
            logger.info(f"[TopicSuggester] After filtering: {len(cleaned_topics)} topics: {cleaned_topics[:3] if cleaned_topics else 'NONE'}")
            
            if not cleaned_topics:
                logger.warning(f"[TopicSuggester] No usable topics extracted from PDF for age {age}")
                return []
            
            # Step 3: Filter out previously covered topics
            if previous_topics:
                filtered = [t for t in cleaned_topics if t.lower() not in [pt.lower() for pt in previous_topics]]
                if filtered:
                    cleaned_topics = filtered
                logger.info(f"[TopicSuggester] Filtered to {len(cleaned_topics)} topics after removing previous ones")
            
            final_topics = cleaned_topics[:5]  # Return top 5 topics from PDF only
            logger.info(f"[TopicSuggester] Final topics for age {age}: {final_topics}")
            return final_topics
            
        except Exception as e:
            logger.error(f"[TopicSuggester] Error getting topics for age {age}: {e}", exc_info=True)
            return []
    
    def _filter_raw_topics(self, raw_topics: List[str], age: int) -> List[str]:
        """
        Filter and clean raw PDF topics
        Removes metadata and keeps only relevant educational topics
        
        Args:
            raw_topics: Raw topics from PDF extraction
            age: User's age for context
        
        Returns:
            Filtered topics from PDF
        """
        filtered = []
        skip_phrases = ['workbook', 'class', 'edition', 'isbn', 'published', 'printed', 
                       'author', 'cbse', 'index', 'page', 'shiksha kendra', 'ncfe',
                       'advisory', 'monitoring', 'editing', 'board', 'geography', 'history',
                       'financial education', 'national centre', 'exchange board',
                       'regulatory', 'development authority', 'insurance regulatory']
        
        for topic in raw_topics:
            # Skip if too short or contains metadata
            if len(topic) < 5 or len(topic) > 100:
                continue
            if any(skip in topic.lower() for skip in skip_phrases):
                continue
            # Skip if mostly digits or has weird formatting
            if sum(1 for c in topic if c.isdigit()) > len(topic) / 3:
                continue
            # Skip if has page number patterns
            if any(c in topic for c in ['Page', 'page', 'No.', 'no.']):
                continue
            
            cleaned = topic.strip()
            if cleaned and len(cleaned) > 5:
                filtered.append(cleaned)
        
        return filtered[:10]
    
    
    def get_difficulty_recommendation(self, score: int, max_score: int) -> str:
        """
        Recommend difficulty level based on quiz performance
        
        Args:
            score: User's score on the quiz
            max_score: Maximum possible score
        
        Returns:
            Difficulty level: 'easy', 'medium', or 'hard'
        """
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        if percentage == 100:
            return "hard"
        elif percentage >= 70:
            return "medium"
        else:
            return "easy"
    
    def get_feedback_message(self, score: int, max_score: int) -> str:
        """
        Get personalized feedback message based on performance
        
        Args:
            score: User's score
            max_score: Maximum possible score
        
        Returns:
            Feedback message
        """
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        if percentage == 0:
            return "🤔 You scored 0%. Don't worry! I'll give you easier level quizzes next time so you can build your foundation."
        elif percentage < 50:
            return f"📚 You scored {percentage:.0f}%. Keep practicing! I'll give you easier level quizzes to help you improve."
        elif percentage < 70:
            return f"👍 Good effort! You scored {percentage:.0f}%. Ready for medium level questions next time?"
        elif percentage < 100:
            return f"🌟 Great job! You scored {percentage:.0f}%. Let's challenge you with harder questions next time!"
        else:
            return f"🏆 Perfect score! You scored {percentage:.0f}%! You're a financial wizard! Bringing you the hardest questions next!"
    
    def analyze_performance_with_gpt4o(self, quiz_history: List[Dict[str, Any]], current_percentage: float, max_score: int, next_difficulty: str = "medium") -> Dict[str, Any]:
        """
        Analyze user performance using GPT-4o to provide detailed insights
        
        Args:
            quiz_history: List of previous quiz attempts with topic and percentage
            current_percentage: Current quiz percentage score (0-100)
            max_score: Max possible score for validation
            next_difficulty: Recommended difficulty level
        
        Returns:
            Dict with feedback, difficulty recommendation, and insights
        """
        try:
            if not self.model:
                return {
                    "success": False,
                    "next_difficulty": next_difficulty,
                    "feedback": self.get_feedback_message(int(current_percentage), max_score),
                    "insight": "Keep practicing to improve!"
                }
            
            # Build history context
            history_context = ""
            if quiz_history:
                avg_score = sum(q.get('percentage', 0) for q in quiz_history[-10:]) / min(10, len(quiz_history))
                topics = list(set([q.get('topic', '') for q in quiz_history if q.get('topic')]))
                topic_str = ", ".join(topics[-3:]) if topics else "various topics"
                history_context = f"\nRecent topics: {topic_str}\nPrevious average: {avg_score:.0f}%"
            
            prompt = f"""You are an encouraging educational coach analyzing a student's quiz performance.

Current Performance:
- Score: {current_percentage:.0f}%
- Performance History:{history_context}

Recommended Difficulty: {next_difficulty.upper()}

Provide ONLY a JSON response (no markdown, just valid JSON):
{{
    "success": true,
    "next_difficulty": "{next_difficulty}",
    "feedback": "One encouraging line acknowledging their performance",
    "insight": "One practical suggestion for improvement"
}}

Be specific, encouraging, and constructive. Keep it short and motivating."""
            
            response = self.model.chat.completions.create(
                model=AZURE_DEPLOYMENT_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
            result = json.loads(response_text)
            
            return {
                "success": True,
                "next_difficulty": result.get("next_difficulty", next_difficulty),
                "feedback": result.get("feedback", self.get_feedback_message(int(current_percentage), max_score)),
                "insight": result.get("insight", "Keep practicing to improve!"),
                "percentage": current_percentage
            }
        except Exception as e:
            logger.error(f"Error analyzing performance with GPT-4o: {e}")
            return {
                "success": False,
                "next_difficulty": next_difficulty,
                "feedback": self.get_feedback_message(int(current_percentage), max_score),
                "insight": "Keep practicing to improve!",
                "percentage": current_percentage
            }
    
    def _get_default_analysis(self, current_score: int, max_score: int) -> Dict[str, Any]:
        """Fallback analysis when GPT-4o is not available"""
        percentage = (current_score / max_score * 100) if max_score > 0 else 0
        return {
            "next_difficulty": self.get_difficulty_recommendation(current_score, max_score),
            "feedback": self.get_feedback_message(current_score, max_score),
            "insight": "Keep practicing to improve!",
            "percentage": percentage
        }
