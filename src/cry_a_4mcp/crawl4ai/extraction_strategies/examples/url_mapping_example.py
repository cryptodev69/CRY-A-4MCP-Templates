#!/usr/bin/env python3
"""
Example usage of URL-to-Extractor mapping.

This module demonstrates how to use the URL-to-extractor mapping system to process
content with the appropriate extractors based on URL patterns.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

from ..factory import StrategyFactory
from ..custom_strategies.url_mapping import URLExtractorMapping, ExtractorConfig, URLMappingManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('url_mapping_example')


async def extract_from_url(url: str, content: str, mapping_manager: URLMappingManager) -> Dict[str, Dict[str, Any]]:
    """Extract information from a URL using the configured extractors.
    
    Args:
        url: The URL of the content
        content: The content to extract information from
        mapping_manager: The URL mapping manager with configured mappings
            
    Returns:
        A dictionary of extracted information organized by target group
    """
    factory = StrategyFactory()
    
    # Get applicable extractors for this URL
    applicable_extractors = mapping_manager.get_extractors_for_url(url)
    
    if not applicable_extractors:
        logger.info(f"No extractors configured for URL: {url}")
        return {}
    
    # Process with each applicable extractor
    results = {}
    for config in applicable_extractors:
        logger.info(f"Using extractor: {config.extractor_id} for target group: {config.target_group}")
        extractor = factory.create(config.extractor_id)
        result = await extractor.extract(content, url=url)
        results[config.target_group] = result
    
    return results


async def main():
    """Run examples of URL-to-extractor mapping."""
    # Create a mapping manager and configure mappings
    mapping_manager = URLMappingManager()
    
    # Configure crypto news mappings
    crypto_extractors = [
        ExtractorConfig(extractor_id="CryptoEntityExtractor", target_group="entities"),
        ExtractorConfig(extractor_id="CryptoTripleExtractor", target_group="triples"),
        ExtractorConfig(extractor_id="SentimentAnalysisExtractor", target_group="sentiment")
    ]
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="coindesk.com",
        pattern_type="domain",
        extractors=crypto_extractors
    ))
    
    # Configure e-commerce mappings
    ecommerce_extractors = [
        ExtractorConfig(extractor_id="ProductExtractor", target_group="products"),
        ExtractorConfig(extractor_id="SentimentAnalysisExtractor", target_group="sentiment")
    ]
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="amazon.com",
        pattern_type="domain",
        extractors=ecommerce_extractors
    ))
    
    # Configure social media mappings
    social_extractors = [
        ExtractorConfig(extractor_id="SocialMediaExtractor", target_group="social"),
        ExtractorConfig(extractor_id="SentimentAnalysisExtractor", target_group="sentiment")
    ]
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="twitter.com",
        pattern_type="domain",
        extractors=social_extractors
    ))
    
    # Example URLs and content
    examples = [
        {
            "url": "https://www.coindesk.com/markets/2023/04/15/bitcoin-price-analysis/",
            "content": "Bitcoin price has been fluctuating between $27,000 and $30,000 over the past week..."
        },
        {
            "url": "https://www.amazon.com/dp/B07ZPML7NP/",
            "content": "Apple AirPods Pro - Active noise cancellation for immersive sound. Transparency mode for hearing..."
        },
        {
            "url": "https://twitter.com/elonmusk/status/1234567890",
            "content": "Just bought some more #Bitcoin. I believe in its long-term potential!"
        },
        {
            "url": "https://www.nytimes.com/2023/04/15/business/crypto-regulation-sec.html",
            "content": "The Securities and Exchange Commission has proposed new regulations for cryptocurrency exchanges..."
        }
    ]
    
    # Process each example
    for example in examples:
        url = example["url"]
        content = example["content"]
        
        logger.info(f"\nProcessing URL: {url}")
        logger.info(f"Content: {content[:50]}...")
        
        # Extract using configured mappings
        results = await extract_from_url(url, content, mapping_manager)
        
        if results:
            logger.info("\nExtracted information by target group:")
            for target_group, result in results.items():
                logger.info(f"Target group '{target_group}': {result}")
        else:
            logger.info("\nNo extractors configured for this URL")


if __name__ == "__main__":
    asyncio.run(main())