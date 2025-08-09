"""
Vector database module with HNSW index for fast similarity search
Supports both Qdrant and ChromaDB
"""

import os
import logging
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import json
import hashlib

# Try to import both vector databases
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    from qdrant_client.models import HnswConfigDiff, OptimizersConfigDiff
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("Qdrant not available. Install with: pip install qdrant-client")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("ChromaDB not available. Install with: pip install chromadb")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self, 
                 collection_name: str = "education_rag",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 db_type: str = "auto",
                 persist_directory: str = "vectordb_data"):
        """
        Initialize vector database
        Args:
            collection_name: Name of the collection/index
            embedding_model: Name of the sentence transformer model
            db_type: "qdrant", "chroma", or "auto" (auto-detect)
            persist_directory: Directory to persist the database
        """
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        self.persist_directory = persist_directory
        
        # Auto-detect available database
        if db_type == "auto":
            if QDRANT_AVAILABLE:
                db_type = "qdrant"
            elif CHROMA_AVAILABLE:
                db_type = "chroma"
            else:
                raise ImportError("No vector database available. Install qdrant-client or chromadb")
        
        self.db_type = db_type
        self.client = None
        self.collection = None
        
        # Initialize the selected database
        if db_type == "qdrant":
            self._init_qdrant()
        elif db_type == "chroma":
            self._init_chroma()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        logger.info(f"Initialized {db_type} vector database with collection: {collection_name}")
    
    def _init_qdrant(self):
        """Initialize Qdrant database"""
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant not available. Install with: pip install qdrant-client")
        
        # Create persist directory
        os.makedirs(self.persist_directory, exist_ok=True)
        qdrant_path = os.path.join(self.persist_directory, "qdrant")
        
        # Initialize Qdrant client (local storage)
        self.client = QdrantClient(path=qdrant_path)
        
        # Create collection if it doesn't exist
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if self.collection_name not in collection_names:
            self.create_collection()
    
    def _init_chroma(self):
        """Initialize ChromaDB database"""
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB not available. Install with: pip install chromadb")
        
        # Create persist directory
        os.makedirs(self.persist_directory, exist_ok=True)
        chroma_path = os.path.join(self.persist_directory, "chroma")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
            logger.info(f"Loaded existing ChromaDB collection: {self.collection_name}")
        except:
            self.create_collection()
    
    def create_collection(self):
        """Create a new collection with HNSW index"""
        if self.db_type == "qdrant":
            # Configure HNSW index for Qdrant
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                ),
                hnsw_config=HnswConfigDiff(
                    m=16,  # Number of edges per node
                    ef_construct=100,  # Size of dynamic candidate list
                    full_scan_threshold=10000
                ),
                optimizers_config=OptimizersConfigDiff(
                    indexing_threshold=20000,
                    memmap_threshold=50000
                )
            )
            logger.info(f"Created Qdrant collection with HNSW index: {self.collection_name}")
            
        elif self.db_type == "chroma":
            # ChromaDB automatically uses HNSW
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created ChromaDB collection with HNSW index: {self.collection_name}")
    
    def generate_id(self, text: str, metadata: Dict = None) -> str:
        """Generate unique ID for a document"""
        content = text
        if metadata:
            content += json.dumps(metadata, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed texts in batches"""
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Embedding texts"):
            batch = texts[i:i + batch_size]
            embeddings = self.embedding_model.encode(batch, show_progress_bar=False)
            all_embeddings.extend(embeddings)
        
        return np.array(all_embeddings)
    
    def add_documents(self, 
                     chunks: List[Dict],
                     embeddings: Optional[np.ndarray] = None,
                     batch_size: int = 100):
        """Add documents to the vector database"""
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        # Extract texts
        texts = [chunk.get('text', '') for chunk in chunks]
        
        # Generate embeddings if not provided
        if embeddings is None:
            logger.info(f"Generating embeddings for {len(texts)} chunks...")
            embeddings = self.embed_texts(texts)
        
        if self.db_type == "qdrant":
            self._add_documents_qdrant(chunks, embeddings, batch_size)
        elif self.db_type == "chroma":
            self._add_documents_chroma(chunks, embeddings, batch_size)
    
    def _add_documents_qdrant(self, chunks: List[Dict], embeddings: np.ndarray, batch_size: int):
        """Add documents to Qdrant"""
        points = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate unique ID
            doc_id = chunk.get('id') or self.generate_id(chunk['text'], chunk)
            
            # Prepare payload (metadata)
            payload = {k: v for k, v in chunk.items() if k != 'text'}
            payload['text'] = chunk['text']
            
            point = PointStruct(
                id=i,  # Qdrant requires integer IDs
                vector=embedding.tolist(),
                payload=payload
            )
            points.append(point)
        
        # Upload in batches
        for i in tqdm(range(0, len(points), batch_size), desc="Uploading to Qdrant"):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        logger.info(f"Added {len(points)} documents to Qdrant")
    
    def _add_documents_chroma(self, chunks: List[Dict], embeddings: np.ndarray, batch_size: int):
        """Add documents to ChromaDB"""
        ids = []
        texts = []
        metadatas = []
        embeddings_list = []
        
        for chunk, embedding in zip(chunks, embeddings):
            # Generate unique ID
            doc_id = chunk.get('id') or self.generate_id(chunk['text'], chunk)
            ids.append(doc_id)
            texts.append(chunk['text'])
            
            # Prepare metadata
            metadata = {k: v for k, v in chunk.items() if k not in ['text', 'id']}
            metadatas.append(metadata)
            embeddings_list.append(embedding.tolist())
        
        # Add in batches
        for i in tqdm(range(0, len(ids), batch_size), desc="Uploading to ChromaDB"):
            self.collection.add(
                ids=ids[i:i + batch_size],
                documents=texts[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
                embeddings=embeddings_list[i:i + batch_size]
            )
        
        logger.info(f"Added {len(ids)} documents to ChromaDB")
    
    def search(self, 
              query: str,
              top_k: int = 50,
              filters: Optional[Dict] = None) -> List[Dict]:
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        if self.db_type == "qdrant":
            return self._search_qdrant(query_embedding, top_k, filters)
        elif self.db_type == "chroma":
            return self._search_chroma(query_embedding, top_k, filters)
    
    def _search_qdrant(self, query_embedding: np.ndarray, top_k: int, filters: Optional[Dict]) -> List[Dict]:
        """Search in Qdrant"""
        # Build filter if provided
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                ))
            if conditions:
                qdrant_filter = Filter(must=conditions)
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=top_k,
            query_filter=qdrant_filter
        )
        
        # Format results
        formatted_results = []
        for hit in results:
            result = {
                'text': hit.payload.get('text', ''),
                'score': hit.score,
                'metadata': {k: v for k, v in hit.payload.items() if k != 'text'}
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def _search_chroma(self, query_embedding: np.ndarray, top_k: int, filters: Optional[Dict]) -> List[Dict]:
        """Search in ChromaDB"""
        # Build where clause if filters provided
        where = filters if filters else None
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                result = {
                    'text': doc,
                    'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def hybrid_search(self, 
                     query: str,
                     top_k: int = 50,
                     keyword_weight: float = 0.3) -> List[Dict]:
        """Combine semantic and keyword search"""
        # Semantic search
        semantic_results = self.search(query, top_k * 2)
        
        # Simple keyword matching (TF-IDF would be better)
        query_words = set(query.lower().split())
        
        # Score and re-rank results
        for result in semantic_results:
            text_words = set(result['text'].lower().split())
            keyword_score = len(query_words.intersection(text_words)) / len(query_words)
            
            # Combine scores
            result['combined_score'] = (
                (1 - keyword_weight) * result['score'] + 
                keyword_weight * keyword_score
            )
        
        # Sort by combined score
        semantic_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return semantic_results[:top_k]
    
    def delete_collection(self):
        """Delete the entire collection"""
        if self.db_type == "qdrant":
            self.client.delete_collection(self.collection_name)
        elif self.db_type == "chroma":
            self.client.delete_collection(self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection"""
        info = {
            'name': self.collection_name,
            'db_type': self.db_type,
            'embedding_dim': self.embedding_dim
        }
        
        if self.db_type == "qdrant":
            collection_info = self.client.get_collection(self.collection_name)
            info['vectors_count'] = collection_info.vectors_count
            info['points_count'] = collection_info.points_count
            info['indexed_vectors_count'] = collection_info.indexed_vectors_count
        elif self.db_type == "chroma":
            info['count'] = self.collection.count()
        
        return info
    
    def update_document(self, doc_id: str, new_text: str, new_metadata: Dict = None):
        """Update a document in the database"""
        # Generate new embedding
        new_embedding = self.embedding_model.encode(new_text)
        
        if self.db_type == "qdrant":
            # In Qdrant, we need to find the point by payload filter first
            # Then update it (this is a limitation of using integer IDs)
            logger.warning("Update not fully implemented for Qdrant with string IDs")
        elif self.db_type == "chroma":
            self.collection.update(
                ids=[doc_id],
                documents=[new_text],
                metadatas=[new_metadata] if new_metadata else None,
                embeddings=[new_embedding.tolist()]
            )
    
    def delete_documents(self, doc_ids: List[str]):
        """Delete documents by IDs"""
        if self.db_type == "qdrant":
            # Need to implement mapping from string IDs to integer IDs
            logger.warning("Delete not fully implemented for Qdrant with string IDs")
        elif self.db_type == "chroma":
            self.collection.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents")

if __name__ == "__main__":
    # Test the vector database
    db = VectorDB(collection_name="test_collection")
    
    # Test data
    test_chunks = [
        {
            'text': "Machine learning is a subset of artificial intelligence.",
            'source': 'test_doc',
            'page': 1
        },
        {
            'text': "Deep learning uses neural networks with multiple layers.",
            'source': 'test_doc',
            'page': 2
        },
        {
            'text': "Natural language processing enables computers to understand human language.",
            'source': 'test_doc',
            'page': 3
        }
    ]
    
    # Add documents
    print("Adding test documents...")
    db.add_documents(test_chunks)
    
    # Search
    query = "What is machine learning?"
    print(f"\nSearching for: {query}")
    results = db.search(query, top_k=2)
    
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"  Text: {result['text'][:100]}...")
        print(f"  Score: {result['score']:.4f}")
        print(f"  Metadata: {result['metadata']}")
    
    # Get collection info
    info = db.get_collection_info()
    print(f"\nCollection info: {info}")