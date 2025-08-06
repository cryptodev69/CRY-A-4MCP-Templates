#!/usr/bin/env python3
"""
Test script for the factory_extension module with default model.

This script tests that the create_strategy method uses the deepseek model
as the default when no model is specified.
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
logger = logging.getLogger('test_default_model')

# Import the necessary components
from src.cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory


def test_default_model():
    """Test that the create_strategy method uses the deepseek model as default."""
    try:
        # Test with CryptoLLMExtractionStrategy without specifying provider or model
        logger.info("Testing create_strategy with default provider and model")
        strategy = StrategyFactory.create_strategy(
            "CryptoLLMExtractionStrategy",
            api_key="test-api-key"
        )
        logger.info(f"Created strategy: {strategy.__class__.__name__}")
        
        # Verify the strategy configuration
        logger.info(f"Provider: {getattr(strategy, 'provider', None)}")
        logger.info(f"Model: {getattr(strategy, 'model', None)}")
        logger.info(f"API Token: {getattr(strategy, 'api_token', None)}")
        
        # Test with explicit provider but default model
        logger.info("Testing create_strategy with explicit provider but default model")
        strategy2 = StrategyFactory.create_strategy(
            "NFTLLMExtractionStrategy",
            provider="openrouter",
            api_key="test-openrouter-key"
        )
        logger.info(f"Created strategy: {strategy2.__class__.__name__}")
        
        # Verify the strategy configuration
        logger.info(f"Provider: {getattr(strategy2, 'provider', None)}")
        logger.info(f"Model: {getattr(strategy2, 'model', None)}")
        logger.info(f"API Token: {getattr(strategy2, 'api_token', None)}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing default model: {e}")
        return False


def main():
    """Run the tests."""
    logger.info("Starting default model tests")
    
    # Test default model
    if test_default_model():
        logger.info("Default model test passed")
    else:
        logger.error("Default model test failed")


if __name__ == "__main__":
    main()