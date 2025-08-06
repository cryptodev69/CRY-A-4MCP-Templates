import asyncio
import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from cry_a_4mcp.config import Settings
from cry_a_4mcp.mcp_server.tools import CrawlWebsiteTool
from cry_a_4mcp.server import CRYA4MCPServer


async def test_mcp_server_integration():
    # Create settings
    settings = Settings()
    
    # Create the MCP server
    server = CRYA4MCPServer(settings)
    print("Created MCP server")
    
    # Initialize only the crawl_website tool
    tool_name = "crawl_website"
    if tool_name in server.tools:
        try:
            await server.tools[tool_name].initialize()
            print(f"Tool initialized: {tool_name}")
        except Exception as e:
            print(f"Tool initialization failed: {tool_name}, Error: {str(e)}")
            raise
    else:
        print(f"Tool '{tool_name}' not found")
        return
    
    print("Crawl website tool initialized")
    
    # Test the crawl_website tool through the MCP server
    tool_name = "crawl_website"
    arguments = {
        "url": "https://example.com/crypto-news",
        "content_type": "news",
        "extract_entities": True,
        "generate_triples": True
    }
    
    print(f"\nExecuting tool '{tool_name}' with arguments: {json.dumps(arguments, indent=2)}")
    
    # This simulates how the MCP server would handle a tool execution request
    if tool_name not in server.tools:
        print(f"Tool '{tool_name}' not found")
        return
        
    tool = server.tools[tool_name]
    
    result = await tool.execute(arguments)
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
    
    # Demonstrate how this data would be used in the MCP server workflow
    print("\nMCP Server Workflow:")
    print("1. Crawl website and extract cryptocurrency data")
    print("2. Update knowledge graph with extracted entities and relationships")
    print("3. Index markdown content in vector database for semantic search")
    print("4. Make data available for hybrid search and analysis tools")


if __name__ == "__main__":
    try:
        asyncio.run(test_mcp_server_integration())
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Note: This test requires the full MCP server implementation.")
        print("You can run the individual tool test instead: python test_crawl_website_tool.py")