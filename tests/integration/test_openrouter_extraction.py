#!/usr/bin/env python3

import asyncio
import os
import json
from typing import Dict, Any

# Import the LLMExtractionStrategy
from src.cry_a_4mcp.crawl4ai.extraction_strategy import LLMExtractionStrategy


class SimpleExtractionStrategy(LLMExtractionStrategy):
    """A simple extraction strategy for testing OpenRouter integration."""
    
    def __init__(self, provider: str, api_token: str, base_url: str = None):
        """Initialize the simple extraction strategy.
        
        Args:
            provider: LLM provider (e.g., "openai")
            api_token: API token for the LLM provider
            base_url: Optional base URL for the API
        """
        # Define a simple schema for content extraction
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "summary": {"type": "string"},
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]}
            }
        }
        
        # Define a simple instruction
        instruction = """
        Analyze this content and extract the following information:
        1. Title or headline
        2. A brief summary (2-3 sentences)
        3. 3-5 key points from the content
        4. Overall sentiment (positive, negative, or neutral)
        
        Return the information in JSON format according to the provided schema.
        """
        
        # Initialize the base class
        super().__init__(
            provider=provider,
            api_token=api_token,
            schema=schema,
            instruction=instruction,
            base_url=base_url
        )


async def test_openrouter_extraction():
    """Test the LLMExtractionStrategy with OpenRouter."""
    # Get OpenRouter API key from environment variable
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set")
        return
    
    print(f"Using OpenRouter API key: {openrouter_api_key[:8]}...{openrouter_api_key[-4:]}")
    
    # Create a SimpleExtractionStrategy instance with OpenRouter
    extraction_strategy = SimpleExtractionStrategy(
        provider="openai",  # OpenRouter uses OpenAI-compatible API
        api_token=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    print(f"Using model: {extraction_strategy.model}")
    
    # Sample content to analyze
    url = "https://example.com/bitcoin-news"
    content = """
    # Bitcoin Surges Past $60,000 as Institutional Adoption Accelerates
    
    Bitcoin has surpassed the $60,000 mark for the first time in two weeks, driven by increased institutional adoption and positive market sentiment. The cryptocurrency market as a whole has seen significant gains, with Ethereum also climbing above $3,000.
    
    According to market analysts, several factors have contributed to this rally:
    
    1. Major financial institutions have announced new Bitcoin investment products
    2. Regulatory clarity has improved in key markets
    3. Inflation concerns continue to drive interest in alternative assets
    4. Technical indicators suggest strong buying pressure
    
    "We're seeing unprecedented institutional interest," said Jane Smith, crypto analyst at Capital Research. "The market has matured significantly over the past year, and Bitcoin is increasingly viewed as a legitimate asset class."
    
    However, some experts urge caution, noting that volatility remains high and regulatory challenges persist in certain jurisdictions. Despite these concerns, the overall market sentiment appears bullish for the near term.
    
    Trading volumes across major exchanges have increased by approximately 30% over the past week, indicating renewed interest from both retail and institutional investors.
    """
    
    try:
        # Extract information using the strategy
        print("\nExtracting information from content...")
        result = await extraction_strategy.extract(url=url, html=content)
        
        # Print the result
        print("\nExtraction Result:")
        print(json.dumps(result, indent=2))
        
        # Print model information if available
        if "_metadata" in result and "model" in result["_metadata"]:
            print(f"\nModel used: {result['_metadata']['model']}")
        
        # Print usage information if available
        if "_metadata" in result and "usage" in result["_metadata"]:
            usage = result["_metadata"]["usage"]
            print(f"\nToken Usage:")
            print(f"  Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"  Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"  Total tokens: {usage.get('total_tokens', 'N/A')}")
        
    except Exception as e:
        print(f"Error during extraction: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_openrouter_extraction())