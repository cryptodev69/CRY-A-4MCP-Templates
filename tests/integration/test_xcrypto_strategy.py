#!/usr/bin/env python3
"""
Test script to verify that the XCryptoHunterLLMExtractionStrategy is properly loaded and registered.
"""

import os
import sys
import logging

# Add the src directory to the Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

from cry_a_4mcp.crawl4ai.extraction_strategies.registry import StrategyRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_xcrypto_strategy')

def test_xcrypto_strategy():
    """Test that the XCryptoHunterLLMExtractionStrategy is registered."""
    # Get all registered strategies
    all_strategies = StrategyRegistry.get_all()
    logger.info(f"Total registered strategies: {len(all_strategies)}")
    
    # Print all strategy names
    logger.info("All registered strategies:")
    for name, strategy in all_strategies.items():
        logger.info(f"- {name}: {strategy.__name__}")
    
    # Check if XCryptoHunterLLMExtractionStrategy is registered
    if 'XCryptoHunterLLMExtractionStrategy' in all_strategies:
        logger.info("✅ XCryptoHunterLLMExtractionStrategy is registered!")
    else:
        logger.error("❌ XCryptoHunterLLMExtractionStrategy is NOT registered!")
    
    # Get all categories
    categories = StrategyRegistry.get_categories()
    logger.info(f"Available categories: {categories}")
    
    # Check strategies in the crypto category
    crypto_strategies = StrategyRegistry.get_by_category('crypto')
    logger.info(f"Crypto category strategies: {len(crypto_strategies)}")
    for name, strategy in crypto_strategies.items():
        logger.info(f"- {name}: {strategy.__name__}")

if __name__ == "__main__":
    test_xcrypto_strategy()