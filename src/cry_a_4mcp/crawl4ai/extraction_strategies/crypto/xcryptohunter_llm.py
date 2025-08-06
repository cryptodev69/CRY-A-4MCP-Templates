#!/usr/bin/env python3
"""XCryptoHunterLLMExtractionStrategy extraction strategy for the cry_a_4mcp.crawl4ai package.

This module provides a specialized extraction strategy for cryptocurrency gem hunting content,
with a detailed schema for extracting relevant information from crypto hunter sources.
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
logger = logging.getLogger('xcryptohunter_extraction_strategy')

class XCryptoHunterLLMExtractionStrategy(LLMExtractionStrategy):
    """Specialized extraction strategy for cryptocurrency content focused on crypto hunters.
    
    This strategy is designed to extract structured information from content related to
    cryptocurrency gem hunting, including token details, market analysis, and social signals.
    
    Extraction strategy for crypto content
    """
    
    # Define the schema for XCryptoHunter extraction as a class attribute
    SCHEMA = {
        "type": "object",
        "properties": {
            "tweet_metadata": {
                "type": "object",
                "properties": {
                    "tweet_id": {
                        "type": "string",
                        "description": "Unique Twitter tweet ID"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Tweet creation timestamp in ISO format"
                    },
                    "author_handle": {
                        "type": "string",
                        "description": "Twitter handle of the tweet author"
                    },
                    "follower_count": {
                        "type": "integer",
                        "description": "Number of followers the author has"
                    },
                    "engagement_metrics": {
                        "type": "object",
                        "properties": {
                            "likes": {
                                "type": "integer"
                            },
                            "retweets": {
                                "type": "integer"
                            },
                            "replies": {
                                "type": "integer"
                            }
                        }
                    }
                }
            },
            "crypto_tokens": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "token_name": {
                            "type": "string",
                            "description": "Name of the cryptocurrency token"
                        },
                        "token_symbol": {
                            "type": "string",
                            "description": "Symbol of the cryptocurrency token"
                        }
                    }
                }
            },
            "extraction_metadata": {
                "type": "object",
                "properties": {
                    "extraction_timestamp": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "confidence_level": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "processing_notes": {
                        "type": "string"
                    },
                    "gem_hunter_score": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 10
                    }
                }
            }
        }
    }
    
    # Define the instruction for XCryptoHunter extraction as a class attribute
    INSTRUCTION = """
    Extract structured information from the provided cryptocurrency content, focusing on gem hunting signals.
    Identify any mentioned cryptocurrency tokens, including their names and symbols.
    Extract metadata about the tweet including ID, creation time, author, and engagement metrics.
    Provide extraction metadata including confidence level and a gem hunter score (0-10) indicating how valuable this information is for crypto gem hunters.
    Ensure the extraction is objective and based solely on the content provided.
    Do not include information not present in the content.
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
        """Initialize the XcryptohunterLLMExtractionStrategy extraction strategy.
        
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
        # The schema and instruction are now defined as class attributes (SCHEMA and INSTRUCTION)
        
        # Define the instruction for the LLM (using the class attribute INSTRUCTION)
        instruction = self.INSTRUCTION
                
            
                
        # Initialize the base class with the class attributes for schema and instruction
        super().__init__(
            provider=provider,
            api_token=api_token,
            instruction=instruction,
            schema=self.SCHEMA,
            base_url=base_url,
            model=model,
            extra_args=extra_args,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs
            )

                                           
