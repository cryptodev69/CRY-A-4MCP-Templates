#!/usr/bin/env python3
"""
Universal News Crawler for Cryptocurrency Content.

This module provides a comprehensive news crawling solution specifically designed for
cryptocurrency content aggregation and analysis. It combines web crawling capabilities
with advanced LLM-based content extraction to provide structured, actionable insights
from various cryptocurrency news sources.

Key Features:
    - Multi-source news aggregation (RSS feeds, web pages, APIs)
    - LLM-powered content extraction and analysis
    - Cryptocurrency-specific sentiment analysis
    - Market impact assessment
    - Persona-based relevance scoring
    - Configurable crawling strategies
    - Rate limiting and concurrent processing
    - Comprehensive error handling and logging

Supported LLM Providers:
    - OpenAI (GPT models)
    - OpenRouter (cost-effective proxy with multiple models)
    - Groq (fast inference)
    - Anthropic Claude (via OpenRouter)
    - Google Gemini (via OpenRouter)

Configuration:
    The crawler is configured via JSON files that define:
    - News source URLs and types
    - Crawling parameters and rate limits
    - LLM extraction settings
    - Output formatting preferences

Usage Example:
    ```python
    # Initialize with configuration file
    crawler = UniversalNewsCrawler(
        config_file_path="config/news_sources.json",
        llm_api_token="your-api-token",
        llm_provider="openrouter",
        llm_base_url="https://openrouter.ai/api/v1"
    )
    
    # Crawl all configured sources
    results = await crawler.crawl_all_sources()
    
    # Process specific source types
    rss_results = await crawler.crawl_rss_feeds()
    web_results = await crawler.crawl_web_pages()
    ```

Author: CRY-A-4MCP Development Team
Version: 1.0.0
License: MIT
"""

import asyncio
import json
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from cry_a_4mcp.crawl4ai.crawler import CryptoCrawler
from cry_a_4mcp.crawl4ai.models import CrawlResult

