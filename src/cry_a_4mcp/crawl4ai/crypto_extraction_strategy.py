#!/usr/bin/env python3
"""
Cryptocurrency-specific extraction strategy implementation.

This module provides a specialized extraction strategy for cryptocurrency content
with enhanced error handling, performance optimization, and model flexibility.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from .extraction_strategies.base import LLMExtractionStrategy
from .extraction_strategy_improved import measure_performance

# Configure logging
logger = logging.getLogger('crypto_extraction')

class CryptoLLMExtractionStrategy(LLMExtractionStrategy):
    """Cryptocurrency-specific LLM extraction strategy.
    
    This class extends the enhanced LLMExtractionStrategy with cryptocurrency-specific
    schema and instructions.
    """
    
    def __init__(self, 
                 provider: str, 
                 api_token: str, 
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 max_retries: int = 3,
                 timeout: int = 60,
                 **kwargs):
        """Initialize the cryptocurrency LLM extraction strategy.
        
        Args:
            provider: LLM provider (e.g., "openai", "groq", "openrouter")
            api_token: API token for the LLM provider
            base_url: Optional base URL for the API
            model: Model to use for extraction
            max_retries: Maximum number of retries for API calls
            timeout: Timeout for API calls in seconds
            **kwargs: Additional configuration options
        """
        # Define the schema for cryptocurrency content extraction
        schema = {
            "type": "object",
            "properties": {
                "headline": {"type": "string", "description": "The main headline or title of the content"},
                "summary": {"type": "string", "description": "A concise summary of the content"},
                "sentiment": {
                    "type": "string", 
                    "enum": ["bullish", "bearish", "neutral"],
                    "description": "The overall market sentiment expressed in the content"
                },
                "category": {
                    "type": "string", 
                    "enum": ["breaking", "analysis", "regulatory", "institutional", "technical", "defi", "nft", "meme"],
                    "description": "The primary category of the content"
                },
                "market_impact": {
                    "type": "string", 
                    "enum": ["high", "medium", "low", "none"],
                    "description": "The potential impact on the market"
                },
                "key_entities": {
                    "type": "array",
                    "description": "Important entities mentioned in the content",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the entity"},
                            "type": {
                                "type": "string", 
                                "enum": ["token", "exchange", "protocol", "person", "company", "regulator"],
                                "description": "Type of entity"
                            },
                            "relevance": {
                                "type": "number", 
                                "minimum": 0, 
                                "maximum": 1,
                                "description": "Relevance score from 0 to 1"
                            }
                        },
                        "required": ["name", "type"]
                    }
                },
                "persona_relevance": {
                    "type": "object",
                    "description": "Relevance scores for different investor personas",
                    "properties": {
                        "meme_snipers": {"type": "number", "minimum": 0, "maximum": 1, "description": "Relevance for meme coin traders"},
                        "gem_hunters": {"type": "number", "minimum": 0, "maximum": 1, "description": "Relevance for early-stage project investors"},
                        "legacy_investors": {"type": "number", "minimum": 0, "maximum": 1, "description": "Relevance for traditional crypto investors"}
                    }
                },
                "urgency_score": {
                    "type": "number", 
                    "minimum": 0, 
                    "maximum": 10,
                    "description": "How time-sensitive the information is (0-10)"
                },
                "price_mentions": {
                    "type": "array",
                    "description": "Specific price information mentioned in the content",
                    "items": {
                        "type": "object",
                        "properties": {
                            "token": {"type": "string", "description": "Token symbol or name"},
                            "price": {"type": "string", "description": "Price mentioned"},
                            "change": {"type": "string", "description": "Price change mentioned (if any)"}
                        },
                        "required": ["token"]
                    }
                }
            },
            "required": ["headline", "summary", "sentiment"]
        }
        
        # Define the instruction for cryptocurrency content extraction
        instruction = """
        Analyze this cryptocurrency content and extract structured information including:
        1. Headline and summary
        2. Overall sentiment (bullish, bearish, neutral)
        3. Content category (breaking, analysis, regulatory, etc.)
        4. Market impact assessment (high, medium, low, none)
        5. Key entities mentioned (tokens, exchanges, protocols, people, companies, regulators)
        6. Relevance to different crypto investor personas (meme snipers, gem hunters, legacy investors)
        7. Urgency score (0-10) indicating how time-sensitive this information is
        8. Any specific price mentions for tokens
        
        Focus on extracting factual information and avoid speculation. If certain information
        is not present in the content, omit those fields from your response.
        
        For sentiment analysis:
        - Bullish: Content suggests positive price movement or market outlook
        - Bearish: Content suggests negative price movement or market outlook
        - Neutral: Content is balanced or doesn't clearly indicate a market direction
        
        For market impact:
        - High: Could significantly affect prices or market behavior
        - Medium: Moderate potential effect on the market
        - Low: Minor or limited market effect
        - None: No discernible market impact
        
        For urgency scoring (0-10):
        - 0-2: Not time-sensitive, general information
        - 3-5: Moderately time-sensitive
        - 6-8: Important to know soon
        - 9-10: Critical, immediate attention required
        """
        
        # Initialize the base class with enhanced parameters
        super().__init__(
            provider=provider,
            api_token=api_token,
            schema=schema,
            instruction=instruction,
            base_url=base_url,
            model=model,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs
        )
        
        logger.info(f"Initialized CryptoLLMExtractionStrategy with {provider} provider and {self.model} model")
    
    @measure_performance
    async def extract(self, url: str, html: str, instruction: Optional[str] = None, 
                     schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract cryptocurrency-specific information from content.
        
        This method extends the base extraction with crypto-specific post-processing.
        
        Args:
            url: The URL of the content
            html: The HTML or markdown content to extract information from
            instruction: Optional override for the default instruction
            schema: Optional override for the default schema
            
        Returns:
            Dictionary of extracted cryptocurrency information
        """
        logger.info(f"Starting crypto extraction for URL: {url}")
        
        # Call the base class extraction method
        result = await super().extract(url, html, instruction, schema)
        
        # Perform crypto-specific post-processing
        try:
            self._validate_crypto_extraction(result)
            self._enhance_crypto_extraction(result)
            logger.info("Crypto-specific post-processing completed successfully")
        except Exception as e:
            logger.warning(f"Crypto-specific post-processing error: {str(e)}")
            # Continue with the extraction result even if post-processing fails
        
        return result
    
    def _validate_crypto_extraction(self, extraction: Dict[str, Any]) -> None:
        """Validate the cryptocurrency extraction result.
        
        Args:
            extraction: The extraction result to validate
        """
        # Check for required fields
        required_fields = ["headline", "summary", "sentiment"]
        missing_fields = [field for field in required_fields if field not in extraction]
        
        if missing_fields:
            logger.warning(f"Missing required fields in extraction: {', '.join(missing_fields)}")
        
        # Validate sentiment value
        if "sentiment" in extraction and extraction["sentiment"] not in ["bullish", "bearish", "neutral"]:
            logger.warning(f"Invalid sentiment value: {extraction['sentiment']}")
            # Correct to a default value
            extraction["sentiment"] = "neutral"
    
    def _enhance_crypto_extraction(self, extraction: Dict[str, Any]) -> None:
        """Enhance the cryptocurrency extraction result with additional information.
        
        Args:
            extraction: The extraction result to enhance
        """
        # Add a confidence score if not present
        if "_metadata" not in extraction:
            extraction["_metadata"] = {}
            
        # Add extraction strategy information
        extraction["_metadata"]["strategy"] = "crypto"
        extraction["_metadata"]["strategy_version"] = "1.0"
        
        # Ensure persona_relevance exists
        if "persona_relevance" not in extraction:
            extraction["persona_relevance"] = {
                "meme_snipers": 0.0,
                "gem_hunters": 0.0,
                "legacy_investors": 0.0
            }
            
        # Ensure urgency_score exists
        if "urgency_score" not in extraction:
            extraction["urgency_score"] = 0.0