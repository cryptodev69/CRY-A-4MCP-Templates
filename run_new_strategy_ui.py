#!/usr/bin/env python3
"""
Run script for the new strategy management UI.

This script launches the completely rebuilt strategy management UI
that fixes all issues with edit and delete functionality.
"""

import streamlit as st
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the new strategy UI
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui import show_new_strategy_management


def main():
    """Main entry point for the new strategy management UI."""
    # Set page config
    st.set_page_config(
        page_title="New Strategy Management",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton button {
        width: 100%;
    }
    .stExpander {
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show the UI
    try:
        show_new_strategy_management()
    except Exception as e:
        st.error(f"Error loading the new strategy management UI: {e}")
        logger.exception("Error in new strategy management UI")


if __name__ == "__main__":
    main()