"""
RAG Pipeline for Educational Content
A complete implementation of RAG with web scraping and vector search
"""

from .scraper import BookScraper
from .pdf_processor import PDFProcessor
from .chunker import TextChunker
from .vectordb import VectorDB
from .retriever import RAGRetriever

__version__ = "1.0.0"
__all__ = [
    "BookScraper",
    "PDFProcessor", 
    "TextChunker",
    "VectorDB",
    "RAGRetriever"
]