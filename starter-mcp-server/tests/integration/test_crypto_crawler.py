import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from cry_a_4mcp.crypto_crawler.crawler import CryptoCrawler


async def test_crypto_crawler():
    # Create a CryptoCrawler instance with enhanced configuration
    config = {
        "user_agent": "Test Crawler/1.0",
        "headless": True,
        "bypass_cache": True,  # Always get fresh content for testing
        "word_count_threshold": 100,  # Minimum word count for content quality
        "capture_screenshot": True,  # Enable screenshot capture
        "extract_images": True  # Enable image extraction
    }
    crawler = CryptoCrawler(config=config)
    print("Created CryptoCrawler instance with enhanced configuration")
    
    try:
        # Initialize the crawler
        await crawler.initialize()
        print("Initialized CryptoCrawler")
        
        # Test crawling with the Altcoin Season Index website
        result = await crawler.crawl_crypto_website(
            url='https://www.blockchaincenter.net/en/altcoin-season-index/',  # Altcoin Season Index
            content_type='market_data',
            extract_entities=True,
            generate_triples=True
        )
        
        print("\nCrawl Result:")
        print(f"Success: {result.metadata.success}")
        print(f"URL: {result.metadata.url}")
        print(f"Content Type: {result.metadata.content_type}")
        print(f"Content Length: {result.metadata.content_length} characters")
        print(f"Processing Time: {result.metadata.processing_time:.2f} seconds")
        print(f"Quality Score: {result.quality_score:.2f}")
        print(f"Entity Density: {result.metadata.entity_density:.4f}")
        print(f"Relationship Density: {result.metadata.relationship_density:.4f}")
        print(f"Has Structured Data: {result.metadata.has_structured_data}")
        
        print("\nExtracted Entities:")
        for entity in result.entities:
            print(f"  - {entity.name} ({entity.entity_type}): {entity.confidence}")
        
        print("\nExtracted Triples:")
        for triple in result.triples:
            print(f"  - {triple.subject} {triple.predicate} {triple.object}: {triple.confidence}")
        
        print("\nMarkdown Content:")
        # Print first 500 characters of markdown to avoid overwhelming output
        if result.markdown:
            print(result.markdown[:500] + "..." if len(result.markdown) > 500 else result.markdown)
        else:
            print("No markdown content generated")
            
        # Print extracted media information
        print("\nExtracted Media:")
        if hasattr(result, 'media') and result.media:
            for i, media_item in enumerate(result.media):
                print(f"  {i+1}. Type: {media_item.get('type', 'unknown')}, URL: {media_item.get('url', 'N/A')}")
        else:
            print("  No media extracted")
            
        # Print screenshot information
        print("\nScreenshot:")
        if hasattr(result, 'screenshot') and result.screenshot:
            # Just print the first 100 characters of the base64 string to confirm it exists
            print(f"  Screenshot captured: {result.screenshot[:100]}...")
            
            # Optionally save the screenshot to a file
            if result.screenshot:
                import base64
                try:
                    screenshot_path = "altcoin_season_index_screenshot.png"
                    with open(screenshot_path, "wb") as f:
                        f.write(base64.b64decode(result.screenshot))
                    print(f"  Screenshot saved to: {screenshot_path}")
                except Exception as e:
                    print(f"  Error saving screenshot: {str(e)}")
        else:
            print("  No screenshot captured")
    finally:
        # Ensure crawler is properly closed
        await crawler.close()
        print("\nCrawler closed properly")


if __name__ == "__main__":
    asyncio.run(test_crypto_crawler())