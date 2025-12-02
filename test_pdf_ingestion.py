#!/usr/bin/env python3
"""
Test script to verify PDF ingestion and RAG system
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_pdf_ingestion():
    """Test PDF ingestion pipeline"""
    print("\n" + "="*60)
    print("🧪 TESTING PDF INGESTION PIPELINE")
    print("="*60)
    
    from services.pdf_ingestion import PDFIngestion
    
    print("\n1️⃣ Starting PDF ingestion...")
    processed_files = PDFIngestion.ingest_pdfs()
    
    print(f"\n✅ Ingestion complete!")
    print(f"📄 Processed files: {len(processed_files)}")
    for f in processed_files:
        file_path = Path(f)
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   • {file_path.name} ({size:,} bytes)")
    
    return processed_files

def test_chunking(processed_files):
    """Test document chunking"""
    print("\n" + "="*60)
    print("🔪 TESTING DOCUMENT CHUNKING")
    print("="*60)
    
    from services.chunker import ChunkingService
    
    chunker = ChunkingService()
    all_chunks = []
    for file_path in processed_files:
        print(f"\n2️⃣ Chunking {Path(file_path).name}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = chunker.chunk_text(content)
        all_chunks.extend(chunks)
        print(f"✅ Created {len(chunks)} chunks")
        if chunks:
            print(f"   Sample chunk (first 100 chars): {chunks[0][:100]}...")
    
    print(f"\n📊 Total chunks created: {len(all_chunks)}")
    return all_chunks

def test_vectorization(chunks):
    """Test vector embeddings"""
    print("\n" + "="*60)
    print("📊 TESTING VECTOR EMBEDDINGS")
    print("="*60)
    
    from services.vectorstore import VectorStore
    
    print(f"\n3️⃣ Creating vectors from {len(chunks)} chunks...")
    vectorstore = VectorStore()
    vectorstore.add_documents(chunks)
    
    print(f"✅ Vector store initialized")
    print(f"   Total documents in store: {len(vectorstore.documents)}")
    print(f"   Embedding dimension: {len(vectorstore.embeddings[0]) if vectorstore.embeddings else 'N/A'}")
    
    return vectorstore

def test_rag_search(vectorstore):
    """Test RAG search"""
    print("\n" + "="*60)
    print("🔍 TESTING RAG SEARCH")
    print("="*60)
    
    test_queries = [
        "What is saving money?",
        "How does compound interest work?",
        "What is a budget?",
        "What are investments?"
    ]
    
    print(f"\n4️⃣ Testing search queries...")
    for query in test_queries:
        results = vectorstore.search(query, top_k=2)
        print(f"\n📌 Query: '{query}'")
        print(f"   Found {len(results)} results:")
        for i, (doc, score) in enumerate(results, 1):
            print(f"      {i}. Score: {score:.3f}")
            print(f"         {doc[:80]}...")

def main():
    """Run all tests"""
    try:
        # Test 1: PDF Ingestion
        processed_files = test_pdf_ingestion()
        
        if not processed_files:
            print("\n❌ No PDF files processed!")
            return False
        
        # Test 2: Chunking
        chunks = test_chunking(processed_files)
        
        if not chunks:
            print("\n❌ No chunks created!")
            return False
        
        # Test 3: Vectorization
        vectorstore = test_vectorization(chunks)
        
        if not vectorstore.embeddings:
            print("\n❌ Vector embeddings failed!")
            return False
        
        # Test 4: RAG Search
        test_rag_search(vectorstore)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED! RAG SYSTEM IS READY")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
