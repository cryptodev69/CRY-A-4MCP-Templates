import asyncio
import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from cry_a_4mcp.config import Settings
from cry_a_4mcp.mcp_server.tools import CrawlWebsiteTool


async def test_crawl_website_tool():
    # Create settings
    settings = Settings()
    
    # Create the tool
    tool = CrawlWebsiteTool(settings)
    print(f"Created tool: {tool.name}")
    print(f"Description: {tool.description}")
    
    # Initialize the tool
    await tool.initialize()
    print("Tool initialized")
    
    # Test execution
    arguments = {
        "url": "https://example.com/crypto-news",
        "content_type": "news",
        "extract_entities": True,
        "generate_triples": True
    }
    
    print(f"\nExecuting tool with arguments: {json.dumps(arguments, indent=2)}")
    result = await tool.execute(arguments)
    
    # Parse the result
    result_dict = json.loads(result)
    
    print("\nExecution Result:")
    print(f"Success: {result_dict['success']}")
    print(f"URL: {result_dict['url']}")
    print(f"Content Type: {result_dict['content_type']}")
    print(f"Quality Score: {result_dict['quality_score']}")
    
    print("\nExtracted Entities:")
    for entity in result_dict['entities']:
        print(f"  - {entity['name']} ({entity['entity_type']}): {entity['confidence']}")
    
    print("\nExtracted Triples:")
    for triple in result_dict['triples']:
        print(f"  - {triple['subject']} {triple['predicate']} {triple['object']}: {triple['confidence']}")
    
    print("\nMarkdown Content:")
    print(result_dict['markdown'])


if __name__ == "__main__":
    asyncio.run(test_crawl_website_tool())