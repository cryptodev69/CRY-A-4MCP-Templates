#!/usr/bin/env python3
"""
Direct test for CryptoCrawler with LLM extraction using OpenRouter API.
This script doesn't require the MCP server to run.
"""

import asyncio
import os
import sys
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the LLMExtractionStrategy from the project
from cry_a_4mcp.crawl4ai.extraction_strategy import LLMExtractionStrategy


# We don't need the crawler-related data classes for this simplified test


class CryptoLLMExtractionStrategy(LLMExtractionStrategy):
    """Cryptocurrency-specific LLM extraction strategy.
    
    This class extends the base LLMExtractionStrategy with cryptocurrency-specific
    schema and instructions.
    """
    
    def __init__(self, provider: str, api_token: str, base_url: Optional[str] = None):
        """Initialize the cryptocurrency LLM extraction strategy.
        
        Args:
            provider: LLM provider (e.g., "openai", "groq")
            api_token: API token for the LLM provider
            base_url: Optional base URL for the API (useful for OpenRouter)
        """
        # Define the schema for cryptocurrency content extraction
        schema = {
            "type": "object",
            "properties": {
                "headline": {"type": "string"},
                "summary": {"type": "string"},
                "sentiment": {"type": "string", "enum": ["bullish", "bearish", "neutral"]},
                "category": {"type": "string", "enum": ["breaking", "analysis", "regulatory", "institutional", "technical", "defi", "nft", "meme"]},
                "market_impact": {"type": "string", "enum": ["high", "medium", "low", "none"]},
                "key_entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["token", "exchange", "protocol", "person", "company", "regulator"]},
                            "relevance": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    }
                },
                "persona_relevance": {
                    "type": "object",
                    "properties": {
                        "meme_snipers": {"type": "number", "minimum": 0, "maximum": 1},
                        "gem_hunters": {"type": "number", "minimum": 0, "maximum": 1},
                        "legacy_investors": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                },
                "urgency_score": {"type": "number", "minimum": 0, "maximum": 10},
                "price_mentions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "token": {"type": "string"},
                            "price": {"type": "string"},
                            "change": {"type": "string"}
                        }
                    }
                }
            }
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
        """
        
        # Initialize the base class
        super().__init__(
            provider=provider,
            api_token=api_token,
            schema=schema,
            instruction=instruction,
            base_url=base_url
        )


async def test_direct_crypto_llm_extraction():
    """Test the CryptoLLMExtractionStrategy directly without a crawler."""
    # Get OpenRouter API key from environment variable
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set")
        return
    
    print(f"Using OpenRouter API key: {openrouter_api_key[:8]}...{openrouter_api_key[-4:]}")
    
    # Create a CryptoLLMExtractionStrategy instance with OpenRouter
    extraction_strategy = CryptoLLMExtractionStrategy(
        provider="openai",  # OpenRouter uses OpenAI-compatible API
        api_token=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    print(f"Using model: {extraction_strategy.model}")
    
    # Sample crypto content to analyze
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
    
    Ethereum has also shown strong performance, climbing above $4,000 as the network prepares for its next major upgrade. The DeFi sector continues to grow, with total value locked (TVL) reaching new all-time highs.
    
    Meme coins like Dogecoin and Shiba Inu have seen increased volatility, with social media mentions driving price action more than fundamental developments.
    """
    
    try:
        # Extract information using the LLM
        print("\nExtracting information from sample crypto content...")
        result = await extraction_strategy.extract(
            url="https://example.com/crypto-news",
            html=sample_content
        )
        
        # Print the extraction result
        print_llm_extraction(result)
        
    except Exception as e:
        print(f"Error during extraction: {str(e)}")


def print_llm_extraction(extraction: Optional[Dict]) -> None:
    """Print details of an LLM extraction result."""
    print("\nLLM Extraction Result:")
    if not extraction:
        print("  No LLM extraction result available")
        return
    
    # Print headline and summary
    if "headline" in extraction:
        print(f"Headline: {extraction['headline']}")
    if "summary" in extraction:
        print(f"Summary: {extraction['summary']}")
    
    # Print sentiment and category
    if "sentiment" in extraction:
        print(f"Sentiment: {extraction['sentiment']}")
    if "category" in extraction:
        print(f"Category: {extraction['category']}")
    if "market_impact" in extraction:
        print(f"Market Impact: {extraction['market_impact']}")
    
    # Print key entities
    if "key_entities" in extraction and extraction["key_entities"]:
        print("\nKey Entities:")
        for entity in extraction["key_entities"]:
            print(f"  - {entity['name']} ({entity['type']}): {entity['relevance']}")
    
    # Print persona relevance
    if "persona_relevance" in extraction:
        print("\nPersona Relevance:")
        for persona, score in extraction["persona_relevance"].items():
            print(f"  - {persona}: {score}")
    
    # Print urgency score
    if "urgency_score" in extraction:
        print(f"\nUrgency Score: {extraction['urgency_score']}/10")
    
    # Print price mentions
    if "price_mentions" in extraction and extraction["price_mentions"]:
        print("\nPrice Mentions:")
        for price in extraction["price_mentions"]:
            print(f"  - {price['token']}: {price['price']} ({price['change'] if 'change' in price else 'N/A'})")
    
    # Print metadata if available
    if "_metadata" in extraction:
        print("\nMetadata:")
        if "model" in extraction["_metadata"]:
            print(f"  Model: {extraction['_metadata']['model']}")
        if "usage" in extraction["_metadata"]:
            usage = extraction["_metadata"]["usage"]
            print(f"  Tokens: {usage.get('total_tokens', 'N/A')} (Prompt: {usage.get('prompt_tokens', 'N/A')}, Completion: {usage.get('completion_tokens', 'N/A')})")


if __name__ == "__main__":
    asyncio.run(test_direct_crypto_llm_extraction())