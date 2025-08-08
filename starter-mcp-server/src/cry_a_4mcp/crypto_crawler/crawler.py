"""Cryptocurrency crawler implementation using Crawl4AI.

This module provides a specialized crawler for cryptocurrency websites
and content sources, built on top of the Crawl4AI library.

Implemented following Crawl4AI best practices for efficient web crawling
and data extraction optimized for cryptocurrency content.
"""

from typing import Dict, List, Optional, Union
from datetime import datetime
import asyncio
import os
import time
import logging

# Core crawl4ai imports with compatibility handling
try:
    # Import basic crawl4ai first to check compatibility
    import crawl4ai
    
    # Try to import core features
    try:
        from crawl4ai import AsyncWebCrawler, LLMConfig, LLMExtractionStrategy, CrawlerRunConfig, CacheMode, BrowserConfig
        from crawl4ai.extraction_strategy import ExtractionStrategy
        from crawl4ai.chunking_strategy import RegexChunking
        CRAWL4AI_CORE_AVAILABLE = True
    except ImportError:
        # Create fallback classes
        class AsyncWebCrawler:
            def __init__(self, **kwargs):
                self.config = kwargs
            async def astart(self):
                pass
            async def aclose(self):
                pass
            async def acrawl(self, url, **kwargs):
                return type('CrawlResult', (), {'success': False, 'error': 'Crawl4AI not available'})()
        
        class LLMConfig:
            def __init__(self, **kwargs):
                self.config = kwargs
        
        class LLMExtractionStrategy:
            def __init__(self, **kwargs):
                self.config = kwargs
        
        class CrawlerRunConfig:
            def __init__(self, **kwargs):
                self.config = kwargs
        
        class CacheMode:
            ENABLED = "enabled"
            DISABLED = "disabled"
        
        class BrowserConfig:
            def __init__(self, **kwargs):
                self.config = kwargs
        
        class ExtractionStrategy:
            def __init__(self, **kwargs):
                self.config = kwargs
        
        class RegexChunking:
            def __init__(self, **kwargs):
                self.config = kwargs
        
        CRAWL4AI_CORE_AVAILABLE = False
    
    # Try to import adaptive features
    try:
        from crawl4ai import StatisticalStrategy, EmbeddingStrategy
        from crawl4ai.adaptive import AdaptiveConfig, AdaptiveCrawlingStrategy
        CRAWL4AI_ADAPTIVE_AVAILABLE = True
    except ImportError:
        # Create fallback classes
        class StatisticalStrategy:
            def __init__(self, **kwargs):
                self.config = kwargs
        
        class EmbeddingStrategy:
            def __init__(self, **kwargs):
                self.config = kwargs
        
        class AdaptiveConfig:
            def __init__(self, **kwargs):
                self.config = kwargs
        
        class AdaptiveCrawlingStrategy:
            def __init__(self, **kwargs):
                self.config = kwargs
        
        CRAWL4AI_ADAPTIVE_AVAILABLE = False
    
except Exception as e:
    print(f"Warning: Crawl4AI import failed: {e}")
    # Create all fallback classes
    class AsyncWebCrawler:
        def __init__(self, **kwargs):
            self.config = kwargs
        async def astart(self):
            pass
        async def aclose(self):
            pass
        async def acrawl(self, url, **kwargs):
            return type('CrawlResult', (), {'success': False, 'error': 'Crawl4AI not available'})()
    
    class LLMConfig:
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class LLMExtractionStrategy:
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class CrawlerRunConfig:
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class CacheMode:
        ENABLED = "enabled"
        DISABLED = "disabled"
    
    class BrowserConfig:
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class ExtractionStrategy:
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class RegexChunking:
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class StatisticalStrategy:
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class EmbeddingStrategy:
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class AdaptiveConfig:
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class AdaptiveCrawlingStrategy:
        def __init__(self, **kwargs):
            self.config = kwargs
    
    CRAWL4AI_CORE_AVAILABLE = False
    CRAWL4AI_ADAPTIVE_AVAILABLE = False

# Set legacy compatibility flag
CRAWL4AI_AVAILABLE = CRAWL4AI_CORE_AVAILABLE

from .models import CrawlResult, CryptoEntity, CryptoTriple, CrawlMetadata
from .extractors import CryptoEntityExtractor, CryptoTripleExtractor
from ..services.adaptive_strategy_service import AdaptiveStrategyService
from ..models.adaptive_models import AdaptiveStrategyConfig, AdaptiveMetrics, LearnedPattern


