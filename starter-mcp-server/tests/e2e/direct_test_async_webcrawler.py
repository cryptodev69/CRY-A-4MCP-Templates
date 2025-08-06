import asyncio
import sys
import os
import base64

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Direct import of AsyncWebCrawler
from crawl4ai import AsyncWebCrawler

async def test_direct_async_webcrawler():
    print("Creating AsyncWebCrawler instance...")
    crawler = AsyncWebCrawler(verbose=True)
    
    try:
        # Use the crawler with async context manager
        print("Crawling Altcoin Season Index website...")
        async with crawler as c:
            result = await c.arun(
                url='https://www.blockchaincenter.net/en/altcoin-season-index/',
                bypass_cache=True,
                verbose=True,
                user_agent="Test Crawler/1.0",
                headless=True,
                word_count_threshold=100,
                screenshot=True,  # Explicitly set screenshot to True
                extract_images=True  # Try passing extract_images directly
            )
        
        print("\nCrawl Result:")
        print(f"Success: {hasattr(result, 'markdown') and len(result.markdown) > 0}")
        print(f"Content Length: {len(result.markdown) if hasattr(result, 'markdown') else 0} characters")
        
        # Print extracted media information
        print("\nExtracted Media:")
        try:
            if hasattr(result, 'media') and result.media:
                # Check if media is a list or another type
                if isinstance(result.media, list):
                    for i, media_item in enumerate(result.media):
                        if isinstance(media_item, dict):
                            print(f"  {i+1}. Type: {media_item.get('type', 'unknown')}, URL: {media_item.get('url', 'N/A')}")
                        else:
                            print(f"  {i+1}. Media item: {media_item}")
                else:
                    print(f"  Media is not a list but: {type(result.media).__name__}")
                    print(f"  Media content: {result.media}")
            else:
                print("  No media extracted")
        except Exception as e:
            print(f"  Error processing media: {str(e)}")
            import traceback
            traceback.print_exc()
            
        # Print screenshot information
        print("\nScreenshot:")
        try:
            print(f"  Has 'screenshot' attribute: {hasattr(result, 'screenshot')}")
            if hasattr(result, 'screenshot'):
                print(f"  Screenshot type: {type(result.screenshot).__name__}")
                print(f"  Screenshot is None: {result.screenshot is None}")
                print(f"  Screenshot is empty: {result.screenshot == ''}")
                
                if result.screenshot:
                    # Just print the first 100 characters of the base64 string to confirm it exists
                    print(f"  Screenshot captured: {result.screenshot[:100]}...")
                    
                    # Save the screenshot to a file
                    try:
                        screenshot_path = "direct_async_screenshot.png"
                        with open(screenshot_path, "wb") as f:
                            f.write(base64.b64decode(result.screenshot))
                        print(f"  Screenshot saved to: {screenshot_path}")
                    except Exception as e:
                        print(f"  Error saving screenshot: {str(e)}")
                else:
                    print("  Screenshot is empty or None")
            else:
                print("  No screenshot attribute found")
                
            # Print all available attributes of the result
            print("\nAll available attributes:")
            for attr in dir(result):
                if not attr.startswith('_'):
                    try:
                        value = getattr(result, attr)
                        value_type = type(value).__name__
                        print(f"  {attr}: {value_type}")
                    except Exception as e:
                        print(f"  {attr}: Error accessing - {str(e)}")
        except Exception as e:
            print(f"  Error processing screenshot: {str(e)}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_direct_async_webcrawler())