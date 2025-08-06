#!/usr/bin/env python3

import os
import sys
import tempfile
import py_compile
import traceback
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.templates.strategy_generator_class_attrs import StrategyTemplateGeneratorClassAttrs

def test_template_generation():
    """Test that the template generator can generate a strategy file without syntax errors."""
    print("Initializing template generator...")
    generator = StrategyTemplateGeneratorClassAttrs()
    
    # Print template file path
    print(f"Template file path: {generator.template_file}")
    print(f"Template file exists: {os.path.exists(generator.template_file)}")
    
    # Check template file content
    if os.path.exists(generator.template_file):
        with open(generator.template_file, 'r') as f:
            template_content = f.read()
            print(f"Template file size: {len(template_content)} bytes")
            print(f"Template contains 'type: ignore': {'type: ignore' in template_content}")
            print(f"Template contains 'pyright: ignore': {'pyright: ignore' in template_content}")
    
    # Create a temporary directory for the output
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory: {temp_dir}")
        
        # Set the output directory for the generator
        generator.output_dir = temp_dir
        
        # Generate a test strategy file
        strategy_name = "TestStrategy"
        strategy_description = "A test strategy for testing template generation"
        schema = {
            "type": "object",
            "properties": {
                "test_field": {
                    "type": "string",
                    "description": "A test field"
                }
            }
        }
        instruction = "Extract test information from the content."
        category = "general"
        
        print(f"Generating strategy file for {strategy_name}...")
        output_filename = generator.generate_strategy_file(
            strategy_name=strategy_name,
            strategy_description=strategy_description,
            schema=schema,
            instruction=instruction,
            category=category
        )
        
        if output_filename:
            # Construct the full path to the generated file
            output_path = os.path.join(temp_dir, output_filename)
            print(f"Strategy file generated: {output_path}")
            
            # Check if the file exists
            if os.path.exists(output_path):
                print(f"File exists: {output_path}")
                
                # Read the generated file content
                with open(output_path, 'r') as f:
                    generated_content = f.read()
                    print(f"Generated file size: {len(generated_content)} bytes")
                    print(f"Generated file contains 'type: ignore': {'type: ignore' in generated_content}")
                    print(f"Generated file contains 'pyright: ignore': {'pyright: ignore' in generated_content}")
                
                # Try to compile the file to check for syntax errors
                try:
                    py_compile.compile(output_path, doraise=True)
                    print("File compiled successfully - no syntax errors!")
                    
                    # Print the first 10 lines of the file
                    with open(output_path, 'r') as f:
                        lines = f.readlines()[:10]
                        print("First 10 lines of the generated file:")
                        for i, line in enumerate(lines):
                            print(f"{i+1}: {line.rstrip()}")
                    
                    return True
                except py_compile.PyCompileError as e:
                    print(f"Compilation error: {e}")
                    print("\nError details:")
                    traceback.print_exc()
                    return False
            else:
                print(f"File does not exist: {output_path}")
        else:
            print("Failed to create strategy file")
    
    return False

if __name__ == "__main__":
    # Create a class to write to both console and file
    class TeeOutput:
        def __init__(self, file_path):
            self.file = open(file_path, 'w')
            self.stdout = sys.stdout
            
        def write(self, data):
            self.file.write(data)
            self.stdout.write(data)
            self.file.flush()  # Ensure file is written immediately
            
        def flush(self):
            self.file.flush()
            self.stdout.flush()
            
        def close(self):
            self.file.close()
    
    # Create the tee output
    log_file = "debug_output.txt"
    tee = TeeOutput(log_file)
    
    # Save the original stdout
    original_stdout = sys.stdout
    
    # Redirect stdout to the tee output
    sys.stdout = tee
    
    try:
        print("Starting template generation test...")
        print("Python version:", sys.version)
        print("Current directory:", os.getcwd())
        
        result = test_template_generation()
        if result:
            print("\nTemplate generation test passed!")
            exit_code = 0
        else:
            print("\nTemplate generation test failed!")
            exit_code = 1
    except Exception as e:
        print(f"\nError during test: {e}")
        traceback.print_exc()
        exit_code = 1
    finally:
        # Restore the original stdout
        sys.stdout = original_stdout
        tee.close()
        
    print(f"Test completed. See {log_file} for details.")
    sys.exit(exit_code)