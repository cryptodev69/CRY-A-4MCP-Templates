import os
import sys
import json
import importlib
import inspect
from pathlib import Path
import argparse
import logging
from typing import Dict, Any, List, Optional

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from cry_a_4mcp.crawl4ai.extraction_strategies.ui.database.strategy_db import StrategyDatabase
from cry_a_4mcp.crawl4ai.extraction_strategies.registry import StrategyRegistry

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
        if inspect.isclass(obj) and hasattr(obj, 'SCHEMA') and hasattr(obj, 'INSTRUCTION'):
            strategy_classes.append(obj)
    
    if not strategy_classes:
        logger.warning(f"No strategy class found in {file_path}")
        return {}
    
    # Use the first strategy class found
    strategy_class = strategy_classes[0]
    
    # Extract data
    strategy_data = {
        'name': getattr(strategy_class, 'NAME', strategy_class.__name__),
        'description': getattr(strategy_class, 'DESCRIPTION', ''),
        'category': getattr(strategy_class, 'CATEGORY', 'general'),
        'default_provider': getattr(strategy_class, 'DEFAULT_PROVIDER', 'openai'),
        'schema': getattr(strategy_class, 'SCHEMA', {}),
        'instruction': getattr(strategy_class, 'INSTRUCTION', ''),
        'file_path': file_path
    }
    
    return strategy_data

def migrate_strategies(strategies_dir: str, db_path: Optional[str] = None) -> int:
    """
Migrate strategy files to the database.
    
    Args:
        strategies_dir: Directory containing strategy files
        db_path: Path to the database file (optional)
        
    Returns:
        Number of strategies migrated
    """
    # Initialize database
    db = StrategyDatabase(db_path)
    
    # Initialize strategy registry to get all strategy files
    registry = StrategyRegistry()
    registry.scan_directory(strategies_dir)
    
    # Get all strategy modules
    strategy_modules = registry.get_all_strategies()
    
    migrated_count = 0
    for strategy_name, strategy_info in strategy_modules.items():
        try:
            # Get the module path
            module_path = strategy_info.get('module_path')
            if not module_path:
                logger.warning(f"No module path for strategy {strategy_name}")
                continue
            
            # Import the module
            module_name = f"cry_a_4mcp.crawl4ai.extraction_strategies.{module_path.replace('/', '.')}"
            module_name = module_name.rstrip('.py')
            strategy_module = importlib.import_module(module_name)
            
            # Extract strategy data
            file_path = os.path.join(strategies_dir, module_path)
            strategy_data = extract_strategy_data(strategy_module, file_path)
            
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
        args.strategies_dir = str(Path(__file__).parent.parent.parent / 'strategies')
    
    # Migrate strategies
    migrated_count = migrate_strategies(args.strategies_dir, args.db_path)
    
    print(f"Migration complete. {migrated_count} strategies migrated.")

if __name__ == '__main__':
    main()