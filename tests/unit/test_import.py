#!/usr/bin/env python3

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("Script starting...")
print("Python version:", sys.version)
print("Current directory:", os.getcwd())

try:
    print("Attempting to import StrategyTemplateGeneratorClassAttrs...")
    from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.templates.strategy_generator_class_attrs import StrategyTemplateGeneratorClassAttrs
    print("Import successful!")
    
    # Try to initialize the class
    print("Initializing StrategyTemplateGeneratorClassAttrs...")
    generator = StrategyTemplateGeneratorClassAttrs()
    print("Initialization successful!")
    
    # Check template file
    print(f"Template file path: {generator.template_file}")
    print(f"Template file exists: {os.path.exists(generator.template_file)}")
    
    if os.path.exists(generator.template_file):
        with open(generator.template_file, 'r') as f:
            first_line = f.readline().strip()
            print(f"First line of template: {first_line}")
    
    print("Test completed successfully!")
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)