"""
PDF Content Extractor Service
Extracts topics and content from educational PDFs based on user age/class
Maps age to appropriate class PDF and extracts learning content
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

logger = logging.getLogger(__name__)

# PDF file paths
PDF_DIR = Path("/Users/mohak@backbase.com/Projects/Internal hackathon/content/financial-education-pdfs")

# Age to class mapping
AGE_TO_CLASS = {
    11: "Class_7th",
    12: "Class_7th",
    13: "Class_8th",
    14: "Class_9th",
    15: "Class_10th",
}

# Age ranges for each class
CLASS_AGE_RANGES = {
    "Class_6th": (11, 12),
    "Class_7th": (12, 13),
    "Class_8th": (13, 14),
    "Class_9th": (14, 15),
    "Class_10th": (15, 16),
}


class PDFContentExtractor:
    """Extracts topics and content from educational PDFs"""
    
    def __init__(self):
        """Initialize PDF extractor"""
        self.pdf_cache = {}  # Cache extracted PDF content
        logger.info("PDFContentExtractor initialized")
    
    def get_class_for_age(self, age: int) -> str:
        """
        Map user age to appropriate class/PDF
        
        Args:
            age: User's age in years
        
        Returns:
            Class name (e.g., "Class_7th")
        """
        # Use the AGE_TO_CLASS mapping, default to Class_10th for higher ages
        return AGE_TO_CLASS.get(age, "Class_10th")
    
    def get_pdf_path(self, class_name: str) -> Optional[Path]:
        """
        Get full path to PDF file for a class
        
        Args:
            class_name: Class name (e.g., "Class_6th")
        
        Returns:
            Path to PDF file or None if not found
        """
        pdf_file = PDF_DIR / f"{class_name}.pdf"
        if pdf_file.exists():
            return pdf_file
        else:
            logger.warning(f"PDF not found: {pdf_file}")
            return None
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract all text from PDF file
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text content
        """
        try:
            if not PyPDF2:
                logger.warning("PyPDF2 not installed. Cannot extract PDF content.")
                return ""
            
            text_content = ""
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                logger.info(f"Extracting text from {num_pages} pages of {pdf_path.name}")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text()
            
            return text_content
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_topics_from_content(self, content: str) -> List[str]:
        """
        Extract topic headings from PDF content
        Looks for chapter/lesson patterns and financial education topics
        
        Args:
            content: Extracted PDF text
        
        Returns:
            List of topic names
        """
        topics = []
        
        # Normalize content: remove excessive whitespace, fix line breaks
        content = re.sub(r'\n\s+', '\n', content)  # Remove leading spaces after newlines
        content = re.sub(r'([a-z])\n([a-z])', r'\1 \2', content)  # Join broken words
        content = re.sub(r'\n+', '\n', content)  # Remove multiple newlines
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines, very short/long lines
            if not line or len(line) < 5 or len(line) > 120:
                continue
            
            # Skip pure numbers or common metadata
            if line.isdigit() or any(skip in line.lower() for skip in 
                    ['cbse', 'isbn', '©', 'edition', 'printed by', 'published by']):
                continue
            
            # Skip common metadata/narrative phrases
            if any(skip in line.lower() for skip in 
                    ['advisory', 'monitoring', 'editing', 'board', 'geography', 'history',
                     'english', 'subject', 'index', 'page no', 'shiksha kendra', 'part i:', 
                     'part ii:', 'let\'s learn', 'can we', 'will tell', 'how to open',
                     'advisor', 'body', 'class:', 'workb']):
                continue
            
            is_topic = False
            topic_text = line
            
            # Pattern 1: Chapter X - Title format
            chapter_match = re.match(r'chapter\s+\d+\s*[:-]\s*(.+)', line, re.IGNORECASE)
            if chapter_match:
                topic_text = chapter_match.group(1).strip()
                is_topic = True
            
            # Pattern 2: Lesson/Unit/Module X - Title
            elif re.match(r'(lesson|unit|module|section)\s+\d+\s*[:-]?\s*(.+)', line, re.IGNORECASE):
                match = re.match(r'(lesson|unit|module|section)\s+\d+\s*[:-]?\s*(.+)', line, re.IGNORECASE)
                if match:
                    topic_text = match.group(2).strip()
                    is_topic = True
            
            # Pattern 3: ALL CAPS headings (but not too short, avoid metadata)
            elif (line.isupper() and len(line) > 8 and len(line.split()) >= 2 and
                  not any(skip in line for skip in ['ADVISOR', 'BODY', 'INDEX', 'CBSE', 'CLASS'])):
                is_topic = True
            
            # Pattern 4: Lines with common financial keywords
            if not is_topic:
                financial_keywords = [
                    'banking', 'account', 'saving', 'investment', 'credit', 'debit', 'loan',
                    'interest', 'insurance', 'budget', 'planning', 'share', 'stock', 'equity',
                    'income', 'expense', 'transaction', 'payment', 'cheque', 'atm', 'card'
                ]
                
                line_lower = line.lower()
                for keyword in financial_keywords:
                    if keyword in line_lower:
                        word_count = len(line.split())
                        has_question = '?' in line
                        
                        # Good topic if: title case, 2-5 words, no questions
                        if (2 <= word_count <= 5 and not has_question and 
                            line[0].isupper() and not line.endswith('.')):
                            is_topic = True
                            topic_text = line
                        break
            
            # Add to topics if valid
            if is_topic and topic_text:
                # Normalize the text: remove extra spaces, special cleanup
                topic_text = re.sub(r'\s+', ' ', topic_text).strip()
                
                # Remove common noise patterns
                topic_text = re.sub(r'^(part [ivx]+:|what is a )', '', topic_text, flags=re.IGNORECASE).strip()
                
                # Validate length and uniqueness
                if (len(topic_text) >= 5 and len(topic_text) < 80 and
                    topic_text not in topics and 
                    not any(t.lower() == topic_text.lower() for t in topics)):
                    topics.append(topic_text)
        
        # If still too few topics, try keyword extraction as backup
        if len(topics) < 5:
            logger.info(f"Found only {len(topics)} structured topics, using keyword extraction")
            topics.extend(self._extract_topics_by_keywords(content, limit=8))
        
        # Deduplicate and limit
        topics = list(dict.fromkeys(topics))
        
        logger.info(f"Extracted {len(topics)} topics from PDF content")
        return topics[:15]
    
    def _extract_topics_by_keywords(self, content: str, limit: int = 10) -> List[str]:
        """
        Extract topics by looking for financial education keywords
        Fallback method when structure-based extraction yields few results
        
        Args:
            content: Extracted PDF text
            limit: Maximum number of keywords to return
        
        Returns:
            List of keywords/topics found
        """
        # Common financial education topics from various curricula
        financial_keywords = [
            'understanding money', 'earning and income', 'spending and budgeting',
            'saving for the future', 'lending and borrowing', 'investment',
            'banking and banking services', 'insurance', 'planning and managing life events',
            'financial fraud', 'digital financial services', 'taxation',
            'credit and debt', 'compound interest', 'inflation', 'risk and return',
            'financial products', 'banking basics', 'consumer protection',
            'financial literacy', 'mutual funds', 'stocks and bonds'
        ]
        
        found_keywords = []
        content_lower = content.lower()
        
        for keyword in financial_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword.title())
        
        return found_keywords[:limit]
    
    def get_topics_for_age(self, age: int) -> List[str]:
        """
        Get topics from PDF corresponding to user's age/class
        
        Args:
            age: User's age
        
        Returns:
            List of topics from the appropriate PDF
        """
        try:
            # Map age to class
            class_name = self.get_class_for_age(age)
            pdf_path = self.get_pdf_path(class_name)
            
            if not pdf_path:
                logger.warning(f"PDF not found for class {class_name}")
                return []
            
            # Check cache first
            if pdf_path in self.pdf_cache:
                content = self.pdf_cache[pdf_path]
            else:
                # Extract text from PDF
                content = self.extract_text_from_pdf(pdf_path)
                if not content:
                    logger.warning(f"No content extracted from {pdf_path}")
                    return []
                
                # Cache the content
                self.pdf_cache[pdf_path] = content
            
            # Extract topics from content
            topics = self.extract_topics_from_content(content)
            
            logger.info(f"Retrieved {len(topics)} topics for age {age} from {class_name}")
            return topics
            
        except Exception as e:
            logger.error(f"Error getting topics for age {age}: {e}")
            return []
    
    def get_content_for_topic(self, age: int, topic: str) -> str:
        """
        Get content from PDF for a specific topic
        Finds sections of PDF that mention the topic using keyword matching
        
        Args:
            age: User's age
            topic: Topic name to find
        
        Returns:
            Relevant content from PDF (up to 4000 chars)
        """
        try:
            class_name = self.get_class_for_age(age)
            pdf_path = self.get_pdf_path(class_name)
            
            if not pdf_path:
                logger.warning(f"No PDF path for age {age}")
                return ""
            
            # Get or extract content
            if pdf_path in self.pdf_cache:
                content = self.pdf_cache[pdf_path]
            else:
                content = self.extract_text_from_pdf(pdf_path)
                self.pdf_cache[pdf_path] = content
            
            if not content:
                logger.warning(f"No content in PDF for age {age}")
                return ""
            
            # Extract keywords from topic for better matching
            topic_words = [word.lower().strip() for word in topic.split() if len(word.strip()) > 2]
            
            # Split content into lines and find sections related to the topic
            lines = content.split('\n')
            relevant_sections = []
            current_section = []
            found_match = False
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Check if this line contains topic keywords
                line_lower = line_stripped.lower()
                has_topic_match = any(word in line_lower for word in topic_words)
                
                # If we find a section with the topic, collect it and surrounding context
                if has_topic_match:
                    # Include previous 2 lines as context
                    if current_section:
                        start_idx = max(0, len(current_section) - 2)
                        context = current_section[start_idx:]
                    else:
                        context = lines[max(0, i - 2):i]
                    
                    # Collect this section and next 10 lines
                    section_content = []
                    if context:
                        section_content.extend([l.strip() for l in context if l.strip()])
                    
                    section_content.append(line_stripped)
                    
                    # Add next 10 lines for complete context
                    for j in range(i + 1, min(i + 10, len(lines))):
                        next_line = lines[j].strip()
                        if next_line:
                            section_content.append(next_line)
                        # Stop if we hit another section heading (all caps line)
                        if next_line and next_line.isupper() and len(next_line) > 5:
                            break
                    
                    relevant_sections.append('\n'.join(section_content))
                    found_match = True
                
                # Keep current section for context
                if line_stripped:
                    current_section.append(line_stripped)
                else:
                    current_section = []
            
            # Combine all relevant sections
            if found_match:
                relevant_content = '\n\n'.join(relevant_sections)
                logger.info(f"Found {len(relevant_content)} chars of content for topic: {topic}")
                return relevant_content[:4000]  # Return up to 4000 chars
            
            # If no exact match found, search for similar keywords
            logger.warning(f"No direct match for topic '{topic}', searching for related content...")
            
            # Try to find content with partial keyword matches
            partial_match_sections = []
            current_section_lines = []
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Match if at least one word from topic is in the line
                if line_stripped and any(word in line_stripped.lower() for word in topic_words):
                    if not current_section_lines:
                        # Start of a new section with matches
                        current_section_lines = [line_stripped]
                    else:
                        current_section_lines.append(line_stripped)
                elif current_section_lines and len(current_section_lines) > 3:
                    # End of section with enough content
                    partial_match_sections.append('\n'.join(current_section_lines))
                    current_section_lines = []
                elif current_section_lines:
                    # Continue building section if less than 3 lines
                    current_section_lines.append(line_stripped)
            
            if current_section_lines:
                partial_match_sections.append('\n'.join(current_section_lines))
            
            if partial_match_sections:
                partial_content = '\n\n'.join(partial_match_sections)
                logger.info(f"Found {len(partial_content)} chars using partial matching for topic: {topic}")
                return partial_content[:4000]
            
            # Final fallback: return general class content
            logger.warning(f"No matching content found for topic '{topic}', using general class content")
            return content[:4000]
            
        except Exception as e:
            logger.error(f"Error getting content for topic {topic}: {e}", exc_info=True)
            return ""
    
    def get_full_class_content(self, age: int) -> str:
        """
        Get full text content from class PDF
        
        Args:
            age: User's age
        
        Returns:
            Full PDF content
        """
        try:
            class_name = self.get_class_for_age(age)
            pdf_path = self.get_pdf_path(class_name)
            
            if not pdf_path:
                return ""
            
            # Check cache first
            if pdf_path in self.pdf_cache:
                return self.pdf_cache[pdf_path]
            
            # Extract and cache
            content = self.extract_text_from_pdf(pdf_path)
            self.pdf_cache[pdf_path] = content
            
            return content
            
        except Exception as e:
            logger.error(f"Error getting class content: {e}")
            return ""
    
    def get_class_info(self, age: int) -> Dict[str, Any]:
        """
        Get information about the class for a given age
        
        Args:
            age: User's age
        
        Returns:
            Dictionary with class info
        """
        class_name = self.get_class_for_age(age)
        pdf_path = self.get_pdf_path(class_name)
        
        return {
            "class": class_name,
            "age_range": CLASS_AGE_RANGES.get(class_name, (0, 0)),
            "pdf_path": str(pdf_path) if pdf_path else None,
            "pdf_exists": pdf_path.exists() if pdf_path else False
        }
