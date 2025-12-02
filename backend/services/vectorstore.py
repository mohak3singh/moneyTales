"""
Vector Store Service
Manages embeddings and similarity search using FAISS or simple in-memory store
"""

import json
import logging
import pickle
from typing import List, Dict, Any
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

EMBEDDINGS_DIR = Path(__file__).parent.parent.parent / "data" / "embeddings"


class VectorStore:
    """
    Simple in-memory vector store for MVP
    In production, use FAISS or Pinecone
    """

    def __init__(self):
        """Initialize vector store"""
        self.vectors = {}  # id -> embedding
        self.metadata = {}  # id -> metadata
        self.embeddings_dir = EMBEDDINGS_DIR
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

    def add_documents(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Add chunked documents to vector store
        chunks: List of dicts with 'id', 'content', 'source', 'chunk_index'
        """
        added_count = 0

        for chunk in chunks:
            try:
                # Simple embedding: use character frequency (for MVP)
                embedding = self._simple_embedding(chunk["content"])
                
                self.vectors[chunk["id"]] = embedding
                self.metadata[chunk["id"]] = {
                    "content": chunk["content"],
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"]
                }
                added_count += 1

            except Exception as e:
                logger.error(f"Error adding document {chunk['id']}: {e}")

        logger.info(f"Added {added_count} documents to vector store")
        return added_count

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        Returns top_k most relevant chunks
        """
        if not self.vectors:
            logger.warning("Vector store is empty")
            return []

        try:
            query_embedding = self._simple_embedding(query)
            scores = {}

            # Calculate cosine similarity with all vectors
            for doc_id, vector in self.vectors.items():
                similarity = self._cosine_similarity(query_embedding, vector)
                scores[doc_id] = similarity

            # Sort by similarity and return top_k
            top_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

            results = []
            for doc_id, score in top_docs:
                results.append({
                    "id": doc_id,
                    "content": self.metadata[doc_id]["content"],
                    "source": self.metadata[doc_id]["source"],
                    "similarity_score": float(score)
                })

            return results
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []

    def _simple_embedding(self, text: str) -> np.ndarray:
        """
        Create simple embedding from text (MVP approach)
        In production, use OpenAI embeddings or sentence-transformers
        
        This uses character frequency as a proxy embedding
        """
        # Simple approach: create a sparse vector from character frequencies
        # Limited to common financial terms for efficiency
        
        financial_terms = [
            "money", "save", "spend", "earn", "invest", "budget", "credit",
            "debt", "interest", "goal", "bank", "account", "stock", "bond",
            "profit", "loss", "income", "expense", "financial", "wealth",
            "rich", "poor", "buy", "sell", "trade", "price", "value",
            "kid", "child", "education", "learn", "understand", "financial literacy",
            "smart", "wise", "future", "plan", "goal", "business", "work"
        ]

        # Create embedding vector based on term frequency
        embedding = np.zeros(len(financial_terms))
        text_lower = text.lower()

        for i, term in enumerate(financial_terms):
            embedding[i] = text_lower.count(term)

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def save(self, filepath: str = None):
        """Save vector store to disk"""
        if filepath is None:
            filepath = self.embeddings_dir / "vectorstore.pkl"

        try:
            with open(filepath, "wb") as f:
                pickle.dump({
                    "vectors": self.vectors,
                    "metadata": self.metadata
                }, f)
            logger.info(f"Vector store saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")

    def load(self, filepath: str = None):
        """Load vector store from disk"""
        if filepath is None:
            filepath = self.embeddings_dir / "vectorstore.pkl"

        try:
            if Path(filepath).exists():
                with open(filepath, "rb") as f:
                    data = pickle.load(f)
                    self.vectors = data["vectors"]
                    self.metadata = data["metadata"]
                logger.info(f"Vector store loaded from {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
