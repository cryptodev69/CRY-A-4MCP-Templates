#!/usr/bin/env python3
"""
Extension for the StrategyFactory class.

This module extends the StrategyFactory class with additional methods
for creating strategy instances with specific provider, model, and API key.
"""

import logging
from typing import Dict, Any, Optional

from .factory import StrategyFactory
from .base import ExtractionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('extraction_strategy_factory_extension')

# Default provider and model settings
DEFAULT_PROVIDER = "openrouter"
DEFAULT_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Extend the StrategyFactory class with a create_strategy method
def create_strategy(cls, strategy_class_name: str, provider: str = None, model: str = None, api_key: str = None) -> ExtractionStrategy:
    """
    Create a strategy instance by class name with provider, model, and API key.
    
    Args:
        strategy_class_name: Name of the strategy class to create
        provider: LLM provider (e.g., 'openai', 'anthropic', 'openrouter')
        model: LLM model name
        api_key: API key for the provider
        
    Returns:
        Strategy instance
        
    Raises:
        ValueError: If the strategy class is not found or initialization fails
    """
    # Create configuration dictionary
    config = {}
    
    # Use default provider and model if not specified
    if not provider:
        provider = DEFAULT_PROVIDER
        logger.info(f"Using default provider: {DEFAULT_PROVIDER}")
    
    if not model and provider == DEFAULT_PROVIDER:
        model = DEFAULT_MODEL
        logger.info(f"Using default model: {DEFAULT_MODEL}")
    
    config['provider'] = provider
    
    if model:
        config['model'] = model
    
    if api_key:
        # Handle both api_key and api_token parameters
        config['api_key'] = api_key
        config['api_token'] = api_key  # Some strategies use api_token instead of api_key
    
    logger.info(f"Creating strategy instance: {strategy_class_name} with provider: {provider}, model: {model}")
    
    try:
        # Create the strategy instance
        return cls.create(strategy_class_name, config)
    except Exception as e:
        logger.error(f"Failed to create strategy instance: {strategy_class_name} - {str(e)}")
        raise ValueError(f"Failed to create strategy '{strategy_class_name}': {str(e)}")

# Add the method to the StrategyFactory class
setattr(StrategyFactory, 'create_strategy', classmethod(create_strategy))