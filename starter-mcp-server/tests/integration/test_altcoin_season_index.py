import asyncio
import json
import base64
import os
from crawl4ai import AsyncWebCrawler

async def crawl_url(url, crawler, output_prefix):
    """Crawl a URL and save the results"""
    print(f"\n{'='*50}\nCrawling {url}\n{'='*50}")
    
    result = await crawler.arun(
        url=url,
        bypass_cache=True,
        verbose=True,
        headless=True,
        screenshot=True,
        extract_images=True
    )
    
    success = hasattr(result, "markdown") and len(result.markdown) > 0
    content_length = len(result.markdown) if hasattr(result, "markdown") else 0
    
    print(f'Success: {success}')
    print(f'Content Length: {content_length} characters')
    
    # Save markdown to file
    if success:
        with open(f"{output_prefix}_content.md", "w") as f:
            f.write(result.markdown)
        print(f"Markdown content saved to {output_prefix}_content.md")
    
    # Print first 500 characters of markdown content
    if hasattr(result, "markdown") and result.markdown:
        print("\nMarkdown Content Preview (first 500 chars):")
        print(result.markdown[:500] + "...")
    
    # Check for media
    if hasattr(result, "media") and result.media:
        media_count = len(result.media)
        print(f"\nExtracted Media: {media_count} items")
        
        # Save media info to file
        with open(f"{output_prefix}_media.json", "w") as f:
            json.dump(result.media, f, indent=2)
        print(f"Media information saved to {output_prefix}_media.json")
    else:
        print("\nNo media extracted")
    
    # Check for screenshots
    if hasattr(result, "screenshot") and result.screenshot:
        print("\nScreenshot captured")
        try:
            with open(f"{output_prefix}_screenshot.png", "wb") as f:
                f.write(base64.b64decode(result.screenshot))
            print(f"Screenshot saved to {output_prefix}_screenshot.png")
        except Exception as e:
            print(f"Error saving screenshot: {e}")
    elif hasattr(result, "screenshots") and result.screenshots:
        print("\nScreenshots captured")
        try:
            # Try to find screenshot data
            screenshot_data = None
            if isinstance(result.screenshots, dict) and len(result.screenshots) > 0:
                first_key = next(iter(result.screenshots))
                item = result.screenshots[first_key]
                if isinstance(item, dict) and 'data' in item:
                    screenshot_data = item['data']
            elif isinstance(result.screenshots, list) and len(result.screenshots) > 0:
                item = result.screenshots[0]
                if isinstance(item, dict) and 'data' in item:
                    screenshot_data = item['data']
            
            if screenshot_data:
                with open(f"{output_prefix}_screenshot.png", "wb") as f:
                    f.write(base64.b64decode(screenshot_data))
                print(f"Screenshot saved to {output_prefix}_screenshot.png")
            else:
                print("No screenshot data found")
        except Exception as e:
            print(f"Error saving screenshot: {e}")
    else:
        print("\nNo screenshots captured")
    
    return {
        "url": url,
        "success": success,
        "content_length": content_length,
        "has_media": hasattr(result, "media") and bool(result.media),
        "has_screenshot": (hasattr(result, "screenshot") and bool(result.screenshot)) or 
                         (hasattr(result, "screenshots") and bool(result.screenshots))
    }

async def test_altcoin_season_index():
    """Test crawling both altcoin season index pages and compare results"""
    # URLs to test
    urls = {
        "coinmarketcap": "https://coinmarketcap.com/charts/altcoin-season-index/",
        "blockchaincenter": "https://www.blockchaincenter.net/en/altcoin-season-index/"
    }
    
    # Create output directory
    output_dir = "altcoin_season_test"
    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)
    print(f"Output will be saved to {os.path.abspath(output_dir)}")
    
    # Initialize crawler
    crawler = AsyncWebCrawler(verbose=True)
    results = {}
    
    async with crawler as c:
        # Crawl each URL
        for name, url in urls.items():
            results[name] = await crawl_url(url, c, name)
    
    # Compare results
    print("\n" + "="*50)
    print("COMPARISON OF RESULTS")
    print("="*50)
    
    comparison_table = [
        ["Metric", "CoinMarketCap", "BlockchainCenter"],
        ["Success", results["coinmarketcap"]["success"], results["blockchaincenter"]["success"]],
        ["Content Length", results["coinmarketcap"]["content_length"], results["blockchaincenter"]["content_length"]],
        ["Has Media", results["coinmarketcap"]["has_media"], results["blockchaincenter"]["has_media"]],
        ["Has Screenshot", results["coinmarketcap"]["has_screenshot"], results["blockchaincenter"]["has_screenshot"]]
    ]
    
    # Print comparison table
    for row in comparison_table:
        print(f"{row[0]:<15} | {str(row[1]):<15} | {str(row[2]):<15}")

if __name__ == "__main__":
    asyncio.run(test_altcoin_season_index())