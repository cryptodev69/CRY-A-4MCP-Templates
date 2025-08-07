#!/usr/bin/env python3
"""Test script for the updated CryptoCrawler with crawl4ai 0.7.0"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cry_a_4mcp.crypto_crawler.crawler import CryptoCrawler

async def test_crawler():
    """Test the crawler with a simple URL"""
    print("Testing CryptoCrawler with crawl4ai 0.7.0...")
    
    crawler = CryptoCrawler()
    
    try:
        # Initialize the crawler
        print("Initializing crawler...")
        await crawler.initialize()
        
        # Test with a simple URL
        test_url = "https://httpbin.org/html"
        print(f"Testing crawl with URL: {test_url}")
        
        try:
            result = await crawler.crawl_crypto_website(test_url, content_type="general")
        except Exception as e:
            print(f"Exception during crawl: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print(f"Crawl result:")
        # Handle custom CrawlResult object from CryptoCrawler
        if hasattr(result, 'metadata') and hasattr(result, 'markdown'):
            print(f"  Success: {result.metadata.success if result.metadata else False}")
            print(f"  URL: {result.metadata.url if result.metadata else 'N/A'}")
            print(f"  Content Type: {result.metadata.content_type if result.metadata else 'N/A'}")
            print(f"  Markdown Length: {len(result.markdown) if result.markdown else 0}")
            print(f"  Quality Score: {result.quality_score}")
            print(f"  Processing Time: {result.metadata.processing_time if result.metadata else 'N/A'}s")
            print(f"  Entities Found: {len(result.entities) if result.entities else 0}")
            print(f"  Triples Found: {len(result.triples) if result.triples else 0}")
            print(f"  Media Items: {len(result.media) if result.media else 0}")
            
            success = result.metadata.success if result.metadata else False
        else:
            # Fallback for other result types
            print(f"  Result type: {type(result)}")
            print(f"  Result: {result}")
            success = False
        
        if success:
            print("✅ Basic crawl test PASSED")
        else:
            print("❌ Basic crawl test FAILED")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        print("Closing crawler...")
        await crawler.close()
        print("Test completed.")

if __name__ == "__main__":
    asyncio.run(test_crawler())