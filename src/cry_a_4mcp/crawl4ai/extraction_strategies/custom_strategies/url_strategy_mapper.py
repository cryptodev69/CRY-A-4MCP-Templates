#!/usr/bin/env python3
"""
URL-to-Strategy Mapper for extraction strategies.

This module provides a mechanism to map URLs to specific extraction strategies
based on domain patterns, URL patterns, or other criteria.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Union, Pattern, Callable, Tuple
from urllib.parse import urlparse

from ..base import ExtractionStrategy
from ..registry import register_strategy, StrategyRegistry
from ..factory import StrategyFactory, CompositeExtractionStrategy

# Configure logging
logger = logging.getLogger('url_strategy_mapper')


class StrategyMatcher:
    """Base class for strategy matchers.
    
    A strategy matcher determines whether a URL should be processed by a specific strategy.
    """
    
    def matches(self, url: str) -> bool:
        """Check if the URL matches this matcher's criteria.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL matches, False otherwise
        """
        raise NotImplementedError("Subclasses must implement matches()")


class DomainMatcher(StrategyMatcher):
    """Match URLs based on their domain.
    
    This matcher checks if a URL's domain matches a specific domain or is a subdomain of it.
    """
    
    def __init__(self, domain: str, include_subdomains: bool = True):
        """Initialize the domain matcher.
        
        Args:
            domain: The domain to match (e.g., "example.com")
            include_subdomains: Whether to match subdomains as well
        """
        self.domain = domain.lower()
        self.include_subdomains = include_subdomains
    
    def matches(self, url: str) -> bool:
        """Check if the URL's domain matches this matcher's domain.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the domain matches, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            url_domain = parsed_url.netloc.lower()
            
            # Remove port if present
            if ':' in url_domain:
                url_domain = url_domain.split(':', 1)[0]
            
            if self.include_subdomains:
                return url_domain == self.domain or url_domain.endswith('.' + self.domain)
            else:
                return url_domain == self.domain
        except Exception as e:
            logger.error(f"Error matching domain for URL {url}: {e}")
            return False


class PatternMatcher(StrategyMatcher):
    """Match URLs based on a regex pattern.
    
    This matcher checks if a URL matches a specific regex pattern.
    """
    
    def __init__(self, pattern: Union[str, Pattern]):
        """Initialize the pattern matcher.
        
        Args:
            pattern: The regex pattern to match against URLs
        """
        if isinstance(pattern, str):
            self.pattern = re.compile(pattern)
        else:
            self.pattern = pattern
    
    def matches(self, url: str) -> bool:
        """Check if the URL matches this matcher's pattern.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the pattern matches, False otherwise
        """
        try:
            return bool(self.pattern.search(url))
        except Exception as e:
            logger.error(f"Error matching pattern for URL {url}: {e}")
            return False


class StrategyMapping:
    """Mapping between a matcher and a strategy.
    
    This class represents a mapping between a URL matcher and the strategy to use
    for URLs that match the matcher's criteria.
    """
    
    def __init__(self, matcher: StrategyMatcher, strategy_name: str, priority: int = 0):
        """Initialize the strategy mapping.
        
        Args:
            matcher: The matcher to use for URL matching
            strategy_name: The name of the strategy to use for matching URLs
            priority: The priority of this mapping (higher values take precedence)
        """
        self.matcher = matcher
        self.strategy_name = strategy_name
        self.priority = priority
    
    def matches(self, url: str) -> bool:
        """Check if the URL matches this mapping's matcher.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL matches, False otherwise
        """
        return self.matcher.matches(url)


