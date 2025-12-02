"""
PDF Data Cleaner and Topic Filter
Cleans PDF extracted data and filters topics for quality
"""

import logging
import re
from typing import List, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class DataCleaner:
    """Cleans and normalizes PDF extracted content"""
    
    # Common English stop words to filter
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'from', 'as', 'is', 'was', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can', 'that', 'this',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
        'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'same', 'so', 'than', 'too',
        'very', 'just', 'about', 'above', 'after', 'before', 'between', 'into', 'through',
        'during', 'while', 'because', 'if', 'then', 'else', 'any', 'many', 'yours', 'theirs'
    }
    
    # Metadata and noise patterns to remove
    NOISE_PATTERNS = {
        'advisory', 'monitoring', 'editing', 'board', 'published', 'printed', 'copyright',
        'isbn', 'page', 'cbse', 'ncert', 'edition', 'index', 'glossary', 'appendix',
        'workbook', 'textbook', 'author', 'edition', 'class:', 'class -', 'standard',
        'subject:', 'chapter:', 'lesson:', 'unit:', 'exercise', 'activity', 'solution',
        'answer', 'summary', 'review', 'test', 'exam', 'quiz', 'worksheet', 'handout'
    }
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted PDF text
        
        Args:
            text: Raw PDF extracted text
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Step 1: Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n\s*\n', '\n', text)  # Multiple newlines to single newline
        
        # Step 2: Fix broken words (words split across lines)
        text = re.sub(r'([a-z])-\n([a-z])', r'\1\2', text, flags=re.IGNORECASE)
        
        # Step 3: Remove special characters that appear as noise
        # Keep only letters, numbers, spaces, punctuation, and newlines
        text = re.sub(r'[^\w\s\n\.\,\:\;\!\?\-\(\)\/]', '', text)
        
        # Step 4: Normalize spacing around punctuation
        text = re.sub(r'\s+([,.:;!?])', r'\1', text)  # Remove space before punctuation
        
        return text.strip()
    
    def clean_line(self, line: str) -> str:
        """
        Clean a single line of text
        
        Args:
            line: Raw line
        
        Returns:
            Cleaned line
        """
        if not line:
            return ""
        
        # Strip whitespace
        line = line.strip()
        
        # Fix broken words with spaces: "Income T ax" -> "Income Tax"
        line = re.sub(r'\s([A-Z])\s+([a-z])', r' \1\2', line)  # "T ax" -> "Tax"
        line = re.sub(r'([a-z])\s+([A-Z])\s+([a-z])', r'\1\2\3', line)  # "T a x" -> "Tax"
        
        # Fix merged words with CamelCase: "CardTypes" -> "Card Types"
        line = re.sub(r'([a-z])([A-Z])', r'\1 \2', line)
        
        # Fix merged topic names: "TypesOf" -> "Types Of" (capital O after non-capital)
        # This catches patterns like "LoanGold" -> "Loan Gold"
        line = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', line)
        
        # Remove extra internal spaces
        line = re.sub(r'\s+', ' ', line)
        
        # Remove trailing punctuation
        line = re.sub(r'[,.:;]+$', '', line)
        
        return line
    
    def filter_topic(self, topic: str) -> bool:
        """
        Check if topic is valid and worth keeping
        
        Args:
            topic: Topic string to validate
        
        Returns:
            True if topic is valid, False otherwise
        """
        if not topic:
            return False
        
        # Length check
        if len(topic) < 5 or len(topic) > 100:
            return False
        
        # Too many numbers
        if sum(1 for c in topic if c.isdigit()) > len(topic) / 3:
            return False
        
        # Contains metadata/noise
        topic_lower = topic.lower()
        if any(noise in topic_lower for noise in self.NOISE_PATTERNS):
            return False
        
        # All stop words
        words = topic_lower.split()
        content_words = [w for w in words if w not in self.STOP_WORDS]
        if len(content_words) == 0:
            return False
        
        # Word count reasonable (2-6 words for a topic)
        if len(words) < 2 or len(words) > 6:
            return False
        
        # Must contain at least one meaningful word (not all numbers/special chars)
        if not any(c.isalpha() for c in topic):
            return False
        
        return True
    
    def extract_key_topics(self, text: str) -> List[str]:
        """
        Extract clean, meaningful topics from text
        
        Args:
            text: Cleaned text content
        
        Returns:
            List of extracted topics
        """
        topics = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = self.clean_line(line)
            
            if not line:
                continue
            
            # Look for potential topic indicators
            is_potential_topic = (
                # Capitalized words (title case)
                (line[0].isupper() if line else False) and
                # Not a question (no question mark)
                '?' not in line and
                # Not a sentence (no period at end typically)
                not line.endswith('.') and
                # Has meaningful length
                len(line) >= 5 and len(line) <= 80
            )
            
            if is_potential_topic and self.filter_topic(line):
                topics.append(line)
        
        return topics
    
    def remove_duplicates_case_insensitive(self, items: List[str]) -> List[str]:
        """
        Remove duplicate items (case-insensitive)
        
        Args:
            items: List of strings
        
        Returns:
            Deduplicated list preserving order
        """
        seen = set()
        result = []
        
        for item in items:
            item_lower = item.lower()
            if item_lower not in seen:
                seen.add(item_lower)
                result.append(item)
        
        return result
    
    def clean_and_filter_topics(self, topics: List[str]) -> List[str]:
        """
        Clean and filter list of topics
        
        Args:
            topics: Raw topic list
        
        Returns:
            Cleaned and filtered topic list
        """
        # Clean each topic
        cleaned = [self.clean_line(t) for t in topics if t]
        
        # Filter valid topics
        filtered = [t for t in cleaned if self.filter_topic(t)]
        
        # Remove duplicates
        deduplicated = self.remove_duplicates_case_insensitive(filtered)
        
        # Sort by relevance (prefer shorter, more specific topics)
        sorted_topics = sorted(deduplicated, key=lambda x: (len(x.split()), len(x)))
        
        logger.info(f"Cleaned {len(topics)} topics → {len(sorted_topics)} valid topics")
        
        return sorted_topics


