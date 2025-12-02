"""
Story Agent
Creates engaging financial stories tailored to kids
"""

import logging
from typing import Dict, Any
from .base_agent import Agent

logger = logging.getLogger(__name__)


class StoryAgent(Agent):
    """Generates financial education stories for kids"""

    def __init__(self):
        super().__init__("StoryAgent")

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate a story based on user profile and topic
        
        Args:
            user_profile: dict with age, hobbies, interests
            topic: str - financial topic (e.g., "saving money", "budgeting")
            difficulty: str - easy, medium, hard
            rag_context: str - context from RAG about the topic
        
        Returns:
            dict with story and metadata
        """
        try:
            user_profile = kwargs.get("user_profile", {})
            topic = kwargs.get("topic", "money basics")
            difficulty = kwargs.get("difficulty", "medium")
            rag_context = kwargs.get("rag_context", "")

            self.log_execution("Story Generation", "started", {
                "user": user_profile.get("name"),
                "topic": topic,
                "difficulty": difficulty
            })

            # Create story based on user's interests
            story = self._create_personalized_story(
                user_profile, topic, difficulty, rag_context
            )

            return {
                "status": "success",
                "story": story,
                "agent": self.name,
                "topic": topic,
                "difficulty": difficulty
            }

        except Exception as e:
            logger.error(f"Error in StoryAgent: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }

    def _create_personalized_story(
        self, user_profile: dict, topic: str, difficulty: str, rag_context: str
    ) -> str:
        """Create a personalized story tailored to the child"""

        name = user_profile.get("name", "Alex")
        age = user_profile.get("age", 10)
        hobbies = user_profile.get("hobbies", "").split(", ") if user_profile.get("hobbies") else []

        # Map hobby to story element
        hobby_element = self._map_hobby_to_story_element(hobbies)

        # Build story based on difficulty level
        if difficulty == "easy":
            story = self._build_easy_story(name, age, topic, hobby_element)
        elif difficulty == "hard":
            story = self._build_hard_story(name, age, topic, hobby_element)
        else:
            story = self._build_medium_story(name, age, topic, hobby_element)

        # Add RAG context if available
        if rag_context:
            story += f"\n\n[Based on: {rag_context[:100]}...]"

        return story

    def _map_hobby_to_story_element(self, hobbies: list) -> str:
        """Map hobbies to story elements"""
        hobby_map = {
            "video games": "gaming tournament prize money",
            "drawing": "art commission earnings",
            "soccer": "team fundraiser for equipment",
            "reading": "bookstore discount cards",
            "science": "science kit to build",
            "music": "musical instrument to buy",
            "anime": "anime convention tickets",
            "coding": "computer upgrade fund",
            "basketball": "basketball camp registration",
            "art": "art supplies shopping spree",
            "mathematics": "math competition prizes",
            "lego": "LEGO set collection goal"
        }

        for hobby in hobbies:
            if hobby in hobby_map:
                return hobby_map[hobby]
        
        return "personal project funding"

    def _build_easy_story(self, name: str, age: int, topic: str, hobby_element: str) -> str:
        """Build a simple story for younger kids"""
        return f"""
🌟 **{name}'s Money Adventure** 🌟

Hi {name}! Today, let's learn about **{topic}** with a fun story!

Imagine {name} wants to save money for {hobby_element}.

💡 **The Challenge:**
You have $10. Your goal is to save enough money in 3 months to buy something special for ${20 * (int(age) / 10):.0f}.

📖 **The Story:**
Every week, {name} does chores and earns $5. Instead of spending it all on snacks, {name} decides to put the money in a special jar.

**Week 1:** $5 saved
**Week 2:** $10 saved (total)
**Week 3:** $15 saved (total)
**Week 4:** $20 saved (total) ✨

🎉 **Success!** {name} reached the goal and bought the {hobby_element}!

💭 **What did we learn?**
- Small amounts add up to big goals
- Patience helps us achieve what we want
- Saving is powerful!
        """

    def _build_medium_story(self, name: str, age: int, topic: str, hobby_element: str) -> str:
        """Build a medium-difficulty story"""
        return f"""
🎯 **{name}'s {topic.title()} Quest** 🎯

Meet {name}, a {age}-year-old financial explorer!

📚 **The Mission:**
Learn about {topic} to unlock the treasure of {hobby_element}.

🗺️ **The Journey:**

**Stage 1: Understanding the Concept**
{name} discovers that {topic} is about making smart choices with money.

**Stage 2: The Challenge**
{name} has three options:
1. Spend all $50 immediately on video games
2. Save $30 and spend $20 on games now
3. Save all $50 for the ultimate {hobby_element}

**Stage 3: The Decision**
{name} chooses option 3! Here's the plan:
- Save $10 per week for 5 weeks = $50
- Add birthday money ($20) = $70
- Buy the {hobby_element} + extras!

**Stage 4: The Twist**
Along the way, {name} learns:
- How interest can grow savings
- Why goals matter
- The joy of achievement

🏆 **The Reward**
After 8 weeks, {name} has enough money AND learned valuable lessons about {topic}!

✨ **The Real Treasure?**
Not just the {hobby_element}, but the financial skills {name} will use forever!
        """

    def _build_hard_story(self, name: str, age: int, topic: str, hobby_element: str) -> str:
        """Build a challenging story for older kids"""
        return f"""
🚀 **{name}'s Advanced {topic.title()} Simulation** 🚀

**Scenario:** {name} is starting a small business to fund {hobby_element}!

📊 **Business Plan:**
Topic: {topic}
Product/Service: Custom {hobby_element} (based on your interests)
Target Customers: School friends and family
Timeline: 12 weeks

💰 **Financial Breakdown:**

Initial Investment: $20
- Supplies and materials

Weekly Revenue Targets:
- Week 1-2: $10/week (startup phase)
- Week 3-6: $20/week (growth phase)
- Week 7-12: $30/week (scaling phase)

Total Expected Revenue: $210

Expenses Analysis:
- Cost per item: $3
- Profit margin: 60%
- Break-even: Week 2

📈 **Growth Projection:**
If successful, could expand to make $500+ in 6 months!

🎓 **Advanced Concepts to Explore:**
1. ROI (Return on Investment): 950%
2. Profit Margins: 60%
3. Reinvestment Strategy
4. Customer Satisfaction = Repeat Business
5. Scaling challenges

🏅 **Success Metrics:**
- Financial Goal: Achieve $200+ revenue
- Learning Goal: Understand business fundamentals
- Personal Goal: Build confidence in financial management

🔮 **The Big Picture:**
This isn't just about {topic} - it's about understanding how money really works in the real world!
        """
