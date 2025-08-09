#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the starter-mcp-server/src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'starter-mcp-server', 'src'))

from cry_a_4mcp.crypto_crawler.crawler import GenericAsyncCrawler

async def test_llm_metadata_fix():
    """Test that LLM metadata contains structured data instead of raw HTML."""
    print("Testing LLM metadata fix...")
    
    crawler = GenericAsyncCrawler()
    
    # Test with a simple schema
    schema = {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
            'summary': {'type': 'string'}
        },
        'required': ['title', 'summary']
    }
    
    instruction = 'Extract the title and summary from this webpage content.'
    
    try:
        result = await crawler.test_url_with_llm(
            url='https://example.com',
            instruction=instruction,
            schema=schema
        )
        
        print("\n=== LLM Test Result ===")
        print(f"Success: {result.get('success')}")
        print(f"URL: {result.get('url')}")
        
        # Check the data field (should contain structured data)
        data = result.get('data', {})
        print(f"\nData type: {type(data)}")
        print(f"Data content: {data}")
        
        # Check the metadata content field (should now contain structured data, not HTML)
        metadata = result.get('metadata', {})
        content = metadata.get('content')
        print(f"\nMetadata content type: {type(content)}")
        print(f"Metadata content: {content}")
        
        # Verify the fix worked
        if isinstance(content, dict):
            print("\n✅ SUCCESS: Metadata content is structured data (dict)")
        elif isinstance(content, str) and content.startswith('<'):
            print("\n❌ FAILED: Metadata content is still raw HTML")
        else:
            print(f"\n⚠️  UNKNOWN: Metadata content is {type(content)}: {content}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_metadata_fix())