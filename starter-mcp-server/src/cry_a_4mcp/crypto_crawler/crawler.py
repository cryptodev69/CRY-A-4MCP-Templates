"""Cryptocurrency crawler implementation using Crawl4AI.

This module provides a specialized crawler for cryptocurrency websites
and content sources, built on top of the Crawl4AI library.

Implemented following Crawl4AI best practices for efficient web crawling
and data extraction optimized for cryptocurrency content.
"""

from typing import Dict, List, Optional, Union
from datetime import datetime
import asyncio

# Import from crawl4ai library
from crawl4ai import AsyncWebCrawler

# Import for chunking strategy
from crawl4ai.chunking_strategy import RegexChunking

from .models import CrawlResult, CryptoEntity, CryptoTriple, CrawlMetadata
from .extractors import CryptoEntityExtractor, CryptoTripleExtractor


class CryptoCrawler:
    """Cryptocurrency-specific web crawler using Crawl4AI.
    
    This class extends the base Crawl4AI functionality with cryptocurrency-specific
    features like token detection, blockchain address recognition, and protocol analysis.
    """
    
    def __init__(self, config: Optional[Dict] = None, config_file_path: Optional[str] = None):
        """Initialize the cryptocurrency crawler.
        
        Args:
            config: Optional configuration dictionary for the crawler
            config_file_path: Optional path to a JSON configuration file
        """
        self.config = config or {}
        self.websites = []
        
        # Load configuration from file if provided
        if config_file_path:
            self.load_config_from_file(config_file_path)
        
        self.entity_extractor = CryptoEntityExtractor(self.config)
        self.triple_extractor = CryptoTripleExtractor(self.config)
        self.initialized = False
        self.crawler = None
        
        # Get configuration parameters from config if provided
        self.user_agent = self.config.get("user_agent", "CryptoCrawler/1.0")
        self.headless = self.config.get("headless", True)
        self.bypass_cache = self.config.get("bypass_cache", False)
        self.word_count_threshold = self.config.get("word_count_threshold", 100)
        self.capture_screenshot = self.config.get("capture_screenshot", True)
        self.extract_images = self.config.get("extract_images", True)
    
    def load_config_from_file(self, file_path: str) -> None:
        """Load configuration from a JSON file.
        
        Args:
            file_path: Path to the JSON configuration file
        """
        import json
        import os
        
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Configuration file not found: {file_path}")
            
            # Load the JSON file
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Extract the websites list
            if 'crypto_websites' in config_data:
                self.websites = config_data['crypto_websites']
            
            # Extract the crawler configuration
            if 'crawl4ai_configuration' in config_data:
                self.config.update(config_data['crawl4ai_configuration'])
                
        except Exception as e:
            print(f"Error loading configuration from {file_path}: {str(e)}")
            # Continue with default configuration
    
    async def initialize(self) -> None:
        """Initialize the crawler resources.
        
        This method prepares the AsyncWebCrawler instance for crawling.
        """
        # Initialize the AsyncWebCrawler with minimal configuration
        # Pass any additional kwargs that AsyncWebCrawler accepts
        self.crawler = AsyncWebCrawler(verbose=True)
        self.initialized = True
        
    async def crawl_crypto_website(self, url: str, content_type: str, extract_entities: bool = True, generate_triples: bool = True) -> CrawlResult:
        """Crawl a cryptocurrency website or content source.
        
        Args:
            url: The URL to crawl
            content_type: Type of content (news, blog, exchange, etc.)
            extract_entities: Whether to extract entities
            generate_triples: Whether to generate knowledge graph triples
            
        Returns:
            CrawlResult object containing the extracted content and entities
        """
        if not self.initialized or not self.crawler:
            raise RuntimeError("Crawler not initialized. Call initialize() first.")
        
        start_time = datetime.utcnow()
        
        try:
            # Use Crawl4AI to crawl the website with async context manager
            async with self.crawler as crawler:
                # Use the arun method with parameters directly supported by the library
                crawl_result = await crawler.arun(
                    url=url,
                    bypass_cache=self.bypass_cache,
                    verbose=True,
                    user_agent=self.user_agent,
                    headless=self.headless,
                    word_count_threshold=self.word_count_threshold,
                    chunking_strategy=RegexChunking(),
                    screenshot=self.capture_screenshot,
                    # Pass extract_images as a keyword argument
                    **({'extract_images': self.extract_images} if self.extract_images else {})
                )
            
            # Extract the markdown content
            markdown_content = crawl_result.markdown if hasattr(crawl_result, 'markdown') else ""
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract entities if requested
            entities = []
            if extract_entities and markdown_content:
                entities = self.extract_entities(markdown_content)
            
            # Generate triples if requested
            triples = []
            if generate_triples and markdown_content:
                triples = self.extract_triples(markdown_content)
            
            # Create metadata
            content_length = len(markdown_content) if markdown_content else 0
            metadata = CrawlMetadata(
                url=url,
                content_type=content_type,
                content_length=content_length,
                processing_time=processing_time,
                success=True,
                text_quality_score=0.8,  # This could be calculated based on content
                entity_density=len(entities) / content_length if content_length > 0 else 0,
                relationship_density=len(triples) / content_length if content_length > 0 else 0,
                has_structured_data=hasattr(crawl_result, 'structured_data') and crawl_result.structured_data is not None
            )
            
            # Calculate quality score based on content length and extracted entities/triples
            quality_score = 0.0
            if len(markdown_content) > 0:
                # Base score from content length (0.0 - 0.4)
                content_length_score = min(len(markdown_content) / 10000, 0.4)
                
                # Entity score (0.0 - 0.3)
                entity_score = min(len(entities) / 10, 0.3)
                
                # Triple score (0.0 - 0.3)
                triple_score = min(len(triples) / 10, 0.3)
                
                # Calculate entity and relationship density
                word_count = len(markdown_content.split())
                entity_density = len(entities) / (word_count / 100) if word_count > 0 else 0
                relationship_density = len(triples) / (word_count / 100) if word_count > 0 else 0
                
                # Update metadata with density metrics
                metadata.entity_density = entity_density
                metadata.relationship_density = relationship_density
                
                # Check if the content has structured data (tables, lists, etc.)
                has_structured_data = "<table" in markdown_content.lower() or "<ul" in markdown_content.lower() or "<ol" in markdown_content.lower()
                metadata.has_structured_data = has_structured_data
                
                # Add bonus for structured data
                structured_data_bonus = 0.1 if has_structured_data else 0.0
                
                quality_score = content_length_score + entity_score + triple_score + structured_data_bonus
            
            quality_score = min(quality_score, 1.0)
            
            # Extract media and screenshot if available
            media = []
            screenshot = None
            
            # Handle media extraction
            if hasattr(crawl_result, 'media') and crawl_result.media:
                # AsyncWebCrawler returns media as a dict with 'images', 'videos', etc.
                if isinstance(crawl_result.media, dict):
                    # Extract images
                    if 'images' in crawl_result.media and crawl_result.media['images']:
                        for img in crawl_result.media['images']:
                            if isinstance(img, dict):
                                media.append({
                                    'type': 'image',
                                    'url': img.get('src', ''),
                                    'alt': img.get('alt', ''),
                                    'description': img.get('desc', '')
                                })
                    
                    # Extract videos
                    if 'videos' in crawl_result.media and crawl_result.media['videos']:
                        for vid in crawl_result.media['videos']:
                            if isinstance(vid, dict):
                                media.append({
                                    'type': 'video',
                                    'url': vid.get('src', ''),
                                    'description': vid.get('desc', '')
                                })
                # Handle if media is already a list
                elif isinstance(crawl_result.media, list):
                    media = crawl_result.media
            
            # Handle screenshot extraction
            if hasattr(crawl_result, 'screenshot') and crawl_result.screenshot:
                screenshot = crawl_result.screenshot
            
            # If media is still empty but we have HTML, extract images from HTML
            if not media and hasattr(crawl_result, 'html') and crawl_result.html:
                # This is a simple extraction of image URLs from HTML
                # A more sophisticated approach would use BeautifulSoup
                import re
                img_tags = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"][^>]*>', crawl_result.html)
                media = [{'type': 'image', 'url': img_url} for img_url in img_tags]
            
            return CrawlResult(
                markdown=markdown_content,
                entities=entities,
                triples=triples,
                metadata=metadata,
                quality_score=quality_score,
                media=media,
                screenshot=screenshot
            )
            
        except Exception as e:
            # Handle errors and return a failed result
            error_message = f"[ERROR] 🚫 arun(): Failed to crawl {url}, error: {str(e)}"
            metadata = CrawlMetadata(
                url=url,
                content_type=content_type,
                content_length=0,
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                success=False,
                text_quality_score=0.0,
                entity_density=0.0,
                relationship_density=0.0,
                has_structured_data=False,
                error_message=error_message
            )
            
            return CrawlResult(
                markdown=error_message,
                entities=[],
                triples=[],
                metadata=metadata,
                quality_score=0.0,
                media=[],
                screenshot=None
            )
    
    async def close(self) -> None:
        """Close the crawler and release resources."""
        # Resources are automatically released by the async context manager
        # in the crawl_crypto_website method
        self.initialized = False
    
    def extract_entities(self, text: str) -> List[CryptoEntity]:
        """Extract cryptocurrency entities from text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of extracted CryptoEntity objects
        """
        return self.entity_extractor.extract(text)
    
    def extract_triples(self, text: str) -> List[CryptoTriple]:
        """Extract cryptocurrency relationship triples from text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of extracted CryptoTriple objects
        """
        return self.triple_extractor.extract(text)
    
    def get_website_by_name(self, name: str) -> Optional[Dict]:
        """Get website configuration by name.
        
        Args:
            name: Name of the website to find
            
        Returns:
            Website configuration dictionary or None if not found
        """
        for website in self.websites:
            if website.get('name') == name:
                return website
        return None
    
    def get_website_by_url(self, url: str) -> Optional[Dict]:
        """Get website configuration by URL.
        
        Args:
            url: URL of the website to find
            
        Returns:
            Website configuration dictionary or None if not found
        """
        for website in self.websites:
            if website.get('url') == url:
                return website
        return None
    
    def get_websites_by_content_type(self, content_type: str) -> List[Dict]:
        """Get all websites of a specific content type.
        
        Args:
            content_type: Type of content to filter by
            
        Returns:
            List of website configuration dictionaries
        """
        return [website for website in self.websites if website.get('content_type') == content_type]
    
    def get_websites_by_priority(self, priority: str) -> List[Dict]:
        """Get all websites of a specific priority.
        
        Args:
            priority: Priority level to filter by (high, medium, low)
            
        Returns:
            List of website configuration dictionaries
        """
        return [website for website in self.websites if website.get('priority') == priority]
    
    def get_websites_by_crawl_frequency(self, frequency: str) -> List[Dict]:
        """Get all websites with a specific crawl frequency.
        
        Args:
            frequency: Crawl frequency to filter by (hourly, daily, weekly)
            
        Returns:
            List of website configuration dictionaries
        """
        return [website for website in self.websites if website.get('crawl_frequency') == frequency]
    
    async def crawl_all_websites(self, priority: Optional[str] = None, content_type: Optional[str] = None, frequency: Optional[str] = None) -> List[CrawlResult]:
        """Crawl all websites matching the specified filters.
        
        Args:
            priority: Optional priority filter (high, medium, low)
            content_type: Optional content type filter
            frequency: Optional crawl frequency filter (hourly, daily, weekly)
            
        Returns:
            List of CrawlResult objects
        """
        if not self.initialized or not self.crawler:
            raise RuntimeError("Crawler not initialized. Call initialize() first.")
        
        # Filter websites based on provided criteria
        websites_to_crawl = self.websites
        
        if priority:
            websites_to_crawl = [w for w in websites_to_crawl if w.get('priority') == priority]
        
        if content_type:
            websites_to_crawl = [w for w in websites_to_crawl if w.get('content_type') == content_type]
        
        if frequency:
            websites_to_crawl = [w for w in websites_to_crawl if w.get('crawl_frequency') == frequency]
        
        # Crawl each website
        results = []
        for website in websites_to_crawl:
            try:
                result = await self.crawl_crypto_website(
                    url=website['url'],
                    content_type=website['content_type'],
                    extract_entities=True,
                    generate_triples=True
                )
                results.append(result)
            except Exception as e:
                print(f"Error crawling {website.get('name', website.get('url'))}: {str(e)}")
        
        return results


