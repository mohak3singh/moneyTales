"""
Text Chunking Service
Splits documents into semantic chunks for embedding
"""

import logging
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)

TEXT_DIR = Path(__file__).parent.parent.parent / "data" / "text"


class ChunkingService:
    """Handle text chunking for RAG"""

    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        """
        Initialize chunking service
        chunk_size: Number of characters per chunk
        chunk_overlap: Overlap between chunks for context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        Uses simple character-based chunking
        """
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - self.chunk_overlap

        return [c for c in chunks if len(c) > 50]  # Filter out too-small chunks

    def chunk_by_paragraphs(self, text: str) -> List[str]:
        """
        Split text by paragraphs while maintaining context
        Better for structured content
        """
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def chunk_by_sections(self, text: str) -> List[str]:
        """
        Split text by section headers (for educational content)
        Preserves semantic structure
        """
        lines = text.split("\n")
        chunks = []
        current_chunk = ""

        for line in lines:
            # Check if line is a header (contains ==== or ####)
            is_header = "====" in line or "----" in line or line.startswith("#")

            if is_header and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"

                if len(current_chunk) > self.chunk_size:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

        if current_chunk:
            chunks.append(current_chunk.strip())

        return [c for c in chunks if len(c) > 30]

    def process_all_documents(self) -> List[dict]:
        """
        Process all text documents and return chunks with metadata
        """
        all_chunks = []
        
        TEXT_DIR.mkdir(parents=True, exist_ok=True)
        
        text_files = list(TEXT_DIR.glob("*.txt"))
        
        if not text_files:
            logger.warning("No text files found for chunking")
            return []

        for text_file in text_files:
            try:
                with open(text_file, "r", encoding="utf-8") as f:
                    text = f.read()

                # Use section-based chunking for educational content
                chunks = self.chunk_by_sections(text)

                for i, chunk in enumerate(chunks):
                    all_chunks.append({
                        "id": f"{text_file.stem}_{i}",
                        "content": chunk,
                        "source": text_file.name,
                        "chunk_index": i
                    })

                logger.info(f"Chunked {text_file.name} into {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Error processing {text_file.name}: {e}")

        return all_chunks
