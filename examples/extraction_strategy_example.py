#!/usr/bin/env python3
"""
Example script demonstrating the use of the extraction strategies framework.

This script shows how to use the extraction strategies framework to extract
information from web content using different strategies.
"""

import asyncio
import json
import os
import sys
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the extraction strategies
from src.cry_a_4mcp.crawl4ai.extraction_strategies import (
    LLMExtractionStrategy,
    CryptoLLMExtractionStrategy,
    StrategyRegistry,
    StrategyFactory,
    CompositeExtractionStrategy,
    register_strategy
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('extraction_example')

# Example content for extraction
EXAMPLE_URL = "https://example.com/crypto-news"
EXAMPLE_CONTENT = """
# Bitcoin Surges Past $60,000 as ETF Approval Looms

Bitcoin has surged past the $60,000 mark for the first time in months, as anticipation builds around the potential approval of a spot Bitcoin ETF by the SEC. The leading cryptocurrency has seen a remarkable rally in recent weeks, with many analysts attributing the price movement to growing institutional interest.

"This is a significant milestone for Bitcoin," said Jane Smith, crypto analyst at Capital Investments. "The potential ETF approval could open the floodgates for institutional capital."

Meanwhile, Ethereum has also shown strong performance, climbing above $3,500 as the broader crypto market experiences positive momentum. The total cryptocurrency market capitalization has now exceeded $2 trillion.

Regulatory developments continue to shape the landscape, with SEC Chair Gary Gensler reiterating the need for investor protection in the crypto space. However, industry insiders view the potential ETF approval as a sign of growing regulatory acceptance.

Trading volumes across major exchanges have increased by 40% in the past week, indicating heightened market activity. Derivatives markets are showing bullish sentiment, with open interest in Bitcoin futures reaching new highs.

As institutional adoption accelerates, companies like MicroStrategy and Tesla, which hold Bitcoin on their balance sheets, have seen their stock prices rise in correlation with the cryptocurrency's performance.

Analysts remain divided on the short-term outlook, with some predicting a pullback after the ETF decision, while others see potential for continued upward momentum toward new all-time highs.
"""

# Define a custom extraction strategy
class SimpleExtractionStrategy(LLMExtractionStrategy):
    """A simple extraction strategy for general content."""
    
    def __init__(self, provider="openrouter", api_token=None, **kwargs):
        # Define a simple schema
        simple_schema = {
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
                    "description": "Key points from the content"
                },
                "sentiment": {
                    "type": "string",
                    "enum": ["negative", "neutral", "positive"],
                    "description": "The overall sentiment of the content"
                }
            },
            "required": ["title", "summary"]
        }
        
        # Define a simple instruction
        simple_instruction = """
        Extract the following information from the provided content:
        1. The title or headline
        2. A brief summary (2-3 sentences)
        3. 3-5 key points as bullet points
        4. The overall sentiment (negative, neutral, or positive)
        
        Provide your extraction in a structured JSON format according to the provided schema.
        """
        
        # Initialize the base class
        super().__init__(
            provider=provider,
            api_token=api_token,
            instruction=simple_instruction,
            schema=simple_schema,
            **kwargs
        )

# Register the custom strategy
register_strategy(
    name="SimpleExtractionStrategy",
    description="A simple extraction strategy for general content",
    category="general"
)(SimpleExtractionStrategy)

async def run_extraction_examples():
    """Run examples of different extraction strategies."""
    # Get API token from environment variable
    api_token = os.environ.get("OPENROUTER_API_KEY")
    if not api_token:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        return
    
    logger.info("Starting extraction examples")
    
    # Example 1: Using the base LLM extraction strategy
    logger.info("Example 1: Using LLMExtractionStrategy directly")
    base_strategy = LLMExtractionStrategy(
        provider="openrouter",
        api_token=api_token,
        instruction="Extract the main headline and a brief summary from the content.",
        schema={
            "type": "object",
            "properties": {
                "headline": {"type": "string"},
                "summary": {"type": "string"}
            },
            "required": ["headline", "summary"]
        }
    )
    
    try:
        base_result = await base_strategy.extract(EXAMPLE_URL, EXAMPLE_CONTENT)
        logger.info(f"Base strategy result: {json.dumps(base_result, indent=2)}")
    except Exception as e:
        logger.error(f"Base strategy failed: {str(e)}")
    
    # Example 2: Using the crypto-specific extraction strategy
    logger.info("\nExample 2: Using CryptoLLMExtractionStrategy")
    crypto_strategy = CryptoLLMExtractionStrategy(
        provider="openrouter",
        api_token=api_token
    )
    
    try:
        crypto_result = await crypto_strategy.extract(EXAMPLE_URL, EXAMPLE_CONTENT)
        logger.info(f"Crypto strategy result: {json.dumps(crypto_result, indent=2)}")
    except Exception as e:
        logger.error(f"Crypto strategy failed: {str(e)}")
    
    # Example 3: Using the custom simple extraction strategy
    logger.info("\nExample 3: Using SimpleExtractionStrategy")
    simple_strategy = SimpleExtractionStrategy(
        provider="openrouter",
        api_token=api_token
    )
    
    try:
        simple_result = await simple_strategy.extract(EXAMPLE_URL, EXAMPLE_CONTENT)
        logger.info(f"Simple strategy result: {json.dumps(simple_result, indent=2)}")
    except Exception as e:
        logger.error(f"Simple strategy failed: {str(e)}")
    
    # Example 4: Using the strategy factory
    logger.info("\nExample 4: Using StrategyFactory")
    try:
        factory_strategy = StrategyFactory.create(
            "CryptoLLMExtractionStrategy",
            {"provider": "openrouter", "api_token": api_token}
        )
        factory_result = await factory_strategy.extract(EXAMPLE_URL, EXAMPLE_CONTENT)
        logger.info(f"Factory-created strategy result: {json.dumps(factory_result, indent=2)}")
    except Exception as e:
        logger.error(f"Factory-created strategy failed: {str(e)}")
    
    # Example 5: Using a composite strategy
    logger.info("\nExample 5: Using CompositeExtractionStrategy")
    try:
        composite_strategy = CompositeExtractionStrategy([
            simple_strategy,
            crypto_strategy
        ])
        composite_result = await composite_strategy.extract(EXAMPLE_URL, EXAMPLE_CONTENT)
        logger.info(f"Composite strategy result: {json.dumps(composite_result, indent=2)}")
    except Exception as e:
        logger.error(f"Composite strategy failed: {str(e)}")
    
    # Example 6: Listing available strategies from the registry
    logger.info("\nExample 6: Listing available strategies from the registry")
    strategies = StrategyRegistry.get_all()
    logger.info(f"Available strategies: {', '.join(strategies.keys())}")
    
    categories = StrategyRegistry.get_categories()
    logger.info(f"Available categories: {', '.join(categories)}")
    
    for category in categories:
        category_strategies = StrategyRegistry.get_by_category(category)
        logger.info(f"Strategies in category '{category}': {', '.join(category_strategies.keys())}")
    
    logger.info("Extraction examples completed")

if __name__ == "__main__":
    asyncio.run(run_extraction_examples())