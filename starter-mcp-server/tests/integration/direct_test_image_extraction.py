import asyncio
import sys
import os
import base64

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Direct import of the crawler module
from cry_a_4mcp.crypto_crawler.crawler import CryptoCrawler
from cry_a_4mcp.crypto_crawler.models import CrawlResult


async def test_image_extraction():
    # Create a CryptoCrawler instance with image extraction enabled
    config = {
        "user_agent": "Test Crawler/1.0",
        "headless": True,
        "bypass_cache": True,
        "word_count_threshold": 100,
        "capture_screenshot": True,
        "extract_images": True
    }
    
    print("Creating CryptoCrawler instance...")
    crawler = CryptoCrawler(config=config)
    
    try:
        # Initialize the crawler
        print("Initializing crawler...")
        await crawler.initialize()
        
        # Test crawling with the Altcoin Season Index website
        print("Crawling Altcoin Season Index website...")
        result = await crawler.crawl_crypto_website(
            url='https://www.blockchaincenter.net/en/altcoin-season-index/',
            content_type='market_data',
            extract_entities=True,
            generate_triples=True
        )
        
        print("\nCrawl Result:")
        print(f"Success: {result.metadata.success}")
        print(f"Content Length: {result.metadata.content_length} characters")
        print(f"Quality Score: {result.quality_score:.2f}")
        
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
            
            # Save the screenshot to a file
            if result.screenshot:
                try:
                    screenshot_path = "altcoin_season_index_screenshot.png"
                    with open(screenshot_path, "wb") as f:
                        f.write(base64.b64decode(result.screenshot))
                    print(f"  Screenshot saved to: {screenshot_path}")
                except Exception as e:
                    print(f"  Error saving screenshot: {str(e)}")
        else:
            print("  No screenshot captured")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Ensure crawler is properly closed
        await crawler.close()
        print("\nCrawler closed properly")


if __name__ == "__main__":
    asyncio.run(test_image_extraction())