@register_strategy(
    name="URLMappingStrategy",
    description="Strategy that selects appropriate extraction strategies based on URL patterns",
    category="composite"
)
class URLMappingStrategy(CompositeExtractionStrategy):
    """URL-based strategy selector.
    
    This strategy selects appropriate extraction strategies based on URL patterns,
    domains, or other criteria. It then delegates the extraction to the selected
    strategies and merges the results.
    """
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        model: Optional[str] = None,
        mappings: Optional[List[Dict[str, Any]]] = None,
        fallback_strategy: Optional[str] = "ComprehensiveLLMExtractionStrategy",
        merge_mode: str = "smart",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 60.0,
        **kwargs
    ):
        """Initialize the URLMappingStrategy.
        
        Args:
            api_token: The API token for the LLM provider
            model: The model to use for extraction
            mappings: List of mapping configurations
            fallback_strategy: Strategy to use if no mappings match
            merge_mode: How to merge results from multiple strategies
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
            timeout: Timeout for API calls in seconds
            **kwargs: Additional keyword arguments
        """
        # Initialize the strategy factory
        self.factory = StrategyFactory()
        
        # Initialize the strategy mappings
        self.strategy_mappings = []
        if mappings:
            for mapping in mappings:
                self._add_mapping_from_config(mapping)
        
        # Set the fallback strategy
        self.fallback_strategy_name = fallback_strategy
        
        # Create the fallback strategy instance
        fallback_strategy_instance = None
        if fallback_strategy:
            try:
                fallback_strategy_instance = self.factory.create(
                    fallback_strategy,
                    api_token=api_token,
                    model=model,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                    timeout=timeout,
                    **kwargs
                )
            except Exception as e:
                logger.warning(f"Failed to initialize fallback strategy {fallback_strategy}: {e}")
        
        # Initialize the base class with an empty list of strategies
        # (we'll select the appropriate strategies at extraction time)
        super().__init__(
            strategies=[fallback_strategy_instance] if fallback_strategy_instance else [],
            merge_mode=merge_mode
        )
        
        # Store configuration for creating strategies later
        self.api_token = api_token
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.kwargs = kwargs
        self.merge_mode = merge_mode
    
    def _add_mapping_from_config(self, config: Dict[str, Any]) -> None:
        """Add a strategy mapping from a configuration dictionary.
        
        Args:
            config: The mapping configuration
        """
        matcher_type = config.get("matcher_type", "domain")
        strategy_name = config.get("strategy_name")
        priority = config.get("priority", 0)
        
        if not strategy_name:
            logger.warning("Skipping mapping with no strategy name")
            return
        
        matcher = None
        if matcher_type == "domain":
            domain = config.get("domain")
            include_subdomains = config.get("include_subdomains", True)
            if domain:
                matcher = DomainMatcher(domain, include_subdomains)
        elif matcher_type == "pattern":
            pattern = config.get("pattern")
            if pattern:
                matcher = PatternMatcher(pattern)
        
        if matcher:
            self.strategy_mappings.append(StrategyMapping(matcher, strategy_name, priority))
        else:
            logger.warning(f"Failed to create matcher for config: {config}")
    
    def add_domain_mapping(self, domain: str, strategy_name: str, include_subdomains: bool = True, priority: int = 0) -> None:
        """Add a domain-based strategy mapping.
        
        Args:
            domain: The domain to match
            strategy_name: The name of the strategy to use for this domain
            include_subdomains: Whether to match subdomains as well
            priority: The priority of this mapping
        """
        matcher = DomainMatcher(domain, include_subdomains)
        self.strategy_mappings.append(StrategyMapping(matcher, strategy_name, priority))
    
    def add_pattern_mapping(self, pattern: Union[str, Pattern], strategy_name: str, priority: int = 0) -> None:
        """Add a pattern-based strategy mapping.
        
        Args:
            pattern: The regex pattern to match
            strategy_name: The name of the strategy to use for matching URLs
            priority: The priority of this mapping
        """
        matcher = PatternMatcher(pattern)
        self.strategy_mappings.append(StrategyMapping(matcher, strategy_name, priority))
    
    def get_strategy_for_url(self, url: str) -> Tuple[Optional[ExtractionStrategy], str]:
        """Get the appropriate strategy for a URL.
        
        Args:
            url: The URL to get a strategy for
            
        Returns:
            A tuple containing the strategy instance and its name, or (None, None) if no strategy matches
        """
        # Sort mappings by priority (descending)
        sorted_mappings = sorted(self.strategy_mappings, key=lambda m: m.priority, reverse=True)
        
        # Find the first matching mapping
        for mapping in sorted_mappings:
            if mapping.matches(url):
                try:
                    strategy = self.factory.create(
                        mapping.strategy_name,
                        api_token=self.api_token,
                        model=self.model,
                        max_retries=self.max_retries,
                        retry_delay=self.retry_delay,
                        timeout=self.timeout,
                        **self.kwargs
                    )
                    return strategy, mapping.strategy_name
                except Exception as e:
                    logger.error(f"Failed to create strategy {mapping.strategy_name}: {e}")
        
        # If no mapping matches, use the fallback strategy
        if self.fallback_strategy_name:
            try:
                strategy = self.factory.create(
                    self.fallback_strategy_name,
                    api_token=self.api_token,
                    model=self.model,
                    max_retries=self.max_retries,
                    retry_delay=self.retry_delay,
                    timeout=self.timeout,
                    **self.kwargs
                )
                return strategy, self.fallback_strategy_name
            except Exception as e:
                logger.error(f"Failed to create fallback strategy {self.fallback_strategy_name}: {e}")
        
        return None, ""
    
    async def extract(self, url: str, content: str, **kwargs) -> Dict[str, Any]:
        """Extract information from content using the appropriate strategy for the URL.
        
        Args:
            url: The URL of the content
            content: The content to extract information from
            **kwargs: Additional extraction parameters
            
        Returns:
            Dictionary of extracted information
        """
        logger.info(f"Extracting information for URL: {url}")
        
        # Get the appropriate strategy for this URL
        strategy, strategy_name = self.get_strategy_for_url(url)
        
        if not strategy:
            logger.warning(f"No strategy found for URL: {url}")
            return {"_metadata": {"error": "No suitable strategy found for URL"}}
        
        logger.info(f"Selected strategy for URL {url}: {strategy_name}")
        
        # Extract information using the selected strategy
        try:
            result = await strategy.extract(url, content, **kwargs)
            
            # Add metadata about the URL mapping
            if "_metadata" not in result:
                result["_metadata"] = {}
            
            result["_metadata"].update({
                "strategy": "URLMappingStrategy",
                "selected_strategy": strategy_name,
                "url": url
            })
            
            return result
        except Exception as e:
            logger.error(f"Extraction failed for URL {url} with strategy {strategy_name}: {e}")
            return {
                "_metadata": {
                    "error": f"Extraction failed: {str(e)}",
                    "strategy": "URLMappingStrategy",
                    "selected_strategy": strategy_name,
                    "url": url
                }
            }