#!/usr/bin/env python3
"""
Test script for loading a file and checking for class attributes.

This script uses AST (Abstract Syntax Tree) to parse a Python file
and check if it contains classes with SCHEMA and INSTRUCTION class attributes.
"""

import os
import ast
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_class_attrs_loading')

def has_class_attributes(file_path):
    """Check if a Python file contains a class with SCHEMA and INSTRUCTION class attributes.
    
    Args:
        file_path: Path to the Python file to check
        
    Returns:
        tuple: (class_name, schema, instruction) if found, else (None, None, None)
    """
    try:
        # Read the file content
        with open(file_path, 'r') as f:
            file_content = f.read()
        
        # Parse the file content into an AST
        tree = ast.parse(file_content)
        
        # Look for classes with SCHEMA and INSTRUCTION class attributes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                logger.info(f"Found class: {class_name}")
                
                schema = None
                instruction = None
                
                # Check for class attributes
                for child in node.body:
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                if target.id == 'SCHEMA':
                                    logger.info(f"Found SCHEMA class attribute in {class_name}")
                                    schema = ast.unparse(child.value)
                                elif target.id == 'INSTRUCTION':
                                    logger.info(f"Found INSTRUCTION class attribute in {class_name}")
                                    instruction = ast.unparse(child.value)
                
                # If both attributes are found, return the class name and attributes
                if schema and instruction:
                    return class_name, schema, instruction
        
        # If no class with both attributes is found, return None
        logger.warning("No class with both SCHEMA and INSTRUCTION class attributes found")
        return None, None, None
    
    except Exception as e:
        logger.error(f"Error checking file {file_path}: {e}")
        return None, None, None

def main():
    """Main function to test the has_class_attributes function."""
    # Path to the test strategy
    strategy_path = "src/cry_a_4mcp/crawl4ai/extraction_strategies/custom/test_class_attrs_llm.py"
    
    # Make sure the file exists
    if not os.path.exists(strategy_path):
        logger.error(f"Strategy file not found: {strategy_path}")
        return
    
    # Check if the file has a class with SCHEMA and INSTRUCTION class attributes
    logger.info(f"Checking file {strategy_path} for class attributes")
    class_name, schema, instruction = has_class_attributes(strategy_path)
    
    if class_name:
        logger.info(f"Found class {class_name} with SCHEMA and INSTRUCTION class attributes")
        logger.info(f"SCHEMA: {schema}")
        logger.info(f"INSTRUCTION: {instruction}")
        logger.info("Test completed successfully")
    else:
        logger.error("No class with SCHEMA and INSTRUCTION class attributes found")

if __name__ == "__main__":
    main()