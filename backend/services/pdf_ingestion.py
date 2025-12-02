"""
PDF Ingestion Service
Extracts text from PDFs and stores in text files
"""

import os
import logging
from pathlib import Path
from typing import List
import shutil

logger = logging.getLogger(__name__)

# Source PDF location (actual financial education PDFs)
CONTENT_PDF_DIR = Path("/Users/mohak@backbase.com/Projects/Internal hackathon/content/financial-education-pdfs")

# Project data directories
PROJECT_ROOT = Path(__file__).parent.parent.parent
PDF_DIR = PROJECT_ROOT / "data" / "pdfs"
TEXT_DIR = PROJECT_ROOT / "data" / "text"


class PDFIngestion:
    """Handle PDF to text conversion"""

    @staticmethod
    def ingest_pdfs() -> List[str]:
        """
        Ingest PDFs from content directory
        Copies PDFs to project data/pdfs and extracts text
        Returns list of processed file paths
        """
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        TEXT_DIR.mkdir(parents=True, exist_ok=True)
        processed_files = []

        try:
            # Check if source directory exists
            if not CONTENT_PDF_DIR.exists():
                logger.warning(f"Content PDF directory not found: {CONTENT_PDF_DIR}")
                PDFIngestion._create_sample_content()
                return [str(TEXT_DIR / "sample_financial_content.txt")]

            # Get all PDF files from source
            pdf_files = list(CONTENT_PDF_DIR.glob("*.pdf"))
            
            if not pdf_files:
                logger.warning(f"No PDF files found in {CONTENT_PDF_DIR}")
                PDFIngestion._create_sample_content()
                return [str(TEXT_DIR / "sample_financial_content.txt")]

            logger.info(f"Found {len(pdf_files)} PDF files to ingest")

            for pdf_file in pdf_files:
                try:
                    # Copy PDF to project directory
                    dest_pdf = PDF_DIR / pdf_file.name
                    shutil.copy2(pdf_file, dest_pdf)
                    logger.info(f"Copied {pdf_file.name} to {dest_pdf}")
                    
                    # Extract text from PDF
                    text_file = TEXT_DIR / f"{pdf_file.stem}.txt"
                    extracted_text = PDFIngestion._extract_text_from_pdf(str(dest_pdf))
                    
                    if extracted_text:
                        with open(text_file, "w", encoding="utf-8") as f:
                            f.write(extracted_text)
                        processed_files.append(str(text_file))
                        logger.info(f"Extracted text from {pdf_file.name} ({len(extracted_text)} chars)")
                    else:
                        logger.warning(f"No text extracted from {pdf_file.name}")
                        
                except Exception as e:
                    logger.error(f"Error processing {pdf_file.name}: {e}")

            if not processed_files:
                logger.warning("No PDFs successfully processed, creating sample content")
                PDFIngestion._create_sample_content()
                return [str(TEXT_DIR / "sample_financial_content.txt")]

            return processed_files
            
        except Exception as e:
            logger.error(f"Error in PDF ingestion: {e}")
            PDFIngestion._create_sample_content()
            return [str(TEXT_DIR / "sample_financial_content.txt")]

    @staticmethod
    def _extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract text from PDF file
        Tries PyPDF2 first, falls back to simple text extraction
        """
        try:
            import PyPDF2
            
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                logger.info(f"Extracting from PDF with {num_pages} pages")
                
                for page_num in range(min(num_pages, 50)):  # Limit to first 50 pages
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                    text += "\n\n"
            
            return text if text.strip() else None
            
        except ImportError:
            logger.warning("PyPDF2 not installed, using fallback method")
            return PDFIngestion._fallback_text_extraction(pdf_path)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return PDFIngestion._fallback_text_extraction(pdf_path)

    @staticmethod
    def _fallback_text_extraction(pdf_path: str) -> str:
        """Fallback text extraction method"""
        try:
            # Try pdfplumber if available
            import pdfplumber
            
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages[:50]):  # Limit to first 50 pages
                    try:
                        text += page.extract_text()
                        text += "\n\n"
                    except:
                        continue
            
            return text if text.strip() else None
            
        except ImportError:
            logger.warning("pdfplumber not installed, creating sample content")
            return None

    @staticmethod
    def _create_sample_content():
        """Create sample financial education content for demo"""
        sample_content = """