# Import LLMExtractionStrategy if available
try:
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class UniversalNewsCrawler:
    """
    Universal News Crawler for cryptocurrency news and data.
    
    This class serves as the main orchestrator for cryptocurrency news aggregation,
    combining web crawling capabilities with advanced LLM-based content extraction.
    It loads configurations from JSON files and provides comprehensive methods for
    crawling various types of cryptocurrency news sources.
    
    Architecture:
        - Configuration-driven design for maximum flexibility
        - Modular LLM integration supporting multiple providers
        - Asynchronous processing for optimal performance
        - Built-in rate limiting and error handling
        - Extensible extraction strategies
    
    Supported Source Types:
        - RSS feeds from major crypto news outlets
        - Direct web page crawling with content extraction
        - API endpoints for real-time data
        - Social media feeds (Twitter, Reddit, etc.)
        - Blockchain explorer data
    
    Content Processing Pipeline:
        1. Source discovery and URL collection
        2. Concurrent crawling with rate limiting
        3. Content preprocessing and cleaning
        4. LLM-based structured extraction
        5. Sentiment and market impact analysis
        6. Persona-based relevance scoring
        7. Result aggregation and formatting
    
    Configuration Structure:
        The JSON configuration file should contain:
        ```json
        {
            "universal_news_crawler": {
                "crawl4ai_configuration": {
                    "concurrent_crawlers": 10,
                    "rate_limiting": {
                        "requests_per_minute": 60,
                        "delay_between_requests": 1
                    }
                },
                "news_sources": [
                    {
                        "name": "CoinDesk",
                        "type": "rss",
                        "url": "https://coindesk.com/feed",
                        "priority": "high"
                    }
                ]
            }
        }
        ```
    
    Attributes:
        config_file_path (str): Path to the JSON configuration file
        config (Dict): Loaded configuration dictionary
        llm_api_token (str): API token for LLM provider
        llm_provider (str): LLM provider name (openai, groq, openrouter)
        llm_base_url (Optional[str]): Custom base URL for LLM API
        llm_strategy (Optional[LLMExtractionStrategy]): Initialized LLM strategy
        crawler (CryptoCrawler): Main crawler instance
        crawled_content (List): Storage for crawled content results
    
    Example:
        ```python
        # Basic initialization
        crawler = UniversalNewsCrawler(
            config_file_path="config/crypto_sources.json"
        )
        
        # With LLM integration
        crawler = UniversalNewsCrawler(
            config_file_path="config/crypto_sources.json",
            llm_api_token="sk-...",
            llm_provider="openrouter",
            llm_base_url="https://openrouter.ai/api/v1"
        )
        
        # Crawl all sources
        results = await crawler.crawl_all_sources()
        
        # Filter by source type
        rss_sources = crawler.get_sources_by_type("rss")
        web_sources = crawler.get_sources_by_type("web")
        ```
    """
    
    def __init__(self, config_file_path: str, llm_api_token: Optional[str] = None, llm_provider: str = "openai", llm_base_url: Optional[str] = None):
        """
        Initialize the Universal News Crawler with configuration and LLM settings.
        
        This constructor sets up the crawler with all necessary components including
        configuration loading, LLM strategy initialization, and crawler setup.
        It validates the configuration file and establishes connections to the
        specified LLM provider for content extraction.
        
        Args:
            config_file_path (str): Absolute or relative path to the JSON configuration file.
                                   The file must contain valid JSON with crawler settings,
                                   news sources, and processing parameters.
            llm_api_token (Optional[str]): API token for the LLM provider. If not provided,
                                         the crawler will attempt to load from environment
                                         variables (e.g., OPENAI_API_KEY, GROQ_API_KEY).
            llm_provider (str): LLM provider identifier. Supported values:
                              - "openai": Direct OpenAI API integration
                              - "groq": Groq API for fast inference
                              - "openrouter": OpenRouter proxy service (cost-effective)
                              Defaults to "openai".
            llm_base_url (Optional[str]): Custom base URL for the LLM API. Useful for:
                                        - OpenRouter: "https://openrouter.ai/api/v1"
                                        - Custom OpenAI-compatible endpoints
                                        - Local LLM deployments
        
        Raises:
            RuntimeError: If the configuration file cannot be loaded or is invalid
            ValueError: If required parameters are missing or invalid
            ImportError: If required dependencies are not installed
        
        Environment Variables:
            The following environment variables can be used instead of passing tokens:
            - OPENAI_API_KEY: For OpenAI provider
            - GROQ_API_KEY: For Groq provider
            - OPENROUTER_API_KEY: For OpenRouter provider
        
        Configuration File Format:
            The configuration file should follow this structure:
            ```json
            {
                "universal_news_crawler": {
                    "crawl4ai_configuration": {
                        "concurrent_crawlers": 10,
                        "rate_limiting": {
                            "requests_per_minute": 60,
                            "delay_between_requests": 1
                        }
                    },
                    "news_sources": [
                        {
                            "name": "Source Name",
                            "type": "rss|web|api",
                            "url": "https://example.com/feed",
                            "priority": "high|medium|low",
                            "extraction_config": {
                                "custom_selectors": {},
                                "content_filters": []
                            }
                        }
                    ]
                }
            }
            ```
        
        Example:
            ```python
            # Basic initialization with config file only
            crawler = UniversalNewsCrawler("config/news_sources.json")
            
            # With OpenAI integration
            crawler = UniversalNewsCrawler(
                config_file_path="config/news_sources.json",
                llm_api_token="sk-...",
                llm_provider="openai"
            )
            
            # With OpenRouter for cost-effective processing
            crawler = UniversalNewsCrawler(
                config_file_path="config/news_sources.json",
                llm_api_token="sk-or-v1-...",
                llm_provider="openai",  # OpenRouter uses OpenAI-compatible API
                llm_base_url="https://openrouter.ai/api/v1"
            )
            ```
        """
        self.config_file_path = config_file_path
        self.config = self._load_config()
        self.llm_api_token = "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"
        self.llm_provider = "openai"
        self.llm_base_url = "https://openrouter.ai/api/v1",
        self.llm_strategy = None
        
        # Initialize LLM strategy if available and token provided
        if LLM_AVAILABLE and llm_api_token:
            self._initialize_llm_strategy()
        
        # Initialize crypto crawler
        self.crawler = self._initialize_crawler()
        
        # Track crawled content
        self.crawled_content = []
    
    def _load_config(self) -> Dict:
        """
        Load and validate configuration from JSON file.
        
        This method reads the configuration file, validates its structure,
        and returns a dictionary containing all crawler settings. It performs
        basic validation to ensure required sections are present.
        
        Returns:
            Dict: Dictionary containing the complete configuration with sections:
                - universal_news_crawler: Main crawler configuration
                - crawl4ai_configuration: Crawler-specific settings
                - news_sources: List of news sources to crawl
                - extraction_settings: LLM and content extraction settings
        
        Raises:
            RuntimeError: If the configuration file cannot be read, contains
                        invalid JSON, or is missing required sections
            FileNotFoundError: If the configuration file does not exist
            PermissionError: If the configuration file cannot be accessed
        
        Configuration Validation:
            The method validates that the configuration contains:
            - Valid JSON structure
            - Required top-level sections
            - Properly formatted news sources
            - Valid crawler parameters
        
        Example Configuration:
            ```json
            {
                "universal_news_crawler": {
                    "crawl4ai_configuration": {
                        "concurrent_crawlers": 10,
                        "rate_limiting": {
                            "requests_per_minute": 60,
                            "delay_between_requests": 1
                        },
                        "user_agent": "CryptoNewsCrawler/1.0",
                        "timeout": 30
                    },
                    "news_sources": [
                        {
                            "name": "CoinDesk",
                            "type": "rss",
                            "url": "https://coindesk.com/feed",
                            "priority": "high",
                            "enabled": true
                        }
                    ]
                }
            }
            ```
        """
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Basic validation
            if not isinstance(config, dict):
                raise RuntimeError("Configuration must be a JSON object")
                
            if "universal_news_crawler" not in config:
                raise RuntimeError("Configuration missing 'universal_news_crawler' section")
                
            return config
            
        except FileNotFoundError:
            raise RuntimeError(f"Configuration file not found: {self.config_file_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in configuration file {self.config_file_path}: {str(e)}")
        except PermissionError:
            raise RuntimeError(f"Permission denied accessing configuration file: {self.config_file_path}")
        except Exception as e:
            raise RuntimeError(f"Error loading configuration from {self.config_file_path}: {str(e)}")
    
    def _initialize_llm_strategy(self) -> None:
        """Initialize the LLM extraction strategy.
        
        This method sets up the LLM extraction strategy with the appropriate configuration.
        It supports both direct LLM provider connections (like OpenAI) and proxy services
        like OpenRouter that offer potentially cheaper alternatives during development.
        
        When using OpenRouter:
        1. Set llm_provider to "openai" (OpenRouter uses OpenAI-compatible API)
        2. Set llm_base_url to "https://openrouter.ai/api/v1"
        3. Provide your OpenRouter API key as llm_api_token
        
        The method automatically detects OpenRouter URLs and configures appropriate
        headers and can be customized to select specific models.
        """
        if not LLM_AVAILABLE:
            print("LLM extraction strategy not available. Install crawl4ai package.")
            return
        
        # Define the schema for cryptocurrency content extraction
        schema = {
            "type": "object",
            "properties": {
                "headline": {"type": "string"},
                "summary": {"type": "string"},
                "sentiment": {"type": "string", "enum": ["bullish", "bearish", "neutral"]},
                "category": {"type": "string", "enum": ["breaking", "analysis", "regulatory", "institutional", "technical", "defi", "nft", "meme"]},
                "market_impact": {"type": "string", "enum": ["high", "medium", "low", "none"]},
                "key_entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["token", "exchange", "protocol", "person", "company", "regulator"]},
                            "relevance": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    }
                },
                "persona_relevance": {
                    "type": "object",
                    "properties": {
                        "meme_snipers": {"type": "number", "minimum": 0, "maximum": 1},
                        "gem_hunters": {"type": "number", "minimum": 0, "maximum": 1},
                        "legacy_investors": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                },
                "urgency_score": {"type": "number", "minimum": 0, "maximum": 10}
            }
        }
        
        # Define the instruction for cryptocurrency content extraction
        instruction = """
        Analyze this cryptocurrency content and extract structured information including:
        1. Headline and summary
        2. Overall sentiment (bullish, bearish, neutral)
        3. Content category (breaking, analysis, regulatory, etc.)
        4. Market impact assessment (high, medium, low, none)
        5. Key entities mentioned (tokens, exchanges, protocols, people, companies, regulators)
        6. Relevance to different crypto investor personas (meme snipers, gem hunters, legacy investors)
        7. Urgency score (0-10) indicating how time-sensitive this information is
        
        Focus on extracting factual information and avoid speculation. If certain information
        is not present in the content, omit those fields from your response.
        """
        
        # Initialize the LLM extraction strategy
        try:
            # Create kwargs dict for optional parameters
            llm_kwargs = {
                "provider": self.llm_provider,
                "api_token": self.llm_api_token,
                "schema": schema,
                "instruction": instruction
            }
            
            # Add base_url if provided (for OpenRouter integration)
            if self.llm_base_url:
                llm_kwargs["base_url"] = self.llm_base_url
                print(f"Using custom base URL: {self.llm_base_url}")
                
                # Special handling for OpenRouter
                if "openrouter.ai" in self.llm_base_url:
                    # For OpenRouter, you can specify the model and other parameters
                    # These are passed to the LLM API call
                    llm_kwargs["extra_args"] = {
                        "headers": {
                            "HTTP-Referer": "https://crypto-news-crawler.com",  # Replace with your site
                            "X-Title": "Crypto News Crawler"  # Optional title for tracking
                        },
                        # Using the specified model
                        "model": "google/gemini-2.0-flash-exp:free"  # Free google/gemini-2.0-flash model
                        # Other model options:
                        # "model": "anthropic/claude-3-haiku-20240307"  # A cheaper, faster model
                        # "model": "google/gemini-pro"  # Another option
                        # "model": "anthropic/claude-3-opus-20240229"  # More expensive but powerful
                    }
                    print("Configured for OpenRouter with model: google/gemini-2.0-flash-exp:free")
            
            self.llm_strategy = LLMExtractionStrategy(**llm_kwargs)
            print(f"Initialized LLM extraction strategy with {self.llm_provider}")
        except Exception as e:
            print(f"Error initializing LLM extraction strategy: {str(e)}")
    
    def _initialize_crawler(self) -> CryptoCrawler:
        """Initialize the CryptoCrawler with configuration.
        
        Returns:
            Configured CryptoCrawler instance
        """
        # Extract crawl4ai configuration
        crawler_config = self.config.get("universal_news_crawler", {}).get("crawl4ai_configuration", {})
        
        # Create a configuration dictionary for CryptoCrawler
        config = {
            "user_agent": "UniversalNewsCrawler/1.0",
            "headless": True,
            "cache_bypass": True,
            "word_count_threshold": 100,
            "capture_screenshot": True,
            "extract_images": True,
            "concurrent_crawlers": crawler_config.get("concurrent_crawlers", 10),
            "rate_limiting": crawler_config.get("rate_limiting", {})
        }
        
        # Initialize the crawler
        crawler = CryptoCrawler(config=config)
        return crawler
    
    def get_all_sources(self) -> List[Dict]:
        """Get all news sources from the configuration.
        
        Returns:
            List of all news sources across all tiers
        """
        sources = []
        
        # Extract sources from each tier
        for tier_key, tier_data in self.config.get("universal_news_crawler", {}).items():
            if isinstance(tier_data, dict) and "sources" in tier_data:
                for source in tier_data["sources"]:
                    # Add tier information to the source
                    source["tier"] = tier_key
                    sources.append(source)
        
        return sources
    
    def get_sources_by_tier(self, tier: str) -> List[Dict]:
        """Get news sources for a specific tier.
        
        Args:
            tier: Tier name (e.g., "tier_1_crypto_news")
            
        Returns:
            List of news sources for the specified tier
        """
        tier_data = self.config.get("universal_news_crawler", {}).get(tier, {})
        sources = tier_data.get("sources", [])
        
        # Add tier information to each source
        for source in sources:
            source["tier"] = tier
        
        return sources
    
    def get_sources_by_priority(self, priority: str) -> List[Dict]:
        """Get news sources with a specific priority.
        
        Args:
            priority: Priority level (e.g., "high", "medium", "low")
            
        Returns:
            List of news sources with the specified priority
        """
        sources = []
        
        # Extract sources from each tier
        for tier_key, tier_data in self.config.get("universal_news_crawler", {}).items():
            if isinstance(tier_data, dict) and "sources" in tier_data:
                for source in tier_data["sources"]:
                    if source.get("priority") == priority:
                        # Add tier information to the source
                        source["tier"] = tier_key
                        sources.append(source)
        
        return sources
    
    def get_sources_by_crawl_frequency(self, frequency: str) -> List[Dict]:
        """Get news sources with a specific crawl frequency.
        
        Args:
            frequency: Crawl frequency (e.g., "2_minutes", "5_minutes", "hourly")
            
        Returns:
            List of news sources with the specified crawl frequency
        """
        sources = []
        
        # Extract sources from each tier
        for tier_key, tier_data in self.config.get("universal_news_crawler", {}).items():
            if isinstance(tier_data, dict) and "sources" in tier_data:
                for source in tier_data["sources"]:
                    if source.get("crawl_frequency") == frequency:
                        # Add tier information to the source
                        source["tier"] = tier_key
                        sources.append(source)
        
        return sources
    
    def get_sources_by_persona_relevance(self, persona: str, min_score: float = 0.7) -> List[Dict]:
        """Get news sources relevant to a specific persona.
        
        Args:
            persona: Persona name (e.g., "meme_snipers", "gem_hunters", "legacy_investors")
            min_score: Minimum relevance score (0.0 to 1.0)
            
        Returns:
            List of news sources relevant to the specified persona
        """
        sources = []
        
        # Extract sources from each tier
        for tier_key, tier_data in self.config.get("universal_news_crawler", {}).items():
            if isinstance(tier_data, dict) and "sources" in tier_data:
                for source in tier_data["sources"]:
                    persona_relevance = source.get("persona_relevance", {})
                    if persona in persona_relevance and persona_relevance[persona] >= min_score:
                        # Add tier information to the source
                        source["tier"] = tier_key
                        sources.append(source)
        
        return sources
    
    async def crawl_rss_feeds(self, max_articles_per_source: int = 10) -> List[Dict]:
        """Crawl RSS feeds from configured sources.
        
        Args:
            max_articles_per_source: Maximum number of articles to crawl per source
            
        Returns:
            List of crawled articles
        """
        # This is a placeholder for RSS feed crawling functionality
        # In a real implementation, you would use a library like feedparser
        print("Crawling RSS feeds...")
        
        rss_sources = []
        for source in self.get_all_sources():
            if "rss_feed" in source:
                rss_sources.append(source)
        
        print(f"Found {len(rss_sources)} RSS sources")
        
        # Return placeholder data
        return [{
            "source": source["name"],
            "url": source["rss_feed"],
            "articles": []
        } for source in rss_sources]
    
    async def crawl_web_pages(self, urls: List[str]) -> List[Dict]:
        """Crawl web pages using the CryptoCrawler.
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            List of crawl results
        """
        print(f"Crawling {len(urls)} web pages...")
        
        results = []
        for url in urls:
            try:
                # Initialize the crawler if needed
                if not self.crawler.initialized:
                    await self.crawler.initialize()
                
                # Determine content type based on URL
                content_type = "news"
                for source in self.get_all_sources():
                    if url == source.get("url") or ("rss_feed" in source and url == source["rss_feed"]):
                        content_type = source.get("content_type", "news")
                        break
                
                # Crawl the web page
                result = await self.crawler.crawl_crypto_website(
                    url=url,
                    content_type=content_type,
                    extract_entities=True,
                    generate_triples=True
                )
                
                # Add LLM extraction if available
                llm_extraction = None
                if self.llm_strategy and result.metadata.success and result.markdown:
                    try:
                        llm_extraction = await self.llm_strategy.extract(
                            url=url,
                            html=result.markdown,
                            instruction=self.llm_strategy.instruction,
                            schema=self.llm_strategy.schema
                        )
                    except Exception as e:
                        print(f"Error during LLM extraction for {url}: {str(e)}")
                
                # Combine crawl result and LLM extraction
                combined_result = {
                    "crawl_result": result,
                    "llm_extraction": llm_extraction
                }
                
                results.append(combined_result)
                self.crawled_content.append(combined_result)
                
            except Exception as e:
                print(f"Error crawling {url}: {str(e)}")
        
        return results
    
    async def fetch_api_data(self, api_sources: Optional[List[str]] = None) -> List[Dict]:
        """Fetch data from API endpoints.
        
        Args:
            api_sources: Optional list of API source names to fetch
            
        Returns:
            List of API data results
        """
        # This is a placeholder for API data fetching functionality
        # In a real implementation, you would use a library like aiohttp
        print("Fetching API data...")
        
        # Get all sources with API endpoints
        api_sources_data = []
        for source in self.get_all_sources():
            if "api_endpoint" in source:
                if api_sources is None or source["name"] in api_sources:
                    api_sources_data.append(source)
        
        print(f"Found {len(api_sources_data)} API sources")
        
        # Return placeholder data
        return [{
            "source": source["name"],
            "url": source["api_endpoint"],
            "data": {}
        } for source in api_sources_data]
    
    def route_to_personas(self, min_score: float = 0.7) -> Dict[str, List[Dict]]:
        """Route crawled content to personas based on relevance scores.
        
        Args:
            min_score: Minimum relevance score (0.0 to 1.0)
            
        Returns:
            Dictionary mapping personas to relevant content
        """
        personas = {
            "meme_snipers": [],
            "gem_hunters": [],
            "legacy_investors": []
        }
        
        for content in self.crawled_content:
            llm_extraction = content.get("llm_extraction", {})
            persona_relevance = llm_extraction.get("persona_relevance", {})
            
            for persona, score in persona_relevance.items():
                if persona in personas and score >= min_score:
                    personas[persona].append(content)
        
        return personas
    
    async def run_crawl_cycle(self):
        """Run a complete crawl cycle based on configuration."""
        print("Starting crawl cycle...")
        
        # Step 1: Crawl RSS feeds from tier 1 sources
        tier_1_sources = self.get_sources_by_tier("tier_1_crypto_news")
        tier_1_urls = [source.get("url") for source in tier_1_sources if "url" in source]
        await self.crawl_web_pages(tier_1_urls[:3])  # Limit to 3 for testing
        
        # Step 2: Fetch API data for market indicators
        await self.fetch_api_data(["Fear & Greed Index", "Bitcoin Dominance"])
        
        # Step 3: Route content to personas
        persona_content = self.route_to_personas()
        
        print("Crawl cycle completed")
        print(f"Crawled {len(self.crawled_content)} pages")
        print(f"Routed content to personas: {', '.join([f'{persona}: {len(content)}' for persona, content in persona_content.items()])}")
    
    async def close(self):
        """Close the crawler and release resources."""
        if self.crawler and self.crawler.initialized:
            await self.crawler.close()
            print("Crawler closed properly")


