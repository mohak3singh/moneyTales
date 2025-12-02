# RAG (Retrieval-Augmented Generation) Implementation

## Current Vector Database Solution

**YES**, we ARE using a vector database, but it's a **lightweight MVP implementation**.

### Current Implementation: Simple In-Memory Vector Store

**File**: `backend/services/vectorstore.py`

**Architecture**:
```
PDF Documents
    ↓
PDF Ingestion (pdf_ingestion.py)
    ↓
Text Chunking (chunker.py)
    ↓
Vector Store (vectorstore.py)
    ├─ Vectors: Dictionary of embeddings
    ├─ Metadata: Document info (content, source, chunk_index)
    └─ Persistence: Pickle file storage
    ↓
RAG Search (RAGAgent)
    ↓
Results returned to query
```

## Components

### 1. Vector Store (`VectorStore` class)

**What it does**:
- Stores document embeddings in memory
- Performs similarity search using cosine similarity
- Saves/loads from disk using pickle

**Data Structure**:
```python
vectors = {
    "doc_id_1": np.array([0.1, 0.2, 0.3, ...]),
    "doc_id_2": np.array([0.15, 0.25, 0.35, ...]),
    ...
}

metadata = {
    "doc_id_1": {
        "content": "The actual chunk text...",
        "source": "Class_7th.pdf",
        "chunk_index": 0
    },
    ...
}
```

### 2. Embedding Strategy (MVP)

**Current Approach**: Character Frequency Embedding
- Uses 40 pre-defined financial keywords
- Creates a frequency vector for each document
- Normalizes using L2 norm

**Financial Keywords Tracked**:
```
money, save, spend, earn, invest, budget, credit, debt, interest, goal, bank, 
account, stock, bond, profit, loss, income, expense, financial, wealth, 
rich, poor, buy, sell, trade, price, value, kid, child, education, learn, 
understand, financial literacy, smart, wise, future, plan, business, work
```

**Why This Approach**:
✓ Fast (no external API calls)
✓ No GPU needed
✓ Works offline
✓ Sufficient for MVP
✗ Not as accurate as ML-based embeddings

### 3. Search Process

**Cosine Similarity Search**:
1. Convert query to embedding (same keyword frequency method)
2. Calculate cosine similarity with all stored vectors
3. Sort by similarity score
4. Return top_k results with highest similarity

**Example**:
```
Query: "How to save money?"
Keywords found: ["save" (1), "money" (1)]
Embedding: [0.0, 0.5, 0.0, ..., 0.5, 0.0, ...]

Search Result:
- Document 1: similarity = 0.89 ✓
- Document 2: similarity = 0.72
- Document 3: similarity = 0.65
```

### 4. Persistence

**Storage**: `/Users/mohak@backbase.com/Projects/Internal hackathon/MoneyTales/data/embeddings/vectorstore.pkl`

**Save/Load Operations**:
```python
vector_store.save()  # Saves to vectorstore.pkl
vector_store.load()  # Loads from vectorstore.pkl
```

## RAG Agent Integration

**File**: `backend/agents/rag_agent.py`

**Usage**:
```python
rag_agent.execute(
    query="How do I save money?",
    top_k=5
)

Returns:
{
    "status": "success",
    "query": "How do I save money?",
    "results_count": 5,
    "context": "Combined context from top 3 results",
    "documents": [
        {
            "id": "doc_1",
            "content": "Content of the document chunk",
            "source": "Class_7th.pdf",
            "similarity_score": 0.89
        },
        ...
    ]
}
```

## Pipeline Flow

```
1. PDF INGESTION (pdf_ingestion.py)
   ↓
   - Extract text from PDFs
   - Store in data/pdfs/ folder
   
2. TEXT CHUNKING (chunker.py)
   ↓
   - Split content into chunks
   - Add metadata (source, chunk_index)
   
3. VECTORIZATION (vectorstore.py)
   ↓
   - Create embeddings using keyword frequency
   - Store in memory + pickle file
   
4. SEARCH (RAGAgent)
   ↓
   - User query converted to embedding
   - Cosine similarity search
   - Top-k results returned
```

## Production Improvements

### Option 1: FAISS (Local Vector Database)
```python
# More efficient than in-memory
import faiss
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
distances, indices = index.search(query_embedding, top_k)
```

### Option 2: Chroma (Lightweight VectorDB)
```python
# Persistent, fast, easy to use
from chromadb import Client
client = Client()
collection = client.get_or_create_collection("documents")
collection.add(ids=ids, documents=docs, embeddings=embeddings)
results = collection.query(query_embedding, n_results=5)
```

### Option 3: Pinecone (Cloud Vector Database)
```python
# Scalable, production-ready
from pinecone import Pinecone
pc = Pinecone(api_key="...")
index = pc.Index("documents")
index.upsert(vectors=vectors)
results = index.query(embedding, top_k=5)
```

### Option 4: Better Embeddings
```python
# Replace keyword frequency with ML embeddings
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(text)  # 384-dim dense vector
```

## Current Limitations

| Limitation | Impact | Solution |
|-----------|--------|----------|
| Keyword frequency embeddings | Lower accuracy | Use sentence-transformers or OpenAI |
| In-memory storage | Limited scalability | Use FAISS, Chroma, or Pinecone |
| No distributed search | Slow with large datasets | Use cloud vector DB |
| Fixed keyword list | Misses domain-specific terms | Dynamic keyword extraction |
| Pickle file storage | Not concurrent-safe | Use persistent DB |

## Summary

**Current State**: ✅ Working MVP
- Vector DB implemented as in-memory store with pickle persistence
- Keyword-based embeddings for financial documents
- Cosine similarity search functioning correctly
- RAG Agent successfully retrieves relevant documents

**For Scale**: Consider upgrading to FAISS, Chroma, or Pinecone with sentence-transformer embeddings

**For Better Quality**: Replace keyword frequency with pre-trained embedding models like:
- `all-MiniLM-L6-v2` (384-dim, fast)
- `all-mpnet-base-v2` (768-dim, accurate)
- OpenAI embeddings (high quality, cost)

