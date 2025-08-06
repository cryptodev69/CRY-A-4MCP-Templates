#!/usr/bin/env python3
"""
Test script to run the strategy manager UI to verify that all strategies are visible.
"""

import os
import sys
import logging

# Add the src directory to the Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

from cry_a_4mcp.crawl4ai.extraction_strategies.ui.strategy_manager import StrategyManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_strategy_ui')

def main():
    """Run the strategy manager UI."""
    logger.info("Starting strategy manager UI...")
    manager = StrategyManager()
    manager.run()

if __name__ == "__main__":
    main()