FINANCIAL LITERACY FOR KIDS - COMPREHENSIVE GUIDE

CHAPTER 1: UNDERSTANDING MONEY
================================
Money is a medium of exchange that represents value. 
Kids should learn about:
- The history of currency
- Different types of money (coins, paper, digital)
- Value and purchasing power

Key Concepts:
- Money is earned through work
- Money can be saved or spent
- Different countries have different currencies

CHAPTER 2: EARNING MONEY
========================
Ways kids can earn money:
1. Allowance from parents
2. Chores and tasks
3. Starting a small business
4. Babysitting or pet sitting
5. Seasonal work

Age-appropriate earnings:
- Ages 8-10: Chores, allowance ($5-20/week)
- Ages 11-13: Babysitting, lawn work ($50-100/month)
- Ages 14+: Part-time jobs, freelancing

CHAPTER 3: SAVING MONEY
=======================
Importance of saving:
- Security and emergency funds
- Goals and dreams
- Interest earning
- Financial independence

Saving strategies:
- Use a piggy bank or savings account
- Set savings goals
- Track your progress
- Avoid impulse purchases

The power of compound interest:
If you save $50/month at 5% interest:
- 1 year: $612
- 5 years: $3,200
- 10 years: $7,700

CHAPTER 4: SPENDING WISELY
===========================
Smart spending habits:
1. Make a shopping list
2. Compare prices
3. Wait 24 hours before big purchases
4. Understand needs vs wants
5. Look for discounts and sales

Budgeting basics:
- Track income
- List expenses
- Allocate percentages (50% needs, 30% wants, 20% savings)

CHAPTER 5: BASIC INVESTMENTS
=============================
Introduction to investments:
- Stocks: Owning part of a company
- Bonds: Lending money to earn interest
- Mutual funds: Diversified investments
- Real estate: Owning property

Investment risks and rewards:
- Higher risk = higher potential returns
- Diversification reduces risk
- Time horizon matters

CHAPTER 6: FINANCIAL GOALS
===========================
Setting SMART goals:
- Specific: Clear and detailed
- Measurable: Track progress
- Achievable: Realistic
- Relevant: Important to you
- Time-bound: Has a deadline

Examples:
- Save $100 for a bike by summer
- Build emergency fund of $500 in 6 months
- Invest $50/month for college

CHAPTER 7: COMMON MONEY MISTAKES
================================
Mistakes to avoid:
1. Overspending on impulse
2. Not saving anything
3. Borrowing without understanding debt
4. Ignoring financial goals
5. Not learning from mistakes

Solutions:
- Use checklists before spending
- Automate savings
- Understand interest and fees
- Review goals monthly

CHAPTER 8: INTRODUCTION TO CREDIT
==================================
What is credit?
- Borrowed money that must be repaid
- Has an associated interest rate
- Builds credit history
- Important for future loans

Credit score factors:
- Payment history (35%)
- Credit utilization (30%)
- Length of history (15%)
- Credit mix (10%)
- New inquiries (10%)

CHAPTER 9: ENTREPRENEURSHIP FOR KIDS
=====================================
Starting a small business:
1. Identify a need or skill
2. Plan your business
3. Set prices
4. Market your service
5. Deliver quality work

Business ideas for kids:
- Tutoring younger students
- Dog walking service
- Car washing
- Lawn care
- Content creation
- Reselling items

CHAPTER 10: FINANCIAL INDEPENDENCE
===================================
Long-term financial planning:
- Education and skill development
- Career planning
- Retirement savings
- Insurance needs
- Estate planning

The path to financial independence:
- Live below your means
- Invest consistently
- Build multiple income streams
- Continuous learning
- Help others

KEY TAKEAWAYS
=============
1. Money is earned through work and effort
2. Save consistently for future goals
3. Spend wisely by distinguishing needs from wants
4. Understand the power of compound interest
5. Start learning finance young for better outcomes
6. Make mistakes early while stakes are low
7. Develop good financial habits for life
8. Think about long-term financial independence
        """
        
        text_file = TEXT_DIR / "sample_financial_content.txt"
        text_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(text_file, "w") as f:
            f.write(sample_content)
        
        logger.info(f"Created sample financial content at {text_file}")
