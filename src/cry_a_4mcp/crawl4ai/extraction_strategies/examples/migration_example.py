"""Migration example script.

This script demonstrates how to migrate from old extraction code to the new
extraction strategies framework. It shows both the old approach and the new approach
side by side for comparison.
"""

import asyncio
import logging
import json
import os
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample content for testing
SAMPLE_CRYPTO_CONTENT = """
Bitcoin surged to $60,000 today, reaching a new all-time high as institutional investors
continue to enter the market. Ethereum also saw significant gains, climbing above $4,000.
Analysts attribute the rally to growing institutional adoption and the recent approval
of Bitcoin ETFs. Meanwhile, Ripple (XRP) faces ongoing regulatory challenges with the SEC.

The total cryptocurrency market capitalization now exceeds $2 trillion, with Bitcoin
dominating at approximately 45% of the market share. DeFi protocols on Ethereum have
locked in over $100 billion in total value, with Uniswap leading the pack.

In other news, Solana's network experienced a brief outage yesterday but has since
recovered. The team is implementing upgrades to prevent similar issues in the future.
"""

SAMPLE_URL = "https://example.com/crypto-news"


# ============================================================================
# Old approach: Direct extraction functions
# ============================================================================

def old_extract_crypto_data(content: str, api_key: str) -> Dict[str, Any]:
    """Old approach: Extract cryptocurrency data using a direct function call.
    
    Args:
        content: The content to extract information from.
        api_key: The API key for the LLM provider.
        
    Returns:
        Extracted cryptocurrency information.
    """
    logger.info("Using old approach to extract crypto data")
    
    # In a real implementation, this would call an LLM API
    # For demonstration, we'll return mock data
    
    # Simulate API call delay
    import time
    time.sleep(1)
    
    # Mock extraction result
    return {
        "headline": "Bitcoin reaches new all-time high",
        "summary": "Bitcoin surged to $60,000, reaching a new all-time high as institutional investors continue to enter the market.",
        "cryptocurrencies": [
            {"name": "Bitcoin", "ticker": "BTC", "price": "$60,000", "movement": "up"},
            {"name": "Ethereum", "ticker": "ETH", "price": "$4,000", "movement": "up"},
            {"name": "Ripple", "ticker": "XRP", "price": None, "movement": None}
        ],
        "market_data": {
            "total_market_cap": "$2 trillion",
            "bitcoin_dominance": "45%"
        },
        "defi_data": {
            "total_value_locked": "$100 billion",
            "leading_protocol": "Uniswap"
        },
        "events": [
            {"type": "price_movement", "description": "Bitcoin reached all-time high"},
            {"type": "network_issue", "description": "Solana network experienced a brief outage"}
        ]
    }


def old_extract_news_data(content: str, api_key: str) -> Dict[str, Any]:
    """Old approach: Extract news data using a direct function call.
    
    Args:
        content: The content to extract information from.
        api_key: The API key for the LLM provider.
        
    Returns:
        Extracted news information.
    """
    logger.info("Using old approach to extract news data")
    
    # In a real implementation, this would call an LLM API
    # For demonstration, we'll return mock data
    
    # Simulate API call delay
    import time
    time.sleep(1)
    
    # Mock extraction result
    return {
        "headline": "Cryptocurrency Market Reaches New Heights",
        "summary": "The cryptocurrency market has reached new heights with Bitcoin and Ethereum leading the rally.",
        "key_points": [
            "Bitcoin reached $60,000",
            "Ethereum climbed above $4,000",
            "Total market cap exceeds $2 trillion",
            "Solana experienced a network outage"
        ],
        "sources": ["Market analysts", "Trading platforms"],
        "sentiment": "positive",
        "topics": ["cryptocurrency", "bitcoin", "ethereum", "market analysis"],
        "entities": ["Bitcoin", "Ethereum", "Ripple", "Solana", "SEC", "Uniswap"]
    }


def old_comprehensive_extraction(content: str, api_key: str) -> Dict[str, Any]:
    """Old approach: Comprehensive extraction combining multiple extraction functions.
    
    Args:
        content: The content to extract information from.
        api_key: The API key for the LLM provider.
        
    Returns:
        Comprehensive extracted information.
    """
    logger.info("Using old approach for comprehensive extraction")
    
    # Extract data using both functions
    crypto_data = old_extract_crypto_data(content, api_key)
    news_data = old_extract_news_data(content, api_key)
    
    # Merge results (simple approach)
    result = {}
    result.update(crypto_data)
    
    # Add news-specific fields that don't conflict with crypto fields
    for key, value in news_data.items():
        if key not in result or key in ["key_points", "sources", "sentiment", "topics", "entities"]:
            result[key] = value
    
    return result


# ============================================================================
# New approach: Using the extraction strategies framework
# ============================================================================

async def new_extract_crypto_data(url: str, content: str, api_key: str) -> Dict[str, Any]:
    """New approach: Extract cryptocurrency data using the strategy framework.
    
    Args:
        url: The URL of the content.
        content: The content to extract information from.
        api_key: The API key for the LLM provider.
        
    Returns:
        Extracted cryptocurrency information.
    """
    logger.info("Using new approach to extract crypto data")
    
    # Import the factory
    from cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory
    
    # Create a strategy instance
    factory = StrategyFactory()
    strategy = factory.create_strategy(
        "CryptoLLMExtractionStrategy",
        api_token=api_key,
        model="gpt-4"
    )
    
    # Extract information
    result = await strategy.extract(url, content)
    
    return result


