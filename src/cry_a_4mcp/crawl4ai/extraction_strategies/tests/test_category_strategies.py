#!/usr/bin/env python3
"""
Test script for verifying the category-based strategy organization.

This script tests that strategies are properly loaded from category subdirectories.
"""

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import the registry
from cry_a_4mcp.crawl4ai.extraction_strategies.registry import StrategyRegistry

def test_category_strategies():
    """Test that strategies are properly loaded from category subdirectories."""
    # Get all registered strategies
    strategies = StrategyRegistry.get_all_strategies()
    
    # Get all categories
    categories = StrategyRegistry.get_categories()
    
    logger.info(f"Found {len(strategies)} registered strategies")
    logger.info(f"Found {len(categories)} categories: {categories}")
    
    # Check each category
    for category in categories:
        category_strategies = StrategyRegistry.get_strategies_by_category(category)
        logger.info(f"Category '{category}' has {len(category_strategies)} strategies")
        
        # List the strategies in this category
        for name, strategy_class in category_strategies.items():
            logger.info(f"  - {name}: {strategy_class.__module__}")

if __name__ == "__main__":
    test_category_strategies()