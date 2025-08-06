#!/usr/bin/env python3
"""
Debug script to investigate crawler creation response.

This script will show the exact response from the crawler creation API
to understand why the 'id' field is missing.
"""

import asyncio
import aiohttp
import json
import sys


async def debug_crawler_creation():
    """Debug the crawler creation API response."""
    backend_url = "http://localhost:4001"
    
    async with aiohttp.ClientSession() as session:
        # First create a URL mapping
        print("1. Creating URL mapping...")
        mapping_data = {
            "name": "Debug Test Mapping",
            "description": "Debug mapping for testing",
            "urls": ["https://debug-test.com"],
            "extractor_ids": ["debug_extractor"],
            "priority": 1,
            "rate_limit": 2
        }
        
        async with session.post(
            f"{backend_url}/api/url-mappings",
            json=mapping_data
        ) as response:
            print(f"URL Mapping Response Status: {response.status}")
            mapping_response = await response.text()
            print(f"URL Mapping Response: {mapping_response}")
            
            if response.status == 200:
                try:
                    mapping_json = json.loads(mapping_response)
                    mapping_id = mapping_json.get("id")
                    print(f"URL Mapping ID: {mapping_id}")
                except json.JSONDecodeError as e:
                    print(f"Failed to parse URL mapping response as JSON: {e}")
                    return
            else:
                print("Failed to create URL mapping")
                return
        
        print("\n2. Creating crawler with URL mapping...")
        crawler_data = {
            "name": "Debug Test Crawler",
            "description": "Debug crawler with URL mapping",
            "crawler_type": "llm",
            "is_active": True,
            "urlMappingId": mapping_id,
            "targetUrls": ["https://debug-test.com/page1"],
            "config": {
                "timeout": 30,
                "retry_attempts": 3
            },
            "llm_config": {
                "model": "gpt-4",
                "temperature": 0.1
            }
        }
        
        print(f"Crawler Request Data: {json.dumps(crawler_data, indent=2)}")
        
        async with session.post(
            f"{backend_url}/api/crawlers",
            json=crawler_data
        ) as response:
            print(f"\nCrawler Response Status: {response.status}")
            print(f"Crawler Response Headers: {dict(response.headers)}")
            
            crawler_response = await response.text()
            print(f"Crawler Response Body: {crawler_response}")
            
            if response.status == 200:
                try:
                    crawler_json = json.loads(crawler_response)
                    print(f"\nParsed Crawler Response: {json.dumps(crawler_json, indent=2)}")
                    
                    # Check for specific fields
                    print(f"\nField Analysis:")
                    print(f"  - 'id' field: {crawler_json.get('id', 'MISSING')}")
                    print(f"  - 'url_mapping_id' field: {crawler_json.get('url_mapping_id', 'MISSING')}")
                    print(f"  - 'target_urls' field: {crawler_json.get('target_urls', 'MISSING')}")
                    print(f"  - 'url_mapping_ids' field: {crawler_json.get('url_mapping_ids', 'MISSING')}")
                    
                except json.JSONDecodeError as e:
                    print(f"Failed to parse crawler response as JSON: {e}")
            else:
                print(f"Crawler creation failed with status {response.status}")
                try:
                    error_json = json.loads(crawler_response)
                    print(f"Error details: {json.dumps(error_json, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Raw error response: {crawler_response}")
        
        # Cleanup
        print("\n3. Cleaning up...")
        if mapping_id:
            async with session.delete(f"{backend_url}/api/url-mappings/{mapping_id}") as response:
                print(f"URL mapping cleanup status: {response.status}")


async def main():
    """Main entry point."""
    print("🔍 Debugging Crawler Creation API")
    print("=================================\n")
    
    try:
        await debug_crawler_creation()
    except Exception as e:
        print(f"\n💥 Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())