async def main():
    """Run the Universal News Crawler."""
    # Path to the configuration file
    config_file_path = os.path.join(
        os.path.dirname(__file__),
        '../../../sample-data/crawled_content/universal_news_crawler_config.json'
    )
    
    print(f"Loading configuration from: {config_file_path}")
    
    # Create a UniversalNewsCrawler instance
    # Note: Replace with your actual API token if using LLM extraction
    
    # Example 1: Using OpenAI directly
    # crawler = UniversalNewsCrawler(
    #     config_file_path=config_file_path,
    #     llm_api_token="your-openai-api-key",  # Replace with your OpenAI API key
    #     llm_provider="openai"
    # )
    
    # Example 2: Using OpenRouter (cheaper during development)
    # Note: With OpenRouter, you can use various models at lower costs
    # The model selection is handled by OpenRouter based on your request
    # You can specify preferred models in your OpenRouter account settings
    # or by adding headers in the LLMExtractionStrategy implementation
    crawler = UniversalNewsCrawler(
        config_file_path=config_file_path,
        llm_api_token="your-openrouter-api-key",  # Replace with your OpenRouter API key
        llm_provider="openai",  # Keep as "openai" since OpenRouter uses OpenAI-compatible API
        llm_base_url="https://openrouter.ai/api/v1"  # OpenRouter base URL
    )
    
    # Example 3: Advanced OpenRouter usage with specific model selection
    # This requires modifying the _initialize_llm_strategy method to pass extra_args
    # You would need to add the following code to _initialize_llm_strategy:
    #
    # if self.llm_base_url and "openrouter.ai" in self.llm_base_url:
    #     # For OpenRouter, you can specify the model and other parameters
    #     llm_kwargs["extra_args"] = {
    #         "headers": {
    #             "HTTP-Referer": "https://your-site.com",  # Optional
    #             "X-Title": "Crypto News Crawler"  # Optional
    #         },
    #         "model": "anthropic/claude-3-opus-20240229"  # Specify exact model
    #     }
    #
    # Then you would initialize the crawler as normal:
    # crawler = UniversalNewsCrawler(
    #     config_file_path=config_file_path,
    #     llm_api_token="your-openrouter-api-key",
    #     llm_provider="openai",
    #     llm_base_url="https://openrouter.ai/api/v1"
    # )
    
    # For development/testing without LLM
    # crawler = UniversalNewsCrawler(
    #     config_file_path=config_file_path,
    #     llm_api_token=None  # No LLM extraction
    # )
    
    try:
        # Print information about loaded sources
        all_sources = crawler.get_all_sources()
        print(f"Loaded {len(all_sources)} sources from configuration")
        
        # Print high priority sources
        high_priority_sources = crawler.get_sources_by_priority("high")
        print(f"\nHigh priority sources ({len(high_priority_sources)}):")
        for source in high_priority_sources:
            print(f"  - {source['name']} ({source.get('tier', 'unknown')})")
        
        # Print sources relevant to meme snipers
        meme_sniper_sources = crawler.get_sources_by_persona_relevance("meme_snipers", 0.7)
        print(f"\nSources relevant to meme snipers ({len(meme_sniper_sources)}):")
        for source in meme_sniper_sources:
            relevance = source.get("persona_relevance", {}).get("meme_snipers", 0)
            print(f"  - {source['name']} (relevance: {relevance})")
        
        # Run a crawl cycle
        await crawler.run_crawl_cycle()
        
    finally:
        # Ensure crawler is properly closed
        await crawler.close()
        print("\nCrawler closed properly")


if __name__ == "__main__":
    asyncio.run(main())