"""
CRY-A-4MCP Server: Main MCP server implementation.

This module provides the main entry point for the CRY-A-4MCP server,
implementing the Model Context Protocol for cryptocurrency analysis tools.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)
from pydantic import BaseModel

from .config import Settings
from .mcp_server.tools import (
    CrawlWebsiteTool,
    HybridSearchTool,
    AnalyzeCryptoTool,
    UpdateKnowledgeGraphTool,
)
from .utils.logging import setup_logging


class CRYA4MCPServer:
    """
    Main CRY-A-4MCP server implementing the Model Context Protocol.
    
    This server provides cryptocurrency analysis capabilities through
    a hybrid approach combining RAG and Knowledge Graph reasoning.
    """
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the CRY-A-4MCP server."""
        self.settings = settings
        self.logger = structlog.get_logger(__name__)
        self.server = Server("cry-a-4mcp-server")
        
        # Initialize tools
        self.tools = {
            "crawl_website": CrawlWebsiteTool(settings),
            "hybrid_search": HybridSearchTool(settings),
            "analyze_crypto": AnalyzeCryptoTool(settings),
            "update_knowledge_graph": UpdateKnowledgeGraphTool(settings),
        }
        
        # Register MCP handlers
        self._register_handlers()
        
        self.logger.info(
            "CRY-A-4MCP server initialized",
            tools_count=len(self.tools),
            version=settings.version,
        )
    
    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools."""
            tools = []
            for tool_name, tool_instance in self.tools.items():
                tools.append(
                    Tool(
                        name=tool_name,
                        description=tool_instance.description,
                        inputSchema=tool_instance.input_schema,
                    )
                )
            
            self.logger.debug("Listed tools", tools_count=len(tools))
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            """Execute a tool call."""
            tool_name = request.name
            arguments = request.arguments or {}
            
            self.logger.info(
                "Tool call received",
                tool_name=tool_name,
                arguments_keys=list(arguments.keys()),
            )
            
            if tool_name not in self.tools:
                error_msg = f"Unknown tool: {tool_name}"
                self.logger.error(error_msg)
                return CallToolResult(
                    content=[TextContent(type="text", text=error_msg)],
                    isError=True,
                )
            
            try:
                tool_instance = self.tools[tool_name]
                result = await tool_instance.execute(arguments)
                
                self.logger.info(
                    "Tool call completed",
                    tool_name=tool_name,
                    success=True,
                )
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result)],
                    isError=False,
                )
                
            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                self.logger.error(
                    "Tool call failed",
                    tool_name=tool_name,
                    error=str(e),
                    exc_info=True,
                )
                
                return CallToolResult(
                    content=[TextContent(type="text", text=error_msg)],
                    isError=True,
                )
    
    async def run(self) -> None:
        """Run the MCP server."""
        self.logger.info("Starting CRY-A-4MCP server")
        
        # Initialize all tools
        for tool_name, tool_instance in self.tools.items():
            try:
                await tool_instance.initialize()
                self.logger.info("Tool initialized", tool_name=tool_name)
            except Exception as e:
                self.logger.error(
                    "Tool initialization failed",
                    tool_name=tool_name,
                    error=str(e),
                    exc_info=True,
                )
                raise
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main() -> None:
    """Main entry point for the CRY-A-4MCP server."""
    # Load configuration
    settings = Settings()
    
    # Setup logging
    setup_logging(settings.log_level)
    logger = structlog.get_logger(__name__)
    
    logger.info(
        "Starting CRY-A-4MCP server",
        version=settings.version,
        environment=settings.environment,
    )
    
    try:
        # Create and run server
        server = CRYA4MCPServer(settings)
        await server.run()
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error("Server failed", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

