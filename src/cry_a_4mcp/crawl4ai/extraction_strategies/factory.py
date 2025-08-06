#!/usr/bin/env python3
"""
Factory for creating extraction strategy instances.

This module provides a factory for creating extraction strategy instances
based on configuration, supporting dynamic strategy creation and composition.
"""

import logging
from typing import Dict, Any, Optional, List, Type, Union
import json
from .base import ExtractionStrategy
from .registry import StrategyRegistry
from .sync_wrapper import SyncExtractionStrategyWrapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('extraction_strategy_factory')

class StrategyFactory:
    """Factory for creating extraction strategy instances.
    
    This class provides methods for creating extraction strategy instances
    based on configuration, supporting dynamic strategy creation and composition.
    """
    
    @classmethod
    def create(cls, strategy_name: str, config: Optional[Dict[str, Any]] = None) -> ExtractionStrategy:
        """Create a strategy instance by name.
        
        Args:
            strategy_name: Name of the strategy to create
            config: Optional configuration for the strategy
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If the strategy is not registered
        """
        # Get the strategy class from the registry
        strategy_class = StrategyRegistry.get(strategy_name)
        if not strategy_class:
            raise ValueError(f"Strategy '{strategy_name}' is not registered")
        
        # Create the strategy instance with the provided configuration
        config = config or {}
        try:
            strategy_instance = strategy_class(**config)
            logger.info(f"Created strategy instance: {strategy_name}")
            return strategy_instance
        except Exception as e:
            logger.error(f"Failed to create strategy instance: {strategy_name} - {str(e)}")
            raise ValueError(f"Failed to create strategy '{strategy_name}': {str(e)}")
    
    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> ExtractionStrategy:
        """Create a strategy instance from a configuration dictionary.
        
        The configuration dictionary should have a 'strategy' key with the name of the
        strategy to create, and optionally a 'config' key with the configuration for
        the strategy.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If the configuration is invalid or the strategy is not registered
        """
        # Validate the configuration
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        if "strategy" not in config:
            raise ValueError("Configuration must have a 'strategy' key")
        
        strategy_name = config["strategy"]
        strategy_config = config.get("config", {})
        
        # Create the strategy instance
        return cls.create(strategy_name, strategy_config)
    
    @classmethod
    def create_from_config_sync(cls, config: Dict[str, Any]) -> ExtractionStrategy:
        """Create a synchronized strategy instance from a configuration dictionary.
        
        The configuration dictionary should have a 'strategy' key with the name of the
        strategy to create, and optionally a 'config' key with the configuration for
        the strategy.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Synchronized strategy instance
            
        Raises:
            ValueError: If the configuration is invalid or the strategy is not registered
        """
        strategy = cls.create_from_config(config)
        return SyncExtractionStrategyWrapper(strategy)
    
    @classmethod
    def create_from_json_sync(cls, json_config: str) -> ExtractionStrategy:
        """Create a synchronized strategy instance from a JSON configuration string.
        
        Args:
            json_config: JSON configuration string
            
        Returns:
            Synchronized strategy instance
            
        Raises:
            ValueError: If the JSON is invalid or the strategy is not registered
        """
        strategy = cls.create_from_json(json_config)
        return SyncExtractionStrategyWrapper(strategy)
    
    @classmethod
    def create_composite_sync(cls, strategies: List[Dict[str, Any]]) -> ExtractionStrategy:
        """Create a synchronized composite strategy from a list of strategy configurations.
        
        Args:
            strategies: List of strategy configurations
            
        Returns:
            Synchronized composite strategy instance
            
        Raises:
            ValueError: If any of the strategies are invalid or not registered
        """
        strategy = cls.create_composite(strategies)
        return SyncExtractionStrategyWrapper(strategy)
    
    @classmethod
    def create_sync(cls, strategy_name: str, config: Optional[Dict[str, Any]] = None) -> ExtractionStrategy:
        """Create a synchronized strategy instance by name.
        
        Args:
            strategy_name: Name of the strategy to create
            config: Optional configuration for the strategy
            
        Returns:
            Synchronized strategy instance
            
        Raises:
            ValueError: If the strategy is not registered
        """
        strategy = cls.create(strategy_name, config)
        return SyncExtractionStrategyWrapper(strategy)
    
    @classmethod
    def create_from_json(cls, json_config: str) -> ExtractionStrategy:
        """Create a strategy instance from a JSON configuration string.
        
        Args:
            json_config: JSON configuration string
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If the JSON is invalid or the strategy is not registered
        """
        try:
            config = json.loads(json_config)
            return cls.create_from_config(config)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON configuration: {str(e)}")
            raise ValueError(f"Invalid JSON configuration: {str(e)}")
    
    @classmethod
    def create_composite(cls, strategies: List[Dict[str, Any]]) -> 'CompositeExtractionStrategy':
        """Create a composite strategy from a list of strategy configurations.
        
        Args:
            strategies: List of strategy configurations
            
        Returns:
            Composite strategy instance
            
        Raises:
            ValueError: If any of the strategies are invalid or not registered
        """
        # Create the strategy instances
        strategy_instances = []
        for strategy_config in strategies:
            strategy_instance = cls.create_from_config(strategy_config)
            strategy_instances.append(strategy_instance)
        
        # Create the composite strategy
        return CompositeExtractionStrategy(strategy_instances)

