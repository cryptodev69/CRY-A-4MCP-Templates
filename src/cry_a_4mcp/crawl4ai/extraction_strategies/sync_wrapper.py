#!/usr/bin/env python3
"""
Synchronous wrapper for asynchronous extraction strategies.

This module provides a wrapper for asynchronous extraction strategies,
allowing them to be used in synchronous contexts like the Streamlit UI.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from functools import wraps

from .base import ExtractionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('extraction_strategy_sync_wrapper')


def sync_extract(strategy: ExtractionStrategy, url: str, content: str, **kwargs) -> Dict[str, Any]:
    """
    Synchronous wrapper for the asynchronous extract method.
    
    This function runs the asynchronous extract method in a new event loop,
    making it usable in synchronous contexts like the Streamlit UI.
    
    Args:
        strategy: The extraction strategy to use
        url: The URL of the content
        content: The content to extract information from
        **kwargs: Additional extraction parameters
        
    Returns:
        Dictionary of extracted information
        
    Raises:
        Any exceptions raised by the extract method
    """
    try:
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the extract method in the event loop
        result = loop.run_until_complete(strategy.extract(url, content, **kwargs))
        
        # Close the event loop
        loop.close()
        
        return result
    except Exception as e:
        logger.error(f"Synchronous extraction failed: {str(e)}")
        raise


class SyncExtractionStrategyWrapper:
    """
    Wrapper class for asynchronous extraction strategies.
    
    This class wraps an asynchronous extraction strategy and provides
    a synchronous interface for its methods.
    """
    
    def __init__(self, strategy: ExtractionStrategy):
        """
        Initialize the wrapper with an extraction strategy.
        
        Args:
            strategy: The extraction strategy to wrap
        """
        self.strategy = strategy
        
    def extract(self, url: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Synchronous version of the extract method.
        
        Args:
            url: The URL of the content
            content: The content to extract information from
            **kwargs: Additional extraction parameters
            
        Returns:
            Dictionary of extracted information
        """
        return sync_extract(self.strategy, url, content, **kwargs)
    
    def validate_provider_connection(self) -> tuple[bool, Optional[str]]:
        """
        Synchronous version of the validate_provider_connection method.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Create a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the validate_provider_connection method in the event loop
            result = loop.run_until_complete(self.strategy.validate_provider_connection())
            
            # Close the event loop
            loop.close()
            
            return result
        except Exception as e:
            logger.error(f"Synchronous provider validation failed: {str(e)}")
            return False, str(e)