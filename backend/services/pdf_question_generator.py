"""
PDF-Based Question Generator
Generates quiz questions based on content from educational PDFs
Uses GPT-4o for question generation
Ensures questions are directly related to PDF content and topics
"""

import logging
import os
from typing import List, Dict, Any, Optional
import json
import time

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

logger.info(f"DEBUG: OPENAI_API_KEY={'SET' if OPENAI_API_KEY else 'NOT SET'}")
logger.info(f"DEBUG: AZURE_OPENAI_ENDPOINT={'SET' if AZURE_OPENAI_ENDPOINT else 'NOT SET'}")
logger.info(f"DEBUG: AZURE_DEPLOYMENT_NAME={AZURE_DEPLOYMENT_NAME}")
logger.info(f"DEBUG: AZURE_OPENAI_AVAILABLE={AZURE_OPENAI_AVAILABLE}")

azure_openai_client = None
if OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_AVAILABLE:
    try:
        azure_openai_client = AzureOpenAI(
            api_key=OPENAI_API_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        logger.info("✅ Azure OpenAI (GPT-4o) configured as PRIMARY LLM")
    except Exception as e:
        logger.warning(f"Failed to configure Azure OpenAI: {e}")
        azure_openai_client = None
else:
    missing_vars = []
    if not OPENAI_API_KEY:
        missing_vars.append("OPENAI_API_KEY")
    if not AZURE_OPENAI_ENDPOINT:
        missing_vars.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_AVAILABLE:
        missing_vars.append("openai library")
    
    vars_str = ", ".join(missing_vars)
    logger.warning(f"⚠️  Azure OpenAI (GPT-4o) not available. Missing: {vars_str}")
    logger.warning(f"📖 See AZURE_OPENAI_SETUP.md for configuration instructions")
    logger.info("ℹ️  Will use fallback PDF-based question extraction")


class PDFBasedQuestionGenerator:
    """Generates questions based on PDF content"""
    
    def __init__(self):
        """Initialize question generator"""
        self.pdf_extractor = PDFContentExtractor()
        self.azure_openai_client = azure_openai_client
        
        if self.azure_openai_client:
            logger.info("✅ PDF-Based Question Generator initialized with Azure OpenAI GPT-4o")
        else:
            logger.warning("⚠️  Azure OpenAI not available. Will use PDF fallback method")
    
    def generate_questions_for_topic(
        self,
        age: int,
        topic: str,
        num_questions: int = 5,
        user_hobbies: str = "",
        difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions for a topic based on PDF content
        Questions are DIRECTLY from PDF content, enhanced with GPT-4o
        
        Args:
            age: User's age (determines which PDF to use)
            topic: Topic to generate questions about
            num_questions: Number of questions to generate
            user_hobbies: User's hobbies for personalization
            difficulty: Question difficulty level (easy, medium, hard)
        
        Returns:
            List of question dictionaries with options and explanations
        """
        try:
            logger.info(f"🎯 Generating {num_questions} questions for topic: {topic} (age {age}, difficulty: {difficulty})")
            
            # Step 1: Get PDF content for the topic
            logger.info(f"📚 Retrieving PDF content for topic: {topic}")
            pdf_content = self.pdf_extractor.get_content_for_topic(age, topic)
            
            if not pdf_content or len(pdf_content.strip()) < 100:
                logger.warning(f"⚠️  Limited PDF content found for topic: {topic}, fetching full class content")
                pdf_content = self.pdf_extractor.get_full_class_content(age)
                if not pdf_content or len(pdf_content.strip()) < 100:
                    logger.error(f"❌ No sufficient PDF content available for age {age}")
                    return []
            
            logger.info(f"✅ Retrieved {len(pdf_content)} characters of PDF content")
            
            # Step 2: Generate questions using GPT-4o API with PDF content
            if self.azure_openai_client:
                logger.info(f"🤖 Using Azure OpenAI GPT-4o to generate questions from PDF content")
                questions = self._generate_with_gpt4o(
                    topic=topic,
                    pdf_content=pdf_content,
                    num_questions=num_questions,
                    age=age,
                    hobbies=user_hobbies,
                    difficulty=difficulty
                )
                
                if questions and len(questions) > 0:
                    logger.info(f"✅ Generated {len(questions)} questions successfully with GPT-4o")
                    return questions
                else:
                    logger.warning(f"⚠️  GPT-4o returned no questions, using fallback PDF-based method")
                    logger.info(f"💡 For more details, see FALLBACK_WARNING_GUIDE.md")
            else:
                logger.warning(f"⚠️  Azure OpenAI (GPT-4o) not configured - using fallback PDF extraction")
                logger.info(f"📖 To enable GPT-4o:")
                logger.info(f"   1. See AZURE_OPENAI_SETUP.md for configuration")
                logger.info(f"   2. Run: python3 validate_azure_config.py")
                logger.info(f"   3. Restart the application")
            
            # Step 3: Fallback: Extract basic questions from PDF content
            logger.info(f"📖 Using PDF content directly to extract questions (fallback mode)")
            questions = self._extract_from_pdf_content(
                topic=topic,
                pdf_content=pdf_content,
                num_questions=num_questions,
                age=age,
                difficulty=difficulty
            )
            
            if questions:
                logger.info(f"✅ Extracted {len(questions)} questions from PDF content")
            
            return questions
            
        except Exception as e:
            logger.error(f"❌ Error generating questions for topic {topic}: {e}", exc_info=True)
            return []
    
    def _generate_with_gpt4o(
        self,
        topic: str,
        pdf_content: str,
        num_questions: int,
        age: int,
        hobbies: str = "",
        difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Use Azure OpenAI GPT-4o to generate questions BASED DIRECTLY on PDF content
        Fallback method when Gemini API is not available
        All questions must be answerable from the provided PDF content
        
        Args:
            topic: Topic to generate questions about
            pdf_content: Extracted content from PDF (source of truth)
            num_questions: Number of questions to generate
            age: User's age
            hobbies: User's hobbies
            difficulty: Question difficulty level (easy, medium, hard)
        
        Returns:
            List of generated questions with PDF content validation
        """
        try:
            # Ensure PDF content is substantial
            if not pdf_content or len(pdf_content.strip()) < 100:
                logger.warning("PDF content too short for reliable question generation")
                return []
            
            # Truncate to fit token limits but keep it comprehensive
            max_content_length = 3000
            pdf_content = pdf_content[:max_content_length]
            
            # Get age-appropriate context
            age_context = self._get_age_context(age)
            vocab_level = self._get_vocabulary_level(age)
            
            # Get difficulty-specific instructions
            difficulty_instructions = self._get_difficulty_instructions(difficulty)
            
            hobbies_context = ""
            if hobbies:
                hobbies_context = f"\nStudent's interests: {hobbies}\nWhere relevant, relate examples to their interests."
            
            prompt = f"""You are an expert financial education teacher creating quiz questions.

CRITICAL REQUIREMENTS:
1. ALL questions MUST be answerable ONLY from the provided curriculum content below
2. Do NOT create questions about information not in the curriculum
3. Do NOT use external knowledge or make up facts
4. Every question must directly test understanding of the curriculum material
5. IMPORTANT: Every answer option MUST be COMPLETE and FULL sentences, NOT truncated
6. Every answer option must be plausible but only ONE correct
7. Vary the position of correct answers (use positions 0, 1, 2, and 3)
8. Do NOT repeat or duplicate options across different questions
9. Make options distinct and clearly different from each other

DIFFICULTY LEVEL: {difficulty.upper()}
{difficulty_instructions}

STUDENT PROFILE:
- Age: {age} years old
- Learning level: {age_context}
- Vocabulary: {vocab_level}{hobbies_context}

CURRICULUM CONTENT (This is your ONLY source for questions):
---START CURRICULUM---
{pdf_content}
---END CURRICULUM---

TOPIC TO FOCUS ON: {topic}

Generate {num_questions} multiple-choice questions about "{topic}" using ONLY the curriculum content above.

For each question:
1. Create a clear, unambiguous question based directly on the curriculum
2. Provide 4 COMPLETE and DISTINCT options
3. Mark the correct answer position (0-3)
4. Provide a detailed explanation citing the curriculum
5. Ensure questions vary in difficulty and topic coverage

Return ONLY valid JSON:

{{
    "questions": [
        {{
            "question_id": "q_1",
            "question": "Question text?",
            "type": "multiple_choice",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answer": 0,
            "explanation": "Explanation with curriculum reference"
        }}
    ]
}}

Generate the questions now:"""
            
            logger.info(f"📤 Sending GPT-4o request for {num_questions} questions on '{topic}'")
            
            # Call GPT-4o API with retries
            max_retries = 2
            response = None
            for attempt in range(max_retries):
                try:
                    response = self.azure_openai_client.chat.completions.create(
                        model=AZURE_DEPLOYMENT_NAME,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert financial education teacher. Generate questions ONLY from the provided curriculum content."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=1500,
                        top_p=0.9
                    )
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️  GPT-4o API call failed (attempt {attempt+1}/{max_retries}), retrying...")
                        time.sleep(0.5)
                    else:
                        raise
            
            if not response or not response.choices:
                logger.error("❌ GPT-4o returned empty response")
                return []
            
            response_text = response.choices[0].message.content.strip()
            logger.info(f"📥 Received GPT-4o response ({len(response_text)} chars)")
            
            # Clean up markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.rstrip("```").strip()
            
            # Parse JSON
            logger.info(f"📊 Parsing JSON response...")
            questions_data = json.loads(response_text)
            questions = questions_data.get("questions", [])
            
            logger.info(f"✅ Parsed {len(questions)} questions from GPT-4o")
            
            # Validate and clean questions
            validated = []
            for i, q in enumerate(questions):
                try:
                    # Strict validation
                    if not q.get("question"):
                        logger.warning(f"Skipping Q{i+1}: missing question text")
                        continue
                    
                    if not q.get("options") or len(q.get("options", [])) != 4:
                        logger.warning(f"Skipping Q{i+1}: doesn't have exactly 4 options")
                        continue
                    
                    if "correct_answer" not in q:
                        logger.warning(f"Skipping Q{i+1}: missing correct_answer")
                        continue
                    
                    if not q.get("explanation"):
                        logger.warning(f"Skipping Q{i+1}: missing explanation")
                        continue
                    
                    # Validate correct_answer index
                    correct_idx = q["correct_answer"]
                    if not isinstance(correct_idx, int) or correct_idx < 0 or correct_idx >= 4:
                        logger.warning(f"Skipping Q{i+1}: invalid correct_answer index {correct_idx}")
                        continue
                    
                    # Set question_id
                    if not q.get("question_id"):
                        q["question_id"] = f"q_{i+1}"
                    
                    validated.append(q)
                    logger.info(f"  ✅ Q{i+1}: Valid (correct at position {correct_idx})")
                    
                except Exception as e:
                    logger.warning(f"Skipping Q{i+1}: {e}")
                    continue
            
            if not validated:
                logger.error(f"❌ No valid questions after validation")
                return []
            
            logger.info(f"✅ Validated {len(validated)}/{len(questions)} questions successfully")
            return validated
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            logger.error(f"Response text (first 500 chars): {response_text[:500] if response_text else 'Empty'}")
            return []
        except Exception as e:
            logger.error(f"❌ Error generating questions with GPT-4o: {e}", exc_info=True)
            return []
    
    def _get_age_context(self, age: int) -> str:
        """Get age-appropriate context for the prompt"""
        if age < 12:
            return "Learning level: Beginner - basic concepts, definitions, and simple applications"
        elif age < 14:
            return "Learning level: Intermediate - understanding relationships, comparisons, and real-world applications"
        else:
            return "Learning level: Advanced - critical thinking, analysis, and complex problem-solving"
    
    def _get_vocabulary_level(self, age: int) -> str:
        """Get appropriate vocabulary level for age"""
        if age < 12:
            return "simple, everyday, easy to understand"
        elif age < 14:
            return "intermediate, moderately technical with explanations"
        else:
            return "advanced, technical, formal financial terminology"
    
    def _extract_from_pdf_content(
        self,
        topic: str,
        pdf_content: str,
        num_questions: int,
        age: int,
        difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Fallback: Generate structured questions from PDF content when GPT-4o API fails

        Creates comprehension-based questions directly from topic-specific PDF content
        
        Args:
            topic: Topic name
            pdf_content: PDF text content specific to the topic
            num_questions: Number of questions to generate
            age: User's age
        
        Returns:
            List of questions created from PDF content
        """
        logger.info(f"📖 Creating structured questions from PDF content (GPT-4o fallback)")
        try:
            questions = []
            
            # Split content into meaningful sections (sentences ending with period)
            sentences = [s.strip() for s in pdf_content.split('.') if s.strip() and len(s.strip()) > 30]
            
            if not sentences:
                logger.warning("❌ Could not extract meaningful sentences from PDF content")
                return []
            
            # Create comprehension-based questions from content
            for idx in range(min(num_questions, len(sentences) // 2)):
                try:
                    # Use multiple different sentences for better question construction
                    main_sentence = sentences[idx * 2] if idx * 2 < len(sentences) else sentences[0]
                    context_sentence = sentences[idx * 2 + 1] if idx * 2 + 1 < len(sentences) else sentences[1] if len(sentences) > 1 else main_sentence
                    alt_sentence1 = sentences[(idx + 1) % len(sentences)]
                    alt_sentence2 = sentences[(idx + 2) % len(sentences)]
                    alt_sentence3 = sentences[(idx + 3) % len(sentences)]
                    
                    # Extract key terms from the main sentence
                    main_words = [w for w in main_sentence.split() if len(w) > 4 and w.lower() not in ['which', 'about', 'also', 'some', 'more', 'that', 'this']]
                    
                    if len(main_words) < 2:
                        continue
                    
                    # Create different question types
                    question_type = idx % 3
                    
                    if question_type == 0:
                        # Definition/Understanding question
                        key_term = main_words[0]
                        question_text = f"According to the curriculum, what does '{key_term}' mean in the context of {topic}?"
                        correct_option = f"{key_term} refers to: {main_sentence}"
                        explanation = f"Based on the curriculum content: {main_sentence}"
                        
                    elif question_type == 1:
                        # Comparison/Relationship question  
                        term1 = main_words[0] if main_words else topic
                        term2 = main_words[1] if len(main_words) > 1 else "financial concepts"
                        question_text = f"What is the relationship between {term1} and {term2} according to the curriculum?"
                        correct_option = f"They are related concepts: {main_sentence}"
                        explanation = f"The curriculum explains: {main_sentence}"
                        
                    else:
                        # Application/Example question
                        terms = ' and '.join(main_words[:2]) if len(main_words) > 1 else main_words[0]
                        question_text = f"Which statement best explains how {terms} applies in {topic}?"
                        correct_option = f"{main_sentence}"
                        explanation = f"This is directly stated in the curriculum: {main_sentence}"
                    
                    # Create UNIQUE, diverse distractor options from different parts of the PDF content
                    # Extract different key terms from alternative sentences
                    alt_words1 = [w for w in alt_sentence1.split() if len(w) > 4][:2]
                    alt_words2 = [w for w in alt_sentence2.split() if len(w) > 4][:2]
                    alt_words3 = [w for w in alt_sentence3.split() if len(w) > 4][:2]
                    
                    # Create distinct distractor options based on content
                    distractors = [
                        f"It refers to: {alt_sentence1}",  # Distractor from different content
                        f"It means: {alt_sentence2}",       # Another unique distractor
                        f"It is: {alt_sentence3}"           # Third unique distractor
                    ]
                    
                    # Shuffle to avoid correct answer always at position 0
                    correct_position = idx % 4  # Vary correct answer position
                    
                    options = distractors[:correct_position] + [correct_option] + distractors[correct_position:]
                    options = options[:4]  # Ensure exactly 4 options
                    
                    # Adjust correct_answer index based on where we placed it
                    correct_idx = correct_position
                    
                    question = {
                        "question_id": f"q_{len(questions)+1}",
                        "question": question_text,
                        "type": "multiple_choice",
                        "options": options,
                        "correct_answer": correct_idx,
                        "explanation": explanation
                    }
                    
                    questions.append(question)
                    logger.info(f"  ✅ Created Q{len(questions)}: {question_text[:60]}...")
                    
                except Exception as e:
                    logger.debug(f"Could not create question from sentence {idx}: {e}")
                    continue
            
            if not questions:
                logger.warning("❌ Could not create any questions from PDF content")
                return []
            
            logger.info(f"✅ Created {len(questions)} structured questions from PDF content")
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"❌ Error creating questions from PDF: {e}")
            return []
    
    def _get_difficulty_instructions(self, difficulty: str) -> str:
        """
        Get difficulty-specific instructions for question generation
        
        Args:
            difficulty: The difficulty level (easy, medium, hard)
        
        Returns:
            String with difficulty-specific instructions
        """
        difficulty = difficulty.lower().strip() if difficulty else "medium"
        
        instructions = {
            "easy": """
EASY LEVEL - Foundational Understanding:
- Focus on simple concepts, definitions, and basic applications
- Questions should test recall of key terms and straightforward facts
- Options should be clearly distinct (no subtle differences)
- Avoid complex scenarios or multi-step reasoning
- Include vocabulary reinforcement where appropriate
- Use concrete examples rather than abstract concepts
- Questions should be answerable by anyone who read the curriculum once
""",
            "medium": """
MEDIUM LEVEL - Applied Understanding:
- Test comprehension and application of concepts
- Include questions about relationships between concepts
- Present realistic, practical scenarios based on curriculum
- Require connecting two or more ideas
- Options should be plausible but clearly different
- Include some inference-based questions
- Focus on practical use cases and real-world application
""",
            "hard": """
HARD LEVEL - Advanced Analysis & Synthesis:
- Require critical thinking and analysis
- Test ability to compare, contrast, and synthesize information
- Include complex scenarios requiring multi-step reasoning
- Present situations not directly stated but implied by curriculum
- Options should be sophisticated and require careful consideration
- Ask "why" and "how" questions rather than "what"
- Include questions that test ability to apply concepts to new situations
- Require understanding of underlying principles, not just facts
"""
        }
        
        return instructions.get(difficulty, instructions["medium"])
    
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
