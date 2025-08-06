#!/usr/bin/env python3
"""
Simple verification script for the NFT extraction strategy.

This script verifies that the NFT extraction strategy is properly registered
and can be instantiated without running full tests.
"""

import os
import sys
import asyncio
from pprint import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.cry_a_4mcp.crawl4ai.extraction_strategies import (
    NFTLLMExtractionStrategy,
    StrategyRegistry,
    StrategyFactory
)


async def verify_nft_strategy():
    """Verify that the NFT extraction strategy is properly registered and can be instantiated."""
    print("\n=== Verifying NFT Extraction Strategy ===\n")
    
    # Check registration
    print("Checking strategy registration...")
    all_strategies = StrategyRegistry.get_all()
    if "NFTLLMExtractionStrategy" in all_strategies:
        print("✅ NFTLLMExtractionStrategy is registered")
    else:
        print("❌ NFTLLMExtractionStrategy is NOT registered")
        print(f"Available strategies: {', '.join(all_strategies)}")
    
    # Check categories
    print("\nChecking strategy categories...")
    categories = StrategyRegistry.get_categories()
    if "nft" in categories:
        print("✅ 'nft' category exists")
        nft_strategies = StrategyRegistry.get_by_category("nft")
        print(f"NFT strategies: {', '.join(nft_strategies)}")
    else:
        print("❌ 'nft' category does NOT exist")
        print(f"Available categories: {', '.join(categories)}")
    
    # Check instantiation
    print("\nChecking strategy instantiation...")
    try:
        strategy = NFTLLMExtractionStrategy(
            provider="test",
            api_token="test_token"
        )
        print("✅ NFTLLMExtractionStrategy can be instantiated")
        print(f"Schema properties: {', '.join(strategy.schema['properties'].keys())}")
    except Exception as e:
        print(f"❌ Error instantiating NFTLLMExtractionStrategy: {e}")
    
    # Check schema
    print("\nChecking NFT-specific schema fields...")
    try:
        strategy = NFTLLMExtractionStrategy(
            provider="test",
            api_token="test_token"
        )
        nft_specific_fields = ["nft_data", "technology_aspects", "metaverse_integration"]
        for field in nft_specific_fields:
            if field in strategy.schema["properties"]:
                print(f"✅ Field '{field}' exists in schema")
            else:
                print(f"❌ Field '{field}' does NOT exist in schema")
    except Exception as e:
        print(f"❌ Error checking schema: {e}")


if __name__ == "__main__":
    asyncio.run(verify_nft_strategy())