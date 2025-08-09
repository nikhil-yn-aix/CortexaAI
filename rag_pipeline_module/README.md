# RAG Pipeline

Retrieval Augmented Generation pipeline with web scraping and vector search.

## Features
- Web scraping from arXiv, Wikipedia, MIT OCW
- PDF processing and text extraction
- Text chunking with 512 token windows
- Vector database with HNSW indexing (Qdrant)
- Semantic search with top-K retrieval

## Usage

```bash
# Build knowledge base
python rag_main.py ingest --topic "machine learning" --max-books 5

# Search
python rag_main.py search "what is gradient descent" --top-k 50

# Check stats
python rag_main.py stats
```

## Components
- `scraper.py` - Content scraping from educational sources
- `pdf_processor.py` - PDF text extraction
- `chunker.py` - Text chunking
- `vectordb.py` - Vector database operations
- `retriever.py` - Main pipeline orchestrator