async def new_extract_news_data(url: str, content: str, api_key: str) -> Dict[str, Any]:
    """New approach: Extract news data using the strategy framework.
    
    Args:
        url: The URL of the content.
        content: The content to extract information from.
        api_key: The API key for the LLM provider.
        
    Returns:
        Extracted news information.
    """
    logger.info("Using new approach to extract news data")
    
    # Import the factory
    from cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory
    
    # Create a strategy instance
    factory = StrategyFactory()
    strategy = factory.create_strategy(
        "NewsLLMExtractionStrategy",
        api_token=api_key,
        model="gpt-4"
    )
    
    # Extract information
    result = await strategy.extract(url, content)
    
    return result


async def new_comprehensive_extraction(url: str, content: str, api_key: str) -> Dict[str, Any]:
    """New approach: Comprehensive extraction using a composite strategy.
    
    Args:
        url: The URL of the content.
        content: The content to extract information from.
        api_key: The API key for the LLM provider.
        
    Returns:
        Comprehensive extracted information.
    """
    logger.info("Using new approach for comprehensive extraction")
    
    # Import the composite strategy
    from cry_a_4mcp.crawl4ai.extraction_strategies.composite import ComprehensiveLLMExtractionStrategy
    
    # Create a composite strategy instance
    strategy = ComprehensiveLLMExtractionStrategy(
        api_token=api_key,
        model="gpt-4",
        strategies=["CryptoLLMExtractionStrategy", "NewsLLMExtractionStrategy"],
        merge_mode="smart"
    )
    
    # Extract information
    result = await strategy.extract(url, content)
    
    return result


# ============================================================================
# Demonstration functions
# ============================================================================

def run_old_approach():
    """Run the old approach to extraction."""
    logger.info("=== Running Old Approach ===")
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY", "dummy_api_key")
    
    # Extract data using the old approach
    crypto_result = old_extract_crypto_data(SAMPLE_CRYPTO_CONTENT, api_key)
    news_result = old_extract_news_data(SAMPLE_CRYPTO_CONTENT, api_key)
    comprehensive_result = old_comprehensive_extraction(SAMPLE_CRYPTO_CONTENT, api_key)
    
    # Print results
    logger.info("Old Crypto Extraction Result:")
    print(json.dumps(crypto_result, indent=2))
    
    logger.info("Old News Extraction Result:")
    print(json.dumps(news_result, indent=2))
    
    logger.info("Old Comprehensive Extraction Result:")
    print(json.dumps(comprehensive_result, indent=2))


async def run_new_approach():
    """Run the new approach to extraction."""
    logger.info("=== Running New Approach ===")
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY", "dummy_api_key")
    
    # Extract data using the new approach
    crypto_result = await new_extract_crypto_data(SAMPLE_URL, SAMPLE_CRYPTO_CONTENT, api_key)
    news_result = await new_extract_news_data(SAMPLE_URL, SAMPLE_CRYPTO_CONTENT, api_key)
    comprehensive_result = await new_comprehensive_extraction(SAMPLE_URL, SAMPLE_CRYPTO_CONTENT, api_key)
    
    # Print results
    logger.info("New Crypto Extraction Result:")
    print(json.dumps(crypto_result, indent=2))
    
    logger.info("New News Extraction Result:")
    print(json.dumps(news_result, indent=2))
    
    logger.info("New Comprehensive Extraction Result:")
    print(json.dumps(comprehensive_result, indent=2))


async def compare_approaches():
    """Compare the old and new approaches."""
    logger.info("=== Comparing Approaches ===")
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY", "dummy_api_key")
    
    # Run both approaches and measure time
    import time
    
    # Old approach
    start_time = time.time()
    old_result = old_comprehensive_extraction(SAMPLE_CRYPTO_CONTENT, api_key)
    old_time = time.time() - start_time
    
    # New approach
    start_time = time.time()
    new_result = await new_comprehensive_extraction(SAMPLE_URL, SAMPLE_CRYPTO_CONTENT, api_key)
    new_time = time.time() - start_time
    
    # Print comparison
    logger.info(f"Old approach time: {old_time:.2f} seconds")
    logger.info(f"New approach time: {new_time:.2f} seconds")
    logger.info(f"Time difference: {new_time - old_time:.2f} seconds")
    
    # Compare result structures
    old_keys = set(old_result.keys())
    new_keys = set(new_result.keys())
    
    logger.info(f"Old result keys: {sorted(old_keys)}")
    logger.info(f"New result keys: {sorted(new_keys)}")
    logger.info(f"Common keys: {sorted(old_keys & new_keys)}")
    logger.info(f"Keys only in old result: {sorted(old_keys - new_keys)}")
    logger.info(f"Keys only in new result: {sorted(new_keys - old_keys)}")


async def main():
    """Main function to demonstrate migration."""
    logger.info("Starting migration example demonstration")
    
    # Run the old approach
    run_old_approach()
    
    # Run the new approach
    await run_new_approach()
    
    # Compare approaches
    await compare_approaches()
    
    logger.info("Migration example demonstration completed")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())