#!/usr/bin/env python3
"""
New Strategy Manager with robust edit/delete functionality.

This module provides a completely rebuilt approach to strategy management that avoids
all previous issues by:
1. Using direct file operations without Python imports
2. Implementing a robust session-based caching system
3. Avoiding module reloading entirely
4. Providing proper error handling and recovery
5. Using a transaction-based approach for file modifications
"""

import json
import logging
import os
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set

import streamlit as st

# Import database components
from .database.strategy_db_manager import StrategyDatabaseManager
from .templates.strategy_generator import StrategyTemplateGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewStrategyManager:
    """
    New strategy manager that handles edit/delete operations
    with a completely rebuilt architecture.
    
    This manager uses direct file operations and a robust session-based
    caching system to provide reliable strategy management functionality.
    """
    
    def __init__(self):
        """Initialize the new strategy manager."""
        self.db_manager = StrategyDatabaseManager()
        self.generator = StrategyTemplateGenerator()
        self.base_strategies_dir = Path(__file__).parent.parent
        
        # Initialize session state for strategy cache
        if 'strategy_cache' not in st.session_state:
            st.session_state.strategy_cache = {}
            
        if 'cache_timestamp' not in st.session_state:
            st.session_state.cache_timestamp = datetime.now()
            
        if 'file_operation_lock' not in st.session_state:
            st.session_state.file_operation_lock = False
            
        # Track modified files to avoid reloading issues
        if 'modified_files' not in st.session_state:
            st.session_state.modified_files = set()
    
    def discover_strategies(self, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Discover strategies by scanning the filesystem directly.
        
        Args:
            force_refresh: Force a refresh of the cache
            
        Returns:
            Dictionary mapping strategy names to their metadata
        """
        # Check if cache needs refresh
        now = datetime.now()
        cache_age = (now - st.session_state.cache_timestamp).seconds
        
        if not force_refresh and cache_age < 300 and st.session_state.strategy_cache:
            return st.session_state.strategy_cache
        
        strategies = {}
        
        # Categories to scan
        categories = [
            "academic", "composite", "crypto", "financial", "news", 
            "nft", "product", "social", "general", "workflow"
        ]
        
        for category in categories:
            category_dir = self.base_strategies_dir / category
            
            if not category_dir.exists():
                continue
                
            logger.debug(f"Scanning category: {category}")
            
            # Scan Python files in category
            for py_file in category_dir.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                    
                # Skip files that have been modified in this session
                if str(py_file.absolute()) in st.session_state.modified_files:
                    logger.debug(f"Skipping modified file: {py_file}")
                    continue
                    
                try:
                    strategy_info = self._extract_strategy_info(py_file, category)
                    if strategy_info:
                        strategies[strategy_info['name']] = strategy_info
                        logger.debug(f"Found strategy: {strategy_info['name']}")
                except Exception as e:
                    logger.warning(f"Error reading strategy file {py_file}: {e}")
        
        # Update cache
        st.session_state.strategy_cache = strategies
        st.session_state.cache_timestamp = now
        
        return strategies
    
    def _extract_strategy_info(self, file_path: Path, category: str) -> Optional[Dict[str, Any]]:
        """
        Extract strategy information from a Python file.
        
        Args:
            file_path: Path to the strategy file
            category: Category of the strategy
            
        Returns:
            Dictionary containing strategy information or None if not a valid strategy
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract class name
            class_name = self._find_strategy_class_name(content)
            if not class_name:
                return None
                
            # Extract schema and instruction
            schema = self._extract_schema(content)
            instruction = self._extract_instruction(content)
            
            # Extract docstring for description
            description = self._extract_class_docstring(content, class_name)
            
            # Extract default provider
            default_provider = self._extract_default_provider(content)
            
            return {
                'name': class_name,
                'description': description or f"Extraction strategy for {category} content",
                'category': category,
                'file_path': str(file_path.absolute()),
                'schema': schema or {},
                'instruction': instruction or "",
                'default_provider': default_provider or 'openai',
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime)
            }
            
        except Exception as e:
            logger.error(f"Error extracting info from {file_path}: {e}")
            return None
    
    def _find_strategy_class_name(self, content: str) -> Optional[str]:
        """
        Find the main strategy class name in the file content.
        
        Args:
            content: File content as string
            
        Returns:
            Class name or None if not found
        """
        # Look for class that inherits from LLMExtractionStrategy
        pattern = r'class\s+(\w+)\s*\([^)]*LLMExtractionStrategy[^)]*\):'
        match = re.search(pattern, content)
        
        if match:
            return match.group(1)
            
        return None
    
    def _extract_schema(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract the schema definition from file content.
        
        Args:
            content: File content as string
            
        Returns:
            Schema dictionary or None if not found
        """
        # Find schema variable assignment
        schema_pattern = r'(\w+_schema)\s*=\s*(\{[^}]+\}(?:\s*\})*)'  
        
        # More sophisticated approach to extract multi-line schema
        lines = content.split('\n')
        schema_start = None
        brace_count = 0
        schema_lines = []
        
        for i, line in enumerate(lines):
            if '_schema = {' in line or '_schema={' in line:
                schema_start = i
                schema_lines = [line]
                brace_count = line.count('{') - line.count('}')
                continue
                
            if schema_start is not None:
                schema_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                
                if brace_count == 0:
                    # End of schema definition
                    break
        
        if schema_lines:
            try:
                # Join lines and extract the dictionary part
                schema_text = '\n'.join(schema_lines)
                # Find the dictionary part
                start_idx = schema_text.find('{')
                if start_idx != -1:
                    dict_text = schema_text[start_idx:]
                    # Try to evaluate as Python dict (controlled environment)
                    schema = eval(dict_text)
                    return schema
            except Exception as e:
                logger.debug(f"Could not parse schema: {e}")
                
        return None
    
    def _extract_instruction(self, content: str) -> Optional[str]:
        """
        Extract the instruction string from file content.
        
        Args:
            content: File content as string
            
        Returns:
            Instruction string or None if not found
        """
        # Look for instruction assignment with different quote styles
        patterns = [
            r'instruction\s*=\s*"""([^"]*(?:"[^"][^"]*)*)"""\'?',
            r'instruction\s*=\s*\'\'\'([^\']*(?:\'[^\'][^\']*)*)\'\'\'\'?',
            r'instruction\s*=\s*"([^"]*(?:"[^"][^"]*)*)"\'?',
            r'instruction\s*=\s*\'([^\']*(?:\'[^\'][^\']*)*)\'\'?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
                
        return None
    
    def _extract_class_docstring(self, content: str, class_name: str) -> Optional[str]:
        """
        Extract the docstring from a class definition.
        
        Args:
            content: File content as string
            class_name: Name of the class
            
        Returns:
            Docstring or None if not found
        """
        # Pattern to find class and its docstring
        pattern = f'class\s+{re.escape(class_name)}[^:]*:\s*"""([^"]+)"""'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
            
        return None
    
    def _extract_default_provider(self, content: str) -> Optional[str]:
        """
        Extract the default provider from the __init__ method.
        
        Args:
            content: File content as string
            
        Returns:
            Default provider or None if not found
        """
        # Look for provider parameter in __init__
        pattern = r'def\s+__init__[^:]*:\s*[^\n]*\s*provider:\s*str\s*=\s*["\']([^"\']*)'
        match = re.search(pattern, content)
        
        if match:
            return match.group(1)
            
        return 'openai'  # Default fallback
    
    def invalidate_cache(self):
        """
        Invalidate the strategy cache to force refresh.
        """
        st.session_state.strategy_cache = {}
        st.session_state.cache_timestamp = datetime.now()
    
    def update_strategy(self, strategy_name: str, updated_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Update a strategy file with new data using a transaction-based approach.
        
        Args:
            strategy_name: Name of the strategy to update
            updated_data: Dictionary containing updated strategy data
            
        Returns:
            Tuple of (success, error_message)
        """
        # Check if another file operation is in progress
        if st.session_state.file_operation_lock:
            return False, "Another file operation is in progress. Please try again."
        
        # Set the lock
        st.session_state.file_operation_lock = True
        
        try:
            # Get current strategy info
            strategies = self.discover_strategies()
            if strategy_name not in strategies:
                st.session_state.file_operation_lock = False
                return False, f"Strategy {strategy_name} not found"
                
            strategy_info = strategies[strategy_name]
            file_path = Path(strategy_info['file_path'])
            
            # Create backup directory if it doesn't exist
            backup_dir = file_path.parent / '.backups'
            backup_dir.mkdir(exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{file_path.stem}_{timestamp}.py.bak"
            
            # Copy file to backup
            shutil.copy2(file_path, backup_path)
            
            # Create a temporary file for the new content
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp_file:
                temp_path = temp_file.name
                
                # Generate new strategy file content
                new_content = self.generator.generate_strategy_content(
                    strategy_name=strategy_name,
                    strategy_description=updated_data.get('description', strategy_info['description']),
                    schema=updated_data.get('schema', strategy_info['schema']),
                    instruction=updated_data.get('instruction', strategy_info['instruction']),
                    default_provider=updated_data.get('default_provider', strategy_info['default_provider']),
                    category=updated_data.get('category', strategy_info['category'])
                )
                
                # Write to temporary file
                temp_file.write(new_content)
            
            # Validate the temporary file
            is_valid, error = self._validate_python_syntax(temp_path)
            if not is_valid:
                # Remove temporary file
                os.unlink(temp_path)
                st.session_state.file_operation_lock = False
                return False, f"Invalid Python syntax: {error}"
            
            # Replace the original file with the temporary file
            shutil.move(temp_path, file_path)
            
            # Update database
            self.db_manager.update_strategy(strategy_name, updated_data)
            
            # DON'T add to modified files set so the updated strategy can be loaded immediately
            # Instead, remove it from the set if it was there
            file_path_str = str(file_path.absolute())
            if file_path_str in st.session_state.modified_files:
                st.session_state.modified_files.remove(file_path_str)
            
            # Invalidate cache
            self.invalidate_cache()
            
            logger.info(f"Successfully updated strategy: {strategy_name}")
            st.session_state.file_operation_lock = False
            return True, None
            
        except Exception as e:
            logger.error(f"Error updating strategy {strategy_name}: {e}")
            st.session_state.file_operation_lock = False
            return False, str(e)
    
    def delete_strategy(self, strategy_name: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a strategy file and remove it from the database.
        
        Args:
            strategy_name: Name of the strategy to delete
            
        Returns:
            Tuple of (success, error_message)
        """
        # Check if another file operation is in progress
        if st.session_state.file_operation_lock:
            return False, "Another file operation is in progress. Please try again."
        
        # Set the lock
        st.session_state.file_operation_lock = True
        
        try:
            # Get current strategy info
            strategies = self.discover_strategies()
            if strategy_name not in strategies:
                st.session_state.file_operation_lock = False
                return False, f"Strategy {strategy_name} not found"
                
            strategy_info = strategies[strategy_name]
            file_path = Path(strategy_info['file_path'])
            
            # Create deleted strategies directory if it doesn't exist
            deleted_dir = file_path.parent / '.deleted'
            deleted_dir.mkdir(exist_ok=True)
            
            # Create timestamped backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            deleted_path = deleted_dir / f"{file_path.stem}_{timestamp}.py.deleted"
            
            # Move file to deleted directory
            shutil.move(str(file_path), str(deleted_path))
            
            # Remove from database
            self.db_manager.delete_strategy(strategy_name)
            
            # DON'T add to modified files set so the new strategy can be loaded immediately
            # Instead, ensure it's not in the set
            file_path_str = str(file_path.absolute())
            if file_path_str in st.session_state.modified_files:
                st.session_state.modified_files.remove(file_path_str)
            
            # Invalidate cache
            self.invalidate_cache()
            
            logger.info(f"Successfully deleted strategy: {strategy_name} (moved to {deleted_path})")
            st.session_state.file_operation_lock = False
            return True, None
            
        except Exception as e:
            logger.error(f"Error deleting strategy {strategy_name}: {e}")
            st.session_state.file_operation_lock = False
            return False, str(e)
    
    def _validate_python_syntax(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a file has correct Python syntax.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try to compile the code
            compile(content, file_path, 'exec')
            return True, None
            
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def get_strategy_code(self, strategy_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the code for a strategy.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Tuple of (code, error_message)
        """
        try:
            strategies = self.discover_strategies()
            if strategy_name not in strategies:
                return None, f"Strategy {strategy_name} not found"
                
            strategy_info = strategies[strategy_name]
            file_path = strategy_info['file_path']
            
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                
            return code, None
            
        except Exception as e:
            logger.error(f"Error getting code for strategy {strategy_name}: {e}")
            return None, str(e)
    
    def create_strategy(self, strategy_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Create a new strategy file.
        
        Args:
            strategy_data: Dictionary containing strategy data
            
        Returns:
            Tuple of (success, error_message or file_path)
        """
        # Check if another file operation is in progress
        if st.session_state.file_operation_lock:
            return False, "Another file operation is in progress. Please try again."
        
        # Set the lock
        st.session_state.file_operation_lock = True
        
        try:
            # Extract required fields
            strategy_name = strategy_data.get('name')
            category = strategy_data.get('category', 'general')
            description = strategy_data.get('description', '')
            schema = strategy_data.get('schema', {})
            instruction = strategy_data.get('instruction', '')
            default_provider = strategy_data.get('default_provider', 'openai')
            
            if not strategy_name:
                st.session_state.file_operation_lock = False
                return False, "Strategy name is required"
                
            # Check if strategy already exists
            strategies = self.discover_strategies()
            
            # Determine the actual strategy class name that will be used
            strategy_name_clean = self.generator._clean_name(strategy_name)
            if not strategy_name_clean.endswith('LLMExtractionStrategy'):
                strategy_class_name = f"{strategy_name_clean}LLMExtractionStrategy"
            else:
                strategy_class_name = strategy_name_clean
                
            if strategy_class_name in strategies:
                st.session_state.file_operation_lock = False
                return False, f"Strategy {strategy_class_name} already exists"
            
            # Create category directory if it doesn't exist
            category_dir = self.base_strategies_dir / category
            category_dir.mkdir(exist_ok=True)
            
            # Create __init__.py if it doesn't exist
            init_file = category_dir / "__init__.py"
            if not init_file.exists():
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(f"#!/usr/bin/env python3\n"
                           f"\"\"\" {category.capitalize()} extraction strategies. \"\"\"\n"
                           f"# Import strategies\n")
            
            # Generate file path
            # Clean the strategy name for file naming
            clean_name = re.sub(r'[^\w\s]', '', strategy_name)
            clean_name = clean_name.replace(' ', '_').lower()
            file_name = f"{clean_name}.py"
            file_path = category_dir / file_name
            
            # Generate strategy content
            content = self.generator.generate_strategy_content(
                strategy_name=strategy_name,
                strategy_description=description,
                schema=schema,
                instruction=instruction,
                default_provider=default_provider,
                category=category
            )
            
            # Create a temporary file for validation
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp_file:
                temp_path = temp_file.name
                temp_file.write(content)
            
            # Validate the temporary file
            is_valid, error = self._validate_python_syntax(temp_path)
            if not is_valid:
                # Remove temporary file
                os.unlink(temp_path)
                st.session_state.file_operation_lock = False
                return False, f"Invalid Python syntax: {error}"
            
            # Write to actual file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Add to database
            # Use the class name as the strategy name in the database
            # This ensures consistency between the file content and database
            strategy_name_clean = self.generator._clean_name(strategy_name)
            if not strategy_name_clean.endswith('LLMExtractionStrategy'):
                db_strategy_name = f"{strategy_name_clean}LLMExtractionStrategy"
            else:
                db_strategy_name = strategy_name_clean
                
            self.db_manager.add_strategy({
                'name': db_strategy_name,
                'description': description,
                'category': category,
                'file_path': str(file_path.absolute()),
                'schema': schema,
                'instruction': instruction,
                'default_provider': default_provider,
                'last_modified': datetime.now()
            })
            
            # DON'T add to modified files set so the new strategy can be loaded immediately
            # Instead, ensure it's not in the set
            file_path_str = str(file_path.absolute())
            if file_path_str in st.session_state.modified_files:
                st.session_state.modified_files.remove(file_path_str)
            
            # Invalidate cache
            self.invalidate_cache()
            
            # Remove temporary file
            os.unlink(temp_path)
            
            logger.info(f"Successfully created strategy: {strategy_name}")
            st.session_state.file_operation_lock = False
            return True, str(file_path.absolute())
            
        except Exception as e:
            logger.error(f"Error creating strategy: {e}")
            st.session_state.file_operation_lock = False
            return False, str(e)