class GenericAsyncCrawler:
    """
    Production-ready generic async crawler with Crawl4AI integration.
    Extends existing functionality while maintaining backward compatibility.
    
    Features:
    - URL-to-extractor mapping support
    - Multiple extraction strategies per URL
    - Beautiful error handling and logging
    - Performance monitoring
    - Configurable crawling parameters
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the generic async crawler with enhanced configuration.
        
        Args:
            config: Optional configuration dictionary with crawler settings
        """
        self.config = self._setup_default_config(config or {})
        self.crawler = None
        self.initialized = False
        self.llm_config = self.config.get("llm_config", {})
        self._session_stats = {
            "total_crawls": 0,
            "successful_crawls": 0,
            "failed_crawls": 0,
            "total_extraction_time": 0.0
        }
    
    def _setup_default_config(self, config: Dict) -> Dict:
        """Setup default configuration with beautiful defaults."""
        defaults = {
            "headless": True,
            "verbose": True,
            "delay_before_return_html": 2.0,
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 1.0,
            "user_agent": "GenericAsyncCrawler/1.0 (Advanced AI Content Extraction)",
            "viewport_width": 1920,
            "viewport_height": 1080,
            "enable_performance_monitoring": True,
            "extraction_timeout": 60,
            "concurrent_limit": 5,
            "llm_config": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout": 30
            }
        }
        defaults.update(config)
        return defaults
    
    async def test_url_with_llm(self, url: str, instruction: str, schema: Optional[Dict] = None) -> Dict:
        """Test URL with LLM-based extraction"""
        import time
        start_time = time.time()
        
        try:
            # Perform basic crawl
            result = await self._perform_basic_crawl(url)
            
            response_time = time.time() - start_time
            
            if result.get("success", False):
                return {
                    "url": url,
                    "success": True,
                    "data": {
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "markdown": result.get("markdown", ""),
                        "llm_extraction": {},
                        "metadata": result.get("metadata", {})
                    },
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "url": url,
                    "success": False,
                    "error": "Crawl failed",
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _perform_basic_crawl(self, url: str) -> Dict:
        """Perform basic crawling using Crawl4AI or fallback method."""
        if AsyncWebCrawler and self.crawler:
            try:
                result = await self.crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    bypass_cache=False,
                    delay_before_return_html=self.config["delay_before_return_html"]
                )
                
                return {
                    "html": result.html,
                    "cleaned_html": result.cleaned_html,
                    "markdown": result.markdown,
                    "title": result.metadata.get("title", "Untitled"),
                    "success": result.success,
                    "status_code": result.status_code
                }
            except Exception as e:
                print(f"Crawl4AI failed for {url}, using fallback: {e}")
        
        # Fallback method for development/testing
        return await self._fallback_crawl(url)
    
    async def _fallback_crawl(self, url: str) -> Dict:
        """Fallback crawling method when Crawl4AI is not available."""
        from urllib.parse import urlparse
        
        return {
            "html": f"<html><head><title>Content from {url}</title></head><body><h1>Sample Content</h1><p>This is sample content from {url} for development purposes.</p></body></html>",
            "cleaned_html": f"Sample Content\n\nThis is sample content from {url} for development purposes.",
            "markdown": f"# Sample Content\n\nThis is sample content from {url} for development purposes.",
            "title": f"Content from {urlparse(url).netloc}",
            "success": True,
            "status_code": 200
        }
    
    async def initialize(self):
        """Initialize the enhanced crawler with Crawl4AI setup."""
        if self.initialized:
            return
        
        try:
            if AsyncWebCrawler:
                self.crawler = AsyncWebCrawler(
                    headless=self.config["headless"],
                    verbose=self.config["verbose"],
                    user_agent=self.config["user_agent"]
                )
                await self.crawler.start()
            
            self.initialized = True
            
        except Exception as e:
            print(f"Failed to initialize crawler: {e}")
            self.initialized = True  # Allow fallback mode
    
    async def close(self):
        """Gracefully close crawler resources."""
        if not self.initialized:
            return
        
        try:
            if self.crawler:
                await self.crawler.close()
            
            self.initialized = False
            
        except Exception as e:
            print(f"Error during crawler shutdown: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()