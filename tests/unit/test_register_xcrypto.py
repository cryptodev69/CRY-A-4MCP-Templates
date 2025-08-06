#!/usr/bin/env python3
"""
Test script to directly import and register the XCryptoHunterLLMExtractionStrategy.
"""

import os
import sys
import logging

# Add the src directory to the Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

from cry_a_4mcp.crawl4ai.extraction_strategies.registry import StrategyRegistry
from cry_a_4mcp.crawl4ai.extraction_strategies.crypto.xcryptohunter_llm import XCryptoHunterLLMExtractionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_register_xcrypto')

def test_register_xcrypto():
    """Test registering the XCryptoHunterLLMExtractionStrategy directly."""
    # Register the strategy directly
    StrategyRegistry.register()(XCryptoHunterLLMExtractionStrategy)
    
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

if __name__ == "__main__":
    test_register_xcrypto()