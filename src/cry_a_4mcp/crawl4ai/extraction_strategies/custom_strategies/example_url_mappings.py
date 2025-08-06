#!/usr/bin/env python3
"""
Example URL-to-Strategy mappings for extraction strategies.

This module provides example implementations of URL-to-strategy mappings
for different domains and URL patterns.
"""

import re
import logging
from typing import Dict, Any, List

from ..registry import register_strategy
from .url_strategy_mapper import URLMappingStrategy, DomainMatcher, PatternMatcher, StrategyMapping

# Configure logging
logger = logging.getLogger('example_url_mappings')


@register_strategy(
    name="CryptoNewsURLMappingStrategy",
    description="URL-based strategy selector for crypto news websites",
    category="crypto"
)
class CryptoNewsURLMappingStrategy(URLMappingStrategy):
    """URL-based strategy selector for crypto news websites.
    
    This strategy selects appropriate extraction strategies based on URL patterns
    and domains specific to crypto news websites.
    """
    
    def __init__(self, **kwargs):
        """Initialize the CryptoNewsURLMappingStrategy.
        
        Args:
            **kwargs: Additional keyword arguments passed to the parent class
        """
        # Define default mappings for crypto news websites
        default_mappings = [
            {
                "matcher_type": "domain",
                "domain": "coindesk.com",
                "include_subdomains": True,
                "strategy_name": "CryptoLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "cointelegraph.com",
                "include_subdomains": True,
                "strategy_name": "CryptoLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "decrypt.co",
                "include_subdomains": True,
                "strategy_name": "CryptoLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "pattern",
                "pattern": r"(crypto|bitcoin|ethereum|blockchain|nft)",
                "strategy_name": "CryptoLLMExtractionStrategy",
                "priority": 50
            }
        ]
        
        # Initialize the parent class with the default mappings
        super().__init__(mappings=default_mappings, fallback_strategy="NewsLLMExtractionStrategy", **kwargs)


@register_strategy(
    name="EcommerceURLMappingStrategy",
    description="URL-based strategy selector for e-commerce websites",
    category="product"
)
class EcommerceURLMappingStrategy(URLMappingStrategy):
    """URL-based strategy selector for e-commerce websites.
    
    This strategy selects appropriate extraction strategies based on URL patterns
    and domains specific to e-commerce websites.
    """
    
    def __init__(self, **kwargs):
        """Initialize the EcommerceURLMappingStrategy.
        
        Args:
            **kwargs: Additional keyword arguments passed to the parent class
        """
        # Define default mappings for e-commerce websites
        default_mappings = [
            {
                "matcher_type": "domain",
                "domain": "amazon.com",
                "include_subdomains": True,
                "strategy_name": "ProductLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "ebay.com",
                "include_subdomains": True,
                "strategy_name": "ProductLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "walmart.com",
                "include_subdomains": True,
                "strategy_name": "ProductLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "pattern",
                "pattern": r"/(product|item|dp)/",
                "strategy_name": "ProductLLMExtractionStrategy",
                "priority": 80
            },
            {
                "matcher_type": "pattern",
                "pattern": r"(review|rating|price|shipping|discount)",
                "strategy_name": "ProductLLMExtractionStrategy",
                "priority": 50
            }
        ]
        
        # Initialize the parent class with the default mappings
        super().__init__(mappings=default_mappings, fallback_strategy="ComprehensiveLLMExtractionStrategy", **kwargs)


@register_strategy(
    name="SocialMediaURLMappingStrategy",
    description="URL-based strategy selector for social media websites",
    category="social"
)
class SocialMediaURLMappingStrategy(URLMappingStrategy):
    """URL-based strategy selector for social media websites.
    
    This strategy selects appropriate extraction strategies based on URL patterns
    and domains specific to social media websites.
    """
    
    def __init__(self, **kwargs):
        """Initialize the SocialMediaURLMappingStrategy.
        
        Args:
            **kwargs: Additional keyword arguments passed to the parent class
        """
        # Define default mappings for social media websites
        default_mappings = [
            {
                "matcher_type": "domain",
                "domain": "twitter.com",
                "include_subdomains": True,
                "strategy_name": "SocialMediaLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "x.com",  # New Twitter domain
                "include_subdomains": True,
                "strategy_name": "SocialMediaLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "facebook.com",
                "include_subdomains": True,
                "strategy_name": "SocialMediaLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "instagram.com",
                "include_subdomains": True,
                "strategy_name": "SocialMediaLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "linkedin.com",
                "include_subdomains": True,
                "strategy_name": "SocialMediaLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "reddit.com",
                "include_subdomains": True,
                "strategy_name": "SocialMediaLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "pattern",
                "pattern": r"/(post|status|tweet|thread)/",
                "strategy_name": "SocialMediaLLMExtractionStrategy",
                "priority": 80
            }
        ]
        
        # Initialize the parent class with the default mappings
        super().__init__(mappings=default_mappings, fallback_strategy="ComprehensiveLLMExtractionStrategy", **kwargs)


