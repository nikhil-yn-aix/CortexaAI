#!/usr/bin/env python3
"""
Main entry point for the RAG Pipeline
Complete example demonstrating all features
"""

import argparse
import json
import logging
import sys
from typing import List, Dict
from rag_pipeline import RAGRetriever
from rag_pipeline.config import get_config, save_config_to_file

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_basic_usage():
    """Demonstrate basic usage of the RAG pipeline"""
    print("\n" + "="*50)
    print("BASIC USAGE DEMO")
    print("="*50)
    
    # Initialize retriever
    retriever = RAGRetriever()
    
    # Example 1: Ingest a topic
    print("\n1. Ingesting content for a topic...")
    topic = "deep learning"
    result = retriever.ingest_topic(topic, max_books=2)
    print(f"   Ingestion result: {json.dumps(result, indent=2)}")
    
    # Example 2: Search for information
    print("\n2. Searching for information...")
    query = "What is gradient descent?"
    search_results = retriever.search(query, top_k=5)
    
    print(f"   Query: {query}")
    print(f"   Found {len(search_results)} results")
    
    for i, result in enumerate(search_results[:3], 1):
        print(f"\n   Result {i}:")
        print(f"   - Text: {result['text'][:150]}...")
        print(f"   - Score: {result.get('score', 0):.4f}")
        if 'metadata' in result:
            print(f"   - Source: {result['metadata'].get('source', 'Unknown')}")
            print(f"   - Page: {result['metadata'].get('page', 'N/A')}")
    
    # Example 3: Get context for LLM
    print("\n3. Getting context for LLM...")
    context = retriever.get_context(query, max_tokens=500)
    print(f"   Context (first 300 chars):\n   {context[:300]}...")
    
    # Example 4: Get statistics
    print("\n4. System statistics:")
    stats = retriever.get_statistics()
    print(f"   - Collection: {stats['collection_info']['name']}")
    print(f"   - Documents processed: {stats['processed_documents']}")
    print(f"   - Total chunks: {stats['total_chunks']}")

def demo_advanced_features():
    """Demonstrate advanced features"""
    print("\n" + "="*50)
    print("ADVANCED FEATURES DEMO")
    print("="*50)
    
    retriever = RAGRetriever()
    
    # Example 1: Filtered search
    print("\n1. Filtered search...")
    filters = {"topic": "machine learning"}
    results = retriever.search("neural networks", top_k=5, filters=filters)
    print(f"   Found {len(results)} results with filter: {filters}")
    
    # Example 2: Hybrid search
    print("\n2. Hybrid search (semantic + keyword)...")
    results = retriever.search("backpropagation algorithm", top_k=5, use_hybrid=True)
    print(f"   Found {len(results)} results using hybrid search")
    
    # Example 3: Batch PDF ingestion
    print("\n3. Batch PDF ingestion...")
    result = retriever.batch_ingest_pdfs("documents")
    print(f"   Batch result: {json.dumps(result, indent=2)}")

def demo_pdf_ingestion():
    """Demonstrate single PDF ingestion"""
    print("\n" + "="*50)
    print("SINGLE PDF INGESTION DEMO")
    print("="*50)
    
    retriever = RAGRetriever()
    
    # Check if there are any PDFs in documents folder
    import os
    pdf_files = [f for f in os.listdir("documents") if f.endswith('.pdf')]
    
    if pdf_files:
        pdf_path = os.path.join("documents", pdf_files[0])
        print(f"\nIngesting PDF: {pdf_path}")
        
        metadata = {
            "topic": "test",
            "source": "manual_upload"
        }
        
        result = retriever.ingest_pdf(pdf_path, metadata)
        print(f"Result: {json.dumps(result, indent=2)}")
    else:
        print("\nNo PDF files found in documents folder")
        print("Please add PDF files or run topic ingestion first")

def interactive_mode():
    """Interactive query mode"""
    print("\n" + "="*50)
    print("INTERACTIVE QUERY MODE")
    print("="*50)
    print("Type 'quit' to exit, 'stats' for statistics")
    print("="*50)
    
    retriever = RAGRetriever()
    
    while True:
        query = input("\nEnter your query: ").strip()
        
        if query.lower() == 'quit':
            break
        elif query.lower() == 'stats':
            stats = retriever.get_statistics()
            print(json.dumps(stats, indent=2))
        elif query:
            # Search
            results = retriever.search(query, top_k=5)
            
            if results:
                print(f"\nFound {len(results)} results:")
                for i, result in enumerate(results[:3], 1):
                    print(f"\n--- Result {i} ---")
                    print(f"Text: {result['text'][:200]}...")
                    print(f"Score: {result.get('score', 0):.4f}")
                    if 'metadata' in result:
                        print(f"Source: {result['metadata'].get('source', 'Unknown')}")
                        print(f"Page: {result['metadata'].get('page', 'N/A')}")
            else:
                print("No results found")

