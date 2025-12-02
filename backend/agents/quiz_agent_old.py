"""
Quiz Agent
Generates engaging quiz questions based on topics and difficulty
Uses Gemini 2.5 Flash for personalized, context-aware questions
"""

import logging
import json
import os
from typing import Dict, List, Any
from .base_agent import Agent

logger = logging.getLogger(__name__)

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
except:
    GEMINI_AVAILABLE = False


class QuizAgent(Agent):
    """Generates quiz questions for financial education"""

    def __init__(self):
        super().__init__("QuizAgent")

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate quiz questions with optional Gemini personalization
        
        Args:
            topic: str - financial topic
            difficulty: str - easy, medium, hard
            num_questions: int - number of questions (default 5)
            rag_context: str - context from RAG
            user_profile: dict - for personalization (includes quiz_history)
        
        Returns:
            dict with quiz questions and metadata
        """
        try:
            topic = kwargs.get("topic", "money basics")
            difficulty = kwargs.get("difficulty", "medium")
            num_questions = kwargs.get("num_questions", 5)
            rag_context = kwargs.get("rag_context", "")
            user_profile = kwargs.get("user_profile", {})

            self.log_execution("Quiz Generation", "started", {
                "topic": topic,
                "difficulty": difficulty,
                "num_questions": num_questions,
                "use_gemini": GEMINI_AVAILABLE
            })

            # Try to generate personalized questions with Gemini if available
            if GEMINI_AVAILABLE:
                try:
                    questions = self._generate_questions_with_gemini(
                        topic, difficulty, num_questions, user_profile
                    )
                    logger.info(f"Generated personalized questions using Gemini for topic: {topic}")
                except Exception as e:
                    logger.warning(f"Gemini personalization failed, falling back to templates: {e}")
                    questions = self._generate_questions(
                        topic, difficulty, num_questions, user_profile, rag_context
                    )
            else:
                questions = self._generate_questions(
                    topic, difficulty, num_questions, user_profile, rag_context
                )

            return {
                "status": "success",
                "questions": questions,
                "topic": topic,
                "difficulty": difficulty,
                "total_questions": len(questions),
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"Error in QuizAgent: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }


    def _generate_questions_with_gemini(
        self, topic: str, difficulty: str, num_questions: int, user_profile: dict
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized quiz questions using Gemini 2.5 Flash
        Takes user history into account for better personalization
        
        Args:
            topic: Financial topic
            difficulty: Easy, medium, or hard
            num_questions: Number of questions to generate
            user_profile: User information including quiz_history
        
        Returns:
            List of personalized quiz questions
        """
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Build user context from history
            user_name = user_profile.get("name", "Student")
            user_age = user_profile.get("age", 10)
            quiz_history = user_profile.get("quiz_history", [])
            
            history_context = ""
            if quiz_history:
                recent_topics = [q.get("topic", "") for q in quiz_history[-5:]]
                avg_score = sum(q.get("percentage", 0) for q in quiz_history[-5:]) / min(5, len(quiz_history))
                history_context = f"\nUser's recent quiz topics: {', '.join(recent_topics)}\nRecent average score: {avg_score:.0f}%\n"
            
            prompt = f"""You are an expert financial education quiz creator. Generate {num_questions} engaging, age-appropriate multiple-choice questions for a {user_age}-year-old student about "{topic}".

Difficulty Level: {difficulty.upper()}
- EASY: Simple concepts, basic math, fundamental ideas
- MEDIUM: Real-world scenarios, slightly complex calculations
- HARD: Advanced concepts, compound scenarios, critical thinking

Student Context:{history_context}

Generate ONLY valid JSON (no markdown, no code blocks) with this exact structure:
{{
    "questions": [
        {{
            "question_id": "q_1",
            "question": "Clear, engaging question text",
            "type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Clear, educational explanation of the correct answer"
        }}
    ]
}}

Requirements:
1. All questions must be about "{topic}"
2. Adjust difficulty level appropriately
3. Make questions practical and relatable to a {user_age}-year-old
4. Include diverse scenario types (calculations, concepts, real-world decisions)
5. Correct answers should be at different positions (not always position 0)
6. Explanations should be educational and encouraging
7. Return EXACTLY {num_questions} questions
8. Ensure valid JSON format with proper escaping

Generate questions now:"""
            
            response = model.generate_content(prompt)
            
            # Parse the response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text)
            questions = result.get("questions", [])
            
            # Validate and ensure correct format
            validated_questions = []
            for i, q in enumerate(questions[:num_questions]):
                validated_q = {
                    "question_id": q.get("question_id", f"gemini_q_{i}"),
                    "question": q.get("question", ""),
                    "type": "multiple_choice",
                    "options": q.get("options", []),
                    "correct_answer": int(q.get("correct_answer", 0)),
                    "explanation": q.get("explanation", "")
                }
                if validated_q["question"] and len(validated_q["options"]) >= 4:
                    validated_questions.append(validated_q)
            
            logger.info(f"Generated {len(validated_questions)} personalized questions with Gemini")
            return validated_questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Error generating questions with Gemini: {e}")
            raise

    def _generate_questions(
        self, topic: str, difficulty: str, num_questions: int, 
        user_profile: dict, rag_context: str
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions based on parameters"""

        questions = []

        # Use topic-specific question templates
        question_bank = self._get_question_bank(topic, difficulty)

        # Select appropriate number of questions
        for i in range(min(num_questions, len(question_bank))):
            questions.append(question_bank[i])

        return questions

    def _get_question_bank(self, topic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Get question bank for a specific topic and difficulty"""

        topic_lower = topic.lower()

        # Easy questions
        if difficulty == "easy":
            return self._easy_questions(topic_lower)
        elif difficulty == "hard":
            return self._hard_questions(topic_lower)
        else:
            return self._medium_questions(topic_lower)

    def _easy_questions(self, topic: str) -> List[Dict[str, Any]]:
        """Generate easy difficulty questions"""
        questions = [
            {
                "question_id": "easy_001",
                "question": "What is money?",
                "type": "multiple_choice",
                "options": [
                    "Something we use to buy things",
                    "Only paper",
                    "Something only for adults",
                    "A game"
                ],
                "correct_answer": 0,
                "explanation": "Money is anything we use to exchange value. It can be paper, coins, or digital!"
            },
            {
                "question_id": "easy_002",
                "question": "What does 'saving money' mean?",
                "type": "multiple_choice",
                "options": [
                    "Not spending all your money at once",
                    "Throwing money away",
                    "Giving money to others",
                    "Losing money"
                ],
                "correct_answer": 0,
                "explanation": "Saving means keeping money for future use instead of spending it immediately!"
            },
            {
                "question_id": "easy_003",
                "question": "If you have $10 and spend $3, how much is left?",
                "type": "multiple_choice",
                "options": [
                    "$7",
                    "$13",
                    "$6",
                    "$4"
                ],
                "correct_answer": 0,
                "explanation": "$10 - $3 = $7. Great math skills!"
            },
            {
                "question_id": "easy_004",
                "question": "What is a piggy bank used for?",
                "type": "multiple_choice",
                "options": [
                    "Saving coins and bills",
                    "Feeding pigs",
                    "Playing with",
                    "Decorating rooms"
                ],
                "correct_answer": 0,
                "explanation": "A piggy bank is a fun way to save money by collecting coins!"
            },
            {
                "question_id": "easy_005",
                "question": "Which is a need?",
                "type": "multiple_choice",
                "options": [
                    "Food and shelter",
                    "Video games",
                    "Toys",
                    "Candy"
                ],
                "correct_answer": 0,
                "explanation": "Needs are things we must have to live, like food and a place to sleep."
            }
        ]
        return questions

    def _medium_questions(self, topic: str) -> List[Dict[str, Any]]:
        """Generate medium difficulty questions"""
        questions = [
            {
                "question_id": "med_001",
                "question": "If you save $5 every week, how much will you have after 4 weeks?",
                "type": "multiple_choice",
                "options": [
                    "$20",
                    "$15",
                    "$25",
                    "$10"
                ],
                "correct_answer": 0,
                "explanation": "$5 × 4 weeks = $20. Good calculation!"
            },
            {
                "question_id": "med_002",
                "question": "What is a budget?",
                "type": "multiple_choice",
                "options": [
                    "A plan for how to spend and save your money",
                    "A type of bank account",
                    "A job",
                    "Money left over after spending"
                ],
                "correct_answer": 0,
                "explanation": "A budget helps you plan where your money goes and reach your goals!"
            },
            {
                "question_id": "med_003",
                "question": "If a bike costs $80 and you can save $10 per week, how many weeks to buy it?",
                "type": "multiple_choice",
                "options": [
                    "8 weeks",
                    "5 weeks",
                    "10 weeks",
                    "6 weeks"
                ],
                "correct_answer": 0,
                "explanation": "$80 ÷ $10 = 8 weeks. Great problem-solving!"
            },
            {
                "question_id": "med_004",
                "question": "What is the difference between needs and wants?",
                "type": "multiple_choice",
                "options": [
                    "Needs are essential, wants are nice to have",
                    "There is no difference",
                    "Needs cost more",
                    "Wants are more important"
                ],
                "correct_answer": 0,
                "explanation": "Needs keep us healthy and safe. Wants are things we desire but don't need to survive."
            },
            {
                "question_id": "med_005",
                "question": "How can a kid earn money?",
                "type": "multiple_choice",
                "options": [
                    "By doing chores, babysitting, or starting a small business",
                    "Only by getting an allowance",
                    "By finding money on the street",
                    "By asking parents"
                ],
                "correct_answer": 0,
                "explanation": "There are many ways to earn money! Chores, services, or small businesses are great for kids."
            }
        ]
        return questions

    def _hard_questions(self, topic: str) -> List[Dict[str, Any]]:
        """Generate hard difficulty questions"""
        questions = [
            {
                "question_id": "hard_001",
                "question": "If you invest $100 at 5% interest per year, how much will you have after 2 years (simple interest)?",
                "type": "multiple_choice",
                "options": [
                    "$110",
                    "$100",
                    "$120",
                    "$105"
                ],
                "correct_answer": 0,
                "explanation": "Simple interest: $100 × 0.05 × 2 = $10. Total: $100 + $10 = $110"
            },
            {
                "question_id": "hard_002",
                "question": "What is the concept of 'opportunity cost'?",
                "type": "multiple_choice",
                "options": [
                    "The value of what you give up when making a choice",
                    "The cost of a business opportunity",
                    "The price difference in stores",
                    "A type of discount"
                ],
                "correct_answer": 0,
                "explanation": "Opportunity cost is what you miss out on by choosing one thing over another."
            },
            {
                "question_id": "hard_003",
                "question": "If you have $500 to invest and can choose between 3% or 7% annual return, which is better over 10 years?",
                "type": "multiple_choice",
                "options": [
                    "7% (earning about $396 more)",
                    "3% (more stable)",
                    "They're the same",
                    "3% (safer)"
                ],
                "correct_answer": 0,
                "explanation": "Higher returns usually mean higher risk, but over 10 years, 7% significantly outpaces 3%."
            },
            {
                "question_id": "hard_004",
                "question": "What is a credit score and why does it matter?",
                "type": "multiple_choice",
                "options": [
                    "A number showing how reliable you are with borrowed money",
                    "Your bank account balance",
                    "How much money you earn",
                    "A grade from school"
                ],
                "correct_answer": 0,
                "explanation": "Credit scores help lenders decide if they'll loan you money at good interest rates."
            },
            {
                "question_id": "hard_005",
                "question": "Starting a business with $200 in costs, earning $50/week profit - how many weeks to break even?",
                "type": "multiple_choice",
                "options": [
                    "4 weeks",
                    "2 weeks",
                    "6 weeks",
                    "8 weeks"
                ],
                "correct_answer": 0,
                "explanation": "$200 ÷ $50 = 4 weeks. After that, all earnings are pure profit!"
            }
        ]
        return questions
