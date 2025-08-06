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

def test_template_generation_debug():
    """Test that the template generator can generate a strategy file without syntax errors.
    This version includes detailed debugging information.
    """
    print("\n" + "=" * 80)
    print("STARTING TEMPLATE GENERATION DEBUG TEST")
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
    
    # Print template file path and check if it exists
    print("\nTemplate File Information:")
    print(f"Template file path: {generator.template_file}")
    template_exists = os.path.exists(generator.template_file)
    print(f"Template file exists: {template_exists}")
    
    if not template_exists:
        print(f"❌ Error: Template file does not exist")
        return False
    
    # Check template file content
    try:
        with open(generator.template_file, 'r') as f:
            template_content = f.read()
            print(f"Template file size: {len(template_content)} bytes")
            print(f"Template contains 'type: ignore': {'type: ignore' in template_content}")
            print(f"Template contains 'pyright: ignore': {'pyright: ignore' in template_content}")
            print(f"Template contains template variables: {'{{' in template_content and '}}' in template_content}")
            
            # Print first few lines of template
            print("\nFirst 5 lines of template:")
            lines = template_content.split('\n')[:5]
            for i, line in enumerate(lines):
                print(f"{i+1}: {line}")
    except Exception as e:
        print(f"❌ Error reading template file: {e}")
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
        
        print(f"Strategy name: {strategy_name}")
        print(f"Strategy description: {strategy_description}")
        print(f"Schema: {json.dumps(schema, indent=2)}")
        print(f"Instruction: {instruction}")
        print(f"Category: {category}")
        
        # First generate the content without writing to a file
        print("\nGenerating strategy content (without writing to file)...")
        content = generator.generate_strategy_content(
            strategy_name=strategy_name,
            strategy_description=strategy_description,
            schema=schema,
            instruction=instruction,
            category=category
        )
        
        print(f"✅ Generated content length: {len(content)} bytes")
        print("First 10 lines of generated content:")
        content_lines = content.split('\n')[:10]
        for i, line in enumerate(content_lines):
            print(f"{i+1}: {line}")
        
        # Now generate the actual file
        print("\nGenerating strategy file...")
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
        # The output_filename already includes the category directory
        output_path = os.path.join(temp_dir, output_filename)
        print(f"Full path: {output_path}")
        
        # Check if the file exists
        file_exists = os.path.exists(output_path)
        print(f"File exists: {file_exists}")
        
        if not file_exists:
            print(f"❌ Error: Generated file does not exist")
            return False
        
        # Read the generated file content
        with open(output_path, 'r') as f:
            generated_content = f.read()
            print(f"Generated file size: {len(generated_content)} bytes")
            print(f"Generated file contains 'type: ignore': {'type: ignore' in generated_content}")
            print(f"Generated file contains 'pyright: ignore': {'pyright: ignore' in generated_content}")
            
            # Print first few lines of generated file
            print("\nFirst 10 lines of generated file:")
            gen_lines = generated_content.split('\n')[:10]
            for i, line in enumerate(gen_lines):
                print(f"{i+1}: {line}")
        
        # Try to compile the file to check for syntax errors
        print("\nCompiling generated file to check for syntax errors...")
        try:
            py_compile.compile(output_path, doraise=True)
            print("✅ File compiled successfully - no syntax errors!")
            return True
        except py_compile.PyCompileError as e:
            print(f"❌ Compilation error: {e}")
            print("\nError details:")
            traceback.print_exc()
            
            # Print the problematic line and surrounding context
            if hasattr(e, 'lineno') and e.lineno is not None:
                with open(output_path, 'r') as f:
                    all_lines = f.readlines()
                    start_line = max(0, e.lineno - 5)
                    end_line = min(len(all_lines), e.lineno + 5)
                    print(f"\nContext around error (lines {start_line+1}-{end_line}):")
                    for i in range(start_line, end_line):
                        prefix = ">>> " if i == e.lineno - 1 else "    "
                        print(f"{prefix}{i+1}: {all_lines[i].rstrip()}")
            return False
    except Exception as e:
        print(f"❌ Error checking generated file: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        result = test_template_generation_debug()
        if result:
            print("\n" + "=" * 80)
            print("✅ TEMPLATE GENERATION TEST PASSED!")
            print("=" * 80)
            sys.exit(0)
        else:
            print("\n" + "=" * 80)
            print("❌ TEMPLATE GENERATION TEST FAILED!")
            print("=" * 80)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unhandled error during test: {e}")
        traceback.print_exc()
        sys.exit(1)