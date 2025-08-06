#!/usr/bin/env python3
"""
Generic async crawler implementation for the cry_a_4mcp.crawl4ai package.
Extends existing functionality with production-ready Crawl4AI integration.
"""

import asyncio
import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import LLMExtractionStrategy as Crawl4AILLMStrategy, JsonCssExtractionStrategy
    from crawl4ai.chunking_strategy import RegexChunking
    from crawl4ai.async_crawler_strategy import AsyncCrawlerStrategy
    from crawl4ai.models import CrawlResult as Crawl4AICrawlResult
except ImportError:
    # Fallback for development/testing
    AsyncWebCrawler = None
    Crawl4AILLMStrategy = None
    JsonCssExtractionStrategy = None
    RegexChunking = None
    AsyncCrawlerStrategy = None
    Crawl4AICrawlResult = None

from .extraction_strategies.custom_strategies.url_mapping import URLMappingManager, extract_from_url
from .extraction_strategies.base import LLMExtractionStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CrawlMetadata:
    """Metadata for crawl results with enhanced tracking."""
    success: bool = True
    source: str = "generic_crawler"
    crawl_time: str = ""
    content_type: str = "unknown"
    model_used: str = ""
    extraction_time: float = 0.0
    url_domain: str = ""
    extractors_used: List[str] = None
    error_message: str = ""
    llm_config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.crawl_time:
            self.crawl_time = datetime.utcnow().isoformat() + "Z"
        if self.extractors_used is None:
            self.extractors_used = []

