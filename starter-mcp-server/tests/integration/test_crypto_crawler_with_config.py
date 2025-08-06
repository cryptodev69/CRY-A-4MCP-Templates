import asyncio
import sys
import os
import json
from typing import Dict, List
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from cry_a_4mcp.crawl4ai.crawler import CryptoCrawler
from cry_a_4mcp.crawl4ai.models import CrawlResult


async def test_crypto_crawler_with_config():
    # Path to the configuration file
    config_file_path = os.path.join(
        os.path.dirname(__file__),
        'src/cry_a_4mcp/crawl4ai/crypto_website_config.json'
    )
    
    print(f"Loading configuration from: {config_file_path}")
    
    # Create a CryptoCrawler instance with configuration from file
    crawler = CryptoCrawler(config_file_path=config_file_path)
    print("Created CryptoCrawler instance with configuration from file")
    
    # Print loaded websites
    print(f"\nLoaded {len(crawler.websites)} websites:")
    for website in crawler.websites:
        print(f"  - {website['name']}: {website['url']} (Type: {website['content_type']}, Priority: {website['priority']})")
    
    # Print crawler configuration
    print("\nCrawler Configuration:")
    for key, value in crawler.config.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        else:
            print(f"  {key}: {value}")
    
    try:
        # Initialize the crawler
        await crawler.initialize()
        print("\nInitialized CryptoCrawler")
        
        # Test crawling a specific website by name
        website_name = "Altcoin Season Index"
        website = crawler.get_website_by_name(website_name)
        
        if website:
            print(f"\nCrawling {website_name}...")
            result = await crawler.crawl_crypto_website(
                url=website['url'],
                content_type=website['content_type'],
                extract_entities=True,
                generate_triples=True
            )
            
            print_crawl_result(result)
        else:
            print(f"Website '{website_name}' not found in configuration")
        
        # Test crawling all high priority websites
        print("\nCrawling all high priority websites...")
        high_priority_websites = crawler.get_websites_by_priority("high")
        print(f"Found {len(high_priority_websites)} high priority websites")
        
        results = await crawler.crawl_all_websites(priority="high")
        print(f"Crawled {len(results)} high priority websites")
        
        # Print summary of results
        print("\nCrawl Results Summary:")
        for i, result in enumerate(results):
            print(f"  {i+1}. {result.metadata.url}: Success={result.metadata.success}, Quality={result.quality_score:.2f}, Entities={len(result.entities)}, Triples={len(result.triples)}")
        
    finally:
        # Ensure crawler is properly closed
        await crawler.close()
        print("\nCrawler closed properly")


def print_crawl_result(result: CrawlResult) -> None:
    """Print details of a crawl result."""
    print("\nCrawl Result:")
    print(f"Success: {result.metadata.success}")
    print(f"URL: {result.metadata.url}")
    print(f"Content Type: {result.metadata.content_type}")
    print(f"Content Length: {result.metadata.content_length} characters")
    print(f"Processing Time: {result.metadata.processing_time:.2f} seconds")
    print(f"Quality Score: {result.quality_score:.2f}")
    
    print("\nExtracted Entities:")
    for entity in result.entities[:5]:  # Print first 5 entities
        print(f"  - {entity.name} ({entity.entity_type}): {entity.confidence}")
    if len(result.entities) > 5:
        print(f"  ... and {len(result.entities) - 5} more entities")
    
    print("\nExtracted Triples:")
    for triple in result.triples[:5]:  # Print first 5 triples
        print(f"  - {triple.subject} {triple.predicate} {triple.object}: {triple.confidence}")
    if len(result.triples) > 5:
        print(f"  ... and {len(result.triples) - 5} more triples")
    
    print("\nMarkdown Content (excerpt):")
    # Print first 300 characters of markdown to avoid overwhelming output
    if result.markdown:
        print(result.markdown[:300] + "..." if len(result.markdown) > 300 else result.markdown)
    else:
        print("No markdown content generated")


async def test_llm_extraction_integration():
    """Test integrating LLMExtractionStrategy with CryptoCrawler."""
    # This would be implemented in a future update
    pass


if __name__ == "__main__":
    asyncio.run(test_crypto_crawler_with_config())