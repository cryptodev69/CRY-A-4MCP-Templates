#!/usr/bin/env python3
"""
Example demonstrating the use of the synchronous extraction strategy wrapper.

This script shows how to use the SyncExtractionStrategyWrapper to convert
asynchronous extraction strategies to synchronous ones, which is useful
for integration with synchronous code or UI frameworks like Streamlit.
"""

import os
import sys
import json
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import the necessary components
from src.cry_a_4mcp.crawl4ai.extraction_strategies import (
    LLMExtractionStrategy,
    CryptoLLMExtractionStrategy
)
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper
from src.cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory


def main():
    """Demonstrate the use of synchronous extraction strategies."""
    print("Synchronous Extraction Strategy Example")
    print("-" * 40)
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Sample content to analyze
    sample_url = "https://example.com/crypto-news"
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
    
    print("\nMethod 1: Using SyncExtractionStrategyWrapper directly")
    print("-" * 40)
    
    # Create an asynchronous extraction strategy
    async_strategy = CryptoLLMExtractionStrategy(
        provider="openai",
        api_token=api_key,
        model="gpt-3.5-turbo"
    )
    
    # Wrap it with the synchronous wrapper
    sync_strategy = SyncExtractionStrategyWrapper(async_strategy)
    
    # Use the synchronous extract method
    try:
        print("Extracting information using synchronous wrapper...")
        result = sync_strategy.extract(sample_url, sample_content)
        print("\nExtraction Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
    
    print("\nMethod 2: Using StrategyFactory.create_sync()")
    print("-" * 40)
    
    # Create a synchronized strategy using the factory
    try:
        print("Creating synchronized strategy using factory...")
        factory_sync_strategy = StrategyFactory.create_sync(
            "CryptoLLMExtractionStrategy",
            config={
                "api_token": api_key,
                "provider": "openai",
                "model": "gpt-3.5-turbo"
            }
        )
        
        print("Extracting information using factory-created synchronized strategy...")
        factory_result = factory_sync_strategy.extract(sample_url, sample_content)
        print("\nExtraction Result:")
        print(json.dumps(factory_result, indent=2))
    except Exception as e:
        print(f"Error during factory extraction: {str(e)}")
    
    print("\nMethod 3: Using StrategyFactory.create_from_config_sync()")
    print("-" * 40)
    
    # Create a synchronized strategy from config
    try:
        print("Creating synchronized strategy from config...")
        config = {
            "strategy": "CryptoLLMExtractionStrategy",
            "config": {
                "api_token": api_key,
                "provider": "openai",
                "model": "gpt-3.5-turbo"
            }
        }
        config_sync_strategy = StrategyFactory.create_from_config_sync(config)
        
        print("Extracting information using config-created synchronized strategy...")
        config_result = config_sync_strategy.extract(sample_url, sample_content)
        print("\nExtraction Result:")
        print(json.dumps(config_result, indent=2))
    except Exception as e:
        print(f"Error during config extraction: {str(e)}")


if __name__ == "__main__":
    main()