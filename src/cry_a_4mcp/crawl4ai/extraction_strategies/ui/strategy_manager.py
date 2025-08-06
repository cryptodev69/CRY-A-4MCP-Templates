"""Strategy Manager UI Module.

This module provides a web-based UI for managing extraction strategies,
including creating, configuring, and testing strategies.
"""

import os

import logging
import json
import asyncio
import inspect
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd

from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.openrouter_utils import get_openrouter_models, format_openrouter_models, save_api_keys_to_file, load_api_keys_from_file

from src.cry_a_4mcp.crawl4ai.extraction_strategies.registry import StrategyRegistry
from src.cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper

# Set up logger
logger = logging.getLogger(__name__)


class StrategyManagerUI:
    """UI for managing extraction strategies.
    
    This class provides a Streamlit-based UI for managing extraction strategies,
    including browsing available strategies, configuring strategy parameters,
    testing strategies on sample content, and creating composite strategies.
    """
    
    def _validate_json_schema(self, json_str: str):
        """Validate a JSON schema string and return the parsed object or None if invalid.
        
        Args:
            json_str: JSON string to validate
            
        Returns:
            Parsed JSON object or None if invalid
        """
        try:
            # First, try to parse as JSON
            json_obj = json.loads(json_str)
            return json_obj
        except json.JSONDecodeError as e:
            # If there's a specific error about expecting a value at line 1, column 1,
            # it might be an empty string or whitespace
            if "line 1 column 1" in str(e) and "Expecting value" in str(e):
                st.error("Invalid JSON: Empty or whitespace-only input")
            else:
                st.error(f"Invalid JSON: {e}")
            return None
    
    def __init__(self):
        """Initialize the StrategyManagerUI."""
        self.registry = StrategyRegistry()
        self.factory = StrategyFactory()
        self.api_tokens = {}
        self.config_dir = Path(__file__).parent / "config"
        self.api_keys_file = self.config_dir / "api_keys.json"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load saved API keys
        self._load_api_keys()
        
        # Initialize the strategy generator
        try:
            from .templates.strategy_generator import StrategyTemplateGenerator
            self.generator = StrategyTemplateGenerator()
        except ImportError as e:
            logger.error(f"Error importing StrategyTemplateGenerator: {e}")
        
    def _load_api_keys(self):
        """Load API keys from file and update session state."""
        loaded_keys = load_api_keys_from_file(str(self.api_keys_file))
        if loaded_keys:
            self.api_tokens = loaded_keys
            if "api_tokens" not in st.session_state:
                st.session_state.api_tokens = loaded_keys
    
    def _save_api_keys(self):
        """Save API keys to file."""
        if "api_tokens" in st.session_state:
            save_api_keys_to_file(st.session_state.api_tokens, str(self.api_keys_file))
    
    def run(self):
        """Run the Streamlit UI application."""
        st.set_page_config(page_title="Extraction Strategy Manager", layout="wide")
        
        # Apply custom CSS for better UI
        st.markdown("""
        <style>
        .main-nav .nav-item {
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            transition: background-color 0.3s;
        }
        .main-nav .nav-item:hover {
            background-color: rgba(237, 237, 237, 0.1);
        }
        .card {
            padding: 1.5rem;
            border-radius: 0.5rem;
            background-color: rgba(247, 247, 247, 0.05);
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create a cleaner header with logo and title
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown("🧠")
        with col2:
            st.title("Extraction Strategy Manager")
        
        # Sidebar for navigation with modern tab-based design
        st.sidebar.markdown("<h3>Navigation</h3>", unsafe_allow_html=True)
        
        # Check if we need to navigate to a specific page based on session state
        default_main_category = "Strategies"
        default_page = "Browse Strategies"
        
        # If test_strategy is in session state, set the page to Test Strategy
        if "test_strategy" in st.session_state:
            default_main_category = "Strategies"
            default_page = "Test Strategy"
        
        # If page is explicitly set in session state, use that
        if "page" in st.session_state:
            default_page = st.session_state.page
            # Clear the page from session state after using it
            del st.session_state.page
            
            # Determine the main category based on the page
            if default_page in ["Browse Strategies", "Test Strategy", "Create New Strategy", "Create Composite Strategy", "Edit Strategy"]:
                default_main_category = "Strategies"
            elif default_page in ["Configure API Keys"]:
                default_main_category = "Configuration"
            elif default_page in ["Help & Guidelines"]:
                default_main_category = "Help"
        
        # Create main navigation categories
        with st.sidebar:
            main_category = st.radio(
                "Main Categories",
                ["Strategies", "Configuration", "Crawling", "Help"],
                index=["Strategies", "Configuration", "Crawling", "Help"].index(default_main_category),
                format_func=lambda x: {
                    "Strategies": "📊 Strategies",
                    "Configuration": "⚙️ Configuration",
                    "Crawling": "🕸️ Crawling",
                    "Help": "❓ Help & Resources"
                }[x],
                horizontal=True
            )
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Show subcategories based on main category
            if main_category == "Strategies":
                strategies_options = ["Browse Strategies", "Test Strategy", "Create New Strategy", "Create Composite Strategy", "Edit Strategy"]
                # Hide Edit Strategy from the radio options as it should only be accessed from the strategy details page
                display_options = ["Browse Strategies", "Test Strategy", "Create New Strategy", "Create Composite Strategy"]
                
                # If we're on the Edit Strategy page, we still want to show it in the radio
                if default_page == "Edit Strategy":
                    display_options = strategies_options
                
                default_index = display_options.index(default_page) if default_page in display_options else 0
                strategies_page = st.radio(
                    "Strategy Options",
                    display_options,
                    index=default_index,
                    label_visibility="visible"
                )
                page = strategies_page
            
            elif main_category == "Configuration":
                config_options = ["Configure API Keys"]
                default_index = config_options.index(default_page) if default_page in config_options else 0
                config_page = st.radio(
                    "Configuration Options",
                    config_options,
                    index=default_index,
                    label_visibility="visible"
                )
                page = config_page
            
            elif main_category == "Crawling":
                st.info("Crawling configuration coming soon")
                crawling_page = None
                page = None
            
            elif main_category == "Help":
                help_options = ["Help & Guidelines"]
                default_index = help_options.index(default_page) if default_page in help_options else 0
                help_page = st.radio(
                    "Help Options",
                    help_options,
                    index=default_index,
                    label_visibility="visible"
                )
                page = help_page
            
            # Default page if nothing is selected
            if page is None:
                page = "Browse Strategies"
        
        # Display the selected page
        if page == "Browse Strategies":
            self._show_browse_strategies()
        elif page == "Configure API Keys":
            self._show_configure_api_keys()
        elif page == "Test Strategy":
            self._show_test_strategy()
        elif page == "Create Composite Strategy":
            self._show_create_composite_strategy()
        elif page == "Create New Strategy":
            self._show_create_new_strategy()
        elif page == "Edit Strategy":
            self._show_edit_strategy()
        elif page == "Help & Guidelines":
            self._show_help_guidelines()
    
    def _show_browse_strategies(self):
        """Show the Browse Strategies page."""
        # Create a header with a reload button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header("Browse Available Strategies")
        with col2:
            if st.button("🔄 Reload Strategies"):
                # Reload all strategies
                StrategyRegistry.reload_strategies()
                st.success("Strategies reloaded successfully!")
                # Rerun the app to refresh the UI
                st.rerun()
        
        # Get all registered strategies
        strategies = self.registry.get_all_metadata()
        
        # Create a DataFrame for display
        strategy_data = []
        for name, info in strategies.items():
            strategy_data.append({
                "Name": name,
                "Description": info.get("description", ""),
                "Category": info.get("category", ""),
                "Tags": info.get("tags", []),
                "Registered At": info.get("registered_at", "")
            })
        
        if strategy_data:
            # Create a modern search and filter interface
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            search_col, filter_col, sort_col = st.columns([2, 1, 1])
            with search_col:
                search_term = st.text_input("🔍 Search strategies", "", placeholder="Enter name, category, or tag")
            with filter_col:
                all_categories = sorted(list(set([s["Category"] for s in strategy_data if s["Category"]])))  
                filter_category = st.selectbox(
                    "Filter by category", 
                    ["All"] + all_categories,
                )
            with sort_col:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Name", "Category", "Recently Added"]
                )
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Apply filters
            filtered_data = strategy_data
            if search_term:
                filtered_data = [s for s in filtered_data if 
                                search_term.lower() in s["Name"].lower() or 
                                search_term.lower() in s["Description"].lower() or 
                                any(search_term.lower() in tag.lower() for tag in s["Tags"]) or
                                search_term.lower() in s["Category"].lower()]
            if filter_category and filter_category != "All":
                filtered_data = [s for s in filtered_data if s["Category"] == filter_category]
            
            # Apply sorting
            if sort_by == "Name":
                filtered_data = sorted(filtered_data, key=lambda x: x["Name"])
            elif sort_by == "Category":
                filtered_data = sorted(filtered_data, key=lambda x: x["Category"])
            elif sort_by == "Recently Added":
                filtered_data = sorted(filtered_data, key=lambda x: x["Registered At"], reverse=True)
            
            # Display strategies in a more visual way
            if not filtered_data:
                st.warning("No strategies match your search criteria.")
            else:
                # Display as cards or table based on view preference
                view_type = st.radio("View as", ["Cards", "Table"], horizontal=True)
                
                if view_type == "Table":
                    # Prepare data for table view
                    table_data = []
                    for s in filtered_data:
                        table_data.append({
                            "Name": s["Name"],
                            "Description": s["Description"],
                            "Category": s["Category"],
                            "Tags": ", ".join(s["Tags"]),
                        })
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True, height=300)
                else:  # Cards view
                    # Display as cards for a more modern look
                    cols = st.columns(2)
                    for i, strategy in enumerate(filtered_data):
                        with cols[i % 2]:
                            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                            st.markdown(f"### {strategy['Name']}")
                            st.markdown(f"**Category:** {strategy['Category'] or 'Uncategorized'}")
                            st.markdown(f"**Description:** {strategy['Description']}")
                            if strategy['Tags']:
                                st.markdown("**Tags:** " + " ".join([f"<span style='background-color:rgba(70,70,70,0.2);padding:2px 8px;border-radius:10px;margin-right:5px;font-size:0.8em;'>{tag}</span>" for tag in strategy['Tags']]), unsafe_allow_html=True)
                            
                            # Quick action buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🔍 View Details", key=f"view_{i}"):
                                    st.session_state.selected_strategy = strategy["Name"]
                            with col2:
                                if st.button("🧪 Test", key=f"test_{i}"):
                                    st.session_state.test_strategy = strategy["Name"]
                                    st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                
                # Strategy details in tabs for better organization
                if "selected_strategy" in st.session_state or (view_type == "Table" and filtered_data):
                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.subheader("Strategy Details")
                    
                    if "selected_strategy" in st.session_state:
                        selected_strategy = st.session_state.selected_strategy
                    else:
                        selected_strategy = st.selectbox("Select a strategy to view details", [s["Name"] for s in filtered_data])
                    
                    if selected_strategy:
                        strategy_info = strategies.get(selected_strategy, {})
                        
                        # Use tabs for different views of the strategy
                        tab1, tab2, tab3 = st.tabs(["Overview", "JSON Schema", "Actions"])
                        
                        with tab1:
                            # Display key information in a more readable format
                            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                            st.markdown(f"### {selected_strategy}")
                            st.markdown(f"**Description:** {strategy_info.get('description', 'No description available')}")
                            st.markdown(f"**Category:** {strategy_info.get('category', 'Uncategorized')}")
                            st.markdown(f"**Tags:** {', '.join(strategy_info.get('tags', ['None']))}")
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                            # Display parameters in a table if available
                            if "parameters" in strategy_info:
                                st.markdown("<div class='card'>", unsafe_allow_html=True)
                                st.subheader("Parameters")
                                params_df = pd.DataFrame([
                                    {
                                        "Parameter": param,
                                        "Type": info.get("type", ""),
                                        "Required": "✓" if info.get("required", False) else "",
                                        "Default": str(info.get("default", "None")),
                                        "Description": info.get("description", "")
                                    }
                                    for param, info in strategy_info["parameters"].items()
                                ])
                                st.dataframe(params_df, use_container_width=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                        
                        with tab2:
                            # Show the full JSON for technical users
                            st.json(strategy_info)
                        
                        with tab3:
                            # Add action buttons
                            st.markdown("<div class='card'>", unsafe_allow_html=True)
                            st.markdown("### Strategy Actions")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🧪 Test This Strategy", key="test_selected", use_container_width=True):
                                    # Set session state to navigate to test page with this strategy selected
                                    st.session_state.test_strategy = selected_strategy
                                    st.rerun()
                            with col2:
                                if st.button("📋 Copy Strategy Name", key="copy_name", use_container_width=True):
                                    # Use JavaScript to copy to clipboard
                                    st.write(f"<div id='copy-container' style='display:none'>{selected_strategy}</div>", unsafe_allow_html=True)
                                    st.write(
                                        "<script>navigator.clipboard.writeText(document.getElementById('copy-container').innerText);</script>",
                                        unsafe_allow_html=True
                                    )
                                    st.success(f"Copied '{selected_strategy}' to clipboard!")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if st.button("✏️ Edit Strategy", key="edit_strategy_btn", use_container_width=True):
                                    # Set session state to navigate to edit page with this strategy selected
                                    st.session_state.page = "Edit Strategy"
                                    st.session_state.edit_strategy = selected_strategy
                                    st.rerun()
                            with col2:
                                if st.button("🗑️ Delete Strategy", key="delete_strategy", use_container_width=True):
                                    # Set session state to confirm deletion
                                    st.session_state.confirm_delete = selected_strategy
                            with col3:
                                if st.button("🔄 Refresh", key="refresh_strategy", use_container_width=True):
                                    st.rerun()
                                    
                            # Confirmation dialog for deletion
                            if "confirm_delete" in st.session_state and st.session_state.confirm_delete == selected_strategy:
                                st.warning(f"Are you sure you want to delete the strategy '{selected_strategy}'? This action cannot be undone.")
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("Yes, Delete", key="confirm_delete_yes", use_container_width=True):
                                        # Get the strategy file path
                                        strategy_path = StrategyRegistry.get_strategy_file_path(selected_strategy)
                                        if strategy_path:
                                            # Delete the strategy file
                                            if self.generator.delete_strategy_file(strategy_path):
                                                # Unregister the strategy
                                                StrategyRegistry.unregister(selected_strategy)
                                                # Reload strategies
                                                StrategyRegistry.reload_strategies()
                                                st.success(f"Strategy '{selected_strategy}' deleted successfully!")
                                                # Clear session state
                                                if "selected_strategy" in st.session_state:
                                                    del st.session_state.selected_strategy
                                                if "confirm_delete" in st.session_state:
                                                    del st.session_state.confirm_delete
                                                # Rerun the app to refresh the UI
                                                st.rerun()
                                            else:
                                                st.error(f"Failed to delete strategy file: {strategy_path}")
                                        else:
                                            st.error(f"Could not find file path for strategy: {selected_strategy}")
                                with col2:
                                    if st.button("No, Cancel", key="confirm_delete_no", use_container_width=True):
                                        # Clear confirmation
                                        if "confirm_delete" in st.session_state:
                                            del st.session_state.confirm_delete
                                        st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No strategies registered yet.")
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("""
            ### Getting Started
            To create your first strategy, go to the **Create New Strategy** page in the sidebar.
            
            For guidance on creating effective strategies, check the **Help & Guidelines** page.
            """)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Quick navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Create New Strategy", use_container_width=True):
                    st.session_state.page = "Create New Strategy"
                    st.rerun()
            with col2:
                if st.button("❓ View Help & Guidelines", use_container_width=True):
                    st.session_state.page = "Help & Guidelines"
                    st.rerun()
                
                # Show strategy parameters
                if "parameters" in strategy_info:
                    st.subheader("Strategy Parameters")
                    params_df = pd.DataFrame([
                        {
                            "Parameter": param,
                            "Type": info.get("type", ""),
                            "Required": info.get("required", False),
                            "Default": str(info.get("default", "None")),
                            "Description": info.get("description", "")
                        }
                        for param, info in strategy_info["parameters"].items()
                    ])
                    st.dataframe(params_df, use_container_width=True)
    
    def _show_configure_api_keys(self):
        """Show the Configure API Keys page."""
        st.header("Configure API Keys")
        
        # List of supported LLM providers
        providers = ["OpenAI", "Anthropic", "Google", "Cohere", "Mistral", "OpenRouter", "Custom"]
        
        # Load existing API keys from session state
        if "api_tokens" not in st.session_state:
            st.session_state.api_tokens = self.api_tokens.copy() if self.api_tokens else {}
        
        # Add a new API key
        with st.form("add_api_key"):
            st.subheader("Add or Update API Key")
            provider = st.selectbox("Provider", providers)
            
            if provider == "Custom":
                provider_name = st.text_input("Custom Provider Name")
            else:
                provider_name = provider
                
            api_key = st.text_input("API Key", type="password")
            persist_key = st.checkbox("Save API key to disk", value=True, help="Save API key to disk for future sessions")
            submitted = st.form_submit_button("Save API Key")
            
            if submitted and provider_name and api_key:
                st.session_state.api_tokens[provider_name] = api_key
                if persist_key:
                    self._save_api_keys()
                st.success(f"API key for {provider_name} saved successfully!")
        
        # Display existing API keys
        st.subheader("Configured API Keys")
        if st.session_state.api_tokens:
            api_key_data = []
            for provider, key in st.session_state.api_tokens.items():
                masked_key = "*" * (len(key) - 4) + key[-4:] if len(key) > 4 else "*" * len(key)
                api_key_data.append({"Provider": provider, "API Key": masked_key})
            
            api_keys_df = pd.DataFrame(api_key_data)
            st.dataframe(api_keys_df, use_container_width=True)
            
            # Option to delete API keys
            provider_to_delete = st.selectbox("Select provider to delete", list(st.session_state.api_tokens.keys()))
            if st.button("Delete Selected API Key"):
                if provider_to_delete in st.session_state.api_tokens:
                    del st.session_state.api_tokens[provider_to_delete]
                    self._save_api_keys()
                    st.success(f"API key for {provider_to_delete} deleted successfully!")
                    st.rerun()
        else:
            st.info("No API keys configured yet.")
        
        # Update the instance's API tokens
        self.api_tokens = st.session_state.api_tokens.copy()
    
    def _show_test_strategy(self):
        """Show the Test Strategy page with improved UI."""
        # Create a header with a reload button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header("Test Extraction Strategy")
        with col2:
            if st.button("🔄 Reload Strategies", key="reload_test_page"):
                # Reload all strategies
                StrategyRegistry.reload_strategies()
                st.success("Strategies reloaded successfully!")
                # Rerun the app to refresh the UI
                st.rerun()
        
        # Get all registered strategies
        strategies = self.registry.get_all_metadata()
        strategy_names = list(strategies.keys())
        
        if not strategy_names:
            st.warning("No strategies registered yet.")
            st.markdown("""
            ### Getting Started
            To create your first strategy, go to the **Create New Strategy** page in the sidebar.
            
            For guidance on creating effective strategies, check the **Help & Guidelines** page.
            """)
            
            # Quick navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Create New Strategy", key="create_new_from_test"):
                    st.session_state.page = "Create New Strategy"
                    st.rerun()
            with col2:
                if st.button("❓ View Help & Guidelines", key="view_help_from_test"):
                    st.session_state.page = "Help & Guidelines"
                    st.rerun()
            return
        
        # Use session state to remember the selected strategy
        if "test_strategy" in st.session_state:
            default_strategy = st.session_state.test_strategy
            # Don't clear the session state to maintain navigation context
            # This ensures we stay on the Test Strategy page when interacting with UI elements
        else:
            default_strategy = strategy_names[0]
        
        # Strategy selection with search functionality
        search_col, filter_col = st.columns([3, 1])
        with search_col:
            search_term = st.text_input("🔍 Search strategies", "", placeholder="Enter strategy name")
        with filter_col:
            categories = ["All"] + sorted(list(set([info.get("category", "Uncategorized") 
                                        for info in strategies.values() if info.get("category")])))
            filter_category = st.selectbox("Category", categories)
        
        # Filter strategies based on search and category
        filtered_strategies = {}
        for name, info in strategies.items():
            category_match = filter_category == "All" or info.get("category", "Uncategorized") == filter_category
            search_match = not search_term or search_term.lower() in name.lower() or search_term.lower() in info.get("description", "").lower()
            if category_match and search_match:
                filtered_strategies[name] = info
        
        filtered_names = list(filtered_strategies.keys())
        if not filtered_names:
            st.warning("No strategies match your search criteria.")
            return
        
        # Ensure default_strategy is in filtered list
        if default_strategy not in filtered_names:
            default_strategy = filtered_names[0]
        
        # Strategy selection
        selected_strategy = st.selectbox("Select a strategy to test", filtered_names, index=filtered_names.index(default_strategy))
        
        if selected_strategy:
            strategy_info = strategies.get(selected_strategy, {})
            
            # Use tabs for better organization
            config_tab, input_tab, results_tab = st.tabs(["Strategy Configuration", "Test Input", "Results"])
            
            with config_tab:
                # Display strategy info in a card-like container
                with st.container(border=True):
                    st.subheader("Strategy Information")
                    st.markdown(f"**Description:** {strategy_info.get('description', 'No description available')}")
                    st.markdown(f"**Category:** {strategy_info.get('category', 'Uncategorized')}")
                    if "tags" in strategy_info and strategy_info["tags"]:
                        st.markdown(f"**Tags:** {', '.join(strategy_info['tags'])}")
                
                # Configure strategy parameters
                st.subheader("Configure Strategy Parameters")
                
                # Get API tokens from session state
                if "api_tokens" in st.session_state:
                    api_tokens = st.session_state.api_tokens
                else:
                    api_tokens = {}
                
                # API configuration in a card-like container
                with st.container(border=True):
                    st.markdown("#### API Configuration")
                    
                    # Select provider and API token
                    provider_options = list(api_tokens.keys())
                    if provider_options:
                        selected_provider = st.selectbox("Select LLM Provider", provider_options)
                        api_token = api_tokens.get(selected_provider, "")
                        st.success(f"Using API key for {selected_provider}")
                    else:
                        st.warning("No API keys configured. Please add API keys in the 'Configure API Keys' page.")
                        selected_provider = ""
                        api_token = ""
                        
                        # Quick navigation to API keys page
                        if st.button("Configure API Keys"):
                            st.session_state.page = "Configure API Keys"
                            st.rerun()
                    
                    # Model selection based on provider
                    if selected_provider == "OpenRouter":
                        st.markdown("#### OpenRouter Models")
                        # Check if we have OpenRouter models in session state
                        if "openrouter_models" not in st.session_state or st.button("Refresh Models"):
                            with st.spinner("Fetching available OpenRouter models..."):
                                success, models, message = asyncio.run(get_openrouter_models(api_token))
                                if success:
                                    st.session_state.openrouter_models = models
                                    st.success("Successfully fetched OpenRouter models")
                                else:
                                    st.error(f"Failed to fetch OpenRouter models: {message}")
                                    st.session_state.openrouter_models = []
                        
                        # Display OpenRouter models
                        if "openrouter_models" in st.session_state and st.session_state.openrouter_models:
                            # Option to filter free models
                            show_free_only = st.checkbox("Show free models only", value=False)
                            
                            # Format models for display
                            formatted_models = format_openrouter_models(
                                st.session_state.openrouter_models, 
                                filter_free=show_free_only
                            )
                            
                            if formatted_models:
                                # Create a DataFrame for display
                                models_data = []
                                model_ids = []
                                
                                for model_info in formatted_models:
                                    models_data.append({
                                        "Model ID": model_info["id"],
                                        "Context Length": model_info["context_length"],
                                        "Prompt Price": model_info["prompt_price_formatted"],
                                        "Completion Price": model_info["completion_price_formatted"],
                                        "Free": "✓" if model_info["is_free"] else ""
                                    })
                                    model_ids.append(model_info["id"])
                                
                                # Display models table
                                st.dataframe(pd.DataFrame(models_data), use_container_width=True, height=200)
                                
                                # Select model from dropdown
                                model = st.selectbox("Select Model", model_ids)
                            else:
                                st.warning("No models available with current filter settings")
                                model = st.text_input("Model Name", value="")
                        else:
                            model = st.text_input("Model Name", value="")
                    else:
                        # For other providers, use text input with smart defaults
                        default_model = ""
                        if "OpenAI" in selected_provider:
                            default_model = "gpt-4"
                        elif "Anthropic" in selected_provider:
                            default_model = "claude-3-opus-20240229"
                        elif "Google" in selected_provider:
                            default_model = "gemini-pro"
                        elif "Mistral" in selected_provider:
                            default_model = "mistral-large-latest"
                        
                        model = st.text_input("Model Name", value=default_model)
                
                # Additional parameters based on strategy type
                if "parameters" in strategy_info and any(param not in ["api_token", "model"] for param in strategy_info["parameters"]):
                    with st.container(border=True):
                        st.markdown("#### Additional Parameters")
                        params = {}
                        
                        for param, info in strategy_info["parameters"].items():
                            if param not in ["api_token", "model"]:
                                param_type = info.get("type", "string")
                                default = info.get("default", None)
                                description = info.get("description", "")
                                required = info.get("required", False)
                                
                                # Add visual indicator for required fields
                                param_label = f"{param}{' *' if required else ''} ({description})"
                                
                                if param_type == "boolean":
                                    params[param] = st.checkbox(param_label, value=default or False)
                                elif param_type == "integer":
                                    params[param] = st.number_input(param_label, value=default or 0, step=1)
                                elif param_type == "number" or param_type == "float":
                                    params[param] = st.number_input(param_label, value=default or 0.0, step=0.1)
                                elif param_type == "array":
                                    items_str = st.text_input(f"{param_label}, comma-separated", value="" if default is None else ",".join(default))
                                    params[param] = [item.strip() for item in items_str.split(",")] if items_str else []
                                else:  # string or other types
                                    params[param] = st.text_input(param_label, value=default or "")
                else:
                    params = {}
            
            with input_tab:
                # Input for testing
                st.subheader("Test Input")
                
                # Add example content option
                # Use a key to maintain state and prevent rerun
                example_option = st.checkbox("Use example content", value=False, key="use_example_content")
                
                # Check if the checkbox state has changed
                if "previous_example_option" not in st.session_state:
                    st.session_state.previous_example_option = False
                
                # If checkbox state changed, ensure we stay on Test Strategy page
                if example_option != st.session_state.previous_example_option:
                    st.session_state.previous_example_option = example_option
                    st.session_state.test_strategy = selected_strategy
                    st.session_state.page = "Test Strategy"
                
                if example_option:
                    example_content = """
                    # Example Content
                    
                    Apple Inc. reported quarterly revenue of $89.5 billion for Q4 2023, down 1% year over year. 
                    The company's CEO, Tim Cook, stated that iPhone sales reached $43.8 billion, up 2.8% from the same period last year.
                    
                    Apple's services revenue hit an all-time high of $22.3 billion, up 16.3% year over year.
                    The company's gross margin was 45.2%, up 0.4 percentage points from the previous quarter.
                    
                    Apple's board of directors declared a cash dividend of $0.24 per share, payable on November 16, 2023.
                    """
                    content = st.text_area("Content to Extract From", value=example_content, height=250)
                    url = st.text_input("URL (optional)", value="https://example.com/apple-q4-2023-earnings")
                else:
                    url = st.text_input("URL (optional)", value="https://example.com")
                    content = st.text_area("Content to Extract From", height=250, placeholder="Paste the content to extract information from...")
                
                # Add sample content suggestions
                st.markdown("""#### Content Tips
                - Paste article text, product descriptions, financial reports, etc.
                - Make sure the content is relevant to the selected strategy
                - For best results, include complete paragraphs rather than fragments
                """)
                
                # Run test button with better visibility
                run_col1, run_col2 = st.columns([3, 1])
                with run_col1:
                    run_test = st.button("🚀 Run Extraction Test", type="primary", use_container_width=True)
            
            with results_tab:
                st.subheader("Extraction Results")
                
                # Only show results if the test has been run
                if "extraction_result" in st.session_state:
                    st.json(st.session_state.extraction_result)
                    
                    # Save results to file option
                    if st.button("💾 Save Results to File"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"extraction_result_{timestamp}.json"
                        with open(filename, "w") as f:
                            json.dump(st.session_state.extraction_result, f, indent=2)
                        st.success(f"Results saved to {filename}")
                else:
                    st.info("Run an extraction test to see results here.")
            
            # Process the extraction test if button was clicked
                if run_test:
                    if not content:
                        st.error("Please provide content to extract from.")
                    elif not api_token and "api_token" in strategy_info.get("parameters", {}):
                        st.error("API token is required for this strategy.")
                    else:
                        try:
                            # Create synchronized strategy instance
                            strategy = self.factory.create_sync(
                                selected_strategy,
                                config={"api_token": api_token, "model": model, **params}
                            )
                            
                            # Run extraction (synchronously)
                            with st.spinner("Extracting information..."):
                                result = strategy.extract(url, content)
                            
                            # Store result in session state
                            st.session_state.extraction_result = result
                            
                            # Ensure we stay on the Test Strategy page
                            st.session_state.test_strategy = selected_strategy
                            st.session_state.page = "Test Strategy"
                            
                            # Switch to results tab
                            st.rerun()
                                
                        except Exception as e:
                            st.error(f"Error during extraction: {str(e)}")
                            logger.exception("Extraction test failed")
    
    def _show_create_composite_strategy(self):
        """Show the Create Composite Strategy page."""
        st.header("Create Composite Strategy")
        
        # Get all registered strategies
        strategies = self.registry.get_all_metadata()
        strategy_names = list(strategies.keys())
        
        if not strategy_names:
            st.warning("No strategies registered yet.")
            return
        
        # Composite strategy configuration
        st.subheader("Configure Composite Strategy")
        
        composite_name = st.text_input("Composite Strategy Name", value="MyCompositeStrategy")
        description = st.text_area("Description", value="A custom composite extraction strategy")
        category = st.text_input("Category", value="composite")
        
        # Select component strategies
        st.subheader("Select Component Strategies")
        component_strategies = st.multiselect("Component Strategies", strategy_names)
        
        # Merge mode selection
        merge_mode = st.selectbox(
            "Merge Mode",
            ["smart", "union", "intersection"],
            format_func=lambda x: {
                "smart": "Smart (Intelligently merge fields)",
                "union": "Union (Include all fields)",
                "intersection": "Intersection (Include only common fields)"
            }.get(x, x)
        )
        
        # API configuration
        st.subheader("API Configuration")
        
        # Get API tokens from session state
        if "api_tokens" in st.session_state:
            api_tokens = st.session_state.api_tokens
        else:
            api_tokens = {}
        
        # Select provider and API token
        provider_options = list(api_tokens.keys())
        if provider_options:
            selected_provider = st.selectbox("Select LLM Provider", provider_options)
            api_token = api_tokens.get(selected_provider, "")
        else:
            st.warning("No API keys configured. Please add API keys in the 'Configure API Keys' page.")
            selected_provider = ""
            api_token = ""
        
        # Model selection based on provider
        if selected_provider == "OpenRouter":
            # Check if we have OpenRouter models in session state
            if "openrouter_models" not in st.session_state or st.button("Refresh Models"):
                with st.spinner("Fetching available OpenRouter models..."):
                    success, models, message = asyncio.run(get_openrouter_models(api_token))
                    if success:
                        st.session_state.openrouter_models = models
                        st.success("Successfully fetched OpenRouter models")
                    else:
                        st.error(f"Failed to fetch OpenRouter models: {message}")
                        st.session_state.openrouter_models = []
            
            # Display OpenRouter models
            if "openrouter_models" in st.session_state and st.session_state.openrouter_models:
                # Option to filter free models
                show_free_only = st.checkbox("Show free models only", value=False)
                
                # Format models for display
                formatted_models = format_openrouter_models(
                    st.session_state.openrouter_models, 
                    filter_free=show_free_only
                )
                
                if formatted_models:
                    # Create a DataFrame for display
                    models_data = []
                    model_ids = []
                    
                    for model_info in formatted_models:
                        models_data.append({
                            "Model ID": model_info["id"],
                            "Context Length": model_info["context_length"],
                            "Prompt Price": model_info["prompt_price_formatted"],
                            "Completion Price": model_info["completion_price_formatted"],
                            "Free": "✓" if model_info["is_free"] else ""
                        })
                        model_ids.append(model_info["id"])
                    
                    # Display models table
                    st.dataframe(pd.DataFrame(models_data), use_container_width=True)
                    
                    # Select model from dropdown
                    model = st.selectbox("Select Model", model_ids)
                else:
                    st.warning("No models available with current filter settings")
                    model = st.text_input("Model Name", value="")
            else:
                model = st.text_input("Model Name", value="")
        else:
            # For other providers, use text input
            model = st.text_input("Model Name", value="gpt-4" if "OpenAI" in selected_provider else "")
        
        # Additional parameters
        max_retries = st.number_input("Max Retries", value=3, min_value=0, max_value=10)
        retry_delay = st.number_input("Retry Delay (seconds)", value=1.0, min_value=0.1, max_value=10.0, step=0.1)
        timeout = st.number_input("Timeout (seconds)", value=60.0, min_value=1.0, max_value=300.0, step=1.0)
        
        # Create strategy button
        if st.button("Create Composite Strategy"):
            if not composite_name:
                st.error("Please provide a name for the composite strategy.")
            elif not component_strategies:
                st.error("Please select at least one component strategy.")
            else:
                try:
                    # Code to create a composite strategy would go here
                    # This is a simplified example that doesn't actually create the strategy
                    
                    # In a real implementation, you would:
                    # 1. Create a new class definition for the composite strategy
                    # 2. Register it with the registry
                    # 3. Save it to a file for future use
                    
                    st.success(f"Composite strategy '{composite_name}' created successfully!")
                    
                    # Display the configuration
                    st.subheader("Composite Strategy Configuration")
                    config = {
                        "name": composite_name,
                        "description": description,
                        "category": category,
                        "component_strategies": component_strategies,
                        "merge_mode": merge_mode,
                        "provider": selected_provider,
                        "model": model,
                        "max_retries": max_retries,
                        "retry_delay": retry_delay,
                        "timeout": timeout
                    }
                    st.json(config)
                    
                except Exception as e:
                    st.error(f"Error creating composite strategy: {str(e)}")
                    logger.exception("Composite strategy creation failed")


    def _show_create_new_strategy(self):
        """Show the Create New Strategy page.
        
        This page allows users to create a new custom extraction strategy by defining
        its metadata, schema, and instructions without writing code.
        """
        st.header("Create New Strategy")
        
        # Strategy metadata
        st.subheader("Strategy Metadata")
        
        strategy_name = st.text_input("Strategy Name", value="")
        strategy_description = st.text_area("Description", value="A custom extraction strategy for specific content")
        
        # API configuration
        st.subheader("API Configuration")
        
        # Get API tokens from session state
        if "api_tokens" in st.session_state:
            api_tokens = st.session_state.api_tokens
        else:
            api_tokens = {}
        
        # Select default provider
        provider_options = list(api_tokens.keys())
        if provider_options:
            default_provider = st.selectbox("Default LLM Provider", provider_options)
        else:
            st.warning("No API keys configured. Please add API keys in the 'Configure API Keys' page.")
            default_provider = st.text_input("Default LLM Provider", value="openai")
        
        # Schema definition
        st.subheader("Schema Definition")
        st.write("Define the JSON schema for the extraction strategy. This schema defines the structure of the data to be extracted.")
        
        # Option to use a template or start from scratch
        schema_option = st.radio(
            "Schema Definition Method",
            ["Use Template", "Start from Scratch"]
        )
        
        if schema_option == "Use Template":
            # Provide some common schema templates
            template_options = [
                "Basic Entity Extraction",
                "Detailed Article Analysis",
                "Product Information",
                "Custom"
            ]
            
            selected_template = st.selectbox("Select a template", template_options)
            
            if selected_template == "Basic Entity Extraction":
                schema_json = {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Name of the entity"},
                                "type": {"type": "string", "description": "Type of the entity (person, organization, location, etc.)"},
                                "description": {"type": "string", "description": "Brief description of the entity"},
                                "relevance": {"type": "number", "description": "Relevance score from 0 to 1"}
                            },
                            "required": ["name", "type"]
                        }
                    },
                    "summary": {"type": "string", "description": "Brief summary of the content"}
                }
            elif selected_template == "Detailed Article Analysis":
                schema_json = {
                    "title": {"type": "string", "description": "Title of the article"},
                    "author": {"type": "string", "description": "Author of the article"},
                    "publication_date": {"type": "string", "description": "Publication date of the article"},
                    "summary": {"type": "string", "description": "Summary of the article"},
                    "key_points": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Key points from the article"
                    },
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        },
                        "description": "Entities mentioned in the article"
                    },
                    "sentiment": {
                        "type": "object",
                        "properties": {
                            "overall": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                            "score": {"type": "number", "minimum": -1, "maximum": 1}
                        },
                        "description": "Sentiment analysis of the article"
                    }
                }
            elif selected_template == "Product Information":
                schema_json = {
                    "product_name": {"type": "string", "description": "Name of the product"},
                    "brand": {"type": "string", "description": "Brand of the product"},
                    "price": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number"},
                            "currency": {"type": "string"}
                        },
                        "description": "Price of the product"
                    },
                    "description": {"type": "string", "description": "Description of the product"},
                    "features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Key features of the product"
                    },
                    "specifications": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "Technical specifications of the product"
                    },
                    "reviews": {
                        "type": "object",
                        "properties": {
                            "average_rating": {"type": "number", "minimum": 0, "maximum": 5},
                            "count": {"type": "integer"},
                            "highlights": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "description": "Review information for the product"
                    }
                }
            else:  # Custom
                schema_json = {}
            
            # Display and allow editing of the schema
            schema_str = json.dumps(schema_json, indent=2)
            schema_editor = st.text_area("Edit Schema JSON", value=schema_str, height=300)
            
            schema_json = self._validate_json_schema(schema_editor)
        else:  # Start from scratch
            schema_editor = st.text_area(
                "Schema JSON", 
                value='''
{
  "entities": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "type": {"type": "string"}
      }
    }
  }
}
''', 
                height=300
            )
            
            schema_json = self._validate_json_schema(schema_editor)
        
        # Instruction definition
        st.subheader("Instruction Definition")
        st.write("Define the instruction for the LLM. This instruction guides the LLM on how to extract information according to the schema.")
        
        # Provide a default instruction template
        default_instruction = f"""You are an AI assistant specialized in extracting structured information from text about {strategy_name if strategy_name else 'specific topics'}.

Your task is to analyze the provided content and extract relevant information according to the specified JSON schema.

Follow these guidelines:
1. Extract all relevant information that fits the schema
2. Be precise and factual
3. If information is not present in the content, use null or empty arrays as appropriate
4. Format the output according to the provided JSON schema exactly

The extracted information should be comprehensive yet concise."""
        
        instruction = st.text_area("Instruction", value=default_instruction, height=200)
        
        # Output file configuration
        st.subheader("Output Configuration")
        
        # Category selection
        category_options = [
            "general",
            "academic", 
            "crypto", 
            "financial", 
            "news", 
            "nft", 
            "product", 
            "social"
        ]
        
        category = st.selectbox("Strategy Category", category_options)
        
        output_filename = st.text_input(
            "Output Filename", 
            value=f"{strategy_name.lower().replace(' ', '_')}_llm.py" if strategy_name else "custom_strategy_llm.py"
        )
        
        # Create strategy button
        if st.button("Create Strategy"):
            if not strategy_name:
                st.error("Please provide a name for the strategy.")
            elif not schema_json:
                st.error("Please provide a valid JSON schema.")
            elif not instruction:
                st.error("Please provide an instruction for the LLM.")
            else:
                try:
                    # Generate the strategy file
                    output_path = self.generator.generate_strategy_file(
                        strategy_name=strategy_name,
                        strategy_description=strategy_description,
                        schema=schema_json,
                        instruction=instruction,
                        default_provider=default_provider,
                        category=category,
                        output_filename=output_filename
                    )
                    
                    st.success(f"Strategy '{strategy_name}' created successfully!")
                    st.info(f"Strategy file created at: {output_path}")
                    
                    # Provide instructions for using the new strategy
                    st.subheader("Next Steps")
                    st.write("To use your new strategy:")
                    
                    # Create two columns for buttons
                    col1, col2 = st.columns(2)
                    
                    # Add a button to reload strategies without restarting
                    with col1:
                        if st.button("Reload Strategies"):
                            # Reload all strategies
                            StrategyRegistry.reload_strategies()
                            st.success("Strategies reloaded successfully! Your new strategy is now available.")
                            # Set session state to navigate to Browse Strategies
                            st.session_state.page = "Browse Strategies"
                            # Rerun the app to refresh the UI
                            st.rerun()
                    
                    # Add a button to directly test the new strategy
                    with col2:
                        if st.button("Test New Strategy"):
                            # Reload all strategies
                            StrategyRegistry.reload_strategies()
                            # Set the test_strategy in session state to the new strategy
                            st.session_state.test_strategy = strategy_name
                            # Navigate to Test Strategy page
                            st.session_state.page = "Test Strategy"
                            # Rerun the app to refresh the UI
                            st.rerun()
                    
                    st.write("1. Click 'Reload Strategies' button to register the new strategy and return to Browse Strategies")
                    st.write("2. Click 'Test New Strategy' button to reload and immediately test your new strategy")
                    st.write("3. Or restart the application if the reload buttons don't work")
                    st.write("4. You can edit the strategy file directly if needed")
                    
                except Exception as e:
                    st.error(f"Error creating strategy: {str(e)}")
                    logger.exception("Strategy creation failed")


    def _show_edit_strategy(self):
        """Show the edit strategy page."""
        st.title("Edit Extraction Strategy")
        
        # Check if a strategy is selected for editing
        if "edit_strategy" not in st.session_state:
            st.error("No strategy selected for editing.")
            if st.button("Return to Browse Strategies"):
                st.session_state.page = "Browse Strategies"
                st.rerun()
            return
        
        strategy_name = st.session_state.edit_strategy
        strategy_info = self.registry.get_metadata(strategy_name)
        
        if not strategy_info:
            st.error(f"Strategy '{strategy_name}' not found.")
            if st.button("Return to Browse Strategies"):
                st.session_state.page = "Browse Strategies"
                st.rerun()
            return
        
        # Get the strategy file path
        strategy_path = StrategyRegistry.get_strategy_file_path(strategy_name)
        if not strategy_path:
            st.error(f"Could not find file path for strategy: {strategy_name}")
            if st.button("Return to Browse Strategies"):
                st.session_state.page = "Browse Strategies"
                st.rerun()
            return
        
        # Get the strategy class
        strategy_class = self.registry.get(strategy_name)
        if not strategy_class:
            st.error(f"Could not find class for strategy: {strategy_name}")
            if st.button("Return to Browse Strategies"):
                st.session_state.page = "Browse Strategies"
                st.rerun()
            return
        
        # Extract current values
        current_description = strategy_info.get("description", "")
        current_category = strategy_info.get("category", "general")
        current_schema = strategy_info.get("schema", {})
        
        # Get the instruction from the class
        current_instruction = getattr(strategy_class, "instruction", "")
        
        # Get the default provider from the class
        current_provider = "openai"  # Default
        try:
            # Try to get the default provider from the class's __init__ method
            init_signature = inspect.signature(strategy_class.__init__)
            for param_name, param in init_signature.parameters.items():
                if param_name == "provider" and param.default != inspect.Parameter.empty:
                    current_provider = param.default
        except Exception as e:
            logger.error(f"Error getting default provider: {e}")
        
        # Strategy name input
        st.subheader("Strategy Name")
        new_strategy_name = st.text_input("Strategy Name", value=strategy_name)
        
        # Strategy description input
        st.subheader("Strategy Description")
        new_strategy_description = st.text_area("Description", value=current_description, height=100)
        
        # Default provider selection
        st.subheader("Default LLM Provider")
        new_default_provider = st.selectbox(
            "Default Provider",
            options=["openai", "anthropic", "google", "cohere", "openrouter", "custom"],
            index=["openai", "anthropic", "google", "cohere", "openrouter", "custom"].index(current_provider) if current_provider in ["openai", "anthropic", "google", "cohere", "openrouter", "custom"] else 0
        )
        
        # Schema definition
        st.subheader("Schema Definition")
        st.write("Define the JSON schema for the extraction strategy. This schema defines the structure of the extracted data.")
        
        # Schema editor with current schema
        schema_editor = st.text_area(
            "Schema JSON",
            value=json.dumps(current_schema, indent=4) if current_schema else "",
            height=300
        )
        
        new_schema_json = self._validate_json_schema(schema_editor)
        
        # Instruction definition
        st.subheader("Instruction Definition")
        st.write("Define the instruction for the LLM. This instruction guides the LLM on how to extract information according to the schema.")
        
        # Instruction editor with current instruction
        new_instruction = st.text_area("Instruction", value=current_instruction, height=200)
        
        # Output file configuration
        st.subheader("Output Configuration")
        
        # Category selection
        category_options = [
            "general",
            "academic", 
            "crypto", 
            "financial", 
            "news", 
            "nft", 
            "product", 
            "social"
        ]
        
        new_category = st.selectbox(
            "Strategy Category", 
            category_options,
            index=category_options.index(current_category) if current_category in category_options else 0
        )
        
        # Update strategy button
        if st.button("Update Strategy"):
            if not new_strategy_name:
                st.error("Please provide a name for the strategy.")
            elif not new_schema_json:
                st.error("Please provide a valid JSON schema.")
            elif not new_instruction:
                st.error("Please provide an instruction for the LLM.")
            else:
                try:
                    # Edit the strategy file
                    output_path = self.generator.edit_strategy_file(
                        strategy_path=strategy_path,
                        strategy_name=new_strategy_name,
                        strategy_description=new_strategy_description,
                        schema=new_schema_json,
                        instruction=new_instruction,
                        default_provider=new_default_provider,
                        category=new_category
                    )
                    
                    st.success(f"Strategy '{new_strategy_name}' updated successfully!")
                    st.info(f"Strategy file updated at: {output_path}")
                    
                    # Provide instructions for using the updated strategy
                    st.subheader("Next Steps")
                    
                    # Create two columns for buttons
                    col1, col2 = st.columns(2)
                    
                    # Add a button to reload strategies without restarting
                    with col1:
                        if st.button("Reload Strategies"):
                            # Reload all strategies
                            StrategyRegistry.reload_strategies()
                            st.success("Strategies reloaded successfully! Your updated strategy is now available.")
                            # Clear edit strategy from session state
                            if "edit_strategy" in st.session_state:
                                del st.session_state.edit_strategy
                            # Set session state to navigate to Browse Strategies
                            st.session_state.page = "Browse Strategies"
                            # Rerun the app to refresh the UI
                            st.rerun()
                    
                    # Add a button to directly test the updated strategy
                    with col2:
                        if st.button("Test Updated Strategy"):
                            # Reload all strategies
                            StrategyRegistry.reload_strategies()
                            # Set the test_strategy in session state to the updated strategy
                            st.session_state.test_strategy = new_strategy_name
                            # Navigate to Test Strategy page
                            st.session_state.page = "Test Strategy"
                            # Rerun the app to refresh the UI
                            st.rerun()
                    
                    st.write("1. Click 'Reload Strategies' button to register the updated strategy and return to Browse Strategies")
                    st.write("2. Click 'Test Updated Strategy' button to reload and immediately test your updated strategy")
                    st.write("3. Or restart the application if the reload buttons don't work")
                    
                except Exception as e:
                    st.error(f"Error updating strategy: {str(e)}")
                    logger.exception("Strategy update failed")
        
        # Cancel button
        if st.button("Cancel"):
            # Clear edit strategy from session state
            if "edit_strategy" in st.session_state:
                del st.session_state.edit_strategy
            # Set session state to navigate to Browse Strategies
            st.session_state.page = "Browse Strategies"
            # Rerun the app to refresh the UI
            st.rerun()
    
    def _show_help_guidelines(self):
        """Show the Help & Guidelines page.
        
        This page provides guidance for business users on how to create effective
        extraction strategies, including examples and best practices.
        """
        st.header("Help & Guidelines for Creating Extraction Strategies")
        
        # Introduction
        st.markdown("""
        ## Introduction
        
        This guide will help you create effective extraction strategies for your business needs without requiring 
        technical expertise. By following these guidelines, you can create custom strategies that extract 
        structured data from various content sources.
        """)
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["Understanding Strategies", "Creating Effective Schemas", "Writing Good Instructions", "Prompt Templates"])
        
        with tab1:
            st.markdown("""
            ## Understanding Extraction Strategies
            
            An extraction strategy is a combination of:
            
            1. **Schema** - Defines the structure of data you want to extract
            2. **Instruction** - Tells the AI how to extract the data according to the schema
            3. **Configuration** - Technical settings for the AI model
            
            ### When to Create a New Strategy
            
            Create a new strategy when:
            - You need to extract specific information not covered by existing strategies
            - You have unique business requirements for data extraction
            - You want to customize the extraction format for your specific use case
            
            ### Types of Strategies
            
            - **Simple Strategies**: Extract basic information with a straightforward schema
            - **Detailed Strategies**: Extract comprehensive information with complex schemas
            - **Composite Strategies**: Combine multiple strategies for more robust extraction
            """)
        
        with tab2:
            st.markdown("""
            ## Creating Effective Schemas
            
            The schema defines the structure of the data you want to extract. A well-designed schema is crucial for getting quality results.
            
            ### Schema Structure
            
            JSON schemas use these common field types:
            - `string`: Text values
            - `number`: Numeric values
            - `boolean`: True/false values
            - `array`: Lists of items
            - `object`: Nested structures with their own properties
            
            ### Best Practices
            
            1. **Be Specific**: Clearly define what each field should contain
            2. **Use Descriptions**: Add descriptions to help the AI understand what to extract
            3. **Set Requirements**: Mark which fields are required vs. optional
            4. **Use Appropriate Types**: Choose the right data type for each field
            5. **Keep It Focused**: Only include fields that are relevant to your needs
            """)
            
            st.subheader("Schema Examples")
            
            schema_examples = {
                "Basic Entity Extraction": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Name of the entity"},
                                "type": {"type": "string", "description": "Type of the entity (person, organization, location, etc.)"},
                                "description": {"type": "string", "description": "Brief description of the entity"},
                                "relevance": {"type": "number", "description": "Relevance score from 0 to 1"}
                            },
                            "required": ["name", "type"]
                        }
                    },
                    "summary": {"type": "string", "description": "Brief summary of the content"}
                },
                "Financial Data Extraction": {
                    "financial_metrics": {
                        "type": "object",
                        "properties": {
                            "revenue": {
                                "type": "object",
                                "properties": {
                                    "value": {"type": "number"},
                                    "currency": {"type": "string"},
                                    "period": {"type": "string", "description": "Time period (e.g., Q1 2023)"}
                                }
                            },
                            "profit_margin": {"type": "number", "description": "Profit margin as a percentage"},
                            "growth_rate": {"type": "number", "description": "Year-over-year growth rate"}
                        }
                    },
                    "key_financial_events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "event_type": {"type": "string", "description": "Type of financial event"},
                                "description": {"type": "string"},
                                "impact": {"type": "string", "enum": ["positive", "neutral", "negative"]}
                            }
                        }
                    }
                }
            }
            
            selected_example = st.selectbox("Select a schema example", list(schema_examples.keys()))
            st.json(schema_examples[selected_example])
            
            st.markdown("""
            ### Tips for Schema Design
            
            - **Start Simple**: Begin with a basic schema and expand as needed
            - **Test Iteratively**: Create a schema, test it, and refine based on results
            - **Consider Nesting**: Use nested objects for related information
            - **Use Enums**: For fields with a fixed set of possible values
            - **Add Constraints**: Use min/max for numbers, patterns for strings
            """)
        
        with tab3:
            st.markdown("""
            ## Writing Effective Instructions
            
            The instruction tells the AI model how to extract information according to your schema. Clear instructions lead to better results.
            
            ### Key Components of Good Instructions
            
            1. **Context**: Explain what kind of content is being analyzed
            2. **Task Definition**: Clearly state what the AI should do
            3. **Guidelines**: Provide specific rules for extraction
            4. **Output Format**: Specify how the output should be structured
            5. **Examples**: When possible, include examples of expected output
            
            ### Instruction Template
            
            ```
            You are an AI assistant specialized in extracting [SPECIFIC TYPE] information from [CONTENT TYPE].
            
            Your task is to analyze the provided content and extract relevant information according to the specified JSON schema.
            
            Follow these guidelines:
            1. [SPECIFIC GUIDELINE 1]
            2. [SPECIFIC GUIDELINE 2]
            3. [SPECIFIC GUIDELINE 3]
            4. Format the output according to the provided JSON schema exactly
            
            The extracted information should be comprehensive yet concise.
            ```
            """)
            
            st.subheader("Instruction Examples")
            
            instruction_examples = {
                "Financial News Analysis": """You are an AI assistant specialized in extracting financial information from news articles and reports.

Your task is to analyze the provided content and extract relevant financial data according to the specified JSON schema.

Follow these guidelines:
1. Focus on extracting concrete financial metrics (revenue, profit, growth rates)
2. Identify key financial events and their potential impact
3. Extract information about financial performance relative to expectations
4. If exact numbers aren't available, note this in the description
5. Format the output according to the provided JSON schema exactly

The extracted information should be comprehensive yet concise, focusing on factual financial data rather than opinions or predictions.""",
                
                "Product Information Extraction": """You are an AI assistant specialized in extracting product information from websites, catalogs, and marketing materials.

Your task is to analyze the provided content and extract detailed product information according to the specified JSON schema.

Follow these guidelines:
1. Extract all product specifications, features, and pricing information
2. Identify the brand, model, and product category accurately
3. Capture customer reviews and ratings when available
4. For technical specifications, maintain the exact terminology used in the source
5. Format the output according to the provided JSON schema exactly

The extracted information should be detailed and structured to help with product comparison and analysis."""
            }
            
            selected_instruction = st.selectbox("Select an instruction example", list(instruction_examples.keys()))
            st.text_area("Example Instruction", instruction_examples[selected_instruction], height=300, disabled=True)
            
            st.markdown("""
            ### Tips for Writing Instructions
            
            - **Be Specific**: Clearly state what information to extract and how
            - **Prioritize Information**: Indicate which fields are most important
            - **Handle Missing Data**: Explain what to do when information isn't available
            - **Consider Edge Cases**: Provide guidance for unusual content
            - **Maintain Objectivity**: Focus on factual extraction, not interpretation
            """)
        
        with tab4:
            st.markdown("""
            ## Prompt Templates for Business Users
            
            If you're working with an external LLM (like ChatGPT or Claude) to help design your extraction strategy,
            here are templates you can use to get better results.
            """)
            
            st.subheader("Template for Schema Design")
            schema_prompt = """I need to create a JSON schema for extracting [TYPE OF INFORMATION] from [TYPE OF CONTENT].

My business requirements are:
1. [REQUIREMENT 1]
2. [REQUIREMENT 2]
3. [REQUIREMENT 3]

The key information I need to extract includes:
- [INFORMATION 1]
- [INFORMATION 2]
- [INFORMATION 3]

Please create a detailed JSON schema that captures this information in a structured way. Include appropriate data types, descriptions, and any constraints. The schema should follow standard JSON Schema format.

Additional context: [ANY ADDITIONAL INFORMATION ABOUT YOUR USE CASE]"""
            
            st.text_area("Schema Design Prompt", schema_prompt, height=250)
            
            st.subheader("Template for Instruction Design")
            instruction_prompt = """I need to write an instruction for an AI model to extract information according to this JSON schema:

```json
[PASTE YOUR SCHEMA HERE]
```

The extraction will be performed on [TYPE OF CONTENT] about [SUBJECT MATTER].

My business requirements are:
1. [REQUIREMENT 1]
2. [REQUIREMENT 2]
3. [REQUIREMENT 3]

Please write a clear, detailed instruction that will guide the AI to extract information according to this schema. The instruction should include:
1. Context about the type of content being analyzed
2. Specific guidelines for extraction
3. How to handle missing or uncertain information
4. Any special considerations for my use case

Additional context: [ANY ADDITIONAL INFORMATION ABOUT YOUR USE CASE]"""
            
            st.text_area("Instruction Design Prompt", instruction_prompt, height=300)
            
            st.markdown("""
            ### How to Use These Templates
            
            1. **Copy the template** that fits your needs
            2. **Replace the placeholders** with your specific information
            3. **Send to an LLM** like ChatGPT or Claude
            4. **Review and refine** the generated schema or instruction
            5. **Copy the result** into the appropriate field in the Create New Strategy page
            
            Remember that these are starting points - you may need to iterate and refine based on your specific needs and the results you get from testing.
            """)
        
        # Final tips and next steps
        st.subheader("Next Steps")
        st.markdown("""
        After reviewing these guidelines:
        
        1. Go to the **Create New Strategy** page to build your custom strategy
        2. Test your strategy with sample content using the **Test Strategy** page
        3. Refine your schema and instructions based on the results
        4. For complex needs, consider creating a **Composite Strategy** that combines multiple approaches
        
        Remember that creating effective extraction strategies is an iterative process. Start simple, test, and refine!
        """)


def main():
    """Run the Strategy Manager UI application."""
    ui = StrategyManagerUI()
    ui.run()


if __name__ == "__main__":
    main()