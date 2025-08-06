# Initialize the custom_strategies package
# This package contains user-created extraction strategies

import os
import importlib
import pkgutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Type
from ..base import ExtractionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('custom_strategies')

def load_custom_strategies() -> List[Type[ExtractionStrategy]]:
    """Dynamically load all custom strategy modules in this package.
    
    Returns:
        List of loaded ExtractionStrategy subclasses
    """
    strategies = []
    package_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure the directory exists
    if not package_dir.exists():
        logger.warning(f"Custom strategies directory does not exist: {package_dir}")
        return strategies
    
    # Get the package name
    package_name = __name__
    
    # Iterate through all modules in the package
    for _, module_name, is_pkg in pkgutil.iter_modules([str(package_dir)]):
        if not is_pkg and module_name.endswith('_llm'):
            try:
                # Import the module
                module = importlib.import_module(f"{package_name}.{module_name}")
                
                # Find ExtractionStrategy subclasses in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, ExtractionStrategy) and attr != ExtractionStrategy:
                        strategies.append(attr)
                        logger.info(f"Loaded custom strategy: {attr.__name__}")
            except Exception as e:
                logger.error(f"Error loading custom strategy module {module_name}: {e}")
    
    return strategies