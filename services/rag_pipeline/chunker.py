"""
Intelligent text chunking module with sliding window and structure awareness
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextChunker:
    def __init__(self, chunk_size=512, overlap=50, model_name='all-MiniLM-L6-v2'):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.model = SentenceTransformer(model_name)
        self.tokenizer = self.model.tokenizer
        
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text"""
        try:
            tokens = self.tokenizer.tokenize(text)
            return len(tokens)
        except:
            # Fallback to word count estimation (roughly 1.3 tokens per word)
            return int(len(text.split()) * 1.3)
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        try:
            sentences = sent_tokenize(text)
            return sentences
        except:
            # Fallback to simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def chunk_text(self, text: str, chunk_size: Optional[int] = None, 
                   overlap: Optional[int] = None) -> List[str]:
        """Basic chunking with sliding window"""
        if not text:
            return []
        
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.overlap
        
        # Split into sentences
        sentences = self.split_into_sentences(text)
        
        if not sentences:
            return []
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If single sentence is too long, split it
            if sentence_tokens > chunk_size:
                # If we have a current chunk, save it
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Split the long sentence
                words = sentence.split()
                temp_chunk = []
                temp_tokens = 0
                
                for word in words:
                    word_tokens = self.count_tokens(word)
                    if temp_tokens + word_tokens <= chunk_size:
                        temp_chunk.append(word)
                        temp_tokens += word_tokens
                    else:
                        if temp_chunk:
                            chunks.append(' '.join(temp_chunk))
                        temp_chunk = [word]
                        temp_tokens = word_tokens
                
                if temp_chunk:
                    current_chunk = temp_chunk[-overlap:] if overlap > 0 else []
                    current_tokens = self.count_tokens(' '.join(current_chunk))
                    chunks.append(' '.join(temp_chunk))
            
            # If adding sentence exceeds chunk size
            elif current_tokens + sentence_tokens > chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                
                # Start new chunk with overlap
                if overlap > 0 and current_chunk:
                    # Take last few sentences for overlap
                    overlap_sentences = []
                    overlap_tokens = 0
                    for sent in reversed(current_chunk):
                        sent_tokens = self.count_tokens(sent)
                        if overlap_tokens + sent_tokens <= overlap:
                            overlap_sentences.insert(0, sent)
                            overlap_tokens += sent_tokens
                        else:
                            break
                    current_chunk = overlap_sentences + [sentence]
                    current_tokens = overlap_tokens + sentence_tokens
                else:
                    current_chunk = [sentence]
                    current_tokens = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Add the last chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        logger.info(f"Created {len(chunks)} chunks from {len(text)} characters")
        return chunks
    
    def smart_chunk(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Structure-aware chunking that respects document organization"""
        if not text:
            return []
        
        chunks_with_metadata = []
        
        # Try to identify document structure
        sections = self.identify_sections(text)
        
        if sections:
            logger.info(f"Found {len(sections)} sections in document")
            for section in sections:
                section_chunks = self.chunk_text(section['text'])
                for i, chunk in enumerate(section_chunks):
                    chunk_metadata = {
                        'text': chunk,
                        'section': section['title'],
                        'section_index': section['index'],
                        'chunk_index': i,
                        'tokens': self.count_tokens(chunk)
                    }
                    if metadata:
                        chunk_metadata.update(metadata)
                    chunks_with_metadata.append(chunk_metadata)
        else:
            # Fallback to regular chunking
            regular_chunks = self.chunk_text(text)
            for i, chunk in enumerate(regular_chunks):
                chunk_metadata = {
                    'text': chunk,
                    'chunk_index': i,
                    'tokens': self.count_tokens(chunk)
                }
                if metadata:
                    chunk_metadata.update(metadata)
                chunks_with_metadata.append(chunk_metadata)
        
        return chunks_with_metadata
    
    def identify_sections(self, text: str) -> List[Dict]:
        """Identify sections in the document based on common patterns"""
        sections = []
        
        # Common section patterns
        section_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headers
            r'^Chapter\s+\d+[:\s]+(.+)$',  # Chapter headings
            r'^Section\s+\d+[:\s]+(.+)$',  # Section headings
            r'^\d+\.\s+(.+)$',  # Numbered sections
            r'^[A-Z][A-Z\s]{2,}$',  # All caps headings
        ]
        
        lines = text.split('\n')
        current_section = None
        current_text = []
        section_index = 0
        
        for line in lines:
            is_header = False
            header_title = None
            
            for pattern in section_patterns:
                match = re.match(pattern, line.strip(), re.IGNORECASE)
                if match:
                    is_header = True
                    header_title = match.group(1) if match.groups() else line.strip()
                    break
            
            if is_header:
                # Save current section
                if current_section and current_text:
                    current_section['text'] = '\n'.join(current_text)
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': header_title,
                    'index': section_index,
                    'text': ''
                }
                current_text = []
                section_index += 1
            else:
                current_text.append(line)
        
        # Save last section
        if current_section and current_text:
            current_section['text'] = '\n'.join(current_text)
            sections.append(current_section)
        
        # If no sections found, return None
        if not sections:
            return None
        
        return sections
    
    def prepare_chunks_for_indexing(self, chunks: List[Dict], metadata: Dict = None) -> List[Dict]:
        """Format chunks for vector database indexing"""
        indexed_chunks = []
        
        for i, chunk in enumerate(chunks):
            if isinstance(chunk, str):
                chunk_data = {'text': chunk}
            else:
                chunk_data = chunk.copy()
            
            # Add indexing metadata
            chunk_data['id'] = f"{metadata.get('doc_id', 'doc')}_{i}" if metadata else f"chunk_{i}"
            chunk_data['index'] = i
            
            # Add document metadata
            if metadata:
                for key, value in metadata.items():
                    if key not in chunk_data:
                        chunk_data[key] = value
            
            # Ensure text field exists
            if 'text' not in chunk_data:
                logger.warning(f"Chunk {i} missing text field")
                continue
            
            indexed_chunks.append(chunk_data)
        
        return indexed_chunks
    
    def chunk_by_paragraphs(self, text: str, max_chunk_size: Optional[int] = None) -> List[str]:
        """Chunk text by paragraphs, combining small paragraphs"""
        max_chunk_size = max_chunk_size or self.chunk_size
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\n+', text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_tokens = self.count_tokens(para)
            
            if para_tokens > max_chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Split large paragraph
                para_chunks = self.chunk_text(para, max_chunk_size)
                chunks.extend(para_chunks)
            elif current_tokens + para_tokens > max_chunk_size:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_tokens = para_tokens
            else:
                # Add to current chunk
                current_chunk.append(para)
                current_tokens += para_tokens
        
        # Save last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def chunk_with_context_preservation(self, text: str, context_sentences: int = 2) -> List[Dict]:
        """Chunk text while preserving context from surrounding sentences"""
        sentences = self.split_into_sentences(text)
        chunks = []
        
        chunk_sentences = []
        chunk_tokens = 0
        
        for i, sentence in enumerate(sentences):
            sentence_tokens = self.count_tokens(sentence)
            
            if chunk_tokens + sentence_tokens > self.chunk_size:
                if chunk_sentences:
                    # Add context from previous sentences
                    start_idx = max(0, i - len(chunk_sentences) - context_sentences)
                    end_idx = min(len(sentences), i + context_sentences)
                    
                    context_before = sentences[start_idx:i-len(chunk_sentences)]
                    context_after = sentences[i:end_idx]
                    
                    chunk_data = {
                        'text': ' '.join(chunk_sentences),
                        'context_before': ' '.join(context_before),
                        'context_after': ' '.join(context_after),
                        'sentence_range': (i - len(chunk_sentences), i)
                    }
                    chunks.append(chunk_data)
                
                chunk_sentences = [sentence]
                chunk_tokens = sentence_tokens
            else:
                chunk_sentences.append(sentence)
                chunk_tokens += sentence_tokens
        
        # Add last chunk
        if chunk_sentences:
            start_idx = len(sentences) - len(chunk_sentences)
            context_before = sentences[max(0, start_idx - context_sentences):start_idx]
            
            chunk_data = {
                'text': ' '.join(chunk_sentences),
                'context_before': ' '.join(context_before),
                'context_after': '',
                'sentence_range': (start_idx, len(sentences))
            }
            chunks.append(chunk_data)
        
        return chunks

if __name__ == "__main__":
    # Test the chunker
    chunker = TextChunker(chunk_size=256, overlap=25)
    
    sample_text = """
    Chapter 1: Introduction to Machine Learning
    
    Machine learning is a subset of artificial intelligence that focuses on the development of algorithms 
    that can learn from and make predictions or decisions based on data. Unlike traditional programming, 
    where explicit instructions are provided for every scenario, machine learning systems improve their 
    performance through experience.
    
    Section 1.1: Types of Machine Learning
    
    There are three main types of machine learning: supervised learning, unsupervised learning, and 
    reinforcement learning. Supervised learning involves training a model on labeled data, where the 
    correct answers are provided. Unsupervised learning works with unlabeled data to find patterns 
    and structures. Reinforcement learning involves an agent learning to make decisions by receiving 
    rewards or penalties for its actions.
    
    Section 1.2: Applications
    
    Machine learning has numerous applications across various industries. In healthcare, it's used for 
    disease diagnosis and drug discovery. In finance, it powers fraud detection and algorithmic trading. 
    In technology, it enables recommendation systems, natural language processing, and computer vision.
    """
    
    # Test basic chunking
    chunks = chunker.chunk_text(sample_text)
    print(f"Basic chunking: {len(chunks)} chunks created")
    
    # Test smart chunking
    smart_chunks = chunker.smart_chunk(sample_text, {'source': 'test_document'})
    print(f"Smart chunking: {len(smart_chunks)} chunks created")
    
    # Test paragraph chunking
    para_chunks = chunker.chunk_by_paragraphs(sample_text)
    print(f"Paragraph chunking: {len(para_chunks)} chunks created")