"""
Legal Educational Content Scraper
Scrapes content from legitimate, open-access educational sources
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import json
import logging
from urllib.parse import urljoin, quote
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict, Optional
import arxiv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalEducationalScraper:
    """
    Scrapes educational content from legal, open-access sources:
    - MIT OpenCourseWare
    - arXiv research papers
    - Wikipedia articles
    - Project Gutenberg books
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Educational-RAG-Pipeline/1.0 (Academic Research Tool)'
        }
        self.session.headers.update(self.headers)
        
        # Legal source configurations
        self.sources = {
            'mit_ocw': {
                'base_url': 'https://ocw.mit.edu',
                'search_url': 'https://ocw.mit.edu/search/',
                'enabled': True
            },
            'arxiv': {
                'enabled': True,
                'max_results': 10
            },
            'wikipedia': {
                'enabled': True,
                'max_articles': 5
            },
            'gutenberg': {
                'base_url': 'https://www.gutenberg.org',
                'enabled': True
            }
        }
    
    def scrape_all_sources(self, topic: str, max_items: int = 10) -> List[Dict]:
        """
        Scrape content from all enabled legal sources
        
        Args:
            topic: The topic to search for
            max_items: Maximum items to retrieve per source
            
        Returns:
            List of scraped content items
        """
        all_content = []
        
        logger.info(f"Scraping educational content for topic: {topic}")
        
        # Scrape MIT OCW
        if self.sources['mit_ocw']['enabled']:
            ocw_content = self.scrape_mit_ocw(topic, max_items=max_items//3)
            all_content.extend(ocw_content)
        
        # Scrape arXiv papers
        if self.sources['arxiv']['enabled']:
            arxiv_content = self.scrape_arxiv(topic, max_results=max_items//3)
            all_content.extend(arxiv_content)
        
        # Scrape Wikipedia
        if self.sources['wikipedia']['enabled']:
            wiki_content = self.scrape_wikipedia(topic, max_articles=max_items//3)
            all_content.extend(wiki_content)
        
        logger.info(f"Total content items scraped: {len(all_content)}")
        return all_content
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def scrape_mit_ocw(self, topic: str, max_items: int = 5) -> List[Dict]:
        """
        Scrape MIT OpenCourseWare for educational content
        
        Args:
            topic: The topic to search for
            max_items: Maximum number of courses to retrieve
            
        Returns:
            List of course content dictionaries
        """
        content_items = []
        
        try:
            logger.info(f"Searching MIT OCW for: {topic}")
            
            # Search MIT OCW
            search_url = f"https://ocw.mit.edu/search/?q={quote(topic)}"
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find course cards
            course_cards = soup.find_all('div', class_='course-card') or \
                          soup.find_all('article', class_='search-result')
            
            for card in course_cards[:max_items]:
                try:
                    # Extract course info
                    title_elem = card.find('h2') or card.find('h3') or card.find('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    # Get course link
                    link_elem = card.find('a', href=True)
                    if link_elem:
                        course_url = urljoin('https://ocw.mit.edu', link_elem['href'])
                        
                        # Scrape course page for content
                        course_content = self._scrape_ocw_course_page(course_url, title)
                        if course_content:
                            content_items.append(course_content)
                    
                    # Be respectful with rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Error processing MIT OCW course: {e}")
                    continue
            
            logger.info(f"Scraped {len(content_items)} items from MIT OCW")
            
        except Exception as e:
            logger.error(f"Error scraping MIT OCW: {e}")
        
        return content_items
    
    def _scrape_ocw_course_page(self, course_url: str, title: str) -> Optional[Dict]:
        """Helper to scrape individual MIT OCW course page"""
        try:
            response = self.session.get(course_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract course description and content
            description = ""
            desc_elem = soup.find('div', class_='course-description') or \
                       soup.find('section', class_='description')
            if desc_elem:
                description = desc_elem.text.strip()
            
            # Look for syllabus or lecture notes
            content_text = description
            
            # Find downloadable resources
            resource_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(ext in href.lower() for ext in ['.pdf', '.txt', '.html']):
                    resource_links.append(urljoin(course_url, href))
            
            return {
                'title': title,
                'source': 'MIT OpenCourseWare',
                'url': course_url,
                'content': content_text[:5000],  # Limit content size
                'type': 'course',
                'metadata': {
                    'resource_links': resource_links[:5],
                    'source_type': 'educational_course'
                }
            }
            
        except Exception as e:
            logger.warning(f"Error scraping OCW course page: {e}")
            return None
    
    def scrape_arxiv(self, topic: str, max_results: int = 5) -> List[Dict]:
        """
        Search and retrieve papers from arXiv using their official API
        
        Args:
            topic: The topic to search for
            max_results: Maximum number of papers to retrieve
            
        Returns:
            List of paper dictionaries
        """
        content_items = []
        
        try:
            logger.info(f"Searching arXiv for: {topic}")
            
            # Search arXiv using the official API
            search = arxiv.Search(
                query=topic,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            for paper in search.results():
                try:
                    # Create content item from paper
                    content_item = {
                        'title': paper.title,
                        'source': 'arXiv',
                        'url': paper.entry_id,
                        'content': paper.summary,
                        'type': 'research_paper',
                        'metadata': {
                            'authors': [author.name for author in paper.authors],
                            'published': str(paper.published),
                            'categories': paper.categories,
                            'pdf_url': paper.pdf_url,
                            'source_type': 'academic_paper'
                        }
                    }
                    
                    content_items.append(content_item)
                    
                except Exception as e:
                    logger.warning(f"Error processing arXiv paper: {e}")
                    continue
            
            logger.info(f"Retrieved {len(content_items)} papers from arXiv")
            
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
        
        return content_items
    
    def scrape_wikipedia(self, topic: str, max_articles: int = 3) -> List[Dict]:
        """
        Scrape Wikipedia articles related to the topic using REST API
        
        Args:
            topic: The topic to search for
            max_articles: Maximum number of articles to retrieve
            
        Returns:
            List of article content dictionaries
        """
        content_items = []
        
        try:
            logger.info(f"Searching Wikipedia for: {topic}")
            
            # Search Wikipedia using REST API
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': topic,
                'srlimit': max_articles * 2
            }
            
            response = self.session.get(search_url, params=search_params, timeout=30)
            response.raise_for_status()
            search_data = response.json()
            
            # Get search results
            search_results = search_data.get('query', {}).get('search', [])
            
            for result in search_results[:max_articles]:
                try:
                    page_title = result['title']
                    
                    # Get page content using REST API
                    content_params = {
                        'action': 'query',
                        'format': 'json',
                        'titles': page_title,
                        'prop': 'extracts|info',
                        'exintro': True,
                        'explaintext': True,
                        'exlimit': 1,
                        'inprop': 'url'
                    }
                    
                    content_response = self.session.get(search_url, params=content_params, timeout=30)
                    content_response.raise_for_status()
                    content_data = content_response.json()
                    
                    # Extract page data
                    pages = content_data.get('query', {}).get('pages', {})
                    for page_id, page_info in pages.items():
                        if page_id != '-1':  # Valid page
                            content = page_info.get('extract', '')[:5000]  # Limit content
                            
                            content_item = {
                                'title': page_info.get('title', page_title),
                                'source': 'Wikipedia',
                                'url': page_info.get('fullurl', f'https://en.wikipedia.org/wiki/{quote(page_title)}'),
                                'content': content,
                                'type': 'encyclopedia_article',
                                'metadata': {
                                    'page_id': page_id,
                                    'source_type': 'reference_article'
                                }
                            }
                            
                            content_items.append(content_item)
                            break
                    
                    # Be respectful with rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Error processing Wikipedia page {page_title}: {e}")
                    continue
            
            logger.info(f"Scraped {len(content_items)} Wikipedia articles")
            
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {e}")
        
        return content_items
    
    def save_content(self, content_items: List[Dict], directory: str = "documents") -> List[str]:
        """
        Save scraped content to files
        
        Args:
            content_items: List of content dictionaries
            directory: Directory to save files to
            
        Returns:
            List of saved file paths
        """
        os.makedirs(directory, exist_ok=True)
        saved_files = []
        
        for item in content_items:
            try:
                # Create safe filename
                safe_title = "".join(c for c in item['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title[:100]  # Limit length
                
                # Save as JSON for now (can be converted to other formats)
                filename = f"{safe_title}_{item['source']}.json"
                filepath = os.path.join(directory, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(item, f, indent=2, ensure_ascii=False)
                
                saved_files.append(filepath)
                logger.info(f"Saved: {filename}")
                
            except Exception as e:
                logger.error(f"Error saving content item: {e}")
                continue
        
        return saved_files
    
    def download_arxiv_pdf(self, pdf_url: str, filename: str, directory: str = "documents") -> Optional[str]:
        """
        Download arXiv PDF (completely legal as arXiv provides open access)
        
        Args:
            pdf_url: URL to the PDF
            filename: Name to save the file as
            directory: Directory to save to
            
        Returns:
            Path to downloaded file or None
        """
        try:
            os.makedirs(directory, exist_ok=True)
            filepath = os.path.join(directory, filename)
            
            if os.path.exists(filepath):
                logger.info(f"File already exists: {filepath}")
                return filepath
            
            logger.info(f"Downloading arXiv paper: {filename}")
            
            response = requests.get(pdf_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as file:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            pbar.update(len(chunk))
            
            logger.info(f"Downloaded successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading arXiv PDF: {e}")
            return None


# Keep the old class name for backward compatibility but use legal scraper
class BookScraper(LegalEducationalScraper):
    """Backward compatibility wrapper - now uses legal sources only"""
    
    def scrape_topic(self, topic: str, max_books: int = 3) -> List[Dict]:
        """
        Main orchestrator function - now scrapes from legal sources
        
        Args:
            topic: Topic to search for
            max_books: Maximum content items to retrieve
            
        Returns:
            List of content items
        """
        # Scrape from all legal sources
        content_items = self.scrape_all_sources(topic, max_items=max_books)
        
        # Download any arXiv PDFs
        downloaded_items = []
        for item in content_items:
            if item['source'] == 'arXiv' and 'pdf_url' in item.get('metadata', {}):
                # Download the PDF
                safe_title = "".join(c for c in item['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title[:50]}.pdf"
                filepath = self.download_arxiv_pdf(
                    item['metadata']['pdf_url'],
                    filename
                )
                if filepath:
                    item['filepath'] = filepath
            
            downloaded_items.append(item)
        
        # Save all content as JSON as well
        self.save_content(downloaded_items)
        
        return downloaded_items
    
    def search_books(self, topic: str, max_results: int = 3) -> List[Dict]:
        """Backward compatibility - search for educational content"""
        content = self.scrape_all_sources(topic, max_items=max_results)
        # Format as "books" for compatibility
        books = []
        for item in content:
            books.append({
                'title': item['title'],
                'author': item.get('metadata', {}).get('authors', ['Unknown'])[0] if item.get('metadata', {}).get('authors') else 'Unknown',
                'url': item['url']
            })
        return books


if __name__ == "__main__":
    # Test the legal scraper
    scraper = LegalEducationalScraper()
    
    # Test all sources
    results = scraper.scrape_all_sources("machine learning", max_items=6)
    
    print(f"\nScraped {len(results)} educational items:")
    for item in results:
        print(f"  - [{item['source']}] {item['title'][:60]}...")
    
    # Save the content
    saved = scraper.save_content(results)
    print(f"\nSaved {len(saved)} files")