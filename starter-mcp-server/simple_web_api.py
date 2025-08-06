#!/usr/bin/env python3
"""
Simple standalone web API for testing the extractors endpoint.
This bypasses the complex dependencies and focuses on the extractors functionality.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
import uvicorn
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import API router and database
try:
    from cry_a_4mcp.api.router import create_api_router
    API_ROUTER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Could not import API router: {e}")
    API_ROUTER_AVAILABLE = False

# Import strategy discovery utilities
try:
    import importlib.util
    import inspect
    from pathlib import Path
    import re
    import ast
    
    def discover_real_strategies():
        """Discover real strategies from the extraction_strategies directory."""
        strategies = {}
        strategies_path = Path(__file__).parent.parent / "src" / "cry_a_4mcp" / "crawl4ai" / "extraction_strategies"
        
        if not strategies_path.exists():
            return {}
        
        # Scan category directories
        for category_dir in strategies_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('_') and category_dir.name != 'ui':
                # Scan Python files in category
                for py_file in category_dir.glob('*.py'):
                    if py_file.name.startswith('_'):
                        continue
                    
                    try:
                        # Read file content
                        content = py_file.read_text()
                        
                        # Extract class name
                        class_match = re.search(r'class\s+(\w+)\s*\([^)]*LLMExtractionStrategy[^)]*\):', content)
                        if not class_match:
                            continue
                        
                        class_name = class_match.group(1)
                        
                        # Extract schema using bracket counting for proper nesting
                        schema = {}
                        
                        def extract_balanced_dict(text, start_pattern):
                            """Extract a balanced dictionary from text starting with the pattern."""
                            match = re.search(start_pattern, text)
                            if not match:
                                return None
                            
                            # Find the opening brace after the match
                            search_start = match.end()
                            brace_pos = -1
                            
                            # Look for the opening brace, allowing for whitespace and newlines
                            for i in range(search_start, min(search_start + 50, len(text))):
                                if text[i] == '{':
                                    brace_pos = i
                                    break
                                elif text[i] not in ' \t\n\r':
                                    # Found non-whitespace that's not a brace
                                    break
                            
                            if brace_pos == -1:
                                return None
                            
                            # Count braces to find the matching closing brace
                            brace_count = 0
                            i = brace_pos
                            while i < len(text):
                                if text[i] == '{':
                                    brace_count += 1
                                elif text[i] == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        return text[brace_pos:i+1]
                                i += 1
                            return None
                        
                        # Try class attribute SCHEMA first
                        schema_str = extract_balanced_dict(content, r'SCHEMA\s*=\s*')
                        
                        if not schema_str:
                            # Try local variable pattern (e.g., cryptoinvestor_schema)
                            schema_str = extract_balanced_dict(content, r'\w*_?schema\s*=\s*')
                        
                        if schema_str:
                            try:
                                # Clean up the schema string and evaluate it
                                schema = ast.literal_eval(schema_str)
                            except Exception as e:
                                print(f"Error parsing schema in {py_file}: {e}")
                                schema = {}
                        
                        # Extract instruction - try both class attribute and local variable patterns
                        instruction = ""
                        # Try class attribute INSTRUCTION first - handle multi-line strings
                        instruction_match = re.search(r'INSTRUCTION\s*=\s*"""([^"]*(?:"(?!"")[^"]*)*?)"""', content, re.DOTALL)
                        if not instruction_match:
                            # Try single/double quotes
                            instruction_match = re.search(r'INSTRUCTION\s*=\s*["\']([^"\']*)["\'\']', content, re.DOTALL)
                        
                        if not instruction_match:
                            # Try local variable pattern (e.g., instruction = "...")
                            instruction_match = re.search(r'instruction\s*=\s*"""([^"]*(?:"(?!"")[^"]*)*?)"""', content, re.DOTALL)
                            if not instruction_match:
                                instruction_match = re.search(r'instruction\s*=\s*["\']([^"\']*)["\'\']', content, re.DOTALL)
                        
                        if instruction_match:
                            instruction = instruction_match.group(1).strip()
                        else:
                            # Fallback: try to find any multi-line string that looks like an instruction
                            fallback_match = re.search(r'"""([^"]*(?:extract|analyze|identify)[^"]*?)"""', content, re.DOTALL | re.IGNORECASE)
                            if fallback_match:
                                instruction = fallback_match.group(1).strip()
                        
                        # Extract description from docstring
                        docstring_match = re.search(r'class\s+' + class_name + r'[^:]*:\s*["\'\'\'\'](.*?)["\'\'\'\'\']', content, re.DOTALL)
                        description = docstring_match.group(1).strip() if docstring_match else f"Extraction strategy for {category_dir.name}"
                        
                        strategies[class_name] = {
                            'name': class_name,
                            'description': description,
                            'category': category_dir.name,
                            'schema': schema,
                            'instruction': instruction,
                            'default_provider': 'openai',
                            'last_modified': datetime.fromtimestamp(py_file.stat().st_mtime)
                        }
                        
                    except Exception as e:
                        print(f"Error processing {py_file}: {e}")
                        continue
        
        return strategies
    
    NewStrategyManager = None
except ImportError as e:
    print(f"Warning: Could not import strategy discovery utilities: {e}")
    NewStrategyManager = None
    discover_real_strategies = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class ExtractorResponse(BaseModel):
    """Response model for extraction strategies."""
    id: str
    name: str
    version: str
    description: str
    author: str
    category: str
    isActive: bool
    tags: List[str]
    usageCount: int
    successRate: float
    updatedAt: str
    config: Dict[str, Any]

class CrawlerConfig(BaseModel):
    """Crawler configuration model."""
    id: Optional[str] = None
    name: str
    description: str
    crawler_type: str  # 'basic', 'llm', 'composite'
    is_active: bool = True
    url_mappings: List[str] = []  # References to URL mapping IDs
    target_urls: List[str] = []
    config: Dict[str, Any] = {}
    llm_config: Optional[Dict[str, Any]] = None
    extraction_strategies: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class URLMappingConfig(BaseModel):
    """URL mapping configuration model."""
    id: Optional[str] = None
    name: str
    description: str
    urls: List[str]
    extractor_ids: List[str]
    crawler_settings: Dict[str, Any] = {}
    priority: int = 1
    rate_limit: Optional[int] = None
    validation_rules: Dict[str, Any] = {}
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class CrawlJob(BaseModel):
    """Crawl job model."""
    id: Optional[str] = None
    name: str
    crawler_id: str
    status: str = 'pending'  # 'pending', 'running', 'completed', 'failed'
    schedule: Optional[str] = None  # Cron expression
    target_urls: List[str]
    results: Optional[Dict[str, Any]] = None
    logs: List[str] = []
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class CreateCrawlerRequest(BaseModel):
    """Request model for creating a crawler."""
    name: str
    description: str
    crawler_type: str
    url_mapping_id: Optional[str] = None
    target_urls: List[str] = []
    config: Dict[str, Any] = {}
    llm_config: Optional[Dict[str, Any]] = None
    extraction_strategies: List[str] = []

class UpdateCrawlerRequest(BaseModel):
    """Request model for updating a crawler."""
    name: Optional[str] = None
    description: Optional[str] = None
    crawler_type: Optional[str] = None
    is_active: Optional[bool] = None
    url_mappings: Optional[List[str]] = None
    target_urls: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    llm_config: Optional[Dict[str, Any]] = None
    extraction_strategies: Optional[List[str]] = None

# Mock strategy manager
class MockNewStrategyManager:
    """Mock strategy manager for testing purposes."""
    
    def discover_strategies(self, force_refresh=False):
        """Return mock strategies for testing."""
        return {
            "CryptoNewsExtractor": {
                "name": "CryptoNewsExtractor",
                "description": "Extracts cryptocurrency news articles with title, content, and metadata",
                "category": "crypto",
                "schema": {
                    "title": "string",
                    "content": "string",
                    "author": "string",
                    "publish_date": "string",
                    "tags": "array"
                },
                "instruction": "Extract the main title, full article content, author name, publication date, and relevant tags from cryptocurrency news articles.",
                "default_provider": "openai",
                "last_modified": datetime.now()
            },
            "DeFiProtocolExtractor": {
                "name": "DeFiProtocolExtractor",
                "description": "Extracts DeFi protocol information including TVL, APY, and token details",
                "category": "financial",
                "schema": {
                    "protocol_name": "string",
                    "tvl": "number",
                    "apy": "number",
                    "token_symbol": "string",
                    "blockchain": "string"
                },
                "instruction": "Extract DeFi protocol details including total value locked (TVL), annual percentage yield (APY), token information, and blockchain network.",
                "default_provider": "openai",
                "last_modified": datetime.now()
            },
            "NFTMarketplaceExtractor": {
                "name": "NFTMarketplaceExtractor",
                "description": "Extracts NFT marketplace data including collection stats and trading volumes",
                "category": "nft",
                "schema": {
                    "collection_name": "string",
                    "floor_price": "number",
                    "volume_24h": "number",
                    "total_supply": "number",
                    "marketplace": "string"
                },
                "instruction": "Extract NFT collection details including floor price, trading volume, total supply, and marketplace information.",
                "default_provider": "openai",
                "last_modified": datetime.now()
            }
        }

# Create FastAPI app
app = FastAPI(
    title="CRY-A-4MCP Simple Web API",
    description="Simple web API for testing extractors endpoint",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize strategy manager
strategy_manager = MockNewStrategyManager()

# Initialize API router if available
if API_ROUTER_AVAILABLE:
    try:
        # Note: API router functionality is limited without database
        logger.info("API router available but database not configured")
    except Exception as e:
        logger.error(f"Error setting up API router: {e}")
else:
    logger.warning("API router not available, running with limited functionality")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "CRY-A-4MCP Simple Web API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/extractors", response_model=List[ExtractorResponse])
async def get_extractors():
    """Get all available extraction strategies."""
    try:
        logger.info("Fetching extraction strategies...")
        
        # Use real strategy discovery if available, fallback to mock
        if discover_real_strategies:
            strategies = discover_real_strategies()
            logger.info(f"Discovered {len(strategies)} real strategies")
        else:
            strategies = strategy_manager.discover_strategies(force_refresh=True)
            logger.info(f"Using {len(strategies)} mock strategies")
        
        # Convert strategies to ExtractorResponse format
        extractors = []
        for name, strategy in strategies.items():
            # Format last_modified as string if it's a datetime object
            last_modified = strategy.get('last_modified', datetime.now())
            if hasattr(last_modified, 'isoformat'):
                last_modified = last_modified.isoformat()
            
            extractor = ExtractorResponse(
                id=name.lower().replace(' ', '_'),
                name=name,
                version="1.0.0",
                description=strategy.get('description', ''),
                author="CRY-A-4MCP Team",
                category=strategy.get('category', 'general'),
                isActive=True,
                tags=[strategy.get('category', 'general'), strategy.get('default_provider', 'openai')],
                usageCount=0,
                successRate=95.0,
                updatedAt=last_modified,
                config={
                    'schema': strategy.get('schema', {}),
                    'instruction': strategy.get('instruction', ''),
                    'default_provider': strategy.get('default_provider', 'openai')
                }
            )
            extractors.append(extractor)
        
        logger.info(f"Successfully fetched {len(extractors)} extractors")
        return extractors
        
    except Exception as e:
        logger.error(f"Error getting extractors: {e}")
