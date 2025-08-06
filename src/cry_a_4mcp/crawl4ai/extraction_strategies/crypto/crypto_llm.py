#!/usr/bin/env python3
"""
CryptoLLMExtractionStrategy extraction strategy for the cry_a_4mcp.crawl4ai package.

This module provides a specialized extraction strategy for CryptoLLMExtractionStrategy content,
with a detailed schema for extracting relevant information from CryptoLLMExtractionStrategy sources.
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
logger = logging.getLogger('crypto_extraction_strategy')

class CryptoLLMExtractionStrategy(LLMExtractionStrategy):
    """Specialized extraction strategy for CryptoLLMExtractionStrategy content.
    
        
       Specialized extraction strategy for cryptocurrency content.
    
    This strategy extends the base LLMExtractionStrategy with a specialized schema
    and instruction for extracting information from cryptocurrency news articles.
    """
    
    # Define the CryptoLLMExtractionStrategy-specific schema as a class attribute
    SCHEMA = {
        "type": "object",
        "properties": {
            "headline": {
                "type": "string",
                "description": "The main Headline or title of the Article"
            },
            "summary": {
                "type": "string",
                "description": "A concise summary of the article's main points"
            },
            "sentiment": {
                "type": "string",
                "enum": [
                    "very_negative",
                    "negative",
                    "neutral",
                    "positive",
                    "very_positive"
                ],
                "description": "The overall sentiment of the article towards cryptocurrency"
            },
            "category": {
                "type": "string",
                "enum": [
                    "market_analysis",
                    "regulation",
                    "technology",
                    "adoption",
                    "security",
                    "investment",
                    "defi",
                    "nft",
                    "mining",
                    "other"
                ],
                "description": "The primary category of the article"
            },
            "market_impact": {
                "type": "string",
                "description": "Analysis of potential market impact based on the article content"
            },
            "key_entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the entity (cryptocurrency, company, person, etc.)"
                        },
                        "type": {
                            "type": "string",
                            "enum": [
                                "cryptocurrency",
                                "token",
                                "company",
                                "person",
                                "organization",
                                "project",
                                "exchange",
                                "other"
                            ],
                            "description": "Type of entity"
                        },
                        "relevance": {
                            "type": "string",
                            "enum": [
                                "primary",
                                "secondary",
                                "mentioned"
                            ],
                            "description": "Relevance of the entity to the article"
                        }
                    },
                    "required": [
                        "name",
                        "type"
                    ]
                },
                "description": "Key entities mentioned in the article"
            },
            "persona_relevance": {
                "type": "object",
                "properties": {
                    "meme_snipers": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Relevance score for traders focused on meme coins and short-term gains (0-10)"
                    },
                    "gem_hunters": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Relevance score for investors looking for undervalued projects with potential (0-10)"
                    },
                    "legacy_investors": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Relevance score for traditional investors focused on established cryptocurrencies (0-10)"
                    }
                },
                "description": "Relevance scores for different investor personas"
            },
            "urgency_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
                "description": "How urgent or time-sensitive the information is (0-10)"
            }
        },
        "required": [
            "headline",
            "summary",
            "sentiment"
        ]
    }
    
    # Define the instruction for the LLM as a class attribute
    INSTRUCTION = """Extract key information from the provided cryptocurrency news article.
    Focus on identifying the main topic, sentiment, market impact, and key entities mentioned.
    Provide a concise summary and categorize the content appropriately.
    Evaluate the relevance of this information for different investor personas.
    Determine how urgent or time-sensitive the information is on a scale of 0-10."""
    
    def __init__(self, 
                 provider: str = "openai", 
                 api_token: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 extra_args: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3,
                 timeout: int = 60,
                 **kwargs):
        """Initialize the CryptoLLMExtractionStrategy extraction strategy.
        
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
        # Initialize the base class with the class-level schema and instruction
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