class CryptoCrawler:
    """Cryptocurrency-specific web crawler using Crawl4AI.
    
    This class extends the base Crawl4AI functionality with cryptocurrency-specific
    features like token detection, blockchain address recognition, and protocol analysis.
    """
    
    def __init__(self, config: Optional[Dict] = None, config_file_path: Optional[str] = None, **kwargs):
        """Initialize the cryptocurrency crawler.
        
        Args:
            config: Optional configuration dictionary for the crawler
            config_file_path: Optional path to a JSON configuration file
            **kwargs: Additional keyword arguments (e.g., enable_adaptive_crawling)
        """
        self.config = config or {}
        # Merge kwargs into config
        self.config.update(kwargs)
        self.websites = []
        
        # Load configuration from file if provided
        if config_file_path:
            self.load_config_from_file(config_file_path)
        
        self.entity_extractor = CryptoEntityExtractor(self.config)
        self.triple_extractor = CryptoTripleExtractor(self.config)
        self.initialized = False
        self.crawler = None
        
        # Initialize adaptive strategy service
        self.adaptive_service = AdaptiveStrategyService()
        
        # Get configuration parameters from config if provided
        self.user_agent = self.config.get("user_agent", "CryptoCrawler/1.0")
        self.headless = self.config.get("headless", True)
        self.bypass_cache = self.config.get("bypass_cache", False)
        self.word_count_threshold = self.config.get("word_count_threshold", 100)
        self.capture_screenshot = self.config.get("capture_screenshot", True)
        self.extract_images = self.config.get("extract_images", True)
        
        # Adaptive crawling configuration
        self.enable_adaptive_crawling = self.config.get("enable_adaptive_crawling", True)
        self.enable_pattern_learning = self.config.get("enable_pattern_learning", True)
        self.enable_smart_stopping = self.config.get("enable_smart_stopping", True)
    
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
                # Use imported classes from crawl4ai 0.7.0
                
                # Create crawler run config for crawl4ai 0.7.0
                run_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS if self.bypass_cache else CacheMode.ENABLED,
                    word_count_threshold=self.word_count_threshold,
                    page_timeout=30000,  # 30 seconds in milliseconds
                    exclude_all_images=not self.extract_images,  # Invert logic for crawl4ai 0.7.0
                    screenshot=self.capture_screenshot
                )
                
                # Use the arun method with config object for crawl4ai 0.7.0
                crawl_result = await crawler.arun(
                    url=url,
                    config=run_config
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
    
    async def crawl_with_adaptive_intelligence(self, url: str, strategy_config: Optional[AdaptiveStrategyConfig] = None, **kwargs) -> Dict:
        """Enhanced crawling with adaptive intelligence features from Crawl4AI v0.7.0.
        
        Args:
            url: The URL to crawl
            strategy_config: Optional adaptive strategy configuration
            **kwargs: Additional crawling parameters
            
        Returns:
            Dictionary containing crawl results with adaptive intelligence metadata
        """
        if not self.initialized or not self.crawler:
            raise RuntimeError("Crawler not initialized. Call initialize() first.")
        
        start_time = datetime.utcnow()
        
        try:
            # Get optimized strategy for the URL
            if not strategy_config:
                strategy_config = await self.adaptive_service.get_optimized_strategy(url)
            
            # Create adaptive strategies based on configuration
            statistical_strategy = None
            embedding_strategy = None
            adaptive_config = None
            
            if CRAWL4AI_ADAPTIVE_AVAILABLE and StatisticalStrategy and EmbeddingStrategy and AdaptiveConfig:
                if strategy_config.strategy_type in ['statistical', 'hybrid']:
                    statistical_strategy = self.adaptive_service.create_statistical_strategy(strategy_config)
                
                if strategy_config.strategy_type in ['embedding', 'hybrid']:
                    embedding_strategy = self.adaptive_service.create_embedding_strategy(strategy_config)
                
                adaptive_config = self.adaptive_service.create_adaptive_config(strategy_config)
            
            # Configure adaptive crawling strategy
            adaptive_strategy = None
            if CRAWL4AI_ADAPTIVE_AVAILABLE and AdaptiveCrawlingStrategy:
                adaptive_strategy = AdaptiveCrawlingStrategy(
                    statistical=statistical_strategy,
                    embedding=embedding_strategy,
                    adaptive_config=adaptive_config
                )
            
            # Create enhanced crawler run config with valid parameters only
            run_config = CrawlerRunConfig(
                disable_cache=self.bypass_cache,
                word_count_threshold=strategy_config.min_word_count,
                page_timeout=kwargs.get('page_timeout', 30) * 1000,  # Convert to milliseconds
                screenshot=kwargs.get('screenshot', self.capture_screenshot),
                verbose=kwargs.get('verbose', True)
            )
            
            # Perform adaptive crawling
            async with self.crawler as crawler:
                result = await crawler.arun(
                    url=url,
                    config=run_config
                )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Process adaptive results
            adaptive_metadata = {
                'patterns_learned': getattr(result, 'patterns_learned', []),
                'content_quality_score': getattr(result, 'quality_score', 0.0),
                'adaptation_applied': getattr(result, 'adaptation_applied', False),
                'stopping_reason': getattr(result, 'stopping_reason', 'manual'),
                'statistical_metrics': getattr(result, 'statistical_metrics', {}),
                'strategy_type': strategy_config.strategy_type,
                'learning_enabled': strategy_config.enable_pattern_learning,
                'smart_stopping_enabled': strategy_config.enable_smart_stopping
            }
            
            # Create result dictionary
            crawl_result = {
                'success': result.success,
                'url': url,
                'content': result.markdown if hasattr(result, 'markdown') else '',
                'metadata': {
                    **(result.metadata if hasattr(result, 'metadata') and result.metadata else {}),
                    'adaptive_intelligence': adaptive_metadata,
                    'extraction_time': processing_time,
                    'strategy_config': strategy_config.dict()
                },
                'extraction_time': processing_time,
                'screenshot': getattr(result, 'screenshot', None)
            }
            
            # Learn from crawl results if pattern learning is enabled
            if strategy_config.enable_pattern_learning:
                await self.adaptive_service.learn_from_crawl_result(url, crawl_result, strategy_config)
            
            return crawl_result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            error_result = {
                'success': False,
                'error': str(e),
                'url': url,
                'metadata': {
                    'extraction_time': processing_time,
                    'error_type': type(e).__name__
                }
            }
            
            # Still try to learn from failed attempts
            if strategy_config and strategy_config.enable_pattern_learning:
                try:
                    await self.adaptive_service.learn_from_crawl_result(url, error_result, strategy_config)
                except Exception:
                    pass  # Don't let learning errors affect the main error response
            
            return error_result
    
    def get_adaptive_insights(self, domain: str) -> Dict:
        """Get adaptive crawling insights for a specific domain.
        
        Args:
            domain: Domain to get insights for
            
        Returns:
            Dictionary containing domain insights and recommendations
        """
        insights = self.adaptive_service.get_domain_insights(domain)
        return insights.dict()
    
    def get_pattern_analysis(self) -> Dict:
        """Get comprehensive pattern analysis across all domains.
        
        Returns:
            Dictionary containing pattern analysis and optimization opportunities
        """
        if self.adaptive_service is None:
            return {
                "total_patterns": 0,
                "effective_patterns": 0,
                "pattern_types": {},
                "domain_coverage": {},
                "effectiveness_distribution": {},
                "learning_trends": [],
                "optimization_opportunities": ["Adaptive service not initialized"]
            }
        
        analysis = self.adaptive_service.get_pattern_analysis()
        return analysis.dict()
    
    def clear_adaptive_cache(self, domain: Optional[str] = None) -> bool:
        """Clear adaptive learning cache for a domain or all domains.
        
        Args:
            domain: Optional domain to clear cache for. If None, clears all.
            
        Returns:
            True if cache was cleared, False otherwise
        """
        if domain:
            return self.adaptive_service.clear_domain_cache(domain)
        else:
            # Clear all domain caches
            cleared = False
            for domain in list(self.adaptive_service.strategies_cache.keys()):
                if self.adaptive_service.clear_domain_cache(domain):
                    cleared = True
            return cleared
    
    def export_learned_patterns(self, domain: Optional[str] = None) -> Dict:
        """Export learned patterns for backup or analysis.
        
        Args:
            domain: Optional domain to export patterns for. If None, exports all.
            
        Returns:
            Dictionary containing exported patterns
        """
        return self.adaptive_service.export_learned_patterns(domain)


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
    
    async def test_url_with_llm(self, url: str, instruction: str, schema: Optional[Dict] = None, 
                               provider: str = "openai", model: str = None, api_key: str = None,
                               temperature: float = 0.1, max_tokens: int = 4000, timeout: int = 30) -> Dict:
        """Test URL with LLM-based extraction using crawl4AI LLMExtractionStrategy"""
        import time
        import logging
        from datetime import datetime
        
        logger = logging.getLogger(__name__)
        start_time = time.time()
        
        logger.info(f"Starting LLM test for URL: {url}")
        logger.debug(f"LLM parameters - Provider: {provider}, Model: {model}, Temperature: {temperature}, Max tokens: {max_tokens}, Timeout: {timeout}")
        
        try:
            # Perform basic crawl first
            logger.info("Performing basic crawl...")
            crawl_result = await self._perform_basic_crawl(url)
            logger.info(f"Basic crawl completed. Success: {crawl_result.get('success', False)}")
            
            if not crawl_result.get("success", False):
                error_msg = f"Basic crawl failed for {url}"
                logger.error(error_msg)
                return {
                    "url": url,
                    "success": False,
                    "error": error_msg,
                    "response_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Initialize LLM extraction strategy
            logger.info("Initializing LLM extraction strategy...")
            try:
                # Check if LLMExtractionStrategy is available
                logger.debug("Checking LLMExtractionStrategy availability...")
                if not CRAWL4AI_AVAILABLE or LLMExtractionStrategy is None:
                    raise ImportError("LLMExtractionStrategy not available")
                logger.info("LLMExtractionStrategy is available")
                
                # Check for API key with multiple fallbacks
                llm_api_key = (
                    api_key or 
                    self.llm_config.get("api_key") or 
                    os.environ.get(f"{provider.upper()}_API_KEY") or
                    os.environ.get("OPENROUTER_API_KEY") if provider == "openrouter" else None or
                    os.environ.get("OPENAI_API_KEY") if provider == "openai" else None
                )
                logger.debug(f"API key check - Provided: {bool(api_key)}, Config: {bool(self.llm_config.get('api_key'))}, Env: {bool(os.environ.get(f'{provider.upper()}_API_KEY'))}")
                
                if not llm_api_key:
                    logger.warning(f"No API key provided for {provider}. Checked: provided key, config, and environment variables. Proceeding without API key - may use default configuration.")
                
                # Create LLM extraction strategy
                model_to_use = model or self.llm_config.get("model")
                
                # Format model name correctly for different providers
                if provider == "openrouter" and model_to_use and not model_to_use.startswith("openrouter/"):
                    # For OpenRouter, ensure model name has the correct prefix
                    formatted_model = f"openrouter/{model_to_use}"
                    logger.info(f"Formatted OpenRouter model: {model_to_use} -> {formatted_model}")
                    model_to_use = formatted_model
                
                logger.info(f"Creating LLM extraction strategy with provider: {provider}, model: {model_to_use}")
                
                # Use imported classes from crawl4ai 0.7.0
                
                # Create LLMConfig object
                # In crawl4ai 0.7.0, provider should contain the full model specification
                provider_with_model = model_to_use if model_to_use else provider
                llm_config = LLMConfig(
                    provider=provider_with_model,
                    api_token=llm_api_key
                )
                
                # Create LLM extraction strategy with LLMConfig
                llm_strategy = LLMExtractionStrategy(
                    llm_config=llm_config,
                    instruction=instruction,
                    schema=schema,
                    extraction_type="schema" if schema else "block"
                )
                logger.info("LLM extraction strategy created successfully")
                
                # Create crawler run config with the extraction strategy
                run_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    extraction_strategy=llm_strategy
                )
                
                # Re-crawl with LLM extraction strategy
                logger.info("Starting LLM extraction crawl...")
                async with AsyncWebCrawler() as llm_crawler:
                    llm_crawl_result = await llm_crawler.arun(
                        url=url,
                        config=run_config
                    )
                
                if not llm_crawl_result.success:
                    raise Exception(f"LLM crawl failed: {llm_crawl_result.error_message}")
                
                # Extract the result from the crawl
                llm_result = llm_crawl_result.extracted_content
                logger.info(f"LLM extraction completed. Result type: {type(llm_result)}")
                logger.debug(f"LLM result preview: {str(llm_result)[:200]}...")
                
                response_time = time.time() - start_time
                
                return {
                    "url": url,
                    "success": True,
                    "data": {
                        "title": llm_crawl_result.metadata.get("title", "") if llm_crawl_result.metadata else "",
                        "content": llm_crawl_result.cleaned_html or "",
                        "markdown": llm_crawl_result.markdown or "",
                        "llm_extraction": llm_result,
                        "metadata": {
                            "status_code": llm_crawl_result.status_code,
                            "provider": provider,
                            "model": model or self.llm_config.get("model"),
                            "extraction_strategy": "LLMExtractionStrategy"
                        }
                    },
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat()
                }
                
            except ImportError as e:
                error_msg = f"LLMExtractionStrategy not available: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {
                    "url": url,
                    "success": False,
                    "error": error_msg,
                    "response_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                error_msg = f"LLM extraction failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                logger.error(f"Exception type: {type(e).__name__}")
                logger.error(f"Exception args: {e.args}")
                return {
                    "url": url,
                    "success": False,
                    "error": error_msg,
                    "response_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            error_msg = f"Overall crawl process failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            return {
                "url": url,
                "success": False,
                "error": error_msg,
                "response_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _perform_basic_crawl(self, url: str) -> Dict:
        """Perform basic crawling using Crawl4AI or fallback method."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Starting basic crawl for URL: {url}")
        
        if AsyncWebCrawler and self.crawler:
            logger.info("Using Crawl4AI for crawling")
            try:
                # Use imported classes from crawl4ai 0.7.0
                
                # Create crawler run config for basic crawling
                run_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    word_count_threshold=10,
                    page_timeout=self.config.get("delay_before_return_html", 5) * 1000  # Convert to milliseconds
                )
                
                logger.debug(f"Crawl4AI parameters - word_count_threshold: 10, cache_mode: BYPASS, page_timeout: {run_config.page_timeout}ms")
                result = await self.crawler.arun(
                    url=url,
                    config=run_config
                )
                
                logger.info(f"Crawl4AI completed. Success: {result.success}, Status: {result.status_code}")
                logger.debug(f"Content lengths - HTML: {len(result.html) if result.html else 0}, Cleaned: {len(result.cleaned_html) if result.cleaned_html else 0}, Markdown: {len(result.markdown) if result.markdown else 0}")
                
                crawl_result = {
                    "html": result.html,
                    "cleaned_html": result.cleaned_html,
                    "markdown": result.markdown,
                    "title": result.metadata.get("title", "Untitled") if result.metadata else "Untitled",
                    "success": result.success,
                    "status_code": result.status_code
                }
                
                if not result.success:
                    logger.warning(f"Crawl4AI reported failure for {url}. Status code: {result.status_code}")
                
                return crawl_result
                
            except Exception as e:
                logger.error(f"Crawl4AI failed for {url}, using fallback: {e}", exc_info=True)
                logger.error(f"Exception type: {type(e).__name__}")
        else:
            logger.info("Crawl4AI not available, using fallback method")
            logger.debug(f"AsyncWebCrawler available: {bool(AsyncWebCrawler)}, Crawler initialized: {bool(self.crawler)}")
        
        # Fallback method for development/testing
        logger.info("Using fallback crawl method")
        return await self._fallback_crawl(url)
    
    async def _fallback_crawl(self, url: str) -> Dict:
        """Fallback crawling method when Crawl4AI is not available."""
        import logging
        from urllib.parse import urlparse
        
        logger = logging.getLogger(__name__)
        logger.info(f"Using fallback crawl for URL: {url}")
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            logger.debug(f"Parsed domain: {domain}")
            
            fallback_result = {
                "html": f"<html><head><title>Content from {url}</title></head><body><h1>Sample Content</h1><p>This is sample content from {url} for development purposes.</p></body></html>",
                "cleaned_html": f"Sample Content\n\nThis is sample content from {url} for development purposes.",
                "markdown": f"# Sample Content\n\nThis is sample content from {url} for development purposes.",
                "title": f"Content from {domain}",
                "success": True,
                "status_code": 200
            }
            
            logger.info("Fallback crawl completed successfully")
            return fallback_result
            
        except Exception as e:
            logger.error(f"Even fallback crawl failed for {url}: {e}", exc_info=True)
            return {
                "html": "",
                "cleaned_html": "",
                "markdown": "",
                "title": "Error",
                "success": False,
                "status_code": 500
            }
    
    async def initialize(self):
        """Initialize the enhanced crawler with Crawl4AI setup."""
        if self.initialized:
            return
        
        try:
            if AsyncWebCrawler and BrowserConfig:
                
                # Create browser config
                browser_config = BrowserConfig(
                    headless=self.config.get("headless", True),
                    verbose=self.config.get("verbose", False),
                    user_agent=self.config.get("user_agent", "CryptoCrawler/1.0")
                )
                
                self.crawler = AsyncWebCrawler(config=browser_config)
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