#!/usr/bin/env python3
"""
Direct test for LLM extraction using OpenRouter API.
This script doesn't require the MCP server to run.
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any, Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the LLMExtractionStrategy from the project
from cry_a_4mcp.crawl4ai.extraction_strategy import LLMExtractionStrategy


class SimpleExtractionStrategy(LLMExtractionStrategy):
    """
    A simple extraction strategy for testing the LLM extraction.
    """
    
    def __init__(self, provider: str, api_token: str, base_url: Optional[str] = None):
        """
        Initialize the simple extraction strategy.
        
        Args:
            provider: LLM provider (e.g., "openai", "groq")
            api_token: API token for the LLM provider
            base_url: Optional base URL for the API (useful for OpenRouter)
        """
        # Define a simple schema for extraction
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
        
        # Define a simple instruction for extraction
        instruction = """
        Analyze the provided content and extract the following information:
        1. A concise title that captures the main topic
        2. A brief summary of the content (2-3 sentences)
        3. 3-5 key points from the content
        4. The overall sentiment of the content (positive, negative, or neutral)
        
        Focus on extracting factual information and avoid speculation.
        """
        
        # Initialize the base class
        super().__init__(
            provider=provider,
            api_token=api_token,
            schema=schema,
            instruction=instruction,
            base_url=base_url
        )


async def test_llm_extraction():
    """
    Test the LLMExtractionStrategy with OpenRouter.
    """
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
    sample_content = """
    Bitcoin Surges Past $60,000 as Institutional Adoption Accelerates
    
    Bitcoin has surpassed the $60,000 mark for the first time in two weeks, driven by increasing institutional adoption and positive market sentiment. The cryptocurrency market has shown strong recovery following recent regulatory clarity from several major economies.
    
    Key developments include:
    
    1. BlackRock's Bitcoin ETF saw inflows of over $500 million in the past week
    2. El Salvador announced plans to build a "Bitcoin City" funded by crypto-bonds
    3. Major payment processor Stripe expanded its cryptocurrency payment options
    4. Federal Reserve Chairman Jerome Powell stated that the U.S. has no intention to ban cryptocurrencies
    
    Market analysts suggest this could be the beginning of a new bull run, with some predicting Bitcoin could reach $100,000 by year-end. However, others caution that volatility remains high and regulatory challenges persist in some regions.
    
    Trading volume across major exchanges has increased by 30% compared to last month, indicating renewed interest from both retail and institutional investors.
    """
    
    try:
        # Extract information using the LLM
        print("\nExtracting information from sample content...")
        result = await extraction_strategy.extract(
            url="https://example.com/crypto-news",
            html=sample_content
        )
        
        # Print the extraction result
        print("\nExtraction Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error during extraction: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_llm_extraction())