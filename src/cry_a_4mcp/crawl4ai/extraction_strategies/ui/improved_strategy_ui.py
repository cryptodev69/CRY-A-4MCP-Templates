#!/usr/bin/env python3
"""
Improved Strategy Management UI.

This module provides a robust user interface for strategy management
that uses the improved strategy manager to avoid module cache issues.
"""

import json
import logging
import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime

from .improved_strategy_manager import ImprovedStrategyManager
from .database.strategy_db_manager import StrategyDatabaseManager
from .templates.strategy_generator import StrategyTemplateGenerator

# Configure logging
logger = logging.getLogger(__name__)

class ImprovedStrategyUI:
    """
    Improved strategy management UI that provides robust edit/delete functionality.
    """
    
    def __init__(self):
        """Initialize the improved strategy UI."""
        self.manager = ImprovedStrategyManager()
        self.db_manager = StrategyDatabaseManager()
        self.generator = StrategyTemplateGenerator()
    
    def show_strategy_management_interface(self):
        """
        Display the main strategy management interface.
        """
        st.title("🔧 Improved Strategy Management")
        st.markdown("---")
        
        # Add refresh button
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔄 Refresh Strategies", help="Refresh strategy list from filesystem"):
                self.manager.invalidate_cache()
                st.rerun()
        
        with col2:
            if st.button("📊 Show Statistics", help="Show strategy statistics"):
                self._show_strategy_statistics()
        
        # Get strategies from improved manager
        strategies = self.manager.get_cached_strategies()
        
        if not strategies:
            st.warning("No strategies found. Please check your strategy files.")
            return
        
        st.success(f"Found {len(strategies)} strategies")
        
        # Strategy selection
        strategy_names = list(strategies.keys())
        selected_strategy = st.selectbox(
            "Select Strategy to Manage:",
            strategy_names,
            help="Choose a strategy to view, edit, or delete"
        )
        
        if selected_strategy:
            self._show_strategy_details(selected_strategy, strategies[selected_strategy])
    
    def _show_strategy_statistics(self):
        """
        Display strategy statistics.
        """
        strategies = self.manager.get_cached_strategies()
        
        if not strategies:
            st.info("No strategies to analyze.")
            return
        
        # Count by category
        categories = {}
        for strategy in strategies.values():
            category = strategy.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        
        st.subheader("📊 Strategy Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Strategies", len(strategies))
            st.metric("Categories", len(categories))
        
        with col2:
            st.write("**Strategies by Category:**")
            for category, count in sorted(categories.items()):
                st.write(f"• {category.title()}: {count}")
    
    def _show_strategy_details(self, strategy_name: str, strategy_info: Dict[str, Any]):
        """
        Display detailed information about a strategy and provide edit/delete options.
        
        Args:
            strategy_name: Name of the strategy
            strategy_info: Strategy information dictionary
        """
        st.subheader(f"Strategy: {strategy_name}")
        
        # Display basic info
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Category:** {strategy_info.get('category', 'Unknown')}")
            st.write(f"**File:** {strategy_info.get('file_path', 'Unknown')}")
        
        with col2:
            last_modified = strategy_info.get('last_modified')
            if last_modified:
                st.write(f"**Last Modified:** {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Provider:** {strategy_info.get('default_provider', 'openai')}")
        
        # Description
        st.write(f"**Description:** {strategy_info.get('description', 'No description available')}")
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"✏️ Edit {strategy_name}", key=f"edit_{strategy_name}"):
                st.session_state[f"editing_{strategy_name}"] = True
                st.rerun()
        
        with col2:
            if st.button(f"🗑️ Delete {strategy_name}", key=f"delete_{strategy_name}"):
                st.session_state[f"deleting_{strategy_name}"] = True
                st.rerun()
        
        with col3:
            if st.button(f"📋 View Code", key=f"view_{strategy_name}"):
                self._show_strategy_code(strategy_info)
        
        # Handle edit mode
        if st.session_state.get(f"editing_{strategy_name}", False):
            self._show_edit_interface(strategy_name, strategy_info)
        
        # Handle delete confirmation
        if st.session_state.get(f"deleting_{strategy_name}", False):
            self._show_delete_confirmation(strategy_name, strategy_info)
    
    def _show_strategy_code(self, strategy_info: Dict[str, Any]):
        """
        Display the strategy code in a code block.
        
        Args:
            strategy_info: Strategy information dictionary
        """
        file_path = strategy_info.get('file_path')
        if not file_path:
            st.error("File path not available")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            st.subheader("📋 Strategy Code")
            st.code(code_content, language='python')
            
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    def _show_edit_interface(self, strategy_name: str, strategy_info: Dict[str, Any]):
        """
        Display the edit interface for a strategy.
        
        Args:
            strategy_name: Name of the strategy
            strategy_info: Strategy information dictionary
        """
        st.markdown("---")
        st.subheader(f"✏️ Editing: {strategy_name}")
        
        with st.form(f"edit_form_{strategy_name}"):
            # Editable fields
            new_description = st.text_area(
                "Description:",
                value=strategy_info.get('description', ''),
                height=100
            )
            
            new_provider = st.selectbox(
                "Default Provider:",
                ['openai', 'anthropic', 'google', 'local'],
                index=['openai', 'anthropic', 'google', 'local'].index(
                    strategy_info.get('default_provider', 'openai')
                )
            )
            
            # Schema editing
            st.write("**Schema Configuration:**")
            current_schema = strategy_info.get('schema', {})
            schema_json = st.text_area(
                "Schema (JSON format):",
                value=json.dumps(current_schema, indent=2) if current_schema else '{}',
                height=200,
                help="Define the JSON schema for extracted data"
            )
            
            # Instruction editing
            st.write("**Extraction Instructions:**")
            new_instruction = st.text_area(
                "Instructions:",
                value=strategy_info.get('instruction', ''),
                height=150,
                help="Provide detailed instructions for the LLM"
            )
            
            # Form buttons
            col1, col2 = st.columns(2)
            
            with col1:
                submit_edit = st.form_submit_button("💾 Save Changes", type="primary")
            
            with col2:
                cancel_edit = st.form_submit_button("❌ Cancel")
            
            if submit_edit:
                self._handle_strategy_update(strategy_name, {
                    'description': new_description,
                    'default_provider': new_provider,
                    'schema': self._parse_schema_json(schema_json),
                    'instruction': new_instruction
                })
            
            if cancel_edit:
                st.session_state[f"editing_{strategy_name}"] = False
                st.rerun()
    
    def _parse_schema_json(self, schema_json: str) -> Dict[str, Any]:
        """
        Parse schema JSON string safely.
        
        Args:
            schema_json: JSON string
            
        Returns:
            Parsed dictionary or empty dict if invalid
        """
        try:
            return json.loads(schema_json)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON schema: {e}")
            return {}
    
    def _handle_strategy_update(self, strategy_name: str, updated_data: Dict[str, Any]):
        """
        Handle strategy update using the improved manager.
        
        Args:
            strategy_name: Name of the strategy to update
            updated_data: Updated strategy data
        """
        try:
            # Validate schema if provided
            if 'schema' in updated_data and updated_data['schema']:
                if not isinstance(updated_data['schema'], dict):
                    st.error("Schema must be a valid JSON object")
                    return
            
            # Update using improved manager
            success = self.manager.update_strategy_file(strategy_name, updated_data)
            
            if success:
                st.success(f"✅ Successfully updated strategy: {strategy_name}")
                st.session_state[f"editing_{strategy_name}"] = False
                
                # Show success message with details
                st.info("Changes saved successfully! The strategy file has been updated.")
                
                # Refresh the page after a short delay
                st.rerun()
            else:
                st.error(f"❌ Failed to update strategy: {strategy_name}")
                st.error("Please check the logs for more details.")
                
        except Exception as e:
            st.error(f"Error updating strategy: {e}")
            logger.error(f"Error updating strategy {strategy_name}: {e}")
    
    def _show_delete_confirmation(self, strategy_name: str, strategy_info: Dict[str, Any]):
        """
        Display delete confirmation dialog.
        
        Args:
            strategy_name: Name of the strategy
            strategy_info: Strategy information dictionary
        """
        st.markdown("---")
        st.subheader(f"🗑️ Delete Confirmation")
        
        st.warning(f"Are you sure you want to delete the strategy '{strategy_name}'?")
        st.write("This action will:")
        st.write("• Move the strategy file to a backup location")
        st.write("• Remove the strategy from the database")
        st.write("• Make the strategy unavailable for use")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"🗑️ Yes, Delete {strategy_name}", key=f"confirm_delete_{strategy_name}", type="primary"):
                self._handle_strategy_deletion(strategy_name)
        
        with col2:
            if st.button("❌ Cancel", key=f"cancel_delete_{strategy_name}"):
                st.session_state[f"deleting_{strategy_name}"] = False
                st.rerun()
    
    def _handle_strategy_deletion(self, strategy_name: str):
        """
        Handle strategy deletion using the improved manager.
        
        Args:
            strategy_name: Name of the strategy to delete
        """
        try:
            success = self.manager.delete_strategy_file(strategy_name)
            
            if success:
                st.success(f"✅ Successfully deleted strategy: {strategy_name}")
                st.info("The strategy file has been moved to a backup location and removed from the database.")
                
                # Clear session state
                st.session_state[f"deleting_{strategy_name}"] = False
                
                # Refresh the page
                st.rerun()
            else:
                st.error(f"❌ Failed to delete strategy: {strategy_name}")
                st.error("Please check the logs for more details.")
                
        except Exception as e:
            st.error(f"Error deleting strategy: {e}")
            logger.error(f"Error deleting strategy {strategy_name}: {e}")

def show_improved_strategy_management():
    """
    Main function to display the improved strategy management interface.
    """
    ui = ImprovedStrategyUI()
    ui.show_strategy_management_interface()

if __name__ == "__main__":
    show_improved_strategy_management()