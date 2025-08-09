"""
Main RAG Retriever interface that orchestrates the entire pipeline
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from tqdm import tqdm

from .scraper import BookScraper
from .pdf_processor import PDFProcessor
from .chunker import TextChunker
from .vectordb import VectorDB
from .config import (
    CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL,
    VECTOR_DB, MAX_BOOKS_PER_TOPIC, MAX_CONTEXT_LENGTH
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGRetriever:
    def __init__(self,
                 collection_name: str = "education_rag",
                 chunk_size: int = CHUNK_SIZE,
                 chunk_overlap: int = CHUNK_OVERLAP,
                 embedding_model: str = EMBEDDING_MODEL,
                 vector_db_type: str = VECTOR_DB):
        """
        Initialize the RAG Retriever
        """
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize components
        logger.info("Initializing RAG Retriever components...")
        self.scraper = BookScraper()
        self.processor = PDFProcessor()
        self.chunker = TextChunker(chunk_size=chunk_size, overlap=chunk_overlap, model_name=embedding_model)
        self.vectordb = VectorDB(
            collection_name=collection_name,
            embedding_model=embedding_model,
            db_type=vector_db_type
        )
        
        # Cache for processed documents
        self.processed_cache_file = "vectordb_data/processed_docs.json"
        self.processed_docs = self._load_processed_cache()
        
        logger.info("RAG Retriever initialized successfully")
    
    def _load_processed_cache(self) -> Dict:
        """Load cache of processed documents"""
        if os.path.exists(self.processed_cache_file):
            try:
                with open(self.processed_cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_processed_cache(self):
        """Save cache of processed documents"""
        os.makedirs(os.path.dirname(self.processed_cache_file), exist_ok=True)
        with open(self.processed_cache_file, 'w') as f:
            json.dump(self.processed_docs, f, indent=2)
    
    def _is_document_processed(self, filepath: str) -> bool:
        """Check if a document has already been processed"""
        if filepath in self.processed_docs:
            # Check if file has been modified since processing
            file_mtime = os.path.getmtime(filepath)
            processed_time = self.processed_docs[filepath].get('processed_time', 0)
            return file_mtime <= processed_time
        return False
    
    def ingest_topic(self, 
                    topic: str,
                    max_books: int = MAX_BOOKS_PER_TOPIC,
                    force_redownload: bool = False) -> Dict:
        """
        Complete pipeline: scrape → process → chunk → embed → store
        """
        logger.info(f"Starting ingestion for topic: {topic}")
        start_time = time.time()
        
        results = {
            'topic': topic,
            'books_downloaded': 0,
            'books_processed': 0,
            'chunks_created': 0,
            'errors': []
        }
        
        try:
            # Step 1: Scrape and download books
            # Always scrape for the topic to get new content
            downloaded_books = self.scraper.scrape_topic(topic, max_books)
            
            results['books_downloaded'] = len(downloaded_books)
            
            if not downloaded_books:
                logger.warning(f"No books downloaded for topic: {topic}")
                return results
            
            # Step 2: Process each item (can be PDF or text content)
            all_chunks = []
            
            for book_metadata in downloaded_books:
                try:
                    # Check if this is a PDF with filepath or just content
                    filepath = book_metadata.get('filepath')
                    
                    if filepath and os.path.exists(filepath) and filepath.endswith('.pdf'):
                        # Process PDF file
                        if self._is_document_processed(filepath):
                            logger.info(f"Skipping already processed document: {filepath}")
                            results['books_processed'] += 1
                            continue
                        
                        logger.info(f"Processing PDF: {book_metadata.get('title', 'Unknown')}")
                        
                        # Extract text with metadata
                        pdf_data = self.processor.extract_with_metadata(filepath)
                        
                        if not pdf_data['pages']:
                            logger.warning(f"No text extracted from: {filepath}")
                            continue
                        
                        # Combine all page texts
                        full_text = '\n\n'.join([page['text'] for page in pdf_data['pages']])
                        
                        # Create document metadata
                        doc_metadata = {
                            'source': book_metadata.get('title', 'Unknown'),
                            'author': book_metadata.get('metadata', {}).get('authors', ['Unknown'])[0] if book_metadata.get('metadata', {}).get('authors') else 'Unknown',
                            'topic': topic,
                            'filepath': filepath,
                            'total_pages': pdf_data['total_pages'],
                            'doc_id': os.path.basename(filepath).replace('.pdf', ''),
                            'source_type': book_metadata.get('source', 'PDF')
                        }
                    else:
                        # Process text content directly (from Wikipedia, MIT OCW, etc.)
                        content = book_metadata.get('content', '')
                        if not content:
                            logger.warning(f"No content found for: {book_metadata.get('title', 'Unknown')}")
                            continue
                        
                        # Check if already processed using title as ID
                        doc_id = f"{book_metadata.get('source', 'unknown')}_{book_metadata.get('title', 'unknown')}"
                        if doc_id in self.processed_docs:
                            logger.info(f"Skipping already processed content: {doc_id}")
                            results['books_processed'] += 1
                            continue
                        
                        logger.info(f"Processing content: {book_metadata.get('title', 'Unknown')} from {book_metadata.get('source', 'Unknown')}")
                        
                        full_text = content
                        
                        # Create document metadata
                        doc_metadata = {
                            'source': book_metadata.get('title', 'Unknown'),
                            'author': book_metadata.get('metadata', {}).get('authors', ['Unknown'])[0] if book_metadata.get('metadata', {}).get('authors') else 'Unknown',
                            'topic': topic,
                            'url': book_metadata.get('url', ''),
                            'doc_id': doc_id,
                            'source_type': book_metadata.get('source', 'Unknown'),
                            'content_type': book_metadata.get('type', 'text')
                        }
                    
                    # Smart chunking
                    chunks = self.chunker.smart_chunk(full_text, doc_metadata)
                    
                    # Add page information to chunks (only for PDFs)
                    if filepath and filepath.endswith('.pdf'):
                        for chunk in chunks:
                            # Find which page this chunk belongs to
                            chunk_start = full_text.find(chunk['text'])
                            current_pos = 0
                            for page in pdf_data['pages']:
                                page_length = len(page['text'])
                                if current_pos <= chunk_start < current_pos + page_length:
                                    chunk['page'] = page['page_number']
                                    break
                                current_pos += page_length + 2  # +2 for \n\n
                    
                    # Prepare chunks for indexing
                    indexed_chunks = self.chunker.prepare_chunks_for_indexing(chunks, doc_metadata)
                    all_chunks.extend(indexed_chunks)
                    
                    # Mark as processed
                    process_key = filepath if filepath else doc_metadata['doc_id']
                    self.processed_docs[process_key] = {
                        'processed_time': time.time(),
                        'chunks': len(indexed_chunks),
                        'title': book_metadata.get('title', 'Unknown')
                    }
                    
                    results['books_processed'] += 1
                    logger.info(f"Created {len(indexed_chunks)} chunks from {book_metadata.get('title', 'Unknown')}")
                    
                except Exception as e:
                    error_msg = f"Error processing {book_metadata.get('title', 'Unknown')}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
                    continue
            
            # Step 3: Add all chunks to vector database
            if all_chunks:
                logger.info(f"Adding {len(all_chunks)} chunks to vector database...")
                self.vectordb.add_documents(all_chunks)
                results['chunks_created'] = len(all_chunks)
                
                # Save processed cache
                self._save_processed_cache()
            
            elapsed_time = time.time() - start_time
            logger.info(f"Ingestion completed in {elapsed_time:.2f} seconds")
            logger.info(f"Results: {results}")
            
        except Exception as e:
            error_msg = f"Fatal error during ingestion: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    def search(self, 
              query: str,
              top_k: int = 50,
              filters: Optional[Dict] = None,
              use_hybrid: bool = True) -> List[Dict]:
        """
        Search for relevant chunks
        """
        logger.info(f"Searching for: {query[:100]}...")
        
        if use_hybrid:
            results = self.vectordb.hybrid_search(query, top_k=top_k)
        else:
            results = self.vectordb.search(query, top_k=top_k, filters=filters)
        
        logger.info(f"Found {len(results)} results")
        return results
    
    def get_context(self, 
                   query: str,
                   max_tokens: int = MAX_CONTEXT_LENGTH,
                   top_k: int = 50) -> str:
        """
        Get context for LLM based on query
        """
        # Search for relevant chunks
        results = self.search(query, top_k=top_k)
        
        if not results:
            return "No relevant information found."
        
        # Build context
        context_parts = []
        current_tokens = 0
        
        for i, result in enumerate(results):
            chunk_text = result['text']
            chunk_tokens = self.chunker.count_tokens(chunk_text)
            
            if current_tokens + chunk_tokens > max_tokens:
                break
            
            # Format chunk with metadata
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            page = metadata.get('page', 'N/A')
            
            context_part = f"[Source: {source}, Page: {page}]\n{chunk_text}\n"
            context_parts.append(context_part)
            current_tokens += chunk_tokens
        
        context = "\n---\n".join(context_parts)
        
        # Add summary header
        header = f"Found {len(results)} relevant chunks. Showing top {len(context_parts)} chunks:\n\n"
        
        return header + context
    
    def ingest_pdf(self, pdf_path: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Ingest a single PDF file
        """
        logger.info(f"Ingesting PDF: {pdf_path}")
        
        results = {
            'file': pdf_path,
            'chunks_created': 0,
            'success': False,
            'error': None
        }
        
        try:
            # Check if file exists
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
            # Extract text
            pdf_data = self.processor.extract_with_metadata(pdf_path)
            
            if not pdf_data['pages']:
                raise ValueError("No text extracted from PDF")
            
            # Combine text
            full_text = '\n\n'.join([page['text'] for page in pdf_data['pages']])
            
            # Prepare metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                'filepath': pdf_path,
                'filename': os.path.basename(pdf_path),
                'total_pages': pdf_data['total_pages'],
                'doc_id': os.path.basename(pdf_path).replace('.pdf', '')
            })
            
            # Chunk text
            chunks = self.chunker.smart_chunk(full_text, doc_metadata)
            indexed_chunks = self.chunker.prepare_chunks_for_indexing(chunks, doc_metadata)
            
            # Add to vector database
            self.vectordb.add_documents(indexed_chunks)
            
            results['chunks_created'] = len(indexed_chunks)
            results['success'] = True
            
            logger.info(f"Successfully ingested {pdf_path}: {len(indexed_chunks)} chunks")
            
        except Exception as e:
            error_msg = f"Error ingesting PDF: {str(e)}"
            logger.error(error_msg)
            results['error'] = error_msg
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the RAG system
        """
        stats = {
            'collection_info': self.vectordb.get_collection_info(),
            'processed_documents': len(self.processed_docs),
            'document_list': list(self.processed_docs.keys()),
            'total_chunks': sum(doc['chunks'] for doc in self.processed_docs.values())
        }
        return stats
    
    def clear_database(self):
        """
        Clear the vector database and reset cache
        """
        logger.warning("Clearing vector database and cache...")
        self.vectordb.delete_collection()
        self.vectordb.create_collection()
        self.processed_docs = {}
        self._save_processed_cache()
        logger.info("Database cleared")
    
    def batch_ingest_pdfs(self, pdf_directory: str = "documents") -> Dict:
        """
        Ingest all PDFs in a directory
        """
        logger.info(f"Batch ingesting PDFs from: {pdf_directory}")
        
        pdf_files = [f for f in os.listdir(pdf_directory) 
                    if f.lower().endswith('.pdf')]
        
        results = {
            'total_files': len(pdf_files),
            'successful': 0,
            'failed': 0,
            'total_chunks': 0,
            'errors': []
        }
        
        for pdf_file in tqdm(pdf_files, desc="Ingesting PDFs"):
            pdf_path = os.path.join(pdf_directory, pdf_file)
            
            # Load metadata if exists
            metadata_path = pdf_path.replace('.pdf', '_metadata.json')
            metadata = {}
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            # Ingest PDF
            ingest_result = self.ingest_pdf(pdf_path, metadata)
            
            if ingest_result['success']:
                results['successful'] += 1
                results['total_chunks'] += ingest_result['chunks_created']
            else:
                results['failed'] += 1
                results['errors'].append(ingest_result['error'])
        
        logger.info(f"Batch ingestion complete: {results}")
        return results

if __name__ == "__main__":
    # Test the retriever
    retriever = RAGRetriever()
    
    # Test ingestion
    print("Testing topic ingestion...")
    result = retriever.ingest_topic("machine learning", max_books=1)
    print(f"Ingestion result: {result}")
    
    # Test search
    if result['chunks_created'] > 0:
        print("\nTesting search...")
        query = "What is deep learning?"
        search_results = retriever.search(query, top_k=5)
        
        for i, result in enumerate(search_results[:3]):
            print(f"\nResult {i+1}:")
            print(f"  Text: {result['text'][:200]}...")
            print(f"  Score: {result.get('score', 0):.4f}")
        
        # Test context generation
        print("\nTesting context generation...")
        context = retriever.get_context(query, max_tokens=500)
        print(f"Context (first 500 chars):\n{context[:500]}...")
    
    # Get statistics
    print("\nSystem statistics:")
    stats = retriever.get_statistics()
    print(json.dumps(stats, indent=2))