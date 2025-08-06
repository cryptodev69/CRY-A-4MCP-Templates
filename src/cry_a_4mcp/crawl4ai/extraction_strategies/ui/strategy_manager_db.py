"""Strategy Manager UI Module with Database Support.

This module provides a web-based UI for managing extraction strategies,
including creating, configuring, and testing strategies using a database backend.
"""

import os
import logging
import json
import asyncio
import inspect
import importlib
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd

from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.openrouter_utils import get_openrouter_models, format_openrouter_models, save_api_keys_to_file, load_api_keys_from_file
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.improved_strategy_ui import show_improved_strategy_management
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui import show_new_strategy_management

from src.cry_a_4mcp.crawl4ai.extraction_strategies.registry import StrategyRegistry
from src.cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.database.strategy_db_manager import StrategyDatabaseManager

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrategyManagerDBUI:
    """UI for managing extraction strategies with database support.
    
    This class provides a Streamlit-based UI for managing extraction strategies,
    including browsing available strategies, configuring strategy parameters,
    testing strategies on sample content, and creating composite strategies.
    It uses a database backend for storing and retrieving strategy data.
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
        """Initialize the StrategyManagerDBUI."""
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
            from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.templates.strategy_generator import StrategyTemplateGenerator
            self.generator = StrategyTemplateGenerator()
        except ImportError as e:
            logger.error(f"Error importing StrategyTemplateGenerator: {e}")
        
        # Initialize the database manager
        self.db_manager = StrategyDatabaseManager()
        
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
        st.set_page_config(page_title="Extraction Strategy Manager (DB)", layout="wide")
        
        # Import and load custom CSS and icons
        try:
            from .assets.ui_utils import load_css, render_app_header
            load_css()
        except ImportError:
            # Fallback to inline CSS if assets module is not available
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
            .main-nav .nav-item.active {
                background-color: rgba(237, 237, 237, 0.2);
                font-weight: bold;
            }
            .stButton>button {
                width: 100%;
                margin-bottom: 10px;
                font-weight: 500;
            }
            /* Improve sidebar navigation buttons */
            .sidebar .stButton>button {
                background-color: rgba(70, 70, 70, 0.2);
                border: 1px solid rgba(250, 250, 250, 0.1);
                transition: all 0.3s ease;
            }
            .sidebar .stButton>button:hover {
                background-color: rgba(70, 70, 70, 0.4);
                border-color: rgba(250, 250, 250, 0.3);
                transform: translateY(-2px);
            }
            .strategy-card {
                border: 1px solid rgba(237, 237, 237, 0.2);
                border-radius: 0.5rem;
                padding: 1rem;
                margin-bottom: 1rem;
                transition: border-color 0.3s;
            }
            .strategy-card:hover {
                border-color: rgba(237, 237, 237, 0.5);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .json-editor {
                font-family: monospace;
                height: 300px;
            }
            .app-header {
                display: flex;
                align-items: center;
                padding: 1rem;
                background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
                color: white;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .app-logo {
                font-size: 24px;
                font-weight: bold;
                margin-right: 10px;
            }
            .app-title {
                font-size: 20px;
                font-weight: bold;
            }
            .category-badge {
                display: inline-block;
                padding: 3px 8px;
                background-color: #E5E7EB;
                color: #4B5563;
                border-radius: 12px;
                font-size: 12px;
                margin-bottom: 10px;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # Initialize session state for navigation
        if "page" not in st.session_state:
            st.session_state.page = "improved_manage"
        if "view_code" not in st.session_state:
            st.session_state.view_code = False
        if "selected_strategy" not in st.session_state:
            st.session_state.selected_strategy = None
            
        # Render professional header with logo
        try:
            render_app_header("Strategy Manager", "Manage, test, and create extraction strategies")
        except (ImportError, NameError):
            # Fallback header
            st.markdown("""
            <div class='app-header'>
                <div class='app-logo'>🧠</div>
                <div class='app-title'>Strategy Manager</div>
            </div>
            """, unsafe_allow_html=True)
            st.subheader("Manage, test, and create extraction strategies")
        
        # Sidebar navigation
        st.sidebar.title("Strategy Manager")
        st.sidebar.markdown("<div class='main-nav'>", unsafe_allow_html=True)
        
        # Try to import the icons and UI utilities
        try:
            from .assets.ui_utils import render_nav_item
            from .assets.icons import get_all_icons
            
            # Navigation items with icons
            render_nav_item("Strategy Dashboard", "manage", "strategy_dashboard", 
                          active=st.session_state.page == "strategy_dashboard")
            render_nav_item("Create Composite", "composite", "composite", 
                          active=st.session_state.page == "composite")
            render_nav_item("API Keys", "api_keys", "api_keys", 
                          active=st.session_state.page == "api_keys")
            
            # Add MCP Server Config option
            # Define standard navigation items for reference
            standard_nav_items = ["strategy_dashboard", "composite", "api_keys"]
            
            # Add MCP Server Config if not already in session state pages
            if "mcp_server" not in standard_nav_items:
                render_nav_item("MCP Server Config", "mcp_server", "mcp_server", 
                              active=st.session_state.page == "mcp_server")
        except ImportError:
            # Fallback to original navigation if icons module is not available
            nav_items = [
                ("strategy_dashboard", "📊 Strategy Dashboard"),
                ("composite", "🔄 Create Composite"),
                ("api_keys", "🔑 API Keys")
            ]
            
            for page_id, label in nav_items:
                active_class = "active" if st.session_state.page == page_id else ""
                if st.sidebar.button(label, key=f"nav_{page_id}", help=f"Go to {label}", use_container_width=True):
                    st.session_state.page = page_id
                    # Clear any temporary session state when changing pages
                    for key in list(st.session_state.keys()):
                        if key.startswith("temp_"):
                            del st.session_state[key]
                    # Force a rerun to apply the navigation change immediately
                    st.rerun()
        
        st.sidebar.markdown("</div>", unsafe_allow_html=True)
        
        # Display the selected page
        # Default to improved management if somehow browse is still selected
        if st.session_state.page == "browse":
            st.session_state.page = "strategy_dashboard"
            st.rerun()
        # Redirect removed pages to strategy dashboard
        elif st.session_state.page in ["test", "create", "improved_manage", "new_manage"]:
            st.info("This functionality is now available in the Strategy Dashboard.")
            st.session_state.page = "strategy_dashboard"
            st.rerun()
        elif st.session_state.page == "strategy_dashboard":
            self._show_strategy_dashboard()
        elif st.session_state.page == "composite":
            self._show_create_composite_strategy()
        elif st.session_state.page == "api_keys":
            self._show_api_keys_config()
        elif st.session_state.page == "edit_strategy":
            self._show_edit_strategy()
        elif st.session_state.page == "mcp_server":
            self._show_mcp_server_config()
        
    def _show_browse_strategies(self):
        """Show the Browse Strategies page using database."""
        # Create a header with a reload button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header("Browse Available Strategies")
        with col2:
            if st.button("🔄 Reload Strategies", use_container_width=True):
                # Reload all strategies
                StrategyRegistry.reload_strategies()
                st.success("Strategies reloaded successfully!")
                # Rerun the app to refresh the UI
                st.rerun()
        
        # Get all strategies from the database
        strategies = self.db_manager.get_all_strategies()
        
        if not strategies:
            st.warning("No strategies found in the database. You may need to run the migration script first.")
            if st.button("Run Migration", use_container_width=True, type="primary"):
                from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.database.migrate_strategies import migrate_strategies
                strategies_dir = str(Path(__file__).parent.parent / "strategies")
                migrate_count = migrate_strategies(strategies_dir)
                st.success(f"Migration complete. {migrate_count} strategies migrated.")
                st.rerun()
            return
        
        # Group strategies by category
        categories = {}
        for strategy in strategies:
            category = strategy.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(strategy)
        
        # Create tabs for each category
        if categories:
            tabs = st.tabs(list(categories.keys()))
            
            for i, (category, category_strategies) in enumerate(categories.items()):
                with tabs[i]:
                    # Display strategies in a grid
                    cols = st.columns(3)
                    for j, strategy in enumerate(category_strategies):
                        with cols[j % 3]:
                            try:
                                # Try to use the new UI utilities
                                from .assets.ui_utils import render_strategy_card
                                render_strategy_card(strategy, f"{category}_{j}")
                            except ImportError:
                                # Fallback to original strategy card display
                                with st.container():
                                    st.markdown(f"<div class='strategy-card'>", unsafe_allow_html=True)
                                    st.subheader(strategy['name'])
                                    
                                    # Add category badge
                                    category_name = strategy.get('category', 'general')
                                    st.markdown(f"<div class='category-badge'>{category_name}</div>", unsafe_allow_html=True)
                                    
                                    st.write(strategy['description'])
                                    st.write(f"Default Provider: {strategy['default_provider']}")
                                    
                                    # Action buttons
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        if st.button("✏️ Edit", key=f"edit_{strategy['name']}", use_container_width=True):
                                            st.session_state.temp_edit_strategy = strategy['name']
                                            st.session_state.page = "edit_strategy"
                                            st.rerun()
                                    with col2:
                                        if st.button("🧪 Test", key=f"test_{strategy['name']}", use_container_width=True):
                                            st.session_state.temp_test_strategy = strategy['name']
                                            st.session_state.page = "test"
                                            st.rerun()
                                    with col3:
                                        if st.button("📄 Code", key=f"code_{strategy['name']}", use_container_width=True):
                                            st.session_state.view_code = True
                                            st.session_state.selected_strategy = strategy['name']
                                            st.rerun()
                                    
                                    st.markdown("</div>", unsafe_allow_html=True)
    
    def _show_test_strategy(self):
        """Show the Test Strategy page with improved UI using database."""
        # Create a header with a reload button and back button
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.header("Test Extraction Strategy")
        with col2:
            if st.button("🔄 Reload Strategies", key="reload_test_page", use_container_width=True):
                # Reload all strategies
                StrategyRegistry.reload_strategies()
                st.success("Strategies reloaded successfully!")
                # Rerun the app to refresh the UI
                st.rerun()
        with col3:
            if st.button("Back to Browse", key="back_to_browse_from_test", use_container_width=True):
                # Navigate directly to browse page
                st.session_state.page = "browse"
                st.rerun()
        
        # Get all strategies from the database
        strategies = self.db_manager.get_all_strategies()
        strategy_names = [s['name'] for s in strategies]
        
        if not strategy_names:
            st.warning("No strategies found in the database.")
            return
        
        # Strategy selection
        selected_strategy = None
        if "temp_test_strategy" in st.session_state and st.session_state.temp_test_strategy in strategy_names:
            selected_strategy = st.session_state.temp_test_strategy
            # Clear the temporary state after using it
            del st.session_state.temp_test_strategy
        
        selected_strategy = st.selectbox(
            "Select a strategy to test",
            options=strategy_names,
            index=strategy_names.index(selected_strategy) if selected_strategy else 0
        )
        
        # Get the selected strategy from the database
        strategy_data = self.db_manager.get_strategy(selected_strategy)
        
        if not strategy_data:
            st.error(f"Strategy '{selected_strategy}' not found in the database.")
            return
        
        # Display strategy details
        with st.expander("Strategy Details", expanded=False):
            st.write(f"**Description:** {strategy_data['description']}")
            st.write(f"**Category:** {strategy_data['category']}")
            st.write(f"**Default Provider:** {strategy_data['default_provider']}")
            
            # Display schema
            st.subheader("Schema")
            st.json(strategy_data['schema'])
            
            # Display instruction
            st.subheader("Instruction")
            st.code(strategy_data['instruction'], language="")
        
        # Provider selection
        st.subheader("Provider Configuration")
        
        # Default to the strategy's default provider
        default_provider = strategy_data['default_provider']
        
        # Provider options
        provider_options = ["openai", "anthropic", "openrouter", "google", "mistral", "ollama"]
        selected_provider = st.selectbox(
            "Select Provider",
            options=provider_options,
            index=provider_options.index(default_provider) if default_provider in provider_options else 0
        )
        
        # Model selection based on provider
        model_options = self._get_model_options(selected_provider)
        selected_model = st.selectbox("Select Model", options=model_options)
        
        # API key input
        api_key = self._get_api_key_input(selected_provider)
        
        # Content input
        st.subheader("Content to Extract From")
        content = st.text_area("Enter content", height=200)
        
        # Run extraction
        if st.button("Run Extraction", type="primary", use_container_width=True):
            if not content:
                st.error("Please enter content to extract from.")
                return
            
            if not api_key and selected_provider != "ollama":
                st.error(f"Please enter an API key for {selected_provider}.")
                return
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Update progress
                progress_bar.progress(10)
                status_text.text("Initializing strategy...")
                
                # Load the strategy module
                strategy_module = self._load_strategy_module(strategy_data['file_path'])
                if not strategy_module:
                    st.error(f"Failed to load strategy module from {strategy_data['file_path']}.")
                    return
                
                # Find the strategy class in the module
                strategy_class = None
                for name, obj in inspect.getmembers(strategy_module):
                    if inspect.isclass(obj) and hasattr(obj, 'SCHEMA') and hasattr(obj, 'INSTRUCTION'):
                        strategy_class = obj
                        break
                
                if not strategy_class:
                    st.error("Strategy class not found in the module.")
                    return
                
                # Update progress
                progress_bar.progress(30)
                status_text.text("Creating strategy instance...")
                
                # Create the strategy instance
                strategy_instance = self.factory.create_strategy(
                    strategy_class.__name__,
                    provider=selected_provider,
                    model=selected_model,
                    api_key=api_key
                )
                
                # Update progress
                progress_bar.progress(50)
                status_text.text("Running extraction...")
                
                # Run the extraction
                start_time = datetime.now()
                
                # Wrap in SyncExtractionStrategyWrapper for synchronous execution
                sync_strategy = SyncExtractionStrategyWrapper(strategy_instance)
                # Pass both url and content parameters to the extract method
                # Using a dummy URL since we're testing with direct content
                result = sync_strategy.extract(url="https://example.com/test", content=content)
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # Update progress
                progress_bar.progress(100)
                status_text.text("Extraction complete!")
                
                # Display results
                st.subheader("Extraction Results")
                st.write(f"Execution time: {execution_time:.2f} seconds")
                
                # Display the result in a nice format
                st.json(result)
                
                # Option to download as JSON
                json_str = json.dumps(result, indent=2)
                st.download_button(
                    label="Download Results as JSON",
                    data=json_str,
                    file_name=f"{selected_strategy}_result.json",
                    mime="application/json",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Error during extraction: {str(e)}")
                logger.exception("Error during extraction")
            finally:
                # Ensure progress bar is completed
                progress_bar.progress(100)
    
    def _load_strategy_module(self, file_path: str):
        """Load a strategy module from file path."""
        try:
            # Convert file path to module path
            module_path = file_path.replace(os.sep, '.')
            if module_path.endswith('.py'):
                module_path = module_path[:-3]
            
            # Import the module
            module_name = f"cry_a_4mcp.crawl4ai.extraction_strategies.{module_path}"
            return importlib.import_module(module_name)
        except Exception as e:
            logger.error(f"Error loading strategy module: {e}")
            return None
    
    def _get_model_options(self, provider: str) -> List[str]:
        """Get model options for the selected provider."""
        if provider == "openai":
            return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        elif provider == "anthropic":
            return ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        elif provider == "openrouter":
            # Get models from OpenRouter API if API key is available
            if "api_tokens" in st.session_state and "openrouter" in st.session_state.api_tokens:
                api_key = st.session_state.api_tokens["openrouter"]
                try:
                    models = get_openrouter_models(api_key)
                    return format_openrouter_models(models)
                except Exception as e:
                    logger.error(f"Error getting OpenRouter models: {e}")
            # Include deepseek model as the first option
            return ["deepseek/deepseek-chat-v3-0324:free", "openai/gpt-4-turbo", "anthropic/claude-3-opus-20240229", "google/gemini-pro"]
        elif provider == "google":
            return ["gemini-pro"]
        elif provider == "mistral":
            return ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"]
        elif provider == "ollama":
            return ["llama3", "llama3:8b", "llama3:70b", "mistral", "mixtral"]
        return []
    
    def _get_api_key_input(self, provider: str) -> str:
        """Get API key input for the selected provider."""
        # Skip API key for Ollama (local models)
        if provider == "ollama":
            return ""
        
        # Get saved API key if available
        saved_key = ""
        if "api_tokens" in st.session_state and provider in st.session_state.api_tokens:
            saved_key = st.session_state.api_tokens[provider]
        
        # API key input
        api_key = st.text_input(
            f"{provider.capitalize()} API Key",
            value=saved_key,
            type="password",
            help=f"Enter your {provider.capitalize()} API key"
        )
        
        # Save API key if provided
        if api_key and ("api_tokens" not in st.session_state or 
                       provider not in st.session_state.api_tokens or 
                       st.session_state.api_tokens[provider] != api_key):
            if "api_tokens" not in st.session_state:
                st.session_state.api_tokens = {}
            st.session_state.api_tokens[provider] = api_key
            self._save_api_keys()
        
        return api_key
    
    def _show_create_composite_strategy(self):
        """Show the Create Composite Strategy page using database."""
        st.header("Create Composite Strategy")
        
        # Get all strategies from the database
        strategies = self.db_manager.get_all_strategies()
        strategy_names = [s['name'] for s in strategies]
        
        if not strategy_names:
            st.warning("No strategies found in the database.")
            return
        
        # Composite strategy configuration
        st.subheader("Configure Composite Strategy")
        
        composite_name = st.text_input("Composite Strategy Name", value="MyCompositeStrategy")
        description = st.text_area("Description", value="A custom composite extraction strategy")
        category = st.text_input("Category", value="composite")
        
        # Strategy selection
        st.subheader("Select Strategies to Combine")
        
        # Allow selecting multiple strategies
        selected_strategies = st.multiselect(
            "Select strategies to combine",
            options=strategy_names
        )
        
        if not selected_strategies:
            st.warning("Please select at least one strategy to combine.")
        
        # Create composite strategy
        if st.button("Create Composite Strategy", type="primary", use_container_width=True):
            if not composite_name:
                st.error("Please enter a name for the composite strategy.")
                return
            
            if not selected_strategies:
                st.error("Please select at least one strategy to combine.")
                return
            
            try:
                # Get the selected strategy modules
                strategy_modules = []
                for strategy_name in selected_strategies:
                    strategy_data = self.db_manager.get_strategy(strategy_name)
                    if not strategy_data:
                        st.error(f"Strategy '{strategy_name}' not found in the database.")
                        return
                    
                    module = self._load_strategy_module(strategy_data['file_path'])
                    if not module:
                        st.error(f"Failed to load strategy module for '{strategy_name}'.")
                        return
                    
                    strategy_modules.append(module)
                
                # Create the composite strategy
                composite_schema = self._create_composite_schema(strategy_modules)
                composite_instruction = self._create_composite_instruction(strategy_modules)
                
                # Generate the composite strategy file
                self.generator.generate_strategy_file(
                    name=composite_name,
                    description=description,
                    schema=composite_schema,
                    instruction=composite_instruction,
                    default_provider="openai",
                    category=category
                )
                
                # Add the composite strategy to the database
                composite_data = {
                    'name': composite_name,
                    'description': description,
                    'category': category,
                    'default_provider': "openai",
                    'schema': composite_schema,
                    'instruction': composite_instruction,
                    'file_path': f"strategies/{category}/{composite_name.lower().replace(' ', '_')}.py"
                }
                
                self.db_manager.add_strategy(composite_data)
                
                # Reload strategies
                StrategyRegistry.reload_strategies()
                
                # Show success message
                st.success(f"Composite strategy '{composite_name}' created successfully!")
                
                # Provide option to test the new strategy
                if st.button("Test New Strategy", key="test_new_composite_strategy", type="primary", use_container_width=True):
                    # Store strategy name for testing
                    st.session_state.temp_test_strategy = composite_name
                    # Set navigation action
                    if 'nav_action' not in st.session_state:
                        st.session_state.nav_action = None
                    st.session_state.nav_action = "test"
                    # Navigate to test page
                    st.session_state.page = "test"
                    st.rerun()
                
            except Exception as e:
                st.error(f"Error creating composite strategy: {str(e)}")
                logger.exception("Error creating composite strategy")
    
    def _create_composite_schema(self, strategy_modules):
        """Create a composite schema from multiple strategy modules."""
        composite_schema = {
            "type": "object",
            "properties": {}
        }
        
        for module in strategy_modules:
            # Find the strategy class in the module
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, 'SCHEMA'):
                    schema = obj.SCHEMA
                    if isinstance(schema, dict) and "properties" in schema:
                        for prop_name, prop_schema in schema["properties"].items():
                            composite_schema["properties"][prop_name] = prop_schema
        
        return composite_schema
    
    def _create_composite_instruction(self, strategy_modules):
        """Create a composite instruction from multiple strategy modules."""
        instructions = []
        
        for module in strategy_modules:
            # Find the strategy class in the module
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, 'INSTRUCTION'):
                    instruction = obj.INSTRUCTION
                    class_name = obj.__name__
                    instructions.append(f"# From {class_name}:\n{instruction}")
        
        composite_instruction = """You are a composite extraction strategy that combines multiple extraction strategies.\n\nExtract information according to the following instructions from each component strategy:\n\n"""
        
        composite_instruction += "\n\n".join(instructions)
        
        return composite_instruction
    
    def _show_create_new_strategy(self):
        """Show the Create New Strategy page using database."""
        st.header("Create New Strategy")
        
        # Strategy metadata
        st.subheader("Strategy Metadata")
        
        strategy_name = st.text_input("Strategy Name", value="")
        strategy_description = st.text_area("Description", value="A custom extraction strategy for specific content")
        
        # API configuration
        st.subheader("API Configuration")
        
        provider_options = ["openai", "anthropic", "openrouter", "google", "mistral", "ollama"]
        default_provider = st.selectbox(
            "Default Provider",
            options=provider_options,
            index=0
        )
        
        category = st.text_input("Category", value="custom")
        
        # Schema definition
        st.subheader("Schema Definition")
        st.write("Define the JSON schema for the extraction output.")
        
        # Help button for schema
        with st.expander("Schema Help", expanded=False):
            st.markdown("""
            The schema defines the structure of the data to be extracted. It follows the JSON Schema format.
            
            Example schema for extracting a person's name and age:
            ```json
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The person's full name"
                    },
                    "age": {
                        "type": "integer",
                        "description": "The person's age in years"
                    }
                }
            }
            ```
            """)
        
        schema_json = st.text_area(
            "Schema JSON",
            value="""
{
    "type": "object",
    "properties": {
        "example_field": {
            "type": "string",
            "description": "Description of what to extract"
        }
    }
}
            """,
            height=300
        )
        
        # Validate schema
        schema_obj = self._validate_json_schema(schema_json)
        
        # Instruction definition
        st.subheader("Instruction Definition")
        st.write("Define the instruction for the LLM on how to extract the data.")
        
        # Help button for instruction
        with st.expander("Instruction Help", expanded=False):
            st.markdown("""
            The instruction guides the LLM on how to extract information according to the schema.
            
            Example instruction for extracting a person's name and age:
            ```
            Extract the person's name and age from the provided text.
            The name should be the full name as mentioned in the text.
            The age should be extracted as a number in years.
            If the information is not present in the text, do not include it in the output.
            ```
            """)
        
        instruction = st.text_area(
            "Instruction",
            value="Extract the requested information from the provided text according to the schema.",
            height=200
        )
        
        # Create strategy
        if st.button("Create Strategy", type="primary", use_container_width=True):
            if not strategy_name:
                st.error("Please enter a name for the strategy.")
                return
            
            if not schema_obj:
                st.error("Please enter a valid JSON schema.")
                return
            
            if not instruction:
                st.error("Please enter an instruction for the LLM.")
                return
            
            try:
                # Generate the strategy file
                file_path = self.generator.generate_strategy_file(
                    name=strategy_name,
                    description=strategy_description,
                    schema=schema_obj,
                    instruction=instruction,
                    default_provider=default_provider,
                    category=category
                )
                
                # Add the strategy to the database
                strategy_data = {
                    'name': strategy_name,
                    'description': strategy_description,
                    'category': category,
                    'default_provider': default_provider,
                    'schema': schema_obj,
                    'instruction': instruction,
                    'file_path': file_path
                }
                
                self.db_manager.add_strategy(strategy_data)
                
                # Reload strategies
                StrategyRegistry.reload_strategies()
                
                # Show success message
                st.success(f"Strategy '{strategy_name}' created successfully!")
                
                # Initialize navigation state if not exists
                if 'nav_action' not in st.session_state:
                    st.session_state.nav_action = None
                
                # Create a container for navigation buttons
                st.write("What would you like to do next?")
                
                # Create columns for buttons
                test_col, browse_col = st.columns(2)
                
                # Test New Strategy button
                with test_col:
                    if st.button("Test New Strategy", key="test_new_strategy_direct", type="primary", use_container_width=True):
                        # Store strategy name and set navigation action
                        st.session_state.temp_test_strategy = strategy_name
                        st.session_state.nav_action = "test"
                
                # Back to Browse button
                with browse_col:
                    if st.button("Back to Browse", key="back_to_browse_from_create", use_container_width=True):
                        st.session_state.nav_action = "browse"
                
                # Check if navigation action is set and perform navigation
                if st.session_state.nav_action == "test":
                    # Clear the action to prevent repeated navigation
                    st.session_state.nav_action = None
                    # Navigate to test page
                    st.session_state.page = "test"
                    st.rerun()
                elif st.session_state.nav_action == "browse":
                    # Clear the action to prevent repeated navigation
                    st.session_state.nav_action = None
                    # Navigate to browse page
                    st.session_state.page = "browse"
                    st.rerun()
                
            except Exception as e:
                st.error(f"Error creating strategy: {str(e)}")
                logger.exception("Error creating strategy")
    
    def _show_api_keys_config(self):
        """Show the API Keys Configuration page."""
        st.header("API Keys Configuration")
        
        # Initialize session state for API tokens if not exists
        if "api_tokens" not in st.session_state:
            st.session_state.api_tokens = {}
        
        # Provider options
        providers = ["openai", "anthropic", "openrouter", "google", "mistral"]
        
        for provider in providers:
            # Get saved API key if available
            saved_key = ""
            if provider in st.session_state.api_tokens:
                saved_key = st.session_state.api_tokens[provider]
            
            # API key input
            api_key = st.text_input(
                f"{provider.capitalize()} API Key",
                value=saved_key,
                type="password",
                key=f"api_key_{provider}"
            )
            
            # Save API key if provided
            if api_key:
                st.session_state.api_tokens[provider] = api_key
        
        # Save button
        if st.button("Save API Keys", use_container_width=True, type="primary"):
            self._save_api_keys()
            st.success("API keys saved successfully!")
    
    def _show_mcp_server_config(self):
        """Show the MCP Server Configuration page."""
        try:
            from .assets.ui_utils import render_status_indicator
            from .assets.icons import get_all_icons
            icons = get_all_icons()
        except ImportError:
            icons = {
                "mcp_server": "🔌",
                "connect": "🔗",
                "disconnect": "🔌",
                "online": "🟢",
                "offline": "🔴",
                "settings": "⚙️"
            }
        
        st.header("MCP Server Configuration")
        
        # Back button
        if st.button("← Back to Browse", key="back_from_mcp_server"):
            st.session_state.page = "improved_manage"
            st.rerun()
        
        st.write("Configure your MCP server connection and tools.")
        
        # Initialize MCP server settings in session state if not present
        if 'mcp_server_settings' not in st.session_state:
            st.session_state.mcp_server_settings = {
                "host": "localhost",
                "port": 8080,
                "enabled": False,
                "connected": False,
                "available_tools": [
                    "TradingSignalsTool",
                    "CrawlWebsiteTool",
                    "HybridSearchTool",
                    "AnalyzeCryptoTool",
                    "UpdateKnowledgeGraphTool"
                ],
                "enabled_tools": []
            }
        
        # Create tabs for different MCP server settings
        tabs = st.tabs(["Connection", "Tools", "Status", "Documentation"])
        
        # Connection tab
        with tabs[0]:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader("Server Connection Settings")
                
                # Connection form
                with st.form("mcp_server_connection_form"):
                    host = st.text_input(
                        "MCP Server Host", 
                        value=st.session_state.mcp_server_settings.get("host", "localhost"),
                        help="Enter the MCP server host (default: localhost)"
                    )
                    
                    port = st.number_input(
                        "MCP Server Port", 
                        value=st.session_state.mcp_server_settings.get("port", 8080),
                        min_value=1,
                        max_value=65535,
                        help="Enter the MCP server port (default: 8080)"
                    )
                    
                    enabled = st.checkbox(
                        "Enable MCP Server Integration", 
                        value=st.session_state.mcp_server_settings.get("enabled", False),
                        help="Enable or disable MCP server integration"
                    )
                    
                    submitted = st.form_submit_button("Save Connection Settings")
                    
                    if submitted:
                        st.session_state.mcp_server_settings["host"] = host
                        st.session_state.mcp_server_settings["port"] = port
                        st.session_state.mcp_server_settings["enabled"] = enabled
                        st.success("MCP server connection settings saved successfully!")
            
            with col2:
                st.subheader("Connection Status")
                
                # Display connection status
                connected = st.session_state.mcp_server_settings.get("connected", False)
                status_icon = icons["online"] if connected else icons["offline"]
                status_text = "Connected" if connected else "Disconnected"
                status_color = "green" if connected else "red"
                
                try:
                    render_status_indicator(status_text, status_color, status_icon)
                except (ImportError, NameError):
                    st.markdown(f"<div style='display:flex;align-items:center;'><span style='font-size:24px;margin-right:10px;'>{status_icon}</span><span style='color:{status_color};font-weight:bold;'>{status_text}</span></div>", unsafe_allow_html=True)
                
                # Connect/Disconnect button
                if not connected:
                    if st.button(f"{icons['connect']} Connect", key="connect_mcp_server"):
                        # Simulate connection (in a real implementation, this would actually connect to the server)
                        st.session_state.mcp_server_settings["connected"] = True
                        st.success("Connected to MCP server successfully!")
                        st.rerun()
                else:
                    if st.button(f"{icons['disconnect']} Disconnect", key="disconnect_mcp_server"):
                        # Simulate disconnection
                        st.session_state.mcp_server_settings["connected"] = False
                        st.warning("Disconnected from MCP server.")
                        st.rerun()
        
        # Tools tab
        with tabs[1]:
            st.subheader("MCP Server Tools")
            
            # Available tools
            st.write("Select which MCP server tools to enable:")
            
            # Get available and enabled tools
            available_tools = st.session_state.mcp_server_settings.get("available_tools", [])
            enabled_tools = st.session_state.mcp_server_settings.get("enabled_tools", [])
            
            # Create a multiselect for tool selection
            selected_tools = st.multiselect(
                "Enabled Tools",
                options=available_tools,
                default=enabled_tools,
                help="Select which MCP server tools to enable"
            )
            
            if st.button("Save Tool Settings", key="save_mcp_tools"):
                st.session_state.mcp_server_settings["enabled_tools"] = selected_tools
                st.success("MCP server tool settings saved successfully!")
            
            # Tool details
            if selected_tools:
                st.subheader("Tool Details")
                
                for tool in selected_tools:
                    with st.expander(f"{tool}"):
                        if tool == "TradingSignalsTool":
                            st.write("Generates, queries, and backtests cryptocurrency trading signals using technical and sentiment analysis.")
                            st.write("**Actions:** generate, query, backtest")
                            st.write("**Parameters:** symbol, timeframe, signal_source, signal_type, confidence_level, limit, strategy, start_date, end_date")
                        elif tool == "CrawlWebsiteTool":
                            st.write("Crawls websites and extracts information based on specified extraction strategies.")
                            st.write("**Parameters:** url, strategy_name, max_depth, max_pages")
                        elif tool == "HybridSearchTool":
                            st.write("Performs hybrid search across multiple data sources.")
                            st.write("**Parameters:** query, sources, limit")
                        elif tool == "AnalyzeCryptoTool":
                            st.write("Analyzes cryptocurrency data and provides insights.")
                            st.write("**Parameters:** symbol, timeframe, analysis_type")
                        elif tool == "UpdateKnowledgeGraphTool":
                            st.write("Updates the knowledge graph with new information.")
                            st.write("**Parameters:** entity_type, entity_data, relationships")
                        else:
                            st.write("No detailed information available for this tool.")
        
        # Status tab
        with tabs[2]:
            st.subheader("MCP Server Status")
            
            # Display server status metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Server Status", "Online" if st.session_state.mcp_server_settings.get("connected", False) else "Offline")
            
            with col2:
                st.metric("Active Tools", len(st.session_state.mcp_server_settings.get("enabled_tools", [])))
            
            with col3:
                st.metric("Available Tools", len(st.session_state.mcp_server_settings.get("available_tools", [])))
            
            # Display recent activity (simulated)
            st.subheader("Recent Activity")
            
            if st.session_state.mcp_server_settings.get("connected", False):
                # Simulated activity log
                activity_log = [
                    {"timestamp": "2023-06-15 14:32:45", "tool": "TradingSignalsTool", "action": "generate", "status": "success"},
                    {"timestamp": "2023-06-15 14:30:12", "tool": "CrawlWebsiteTool", "action": "crawl", "status": "success"},
                    {"timestamp": "2023-06-15 14:28:05", "tool": "AnalyzeCryptoTool", "action": "analyze", "status": "error"},
                    {"timestamp": "2023-06-15 14:25:33", "tool": "HybridSearchTool", "action": "search", "status": "success"},
                ]
                
                # Display activity log in a table
                st.table(activity_log)
            else:
                st.info("Connect to the MCP server to view recent activity.")
        
        # Documentation tab
        with tabs[3]:
            st.subheader("MCP Server Documentation")
            
            st.write("""The MCP (Model Control Protocol) server provides a standardized way for AI models to interact with external tools and services. 
            This integration allows the Strategy Manager to leverage powerful tools for cryptocurrency analysis, trading signal generation, and more.""")
            
            st.subheader("Available Tools")
            
            with st.expander("TradingSignalsTool"):
                st.write("""### TradingSignalsTool
                
                Generates, queries, and backtests cryptocurrency trading signals using technical and sentiment analysis.
                
                #### Actions:
                - **generate**: Generate new trading signals for a specified cryptocurrency and timeframe
                - **query**: Query existing trading signals based on various criteria
                - **backtest**: Backtest a trading strategy using historical signals
                
                #### Parameters:
                - **symbol**: Cryptocurrency symbol (e.g., BTC, ETH)
                - **timeframe**: Time interval for analysis (e.g., 1h, 4h, 1d)
                - **signal_source**: Source of signals (technical, sentiment, combined)
                - **signal_type**: Type of signal (buy, sell, hold)
                - **confidence_level**: Minimum confidence level for signals (0-100)
                - **limit**: Maximum number of signals to return
                - **strategy**: Trading strategy for backtesting
                - **start_date**: Start date for backtesting
                - **end_date**: End date for backtesting
                """)
            
            with st.expander("CrawlWebsiteTool"):
                st.write("""### CrawlWebsiteTool
                
                Crawls websites and extracts information based on specified extraction strategies.
                
                #### Parameters:
                - **url**: URL to crawl
                - **strategy_name**: Name of the extraction strategy to use
                - **max_depth**: Maximum crawl depth
                - **max_pages**: Maximum number of pages to crawl
                """)
            
            with st.expander("HybridSearchTool"):
                st.write("""### HybridSearchTool
                
                Performs hybrid search across multiple data sources.
                
                #### Parameters:
                - **query**: Search query
                - **sources**: Data sources to search (web, database, knowledge_graph)
                - **limit**: Maximum number of results to return
                """)
            
            with st.expander("AnalyzeCryptoTool"):
                st.write("""### AnalyzeCryptoTool
                
                Analyzes cryptocurrency data and provides insights.
                
                #### Parameters:
                - **symbol**: Cryptocurrency symbol (e.g., BTC, ETH)
                - **timeframe**: Time interval for analysis (e.g., 1h, 4h, 1d)
                - **analysis_type**: Type of analysis (technical, fundamental, sentiment)
                """)
            
            with st.expander("UpdateKnowledgeGraphTool"):
                st.write("""### UpdateKnowledgeGraphTool
                
                Updates the knowledge graph with new information.
                
                #### Parameters:
                - **entity_type**: Type of entity to update
                - **entity_data**: Data for the entity
                - **relationships**: Relationships to other entities
                """)
    
    def _show_edit_strategy(self):
        """Show the Edit Strategy page using database."""
        if "temp_edit_strategy" not in st.session_state:
            st.error("No strategy selected for editing.")
            if st.button("Back to Browse", use_container_width=True):
                st.session_state.page = "browse"
                st.rerun()
            return
        
        strategy_name = st.session_state.temp_edit_strategy
        
        # Get the strategy from the database
        strategy_data = self.db_manager.get_strategy(strategy_name)
        
        if not strategy_data:
            st.error(f"Strategy '{strategy_name}' not found in the database.")
            if st.button("Back to Browse", use_container_width=True):
                st.session_state.page = "browse"
                st.rerun()
            return
        
        st.header(f"Edit Strategy: {strategy_name}")
        
        # Strategy metadata
        st.subheader("Strategy Metadata")
        
        strategy_description = st.text_area("Description", value=strategy_data['description'])
        
        # API configuration
        st.subheader("API Configuration")
        
        provider_options = ["openai", "anthropic", "openrouter", "google", "mistral", "ollama"]
        default_provider = st.selectbox(
            "Default Provider",
            options=provider_options,
            index=provider_options.index(strategy_data['default_provider']) if strategy_data['default_provider'] in provider_options else 0
        )
        
        category = st.text_input("Category", value=strategy_data['category'])
        
        # Schema definition
        st.subheader("Schema Definition")
        
        # Convert schema to JSON string for editing
        schema_json = json.dumps(strategy_data['schema'], indent=4)
        
        schema_json = st.text_area(
            "Schema JSON",
            value=schema_json,
            height=300
        )
        
        # Validate schema
        schema_obj = self._validate_json_schema(schema_json)
        
        # Instruction definition
        st.subheader("Instruction Definition")
        
        instruction = st.text_area(
            "Instruction",
            value=strategy_data['instruction'],
            height=200
        )
        
        # Update strategy
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Strategy", type="primary", use_container_width=True):
                if not schema_obj:
                    st.error("Please enter a valid JSON schema.")
                    return
                
                if not instruction:
                    st.error("Please enter an instruction for the LLM.")
                    return
                
                try:
                    # Update the strategy file
                    file_path = self.generator.edit_strategy_file(
                        strategy_path=strategy_data['file_path'],
                        strategy_name=strategy_name,
                        strategy_description=strategy_description,
                        schema=schema_obj,
                        instruction=instruction,
                        default_provider=default_provider,
                        category=category
                    )
                    
                    # Update the strategy in the database
                    updated_data = {
                        'description': strategy_description,
                        'category': category,
                        'default_provider': default_provider,
                        'schema': schema_obj,
                        'instruction': instruction,
                        'file_path': file_path
                    }
                    
                    self.db_manager.update_strategy(strategy_name, updated_data)
                    
                    # Reload strategies
                    StrategyRegistry.reload_strategies()
                    
                    # Show success message
                    st.success(f"Strategy '{strategy_name}' updated successfully!")
                    
                    # Navigation now uses direct page changes instead of action state
                    
                    # Create a container for navigation buttons
                    st.write("What would you like to do next?")
                    
                    # Create columns for buttons
                    test_col, browse_col = st.columns(2)
                    
                    # Test Updated Strategy button
                    with test_col:
                        if st.button("Test Updated Strategy", key="test_updated_strategy_button", type="primary", use_container_width=True):
                            # Store strategy name for the test page to use
                            st.session_state.temp_test_strategy = strategy_name
                            # Navigate directly to test page
                            st.session_state.page = "test"
                            st.rerun()
                    
                    # Back to Browse button
                    with browse_col:
                        if st.button("Back to Browse", key="back_to_browse_button", use_container_width=True):
                            # Navigate directly to browse page
                            st.session_state.page = "browse"
                            st.rerun()
                    
                    # Navigation is now handled directly in the button callbacks
                    
                except Exception as e:
                    st.error(f"Error updating strategy: {str(e)}")
                    logger.exception("Error updating strategy")
        
        with col2:
            if st.button("Cancel", type="secondary", use_container_width=True):
                st.session_state.page = "browse"
                st.rerun()
    
    def _show_help_guidelines(self):
        """Show help guidelines for creating extraction strategies."""
        st.header("Guidelines for Creating Extraction Strategies")
        
        # Understanding Strategies
        st.subheader("Understanding Extraction Strategies")
        st.write("""
        Extraction strategies are templates that guide LLMs to extract structured information from text.
        Each strategy consists of:
        - A JSON schema defining the structure of the output
        - An instruction that guides the LLM on how to extract the information
        - Configuration for the default LLM provider
        """)
        
        # Creating Effective Schemas
        st.subheader("Creating Effective Schemas")
        st.write("""
        A good schema should:
        - Clearly define the structure of the data to be extracted
        - Use appropriate data types (string, number, boolean, array, object)
        - Include descriptive field names
        - Provide descriptions for each field to guide the extraction
        - Consider using nested objects for complex data
        """)
        
        # Writing Good Instructions
        st.subheader("Writing Good Instructions")
        st.write("""
        Effective instructions should:
        - Be clear and concise
        - Specify exactly what information to extract
        - Provide guidance on how to handle ambiguous cases
        - Include examples if helpful
        - Specify how to handle missing information
        """)
        
        # Prompt Templates
        st.subheader("Prompt Templates")
        st.write("""
        The system combines your schema and instruction into a prompt for the LLM.
        The prompt typically follows this structure:
        
        1. Introduction of the task (extraction)
        2. Your custom instruction
        3. The schema definition
        4. Request to output valid JSON matching the schema
        5. The content to extract from
        """)
    
    def _show_strategy_dashboard(self):
        """Show the comprehensive strategy dashboard interface."""
        try:
            # Use the new UI which has all the latest features
            show_new_strategy_management()
        except Exception as e:
            st.error(f"Error loading strategy dashboard: {e}")
            logger.error(f"Error in strategy dashboard: {e}")
            
            # Fallback to regular browse page
            st.warning("Falling back to regular browse interface...")
            if st.button("Go to Browse Strategies"):
                st.session_state.page = "browse"
                st.rerun()


def main():
    """Run the Strategy Manager UI application with database support."""
    ui = StrategyManagerDBUI()
    ui.run()


if __name__ == "__main__":
    main()