#!/usr/bin/env python3

import os
import sys
import tempfile
import shutil
import re
import importlib.util
import inspect
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the current directory to the path so we can import the modules
sys.path.append(os.getcwd())

# Import the strategy generator
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.templates.strategy_generator_class_attrs import StrategyTemplateGeneratorClassAttrs

# Define test categories and their schemas
TEST_CATEGORIES = [
    "academic",
    "composite",
    "crypto",
    "financial",
    "general",
    "news",
    "nft",
    "product",
    "social",  # Changed from social_media to match directory structure
    "workflow"
]

def create_test_package(temp_dir, strategy_file_path, category):
    """Create a test package structure for importing the strategy."""
    # Create package directory
    package_dir = os.path.join(temp_dir, "test_package")
    os.makedirs(package_dir, exist_ok=True)
    
    # Create __init__.py files
    with open(os.path.join(package_dir, "__init__.py"), "w") as f:
        f.write("")
    
    # Create base.py with the base strategy class
    with open(os.path.join(package_dir, "base.py"), "w") as f:
        f.write("""
# Base strategy class for testing
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
    
    def extract(self, content):
        # Mock implementation for testing
        return {"mock_result": True}
""")
    
    # Copy the strategy file to the package
    strategy_filename = os.path.basename(strategy_file_path)
    strategy_dest_path = os.path.join(package_dir, strategy_filename)
    shutil.copy(strategy_file_path, strategy_dest_path)
    
    # Modify the import statement in the strategy file
    with open(strategy_dest_path, "r") as f:
        content = f.read()
    
    # Replace the relative import with an absolute import
    content = content.replace("from ..base import LLMExtractionStrategy", 
                             "from test_package.base import LLMExtractionStrategy")
    
    # Extract the class name for debugging
    class_match = re.search(r'class\s+(\w+LLMExtractionStrategy)', content)
    class_name = class_match.group(1) if class_match else None
    
    with open(strategy_dest_path, "w") as f:
        f.write(content)
    
    return package_dir, strategy_filename, class_name

def import_strategy_module(package_dir, strategy_filename):
    """Import the strategy module."""
    # Get the module name without extension
    module_name = os.path.splitext(strategy_filename)[0]
    
    # Import path
    import_path = f"test_package.{module_name}"
    
    # Import the module
    spec = importlib.util.spec_from_file_location(
        import_path, 
        os.path.join(package_dir, strategy_filename)
    )
    strategy_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(strategy_module)
    
    return strategy_module, import_path

def test_category(generator, temp_dir, category):
    """Test a specific category."""
    print(f"\nTesting category: {category}")
    print("-" * 50)
    
    # Remove the temp directory from sys.path if it was added in a previous test
    if temp_dir in sys.path:
        sys.path.remove(temp_dir)
    
    # Generate a test strategy file
    strategy_name = f"{category}test"
    strategy_description = f"A test strategy for {category} category"
    schema = {
        "type": "object",
        "properties": {
            f"{category}_field": {
                "type": "string",
                "description": f"A {category} test field"
            }
        }
    }
    instruction = f"Extract {category} test information from the content."
    default_provider = "test_provider"
    
    # Generate the strategy file
    strategy_file_path = generator.generate_strategy_file(
        strategy_name=strategy_name,
        strategy_description=strategy_description,
        schema=schema,
        instruction=instruction,
        default_provider=default_provider,
        category=category
    )
    
    print(f"✅ Strategy file generated: {strategy_file_path}")
    
    # Create package structure for importing
    package_dir, strategy_filename, class_name = create_test_package(temp_dir, os.path.join(temp_dir, strategy_file_path), category)
    print(f"Found strategy class name: {class_name}")
    
    # Add the temp directory to the Python path
    if temp_dir not in sys.path:
        sys.path.insert(0, temp_dir)
    
    # Import the strategy module
    try:
        strategy_module, import_path = import_strategy_module(package_dir, strategy_filename)
        print(f"✅ Strategy module imported: {import_path}")
    except Exception as e:
        print(f"❌ Error importing strategy module: {e}")
        return False
    
    # Find the strategy class in the module
    strategy_class = None
    for name, obj in inspect.getmembers(strategy_module):
        if inspect.isclass(obj) and name == class_name:
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
    has_schema = hasattr(strategy_class, "SCHEMA")
    has_instruction = hasattr(strategy_class, "INSTRUCTION")
    
    print(f"Has SCHEMA class attribute: {has_schema}")
    print(f"Has INSTRUCTION class attribute: {has_instruction}")
    
    if not has_schema or not has_instruction:
        print("❌ Error: Missing required class attributes")
        return False
    
    # Verify attribute values
    schema_attr = strategy_class.SCHEMA if has_schema else None
    instruction_value = strategy_class.INSTRUCTION if has_instruction else None
    
    # Check if schema is a string (JSON) or already a dict
    if has_schema:
        if isinstance(schema_attr, str):
            try:
                schema_json = json.loads(schema_attr)
            except json.JSONDecodeError:
                print(f"❌ Error: SCHEMA attribute is not valid JSON: {schema_attr}")
                return False
        else:
            schema_json = schema_attr
    else:
        schema_json = None
    
    schema_valid = schema_json is not None and schema_json.get("properties", {}).get(f"{category}_field") is not None
    instruction_valid = instruction_value is not None and f"{category} test information" in instruction_value
    
    if not schema_valid:
        print("❌ Error: SCHEMA attribute is invalid or does not match expected schema")
        return False
    
    if not instruction_valid:
        print("❌ Error: INSTRUCTION attribute is invalid or does not match expected instruction")
        return False
    
    # Instantiate the strategy
    try:
        # Only pass provider and api_token, not instruction
        strategy_instance = strategy_class(provider="test_provider", api_token="test_token")
        print("✅ Strategy instantiated successfully")
        
        # Print strategy instance details
        print("\nVerifying strategy instance...")
        print(f"Provider: {strategy_instance.provider}")
        print(f"API Token: {strategy_instance.api_token}")
        print(f"Instruction: {strategy_class.INSTRUCTION}")
        print(f"Schema: {json.dumps(schema_json, indent=2)}")
    except Exception as e:
        print(f"❌ Error instantiating strategy: {e}")
        return False
    
    # Test the extract method
    try:
        result = strategy_instance.extract("test content")
        print(f"Extract result: {result}")
        print("✅ Extract method called successfully")
    except Exception as e:
        print(f"❌ Error calling extract method: {e}")
        return False
    
    return True

def main():
    print("=" * 80)
    print("TESTING ALL STRATEGY CATEGORIES")
    print("=" * 80)
    print()
    
    print("System Information:")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"Created temporary directory: {temp_dir}")
    print()
    
    try:
        # Initialize the template generator
        print("Initializing template generator...")
        generator = StrategyTemplateGeneratorClassAttrs(output_dir=temp_dir)
        print("✅ Generator initialized successfully")
        print()
        
        # Test each category
        results = {}
        for category in TEST_CATEGORIES:
            results[category] = test_category(generator, temp_dir, category)
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        all_passed = True
        for category, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{category}: {status}")
            if not passed:
                all_passed = False
        
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED!")
        print("=" * 80)
        
    finally:
        # Clean up
        print(f"\nCleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()