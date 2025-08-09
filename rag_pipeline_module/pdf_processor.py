"""
PDF processor for extracting text and metadata from PDF files
"""

import os
import logging
from typing import List, Dict, Tuple, Optional
import PyPDF2
import pdfplumber
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.supported_extensions = ['.pdf']
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a PDF file"""
        try:
            text = ""
            
            # Try pdfplumber first (better for complex layouts)
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                            
                if text.strip():
                    logger.info(f"Successfully extracted text using pdfplumber from: {pdf_path}")
                    return text
                    
            except Exception as e:
                logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    try:
                        pdf_reader.decrypt('')  # Try empty password
                    except:
                        logger.error(f"PDF is encrypted and cannot be decrypted: {pdf_path}")
                        return ""
                
                num_pages = len(pdf_reader.pages)
                logger.info(f"Processing {num_pages} pages from: {pdf_path}")
                
                for page_num in range(num_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num}: {e}")
                        continue
            
            logger.info(f"Successfully extracted {len(text)} characters from: {pdf_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def extract_with_metadata(self, pdf_path: str) -> Dict:
        """Extract text with page numbers and metadata"""
        try:
            result = {
                'filepath': pdf_path,
                'filename': os.path.basename(pdf_path),
                'pages': [],
                'metadata': {},
                'total_pages': 0,
                'total_text_length': 0
            }
            
            # Try pdfplumber for better extraction
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    result['total_pages'] = len(pdf.pages)
                    
                    # Extract metadata
                    if pdf.metadata:
                        result['metadata'] = {
                            'title': pdf.metadata.get('Title', ''),
                            'author': pdf.metadata.get('Author', ''),
                            'subject': pdf.metadata.get('Subject', ''),
                            'creator': pdf.metadata.get('Creator', ''),
                            'producer': pdf.metadata.get('Producer', ''),
                            'creation_date': str(pdf.metadata.get('CreationDate', '')),
                            'modification_date': str(pdf.metadata.get('ModDate', ''))
                        }
                    
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            page_data = {
                                'page_number': i + 1,
                                'text': page_text,
                                'text_length': len(page_text)
                            }
                            result['pages'].append(page_data)
                            result['total_text_length'] += len(page_text)
                    
                    if result['pages']:
                        logger.info(f"Extracted {len(result['pages'])} pages with metadata from: {pdf_path}")
                        return result
                        
            except Exception as e:
                logger.warning(f"pdfplumber failed for metadata extraction, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if pdf_reader.is_encrypted:
                    try:
                        pdf_reader.decrypt('')
                    except:
                        logger.error(f"PDF is encrypted: {pdf_path}")
                        return result
                
                result['total_pages'] = len(pdf_reader.pages)
                
                # Extract metadata
                if pdf_reader.metadata:
                    result['metadata'] = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                        'modification_date': str(pdf_reader.metadata.get('/ModDate', ''))
                    }
                
                for page_num in range(result['total_pages']):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            page_data = {
                                'page_number': page_num + 1,
                                'text': page_text,
                                'text_length': len(page_text)
                            }
                            result['pages'].append(page_data)
                            result['total_text_length'] += len(page_text)
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num}: {e}")
                        continue
            
            logger.info(f"Extracted {len(result['pages'])} pages with metadata from: {pdf_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting with metadata from {pdf_path}: {e}")
            return {
                'filepath': pdf_path,
                'filename': os.path.basename(pdf_path),
                'pages': [],
                'metadata': {},
                'total_pages': 0,
                'total_text_length': 0
            }
    
    def extract_chapters(self, pdf_path: str) -> List[Dict]:
        """Try to extract chapter structure from PDF"""
        try:
            chapters = []
            current_chapter = None
            
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # Look for chapter headings (common patterns)
                    lines = text.split('\n')
                    for line in lines[:10]:  # Check first 10 lines of each page
                        line = line.strip()
                        if any(pattern in line.upper() for pattern in ['CHAPTER', 'SECTION', 'PART']):
                            if current_chapter:
                                chapters.append(current_chapter)
                            current_chapter = {
                                'title': line,
                                'start_page': i + 1,
                                'text': text
                            }
                            break
                    else:
                        if current_chapter:
                            current_chapter['text'] += '\n' + text
                
                if current_chapter:
                    chapters.append(current_chapter)
            
            logger.info(f"Extracted {len(chapters)} chapters from: {pdf_path}")
            return chapters
            
        except Exception as e:
            logger.warning(f"Could not extract chapters: {e}")
            return []
    
    def process_all_pdfs(self, directory: str) -> List[Dict]:
        """Batch process all PDFs in a directory"""
        try:
            results = []
            pdf_files = [f for f in os.listdir(directory) 
                        if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                logger.warning(f"No PDF files found in: {directory}")
                return results
            
            logger.info(f"Processing {len(pdf_files)} PDF files...")
            
            for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
                pdf_path = os.path.join(directory, pdf_file)
                
                # Skip metadata files
                if '_metadata.json' in pdf_file:
                    continue
                
                try:
                    # Extract with metadata
                    pdf_data = self.extract_with_metadata(pdf_path)
                    
                    if pdf_data['pages']:
                        # Try to extract chapters
                        chapters = self.extract_chapters(pdf_path)
                        if chapters:
                            pdf_data['chapters'] = chapters
                        
                        results.append(pdf_data)
                        logger.info(f"Successfully processed: {pdf_file}")
                    else:
                        logger.warning(f"No text extracted from: {pdf_file}")
                        
                except Exception as e:
                    logger.error(f"Error processing {pdf_file}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(results)} PDF files")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return []
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """Validate if a PDF file is readable and not corrupted"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if we can read basic info
                num_pages = len(pdf_reader.pages)
                if num_pages == 0:
                    return False
                
                # Try to read first page
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()
                
                return len(text) > 0
                
        except Exception as e:
            logger.error(f"PDF validation failed for {pdf_path}: {e}")
            return False
    
    def get_pdf_info(self, pdf_path: str) -> Dict:
        """Get basic information about a PDF file"""
        try:
            info = {
                'filepath': pdf_path,
                'filename': os.path.basename(pdf_path),
                'file_size': os.path.getsize(pdf_path),
                'is_valid': False,
                'num_pages': 0,
                'has_text': False,
                'is_encrypted': False
            }
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                info['is_encrypted'] = pdf_reader.is_encrypted
                info['num_pages'] = len(pdf_reader.pages)
                
                if not info['is_encrypted']:
                    # Check if has extractable text
                    for page_num in range(min(5, info['num_pages'])):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        if text and len(text.strip()) > 10:
                            info['has_text'] = True
                            break
                
                info['is_valid'] = info['num_pages'] > 0
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info for {pdf_path}: {e}")
            return {
                'filepath': pdf_path,
                'filename': os.path.basename(pdf_path),
                'file_size': 0,
                'is_valid': False,
                'num_pages': 0,
                'has_text': False,
                'is_encrypted': False,
                'error': str(e)
            }

if __name__ == "__main__":
    # Test the PDF processor
    processor = PDFProcessor()
    
    # Test with a single PDF if it exists
    test_pdf = "documents/test.pdf"
    if os.path.exists(test_pdf):
        # Test basic extraction
        text = processor.extract_text_from_pdf(test_pdf)
        print(f"Extracted {len(text)} characters")
        
        # Test extraction with metadata
        data = processor.extract_with_metadata(test_pdf)
        print(f"Pages: {data['total_pages']}, Text length: {data['total_text_length']}")
        
        # Test validation
        is_valid = processor.validate_pdf(test_pdf)
        print(f"PDF is valid: {is_valid}")
    else:
        print("No test PDF found. Processing all PDFs in documents folder...")
        results = processor.process_all_pdfs("documents")
        print(f"Processed {len(results)} PDFs")