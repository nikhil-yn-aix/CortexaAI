"""
Configuration settings for the RAG pipeline
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Legal Educational Sources Configuration
ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", "10"))
WIKIPEDIA_MAX_ARTICLES = int(os.getenv("WIKIPEDIA_MAX_ARTICLES", "5"))
MIT_OCW_ENABLED = os.getenv("MIT_OCW_ENABLED", "true").lower() == "true"

# Chunking Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Vector Database Configuration
VECTOR_DB = os.getenv("VECTOR_DB", "auto")  # "qdrant", "chroma", or "auto"
# Get the services directory path
SERVICES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", os.path.join(SERVICES_DIR, "vectordb_data"))

# Scraping Configuration
MAX_BOOKS_PER_TOPIC = int(os.getenv("MAX_BOOKS_PER_TOPIC", "3"))
DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", "60"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Search Configuration
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "50"))
USE_HYBRID_SEARCH = os.getenv("USE_HYBRID_SEARCH", "true").lower() == "true"
KEYWORD_WEIGHT = float(os.getenv("KEYWORD_WEIGHT", "0.3"))

# Context Generation
MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "2000"))

# Processing Configuration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/rag_pipeline.log")

# File Paths - relative to services directory
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", os.path.join(SERVICES_DIR, "documents"))
LOGS_DIR = os.getenv("LOGS_DIR", os.path.join(SERVICES_DIR, "logs"))
CACHE_DIR = os.getenv("CACHE_DIR", os.path.join(SERVICES_DIR, "cache"))

# Create necessary directories
for directory in [DOCUMENTS_DIR, LOGS_DIR, CACHE_DIR, VECTOR_DB_PATH]:
    os.makedirs(directory, exist_ok=True)

# User Agent for web scraping
USER_AGENT = os.getenv("USER_AGENT", 
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

# Performance Settings
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
CACHE_EXPIRY_HOURS = int(os.getenv("CACHE_EXPIRY_HOURS", "24"))

# Debug Settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
SAVE_INTERMEDIATE_FILES = os.getenv("SAVE_INTERMEDIATE_FILES", "false").lower() == "true"

# Collection Names
DEFAULT_COLLECTION_NAME = os.getenv("DEFAULT_COLLECTION_NAME", "education_rag")

# PDF Processing Settings
PDF_EXTRACT_IMAGES = os.getenv("PDF_EXTRACT_IMAGES", "false").lower() == "true"
PDF_OCR_ENABLE = os.getenv("PDF_OCR_ENABLE", "false").lower() == "true"

# Rate Limiting
SCRAPING_DELAY = float(os.getenv("SCRAPING_DELAY", "2.0"))  # Delay between requests in seconds
CONCURRENT_DOWNLOADS = int(os.getenv("CONCURRENT_DOWNLOADS", "2"))

# Validation Settings
MIN_CHUNK_LENGTH = int(os.getenv("MIN_CHUNK_LENGTH", "50"))  # Minimum characters for a valid chunk
MIN_PDF_SIZE = int(os.getenv("MIN_PDF_SIZE", "1024"))  # Minimum PDF size in bytes

# Export configuration as dictionary
CONFIG = {
    "arxiv_max_results": ARXIV_MAX_RESULTS,
    "wikipedia_max_articles": WIKIPEDIA_MAX_ARTICLES,
    "mit_ocw_enabled": MIT_OCW_ENABLED,
    "chunk_size": CHUNK_SIZE,
    "chunk_overlap": CHUNK_OVERLAP,
    "embedding_model": EMBEDDING_MODEL,
    "vector_db": VECTOR_DB,
    "vector_db_path": VECTOR_DB_PATH,
    "max_books_per_topic": MAX_BOOKS_PER_TOPIC,
    "download_timeout": DOWNLOAD_TIMEOUT,
    "max_retries": MAX_RETRIES,
    "default_top_k": DEFAULT_TOP_K,
    "use_hybrid_search": USE_HYBRID_SEARCH,
    "keyword_weight": KEYWORD_WEIGHT,
    "max_context_length": MAX_CONTEXT_LENGTH,
    "batch_size": BATCH_SIZE,
    "max_workers": MAX_WORKERS,
    "log_level": LOG_LEVEL,
    "log_file": LOG_FILE,
    "documents_dir": DOCUMENTS_DIR,
    "logs_dir": LOGS_DIR,
    "cache_dir": CACHE_DIR,
    "user_agent": USER_AGENT,
    "enable_caching": ENABLE_CACHING,
    "cache_expiry_hours": CACHE_EXPIRY_HOURS,
    "debug_mode": DEBUG_MODE,
    "save_intermediate_files": SAVE_INTERMEDIATE_FILES,
    "default_collection_name": DEFAULT_COLLECTION_NAME,
    "pdf_extract_images": PDF_EXTRACT_IMAGES,
    "pdf_ocr_enable": PDF_OCR_ENABLE,
    "scraping_delay": SCRAPING_DELAY,
    "concurrent_downloads": CONCURRENT_DOWNLOADS,
    "min_chunk_length": MIN_CHUNK_LENGTH,
    "min_pdf_size": MIN_PDF_SIZE
}

def get_config():
    """Get the configuration dictionary"""
    return CONFIG

def update_config(key: str, value):
    """Update a configuration value"""
    CONFIG[key] = value
    # Also update the module-level variable if it exists
    if key.upper() in globals():
        globals()[key.upper()] = value

def save_config_to_file(filepath: str = ".env"):
    """Save current configuration to a file"""
    with open(filepath, 'w') as f:
        for key, value in CONFIG.items():
            env_key = key.upper()
            f.write(f"{env_key}={value}\n")

def load_config_from_file(filepath: str = ".env"):
    """Load configuration from a file"""
    if os.path.exists(filepath):
        load_dotenv(filepath, override=True)
        # Reload all configuration values
        for key in CONFIG.keys():
            env_key = key.upper()
            if env_value := os.getenv(env_key):
                CONFIG[key] = env_value
                if env_key in globals():
                    globals()[env_key] = env_value