#!/usr/bin/env python3
"""
Example for URL-to-Extractor mapping.

This module demonstrates how to use the URL-to-extractor mapping system to
process content from different URLs with appropriate extractors based on
URL patterns and target groups.
"""

import asyncio
import logging
from typing import Dict, Any, List

from ..factory import ExtractorFactory
from ..custom_strategies.url_mapping import URLExtractorMapping, ExtractorConfig, URLMappingManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('url_extractor_mapping_example')


async def extract_from_url(url: str, content: str, mapping_manager: URLMappingManager) -> Dict[str, Any]:
    """Extract information from a URL using the appropriate extractors.
    
    Args:
        url: The URL to extract content from.
        content: The content to extract information from.
        mapping_manager: The URL mapping manager to use for finding extractors.
        
    Returns:
        Dictionary of extraction results organized by target group.
    """
    # Get all applicable extractors for this URL
    extractors = mapping_manager.get_extractors_for_url(url)
    
    if not extractors:
        logger.warning(f"No extractors found for URL: {url}")
        return {"_metadata": {"error": "No suitable extractors found for URL"}}
    
    # Create extractor factory
    factory = ExtractorFactory()
    
    # Organize results by target group
    results = {}
    
    for extractor_config in extractors:
        # Create the extractor
        extractor = factory.create(extractor_config.extractor_id)
        
        if not extractor:
            logger.warning(f"Failed to create extractor: {extractor_config.extractor_id}")
            continue
        
        # Extract content using the extractor
        try:
            extraction_result = await extractor.extract(content, url=url, **extractor_config.params)
            
            # Store result under the target group
            target_group = extractor_config.target_group
            results[target_group] = extraction_result
            
            logger.info(f"Successfully extracted {target_group} from {url}")
        except Exception as e:
            logger.error(f"Error extracting {extractor_config.target_group} from {url}: {str(e)}")
            results[extractor_config.target_group] = {"error": str(e)}
    
    # Add metadata
    results["_metadata"] = {
        "url": url,
        "extractors_used": [e.extractor_id for e in extractors]
    }
    
    return results


async def main():
    """Main entry point for the URL-to-extractor mapping example."""
    # Create a URL mapping manager
    mapping_manager = URLMappingManager()
    
    # Configure mappings for different domains
    
    # Crypto news website mappings
    coindesk_extractors = [
        ExtractorConfig(extractor_id="TitleExtractor", target_group="title"),
        ExtractorConfig(extractor_id="AuthorExtractor", target_group="author"),
        ExtractorConfig(extractor_id="DateExtractor", target_group="date"),
        ExtractorConfig(extractor_id="CryptoContentExtractor", target_group="content"),
        ExtractorConfig(extractor_id="CryptoPriceExtractor", target_group="price_data")
    ]
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="coindesk.com",
        pattern_type="domain",
        extractors=coindesk_extractors,
        priority=100
    ))
    
    # E-commerce website mappings
    amazon_extractors = [
        ExtractorConfig(extractor_id="TitleExtractor", target_group="title"),
        ExtractorConfig(extractor_id="PriceExtractor", target_group="price"),
        ExtractorConfig(extractor_id="ProductDescriptionExtractor", target_group="description"),
        ExtractorConfig(extractor_id="ReviewExtractor", target_group="reviews"),
        ExtractorConfig(extractor_id="ImageExtractor", target_group="images")
    ]
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="amazon.com",
        pattern_type="domain",
        extractors=amazon_extractors,
        priority=100
    ))
    
    # Social media website mappings
    twitter_extractors = [
        ExtractorConfig(extractor_id="TitleExtractor", target_group="title"),
        ExtractorConfig(extractor_id="AuthorExtractor", target_group="author"),
        ExtractorConfig(extractor_id="DateExtractor", target_group="date"),
        ExtractorConfig(extractor_id="SocialMediaContentExtractor", target_group="content"),
        ExtractorConfig(extractor_id="HashtagExtractor", target_group="hashtags"),
        ExtractorConfig(extractor_id="MentionExtractor", target_group="mentions")
    ]
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="twitter.com",
        pattern_type="domain",
        extractors=twitter_extractors,
        priority=100
    ))
    
    # Path-based mappings for product pages
    product_page_extractors = [
        ExtractorConfig(extractor_id="PriceExtractor", target_group="price"),
        ExtractorConfig(extractor_id="ProductDescriptionExtractor", target_group="description")
    ]
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="/product/",
        pattern_type="path",
        extractors=product_page_extractors,
        priority=80
    ))
    
    # Example URLs to process
    example_urls = [
        "https://www.coindesk.com/markets/2023/01/01/bitcoin-price-surges-to-new-high/",
        "https://www.amazon.com/product/B08N5KWB9H",
        "https://twitter.com/user/status/1234567890",
        "https://www.example.com/product/123"
    ]
    
    # Process each URL
    for url in example_urls:
        print(f"\nProcessing URL: {url}")
        
        # In a real scenario, you would fetch the content from the URL
        # For this example, we'll use a placeholder content
        content = f"Sample content from {url}"
        
        # Extract information using the URL mapping system
        result = await extract_from_url(url, content, mapping_manager)
        
        # Print the result
        print("Extracted information:")
        for group, data in result.items():
            if group == "_metadata":
                continue
            print(f"  {group}: {data if isinstance(data, str) else '[complex data]'}")
        
        print(f"Extractors used: {', '.join(result['_metadata']['extractors_used'])}")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())