class TopicSelector:
    """Intelligently selects best topics for user dropdown"""
    
    # Financial education core topics
    CORE_TOPICS = {
        'banking', 'savings', 'credit', 'investment', 'budgeting', 'income',
        'insurance', 'debt', 'payment', 'planning', 'interest', 'account',
        'loan', 'expense', 'earning', 'financial', 'money', 'card', 'tax'
    }
    
    def score_topic(self, topic: str, age: int) -> float:
        """
        Score a topic based on relevance and age appropriateness
        
        Args:
            topic: Topic string
            age: User age
        
        Returns:
            Relevance score (0-100)
        """
        score = 50  # Base score
        topic_lower = topic.lower()
        
        # Boost for core financial topics
        if any(core in topic_lower for core in self.CORE_TOPICS):
            score += 20
        
        # Age-based adjustments
        if age < 12:
            # Prefer basic, simple topics
            if len(topic.split()) <= 3:
                score += 10
            if any(word in topic_lower for word in ['basic', 'simple', 'intro', 'introduction']):
                score += 10
        elif age < 14:
            # Medium complexity
            if 2 <= len(topic.split()) <= 4:
                score += 10
        else:
            # Prefer slightly longer, more complex topics
            if len(topic.split()) >= 3:
                score += 10
            if any(word in topic_lower for word in ['advanced', 'management', 'planning']):
                score += 10
        
        # Penalty for overly long topics
        if len(topic) > 60:
            score -= 15
        
        # Penalty for ambiguous topics
        if len(topic.split()) > 5:
            score -= 10
        
        return max(0, min(100, score))
    
    def select_best_topics(self, topics: List[str], age: int, count: int = 5) -> List[str]:
        """
        Select best topics for user's age group
        
        Args:
            topics: Available topics
            age: User age
            count: Number of topics to select
        
        Returns:
            Selected topics ranked by relevance
        """
        if not topics:
            return []
        
        # Score each topic
        scored = [(t, self.score_topic(t, age)) for t in topics]
        
        # Sort by score (descending)
        ranked = sorted(scored, key=lambda x: x[1], reverse=True)
        
        # Take top count
        selected = [t for t, _ in ranked[:count]]
        
        logger.info(f"Selected {len(selected)} best topics for age {age}")
        
        return selected