@dataclass
class CrawlResult:
    """Enhanced crawl result with comprehensive data structure."""
    url: str
    title: str
    content: str
    markdown: str
    metadata: CrawlMetadata
    html: str = ""
    extracted_data: Dict[str, Any] = None
    extraction_results: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.extracted_data is None:
            self.extracted_data = {}
        if self.extraction_results is None:
            self.extraction_results = []

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
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the generic async crawler with enhanced configuration.
        
        Args:
            config: Optional configuration dictionary with crawler settings
        """
        self.config = self._setup_default_config(config or {})
        self.crawler = None
        self.url_mapping_manager = URLMappingManager()
        self.initialized = False
        self.llm_config = self.config.get("llm_config", {})
        self._session_stats = {
            "total_crawls": 0,
            "successful_crawls": 0,
            "failed_crawls": 0,
            "total_extraction_time": 0.0
        }
        
        # Load URL mappings if config file exists
        mapping_file = self.config.get("url_mapping_file", "url_mappings.json")
        if os.path.exists(mapping_file):
            try:
                self.url_mapping_manager.load_from_file(mapping_file)
                logger.info(f"Loaded URL mappings from {mapping_file}")
            except Exception as e:
                logger.warning(f"Failed to load URL mappings: {e}")
    
    def _setup_default_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
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
            "url_mapping_file": "url_mappings.json",
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
    
    def _create_llm_extraction_strategy(self, instruction: str, schema: Optional[Dict] = None) -> Optional[Any]:
        """Create LLM extraction strategy based on configuration"""
        if not Crawl4AILLMStrategy or not self.llm_config.get("api_key"):
            logger.warning("LLM extraction not available - missing strategy or API key")
            return None
        
        try:
            strategy_config = {
                "provider": self.llm_config.get("provider", "openai"),
                "api_key": self.llm_config.get("api_key"),
                "model": self.llm_config.get("model", "gpt-4"),
                "temperature": self.llm_config.get("temperature", 0.1),
                "max_tokens": self.llm_config.get("max_tokens", 4000)
            }
            
            if schema:
                return Crawl4AILLMStrategy(
                    provider=strategy_config["provider"],
                    api_key=strategy_config["api_key"],
                    model=strategy_config["model"],
                    instruction=instruction,
                    schema=schema,
                    temperature=strategy_config["temperature"],
                    max_tokens=strategy_config["max_tokens"]
                )
            else:
                return Crawl4AILLMStrategy(
                    provider=strategy_config["provider"],
                    api_key=strategy_config["api_key"],
                    model=strategy_config["model"],
                    instruction=instruction,
                    temperature=strategy_config["temperature"],
                    max_tokens=strategy_config["max_tokens"]
                )
        except Exception as e:
            logger.error(f"Failed to create LLM extraction strategy: {e}")
            return None
    
    async def test_url_with_llm(self, url: str, instruction: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Test URL with LLM-based extraction"""
        start_time = time.time()
        
        try:
            # Create LLM extraction strategy
            extraction_strategy = self._create_llm_extraction_strategy(instruction, schema)
            
            if not extraction_strategy:
                return {
                    "url": url,
                    "success": False,
                    "error": "LLM extraction strategy not available",
                    "response_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Perform crawl with LLM extraction
            result = await self._perform_basic_crawl(url, extraction_strategy)
            
            response_time = time.time() - start_time
            
            if result.get("success", False):
                return {
                    "url": url,
                    "success": True,
                    "data": {
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "markdown": result.get("markdown", ""),
                        "llm_extraction": result.get("extracted_content", {}),
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
            logger.error(f"LLM URL test failed for {url}: {e}")
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
        
    async def crawl_web_pages(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Crawl a list of web pages with enhanced extraction and mapping support.
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            List of enhanced crawl results with extraction data
        """
        if not self.initialized:
            await self.initialize()
        
        results = []
        semaphore = asyncio.Semaphore(self.config["concurrent_limit"])
        
        async def crawl_single_url(url: str) -> Dict[str, Any]:
            async with semaphore:
                return await self._crawl_url_with_extraction(url)
        
        # Process URLs concurrently with rate limiting
        tasks = [crawl_single_url(url) for url in urls]
        crawl_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(crawl_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to crawl {urls[i]}: {result}")
                self._session_stats["failed_crawls"] += 1
                # Create error result
                error_result = {
                    "url": urls[i],
                    "title": "Crawl Failed",
                    "content": "",
                    "metadata": asdict(CrawlMetadata(
                        success=False,
                        url_domain=urlparse(urls[i]).netloc,
                        error_message=str(result)
                    )),
                    "llm_extraction": {},
                    "extraction_results": []
                }
                results.append(error_result)
            else:
                results.append(result)
                self._session_stats["successful_crawls"] += 1
            
            self._session_stats["total_crawls"] += 1
        
        # Log session statistics
        if self.config["enable_performance_monitoring"]:
            self._log_session_stats()
        
        return results
    
    async def _crawl_url_with_extraction(self, url: str) -> Dict[str, Any]:
        """
        Crawl a single URL with intelligent extraction based on URL mappings.
        
        Args:
            url: URL to crawl
            
        Returns:
            Enhanced crawl result with extraction data
        """
        start_time = time.time()
        
        try:
            # Get URL mappings for this URL
            mappings = self.url_mapping_manager.get_mappings_for_url(url)
            
            # Perform basic crawl
            crawl_result = await self._perform_basic_crawl(url)
            
            # Apply extractors based on mappings
            extraction_results = []
            extractors_used = []
            
            if mappings:
                for mapping in mappings:
                    for extractor_config in mapping.extractors:
                        try:
                            extraction_result = await self._apply_extractor(
                                crawl_result, extractor_config, url
                            )
                            extraction_results.append(extraction_result)
                            extractors_used.append(extractor_config.extractor_id)
                        except Exception as e:
                            logger.warning(f"Extractor {extractor_config.extractor_id} failed for {url}: {e}")
            
            # Create comprehensive result
            extraction_time = time.time() - start_time
            self._session_stats["total_extraction_time"] += extraction_time
            
            metadata = CrawlMetadata(
                success=True,
                url_domain=urlparse(url).netloc,
                extraction_time=extraction_time,
                extractors_used=extractors_used,
                llm_config=self.llm_config
            )
            
            # Format result for backward compatibility
            result = {
                "url": url,
                "title": crawl_result.get("title", "Untitled"),
                "content": crawl_result.get("cleaned_html", ""),
                "metadata": asdict(metadata),
                "llm_extraction": self._merge_extraction_results(extraction_results),
                "extraction_results": extraction_results,
                "html": crawl_result.get("html", ""),
                "markdown": crawl_result.get("markdown", "")
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to crawl {url}: {e}")
            extraction_time = time.time() - start_time
            
            metadata = CrawlMetadata(
                success=False,
                url_domain=urlparse(url).netloc,
                extraction_time=extraction_time,
                error_message=str(e)
            )
            
            return {
                "url": url,
                "title": "Crawl Failed",
                "content": "",
                "metadata": asdict(metadata),
                "llm_extraction": {},
                "extraction_results": [],
                "html": "",
                "markdown": ""
            }
        
    async def _perform_basic_crawl(self, url: str, extraction_strategy=None) -> Dict[str, Any]:
        """
        Perform basic crawling using Crawl4AI or fallback method with optional LLM extraction.
        
        Args:
            url: URL to crawl
            extraction_strategy: Optional extraction strategy for LLM-based extraction
            
        Returns:
            Basic crawl result with HTML, text, and metadata
        """
        if AsyncWebCrawler and self.crawler:
            try:
                # Prepare crawl parameters
                crawl_params = {
                    "url": url,
                    "word_count_threshold": 10,
                    "bypass_cache": False,
                    "delay_before_return_html": self.config["delay_before_return_html"]
                }
                
                # Add extraction strategy if provided
                if extraction_strategy:
                    crawl_params["extraction_strategy"] = extraction_strategy
                
                result = await self.crawler.arun(**crawl_params)
                
                return {
                    "html": result.html,
                    "cleaned_html": result.cleaned_html,
                    "markdown": result.markdown,
                    "title": result.metadata.get("title", "Untitled"),
                    "success": result.success,
                    "status_code": result.status_code,
                    "extracted_content": getattr(result, 'extracted_content', None)
                }
            except Exception as e:
                logger.warning(f"Crawl4AI failed for {url}, using fallback: {e}")
        
        # Fallback method for development/testing
        return await self._fallback_crawl(url)
    
    async def _fallback_crawl(self, url: str) -> Dict[str, Any]:
        """
        Fallback crawling method when Crawl4AI is not available.
        
        Args:
            url: URL to crawl
            
        Returns:
            Mock crawl result for development
        """
        logger.info(f"Using fallback crawler for {url}")
        
        # Simple mock data for development
        return {
            "html": f"<html><head><title>Content from {url}</title></head><body><h1>Sample Content</h1><p>This is sample content from {url} for development purposes.</p></body></html>",
            "cleaned_html": f"Sample Content\n\nThis is sample content from {url} for development purposes.",
            "markdown": f"# Sample Content\n\nThis is sample content from {url} for development purposes.",
            "title": f"Content from {urlparse(url).netloc}",
            "success": True,
            "status_code": 200
        }
    
    async def _apply_extractor(self, crawl_result: Dict[str, Any], extractor_config, url: str) -> Dict[str, Any]:
        """
        Apply a specific extractor to crawled content.
        
        Args:
            crawl_result: Basic crawl result
            extractor_config: Extractor configuration
            url: Original URL
            
        Returns:
            Extraction result
        """
        try:
            # Use the existing extraction strategy framework
            extraction_result = await extract_from_url(
                url, 
                crawl_result["cleaned_html"], 
                self.url_mapping_manager
            )
            
            return {
                "extractor_id": extractor_config.extractor_id,
                "target_group": extractor_config.target_group,
                "extraction_data": extraction_result,
                "success": True,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as e:
            logger.error(f"Extraction failed for {extractor_config.extractor_id}: {e}")
            return {
                "extractor_id": extractor_config.extractor_id,
                "target_group": extractor_config.target_group,
                "extraction_data": {},
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    def _merge_extraction_results(self, extraction_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple extraction results into a single LLM extraction format.
        
        Args:
            extraction_results: List of extraction results
            
        Returns:
            Merged extraction data for backward compatibility
        """
        if not extraction_results:
            return {
                "_model_info": {
                    "name": "generic-extractor",
                    "provider": "generic_crawler"
                }
            }
        
        merged = {}
        model_info = {
            "name": "generic-extractor",
            "provider": "generic_crawler",
            "extractors_used": []
        }
        
        for result in extraction_results:
            if result["success"]:
                # Merge extraction data
                extraction_data = result.get("extraction_data", {})
                for key, value in extraction_data.items():
                    if key not in merged:
                        merged[key] = value
                    elif isinstance(merged[key], list) and isinstance(value, list):
                        merged[key].extend(value)
                
                model_info["extractors_used"].append(result["extractor_id"])
        
        merged["_model_info"] = model_info
        return merged
    
    def _log_session_stats(self):
        """
        Log beautiful session statistics for monitoring.
        """
        stats = self._session_stats
        success_rate = (stats["successful_crawls"] / max(stats["total_crawls"], 1)) * 100
        avg_extraction_time = stats["total_extraction_time"] / max(stats["successful_crawls"], 1)
        
        logger.info(
            f"📊 Session Stats: {stats['total_crawls']} total, "
            f"{stats['successful_crawls']} successful ({success_rate:.1f}%), "
            f"avg extraction time: {avg_extraction_time:.2f}s"
        )
    
    async def crawl_crypto_website(self, url: str, content_type: str, extract_entities: bool = True, generate_triples: bool = True) -> CrawlResult:
        """
        Enhanced cryptocurrency website crawling with intelligent extraction.
        
        Args:
            url: URL to crawl
            content_type: Type of content (news, forum, etc.)
            extract_entities: Whether to extract entities
            generate_triples: Whether to generate knowledge graph triples
            
        Returns:
            Enhanced CrawlResult object with comprehensive data
        """
        logger.info(f"🚀 Crawling crypto website: {url} (content type: {content_type})")
        
        try:
            # Use the enhanced crawling method
            crawl_data = await self._crawl_url_with_extraction(url)
            
            # Create enhanced metadata
            metadata = CrawlMetadata(
                success=crawl_data["metadata"]["success"],
                content_type=content_type,
                url_domain=urlparse(url).netloc,
                extractors_used=crawl_data["metadata"].get("extractors_used", []),
                extraction_time=crawl_data["metadata"].get("extraction_time", 0.0)
            )
            
            # Create comprehensive result
            result = CrawlResult(
                url=url,
                title=crawl_data["title"],
                content=crawl_data["content"],
                markdown=crawl_data["markdown"],
                html=crawl_data["html"],
                metadata=metadata,
                extracted_data=crawl_data["llm_extraction"],
                extraction_results=crawl_data["extraction_results"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to crawl crypto website {url}: {e}")
            
            # Return error result
            error_metadata = CrawlMetadata(
                success=False,
                content_type=content_type,
                url_domain=urlparse(url).netloc,
                error_message=str(e)
            )
            
            return CrawlResult(
                url=url,
                title="Crawl Failed",
                content="",
                markdown="",
                html="",
                metadata=error_metadata
            )
        
    async def initialize(self):
        """
        Initialize the enhanced crawler with Crawl4AI setup.
        """
        if self.initialized:
            return
        
        logger.info("🚀 Initializing GenericAsyncCrawler...")
        
        try:
            if AsyncWebCrawler:
                # Initialize Crawl4AI with enhanced configuration
                self.crawler = AsyncWebCrawler(
                    headless=self.config["headless"],
                    verbose=self.config["verbose"],
                    user_agent=self.config["user_agent"],
                    viewport_width=self.config["viewport_width"],
                    viewport_height=self.config["viewport_height"]
                )
                await self.crawler.start()
                logger.info("✅ Crawl4AI initialized successfully")
            else:
                logger.warning("⚠️ Crawl4AI not available, using fallback mode")
            
            self.initialized = True
            logger.info("🎉 GenericAsyncCrawler ready for action!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize crawler: {e}")
            logger.info("🔄 Falling back to development mode")
            self.initialized = True  # Allow fallback mode
    
    async def close(self):
        """
        Gracefully close crawler resources with beautiful cleanup.
        """
        if not self.initialized:
            return
        
        logger.info("🛑 Shutting down GenericAsyncCrawler...")
        
        try:
            if self.crawler:
                await self.crawler.close()
                logger.info("✅ Crawl4AI closed successfully")
            
            # Save URL mappings if modified
            mapping_file = self.config.get("url_mapping_file", "url_mappings.json")
            try:
                self.url_mapping_manager.save_to_file(mapping_file)
                logger.info(f"💾 URL mappings saved to {mapping_file}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save URL mappings: {e}")
            
            # Log final session statistics
            if self.config["enable_performance_monitoring"]:
                self._log_session_stats()
                logger.info("📊 Final session statistics logged")
            
            self.initialized = False
            logger.info("👋 GenericAsyncCrawler shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during crawler shutdown: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get current session statistics.
        
        Returns:
            Dictionary with session statistics
        """
        stats = self._session_stats.copy()
        if stats["total_crawls"] > 0:
            stats["success_rate"] = (stats["successful_crawls"] / stats["total_crawls"]) * 100
        else:
            stats["success_rate"] = 0.0
        
        if stats["successful_crawls"] > 0:
            stats["avg_extraction_time"] = stats["total_extraction_time"] / stats["successful_crawls"]
        else:
            stats["avg_extraction_time"] = 0.0
        
        return stats
    
    def add_url_mapping(self, pattern: str, pattern_type: str, extractors: List[Dict[str, Any]], priority: int = 1):
        """
        Add a new URL mapping for extractor association.
        
        Args:
            pattern: URL pattern to match
            pattern_type: Type of pattern (domain, path, exact)
            extractors: List of extractor configurations
            priority: Mapping priority (higher = more important)
        """
        from .extraction_strategies.custom_strategies.url_mapping import URLExtractorMapping, ExtractorConfig
        
        extractor_configs = []
        for ext in extractors:
            config = ExtractorConfig(
                extractor_id=ext["extractor_id"],
                target_group=ext.get("target_group", "default"),
                parameters=ext.get("parameters", {})
            )
            extractor_configs.append(config)
        
        mapping = URLExtractorMapping(
            pattern=pattern,
            pattern_type=pattern_type,
            extractors=extractor_configs,
            priority=priority
        )
        
        self.url_mapping_manager.add_mapping(mapping)
        logger.info(f"✅ Added URL mapping: {pattern} -> {len(extractors)} extractors")


# Backward compatibility alias
CryptoCrawler = GenericAsyncCrawler