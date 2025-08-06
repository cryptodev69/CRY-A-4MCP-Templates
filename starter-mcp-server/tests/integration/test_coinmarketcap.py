import asyncio
import json
import base64
from crawl4ai import AsyncWebCrawler

async def test_coinmarketcap():
    crawler = AsyncWebCrawler(verbose=True)
    async with crawler as c:
        result = await c.arun(
            url='https://coinmarketcap.com/charts/altcoin-season-index/',
            bypass_cache=True,
            verbose=True,
            headless=True,
            screenshot=True,
            extract_images=True
        )
        
        print(f'Success: {hasattr(result, "markdown") and len(result.markdown) > 0}')
        print(f'Content Length: {len(result.markdown) if hasattr(result, "markdown") else 0} characters')
        
        # Print first 500 characters of markdown content
        if hasattr(result, "markdown") and result.markdown:
            print("\nMarkdown Content Preview (first 500 chars):")
            print(result.markdown[:500] + "...")
        
        # Check for media
        if hasattr(result, "media") and result.media:
            # Check if media is a dictionary or list
            if isinstance(result.media, dict):
                print(f"\nExtracted Media: {len(result.media)} items")
                # If it's a dictionary, iterate through items
                count = 0
                for key, media_item in result.media.items():
                    if count < 3:  # Show first 3 media items
                        if isinstance(media_item, dict):
                            print(f"Media {count+1}: {media_item.get('url', 'No URL')}")
                        elif isinstance(media_item, list) and len(media_item) > 0:
                            if isinstance(media_item[0], dict):
                                print(f"Media {count+1}: {media_item[0].get('url', 'No URL')}")
                            else:
                                print(f"Media {count+1}: {str(media_item[0])[:100]}")
                        else:
                            print(f"Media {count+1}: {str(media_item)[:100]}")
                        count += 1
            elif isinstance(result.media, list):
                print(f"\nExtracted Media: {len(result.media)} items")
                # If it's a list, iterate through first 3 items
                for i, media_item in enumerate(result.media[:3]):
                    if isinstance(media_item, dict):
                        print(f"Media {i+1}: {media_item.get('url', 'No URL')}")
                    else:
                        print(f"Media {i+1}: {str(media_item)[:100]}")
            else:
                print(f"\nExtracted Media: Type {type(result.media)}")
                print(str(result.media)[:200] + "..." if len(str(result.media)) > 200 else str(result.media))
        else:
            print("\nNo media extracted")
        
        # Check for screenshots
        if hasattr(result, "screenshots") and result.screenshots:
            # Check if screenshots is a dictionary or list
            if isinstance(result.screenshots, dict):
                print(f"\nScreenshots: {len(result.screenshots)} captured")
                # If it's a dictionary, get the first item
                if len(result.screenshots) > 0:
                    first_key = next(iter(result.screenshots))
                    screenshot_item = result.screenshots[first_key]
                    if isinstance(screenshot_item, dict):
                        screenshot_data = screenshot_item.get('data')
                    elif isinstance(screenshot_item, list) and len(screenshot_item) > 0:
                        screenshot_data = screenshot_item[0].get('data') if isinstance(screenshot_item[0], dict) else None
                    else:
                        screenshot_data = None
                        
                    if screenshot_data:
                        try:
                            with open('coinmarketcap_screenshot.png', 'wb') as f:
                                f.write(base64.b64decode(screenshot_data))
                            print("Screenshot saved to coinmarketcap_screenshot.png")
                        except Exception as e:
                            print(f"Error saving screenshot: {e}")
            elif isinstance(result.screenshots, list):
                print(f"\nScreenshots: {len(result.screenshots)} captured")
                # If it's a list, get the first item
                if len(result.screenshots) > 0:
                    screenshot_item = result.screenshots[0]
                    if isinstance(screenshot_item, dict):
                        screenshot_data = screenshot_item.get('data')
                    else:
                        screenshot_data = None
                        
                    if screenshot_data:
                        try:
                            with open('coinmarketcap_screenshot.png', 'wb') as f:
                                f.write(base64.b64decode(screenshot_data))
                            print("Screenshot saved to coinmarketcap_screenshot.png")
                        except Exception as e:
                            print(f"Error saving screenshot: {e}")
            else:
                print(f"\nScreenshots: Type {type(result.screenshots)}")
                print(str(result.screenshots)[:200] + "..." if len(str(result.screenshots)) > 200 else str(result.screenshots))
        else:
            print("\nNo screenshots captured")

        # Print the structure of the result object
        print("\nResult Object Structure:")
        for attr in dir(result):
            if not attr.startswith('_'):
                try:
                    value = getattr(result, attr)
                    if not callable(value):
                        print(f"{attr}: {type(value)}")
                except Exception as e:
                    print(f"{attr}: Error accessing - {e}")

if __name__ == "__main__":
    asyncio.run(test_coinmarketcap())