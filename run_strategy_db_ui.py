#!/usr/bin/env python
"""
Run the Strategy Manager UI with database support.

This script launches the Streamlit-based UI for managing extraction strategies
using a database backend for storing and retrieving strategy data.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import the StrategyManagerDBUI class
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.strategy_manager_db import StrategyManagerDBUI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run the Strategy Manager UI application with database support."""
    try:
        # Create and run the UI
        ui = StrategyManagerDBUI()
        ui.run()
    except Exception as e:
        logger.exception(f"Error running Strategy Manager UI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()