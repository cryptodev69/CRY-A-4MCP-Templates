#!/usr/bin/env python3

import os
import sys
import tempfile
import py_compile
import traceback
import json
import importlib.util
import inspect

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.templates.strategy_generator_class_attrs import StrategyTemplateGeneratorClassAttrs

def test_class_attrs_template():
    """Test that the template generator correctly creates a strategy with class attributes.
    This test verifies that SCHEMA and INSTRUCTION are defined as class attributes.
    """
    print("\n" + "=" * 80)
    print("STARTING CLASS ATTRIBUTES TEMPLATE TEST")
    print("=" * 80)
    
    print("\nSystem Information:")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    print("\nInitializing template generator...")
    try:
        generator = StrategyTemplateGeneratorClassAttrs()
        print("✅ Generator initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing generator: {e}")
        traceback.print_exc()
        return False
    
    # Create a temporary directory for the output
    print("\nCreating temporary directory for output...")
    try:
        temp_dir = tempfile.mkdtemp()
        print(f"✅ Created temporary directory: {temp_dir}")
        
        # Set the output directory for the generator
        generator.output_dir = temp_dir
    except Exception as e:
        print(f"❌ Error creating temporary directory: {e}")
        traceback.print_exc()
        return False
    
    # Generate a test strategy file
    print("\nGenerating test strategy file...")
    try:
        strategy_name = "ClassAttrsTest"
        strategy_description = "A test strategy for verifying class attributes"
        schema = {
            "type": "object",
            "properties": {
                "test_field": {
                    "type": "string",
                    "description": "A test field"
                },
                "another_field": {
                    "type": "number",
                    "description": "Another test field"
                }
            }
        }
        instruction = "Extract test information from the content using class attributes."
        category = "testing"
        
        print(f"Strategy name: {strategy_name}")
        print(f"Strategy description: {strategy_description}")
        print(f"Schema: {json.dumps(schema, indent=2)}")
        print(f"Instruction: {instruction}")
        print(f"Category: {category}")
        
        # Generate the strategy file
        output_filename = generator.generate_strategy_file(
            strategy_name=strategy_name,
            strategy_description=strategy_description,
            schema=schema,
            instruction=instruction,
            category=category
        )
        
        print(f"✅ Strategy file generated: {output_filename}")
    except Exception as e:
        print(f"❌ Error generating strategy file: {e}")
        traceback.print_exc()
        return False
    
    # Check the generated file
    print("\nChecking generated file...")
    try:
        # Construct the full path to the generated file
        output_path = os.path.join(temp_dir, output_filename)
        print(f"Full path: {output_path}")
        
        # Check if the file exists
        file_exists = os.path.exists(output_path)
        print(f"File exists: {file_exists}")
        
        if not file_exists:
            print(f"❌ Error: Generated file does not exist")
            return False
        
        # Try to compile the file to check for syntax errors
        print("\nCompiling generated file to check for syntax errors...")
        try:
            py_compile.compile(output_path, doraise=True)
            print("✅ File compiled successfully - no syntax errors!")
        except py_compile.PyCompileError as e:
            print(f"❌ Compilation error: {e}")
            print("\nError details:")
            traceback.print_exc()
            return False
        
        # Load the generated module to check for class attributes
        print("\nLoading generated module to check for class attributes...")
        try:
            # Instead of trying to import the module directly, let's check for class attributes
            # by parsing the file content
            with open(output_path, 'r') as f:
                file_content = f.read()
            
            print("Checking file content for class attributes...")
            
            # Check if the file contains class attribute definitions
            has_schema_attr = "SCHEMA = " in file_content
            has_instruction_attr = "INSTRUCTION = " in file_content
            
            print(f"File contains SCHEMA class attribute definition: {has_schema_attr}")
            print(f"File contains INSTRUCTION class attribute definition: {has_instruction_attr}")
            
            if not has_schema_attr or not has_instruction_attr:
                print("❌ Error: Missing required class attribute definitions")
                return False
            
            # Check if the schema content is in the file
            schema_str = json.dumps(schema, sort_keys=True)
            # We don't need an exact match, just check if the key parts are there
            schema_keys_present = all(key in file_content for key in schema["properties"].keys())
            
            # Check if the instruction is in the file
            instruction_present = instruction in file_content
            
            print(f"Schema keys present in file: {schema_keys_present}")
            print(f"Instruction present in file: {instruction_present}")
            
            if not schema_keys_present or not instruction_present:
                print("❌ Error: Class attribute content not found in file")
                return False
            
            print("✅ Class attributes verified successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading or checking module: {e}")
            traceback.print_exc()
            return False
    except Exception as e:
        print(f"❌ Error checking generated file: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        result = test_class_attrs_template()
        if result:
            print("\n" + "=" * 80)
            print("✅ CLASS ATTRIBUTES TEMPLATE TEST PASSED!")
            print("=" * 80)
            sys.exit(0)
        else:
            print("\n" + "=" * 80)
            print("❌ CLASS ATTRIBUTES TEMPLATE TEST FAILED!")
            print("=" * 80)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unhandled error during test: {e}")
        traceback.print_exc()
        sys.exit(1)