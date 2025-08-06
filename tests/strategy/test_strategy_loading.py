#!/usr/bin/env python3
"""
Test script for loading strategies with class attributes.

This script tests loading a strategy with SCHEMA and INSTRUCTION defined as class attributes.
"""

import os
import sys
import inspect
import importlib.util
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_strategy_loading')

def load_module_from_path(file_path):
    """Load a module directly from a file path."""
    try:
        # Get the absolute path
        abs_path = os.path.abspath(file_path)
        logger.info(f"Loading module from absolute path: {abs_path}")
        
        # Get the module name from the file name
        module_name = os.path.basename(file_path)
        if module_name.endswith('.py'):
            module_name = module_name[:-3]
        
        # Create a mock LLMExtractionStrategy class to avoid import errors
        class MockLLMExtractionStrategy:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        # Add the mock class to sys.modules
        sys.modules['cry_a_4mcp.crawl4ai.extraction_strategies.base'] = type('module', (), {'LLMExtractionStrategy': MockLLMExtractionStrategy})
        
        # Load the module spec
        spec = importlib.util.spec_from_file_location(module_name, abs_path)
        if spec is None or spec.loader is None:
            logger.error(f"Could not load module spec from {abs_path}")
            return None
        
        # Create the module
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        
        # Execute the module
        spec.loader.exec_module(module)
        
        return module
    except Exception as e:
        logger.error(f"Error loading module: {e}")
        return None

def main():
    # Path to the test strategy
    strategy_path = "src/cry_a_4mcp/crawl4ai/extraction_strategies/custom/test_class_attrs_llm.py"
    
    # Make sure the file exists
    if not os.path.exists(strategy_path):
        logger.error(f"Strategy file not found: {strategy_path}")
        return
    
    # Load the strategy module
    logger.info(f"Loading strategy module from {strategy_path}")
    strategy_module = load_module_from_path(strategy_path)
    
    if not strategy_module:
        logger.error("Failed to load strategy module")
        return
    
    logger.info("Strategy module loaded successfully")
    
    # Find the strategy class in the module
    strategy_class = None
    for name, obj in inspect.getmembers(strategy_module):
        if inspect.isclass(obj):
            logger.info(f"Found class: {name}")
            if hasattr(obj, 'SCHEMA') and hasattr(obj, 'INSTRUCTION'):
                strategy_class = obj
                logger.info(f"Found strategy class: {name}")
                break
    
    if not strategy_class:
        logger.error("Strategy class not found in the module")
        return
    
    logger.info("Strategy class found successfully")
    
    # Print the schema and instruction
    logger.info(f"SCHEMA: {strategy_class.SCHEMA}")
    logger.info(f"INSTRUCTION: {strategy_class.INSTRUCTION}")
    
    logger.info("Test completed successfully")

if __name__ == "__main__":
    main()