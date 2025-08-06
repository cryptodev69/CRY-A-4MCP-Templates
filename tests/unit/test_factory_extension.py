#!/usr/bin/env python3
"""
Test script for the factory_extension module.

This script tests the create_strategy method added to the StrategyFactory class
by the factory_extension module.
"""

import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_factory_extension')

# Import the necessary components
from src.cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory


def test_create_strategy():
    """Test the create_strategy method of the StrategyFactory class."""
    try:
        # Test with CryptoLLMExtractionStrategy
        logger.info("Testing create_strategy with CryptoLLMExtractionStrategy")
        strategy = StrategyFactory.create_strategy(
            "CryptoLLMExtractionStrategy",
            provider="openai",
            model="gpt-4",
            api_key="test-api-key"
        )
        logger.info(f"Created strategy: {strategy.__class__.__name__}")
        
        # Verify the strategy configuration
        logger.info(f"Provider: {getattr(strategy, 'provider', None)}")
        logger.info(f"Model: {getattr(strategy, 'model', None)}")
        logger.info(f"API Token: {getattr(strategy, 'api_token', None)}")
        
        # Test with another strategy
        logger.info("Testing create_strategy with NFTLLMExtractionStrategy")
        strategy2 = StrategyFactory.create_strategy(
            "NFTLLMExtractionStrategy",
            provider="anthropic",
            model="claude-3-opus",
            api_key="test-anthropic-key"
        )
        logger.info(f"Created strategy: {strategy2.__class__.__name__}")
        
        # Verify the strategy configuration
        logger.info(f"Provider: {getattr(strategy2, 'provider', None)}")
        logger.info(f"Model: {getattr(strategy2, 'model', None)}")
        logger.info(f"API Token: {getattr(strategy2, 'api_token', None)}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing create_strategy: {e}")
        return False


def main():
    """Run the tests."""
    logger.info("Starting factory_extension tests")
    
    # Test create_strategy
    if test_create_strategy():
        logger.info("create_strategy test passed")
    else:
        logger.error("create_strategy test failed")


if __name__ == "__main__":
    main()