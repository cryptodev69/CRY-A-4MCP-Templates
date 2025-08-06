#!/usr/bin/env python3
"""
Test script to verify that the migration script correctly extracts schema and instruction from strategy files.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
import json

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

# Add src directory to Python path to allow imports
src_path = str(Path(__file__).parent / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Set PYTHONPATH environment variable to help with imports
os.environ['PYTHONPATH'] = src_path

# Import the extract_strategy_data function from migrate_strategies.py
from migrate_strategies import extract_strategy_data

# Import the CryptoLLMExtractionStrategy class
from cry_a_4mcp.crawl4ai.extraction_strategies.crypto.crypto_llm import CryptoLLMExtractionStrategy

def test_crypto_strategy_extraction():
    """Test that the schema and instruction are correctly extracted from the CryptoLLMExtractionStrategy class."""
    # Get the module
    module = inspect.getmodule(CryptoLLMExtractionStrategy)
    
    # Get the file path
    file_path = inspect.getfile(CryptoLLMExtractionStrategy)
    
    # Extract strategy data
    strategy_data = extract_strategy_data(module, file_path)
    
    # Print the extracted data
    print("Extracted strategy data:")
    print(f"Name: {strategy_data.get('name')}")
    print(f"Description: {strategy_data.get('description')}")
    print(f"Category: {strategy_data.get('category')}")
    print(f"Default Provider: {strategy_data.get('default_provider')}")
    
    # Print schema and instruction
    print("\nSchema:")
    schema = strategy_data.get('schema')
    if schema:
        print(json.dumps(schema, indent=2))
    else:
        print("No schema found!")
    
    print("\nInstruction:")
    instruction = strategy_data.get('instruction')
    if instruction:
        print(instruction)
    else:
        print("No instruction found!")

if __name__ == '__main__':
    test_crypto_strategy_extraction()