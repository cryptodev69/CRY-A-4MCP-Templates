#!/usr/bin/env python3
# pyright: ignore
# type: ignore
# basedpyright: ignore
# This is a template file and not valid Python syntax
# It contains template variables that will be replaced by the template generator
# The following line ensures this file is not treated as Python code by linters
# pyright: strict-optional=false
"""
NewsLLMExtractionStrategy extraction strategy for the cry_a_4mcp.crawl4ai package.

This module provides a specialized extraction strategy for NewsLLMExtractionStrategy content,
with a detailed schema for extracting relevant information from NewsLLMExtractionStrategy sources.
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
logger = logging.getLogger('news_extraction_strategy')

# type: ignore
class NewsLLMExtractionStrategy(LLMExtractionStrategy):
    """Specialized extraction strategy for NewsLLMExtractionStrategy content.
    
    Specialized extraction strategy for NewsLLMExtractionStrategy content.
    
    Extraction strategy for news content
    """
    
    # Define the NewsLLMExtractionStrategy-specific schema as a class attribute
    SCHEMA = {
        "type": "object",
        "properties": {
            "headline": {
                "type": "string",
                "description": "The main headline or title of the news Article"
            },
            "summary": {
                "type": "string",
                "description": "A concise summary of the news article (2-3 sentences)"
            },
            "key_points": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of key points or takeaways from the article"
            },
            "sources": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "role": {
                            "type": "string"
                        },
                        "organization": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "name"
                    ]
                },
                "description": "Sources cited in the article"
            },
            "quotes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string"
                        },
                        "source": {
                            "type": "string"
                        },
                        "context": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "text"
                    ]
                },
                "description": "Notable quotes from the article"
            },
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "type": {
                            "type": "string"
                        },
                        "relevance": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1
                        }
                    },
                    "required": [
                        "name",
                        "type"
                    ]
                },
                "description": "Entities mentioned in the article (people, organizations, locations, etc.)"
            },
            "sentiment": {
                "type": "string",
                "enum": [
                    "positive",
                    "negative",
                    "neutral",
                    "mixed"
                ],
                "description": "Overall sentiment of the article"
            },
            "topics": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Main topics covered in the article"
            },
            "publication_date": {
                "type": "string",
                "format": "date-time",
                "description": "Publication date of the article if mentioned"
            },
            "factual_claims": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Factual claims made in the article"
            },
            "bias_assessment": {
                "type": "string",
                "enum": [
                    "left",
                    "center-left",
                    "center",
                    "center-right",
                    "right",
                    "unbiased",
                    "unknown"
                ],
                "description": "Assessment of potential bias in the article"
            },
            "urgency_level": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Urgency level of the news (1-10)"
            }
        },
        "required": [
            "headline",
            "summary",
            "key_points",
            "sentiment"
        ]
    }
    
    # Define the instruction for the LLM as a class attribute
    INSTRUCTION = """1. Be Precise"""
    
    # type: ignore
    def __init__(self, 
                 provider: str = "openai", 
                 api_token: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 extra_args: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3,
                 timeout: int = 60,
                 **kwargs):
        """Initialize the NewsLLMExtractionStrategy extraction strategy.
        
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
        # Initialize the base class with the schema and instruction class attributes
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