class CompositeExtractionStrategy(ExtractionStrategy):
    """Composite extraction strategy that combines multiple strategies.
    
    This strategy applies multiple extraction strategies in sequence and
    combines their results.
    """
    
    def __init__(self, strategies: List[ExtractionStrategy]):
        """Initialize the composite strategy.
        
        Args:
            strategies: List of extraction strategies to apply
        """
        self.strategies = strategies
        logger.info(f"Created composite strategy with {len(strategies)} strategies")
    
    async def extract(self, url: str, content: str, **kwargs) -> Dict[str, Any]:
        """Extract information from content using multiple strategies.
        
        This method applies each strategy in sequence and combines their results.
        
        Args:
            url: The URL of the content
            content: The content to extract information from
            **kwargs: Additional extraction parameters
            
        Returns:
            Combined dictionary of extracted information
        """
        logger.info(f"Starting composite extraction for URL: {url}")
        
        # Apply each strategy in sequence
        results = []
        for i, strategy in enumerate(self.strategies):
            try:
                logger.info(f"Applying strategy {i+1}/{len(self.strategies)}: {strategy.__class__.__name__}")
                result = await strategy.extract(url, content, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Strategy {i+1}/{len(self.strategies)} failed: {str(e)}")
                # Continue with other strategies even if one fails
        
        # Combine the results
        combined_result = self._combine_results(results)
        
        logger.info(f"Completed composite extraction for URL: {url}")
        return combined_result
    
    def _combine_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple extraction results into a single result.
        
        This method combines the results from multiple strategies into a single
        result dictionary. It handles merging of metadata and resolving conflicts.
        
        Args:
            results: List of extraction results to combine
            
        Returns:
            Combined extraction result
        """
        if not results:
            return {}
        
        # Start with the first result
        combined = results[0].copy()
        
        # Combine metadata from all results
        combined_metadata = combined.get("_metadata", {}).copy()
        
        # Add results from other strategies
        for result in results[1:]:
            # Merge metadata
            if "_metadata" in result:
                for key, value in result["_metadata"].items():
                    if key not in combined_metadata:
                        combined_metadata[key] = value
                    elif key == "strategies":
                        # Combine strategy lists
                        combined_metadata[key] = combined_metadata[key] + value
                    elif isinstance(value, dict) and isinstance(combined_metadata[key], dict):
                        # Recursively merge dictionaries
                        combined_metadata[key].update(value)
            
            # Add other fields, preferring non-empty values
            for key, value in result.items():
                if key == "_metadata":
                    continue
                
                if key not in combined or not combined[key]:
                    combined[key] = value
                elif isinstance(value, list) and isinstance(combined[key], list):
                    # Combine lists, avoiding duplicates
                    combined[key] = list(set(combined[key] + value))
                elif isinstance(value, dict) and isinstance(combined[key], dict):
                    # Recursively merge dictionaries
                    combined[key].update(value)
        
        # Add strategy information to metadata
        if "strategies" not in combined_metadata:
            combined_metadata["strategies"] = []
        
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            if strategy_name not in combined_metadata["strategies"]:
                combined_metadata["strategies"].append(strategy_name)
        
        # Update the combined metadata
        combined["_metadata"] = combined_metadata
        
        return combined