def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(description="RAG Pipeline - Educational Content Retrieval System")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest content')
    ingest_parser.add_argument('--topic', type=str, help='Topic to search and ingest')
    ingest_parser.add_argument('--pdf', type=str, help='Path to PDF file to ingest')
    ingest_parser.add_argument('--batch', type=str, help='Directory with PDFs to batch ingest')
    ingest_parser.add_argument('--max-books', type=int, default=3, help='Maximum books to download')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for information')
    search_parser.add_argument('query', type=str, help='Search query')
    search_parser.add_argument('--top-k', type=int, default=10, help='Number of results')
    search_parser.add_argument('--hybrid', action='store_true', help='Use hybrid search')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Interactive query mode')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demonstration')
    demo_parser.add_argument('--type', choices=['basic', 'advanced', 'pdf', 'all'], 
                            default='basic', help='Type of demo to run')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show system statistics')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear database')
    clear_parser.add_argument('--confirm', action='store_true', help='Confirm clearing')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show or save configuration')
    config_parser.add_argument('--save', type=str, help='Save config to file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize retriever for most commands
    if args.command not in ['config', 'demo']:
        retriever = RAGRetriever()
    
    # Execute commands
    if args.command == 'ingest':
        if args.topic:
            print(f"Ingesting topic: {args.topic}")
            result = retriever.ingest_topic(args.topic, max_books=args.max_books)
            print(json.dumps(result, indent=2))
        elif args.pdf:
            print(f"Ingesting PDF: {args.pdf}")
            result = retriever.ingest_pdf(args.pdf)
            print(json.dumps(result, indent=2))
        elif args.batch:
            print(f"Batch ingesting from: {args.batch}")
            result = retriever.batch_ingest_pdfs(args.batch)
            print(json.dumps(result, indent=2))
        else:
            print("Please specify --topic, --pdf, or --batch")
    
    elif args.command == 'search':
        results = retriever.search(args.query, top_k=args.top_k, use_hybrid=args.hybrid)
        print(f"\nFound {len(results)} results for: {args.query}\n")
        
        for i, result in enumerate(results, 1):
            print(f"--- Result {i} ---")
            print(f"Text: {result['text'][:300]}...")
            print(f"Score: {result.get('score', 0):.4f}")
            if 'metadata' in result:
                print(f"Source: {result['metadata'].get('source', 'Unknown')}")
                print(f"Page: {result['metadata'].get('page', 'N/A')}")
            print()
    
    elif args.command == 'interactive':
        interactive_mode()
    
    elif args.command == 'demo':
        if args.type == 'basic':
            demo_basic_usage()
        elif args.type == 'advanced':
            demo_advanced_features()
        elif args.type == 'pdf':
            demo_pdf_ingestion()
        elif args.type == 'all':
            demo_basic_usage()
            demo_advanced_features()
            demo_pdf_ingestion()
    
    elif args.command == 'stats':
        stats = retriever.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.command == 'clear':
        if args.confirm:
            retriever.clear_database()
            print("Database cleared")
        else:
            print("Use --confirm to clear the database")
    
    elif args.command == 'config':
        config = get_config()
        if args.save:
            save_config_to_file(args.save)
            print(f"Configuration saved to: {args.save}")
        else:
            print(json.dumps(config, indent=2))

if __name__ == "__main__":
    try:
        # Check if running without arguments
        if len(sys.argv) == 1:
            print("\n" + "="*60)
            print("RAG PIPELINE - Educational Content Retrieval System")
            print("="*60)
            print("\nQuick Start Examples:")
            print("-"*40)
            print("\n1. Ingest content for a topic:")
            print("   python main.py ingest --topic 'machine learning' --max-books 2")
            print("\n2. Search for information:")
            print("   python main.py search 'what is neural network' --top-k 5")
            print("\n3. Interactive mode:")
            print("   python main.py interactive")
            print("\n4. Run demonstration:")
            print("   python main.py demo --type basic")
            print("\n5. Show statistics:")
            print("   python main.py stats")
            print("\n6. Batch ingest PDFs:")
            print("   python main.py ingest --batch documents")
            print("\nFor more options, use: python main.py --help")
            print("="*60)
        else:
            main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)