"""
Quiz Agent V3 - PDF-Based Question Generation
Generates quiz questions from educational PDF content
Uses PDF topics and content combined with Gemini for personalization
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

# Import PDF-based question generator
try:
    from backend.services.pdf_question_generator import PDFBasedQuestionGenerator
    PDF_GENERATOR_AVAILABLE = True
except ImportError:
    PDF_GENERATOR_AVAILABLE = False


class QuizAgent(Agent):
    """Generates personalized quiz questions from PDF content"""

    def __init__(self):
        super().__init__("QuizAgent")
        
        # Initialize PDF-based question generator
        if PDF_GENERATOR_AVAILABLE:
            self.pdf_generator = PDFBasedQuestionGenerator()
            logger.info("✅ PDF-based question generator initialized")
        else:
            self.pdf_generator = None
            logger.warning("⚠️  PDF generator not available")

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate personalized quiz questions from PDF content
        
        Args:
            topic: str - financial topic (from PDF topics)
            difficulty: str - easy, medium, hard
            num_questions: int - number of questions (default 5)
            user_profile: dict - user info including age, hobbies, quiz_history
            database: database instance for fetching answer history
            user_id: str - user ID for fetching their answer history
        
        Returns:
            dict with quiz questions generated from PDF content
        """
        try:
            topic = kwargs.get("topic", "money basics")
            difficulty = kwargs.get("difficulty", "medium")
            num_questions = kwargs.get("num_questions", 5)
            user_profile = kwargs.get("user_profile", {})
            database = kwargs.get("database", None)
            user_id = kwargs.get("user_id", "")
            user_age = user_profile.get("age", 11)
            user_hobbies = user_profile.get("hobbies", "")

            self.log_execution("Quiz Generation", "started", {
                "topic": topic,
                "difficulty": difficulty,
                "user": user_profile.get("name", "Unknown"),
                "source": "PDF",
                "personalized": True
            })

            # Get questions user has already answered correctly
            correctly_answered = []
            if database and user_id:
                try:
                    correctly_answered = database.get_correctly_answered_questions(user_id, limit=30)
                except Exception as e:
                    logger.warning(f"Could not fetch answered questions: {e}")

            # Step 1: Try PDF-based question generation (NEW APPROACH)
            if self.pdf_generator:
                try:
                    questions = self.pdf_generator.generate_questions_for_topic(
                        age=user_age,
                        topic=topic,
                        num_questions=num_questions,
                        user_hobbies=user_hobbies
                    )
                    
                    if questions and len(questions) > 0:
                        # Filter out questions user has already answered correctly
                        questions = self._filter_answered_questions(questions, correctly_answered)
                        
                        logger.info(f"Generated {len(questions)} questions from PDF for topic: {topic}")
                        return {
                            "status": "success",
                            "questions": questions,
                            "topic": topic,
                            "difficulty": difficulty,
                            "total_questions": len(questions),
                            "personalized": True,
                            "source": "PDF",
                            "agent": self.name
                        }
                except Exception as e:
                    logger.warning(f"PDF generation failed: {e}, trying fallback")
            
            # Step 2: Fallback to Gemini-based generation
            if GEMINI_AVAILABLE:
                try:
                    questions = self._generate_with_gemini(
                        topic, difficulty, num_questions, user_profile, correctly_answered
                    )
                    logger.info(f"Generated {len(questions)} personalized questions with Gemini (fallback)")
                    return {
                        "status": "success",
                        "questions": questions,
                        "topic": topic,
                        "difficulty": difficulty,
                        "total_questions": len(questions),
                        "personalized": True,
                        "source": "Gemini",
                        "agent": self.name
                    }
                except Exception as e:
                    logger.warning(f"Gemini generation failed: {e}, using templates")
            
            # Step 3: Final fallback to template-based questions
            questions = self._generate_from_templates(
                topic, difficulty, num_questions, user_profile, correctly_answered
            )
            

            return {
                "status": "success",
                "questions": questions,
                "topic": topic,
                "difficulty": difficulty,
                "total_questions": len(questions),
                "personalized": False,
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"Error in QuizAgent: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }

    def _filter_answered_questions(
        self, questions: List[Dict[str, Any]], correctly_answered: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter out questions that the user has already answered correctly
        
        Args:
            questions: List of generated questions
            correctly_answered: List of questions user got right (contains 'question_text')
        
        Returns:
            Filtered list of new questions
        """
        if not correctly_answered:
            return questions
        
        # Extract question text from correctly answered questions
        answered_texts = {qa.get("question_text", "").lower().strip() for qa in correctly_answered}
        
        # Filter out duplicate/similar questions
        filtered = []
        for q in questions:
            q_text = q.get("question", "").lower().strip()
            if q_text and q_text not in answered_texts:
                filtered.append(q)
        
        return filtered if filtered else questions

    def _generate_with_gemini(
        self, topic: str, difficulty: str, num_questions: int, user_profile: dict,
        correctly_answered: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized questions using Gemini 2.5 Flash
        
        Personalization factors:
        - User age and hobbies for context
        - Previous quiz history and scores
        - Current difficulty level
        - Topic focus
        - Questions user has already mastered (correctly answered)
        """
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Extract user information
            user_name = user_profile.get("name", "Student")
            user_age = user_profile.get("age", 10)
            hobbies = user_profile.get("hobbies", "learning")
            quiz_history = user_profile.get("quiz_history", [])
            
            # Build context from quiz history
            history_context = ""
            if quiz_history:
                # Get topics they've studied
                studied_topics = list(set([q.get("topic", "") for q in quiz_history[-10:]]))
                avg_score = sum(q.get("percentage", 0) for q in quiz_history) / len(quiz_history) if quiz_history else 0
                weak_areas = [q.get("topic", "") for q in quiz_history if q.get("percentage", 0) < 60]
                
                history_context = f"""
Previous Learning History:
- Topics studied: {', '.join(studied_topics) if studied_topics else 'None yet'}
- Average score: {avg_score:.0f}%
- Areas needing improvement: {', '.join(set(weak_areas)) if weak_areas else 'None'}
- Number of quizzes completed: {len(quiz_history)}
"""
            
            # Build context of questions they've already mastered
            mastered_context = ""
            if correctly_answered:
                mastered_topics = list(set([q.get("topic", "") for q in correctly_answered]))
                mastered_context = f"""

IMPORTANT - Questions User Has Mastered:
- User has already correctly answered questions on: {', '.join(mastered_topics) if mastered_topics else 'None'}
- Generate NEW, DIFFERENT questions they haven't seen before
- Avoid these specific topics or similar questions:"""
                for q in correctly_answered[:5]:
                    mastered_context += f"\n  * {q.get('question', '')[:100]}"
                mastered_context += "\n- Focus on new aspects of the topic or challenging variations"
            
            # Customize prompt based on difficulty
            difficulty_hints = {
                "easy": "Simple, fundamental concepts. Include basic calculations. Keep language simple.",
                "medium": "Real-world scenarios. Some calculations. Practical decision-making.",
                "hard": "Complex scenarios. Multiple-step problems. Critical thinking required."
            }
            
            prompt = f"""Generate {num_questions} personalized multiple-choice questions about "{topic}" for financial education.

STUDENT PROFILE:
- Name: {user_name}
- Age: {user_age} years old
- Hobbies/Interests: {hobbies}
{history_context}{mastered_context}

DIFFICULTY LEVEL: {difficulty.upper()}
{difficulty_hints.get(difficulty, '')}

REQUIREMENTS:
1. Make questions relatable to the student's age ({user_age}) and interests ({hobbies})
2. Focus on "{topic}" topic
3. Correct answers should be randomly distributed (positions 0-3, NOT always position 0)
4. Include diverse question types (calculations, concepts, scenarios, decisions)
5. Include clear, educational explanations
6. CRITICAL: Avoid questions user has already mastered - create NEW variations
7. All questions must be engaging and age-appropriate
8. If user has mastered the topic, create challenging scenarios or extensions

RESPONSE FORMAT - RETURN ONLY VALID JSON (no markdown, no code blocks):
{{
    "questions": [
        {{
            "question_id": "q_1",
            "question": "Question text here",
            "type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Explanation of why this answer is correct"
        }},
        ...
    ]
}}

Important: Ensure correct_answer positions vary! Use 0, 1, 2, 3 randomly, not always 0.

Generate {num_questions} questions now:"""
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean JSON if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text)
            questions = result.get("questions", [])
            
            # Validate questions
            validated = []
            for i, q in enumerate(questions[:num_questions]):
                if not q.get("question") or len(q.get("options", [])) < 4:
                    continue
                    
                validated_q = {
                    "question_id": f"q_{i+1}",
                    "question": q.get("question", ""),
                    "type": "multiple_choice",
                    "options": q.get("options", []),
                    "correct_answer": int(q.get("correct_answer", 0)) % 4,  # Ensure 0-3
                    "explanation": q.get("explanation", "")
                }
                validated.append(validated_q)
            
            if len(validated) < num_questions:
                logger.warning(f"Only generated {len(validated)} valid questions out of {num_questions} requested")
            
            return validated[:num_questions]
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error from Gemini: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating with Gemini: {e}")
            raise

    def _generate_from_templates(
        self, topic: str, difficulty: str, num_questions: int, user_profile: dict,
        correctly_answered: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fallback: Generate questions from templates
        Ensures variety in correct answer positions
        Filters out questions user has already mastered
        """
        topic_lower = topic.lower()
        
        # Get base question bank
        if difficulty == "easy":
            question_bank = self._get_easy_bank(topic_lower, user_profile)
        elif difficulty == "hard":
            question_bank = self._get_hard_bank(topic_lower, user_profile)
        else:
            question_bank = self._get_medium_bank(topic_lower, user_profile)
        
        # Filter out questions user has already mastered
        if correctly_answered:
            correctly_answered_questions = {q.get("question", "") for q in correctly_answered}
            filtered_bank = [q for q in question_bank if q.get("question", "") not in correctly_answered_questions]
            question_bank = filtered_bank if filtered_bank else question_bank  # Use original if all filtered
        
        # Shuffle correct answer positions to avoid pattern
        for q in question_bank:
            self._shuffle_options(q)
        
        return question_bank[:num_questions]

    def _shuffle_options(self, question: Dict[str, Any]) -> None:
        """Randomize option positions while tracking correct answer"""
        import random
        
        correct_option = question["options"][question["correct_answer"]]
        options = question["options"][:]
        random.shuffle(options)
        
        question["options"] = options
        question["correct_answer"] = options.index(correct_option)

    def _get_easy_bank(self, topic: str, user_profile: dict) -> List[Dict[str, Any]]:
        """Easy questions - age appropriate"""
        age = user_profile.get("age", 10)
        hobbies = user_profile.get("hobbies", "")
        
        questions = [
            {
                "question_id": "e1",
                "question": "What is money used for?",
                "options": ["To buy things we want and need", "To decorate rooms", "To play games", "Only for adults"],
                "correct_answer": 0,
                "explanation": "Money helps us buy both things we need (food, clothes) and things we want (toys, games)!"
            },
            {
                "question_id": "e2",
                "question": "What is saving?",
                "options": ["Keeping money instead of spending it", "Giving money away", "Losing money", "Making money"],
                "correct_answer": 0,
                "explanation": "Saving means putting money aside for the future instead of spending it right away."
            },
            {
                "question_id": "e3",
                "question": f"If you have $15 and spend $6, how much is left?",
                "options": ["$9", "$21", "$6", "$15"],
                "correct_answer": 0,
                "explanation": "$15 - $6 = $9. You did the math correctly!"
            },
            {
                "question_id": "e4",
                "question": "Which is something you NEED?",
                "options": ["Food and shelter", "Video games", "Toys", "Candy"],
                "correct_answer": 0,
                "explanation": "Needs are things necessary for living. Wants are things we'd like to have!"
            },
            {
                "question_id": "e5",
                "question": "What does a piggy bank do?",
                "options": ["Helps you save money", "Feeds animals", "Teaches math", "Makes money"],
                "correct_answer": 0,
                "explanation": "A piggy bank is a fun way to collect and save coins!"
            },
            {
                "question_id": "e6",
                "question": "How much is 2 coins of $5 each?",
                "options": ["$10", "$7", "$3", "$5"],
                "correct_answer": 0,
                "explanation": "$5 + $5 = $10. Great counting!"
            },
            {
                "question_id": "e7",
                "question": "What's a coin?",
                "options": ["A round piece of metal money", "A game", "A chocolate candy", "A type of game token"],
                "correct_answer": 0,
                "explanation": "Coins are physical money made from metal. Paper money is called bills!"
            },
            {
                "question_id": "e8",
                "question": "If your friend gives you $3 and you have $2, how much total?",
                "options": ["$5", "$1", "$3", "$2"],
                "correct_answer": 0,
                "explanation": "$2 + $3 = $5. Sharing and adding makes more!"
            }
        ]
        
        return questions

    def _get_medium_bank(self, topic: str, user_profile: dict) -> List[Dict[str, Any]]:
        """Medium difficulty questions"""
        age = user_profile.get("age", 10)
        
        questions = [
            {
                "question_id": "m1",
                "question": "If you save $5 every week for 4 weeks, how much total?",
                "options": ["$20", "$9", "$15", "$5"],
                "correct_answer": 0,
                "explanation": "$5 × 4 = $20. Regular saving adds up!"
            },
            {
                "question_id": "m2",
                "question": "What is a budget?",
                "options": ["A plan for how to spend money", "A type of bank", "A game about money", "A job"],
                "correct_answer": 0,
                "explanation": "A budget helps you plan how to use your money wisely."
            },
            {
                "question_id": "m3",
                "question": "A jacket costs $40. You have $50. How much change?",
                "options": ["$10", "$90", "$40", "$50"],
                "correct_answer": 0,
                "explanation": "$50 - $40 = $10. That's your change!"
            },
            {
                "question_id": "m4",
                "question": "What does interest mean in banking?",
                "options": ["Extra money the bank gives you", "A type of hobby", "Bank rules", "A payment"],
                "correct_answer": 0,
                "explanation": "Interest is extra money banks give you for keeping money with them!"
            },
            {
                "question_id": "m5",
                "question": "If you earn $20 and save half, how much saved?",
                "options": ["$10", "$20", "$30", "$5"],
                "correct_answer": 0,
                "explanation": "Half of $20 is $10. Half means divide by 2!"
            },
            {
                "question_id": "m6",
                "question": "What is the best reason to save money?",
                "options": ["For future needs and goals", "To hide it", "To show friends", "No reason"],
                "correct_answer": 0,
                "explanation": "Saving helps you prepare for future expenses and dreams!"
            },
            {
                "question_id": "m7",
                "question": "A book costs $8. You buy 3 books. Total cost?",
                "options": ["$24", "$11", "$8", "$3"],
                "correct_answer": 0,
                "explanation": "$8 × 3 = $24. Multiplication helps with shopping!"
            },
            {
                "question_id": "m8",
                "question": "What is a debit card?",
                "options": ["A card that uses your own money", "Borrowed money", "Credit card", "A game card"],
                "correct_answer": 0,
                "explanation": "Debit cards let you spend money from your own bank account!"
            }
        ]
        
        return questions

    def _get_hard_bank(self, topic: str, user_profile: dict) -> List[Dict[str, Any]]:
        """Hard difficulty questions"""
        
        questions = [
            {
                "question_id": "h1",
                "question": "You earn $100. You save 30%, spend 50%, donate 20%. How much saved?",
                "options": ["$30", "$50", "$20", "$80"],
                "correct_answer": 0,
                "explanation": "30% of $100 = $30. Breaking down percentages helps with finances!"
            },
            {
                "question_id": "h2",
                "question": "If you invest $100 at 10% interest per year, how much after 1 year?",
                "options": ["$110", "$100", "$120", "$90"],
                "correct_answer": 0,
                "explanation": "10% of $100 = $10, so $100 + $10 = $110. That's compound interest!"
            },
            {
                "question_id": "h3",
                "question": "A store offers 20% discount on $50 item. Final price?",
                "options": ["$40", "$70", "$50", "$30"],
                "correct_answer": 0,
                "explanation": "20% of $50 = $10, so $50 - $10 = $40. Discounts save money!"
            },
            {
                "question_id": "h4",
                "question": "What is inflation?",
                "options": ["When prices of things increase over time", "Blowing air", "A type of bank", "Money disappearing"],
                "correct_answer": 0,
                "explanation": "Inflation means things cost more money as time passes. Your money buys less!"
            },
            {
                "question_id": "h5",
                "question": "You need $500 in 5 months. How much to save monthly?",
                "options": ["$100", "$500", "$50", "$250"],
                "correct_answer": 0,
                "explanation": "$500 ÷ 5 = $100/month. Planning ahead with math!"
            },
            {
                "question_id": "h6",
                "question": "What is a credit score?",
                "options": ["A number showing how trustworthy you are with money", "Your total money", "Bank password", "Interest rate"],
                "correct_answer": 0,
                "explanation": "Credit scores help banks decide if they'll lend you money. Higher is better!"
            },
            {
                "question_id": "h7",
                "question": "You spend 60% of income on needs, rest on wants. On $1000 income, wants budget?",
                "options": ["$400", "$600", "$1000", "$200"],
                "correct_answer": 0,
                "explanation": "60% on needs = $600, so 40% remains for wants = $400. Balance is important!"
            },
            {
                "question_id": "h8",
                "question": "What is an emergency fund?",
                "options": ["Money saved for unexpected expenses", "Money for games", "Credit card", "Bank loan"],
                "correct_answer": 0,
                "explanation": "Emergency funds protect you when unexpected costs happen. Experts suggest 3-6 months of expenses!"
            }
        ]
        
        return questions
