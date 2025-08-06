#!/usr/bin/env python3
"""
Integration example for URL-to-Extractor mapping.

This module demonstrates how to integrate the URL-to-extractor mapping system
into a content extraction pipeline, including batch processing and interactive mode.
"""

import asyncio
import argparse
import json
import logging
from typing import Dict, Any, List
from pathlib import Path

from ..factory import ExtractorFactory
from ..custom_strategies.url_mapping import URLExtractorMapping, ExtractorConfig, URLMappingManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('url_extractor_mapping_integration')


async def extract_from_multiple_sources(sources: List[Dict[str, Any]], 
                                       mapping_manager: URLMappingManager) -> List[Dict[str, Any]]:
    """Extract information from multiple sources using URL-to-extractor mapping.
    
    Args:
        sources: List of source dictionaries, each containing 'url' and 'content' keys.
        mapping_manager: The URL mapping manager to use for finding extractors.
        
    Returns:
        List of extraction results, one for each source.
    """
    results = []
    
    for source in sources:
        url = source.get('url')
        content = source.get('content')
        
        if not url:
            logger.warning("Source missing URL, skipping")
            results.append({"error": "Missing URL"})
            continue
            
        if not content:
            logger.warning(f"Source missing content for URL: {url}, skipping")
            results.append({"url": url, "error": "Missing content"})
            continue
        
        try:
            # Get all applicable extractors for this URL
            extractors = mapping_manager.get_extractors_for_url(url)
            
            if not extractors:
                logger.warning(f"No extractors found for URL: {url}")
                results.append({"url": url, "error": "No suitable extractors found"})
                continue
            
            # Create extractor factory
            factory = ExtractorFactory()
            
            # Organize results by target group
            extraction_result = {}
            
            for extractor_config in extractors:
                # Create the extractor
                extractor = factory.create(extractor_config.extractor_id)
                
                if not extractor:
                    logger.warning(f"Failed to create extractor: {extractor_config.extractor_id}")
                    continue
                
                # Extract content using the extractor
                try:
                    result = await extractor.extract(content, url=url, **extractor_config.params)
                    
                    # Store result under the target group
                    target_group = extractor_config.target_group
                    extraction_result[target_group] = result
                    
                    logger.info(f"Successfully extracted {target_group} from {url}")
                except Exception as e:
                    logger.error(f"Error extracting {extractor_config.target_group} from {url}: {str(e)}")
                    extraction_result[extractor_config.target_group] = {"error": str(e)}
            
            # Add metadata
            extraction_result["_metadata"] = {
                "url": url,
                "extractors_used": [e.extractor_id for e in extractors]
            }
            
            results.append(extraction_result)
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            results.append({"url": url, "error": str(e)})
    
    return results


async def process_batch(batch_file: str) -> None:
    """Process a batch of sources from a JSON file.
    
    Args:
        batch_file: Path to a JSON file containing a list of sources.
    """
    try:
        # Load the batch file
        batch_path = Path(batch_file)
        if not batch_path.exists():
            logger.error(f"Batch file not found: {batch_file}")
            return
            
        with open(batch_path, 'r') as f:
            sources = json.load(f)
            
        if not isinstance(sources, list):
            logger.error(f"Batch file must contain a list of sources")
            return
            
        # Create a URL mapping manager with default configurations
        mapping_manager = create_default_mapping_manager()
        
        # Process the sources
        logger.info(f"Processing {len(sources)} sources from {batch_file}")
        results = await extract_from_multiple_sources(sources, mapping_manager)
        
        # Save the results
        output_path = batch_path.with_suffix('.results.json')
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Results saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error processing batch file: {str(e)}")


