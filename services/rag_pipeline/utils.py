"""
Utility functions for the RAG pipeline
"""

import os
import re
import json
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import pickle
import time

logger = logging.getLogger(__name__)

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize a filename to be safe for all operating systems
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Limit length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    return filename

def generate_hash(text: str) -> str:
    """
    Generate MD5 hash of text
    """
    return hashlib.md5(text.encode()).hexdigest()

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis
    """
    # Common stop words to filter out
    stop_words = set([
        'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was',
        'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
        'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how',
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 'just', 'but', 'for', 'with', 'about',
        'against', 'between', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'off',
        'over', 'under', 'again', 'further', 'then', 'once'
    ])
    
    # Extract words
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Filter stop words and short words
    words = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Count frequency
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', '', text)
    # Remove multiple punctuation
    text = re.sub(r'([\.!\?])\1+', r'\1', text)
    return text.strip()

def split_into_batches(items: List[Any], batch_size: int) -> List[List[Any]]:
    """
    Split a list into batches
    """
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches

def merge_overlapping_chunks(chunks: List[Dict], overlap_threshold: float = 0.5) -> List[Dict]:
    """
    Merge chunks that have significant overlap
    """
    if not chunks:
        return []
    
    merged = []
    current = chunks[0].copy()
    
    for next_chunk in chunks[1:]:
        # Calculate overlap
        current_text = current['text']
        next_text = next_chunk['text']
        
        # Find common substring
        min_len = min(len(current_text), len(next_text))
        overlap_len = 0
        
        for i in range(min_len, 0, -1):
            if current_text[-i:] == next_text[:i]:
                overlap_len = i
                break
        
        overlap_ratio = overlap_len / min_len if min_len > 0 else 0
        
        if overlap_ratio >= overlap_threshold:
            # Merge chunks
            current['text'] = current_text + next_text[overlap_len:]
            # Merge metadata
            if 'metadata' in current and 'metadata' in next_chunk:
                current['metadata'].update(next_chunk['metadata'])
        else:
            # No significant overlap, save current and start new
            merged.append(current)
            current = next_chunk.copy()
    
    # Add last chunk
    merged.append(current)
    return merged

class Cache:
    """Simple file-based cache with expiration"""
    
    def __init__(self, cache_dir: str = "cache", expiry_hours: int = 24):
        self.cache_dir = cache_dir
        self.expiry_hours = expiry_hours
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path for a key"""
        key_hash = generate_hash(key)
        return os.path.join(self.cache_dir, f"{key_hash}.cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            # Check if cache is expired
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
            if datetime.now() - file_time > timedelta(hours=self.expiry_hours):
                os.remove(cache_path)
                return None
            
            # Load cached value
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")
    
    def clear(self):
        """Clear all cache files"""
        for file in os.listdir(self.cache_dir):
            if file.endswith('.cache'):
                try:
                    os.remove(os.path.join(self.cache_dir, file))
                except:
                    pass

def estimate_tokens(text: str) -> int:
    """
    Estimate number of tokens in text (rough approximation)
    """
    # Rough estimate: 1 token ≈ 4 characters or 0.75 words
    word_count = len(text.split())
    char_count = len(text)
    return max(int(word_count * 1.3), int(char_count / 4))

def truncate_text(text: str, max_length: int, add_ellipsis: bool = True) -> str:
    """
    Truncate text to maximum length while preserving word boundaries
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    
    # Find last complete word
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    
    if add_ellipsis:
        truncated += '...'
    
    return truncated

def format_timestamp(timestamp: float) -> str:
    """
    Format Unix timestamp to readable string
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity using Jaccard index
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def create_summary(text: str, max_sentences: int = 3) -> str:
    """
    Create a simple extractive summary
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= max_sentences:
        return text
    
    # Simple scoring based on word frequency
    word_freq = {}
    for sentence in sentences:
        words = sentence.lower().split()
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
    
    # Score sentences
    sentence_scores = []
    for sentence in sentences:
        score = sum(word_freq.get(word.lower(), 0) for word in sentence.split())
        sentence_scores.append((sentence, score))
    
    # Sort by score and take top sentences
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    summary_sentences = [s[0] for s in sentence_scores[:max_sentences]]
    
    # Maintain original order
    summary = []
    for sentence in sentences:
        if sentence in summary_sentences:
            summary.append(sentence)
    
    return '. '.join(summary) + '.'

def get_file_metadata(filepath: str) -> Dict:
    """
    Get metadata about a file
    """
    if not os.path.exists(filepath):
        return {}
    
    stat = os.stat(filepath)
    return {
        'filename': os.path.basename(filepath),
        'filepath': os.path.abspath(filepath),
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'created': format_timestamp(stat.st_ctime),
        'modified': format_timestamp(stat.st_mtime),
        'extension': os.path.splitext(filepath)[1]
    }

def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0):
    """
    Retry a function with exponential backoff
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise last_exception

def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace in text
    """
    # Replace all whitespace with single space
    text = ' '.join(text.split())
    return text

def is_valid_json(json_string: str) -> bool:
    """
    Check if a string is valid JSON
    """
    try:
        json.loads(json_string)
        return True
    except (json.JSONDecodeError, TypeError):
        return False

def extract_numbers(text: str) -> List[float]:
    """
    Extract all numbers from text
    """
    # Pattern for integers and decimals
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    
    numbers = []
    for match in matches:
        try:
            if '.' in match:
                numbers.append(float(match))
            else:
                numbers.append(int(match))
        except ValueError:
            continue
    
    return numbers

if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...")
    
    # Test filename sanitization
    filename = "Test: File<Name>.pdf"
    print(f"Sanitized filename: {sanitize_filename(filename)}")
    
    # Test text cleaning
    text = "This   is   a   test!!!   With    extra     spaces..."
    print(f"Cleaned text: {clean_text(text)}")
    
    # Test keyword extraction
    sample_text = """
    Machine learning is a subset of artificial intelligence that focuses on
    the development of algorithms that can learn from and make predictions
    based on data. Deep learning is a type of machine learning.
    """
    keywords = extract_keywords(sample_text, 5)
    print(f"Keywords: {keywords}")
    
    # Test cache
    cache = Cache()
    cache.set("test_key", {"data": "test_value"})
    cached_value = cache.get("test_key")
    print(f"Cached value: {cached_value}")
    
    # Test text similarity
    text1 = "Machine learning is awesome"
    text2 = "Machine learning is great"
    similarity = calculate_similarity(text1, text2)
    print(f"Similarity: {similarity:.2f}")