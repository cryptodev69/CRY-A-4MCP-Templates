"""Core dependencies for CRY-A-4MCP."""

from typing import Generator
from ..storage.url_configuration_db import URLConfigurationDatabase


def get_url_config_db() -> Generator[URLConfigurationDatabase, None, None]:
    """Get URL configuration database instance.
    
    Yields:
        URLConfigurationDatabase: Database instance for URL configurations.
    """
    db = URLConfigurationDatabase()
    try:
        yield db
    finally:
        # Clean up if needed
        pass