def create_default_mapping_manager() -> URLMappingManager:
    """Create a URL mapping manager with default configurations.
    
    Returns:
        Configured URLMappingManager instance.
    """
    mapping_manager = URLMappingManager()
    
    # Crypto news website mappings
    crypto_extractors = [
        ExtractorConfig(extractor_id="TitleExtractor", target_group="title"),
        ExtractorConfig(extractor_id="AuthorExtractor", target_group="author"),
        ExtractorConfig(extractor_id="DateExtractor", target_group="date"),
        ExtractorConfig(extractor_id="CryptoContentExtractor", target_group="content"),
        ExtractorConfig(extractor_id="CryptoPriceExtractor", target_group="price_data")
    ]
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="coindesk.com",
        pattern_type="domain",
        extractors=crypto_extractors,
        priority=100
    ))
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="cointelegraph.com",
        pattern_type="domain",
        extractors=crypto_extractors,
        priority=100
    ))
    
    # E-commerce website mappings
    ecommerce_extractors = [
        ExtractorConfig(extractor_id="TitleExtractor", target_group="title"),
        ExtractorConfig(extractor_id="PriceExtractor", target_group="price"),
        ExtractorConfig(extractor_id="ProductDescriptionExtractor", target_group="description"),
        ExtractorConfig(extractor_id="ReviewExtractor", target_group="reviews"),
        ExtractorConfig(extractor_id="ImageExtractor", target_group="images")
    ]
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="amazon.com",
        pattern_type="domain",
        extractors=ecommerce_extractors,
        priority=100
    ))
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="ebay.com",
        pattern_type="domain",
        extractors=ecommerce_extractors,
        priority=100
    ))
    
    # Social media website mappings
    social_extractors = [
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
        extractors=social_extractors,
        priority=100
    ))
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern="x.com",
        pattern_type="domain",
        extractors=social_extractors,
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
    
    # Fallback extractors for any URL
    fallback_extractors = [
        ExtractorConfig(extractor_id="TitleExtractor", target_group="title"),
        ExtractorConfig(extractor_id="ContentExtractor", target_group="content")
    ]
    mapping_manager.add_mapping(URLExtractorMapping(
        url_pattern=".*",
        pattern_type="exact",
        extractors=fallback_extractors,
        priority=10  # Low priority, used only if no other mappings match
    ))
    
    return mapping_manager


async def interactive_mode() -> None:
    """Run the URL-to-extractor mapping in interactive mode."""
    # Create a URL mapping manager with default configurations
    mapping_manager = create_default_mapping_manager()
    
    print("\nURL-to-Extractor Mapping Interactive Mode")
    print("Enter 'quit' to exit\n")
    
    while True:
        url = input("\nEnter URL (or 'quit' to exit): ").strip()
        if url.lower() == 'quit':
            break
        
        if not url:
            print("URL cannot be empty. Please try again.")
            continue
        
        content = input("Enter content: ").strip()
        if not content:
            print("Content cannot be empty. Please try again.")
            continue
        
        try:
            # Get the extractors that would be used for this URL
            extractors = mapping_manager.get_extractors_for_url(url)
            
            if not extractors:
                print(f"\nNo extractors found for URL: {url}")
                continue
                
            print(f"\nSelected extractors: {', '.join([e.extractor_id for e in extractors])}")
            
            # Create extractor factory
            factory = ExtractorFactory()
            
            # Extract information
            extraction_result = {}
            
            for extractor_config in extractors:
                # Create the extractor
                extractor = factory.create(extractor_config.extractor_id)
                
                if not extractor:
                    print(f"Failed to create extractor: {extractor_config.extractor_id}")
                    continue
                
                # Extract content using the extractor
                try:
                    result = await extractor.extract(content, url=url, **extractor_config.params)
                    
                    # Store result under the target group
                    target_group = extractor_config.target_group
                    extraction_result[target_group] = result
                    
                except Exception as e:
                    print(f"Error extracting {extractor_config.target_group}: {str(e)}")
                    extraction_result[extractor_config.target_group] = {"error": str(e)}
            
            # Add metadata
            extraction_result["_metadata"] = {
                "url": url,
                "extractors_used": [e.extractor_id for e in extractors]
            }
            
            # Print the result
            print("\nExtracted information:")
            print(json.dumps(extraction_result, indent=2))
            
        except Exception as e:
            print(f"\nError: {str(e)}")


async def main():
    """Main entry point for the URL-to-extractor mapping integration example."""
    parser = argparse.ArgumentParser(description="URL-to-Extractor Mapping Integration Example")
    parser.add_argument(
        "--batch", "-b",
        help="Path to a JSON file containing a batch of sources to process"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to a JSON configuration file for URL mappings"
    )
    
    args = parser.parse_args()
    
    if args.batch:
        await process_batch(args.batch)
    elif args.interactive:
        await interactive_mode()
    else:
        # Default to interactive mode if no arguments are provided
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())