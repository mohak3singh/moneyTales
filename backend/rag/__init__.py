"""
RAG Module Initialization
Coordinates PDF ingestion, chunking, and vector storage
"""

from backend.services.pdf_ingestion import PDFIngestion
from backend.services.chunker import ChunkingService
from backend.services.vectorstore import VectorStore


class RAGManager:
    """
    Manages the complete RAG pipeline:
    PDFs -> Text -> Chunks -> Vectors -> Search
    """

    def __init__(self):
        self.vector_store = VectorStore()
        self.chunking_service = ChunkingService(chunk_size=400, chunk_overlap=50)

    def initialize(self):
        """
        Initialize RAG system:
        1. Ingest PDFs to text files
        2. Chunk documents
        3. Create embeddings
        """
        # Step 1: Ingest PDFs
        PDFIngestion.ingest_pdfs()

        # Step 2: Chunk documents
        chunks = self.chunking_service.process_all_documents()

        # Step 3: Add to vector store
        if chunks:
            self.vector_store.add_documents(chunks)
            self.vector_store.save()

        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> list:
        """
        Search for relevant documents
        query: Question or topic
        top_k: Number of results to return
        """
        return self.vector_store.search(query, top_k)

    def get_context(self, topic: str) -> str:
        """
        Get context for a specific topic
        Returns concatenated relevant chunks
        """
        results = self.search(topic, top_k=3)
        context = "\n\n---\n\n".join([r["content"] for r in results])
        return context
