#!/usr/bin/env python3
"""
Registry system for extraction strategies.

This module provides a registry system that allows extraction strategies to register
themselves, enabling dynamic discovery and management of available strategies.
"""

import logging
import importlib
import os
from pathlib import Path
from typing import Dict, Type, List, Any, Optional, Callable, Union
import inspect
from .base import ExtractionStrategy

# Try to import custom strategies if available
try:
    from .custom_strategies import load_custom_strategies
    HAS_CUSTOM_STRATEGIES = True
except ImportError:
    HAS_CUSTOM_STRATEGIES = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('extraction_strategy_registry')

class StrategyRegistry:
    """Registry for extraction strategies.
    
    This class provides a registry system for extraction strategies, allowing them
    to be registered, discovered, and instantiated dynamically.
    """
    
    _strategies: Dict[str, Type[ExtractionStrategy]] = {}
    _metadata: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register(cls, name: str = None, description: str = None, 
                 category: str = None, schema: Dict[str, Any] = None,
                 config_schema: Dict[str, Any] = None) -> Callable:
        """Register a strategy class with the registry.
        
        This method can be used as a decorator to register a strategy class.
        
        Args:
            name: Optional name for the strategy (defaults to class name)
            description: Optional description of the strategy
            category: Optional category for the strategy
            schema: Optional JSON schema for the strategy's output
            config_schema: Optional JSON schema for the strategy's configuration
            
        Returns:
            Decorator function
        """
        def decorator(strategy_class: Type[ExtractionStrategy]) -> Type[ExtractionStrategy]:
            # Validate that the class is a subclass of ExtractionStrategy
            if not issubclass(strategy_class, ExtractionStrategy):
                raise TypeError(f"{strategy_class.__name__} must be a subclass of ExtractionStrategy")
            
            # Use the provided name or the class name
            strategy_name = name or strategy_class.__name__
            
            # Register the strategy class
            cls._strategies[strategy_name] = strategy_class
            
            # Extract init parameters for configuration schema if not provided
            derived_config_schema = config_schema
            if derived_config_schema is None:
                derived_config_schema = cls._derive_config_schema(strategy_class)
            
            # Store metadata about the strategy
            cls._metadata[strategy_name] = {
                "description": description or strategy_class.__doc__ or "",
                "category": category or "general",
                "schema": schema or {},
                "config_schema": derived_config_schema,
                "class": strategy_class.__name__
            }
            
            logger.info(f"Registered extraction strategy: {strategy_name}")
            return strategy_class
        
        return decorator
    
    @classmethod
    def _derive_config_schema(cls, strategy_class: Type[ExtractionStrategy]) -> Dict[str, Any]:
        """Derive a configuration schema from the class's __init__ method.
        
        Args:
            strategy_class: The strategy class to derive the schema from
            
        Returns:
            JSON schema for the strategy's configuration
        """
        # Get the __init__ method signature
        signature = inspect.signature(strategy_class.__init__)
        
        # Create a properties dictionary for each parameter
        properties = {}
        required = []
        
        for param_name, param in signature.parameters.items():
            # Skip self parameter
            if param_name == "self":
                continue
                
            # Skip **kwargs parameter
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                continue
                
            # Determine if the parameter is required
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
            
            # Get parameter type annotation if available
            param_type = "string"  # Default type
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_type = "string"
                elif param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == dict or param.annotation == Dict:
                    param_type = "object"
                elif param.annotation == list or param.annotation == List:
                    param_type = "array"
            
            # Create property definition
            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter: {param_name}"
            }
            
            # Add default value if available
            if param.default != inspect.Parameter.empty and param.default is not None:
                properties[param_name]["default"] = param.default
        
        # Create the schema
        schema = {
            "type": "object",
            "properties": properties,
            "required": required
        }
        
        return schema
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[ExtractionStrategy]]:
        """Get a strategy class by name.
        
        Args:
            name: Name of the strategy to get
            
        Returns:
            Strategy class or None if not found
        """
        return cls._strategies.get(name)
    
    @classmethod
    def get_all(cls) -> Dict[str, Type[ExtractionStrategy]]:
        """Get all registered strategy classes.
        
        Returns:
            Dictionary of strategy names to strategy classes
        """
        return cls._strategies.copy()
    
    @classmethod
    def get_metadata(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a strategy.
        
        Args:
            name: Name of the strategy to get metadata for
            
        Returns:
            Metadata dictionary or None if not found
        """
        return cls._metadata.get(name)
    
    @classmethod
    def get_all_metadata(cls) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all registered strategies.
        
        Returns:
            Dictionary of strategy names to metadata dictionaries
        """
        return cls._metadata.copy()
    
    @classmethod
    def get_by_category(cls, category: str) -> Dict[str, Type[ExtractionStrategy]]:
        """Get all strategies in a category.
        
        Args:
            category: Category to filter by
            
        Returns:
            Dictionary of strategy names to strategy classes
        """
        return {name: strategy for name, strategy in cls._strategies.items()
                if cls._metadata.get(name, {}).get("category") == category}
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get all available categories.
        
        Returns:
            List of category names
        """
        return list(set(metadata.get("category", "general") for metadata in cls._metadata.values()))
    
    @classmethod
    def unregister(cls, name: str) -> bool:
        """Unregister a strategy.
        
        Args:
            name: Name of the strategy to unregister
            
        Returns:
            True if the strategy was unregistered, False if it wasn't registered
        """
        if name in cls._strategies:
            del cls._strategies[name]
            if name in cls._metadata:
                del cls._metadata[name]
            logger.info(f"Unregistered extraction strategy: {name}")
            return True
        return False

    @classmethod
    def load_custom_strategies(cls) -> None:
        """Load and register custom strategies from the custom_strategies package.
        
        This method dynamically loads all custom strategies from the custom_strategies
        package and registers them with the registry.
        """
        if not HAS_CUSTOM_STRATEGIES:
            logger.warning("Custom strategies package not available")
            return
        
        try:
            # Load custom strategies
            custom_strategy_classes = load_custom_strategies()
            
            # Register each custom strategy
            for strategy_class in custom_strategy_classes:
                # Use the class name as the strategy name
                strategy_name = strategy_class.__name__
                
                # Register the strategy class
                cls._strategies[strategy_name] = strategy_class
                
                # Extract init parameters for configuration schema
                config_schema = cls._derive_config_schema(strategy_class)
                
                # Store metadata about the strategy
                cls._metadata[strategy_name] = {
                    "description": strategy_class.__doc__ or "",
                    "category": "custom",  # Mark as a custom strategy
                    "schema": getattr(strategy_class, "schema", {}),
                    "config_schema": config_schema,
                    "class": strategy_class.__name__
                }
                
                logger.info(f"Registered custom extraction strategy: {strategy_name}")
        except Exception as e:
            logger.error(f"Error loading custom strategies: {e}")
            
    @classmethod
    def load_category_strategies(cls) -> None:
        """Load and register strategies from category subdirectories.
        
        This method dynamically loads strategies from all category subdirectories
        within the extraction_strategies package.
        """
        try:
            # Get the base directory for extraction strategies
            base_dir = Path(__file__).parent
            
            # List of standard category directories to scan
            categories = [
                "academic", 
                "crypto", 
                "financial", 
                "news", 
                "nft", 
                "product", 
                "social",
                "general",
                "workflow",
                "composite"
            ]
            
            for category in categories:
                category_dir = base_dir / category
                
                # Skip if the directory doesn't exist
                if not category_dir.exists() or not category_dir.is_dir():
                    continue
                    
                logger.info(f"Scanning category directory: {category}")
                
                # Import all Python files in the category directory
                for py_file in category_dir.glob("*.py"):
                    if py_file.name == "__init__.py":
                        continue
                        
                    # Convert file path to module path
                    module_name = f"src.cry_a_4mcp.crawl4ai.extraction_strategies.{category}.{py_file.stem}"
                    
                    try:
                        # Import the module
                        module = importlib.import_module(module_name)
                        
                        # Find all strategy classes in the module
                        for name, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and 
                                issubclass(obj, ExtractionStrategy) and 
                                obj != ExtractionStrategy and
                                obj.__module__ == module.__name__):
                                
                                # Skip if already registered
                                if name in cls._strategies:
                                    continue
                                    
                                # Register the strategy class
                                cls._strategies[name] = obj
                                
                                # Extract init parameters for configuration schema
                                config_schema = cls._derive_config_schema(obj)
                                
                                # Store metadata about the strategy
                                cls._metadata[name] = {
                                    "description": obj.__doc__ or "",
                                    "category": category,
                                    "schema": getattr(obj, "schema", {}),
                                    "config_schema": config_schema,
                                    "class": name
                                }
                                
                                logger.info(f"Registered {category} extraction strategy: {name}")
                    except Exception as e:
                        logger.error(f"Error loading module {module_name}: {e}")
        except Exception as e:
            logger.error(f"Error scanning category directories: {e}")
            
    @classmethod
    def get_strategy_file_path(cls, strategy_name: str) -> Optional[str]:
        """Get the file path for a registered strategy.
        
        Args:
            strategy_name: Name of the strategy to get the file path for
            
        Returns:
            Absolute file path to the strategy file or None if not found
        """
        if strategy_name not in cls._strategies:
            return None
            
        strategy_class = cls._strategies[strategy_name]
        category = cls._metadata.get(strategy_name, {}).get("category", "general")
        
        # Get the module file path
        module_path = inspect.getmodule(strategy_class).__file__
        if not module_path:
            return None
            
        return module_path
        
    @classmethod
    def reload_strategies(cls) -> None:
        """Reload all strategies from custom and category directories.
        
        This method clears the existing registry and reloads all strategies,
        allowing newly created strategies to be registered without restarting
        the application.
        
        Returns:
            None
        """
        import sys
        
        # Clear existing strategies and metadata
        cls._strategies = {}
        cls._metadata = {}
        
        logger.info("Reloading all strategies...")
        
        try:
            # Clear module cache for strategy modules to force reload from disk
            modules_to_remove = []
            for module_name in sys.modules.keys():
                if ('cry_a_4mcp.crawl4ai.extraction_strategies' in module_name and 
                    module_name != 'src.cry_a_4mcp.crawl4ai.extraction_strategies.registry'):
                    modules_to_remove.append(module_name)
            
            for module_name in modules_to_remove:
                del sys.modules[module_name]
                logger.debug(f"Cleared module cache for: {module_name}")
            
            # Reload custom strategies
            cls.load_custom_strategies()
            # Reload category strategies
            cls.load_category_strategies()
            logger.info(f"Successfully reloaded {len(cls._strategies)} strategies")
        except Exception as e:
            logger.error(f"Failed to reload strategies: {e}")

# Create a decorator for easy registration
register_strategy = StrategyRegistry.register

# Load custom strategies and category strategies at module import time
try:
    StrategyRegistry.load_custom_strategies()
    StrategyRegistry.load_category_strategies()
except Exception as e:
    logger.error(f"Failed to load strategies: {e}")