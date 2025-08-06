#!/usr/bin/env python3
"""
Test script for the StrategyTemplateGeneratorClassAttrs class.

This script tests the generation of a new strategy file using the class attributes template.
"""

import os
import json
import logging
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.templates.strategy_generator_class_attrs import StrategyTemplateGeneratorClassAttrs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_strategy_generator_class_attrs')

def main():
    """Main function to test the StrategyTemplateGeneratorClassAttrs class."""
    # Create a generator instance
    generator = StrategyTemplateGeneratorClassAttrs()
    
    # Define test strategy parameters
    strategy_name = "TestGenerated"
    strategy_description = "A test strategy generated with class attributes."
    
    # Define a simple schema
    schema = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title or headline of the content"
            },
            "summary": {
                "type": "string",
                "description": "A brief summary of the content"
            },
            "key_points": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of key points from the content"
            }
        },
        "required": ["title", "summary"]
    }
    
    # Define a simple instruction
    instruction = """Extract the title, summary, and key points from the provided content.
The title should be the main headline or title of the content.
The summary should be a concise overview of the main points.
The key points should be a list of the most important information from the content.
"""
    
    # Generate the strategy file
    try:
        output_path = generator.generate_strategy_file(
            strategy_name=strategy_name,
            strategy_description=strategy_description,
            schema=schema,
            instruction=instruction,
            default_provider="openai",
            category="test"
        )
        
        logger.info(f"Successfully generated strategy file: {output_path}")
        
        # Now verify that the file exists and has class attributes
        full_path = os.path.join(generator.output_dir, output_path)
        if os.path.exists(full_path):
            logger.info(f"File exists at {full_path}")
            
            # Use the test_class_attrs_loading.py functionality to check for class attributes
            from test_class_attrs_loading import has_class_attributes
            
            class_name, schema_attr, instruction_attr = has_class_attributes(full_path)
            
            if class_name:
                logger.info(f"Found class {class_name} with SCHEMA and INSTRUCTION class attributes")
                logger.info(f"SCHEMA: {schema_attr}")
                logger.info(f"INSTRUCTION: {instruction_attr}")
                logger.info("Test completed successfully")
            else:
                logger.error("No class with SCHEMA and INSTRUCTION class attributes found")
        else:
            logger.error(f"File does not exist at {full_path}")
    
    except Exception as e:
        logger.error(f"Error generating strategy file: {e}")

if __name__ == "__main__":
    main()