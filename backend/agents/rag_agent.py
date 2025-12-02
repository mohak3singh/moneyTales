"""
RAG Agent
Retrieves relevant financial knowledge from the knowledge base
"""

import logging
from typing import Dict, Any
from .base_agent import Agent

logger = logging.getLogger(__name__)


class RAGAgent(Agent):
    """Retrieves context from the RAG knowledge base"""

    def __init__(self, rag_manager):
        """
        Initialize RAG Agent
        rag_manager: RAGManager instance for vector search
        """
        super().__init__("RAGAgent")
        self.rag_manager = rag_manager

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Retrieve relevant context for a topic
        
        Args:
            query: str - the topic or question to search for
            top_k: int - number of results to return (default 5)
        
        Returns:
            dict with retrieved documents and context
        """
        try:
            query = kwargs.get("query", "")
            top_k = kwargs.get("top_k", 5)

            if not query:
                return {
                    "status": "error",
                    "error": "No query provided",
                    "agent": self.name
                }

            self.log_execution("RAG Retrieval", "started", {"query": query})

            # Search vector store
            results = self.rag_manager.search(query, top_k=top_k)

            # Prepare context
            context = self._prepare_context(results)

            return {
                "status": "success",
                "query": query,
                "results_count": len(results),
                "context": context,
                "documents": results,
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"Error in RAGAgent: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }

    def _prepare_context(self, results: list) -> str:
        """Combine retrieved documents into a context string"""

        if not results:
            return "No relevant information found."

        context_parts = []
        for i, result in enumerate(results[:3]):  # Use top 3
            context_parts.append(result.get("content", ""))

        return "\n\n---\n\n".join(context_parts)
