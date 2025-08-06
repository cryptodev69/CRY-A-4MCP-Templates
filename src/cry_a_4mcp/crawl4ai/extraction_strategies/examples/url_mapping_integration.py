#!/usr/bin/env python3
"""
Integration example for URL-to-Strategy mapping.

This module demonstrates how to integrate URL mapping strategies into a
real-world content extraction pipeline.
"""

import asyncio
import logging
import argparse
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from ..factory import StrategyFactory
from ..custom_strategies.url_strategy_mapper import URLMappingStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('url_mapping_integration')


async def extract_from_multiple_sources(sources: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Extract information from multiple sources using URL-based strategy selection.
    
    Args:
        sources: A list of dictionaries, each containing a URL and content
            
    Returns:
        A list of dictionaries containing the extracted information and metadata
    """
    factory = StrategyFactory()
    url_strategy = factory.create("ComprehensiveURLMappingStrategy")
    
    results = []
    for source in sources:
        url = source.get("url")
        content = source.get("content")
        
        if not url or not content:
            logger.warning(f"Skipping source with missing URL or content: {source}")
            continue
        
        try:
            # Extract domain for logging
            domain = urlparse(url).netloc
            logger.info(f"Processing content from {domain}")
            
            # Extract information using the URL mapping strategy
            result = await url_strategy.extract(content, url=url)
            
            # Add source metadata
            result["source_url"] = url
            result["source_domain"] = domain
            
            results.append(result)
            logger.info(f"Successfully extracted information from {domain}")
            
        except Exception as e:
            logger.error(f"Error extracting information from {url}: {str(e)}")
    
    return results


async def process_batch(batch_file: str) -> None:
    """Process a batch of sources from a file.
    
    Args:
        batch_file: Path to a JSON file containing a list of sources
    """
    import json
    
    try:
        with open(batch_file, 'r') as f:
            sources = json.load(f)
        
        if not isinstance(sources, list):
            logger.error(f"Batch file must contain a JSON array of sources")
            return
        
        logger.info(f"Processing {len(sources)} sources from {batch_file}")
        results = await extract_from_multiple_sources(sources)
        
        # Save results to a file
        output_file = f"{batch_file.rsplit('.', 1)[0]}_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved results to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing batch file {batch_file}: {str(e)}")


async def interactive_mode() -> None:
    """Run in interactive mode, allowing the user to input URLs and content."""
    factory = StrategyFactory()
    url_strategy = factory.create("ComprehensiveURLMappingStrategy")
    
    print("\nURL-to-Strategy Mapping Interactive Mode")
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
            # Get the strategy that would be used for this URL
            strategy = await url_strategy.get_strategy_for_url(url)
            strategy_name = strategy.__class__.__name__
            print(f"\nSelected strategy: {strategy_name}")
            
            # Extract information
            result = await url_strategy.extract(content, url=url)
            
            # Print the result
            print("\nExtracted information:")
            import json
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"\nError: {str(e)}")


async def main():
    """Main entry point for the URL mapping integration example."""
    parser = argparse.ArgumentParser(description="URL-to-Strategy Mapping Integration Example")
    parser.add_argument(
        "--batch", "-b",
        help="Path to a JSON file containing a batch of sources to process"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
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