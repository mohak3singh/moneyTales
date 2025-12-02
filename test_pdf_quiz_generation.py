#!/usr/bin/env python3
"""
Test PDF-based quiz generation flow
Tests: PDF extraction → Topic selection → Question generation
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.pdf_content_extractor import PDFContentExtractor
from backend.services.pdf_question_generator import PDFBasedQuestionGenerator
from backend.services.topic_suggester import TopicSuggester


def test_pdf_extraction():
    """Test PDF content extraction"""
    print("\n" + "="*60)
    print("TEST 1: PDF Content Extraction")
    print("="*60)
    
    extractor = PDFContentExtractor()
    
    # Test for each age
    ages = [11, 12, 13, 14, 15, 16]
    for age in ages:
        class_name = extractor.get_class_for_age(age)
        topics = extractor.get_topics_for_age(age)
        print(f"\nAge {age} → {class_name}")
        print(f"  Topics found: {len(topics)}")
        if topics:
            print(f"  First 3 topics:")
            for topic in topics[:3]:
                print(f"    - {topic}")


def test_topic_suggestions():
    """Test topic suggester with PDF extraction"""
    print("\n" + "="*60)
    print("TEST 2: Topic Suggestions (PDF-based)")
    print("="*60)
    
    suggester = TopicSuggester()
    
    ages = [11, 13, 15]
    for age in ages:
        print(f"\nAge {age}:")
        try:
            topics = suggester.get_topics_for_age(age)
            print(f"  Suggested {len(topics)} topics:")
            for i, topic in enumerate(topics[:5], 1):
                print(f"    {i}. {topic}")
        except Exception as e:
            print(f"  Error: {e}")


def test_question_generation():
    """Test question generation from PDF content"""
    print("\n" + "="*60)
    print("TEST 3: Question Generation from PDF")
    print("="*60)
    
    generator = PDFBasedQuestionGenerator()
    
    # Test with age 12 and a specific topic
    age = 12
    topic = "Banking"
    
    print(f"\nGenerating questions for Age {age}, Topic: {topic}")
    try:
        questions = generator.generate_questions_for_topic(
            age=age,
            topic=topic,
            num_questions=2,
            user_hobbies="sports, reading"
        )
        
        if questions:
            print(f"Generated {len(questions)} questions")
            for i, q in enumerate(questions, 1):
                print(f"\nQuestion {i}:")
                print(f"  Q: {q.get('question', 'N/A')}")
                print(f"  Options: {q.get('options', [])}")
                print(f"  Correct: {q.get('correct_answer', 'N/A')}")
                print(f"  Explanation: {q.get('explanation', 'N/A')[:100]}...")
        else:
            print("No questions generated")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_content_for_topic():
    """Test retrieving content for a specific topic"""
    print("\n" + "="*60)
    print("TEST 4: Content Retrieval for Topic")
    print("="*60)
    
    extractor = PDFContentExtractor()
    
    age = 12
    topics = extractor.get_topics_for_age(age)
    
    if topics:
        topic = topics[1] if len(topics) > 1 else topics[0]
        print(f"\nAge {age}, Topic: {topic}")
        
        content = extractor.get_content_for_topic(age, topic)
        if content:
            print(f"Content length: {len(content)} characters")
            print(f"Content preview:\n{content[:300]}...")
        else:
            print("No content found for topic")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PDF-Based Quiz Generation System - Test Suite")
    print("="*60)
    
    try:
        test_pdf_extraction()
        test_topic_suggestions()
        test_content_for_topic()
        test_question_generation()
        
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
