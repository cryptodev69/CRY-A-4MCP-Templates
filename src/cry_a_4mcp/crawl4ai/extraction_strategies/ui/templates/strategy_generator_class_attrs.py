#!/usr/bin/env python3
"""
Strategy Template Generator for the cry_a_4mcp.crawl4ai package.

This module provides functionality to generate new extraction strategy classes
from templates, allowing users to create custom strategies without coding.

This version uses a template that defines SCHEMA and INSTRUCTION as class attributes.
"""

import os
import json
import re
import importlib.util
import sys
import logging
from pathlib import Path
from string import Template
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('strategy_generator_class_attrs')

class StrategyTemplateGeneratorClassAttrs:
    """Generator for creating new extraction strategy classes from templates with class attributes."""
    
    def __init__(self, templates_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """Initialize the strategy template generator.
        
        Args:
            templates_dir: Directory containing strategy templates
            output_dir: Directory where generated strategies will be saved
        """
        # Get the directory of this file
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # Set default directories if not provided
        self.templates_dir = Path(templates_dir) if templates_dir else current_dir
        
        # Default output directory is the parent directory of the templates
        parent_dir = current_dir.parent.parent
        self.output_dir = Path(output_dir) if output_dir else parent_dir
        
        # Template file path - using the class attributes template
        self.template_file = self.templates_dir / "strategy_template_class_attrs.py.tmpl"
        
        # Ensure the template file exists
        if not self.template_file.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_file}")
    
    def generate_strategy_file(self, 
                              strategy_name: str, 
                              strategy_description: str,
                              schema: Dict[str, Any],
                              instruction: str,
                              default_provider: str = "openai",
                              category: str = "general",
                              output_filename: Optional[str] = None) -> str:
        """Generate a new strategy file from the template.
        
        Args:
            strategy_name: Name of the strategy (e.g., "NFT", "Crypto")
            strategy_description: Description of what the strategy does
            schema: JSON schema for the extraction strategy
            instruction: Instructions for the LLM
            default_provider: Default LLM provider
            category: Category for the strategy (e.g., "crypto", "nft", "news")
            output_filename: Optional custom filename for the output file
            
        Returns:
            Path to the generated strategy file
        """
        # Read the template file
        with open(self.template_file, 'r') as f:
            template_content = f.read()
        
        # Clean and normalize the strategy name
        strategy_name_clean = self._clean_name(strategy_name)
        strategy_class_name = f"{strategy_name_clean}LLMExtractionStrategy"
        
        # Generate the filename if not provided
        if not output_filename:
            output_filename = f"{strategy_name_clean.lower()}_llm.py"
        
        # Format the schema as a pretty-printed JSON string
        schema_json = json.dumps(schema, indent=4)
        
        # Prepare the template variables
        template_vars = {
            "strategy_name": strategy_name,
            "strategy_name_lower": strategy_name_clean.lower(),
            "strategy_class_name": strategy_class_name,
            "strategy_description": strategy_description,
            "schema_json": schema_json,
            "instruction": instruction,
            "default_provider": default_provider
        }
        
        # Replace template variables
        output_content = template_content
        for key, value in template_vars.items():
            # Handle multiline values (like schema_json and instruction)
            if key in ["schema_json", "instruction"]:
                # Indent multiline content properly
                if key == "schema_json":
                    output_content = output_content.replace(f"{{{{{key}}}}}", value)
                else:  # instruction
                    # Escape any triple quotes in the instruction
                    escaped_value = value.replace('"""', '\\"\\"\\"')
                    output_content = output_content.replace(f"{{{{{key}}}}}", escaped_value)
            else:
                # Replace simple variables
                output_content = output_content.replace(f"{{{{{key}}}}}", value)
        
        # Create the output directory if it doesn't exist
        # Use os.path.join for path concatenation instead of / operator
        category_dir = os.path.join(self.output_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Write the output file
        output_path = os.path.join(category_dir, output_filename)
        with open(output_path, 'w') as f:
            f.write(output_content)
        
        logger.info(f"Generated strategy file: {output_path}")
        
        # Return the relative path from the output directory
        return str(os.path.join(category, output_filename))
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize a strategy name.
        
        Args:
            name: The raw strategy name
            
        Returns:
            Cleaned and normalized strategy name
        """
        # Remove special characters and spaces
        cleaned = re.sub(r'[^\w\s]', '', name)
        
        # Split by whitespace and capitalize each word
        words = cleaned.split()
        capitalized = [word.capitalize() for word in words]
        
        # Join the words without spaces
        return ''.join(capitalized)
    
    def load_strategy_module(self, strategy_file_path: str) -> Any:
        """Dynamically load a generated strategy module.
        
        Args:
            strategy_file_path: Path to the generated strategy file
            
        Returns:
            The loaded module
        """
        strategy_file_path = Path(strategy_file_path)
        
        # Extract the module name from the file path
        module_name = strategy_file_path.stem
        
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(module_name, strategy_file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {strategy_file_path}")
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        logger.info(f"Loaded strategy module: {module_name}")
        return module
    
    def generate_strategy_content(self, 
                                 strategy_name: str, 
                                 strategy_description: str,
                                 schema: Dict[str, Any],
                                 instruction: str,
                                 default_provider: str = "openai",
                                 category: str = "general") -> str:
        """Generate strategy file content without writing to a file.
        
        Args:
            strategy_name: Name of the strategy (e.g., "NFT", "Crypto")
            strategy_description: Description of what the strategy does
            schema: JSON schema for the extraction strategy
            instruction: Instructions for the LLM
            default_provider: Default LLM provider
            category: Category for the strategy (e.g., "crypto", "nft", "news")
            
        Returns:
            Generated strategy file content as a string
        """
        # Read the template file
        with open(self.template_file, 'r') as f:
            template_content = f.read()
        
        # Clean and normalize the strategy name
        strategy_name_clean = self._clean_name(strategy_name)
        strategy_class_name = f"{strategy_name_clean}LLMExtractionStrategy"
        
        # Format the schema as a pretty-printed JSON string
        schema_json = json.dumps(schema, indent=4)
        
        # Prepare the template variables
        template_vars = {
            "strategy_name": strategy_name,
            "strategy_name_lower": strategy_name_clean.lower(),
            "strategy_class_name": strategy_class_name,
            "strategy_description": strategy_description,
            "schema_json": schema_json,
            "instruction": instruction,
            "default_provider": default_provider
        }
        
        # Replace template variables
        output_content = template_content
        for key, value in template_vars.items():
            # Handle multiline values (like schema_json and instruction)
            if key in ["schema_json", "instruction"]:
                # Indent multiline content properly
                if key == "schema_json":
                    output_content = output_content.replace(f"{{{{{key}}}}}", value)
                else:  # instruction
                    # Escape any triple quotes in the instruction
                    escaped_value = value.replace('"""', '\\"\\"\\"')
                    output_content = output_content.replace(f"{{{{{key}}}}}", escaped_value)
            else:
                # Replace simple variables
                output_content = output_content.replace(f"{{{{{key}}}}}", value)
        
        return output_content