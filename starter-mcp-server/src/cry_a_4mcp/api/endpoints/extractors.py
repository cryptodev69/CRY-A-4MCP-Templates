"""Extractors API endpoints for CRY-A-4MCP platform.

This module provides REST API endpoints for discovering and managing extraction strategies
within the CRY-A-4MCP (Crypto AI for Model Context Protocol) platform. It dynamically
scans the filesystem for extraction strategy implementations and exposes them through
a standardized API interface.

The module supports:
    - Dynamic discovery of extraction strategies from the filesystem
    - RESTful endpoints for listing and retrieving extractor configurations
    - Automatic parsing of strategy metadata (schema, instructions)
    - Error handling and logging for robust operation

Typical usage:
    GET /api/extractors - List all available extraction strategies
    GET /api/extractors/{id} - Get specific extractor configuration

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

import os
import re
import ast
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
import logging

from ..models import ExtractorResponse

# Initialize FastAPI router with prefix and tags for API organization
router = APIRouter(prefix="/extractors", tags=["Extractors"])

# Configure module-level logger for debugging and monitoring
logger = logging.getLogger(__name__)


def parse_python_dict_to_json(dict_str: str) -> str:
    """Parse Python dictionary syntax and convert to JSON format.
    
    Args:
        dict_str (str): String containing Python dictionary syntax
        
    Returns:
        str: JSON formatted string
    """
    try:
        # Remove outer braces if present and add them back
        dict_str = dict_str.strip()
        if not dict_str.startswith('{'):
            dict_str = '{' + dict_str + '}'
        
        # Parse the Python dictionary syntax
        parsed_dict = ast.literal_eval(dict_str)
        
        # Convert to JSON string
        return json.dumps(parsed_dict, indent=2)
    except (ValueError, SyntaxError) as e:
        # Use debug level instead of warning to reduce console noise
        logger.debug(f"Failed to parse dictionary string: {e} - Input: {dict_str[:100]}...")
        return dict_str  # Return original if parsing fails


def parse_python_dict_to_object(dict_str: str) -> dict:
    """Parse Python dictionary syntax and return as dictionary object.
    
    Args:
        dict_str (str): String containing Python dictionary syntax
        
    Returns:
        dict: Parsed dictionary object
    """
    try:
        # Remove outer braces if present and add them back
        dict_str = dict_str.strip()
        if not dict_str.startswith('{'):
            dict_str = '{' + dict_str + '}'
        
        # Parse the Python dictionary syntax
        parsed_dict = ast.literal_eval(dict_str)
        
        # Return the actual dictionary object
        return parsed_dict
    except (ValueError, SyntaxError) as e:
        # Use debug level instead of warning to reduce console noise
        logger.debug(f"Failed to parse dictionary string: {e} - Input: {dict_str[:100]}...")
        return {}  # Return empty dict if parsing fails


def discover_real_strategies() -> List[Dict[str, Any]]:
    """Dynamically discover extraction strategies from the filesystem.
    
    This function performs a comprehensive scan of the extraction strategies directory
    to identify and parse Python-based extraction strategy implementations. It uses
    regex pattern matching to extract class definitions and their associated metadata.
    
    The discovery process:
        1. Locates the extraction_strategies directory relative to this module
        2. Scans for Python files (excluding __init__.py and similar)
        3. Parses each file to extract class definitions
        4. Extracts schema and instructions metadata using regex patterns
        5. Constructs strategy dictionaries with standardized structure
    
    Returns:
        List[Dict[str, str]]: A list of strategy dictionaries, each containing:
            - name (str): The class name of the extraction strategy
            - file (str): The filename containing the strategy
            - schema (str): The extracted schema definition (if found)
            - instructions (str): The extracted instructions text (if found)
    
    Raises:
        No exceptions are raised directly. File reading errors are logged and
        the problematic files are skipped to ensure partial success.
    
    Example:
        >>> strategies = discover_real_strategies()
        >>> print(strategies[0])
        {
            'name': 'CryptoNewsExtractor',
            'file': 'crypto_news.py',
            'schema': 'title,content,timestamp',
            'instructions': 'Extract cryptocurrency news articles'
        }
    
    Note:
        This function assumes a specific directory structure and naming conventions.
        Strategy files must contain class definitions with optional schema and
        instructions attributes defined as string literals.
    """
    # Initialize empty list to collect discovered strategies
    strategies: List[Dict[str, Any]] = []
    
    # Construct path to extraction strategies directory
    # Navigate to the main project's extraction strategies location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up to starter-mcp-server, then to project root, then to the strategies
    project_root = os.path.join(current_dir, '..', '..', '..', '..', '..')
    strategies_dir = os.path.join(project_root, 'src', 'cry_a_4mcp', 'crawl4ai', 'extraction_strategies')
    
    # Validate that the strategies directory exists
    if not os.path.exists(strategies_dir):
        logger.warning(
            f"Strategies directory not found at: {strategies_dir}. "
            "No extraction strategies will be available."
        )
        return strategies
    
    logger.info(f"Scanning for extraction strategies in: {strategies_dir}")
    
    # Categories to scan for strategies
    categories = ["crypto", "news", "nft", "academic", "composite", "financial", "product", "social", "general", "workflow"]
    
    # Scan both root directory and category subdirectories
    directories_to_scan = [strategies_dir]  # Start with root directory
    
    # Add category subdirectories if they exist
    for category in categories:
        category_dir = os.path.join(strategies_dir, category)
        if os.path.exists(category_dir) and os.path.isdir(category_dir):
            directories_to_scan.append(category_dir)
            logger.debug(f"Added category directory: {category_dir}")
    
    # Iterate through all directories to scan
    for scan_dir in directories_to_scan:
        if not os.path.exists(scan_dir):
            continue
            
        logger.debug(f"Scanning directory: {scan_dir}")
        
        # Iterate through all files in the current directory
        for filename in os.listdir(scan_dir):
            # Filter for Python files, excluding special files like __init__.py
            if filename.endswith('.py') and not filename.startswith('__'):
                filepath = os.path.join(scan_dir, filename)
                
                try:
                    # Read the entire file content for parsing
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    logger.debug(f"Parsing strategy file: {filename}")
                    
                    # Extract class definitions using regex pattern matching
                    # Pattern matches: class ClassName(BaseClass): or class ClassName:
                    class_matches = re.findall(r'class\s+(\w+)\s*\([^)]*\):', content)
                    
                    # Process each discovered class as a potential extraction strategy
                    for class_name in class_matches:
                        logger.debug(f"Found strategy class: {class_name} in {filename}")
                        
                        # Filter out base classes, error classes, and other non-extractors
                        excluded_classes = {
                            'ExtractionStrategy',  # Base class
                            'LLMExtractionStrategy',  # Base class
                            'CompositeExtractionStrategy',  # Base class
                            'ExtractionError',  # Error class
                            'APIConnectionError',  # Error class
                            'APIResponseError',  # Error class
                            'ContentParsingError',  # Error class
                            'ComprehensiveLLMExtractionStrategy',  # Composite strategy without schema
                            'SequentialLLMExtractionStrategy'  # Composite strategy without schema
                        }
                        
                        if class_name in excluded_classes:
                            logger.debug(f"Skipping excluded class: {class_name}")
                            continue
                        
                        # Initialize metadata fields with empty defaults
                        schema = ""
                        instructions = ""
                        
                        # Extract schema definition using regex - look for complex schema objects
                        # First try to find schemas defined within __init__ methods
                        init_schema_match = re.search(
                            rf'def\s+__init__.*?(\w+_schema)\s*=\s*\{{(.+?)\}}', 
                            content, 
                            re.DOTALL
                        )
                        if init_schema_match:
                            raw_schema = f"{{{init_schema_match.group(2)}}}"
                            schema = parse_python_dict_to_object(raw_schema)
                            logger.debug(f"Extracted __init__ schema for {class_name}: {str(schema)[:100]}...")
                        else:
                            # Try to find class-level SCHEMA attribute with improved pattern
                            # This pattern handles nested dictionaries and arrays better
                            class_schema_match = re.search(
                                r'SCHEMA\s*=\s*\{([^{}]*(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}[^{}]*)*)\}', 
                                content, 
                                re.DOTALL
                            )
                            if not class_schema_match:
                                # Fallback to simpler pattern for deeply nested structures
                                schema_start = content.find('SCHEMA = {')
                                if schema_start != -1:
                                    # Find the matching closing brace
                                    brace_count = 0
                                    start_pos = schema_start + len('SCHEMA = ')
                                    end_pos = start_pos
                                    
                                    for i, char in enumerate(content[start_pos:], start_pos):
                                        if char == '{':
                                            brace_count += 1
                                        elif char == '}':
                                            brace_count -= 1
                                            if brace_count == 0:
                                                end_pos = i + 1
                                                break
                                    
                                    if brace_count == 0:
                                        raw_schema = content[start_pos:end_pos]
                                        schema = parse_python_dict_to_object(raw_schema)
                                        logger.debug(f"Extracted class-level SCHEMA for {class_name}: {str(schema)[:100]}...")
                            else:
                                raw_schema = f"{{{class_schema_match.group(1)}}}"
                                schema = parse_python_dict_to_object(raw_schema)
                                logger.debug(f"Extracted class-level SCHEMA for {class_name}: {str(schema)[:100]}...")
                            
                            if not schema:
                                # Fallback to module-level schema definitions
                                schema_match = re.search(
                                    r'(\w+_schema)\s*=\s*\{(.+?)\}', 
                                    content, 
                                    re.DOTALL
                                )
                                if schema_match:
                                    raw_schema = f"{{{schema_match.group(2)}}}"
                                    schema = parse_python_dict_to_object(raw_schema)
                                    logger.debug(f"Extracted module-level schema for {class_name}: {str(schema)[:100]}...")
                                else:
                                    # Final fallback to simple string schema
                                    simple_schema_match = re.search(
                                        r'schema\s*=\s*["\'](.+?)["\']', 
                                        content, 
                                        re.DOTALL
                                    )
                                    if simple_schema_match:
                                        schema = simple_schema_match.group(1).strip()
                        
                        # Only include strategies that have schemas (legitimate extractors)
                        if not schema:
                            logger.debug(f"Skipping {class_name} - no schema found")
                            continue
                        
                        # Extract instructions from class docstring
                        docstring_match = re.search(
                            rf'class\s+{re.escape(class_name)}\s*\([^)]*\):\s*"""(.+?)"""', 
                            content, 
                            re.DOTALL
                        )
                        if docstring_match:
                            instructions = docstring_match.group(1).strip()
                            logger.debug(f"Extracted instructions for {class_name}: {instructions[:100]}...")
                        
                        # Construct strategy dictionary with standardized structure
                        strategy = {
                            'name': class_name,
                            'file': filename,
                            'schema': schema,
                            'instructions': instructions
                        }
                        strategies.append(strategy)
                        
                        logger.info(f"Successfully registered strategy: {class_name}")
                        
                except Exception as e:
                    # Log file reading errors but continue processing other files
                    logger.error(
                        f"Failed to parse strategy file {filepath}: {e}. "
                        "This file will be skipped."
                    )
                    continue
    
    logger.info(f"Discovery complete. Found {len(strategies)} extraction strategies.")
    return strategies


@router.get("", response_model=List[ExtractorResponse])
async def get_extractors() -> List[ExtractorResponse]:
    """Retrieve all available extraction strategies from the platform.
    
    This endpoint performs a comprehensive discovery of all extraction strategies
    available in the CRY-A-4MCP platform. It scans the filesystem for strategy
    implementations and returns them in a standardized format suitable for
    client consumption.
    
    The endpoint:
        1. Invokes the discovery mechanism to scan for strategies
        2. Transforms raw strategy data into API response models
        3. Handles errors gracefully with appropriate HTTP status codes
        4. Provides comprehensive logging for monitoring and debugging
    
    Returns:
        List[ExtractorResponse]: A list of extractor configurations, each containing:
            - id (str): Unique identifier for the extraction strategy
            - name (str): Human-readable name of the strategy
            - description (str): Detailed description or instructions
            - schema (str): Data schema definition for the extractor
            - file_path (str): Source file containing the implementation
    
    Raises:
        HTTPException: 
            - 500 Internal Server Error: When strategy discovery fails
              due to filesystem issues, parsing errors, or other system problems
    
    Example Response:
        [
            {
                "id": "CryptoNewsExtractor",
                "name": "CryptoNewsExtractor",
                "description": "Extract cryptocurrency news articles with sentiment",
                "schema": "title,content,timestamp,sentiment",
                "file_path": "crypto_news.py"
            },
            {
                "id": "TradingSignalExtractor",
                "name": "TradingSignalExtractor",
                "description": "Extract trading signals from market data",
                "schema": "symbol,signal,confidence,timestamp",
                "file_path": "trading_signals.py"
            }
        ]
    
    HTTP Status Codes:
        200 OK: Successfully retrieved extractors list
        500 Internal Server Error: Strategy discovery failed
    
    Note:
        This endpoint is cached-friendly and can be called frequently.
        The discovery process is performed on each request to ensure
        real-time availability of newly added strategies.
    """
    try:
        logger.info("Processing request to retrieve all extraction strategies")
        
        # Discover all available strategies from the filesystem
        strategies = discover_real_strategies()
        logger.debug(f"Discovered {len(strategies)} strategies for API response")
        
        # Transform strategy dictionaries into API response models
        extractors: List[ExtractorResponse] = []
        
        for strategy in strategies:
            # Create standardized API response object for each strategy
            extractor = ExtractorResponse(
                id=strategy['name'],  # Use class name as unique identifier
                name=strategy['name'],  # Display name matches the class name
                description=strategy.get(
                    'instructions', 
                    f"Extraction strategy implemented in {strategy['file']}"
                ),  # Use instructions as description, with fallback
                schema=strategy.get('schema', ''),  # Include schema if available
                file_path=strategy['file']  # Reference to source implementation
            )
            extractors.append(extractor)
            
            logger.debug(f"Transformed strategy '{strategy['name']}' to API response")
        
        logger.info(f"Successfully returning {len(extractors)} extractors to client")
        return extractors
        
    except Exception as e:
        # Log the error with full context for debugging
        logger.error(
            f"Failed to retrieve extraction strategies: {e}", 
            exc_info=True
        )
        
        # Return standardized HTTP error response
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while discovering extractors: {str(e)}"
        )


@router.get("/{extractor_id}", response_model=ExtractorResponse)
async def get_extractor(extractor_id: str) -> ExtractorResponse:
    """Retrieve a specific extraction strategy by its unique identifier.
    
    This endpoint provides detailed information about a single extraction strategy
    identified by its unique ID. It performs a discovery operation and searches
    for the requested strategy, returning comprehensive configuration details.
    
    The endpoint:
        1. Validates the provided extractor ID parameter
        2. Discovers all available strategies from the filesystem
        3. Searches for the strategy matching the provided ID
        4. Returns detailed configuration if found
        5. Provides appropriate error responses for missing strategies
    
    Args:
        extractor_id (str): The unique identifier of the extraction strategy.
                           This should match the class name of the strategy
                           implementation. Case-sensitive.
    
    Returns:
        ExtractorResponse: Detailed configuration of the requested extractor:
            - id (str): Unique identifier matching the request parameter
            - name (str): Human-readable name of the strategy
            - description (str): Detailed description or instructions
            - schema (str): Data schema definition for the extractor
            - file_path (str): Source file containing the implementation
    
    Raises:
        HTTPException:
            - 404 Not Found: When the specified extractor ID does not exist
              in the available strategies collection
            - 500 Internal Server Error: When strategy discovery fails
              due to filesystem issues, parsing errors, or other system problems
    
    Example Request:
        GET /api/extractors/CryptoNewsExtractor
    
    Example Response:
        {
            "id": "CryptoNewsExtractor",
            "name": "CryptoNewsExtractor",
            "description": "Extract cryptocurrency news articles with sentiment analysis",
            "schema": "title,content,timestamp,sentiment,source",
            "file_path": "crypto_news.py"
        }
    
    HTTP Status Codes:
        200 OK: Successfully retrieved extractor details
        404 Not Found: Extractor with specified ID does not exist
        500 Internal Server Error: Strategy discovery or processing failed
    
    Note:
        The extractor_id parameter is case-sensitive and must exactly match
        the class name of the extraction strategy implementation. This endpoint
        performs real-time discovery to ensure up-to-date information.
    """
    try:
        logger.info(f"Processing request for specific extractor: {extractor_id}")
        
        # Validate input parameter
        if not extractor_id or not extractor_id.strip():
            logger.warning("Received empty or whitespace-only extractor_id")
            raise HTTPException(
                status_code=400, 
                detail="Extractor ID cannot be empty or whitespace"
            )
        
        # Discover all available strategies to search within
        strategies = discover_real_strategies()
        logger.debug(f"Searching for '{extractor_id}' among {len(strategies)} available strategies")
        
        # Search for the requested strategy by exact name match
        for strategy in strategies:
            if strategy['name'] == extractor_id:
                logger.info(f"Found matching strategy: {extractor_id}")
                
                # Construct and return the detailed response
                response = ExtractorResponse(
                    id=strategy['name'],  # Unique identifier
                    name=strategy['name'],  # Display name
                    description=strategy.get(
                        'instructions', 
                        f"Extraction strategy implemented in {strategy['file']}"
                    ),  # Detailed description with fallback
                    schema=strategy.get('schema', ''),  # Schema definition
                    file_path=strategy['file']  # Source file reference
                )
                
                logger.debug(f"Returning detailed configuration for: {extractor_id}")
                return response
        
        # Strategy not found - log and return 404
        logger.warning(
            f"Extractor '{extractor_id}' not found. Available strategies: "
            f"{[s['name'] for s in strategies]}"
        )
        raise HTTPException(
            status_code=404, 
            detail=f"Extractor '{extractor_id}' not found. "
                   f"Available extractors: {[s['name'] for s in strategies]}"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log unexpected errors with full context
        logger.error(
            f"Unexpected error while retrieving extractor '{extractor_id}': {e}", 
            exc_info=True
        )
        
        # Return standardized error response
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while retrieving extractor '{extractor_id}': {str(e)}"
        )