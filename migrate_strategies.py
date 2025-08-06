#!/usr/bin/env python3
"""
Migration script for strategy files to database.

This script migrates strategy files to the database, extracting relevant data
from strategy modules and storing it in the database for use by the UI.

Usage:
    python migrate_strategies.py [--strategies-dir STRATEGIES_DIR] [--db-path DB_PATH]

Options:
    --strategies-dir STRATEGIES_DIR  Directory containing strategy files
    --db-path DB_PATH               Path to the database file

If no strategies directory is provided, the script will use the default
extraction_strategies directory in the src folder.

If no database path is provided, the script will use the default database
path in the UI config directory.
"""

import os
import sys
import json
import importlib
import inspect
import re
from pathlib import Path
import argparse
import logging
from typing import Dict, Any, List, Optional

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

# Add src directory to Python path to allow imports
src_path = str(Path(__file__).parent / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Set PYTHONPATH environment variable to help with imports
os.environ['PYTHONPATH'] = src_path

try:
    # Try importing with package name first
    from cry_a_4mcp.crawl4ai.extraction_strategies.ui.database.strategy_db import StrategyDatabase
    from cry_a_4mcp.crawl4ai.extraction_strategies.registry import StrategyRegistry
except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    logger.info("Make sure the cry_a_4mcp package is installed or in your PYTHONPATH")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_strategy_data(strategy_module, file_path: str) -> Dict[str, Any]:
    """Extract strategy data from a strategy module.
    
    Args:
        strategy_module: The imported strategy module
        file_path: Path to the strategy file
        
    Returns:
        Dictionary containing strategy data
    """
    # Get the strategy class from the module
    strategy_classes = []
    for name, obj in inspect.getmembers(strategy_module):
        # Check if it's a class and a subclass of ExtractionStrategy, but not the base class itself
        if (inspect.isclass(obj) and 
            hasattr(obj, '__module__') and 
            obj.__module__ == strategy_module.__name__ and
            'ExtractionStrategy' in obj.__name__ and
            obj.__name__ != 'ExtractionStrategy'):
            strategy_classes.append(obj)
    
    if not strategy_classes:
        logger.warning(f"No strategy class found in {file_path}")
        return {}
    
    # Use the first strategy class found
    strategy_class = strategy_classes[0]
    logger.info(f"Found strategy class: {strategy_class.__name__} in {file_path}")
    
    # Initialize schema and instruction
    schema = None
    instruction = None
    
    # Try to create an instance with minimal parameters
    try:
        # For LLMExtractionStrategy subclasses, we need to pass provider and api_token
        if 'LLMExtractionStrategy' in str(strategy_class.__bases__):
            logger.info(f"Creating instance of LLM-based strategy: {strategy_class.__name__}")
            strategy_instance = strategy_class(provider="openai", api_token="dummy_token")
        else:
            # Try with default parameters
            logger.info(f"Creating instance of non-LLM strategy: {strategy_class.__name__}")
            strategy_instance = strategy_class()
        
        # Get schema and instruction from instance
        schema = getattr(strategy_instance, 'schema', None)
        instruction = getattr(strategy_instance, 'instruction', None)
        
        logger.info(f"Successfully created instance of {strategy_class.__name__}")
        logger.info(f"Schema found: {schema is not None}")
        logger.info(f"Instruction found: {instruction is not None}")
    except Exception as e:
        logger.warning(f"Could not create instance of {strategy_class.__name__}: {e}")
        
        # If we couldn't create an instance, try to get schema and instruction from class attributes
        schema = getattr(strategy_class, 'SCHEMA', getattr(strategy_class, 'schema', None))
        instruction = getattr(strategy_class, 'INSTRUCTION', getattr(strategy_class, 'instruction', None))
        
        # If still not found, try to inspect the source code
        if schema is None or instruction is None:
            try:
                # Get the source code of the module
                module_source = inspect.getsource(strategy_module)
                
                # Look for schema variable definitions in the module
                if schema is None:
                    schema_vars = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*_schema)\s*=\s*\{', module_source)
                    for var_name in schema_vars:
                        # Check if this variable is used in the __init__ method
                        if f"schema={var_name}" in module_source.replace(" ", ""):
                            # Try to get the variable from the module
                            if hasattr(strategy_module, var_name):
                                schema = getattr(strategy_module, var_name)
                                logger.info(f"Found schema variable: {var_name}")
                                break
                
                # Look for instruction variable definitions in the module
                if instruction is None:
                    instruction_vars = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*_instruction)\s*=\s*["\\\']{3}', module_source)
                    # Fix: Added a corrected version of the regex pattern
                    # instruction_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*_instruction)\s*=\s*["\\\']{3}.*?["\\\']{3}', module_source, re.DOTALL)
                    for var_name in instruction_vars:
                        # Check if this variable is used in the __init__ method
                        if f"instruction={var_name}" in module_source.replace(" ", ""):
                            # Try to get the variable from the module
                            if hasattr(strategy_module, var_name):
                                instruction = getattr(strategy_module, var_name)
                                logger.info(f"Found instruction variable: {var_name}")
                                break
            except Exception as inspect_error:
                logger.warning(f"Could not inspect module source: {inspect_error}")
    
    # Extract data
    strategy_data = {
        'name': getattr(strategy_class, 'NAME', strategy_class.__name__),
        'description': getattr(strategy_class, '__doc__', '') or '',
        'category': getattr(strategy_class, 'CATEGORY', 
                           file_path.split('extraction_strategies/')[-1].split('/')[0] if 'extraction_strategies/' in file_path else 'general'),
        'default_provider': getattr(strategy_class, 'DEFAULT_PROVIDER', 'openai'),
        'schema': schema or {},
        'instruction': instruction or '',
        'file_path': file_path
    }
    
    return strategy_data

def migrate_strategies(strategies_dir: str, db_path: Optional[str] = None) -> int:
    """
Migrate strategy files to the database.
    
    This function loads all strategy classes from the registry, extracts relevant data
    from each strategy class, and stores it in the database. If a strategy already exists
    in the database, it will be updated with the latest data.
    
    The function uses the StrategyRegistry class to load and access strategy classes,
    and the StrategyDatabase class to store the extracted data.
    
    Args:
        strategies_dir: Directory containing strategy files
        db_path: Path to the database file (optional)
        
    Returns:
        Number of strategies migrated
    """
    # Initialize database
    db = StrategyDatabase(db_path)
    
    # Initialize strategy registry
    registry = StrategyRegistry()
    
    # Load strategies from the directory
    # Use the available methods to load strategies
    logger.info(f"Loading strategies from registry...")
    registry.load_custom_strategies()
    registry.load_category_strategies()
    
    # Get all strategy modules
    strategy_modules = registry.get_all()  # This returns a dictionary of strategy names to strategy classes
    
    migrated_count = 0
    for strategy_name, strategy_class in strategy_modules.items():
        try:
            # Get the module path
            module_path = registry.get_strategy_file_path(strategy_name)
            if not module_path:
                logger.warning(f"No module path for strategy {strategy_name}")
                continue
            
            # Get the module
            module = inspect.getmodule(strategy_class)
            if not module:
                logger.warning(f"Could not get module for strategy {strategy_name}")
                continue
            
            # Extract strategy data
            strategy_data = extract_strategy_data(module, module_path)
            
            if not strategy_data:
                continue
            
            # Check if strategy already exists in database
            existing_strategy = db.get_strategy(strategy_data['name'])
            
            if existing_strategy:
                # Update existing strategy
                db.update_strategy(strategy_data['name'], strategy_data)
                logger.info(f"Updated strategy {strategy_data['name']} in database")
            else:
                # Add new strategy
                db.add_strategy(strategy_data)
                logger.info(f"Added strategy {strategy_data['name']} to database")
            
            migrated_count += 1
            
        except Exception as e:
            logger.error(f"Error migrating strategy {strategy_name}: {e}")
    
    logger.info(f"Migration complete. {migrated_count} strategies migrated.")
    return migrated_count

def main():
    """Main function for the migration script."""
    parser = argparse.ArgumentParser(description='Migrate strategy files to database')
    parser.add_argument('--strategies-dir', type=str, help='Directory containing strategy files')
    parser.add_argument('--db-path', type=str, help='Path to the database file')
    
    args = parser.parse_args()
    
    # Use default strategies directory if not provided
    if not args.strategies_dir:
        # Use the extraction_strategies directory in the src folder
        args.strategies_dir = str(Path(__file__).parent / 'src' / 'cry_a_4mcp' / 'crawl4ai' / 'extraction_strategies')
        logger.info(f"Using default strategies directory: {args.strategies_dir}")
    
    # Make sure the strategies directory exists
    if not os.path.exists(args.strategies_dir):
        logger.error(f"Strategies directory does not exist: {args.strategies_dir}")
        sys.exit(1)
    
    # Migrate strategies
    migrated_count = migrate_strategies(args.strategies_dir, args.db_path)
    
    print(f"Migration complete. {migrated_count} strategies migrated.")

if __name__ == '__main__':
    main()