#!/usr/bin/env python3
"""
Strategy Template Generator for the cry_a_4mcp.crawl4ai package.

This module provides functionality to generate new extraction strategy classes
from templates, allowing users to create custom strategies without coding.
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
logger = logging.getLogger('strategy_generator')

class StrategyTemplateGenerator:
    """Generator for creating new extraction strategy classes from templates."""
    
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
        
        # Template file path
        self.template_file = self.templates_dir / "strategy_template.py.tmpl"
        
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
        
        # Append LLMExtractionStrategy suffix only if it's not already present
        if not strategy_name_clean.lower().endswith('llmextractionstrategy'):
            strategy_class_name = f"{strategy_name_clean}LLMExtractionStrategy"
        else:
            strategy_class_name = strategy_name_clean
        
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
                output_content = output_content.replace(f"{{{{{key}}}}}", value)
        
        # Create the output file path in the appropriate category subdirectory
        category_dir = self.output_dir / category.lower()
        
        # Ensure the category directory exists
        category_dir.mkdir(exist_ok=True)
        
        output_path = category_dir / output_filename
        
        # Write the generated content to the output file
        with open(output_path, 'w') as f:
            f.write(output_content)
        
        logger.info(f"Generated strategy file: {output_path}")
        
        # Try to load the strategy module immediately
        try:
            self.load_strategy_module(str(output_path))
            logger.info(f"Successfully loaded strategy module from {output_path}")
        except Exception as e:
            logger.error(f"Failed to load strategy module: {e}")
            
        return str(output_path)
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize a name for use in class names.
        
        Args:
            name: The name to clean
            
        Returns:
            Cleaned name suitable for use in a Python class name
        """
        # We no longer remove the LLMExtractionStrategy suffix if it exists
        # This ensures user-provided names with the suffix are preserved
        
        # Remove special characters and spaces
        cleaned = re.sub(r'[^\w\s]', '', name)
        
        # Replace spaces with underscores
        cleaned = cleaned.replace(' ', '_')
        
        # Ensure the name starts with a letter
        if cleaned and not cleaned[0].isalpha():
            cleaned = 'X' + cleaned
        elif not cleaned:
            cleaned = 'X'
        
        # Convert to CamelCase
        words = cleaned.split('_')
        camel_case = ''.join(word.capitalize() for word in words)
        
        return camel_case
    
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
        
    def edit_strategy_file(self, 
                          strategy_path: str, 
                          strategy_name: str, 
                          strategy_description: str,
                          schema: Dict[str, Any],
                          instruction: str,
                          default_provider: str = "openai",
                          category: str = "general") -> str:
        """Edit an existing strategy file with updated content.
        
        Args:
            strategy_path: Path to the existing strategy file
            strategy_name: Updated name of the strategy
            strategy_description: Updated description
            schema: Updated JSON schema
            instruction: Updated instructions for the LLM
            default_provider: Updated default LLM provider
            category: Updated category for the strategy
            
        Returns:
            Path to the edited strategy file
        """
        strategy_path = Path(strategy_path)
        
        # Ensure the file exists
        if not strategy_path.exists():
            raise FileNotFoundError(f"Strategy file not found: {strategy_path}")
        
        # Read the template file
        with open(self.template_file, 'r') as f:
            template_content = f.read()
        
        # Clean and normalize the strategy name
        strategy_name_clean = self._clean_name(strategy_name)
        
        # Append LLMExtractionStrategy suffix only if it's not already present
        if not strategy_name_clean.lower().endswith('llmextractionstrategy'):
            strategy_class_name = f"{strategy_name_clean}LLMExtractionStrategy"
        else:
            strategy_class_name = strategy_name_clean
        
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
                output_content = output_content.replace(f"{{{{{key}}}}}", value)
        
        # Determine if we need to move the file to a different category
        current_category = strategy_path.parent.name
        
        if current_category != category.lower():
            # Create the new category directory if it doesn't exist
            category_dir = self.output_dir / category.lower()
            category_dir.mkdir(exist_ok=True)
            
            # Create a new file path in the new category
            new_file_path = category_dir / strategy_path.name
            
            # Delete the old file after writing the new one
            old_file_path = strategy_path
            strategy_path = new_file_path
        
        # Write the updated content to the file
        with open(strategy_path, 'w') as f:
            f.write(output_content)
        
        logger.info(f"Updated strategy file: {strategy_path}")
        
        # If we moved to a new category, delete the old file
        if current_category != category.lower():
            try:
                old_file_path.unlink()
                logger.info(f"Deleted old strategy file: {old_file_path}")
            except Exception as e:
                logger.error(f"Failed to delete old strategy file: {e}")
        
        # Try to load the strategy module immediately
        try:
            self.load_strategy_module(str(strategy_path))
            logger.info(f"Successfully loaded updated strategy module from {strategy_path}")
        except Exception as e:
            logger.error(f"Failed to load updated strategy module: {e}")
            
        return str(strategy_path)
        
    def delete_strategy_file(self, strategy_path: str) -> bool:
        """Delete a strategy file.
        
        Args:
            strategy_path: Path to the strategy file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        strategy_path = Path(strategy_path)
        
        # Ensure the file exists
        if not strategy_path.exists():
            logger.error(f"Strategy file not found: {strategy_path}")
            return False
        
        try:
            # Delete the file
            strategy_path.unlink()
            logger.info(f"Deleted strategy file: {strategy_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete strategy file: {e}")
            return False
            
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
        
        # Append LLMExtractionStrategy suffix only if it's not already present
        if not strategy_name_clean.endswith('LLMExtractionStrategy'):
            strategy_class_name = f"{strategy_name_clean}LLMExtractionStrategy"
        else:
            strategy_class_name = strategy_name_clean
        
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
                output_content = output_content.replace(f"{{{{{key}}}}}", value)
        
        return output_content