#!/usr/bin/env python
"""
Run the Improved Strategy Management UI.

This script launches the Streamlit-based UI for managing extraction strategies
using the improved strategy manager that avoids module cache issues.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print("✅ Successfully loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed. Environment variables will only be loaded from the system.")
    print("   To install: pip install python-dotenv")

# Import the show_improved_strategy_management function
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.improved_strategy_ui import show_improved_strategy_management

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run the Improved Strategy Management UI application."""
    try:
        # Run the improved strategy management UI
        show_improved_strategy_management()
    except Exception as e:
        logger.exception(f"Error running Improved Strategy Management UI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()