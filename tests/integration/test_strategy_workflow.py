#!/usr/bin/env python3

import os
import sys
import tempfile
import shutil
import traceback
import json
import importlib.util
import inspect

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.templates.strategy_generator_class_attrs import StrategyTemplateGeneratorClassAttrs

def create_package_structure(temp_dir, strategy_file_path):
    """Create a temporary package structure to allow importing the strategy.
    
    Args:
        temp_dir: The temporary directory to create the package in
        strategy_file_path: The path to the generated strategy file
        
    Returns:
        The path to the package directory and the import path for the strategy
    """
    # Create a package structure
    package_dir = os.path.join(temp_dir, "test_package")
    os.makedirs(package_dir, exist_ok=True)
    
    # Create an __init__.py file in the package directory
    with open(os.path.join(package_dir, "__init__.py"), "w") as f:
        f.write("# Test package\n")
    
    # Create a base.py file with the LLMExtractionStrategy class
    with open(os.path.join(package_dir, "base.py"), "w") as f:
        f.write("""
# Mock base class for testing
class LLMExtractionStrategy:
    def __init__(self, provider=None, api_token=None, instruction=None, schema=None, 
                 base_url=None, model=None, extra_args=None, max_retries=3, timeout=60, **kwargs):
        self.provider = provider
        self.api_token = api_token
        self.instruction = instruction
        self.schema = schema
        self.base_url = base_url
        self.model = model
        self.extra_args = extra_args or {}
        self.max_retries = max_retries
        self.timeout = timeout
        self.kwargs = kwargs
        
    def extract(self, content):
        # Mock extraction method
        return {"mock_result": True}
""")
    
    # Copy the strategy file to the package directory
    strategy_filename = os.path.basename(strategy_file_path)
    strategy_dest_path = os.path.join(package_dir, strategy_filename)
    shutil.copy(strategy_file_path, strategy_dest_path)
    
    # Modify the import statement in the strategy file
    with open(strategy_dest_path, "r") as f:
        content = f.read()
    
    # Replace the relative import with an absolute import
    content = content.replace("from ..base import LLMExtractionStrategy", 
                             "from test_package.base import LLMExtractionStrategy")
    
    # Print the class name for debugging
    import re
    class_match = re.search(r'class\s+(\w+LLMExtractionStrategy)', content)
    if class_match:
        class_name = class_match.group(1)
        print(f"Found strategy class name in file: {class_name}")
    else:
        print("Warning: Could not find strategy class name in file")
    
    with open(strategy_dest_path, "w") as f:
        f.write(content)
    
    # Return the package directory and the import path
    module_name = os.path.splitext(strategy_filename)[0]
    import_path = f"test_package.{module_name}"
    
    return package_dir, import_path

def test_strategy_workflow():
    """Test the entire workflow from template generation to strategy instantiation."""
    print("\n" + "=" * 80)
    print("STARTING STRATEGY WORKFLOW TEST")
    print("=" * 80)
    
    print("\nSystem Information:")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"\nCreated temporary directory: {temp_dir}")
    
    try:
        # Initialize the template generator
        print("\nInitializing template generator...")
        generator = StrategyTemplateGeneratorClassAttrs()
        generator.output_dir = temp_dir
        print("✅ Generator initialized successfully")
        
        # Generate a test strategy file
        print("\nGenerating test strategy file...")
        strategy_name = "WorkflowTest"
        strategy_description = "A test strategy for verifying the entire workflow"
        schema = {
            "type": "object",
            "properties": {
                "workflow_field": {
                    "type": "string",
                    "description": "A workflow test field"
                }
            }
        }
        instruction = "Extract workflow test information from the content."
        category = "workflow"
        
        output_filename = generator.generate_strategy_file(
            strategy_name=strategy_name,
            strategy_description=strategy_description,
            schema=schema,
            instruction=instruction,
            category=category
        )
        
        print(f"✅ Strategy file generated: {output_filename}")
        
        # Get the full path to the generated file
        strategy_file_path = os.path.join(temp_dir, output_filename)
        print(f"Strategy file path: {strategy_file_path}")
        
        # Create a package structure to allow importing the strategy
        print("\nCreating package structure for importing...")
        package_dir, import_path = create_package_structure(temp_dir, strategy_file_path)
        print(f"Package directory: {package_dir}")
        print(f"Import path: {import_path}")
        
        # Add the temp directory to the Python path
        sys.path.insert(0, temp_dir)
        
        # Import the strategy module
        print("\nImporting strategy module...")
        try:
            strategy_module = __import__(import_path, fromlist=["*"])
            print("✅ Strategy module imported successfully")
            
            # Find the strategy class in the module
            strategy_class = None
            for name, obj in inspect.getmembers(strategy_module):
                if inspect.isclass(obj) and name.endswith("LLMExtractionStrategy") and name != "LLMExtractionStrategy":
                    strategy_class = obj
                    break
            
            if strategy_class is None:
                print("❌ Error: Could not find strategy class in module")
                print("Available classes:")
                for name, obj in inspect.getmembers(strategy_module):
                    if inspect.isclass(obj):
                        print(f"  - {name}")
                return False
            
            print(f"✅ Found strategy class: {strategy_class.__name__}")
            
            # Verify class attributes
            print("\nVerifying class attributes...")
            has_schema_attr = hasattr(strategy_class, "SCHEMA")
            has_instruction_attr = hasattr(strategy_class, "INSTRUCTION")
            
            print(f"Has SCHEMA class attribute: {has_schema_attr}")
            print(f"Has INSTRUCTION class attribute: {has_instruction_attr}")
            
            if not has_schema_attr or not has_instruction_attr:
                print("❌ Error: Missing required class attributes")
                return False
            
            # Instantiate the strategy
            print("\nInstantiating strategy...")
            strategy_instance = strategy_class(provider="test_provider", api_token="test_token")
            print("✅ Strategy instantiated successfully")
            
            # Verify the strategy instance
            print("\nVerifying strategy instance...")
            print(f"Provider: {strategy_instance.provider}")
            print(f"API Token: {strategy_instance.api_token}")
            print(f"Instruction: {strategy_instance.instruction}")
            print(f"Schema: {json.dumps(strategy_instance.schema, indent=2)}")
            
            # Test the extract method
            print("\nTesting extract method...")
            result = strategy_instance.extract("Test content")
            print(f"Extract result: {result}")
            
            print("\n✅ Strategy workflow test completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Error during strategy import or instantiation: {e}")
            traceback.print_exc()
            return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        traceback.print_exc()
        return False
    finally:
        # Clean up the temporary directory
        print(f"\nCleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    try:
        result = test_strategy_workflow()
        if result:
            print("\n" + "=" * 80)
            print("✅ STRATEGY WORKFLOW TEST PASSED!")
            print("=" * 80)
            sys.exit(0)
        else:
            print("\n" + "=" * 80)
            print("❌ STRATEGY WORKFLOW TEST FAILED!")
            print("=" * 80)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unhandled error during test: {e}")
        traceback.print_exc()
        sys.exit(1)