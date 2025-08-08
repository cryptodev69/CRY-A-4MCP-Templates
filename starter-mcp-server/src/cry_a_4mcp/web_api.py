"""Web API server for CRY-A-4MCP.

This module provides a FastAPI web server with REST endpoints
for the frontend to interact with the crawling system.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from crawl4ai.models import CrawlResult  # Commented out to avoid circular import
from .storage.url_configuration_db import URLConfigurationDatabase
from .storage.url_mappings_db import URLMappingsDatabase
from .storage.data_loader import load_predefined_urls
from .utils.logging import setup_logging
from .crypto_crawler.crawler import CryptoCrawler
from .api.router import create_api_router
# Model imports are now handled by the modular router

# Import GenericAsyncCrawler from the main src directory
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
from .crypto_crawler.crawler import GenericAsyncCrawler
from .crypto_crawler.extraction_strategies.ui.openrouter_utils import get_openrouter_models, format_openrouter_models

# Import strategy manager for extractors
import re
import json

def discover_real_strategies():
    """Discovers and loads real extraction strategies from the filesystem.

    It scans predefined categories within the 'extraction_strategies' directory,
    parses Python files to extract strategy class names, schemas, and instructions,
    and compiles them into a dictionary of available strategies.

    Returns:
        dict: A dictionary where keys are strategy class names and values are
              dictionaries containing strategy metadata (name, description, category,
              file_path, schema, instruction, default_provider, last_modified).
    """
    strategies = {}
    
    # Path to extraction strategies
    strategies_base = Path(__file__).parent.parent.parent.parent / "src" / "cry_a_4mcp" / "crawl4ai" / "extraction_strategies"
    
    # Categories to scan
    categories = ["crypto", "news", "nft", "academic", "composite", "financial", "product", "social", "general", "workflow"]
    
    for category in categories:
        category_dir = strategies_base / category
        if not category_dir.exists():
            continue
            
        # Scan Python files in category
        for py_file in category_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract class name
                class_match = re.search(r'class\s+(\w+)\s*\([^)]*LLMExtractionStrategy[^)]*\):', content)
                if not class_match:
                    continue
                    
                class_name = class_match.group(1)
                
                # Extract schema - try multiple patterns
                schema = {}
                
                # Pattern 1: Class attribute SCHEMA = {...}
                schema_start = re.search(r'SCHEMA\s*=\s*\{', content)
                if schema_start:
                    # Find the position of the opening brace
                    brace_pos = content.find('{', schema_start.start())
                    if brace_pos != -1:
                        start_pos = brace_pos
                        brace_count = 0
                        end_pos = start_pos
                        
                        # Find the matching closing brace
                        for i, char in enumerate(content[start_pos:], start_pos):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_pos = i + 1
                                    break
                        
                        if brace_count == 0:  # Found matching closing brace
                            try:
                                schema_str = content[start_pos:end_pos]
                                schema_str = re.sub(r'#.*?\n', '\n', schema_str)  # Remove comments
                                schema = eval(schema_str)
                            except Exception as e:
                                logging.warning(f"Failed to parse SCHEMA in {py_file}: {e}")
                                schema = {}
                        else:
                            logging.warning(f"Unclosed braces in SCHEMA in {py_file}")
                            schema = {}
                
                # Pattern 2: Local variable like cryptoinvestor_schema = {...}
                if not schema:
                    # Find schema variable assignment and extract the complete dict
                    schema_start = re.search(r'(\w*schema)\s*=\s*\{', content, re.IGNORECASE)
                    if schema_start:
                        logging.info(f"Found schema variable in {py_file}: {schema_start.group(1)}")
                        # Find the position of the opening brace
                        brace_pos = content.find('{', schema_start.start())
                        if brace_pos != -1:
                            start_pos = brace_pos
                            brace_count = 0
                            end_pos = start_pos
                            
                            # Find the matching closing brace
                            for i, char in enumerate(content[start_pos:], start_pos):
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end_pos = i + 1
                                        break
                            
                            if brace_count == 0:  # Found matching closing brace
                                try:
                                    schema_str = content[start_pos:end_pos]
                                    schema_str = re.sub(r'#.*?\n', '\n', schema_str)  # Remove comments
                                    schema = eval(schema_str)
                                    logging.info(f"Successfully parsed schema in {py_file}")
                                except Exception as e:
                                    logging.warning(f"Failed to parse schema variable in {py_file}: {e}")
                                    schema = {}
                            else:
                                logging.warning(f"Unclosed braces in schema variable in {py_file}")
                    else:
                        logging.info(f"No schema variable found in {py_file}")
                
                # Extract instruction - try multiple patterns
                instruction = ""
                
                # Pattern 1: Class attribute INSTRUCTION = "..."
                instruction_match = re.search(r'INSTRUCTION\s*=\s*["\'\'\'\'](.*?)["\'\'\'\'\']', content, re.DOTALL)
                if not instruction_match:
                    # Try simpler patterns
                    instruction_match = re.search(r'INSTRUCTION\s*=\s*"""(.*?)"""', content, re.DOTALL)
                    if not instruction_match:
                        instruction_match = re.search(r'INSTRUCTION\s*=\s*"(.*?)"', content, re.DOTALL)
                        if not instruction_match:
                            instruction_match = re.search(r'INSTRUCTION\s*=\s*\'(.*?)\'', content, re.DOTALL)
                
                if instruction_match:
                    instruction = instruction_match.group(1).strip()
                
                # Pattern 2: Local variable instruction = "..."
                if not instruction:
                    # Try triple-quoted strings first
                    instruction_match = re.search(r'instruction\s*=\s*"""(.*?)"""', content, re.DOTALL)
                    if instruction_match:
                        instruction = instruction_match.group(1).strip()
                        logging.info(f"Found triple-quoted instruction in {py_file}")
                    else:
                        # Try single-quoted triple strings
                        instruction_match = re.search(r"instruction\s*=\s*'''(.*?)'''", content, re.DOTALL)
                        if instruction_match:
                            instruction = instruction_match.group(1).strip()
                            logging.info(f"Found single-quoted triple instruction in {py_file}")
                        else:
                            # Try single/double quoted strings (non-multiline)
                            instruction_match = re.search(r'instruction\s*=\s*["\']([^"\']*)["\'\']', content)
                            if instruction_match:
                                instruction = instruction_match.group(1).strip()
                                logging.info(f"Found simple quoted instruction in {py_file}")
                            else:
                                logging.info(f"No instruction variable found in {py_file}")
                
                # Extract description from docstring
                description = f"Extraction strategy for {category} content"
                docstring_match = re.search(rf'class\s+{class_name}[^:]*:\s*"""([^"]*?)"""', content, re.DOTALL)
                if docstring_match:
                    description = docstring_match.group(1).strip()
                
                strategies[class_name] = {
                    'name': class_name,
                    'description': description,
                    'category': category,
                    'file_path': str(py_file.absolute()),
                    'schema': schema,
                    'instruction': instruction,
                    'default_provider': 'openai',
                    'last_modified': datetime.fromtimestamp(py_file.stat().st_mtime)
                }
                
            except Exception as e:
                logging.warning(f"Error reading strategy file {py_file}: {e}")
                continue
    
    return strategies

class NewStrategyManager:
    """Manages the discovery and retrieval of extraction strategies.

    This class acts as a wrapper around the `discover_real_strategies` function,
    providing a consistent interface for accessing available extraction strategies.
    """
    def discover_strategies(self, force_refresh=False):
        """Discovers and returns all available extraction strategies.

        Args:
            force_refresh (bool): If True, forces a re-discovery of strategies
                                  instead of returning cached results (if any).

        Returns:
            dict: A dictionary of discovered strategies.
        """
        return discover_real_strategies()

# Simple settings class since we're removing the config import
class Settings:
    """Simple settings class for application configuration.

    This class holds basic application settings, such as the logging level.
    """
    def __init__(self):
        """Initializes the Settings with default values."""
        self.log_level = "INFO"


# All Pydantic models are now defined in api/models.py


class WebAPIServer:
    """FastAPI web server for CRY-A-4MCP.

    This server provides REST endpoints for the frontend to interact with
    the crawling system, including URL configuration management, extractor
    discovery, OpenRouter model integration, and URL testing with LLMs.
    """

    def __init__(self, settings: Settings):
        """Initializes the WebAPIServer.

        Args:
            settings (Settings): Application settings, including log level.
        """
        self.settings = settings
        self.app = FastAPI(
            title="CRY-A-4MCP Web API",
            description="Web API for Crypto Data Crawler with LLM",
            version="1.0.0"
        )
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:5000", "http://localhost:5002"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize URL configuration database (business-focused)
        # Use absolute path to database file in starter-mcp-server directory
        db_base_path = Path(__file__).parent.parent.parent
        self.url_configuration_db = URLConfigurationDatabase(str(db_base_path / "url_configurations.db"))
        
        # Initialize URL mappings database (technical-focused)
        self.url_mappings_db = URLMappingsDatabase(str(db_base_path / "url_mappings.db"))
        
        # Initialize crawler database
        from .storage.crawler_db import CrawlerDatabase
        self.crawler_db = CrawlerDatabase()
        
        # Initialize crawler
        self.crawler = None
        
        # Initialize strategy manager for extractors
        self.strategy_manager = None
        
        # Store for active crawl jobs (in production, use Redis or similar)
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        
        # Setup routes
        self._setup_routes()
        
        # Add startup event to initialize databases
        @self.app.on_event("startup")
        async def startup_event():
            await self.initialize()
    

    

    
    def _setup_routes(self):
        """Sets up all API routes for the FastAPI application.

        This method integrates the modular API router and sets up basic health check.
        """
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "cry-a-4mcp-web-api"}
        
        # Add direct endpoints for frontend compatibility (without /api prefix)
        @self.app.get("/url-configurations/")
        async def get_url_configurations():
            """Get all URL configurations for frontend compatibility."""
            try:
                configs = await self.url_configuration_db.get_all_configurations()
                return configs
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve URL configurations: {str(e)}")
        
        @self.app.get("/url-mappings/")
        async def get_url_mappings():
            """Get all URL mappings for frontend compatibility."""
            try:
                mappings = await self.url_mappings_db.get_all_mappings()
                return mappings
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve URL mappings: {str(e)}")
        
        # Store router setup for later initialization
        self._api_router_setup_pending = True
        
        # All API endpoints will be handled by the modular router after initialization
    
    async def initialize(self):
        """Initializes the web API server's components.

        This includes initializing the URL configuration database and loading
        predefined URLs if the database is empty.
        """
        # Initialize databases
        await self.url_configuration_db.initialize()
        await self.url_mappings_db.initialize()
        await self.crawler_db.initialize()
        
        # Load predefined URLs if database is empty
        configs = await self.url_configuration_db.get_all_configurations()
        if not configs:
            await load_predefined_urls(self.url_configuration_db)
            logging.info("Loaded predefined URL configurations")
        
        # Seed databases with sample data if empty
        try:
            await self.crawler_db.seed_sample_data()
            logging.info("Seeded databases with sample data")
        except Exception as e:
            logging.warning(f"Failed to seed sample data: {e}")
        
        # Setup API router after database initialization
        if hasattr(self, '_api_router_setup_pending') and self._api_router_setup_pending:
            api_router = await create_api_router(
                url_configuration_db=self.url_configuration_db,
                url_mappings_db=self.url_mappings_db,
                crawler_db=self.crawler_db,
                active_jobs=self.active_jobs
            )
            self.app.include_router(api_router)
            self._api_router_setup_pending = False
            logging.info("API router with adaptive crawling capabilities initialized")
    
    async def run(self, host: str = "0.0.0.0", port: int = 4000):
        """Runs the FastAPI web server using Uvicorn.

        Args:
            host (str): The host address to bind the server to.
            port (int): The port number to listen on.
        """
        await self.initialize()
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


async def main():
    """Main entry point for the web API server.

    Initializes settings, sets up logging (currently commented out), and starts
    the WebAPIServer.
    """
    settings = Settings()
    # setup_logging(settings.log_level)  # Comment out for now to avoid import issues
    
    server = WebAPIServer(settings)
    await server.run(host="0.0.0.0", port=4000)


# Create app instance for uvicorn
def create_app():
    """Create FastAPI app instance for uvicorn."""
    settings = Settings()
    server = WebAPIServer(settings)
    return server.app

app = create_app()

if __name__ == "__main__":
    asyncio.run(main())