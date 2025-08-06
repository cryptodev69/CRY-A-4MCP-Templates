#!/usr/bin/env python3
"""
Improved Strategy Manager with robust edit/delete functionality.

This module provides a better approach to strategy management that avoids
the module cache issues of the previous implementation by:
1. Using file-based operations without Python imports
2. Implementing session-based strategy discovery
3. Avoiding problematic module reloading
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import streamlit as st
from datetime import datetime

# Import database components
from .database.strategy_db_manager import StrategyDatabaseManager
from .templates.strategy_generator import StrategyTemplateGenerator

# Configure logging
logger = logging.getLogger(__name__)

class ImprovedStrategyManager:
    """
    Improved strategy manager that handles edit/delete operations
    without relying on problematic module reloading.
    
    This manager uses file-based operations and session-based caching
    to provide robust strategy management functionality.
    """
    
    def __init__(self):
        """Initialize the improved strategy manager."""
        self.db_manager = StrategyDatabaseManager()
        self.generator = StrategyTemplateGenerator()
        self.base_strategies_dir = Path(__file__).parent.parent
        
        # Session-based strategy cache
        if 'strategy_cache' not in st.session_state:
            st.session_state.strategy_cache = {}
            
        if 'cache_timestamp' not in st.session_state:
            st.session_state.cache_timestamp = datetime.now()
    
    def discover_strategies_from_filesystem(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover strategies by scanning the filesystem directly.
        
        This method avoids Python imports and instead reads strategy files
        directly to extract metadata and configuration.
        
        Returns:
            Dictionary mapping strategy names to their metadata
        """
        strategies = {}
        
        # Categories to scan
        categories = [
            "academic", "crypto", "financial", "news", 
            "nft", "product", "social", "general"
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
                    
                try:
                    strategy_info = self._extract_strategy_info_from_file(py_file, category)
                    if strategy_info:
                        strategies[strategy_info['name']] = strategy_info
                        logger.debug(f"Found strategy: {strategy_info['name']}")
                except Exception as e:
                    logger.warning(f"Error reading strategy file {py_file}: {e}")
                    
        return strategies
    
    def _extract_strategy_info_from_file(self, file_path: Path, category: str) -> Optional[Dict[str, Any]]:
        """
        Extract strategy information from a Python file without importing it.
        
        Args:
            file_path: Path to the strategy file
            category: Category of the strategy
            
        Returns:
            Dictionary containing strategy information or None if not a valid strategy
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for class definition
            class_name = self._find_strategy_class_name(content)
            if not class_name:
                return None
                
            # Extract schema and instruction
            schema = self._extract_schema_from_content(content)
            instruction = self._extract_instruction_from_content(content)
            
            # Extract docstring for description
            description = self._extract_class_docstring(content, class_name)
            
            return {
                'name': class_name,
                'description': description or f"Extraction strategy for {category} content",
                'category': category,
                'file_path': str(file_path.absolute()),
                'schema': schema or {},
                'instruction': instruction or "",
                'default_provider': 'openai',  # Default value
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
        import re
        
        # Look for class that inherits from LLMExtractionStrategy
        pattern = r'class\s+(\w+)\s*\([^)]*LLMExtractionStrategy[^)]*\):'
        match = re.search(pattern, content)
        
        if match:
            return match.group(1)
            
        return None
    
    def _extract_schema_from_content(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract the schema definition from file content.
        
        Args:
            content: File content as string
            
        Returns:
            Schema dictionary or None if not found
        """
        import re
        
        # Look for schema assignment
        pattern = r'(\w+_schema)\s*=\s*(\{[^}]+\}(?:\s*\})*)'  # Simple pattern for now
        
        # More sophisticated approach: find the schema variable
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
                    # Try to evaluate as Python dict (unsafe but controlled environment)
                    schema = eval(dict_text)
                    return schema
            except Exception as e:
                logger.debug(f"Could not parse schema: {e}")
                
        return None
    
    def _extract_instruction_from_content(self, content: str) -> Optional[str]:
        """
        Extract the instruction string from file content.
        
        Args:
            content: File content as string
            
        Returns:
            Instruction string or None if not found
        """
        import re
        
        # Look for instruction assignment
        patterns = [
            r'instruction\s*=\s*"""([^"]+)"""',
            r'instruction\s*=\s*\'\'\'([^\']+)\'\'\'',
            r'instruction\s*=\s*"([^"]+)"',
            r'instruction\s*=\s*\'([^\']+)\''
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
        import re
        
        # Pattern to find class and its docstring
        pattern = f'class\s+{re.escape(class_name)}[^:]*:\s*"""([^"]+)"""'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
            
        return None
    
    def get_cached_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Get strategies from session cache, refreshing if needed.
        
        Returns:
            Dictionary of cached strategies
        """
        # Check if cache needs refresh (every 5 minutes)
        now = datetime.now()
        if (now - st.session_state.cache_timestamp).seconds > 300:
            st.session_state.strategy_cache = self.discover_strategies_from_filesystem()
            st.session_state.cache_timestamp = now
            
        return st.session_state.strategy_cache
    
    def invalidate_cache(self):
        """
        Invalidate the strategy cache to force refresh.
        """
        st.session_state.strategy_cache = {}
        st.session_state.cache_timestamp = datetime.now()
    
    def update_strategy_file(self, strategy_name: str, updated_data: Dict[str, Any]) -> bool:
        """
        Update a strategy file with new data without using module imports.
        
        Args:
            strategy_name: Name of the strategy to update
            updated_data: Dictionary containing updated strategy data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current strategy info
            strategies = self.get_cached_strategies()
            if strategy_name not in strategies:
                logger.error(f"Strategy {strategy_name} not found in cache")
                return False
                
            strategy_info = strategies[strategy_name]
            file_path = Path(strategy_info['file_path'])
            
            # Create backup
            backup_path = file_path.with_suffix('.py.backup')
            shutil.copy2(file_path, backup_path)
            
            try:
                # Generate new strategy file content
                new_content = self.generator.generate_strategy_content(
                    strategy_name=strategy_name,
                    strategy_description=updated_data.get('description', strategy_info['description']),
                    schema=updated_data.get('schema', strategy_info['schema']),
                    instruction=updated_data.get('instruction', strategy_info['instruction']),
                    default_provider=updated_data.get('default_provider', strategy_info['default_provider']),
                    category=updated_data.get('category', strategy_info['category'])
                )
                
                # Write new content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                # Update database
                self.db_manager.update_strategy(strategy_name, updated_data)
                
                # Invalidate cache
                self.invalidate_cache()
                
                # Remove backup on success
                backup_path.unlink()
                
                logger.info(f"Successfully updated strategy: {strategy_name}")
                return True
                
            except Exception as e:
                # Restore from backup on error
                shutil.copy2(backup_path, file_path)
                backup_path.unlink()
                logger.error(f"Error updating strategy file, restored from backup: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating strategy {strategy_name}: {e}")
            return False
    
    def delete_strategy_file(self, strategy_name: str) -> bool:
        """
        Delete a strategy file and remove it from the database.
        
        Args:
            strategy_name: Name of the strategy to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current strategy info
            strategies = self.get_cached_strategies()
            if strategy_name not in strategies:
                logger.error(f"Strategy {strategy_name} not found in cache")
                return False
                
            strategy_info = strategies[strategy_name]
            file_path = Path(strategy_info['file_path'])
            
            # Create backup before deletion
            backup_dir = file_path.parent / 'deleted_strategies'
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{strategy_name}_{timestamp}.py.deleted"
            
            # Move file to backup location
            shutil.move(str(file_path), str(backup_path))
            
            # Remove from database
            self.db_manager.delete_strategy(strategy_name)
            
            # Invalidate cache
            self.invalidate_cache()
            
            logger.info(f"Successfully deleted strategy: {strategy_name} (backed up to {backup_path})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting strategy {strategy_name}: {e}")
            return False
    
    def validate_strategy_syntax(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a strategy file has correct Python syntax.
        
        Args:
            file_path: Path to the strategy file
            
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