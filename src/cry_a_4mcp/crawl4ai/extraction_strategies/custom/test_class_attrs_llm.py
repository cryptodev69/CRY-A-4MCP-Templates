#!/usr/bin/env python3
"""
Test extraction strategy for the cry_a_4mcp.crawl4ai package.

This module provides a specialized extraction strategy for Test content,
with a detailed schema for extracting relevant information from Test sources.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from ..base import LLMExtractionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_extraction_strategy')

class TestLLMExtractionStrategy(LLMExtractionStrategy):
    """Specialized extraction strategy for Test content.
    
    A test strategy with class attributes for SCHEMA and INSTRUCTION.
    """
    
    # Define the Test-specific schema as a class attribute
    SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "The title or headline of the content"
        },
        "summary": {
            "type": "string",
            "description": "A brief summary of the content"
        },
        "key_points": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of key points from the content"
        }
    },
    "required": ["title", "summary"]
}
    
    # Define the instruction for the LLM as a class attribute
    INSTRUCTION = """Extract the title, summary, and key points from the provided content.
The title should be the main headline or title of the content.
The summary should be a concise overview of the main points.
The key points should be a list of the most important information from the content.
"""
    
    def __init__(self, 
                 provider: str = "openai", 
                 api_token: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 extra_args: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3,
                 timeout: int = 60,
                 **kwargs):
        """Initialize the Test extraction strategy.
        
        Args:
            provider: LLM provider (e.g., "openai", "groq", "openrouter")
            api_token: API token for the LLM provider
            base_url: Optional base URL for the API
            model: Model to use for extraction
            extra_args: Additional arguments to pass to the API
            max_retries: Maximum number of retries for API calls
            timeout: Timeout for API calls in seconds
            **kwargs: Additional configuration options
        """
        # Initialize the base class with the schema and instruction
        super().__init__(
            provider=provider,
            api_token=api_token,
            instruction=self.INSTRUCTION,
            schema=self.SCHEMA,
            base_url=base_url,
            model=model,
            extra_args=extra_args,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs
        )