@register_strategy(
    name="ComprehensiveURLMappingStrategy",
    description="Comprehensive URL-based strategy selector for all types of websites",
    category="composite"
)
class ComprehensiveURLMappingStrategy(URLMappingStrategy):
    """Comprehensive URL-based strategy selector for all types of websites.
    
    This strategy combines mappings from multiple domain-specific URL mapping strategies
    to provide a comprehensive solution for all types of websites.
    """
    
    def __init__(self, **kwargs):
        """Initialize the ComprehensiveURLMappingStrategy.
        
        Args:
            **kwargs: Additional keyword arguments passed to the parent class
        """
        # Define mappings for various types of websites
        mappings = []
        
        # Add crypto news mappings
        mappings.extend([
            {
                "matcher_type": "domain",
                "domain": "coindesk.com",
                "include_subdomains": True,
                "strategy_name": "CryptoLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "cointelegraph.com",
                "include_subdomains": True,
                "strategy_name": "CryptoLLMExtractionStrategy",
                "priority": 100
            }
        ])
        
        # Add e-commerce mappings
        mappings.extend([
            {
                "matcher_type": "domain",
                "domain": "amazon.com",
                "include_subdomains": True,
                "strategy_name": "ProductLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "ebay.com",
                "include_subdomains": True,
                "strategy_name": "ProductLLMExtractionStrategy",
                "priority": 100
            }
        ])
        
        # Add social media mappings
        mappings.extend([
            {
                "matcher_type": "domain",
                "domain": "twitter.com",
                "include_subdomains": True,
                "strategy_name": "SocialMediaLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "facebook.com",
                "include_subdomains": True,
                "strategy_name": "SocialMediaLLMExtractionStrategy",
                "priority": 100
            }
        ])
        
        # Add news mappings
        mappings.extend([
            {
                "matcher_type": "domain",
                "domain": "nytimes.com",
                "include_subdomains": True,
                "strategy_name": "NewsLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "bbc.com",
                "include_subdomains": True,
                "strategy_name": "NewsLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "cnn.com",
                "include_subdomains": True,
                "strategy_name": "NewsLLMExtractionStrategy",
                "priority": 100
            }
        ])
        
        # Add financial mappings
        mappings.extend([
            {
                "matcher_type": "domain",
                "domain": "bloomberg.com",
                "include_subdomains": True,
                "strategy_name": "FinancialLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "wsj.com",
                "include_subdomains": True,
                "strategy_name": "FinancialLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "ft.com",
                "include_subdomains": True,
                "strategy_name": "FinancialLLMExtractionStrategy",
                "priority": 100
            }
        ])
        
        # Add academic mappings
        mappings.extend([
            {
                "matcher_type": "domain",
                "domain": "arxiv.org",
                "include_subdomains": True,
                "strategy_name": "AcademicLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "scholar.google.com",
                "include_subdomains": True,
                "strategy_name": "AcademicLLMExtractionStrategy",
                "priority": 100
            },
            {
                "matcher_type": "domain",
                "domain": "researchgate.net",
                "include_subdomains": True,
                "strategy_name": "AcademicLLMExtractionStrategy",
                "priority": 100
            }
        ])
        
        # Add pattern-based mappings
        mappings.extend([
            {
                "matcher_type": "pattern",
                "pattern": r"(crypto|bitcoin|ethereum|blockchain|nft)",
                "strategy_name": "CryptoLLMExtractionStrategy",
                "priority": 50
            },
            {
                "matcher_type": "pattern",
                "pattern": r"/(product|item|dp)/",
                "strategy_name": "ProductLLMExtractionStrategy",
                "priority": 80
            },
            {
                "matcher_type": "pattern",
                "pattern": r"/(post|status|tweet|thread)/",
                "strategy_name": "SocialMediaLLMExtractionStrategy",
                "priority": 80
            },
            {
                "matcher_type": "pattern",
                "pattern": r"/(article|news|story)/",
                "strategy_name": "NewsLLMExtractionStrategy",
                "priority": 80
            },
            {
                "matcher_type": "pattern",
                "pattern": r"/(research|paper|study|journal)/",
                "strategy_name": "AcademicLLMExtractionStrategy",
                "priority": 80
            },
            {
                "matcher_type": "pattern",
                "pattern": r"/(market|stock|investor|finance)/",
                "strategy_name": "FinancialLLMExtractionStrategy",
                "priority": 80
            }
        ])
        
        # Initialize the parent class with the combined mappings
        super().__init__(
            mappings=mappings,
            fallback_strategy="ComprehensiveLLMExtractionStrategy",
            **kwargs
        )