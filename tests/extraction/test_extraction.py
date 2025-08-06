#!/usr/bin/env python3

"""
Test script to verify extraction of schema and instruction from strategy files.
"""

import sys
import os
import importlib.util
from pathlib import Path
import inspect
import json

# Add src directory to Python path to allow imports
src_path = str(Path(__file__).parent / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Set PYTHONPATH environment variable to help with imports
os.environ['PYTHONPATH'] = src_path

# First import the base module to make relative imports work
base_path = Path(__file__).parent / 'src' / 'cry_a_4mcp' / 'crawl4ai' / 'extraction_strategies' / 'base.py'
base_spec = importlib.util.spec_from_file_location("base", base_path)
base_module = importlib.util.module_from_spec(base_spec)
sys.modules["cry_a_4mcp.crawl4ai.extraction_strategies.base"] = base_module
base_spec.loader.exec_module(base_module)

# Set up the package structure for relative imports
sys.modules["cry_a_4mcp"] = type('module', (), {})()
sys.modules["cry_a_4mcp.crawl4ai"] = type('module', (), {})()
sys.modules["cry_a_4mcp.crawl4ai.extraction_strategies"] = type('module', (), {})()
sys.modules["cry_a_4mcp.crawl4ai.extraction_strategies.crypto"] = type('module', (), {})()

# Import the crypto strategy module
module_path = Path(__file__).parent / 'src' / 'cry_a_4mcp' / 'crawl4ai' / 'extraction_strategies' / 'crypto' / 'crypto_llm.py'
spec = importlib.util.spec_from_file_location("cry_a_4mcp.crawl4ai.extraction_strategies.crypto.crypto_llm", module_path)
module = importlib.util.module_from_spec(spec)
sys.modules["cry_a_4mcp.crawl4ai.extraction_strategies.crypto.crypto_llm"] = module
spec.loader.exec_module(module)

# Find the CryptoLLMExtractionStrategy class
strategy_class = None
for name, obj in inspect.getmembers(module):
    if (inspect.isclass(obj) and 
        hasattr(obj, '__module__') and 
        obj.__module__ == module.__name__ and
        'ExtractionStrategy' in obj.__name__):
        strategy_class = obj
        break

if not strategy_class:
    print("No strategy class found!")
    sys.exit(1)

print(f"Found strategy class: {strategy_class.__name__}")

# Create an instance of the strategy class
try:
    # For CryptoLLMExtractionStrategy, we need to pass provider and api_token
    strategy_instance = strategy_class(provider="openai", api_token="dummy_token")
    
    # Get schema and instruction from instance
    schema = getattr(strategy_instance, 'schema', None)
    instruction = getattr(strategy_instance, 'instruction', None)
    
    print("\nSchema:")
    if schema:
        print(json.dumps(schema, indent=2))
    else:
        print("No schema found!")
    
    print("\nInstruction:")
    if instruction:
        print(instruction)
    else:
        print("No instruction found!")
    
except Exception as e:
    print(f"Error creating instance: {e}")
    
    # Try to get schema and instruction from class attributes
    schema = getattr(strategy_class, 'SCHEMA', getattr(strategy_class, 'schema', None))
    instruction = getattr(strategy_class, 'INSTRUCTION', getattr(strategy_class, 'instruction', None))
    
    print("\nSchema from class attributes:")
    if schema:
        print(json.dumps(schema, indent=2))
    else:
        print("No schema found in class attributes!")
    
    print("\nInstruction from class attributes:")
    if instruction:
        print(instruction)
    else:
        print("No instruction found in class attributes!")