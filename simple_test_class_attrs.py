#!/usr/bin/env python3
"""
Simple test class with class attributes for SCHEMA and INSTRUCTION.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('simple_test')

class BaseLLMStrategy:
    """Base class for LLM strategies."""
    
    def __init__(self, schema, instruction, **kwargs):
        self.schema = schema
        self.instruction = instruction
        for key, value in kwargs.items():
            setattr(self, key, value)

class TestLLMStrategy(BaseLLMStrategy):
    """Test strategy with class attributes for SCHEMA and INSTRUCTION."""
    
    # Define the schema as a class attribute
    SCHEMA = {
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
    
    # Define the instruction as a class attribute
    INSTRUCTION = """Extract the title, summary, and key points from the provided content.
    The title should be the main headline or title of the content.
    The summary should be a concise overview of the main points.
    The key points should be a list of the most important information from the content.
    """
    
    def __init__(self, **kwargs):
        """Initialize the Test strategy."""
        super().__init__(
            schema=self.SCHEMA,
            instruction=self.INSTRUCTION,
            **kwargs
        )

def main():
    """Test the TestLLMStrategy class."""
    logger.info("Testing TestLLMStrategy class")
    
    # Print the class attributes
    logger.info(f"SCHEMA: {TestLLMStrategy.SCHEMA}")
    logger.info(f"INSTRUCTION: {TestLLMStrategy.INSTRUCTION}")
    
    # Create an instance of the class
    strategy = TestLLMStrategy(provider="test")
    
    # Print the instance attributes
    logger.info(f"schema: {strategy.schema}")
    logger.info(f"instruction: {strategy.instruction}")
    logger.info(f"provider: {strategy.provider}")
    
    logger.info("Test completed successfully")

if __name__ == "__main__":
    main()