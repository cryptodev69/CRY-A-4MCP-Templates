#!/usr/bin/env python3
"""
New Strategy UI with robust edit/delete functionality.

This module provides a completely rebuilt Streamlit UI for strategy management that avoids
all previous issues by using the NewStrategyManager which implements:
1. Direct file operations without Python imports
2. A robust session-based caching system
3. No module reloading
4. Proper error handling and recovery
5. A transaction-based approach for file modifications
"""

import json
import logging
import os
import inspect
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import streamlit as st

# Import the new strategy manager
from .new_strategy_manager import NewStrategyManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewStrategyUI:
    """
    New Streamlit UI for managing extraction strategies.
    
    This UI provides a completely rebuilt interface for viewing, editing,
    and deleting extraction strategies with robust error handling and
    a transaction-based approach to file modifications.
    """
    
    def __init__(self):
        """Initialize the new strategy UI."""
        self.manager = NewStrategyManager()
        
        # Initialize session state for UI
        if 'selected_strategy' not in st.session_state:
            st.session_state.selected_strategy = None
            
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = False
            
        if 'delete_confirmation' not in st.session_state:
            st.session_state.delete_confirmation = False
            
        if 'view_code' not in st.session_state:
            st.session_state.view_code = False
            
        if 'test_mode' not in st.session_state:
            st.session_state.test_mode = False
            
        if 'create_mode' not in st.session_state:
            st.session_state.create_mode = False
            
        if 'filter_category' not in st.session_state:
            st.session_state.filter_category = 'All'
            
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ''
            
        if 'operation_result' not in st.session_state:
            st.session_state.operation_result = None
            
        if 'operation_error' not in st.session_state:
            st.session_state.operation_error = None
            
        if 'api_tokens' not in st.session_state:
            st.session_state.api_tokens = {}
            
        if 'openrouter_models' not in st.session_state:
            st.session_state.openrouter_models = {}
    
    def show(self):
        """Display the strategy management UI."""
        st.title("Strategy Dashboard")
        
        # Add a refresh button
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🔄 Refresh"):
                self.manager.invalidate_cache()
                st.session_state.operation_result = "Cache refreshed"
                st.rerun()
        
        # Show operation result/error if any
        self._show_operation_feedback()
        
        # Get strategies
        strategies = self.manager.discover_strategies()
        
        # Show statistics
        self._show_statistics(strategies)
        
        # Show filters
        self._show_filters(strategies)
        
        # Apply filters
        filtered_strategies = self._apply_filters(strategies)
        
        # Show strategies
        self._show_strategies(filtered_strategies)
        
        # Show create button
        if not st.session_state.create_mode and not st.session_state.edit_mode:
            if st.button("➕ Create New Strategy"):
                st.session_state.create_mode = True
                st.rerun()
        
        # Show create form if in create mode
        if st.session_state.create_mode:
            self._show_create_form()
            
        # Show strategy details if one is selected
        if st.session_state.selected_strategy and not st.session_state.edit_mode and not st.session_state.test_mode:
            self._show_strategy_details(strategies[st.session_state.selected_strategy])
            
        # Show edit form if in edit mode
        if st.session_state.edit_mode and st.session_state.selected_strategy:
            self._show_edit_form(strategies[st.session_state.selected_strategy])
            
        # Show delete confirmation if needed
        if st.session_state.delete_confirmation and st.session_state.selected_strategy:
            self._show_delete_confirmation(st.session_state.selected_strategy)
            
        # Show code view if requested
        if st.session_state.view_code and st.session_state.selected_strategy:
            self._show_code_view(st.session_state.selected_strategy)
            
        # Show test form if in test mode
        if st.session_state.test_mode and st.session_state.selected_strategy:
            self._show_test_strategy(strategies[st.session_state.selected_strategy])
    
    def _show_operation_feedback(self):
        """Show operation result or error message."""
        if st.session_state.operation_result:
            st.success(st.session_state.operation_result)
            st.session_state.operation_result = None
            
        if st.session_state.operation_error:
            st.error(st.session_state.operation_error)
            st.session_state.operation_error = None
    
    def _show_statistics(self, strategies: Dict[str, Dict[str, Any]]):
        """Show statistics about strategies."""
        # Count strategies by category
        categories = {}
        for strategy in strategies.values():
            category = strategy.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
            
        # Display statistics
        st.subheader("Statistics")
        cols = st.columns(len(categories) + 1)
        
        with cols[0]:
            st.metric("Total Strategies", len(strategies))
            
        for i, (category, count) in enumerate(categories.items(), 1):
            with cols[i % len(cols)]:
                st.metric(f"{category.capitalize()}", count)
    
    def _show_filters(self, strategies: Dict[str, Dict[str, Any]]):
        """Show filter options for strategies."""
        st.subheader("Filters")
        
        # Get unique categories
        categories = set()
        for strategy in strategies.values():
            categories.add(strategy.get('category', 'unknown'))
            
        # Sort categories
        categories = sorted(list(categories))
        
        # Create filter columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Category filter
            category_options = ['All'] + categories
            st.session_state.filter_category = st.selectbox(
                "Category",
                category_options,
                index=category_options.index(st.session_state.filter_category)
            )
            
        with col2:
            # Search filter
            st.session_state.search_query = st.text_input(
                "Search",
                value=st.session_state.search_query
            )
    
    def _apply_filters(self, strategies: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Apply filters to strategies."""
        filtered = {}
        
        for name, strategy in strategies.items():
            # Apply category filter
            if st.session_state.filter_category != 'All' and strategy.get('category') != st.session_state.filter_category:
                continue
                
            # Apply search filter
            if st.session_state.search_query and st.session_state.search_query.lower() not in name.lower() and st.session_state.search_query.lower() not in strategy.get('description', '').lower():
                continue
                
            filtered[name] = strategy
            
        return filtered
    
    def _show_strategies(self, strategies: Dict[str, Dict[str, Any]]):
        """Show a list of strategies."""
        st.subheader("Strategies")
        
        if not strategies:
            st.info("No strategies found matching the filters.")
            return
            
        # Sort strategies by name
        sorted_strategies = sorted(strategies.items(), key=lambda x: x[0])
        
        # Create a card for each strategy
        for name, strategy in sorted_strategies:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Strategy name and description
                    st.markdown(f"**{name}**")
                    st.markdown(f"*{strategy.get('description', '')}*")
                    st.markdown(f"Category: {strategy.get('category', 'unknown')}")
                    
                with col2:
                    # Select button
                    if st.button("Select", key=f"select_{name}"):
                        st.session_state.selected_strategy = name
                        st.session_state.edit_mode = False
                        st.session_state.delete_confirmation = False
                        st.session_state.view_code = False
                        st.rerun()
                        
                st.divider()
    
    def _show_strategy_details(self, strategy: Dict[str, Any]):
        """Show details for a selected strategy."""
        st.subheader(f"Strategy: {strategy['name']}")
        
        # Strategy metadata
        st.markdown(f"**Description:** {strategy.get('description', '')}")
        st.markdown(f"**Category:** {strategy.get('category', 'unknown')}")
        st.markdown(f"**Default Provider:** {strategy.get('default_provider', 'openai')}")
        st.markdown(f"**Last Modified:** {strategy.get('last_modified', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Schema
        with st.expander("Schema"):
            st.json(strategy.get('schema', {}))
            
        # Instruction
        with st.expander("Instruction"):
            st.markdown(strategy.get('instruction', ''))
            
        # Action buttons
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("✏️ Edit"):
                st.session_state.edit_mode = True
                st.session_state.delete_confirmation = False
                st.session_state.view_code = False
                st.session_state.test_mode = False
                st.rerun()
                
        with col2:
            if st.button("🗑️ Delete"):
                st.session_state.delete_confirmation = True
                st.session_state.edit_mode = False
                st.session_state.view_code = False
                st.session_state.test_mode = False
                st.rerun()
                
        with col3:
            if st.button("👁️ View Code"):
                st.session_state.view_code = True
                st.session_state.edit_mode = False
                st.session_state.delete_confirmation = False
                st.session_state.test_mode = False
                st.rerun()
                
        with col4:
            if st.button("🧪 Test"):
                st.session_state.test_mode = True
                st.session_state.edit_mode = False
                st.session_state.delete_confirmation = False
                st.session_state.view_code = False
                st.rerun()
                
        with col5:
            if st.button("⬅️ Back"):
                st.session_state.selected_strategy = None
                st.session_state.edit_mode = False
                st.session_state.delete_confirmation = False
                st.session_state.view_code = False
                st.session_state.test_mode = False
                st.rerun()
    
    def _show_edit_form(self, strategy: Dict[str, Any]):
        """Show form for editing a strategy."""
        st.subheader(f"Edit Strategy: {strategy['name']}")
        
        # Create a form
        with st.form("edit_strategy_form"):
            # Description
            description = st.text_area(
                "Description",
                value=strategy.get('description', ''),
                height=100
            )
            
            # Default provider
            default_provider = st.selectbox(
                "Default Provider",
                ["openai", "anthropic", "google", "cohere", "mistral", "openrouter"],
                index=["openai", "anthropic", "google", "cohere", "mistral", "openrouter"].index(
                    strategy.get('default_provider', 'openai')
                ) if strategy.get('default_provider', 'openai') in ["openai", "anthropic", "google", "cohere", "mistral", "openrouter"] else 0
            )
            
            # Schema (as JSON)
            schema_json = st.text_area(
                "Schema (JSON)",
                value=json.dumps(strategy.get('schema', {}), indent=2),
                height=200
            )
            
            # Instruction
            instruction = st.text_area(
                "Instruction",
                value=strategy.get('instruction', ''),
                height=300
            )
            
            # Submit buttons
            col1, col2 = st.columns(2)
            
            with col1:
                submit = st.form_submit_button("💾 Save Changes")
                
            with col2:
                cancel = st.form_submit_button("❌ Cancel")
                
        # Handle form submission
        if submit:
            # Parse schema JSON
            try:
                schema = json.loads(schema_json)
            except json.JSONDecodeError as e:
                st.session_state.operation_error = f"Invalid JSON schema: {e}"
                return
                
            # Update strategy
            success, error = self.manager.update_strategy(
                strategy['name'],
                {
                    'description': description,
                    'default_provider': default_provider,
                    'schema': schema,
                    'instruction': instruction
                }
            )
            
            if success:
                st.session_state.operation_result = f"Strategy {strategy['name']} updated successfully"
                st.session_state.edit_mode = False
                st.rerun()
            else:
                st.session_state.operation_error = f"Error updating strategy: {error}"
                
        if cancel:
            st.session_state.edit_mode = False
            st.rerun()
    
    def _show_delete_confirmation(self, strategy_name: str):
        """Show confirmation dialog for deleting a strategy."""
        st.subheader("Delete Confirmation")
        st.warning(f"Are you sure you want to delete the strategy '{strategy_name}'? This action cannot be undone.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Yes, Delete"):
                success, error = self.manager.delete_strategy(strategy_name)
                
                if success:
                    st.session_state.operation_result = f"Strategy {strategy_name} deleted successfully"
                    st.session_state.selected_strategy = None
                    st.session_state.delete_confirmation = False
                    st.rerun()
                else:
                    st.session_state.operation_error = f"Error deleting strategy: {error}"
                    st.session_state.delete_confirmation = False
                    st.rerun()
                    
        with col2:
            if st.button("❌ No, Cancel"):
                st.session_state.delete_confirmation = False
                st.rerun()
    
    def _show_code_view(self, strategy_name: str):
        """Show the code for a strategy."""
        st.subheader("Strategy Code")
        
        code, error = self.manager.get_strategy_code(strategy_name)
        
        if code:
            st.code(code, language="python")
        else:
            st.error(f"Error getting code: {error}")
            
        if st.button("⬅️ Back to Details"):
            st.session_state.view_code = False
            st.rerun()
    
    def _show_create_form(self):
        """Show form for creating a new strategy."""
        st.subheader("Create New Strategy")
        
        # Create a form
        with st.form("create_strategy_form"):
            # Strategy name
            name = st.text_input(
                "Strategy Name",
                help="Name of the strategy class. The suffix 'LLMExtractionStrategy' will be automatically added if not already included (e.g., enter 'Crypto' to create 'CryptoLLMExtractionStrategy'). Special characters will be removed and spaces will be converted to underscores in the file name."
            )
            
            # Category
            category = st.selectbox(
                "Category",
                ["academic", "crypto", "financial", "news", "nft", "product", "social", "general"]
            )
            
            # Description
            description = st.text_area(
                "Description",
                height=100
            )
            
            # Default provider
            default_provider = st.selectbox(
                "Default Provider",
                ["openai", "anthropic", "google", "cohere", "mistral", "openrouter"]
            )
            
            # Schema (as JSON)
            schema_json = st.text_area(
                "Schema (JSON)",
                value="{}",
                height=200
            )
            
            # Instruction
            instruction = st.text_area(
                "Instruction",
                height=300
            )
            
            # Submit buttons
            col1, col2 = st.columns(2)
            
            with col1:
                submit = st.form_submit_button("💾 Create Strategy")
                
            with col2:
                cancel = st.form_submit_button("❌ Cancel")
                
        # Handle form submission
        if submit:
            # Validate name
            if not name:
                st.session_state.operation_error = "Strategy name is required"
                return
                
            # Parse schema JSON
            try:
                schema = json.loads(schema_json)
            except json.JSONDecodeError as e:
                st.session_state.operation_error = f"Invalid JSON schema: {e}"
                return
                
            # Create strategy
            success, result = self.manager.create_strategy(
                {
                    'name': name,
                    'category': category,
                    'description': description,
                    'default_provider': default_provider,
                    'schema': schema,
                    'instruction': instruction
                }
            )
            
            if success:
                # Extract the actual strategy class name from the result
                if isinstance(result, str) and result.startswith('/'):
                    # Result is a file path, extract the class name from the manager
                    try:
                        with open(result, 'r') as f:
                            content = f.read()
                        # Find the class name in the content
                        import re
                        pattern = r'class\s+(\w+)\s*\([^)]*LLMExtractionStrategy[^)]*\):'
                        match = re.search(pattern, content)
                        if match:
                            actual_name = match.group(1)
                        else:
                            actual_name = name
                    except Exception:
                        actual_name = name
                else:
                    actual_name = name
                    
                st.session_state.operation_result = f"Strategy {actual_name} created successfully"
                st.session_state.create_mode = False
                st.session_state.selected_strategy = actual_name
                st.rerun()
            else:
                st.session_state.operation_error = f"Error creating strategy: {result}"
                
        if cancel:
            st.session_state.create_mode = False
            st.rerun()


    def _show_test_strategy(self, strategy: Dict[str, Any]):
        """Show form for testing a strategy with LLM extraction."""
        st.subheader(f"Test Strategy: {strategy['name']}")
        
        # Create a back button
        if st.button("⬅️ Back to Strategy Details"):
            st.session_state.test_mode = False
            st.rerun()
        
        # Display strategy details in an expander
        with st.expander("Strategy Details", expanded=False):
            st.write(f"**Description:** {strategy.get('description', '')}")
            st.write(f"**Category:** {strategy.get('category', 'unknown')}")
            st.write(f"**Default Provider:** {strategy.get('default_provider', 'openai')}")
            
            # Display schema
            st.subheader("Schema")
            st.json(strategy.get('schema', {}))
            
            # Display instruction
            st.subheader("Instruction")
            st.code(strategy.get('instruction', ''), language="")
        
        # Provider selection
        st.subheader("Provider Configuration")
        
        # Default to the strategy's default provider
        default_provider = strategy.get('default_provider', 'openai')
        
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
                strategy_module = self._load_strategy_module(strategy.get('file_path'))
                if not strategy_module:
                    st.error(f"Failed to load strategy module from {strategy.get('file_path')}.")
                    return
                
                # Find the strategy class in the module
                try:
                    strategy_class = self._find_strategy_class(strategy_module, strategy.get('name'))
                except ValueError as e:
                    st.error(str(e))
                    return
                
                # Update progress
                progress_bar.progress(30)
                status_text.text("Creating strategy instance...")
                
                # Create the strategy instance
                try:
                    # Try relative import first
                    from ....extraction_strategies.factory import StrategyFactory
                except ImportError:
                    # Fall back to absolute import
                    try:
                        from src.cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory
                    except ImportError:
                        st.error("Could not import StrategyFactory. Please check your Python path.")
                        return
                
                factory = StrategyFactory()
                strategy_instance = factory.create_strategy(
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
                try:
                    # Try relative import first
                    from ....extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper
                except ImportError:
                    # Fall back to absolute import
                    try:
                        from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper
                    except ImportError:
                        st.error("Could not import SyncExtractionStrategyWrapper. Please check your Python path.")
                        return
                
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
                    file_name=f"{strategy['name']}_result.json",
                    mime="application/json",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Error during extraction: {str(e)}")
                logger.exception("Error during extraction")
            finally:
                progress_bar.progress(100)
    
    def _load_strategy_module(self, file_path: str):
        """Load a strategy module from file path."""
        try:
            # Get the absolute path to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up 5 levels to reach the project root (ui -> extraction_strategies -> crawl4ai -> cry_a_4mcp -> src -> root)
            project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..', '..'))
            
            # Add project root to sys.path if not already there
            import sys
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # Special case for test_strategy.py in the root directory
            if file_path.endswith('test_strategy.py') or os.path.basename(file_path) == 'test_strategy.py':
                try:
                    # Try to import directly from the root directory
                    return importlib.import_module('test_strategy')
                except ImportError as e:
                    logger.error(f"Error importing test_strategy.py: {e}")
            
            # Convert file path to module path
            if file_path.startswith('/'):
                # Handle absolute path
                # Find the position of 'extraction_strategies' in the path
                es_pos = file_path.find('extraction_strategies')
                if es_pos != -1:
                    # Extract the part after 'extraction_strategies'
                    rel_path = file_path[es_pos + len('extraction_strategies'):]
                    if rel_path.startswith('/'):
                        rel_path = rel_path[1:]
                    if rel_path.endswith('.py'):
                        rel_path = rel_path[:-3]
                    # Replace path separators with dots
                    module_path = rel_path.replace(os.sep, '.')
                    
                    # Try different import approaches
                    try:
                        # Try direct import first
                        return importlib.import_module(f"src.cry_a_4mcp.crawl4ai.extraction_strategies.{module_path}")
                    except ImportError:
                        try:
                            # Try without src prefix
                            return importlib.import_module(f"cry_a_4mcp.crawl4ai.extraction_strategies.{module_path}")
                        except ImportError:
                            # Try relative import
                            from .... import extraction_strategies
                            return importlib.import_module(f"....extraction_strategies.{module_path}", package=__name__)
            else:
                # Handle relative path
                module_path = file_path.replace(os.sep, '.')
                if module_path.endswith('.py'):
                    module_path = module_path[:-3]
                
                # Try different import approaches
                try:
                    # Try direct import with src prefix
                    return importlib.import_module(f"src.cry_a_4mcp.crawl4ai.extraction_strategies.{module_path}")
                except ImportError:
                    try:
                        # Try without src prefix
                        return importlib.import_module(f"cry_a_4mcp.crawl4ai.extraction_strategies.{module_path}")
                    except ImportError:
                        # Try relative import
                        from .... import extraction_strategies
                        return importlib.import_module(f"....extraction_strategies.{module_path}", package=__name__)
        except Exception as e:
            logger.error(f"Error loading strategy module: {e}")
            return None
            
    def _find_strategy_class(self, module, strategy_name: str):
        """Find a strategy class in a module.
        
        Args:
            module: The module to search in.
            strategy_name: The name of the strategy to find.
            
        Returns:
            The strategy class if found.
            
        Raises:
            ValueError: If the strategy class is not found.
        """
        # Log the module and available classes for debugging
        logger.info(f"Looking for strategy class in module: {module.__name__ if hasattr(module, '__name__') else 'unknown module'}")
        all_classes = inspect.getmembers(module, inspect.isclass)
        logger.info(f"Available classes: {[name for name, _ in all_classes]}")
        
        # Special case for TestStrategy
        if strategy_name == 'TestStrategy' or module.__name__ == 'test_strategy':
            for name, obj in all_classes:
                if name == 'TestStrategy':
                    logger.info(f"Found TestStrategy class: {obj}")
                    return obj
        
        # First, try to find a class with the exact name if provided
        if strategy_name:
            for name, obj in all_classes:
                if name == strategy_name:
                    # Check if it has the required attributes
                    if hasattr(obj, 'SCHEMA') and hasattr(obj, 'INSTRUCTION'):
                        logger.info(f"Found strategy class with exact name: {name}")
                        return obj
                    else:
                        logger.warning(f"Found class with name {name} but it's missing SCHEMA or INSTRUCTION attributes")
        
        # If no specific name is provided or the named class wasn't found,
        # look for any class with SCHEMA and INSTRUCTION attributes
        for name, obj in all_classes:
            if hasattr(obj, 'SCHEMA') and hasattr(obj, 'INSTRUCTION'):
                logger.info(f"Found strategy class with SCHEMA and INSTRUCTION: {name}")
                return obj
        
        # Log all available attributes in the module for debugging
        logger.error(f"No suitable strategy class found in module {module.__name__ if hasattr(module, '__name__') else 'unknown'}")
        logger.error(f"Module dir: {dir(module)}")
        
        raise ValueError(f"Strategy class not found in the module. Make sure it has SCHEMA and INSTRUCTION attributes.")
    
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
                    from .openrouter_utils import get_openrouter_models, format_openrouter_models
                    
                    # Check if we have cached models in session state
                    if "openrouter_models" not in st.session_state:
                        st.session_state.openrouter_models = {}
                    
                    # Use cached models if available and not expired
                    if api_key in st.session_state.openrouter_models:
                        return [model["id"] for model in st.session_state.openrouter_models[api_key]]
                    
                    # Run the async function to get models
                    import asyncio
                    success, models_data, message = asyncio.run(get_openrouter_models(api_key))
                    
                    if success and models_data:
                        # Format and cache the models
                        formatted_models = format_openrouter_models(models_data)
                        st.session_state.openrouter_models[api_key] = formatted_models
                        # Return just the model IDs for the dropdown
                        return [model["id"] for model in formatted_models]
                    else:
                        logger.error(f"Error getting OpenRouter models: {message}")
                except Exception as e:
                    logger.error(f"Error getting OpenRouter models: {e}")
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
    
    def _save_api_keys(self):
        """Save API keys to file."""
        if "api_tokens" in st.session_state:
            from .openrouter_utils import save_api_keys_to_file
            config_dir = Path(__file__).parent / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            api_keys_file = config_dir / "api_keys.json"
            save_api_keys_to_file(st.session_state.api_tokens, str(api_keys_file))


def show_new_strategy_management():
    """Show the new strategy management UI."""
    ui = NewStrategyUI()
    ui.show()


if __name__ == "__main__":
    show_new_strategy_management()