"""Main API router for CRY-A-4MCP platform.

This module creates and configures the main API router that consolidates all
endpoint modules into a unified FastAPI router. It handles dependency injection
for database instances and provides a single entry point for all API routes.

The router integrates the following endpoint modules:
    - URL Configurations: Managing crawl target URLs
    - URL Mappings: Associating URLs with extraction strategies
    - Crawlers: Web crawler configuration management
    - Crawl Jobs: Individual crawling task execution
    - Extractors: Extraction strategy discovery and management

Usage:
    ```python
    from cry_a_4mcp.api.router import create_api_router
    
    # Create router with database dependencies
    api_router = create_api_router(
        url_db=url_database,
        url_mapping_db=mapping_database,
        crawler_db=crawler_database,
        active_jobs=job_tracker
    )
    
    # Include in FastAPI app
    app.include_router(api_router)
    ```

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

# Standard library imports
from typing import Dict, Any
import logging

# FastAPI imports
from fastapi import APIRouter

# Internal endpoint module imports
from .endpoints.url_configurations import setup_url_configuration_routes
from .endpoints.url_mappings import setup_url_mapping_routes
from .endpoints.crawlers import setup_crawler_routes
from .endpoints.crawl_jobs import setup_crawl_job_routes
from .endpoints.extractors import router as extractors_router
from .endpoints.test_url import router as test_url_router
from .endpoints.openrouter import setup_openrouter_routes

# Database type imports for type hints
from ..storage.url_configuration_db import URLConfigurationDatabase
from ..storage.url_mappings_db import URLMappingsDatabase
from ..storage.crawler_db import CrawlerDatabase

# Module-level logger
logger = logging.getLogger(__name__)


def create_api_router(
    url_configuration_db: URLConfigurationDatabase,
    url_mappings_db: URLMappingsDatabase,
    crawler_db: CrawlerDatabase,
    active_jobs: Dict[str, Any]
) -> APIRouter:
    """Create and configure the main API router with all endpoints.
    
    This function creates a unified FastAPI router that includes all endpoint
    modules with their respective database dependencies injected. It serves as
    the central configuration point for the entire API surface.
    
    The function follows the dependency injection pattern, accepting database
    instances and other dependencies as parameters and passing them to the
    individual endpoint setup functions. This approach ensures loose coupling
    and makes testing easier.
    
    Args:
        url_configuration_db (URLConfigurationDatabase): Database instance for URL configuration operations.
            Must be properly initialized and connected.
        url_mappings_db (URLMappingsDatabase): Database instance for URL mappings operations.
            Must be properly initialized and connected.
        crawler_db (CrawlerDatabase): Database instance for crawler configuration operations.
            Must be properly initialized and connected.
        active_jobs (Dict[str, Any]): Dictionary for tracking active crawl jobs.
            Used for job status management and coordination.
    
    Returns:
        APIRouter: Configured FastAPI router with all API endpoints registered
            and ready for inclusion in the main application.
    
    Raises:
        Exception: May raise exceptions during router setup if database connections
            are invalid or endpoint configuration fails.
    
    Example:
        ```python
        # Initialize databases
        url_configuration_db = URLConfigurationDatabase()
        crawler_db = CrawlerDatabase()
        jobs = {}
        
        # Create unified router
        api_router = create_api_router(
            url_configuration_db=url_configuration_db,
            crawler_db=crawler_db,
            active_jobs=jobs
        )
        
        # Include in FastAPI application
        app.include_router(api_router)
        ```
    
    Note:
        All database instances should be properly initialized and connected
        before passing them to this function. The active_jobs dictionary
        should be shared across the application for proper job coordination.
    """
    logger.info("Creating main API router with all endpoint modules")
    
    # Create the main router instance with /api prefix
    main_router = APIRouter(prefix="/api")
    
    try:
        # Setup unified URL configuration routes
        logger.debug("Setting up unified URL configuration routes")
        url_configuration_router = setup_url_configuration_routes(url_configuration_db)
        main_router.include_router(url_configuration_router)
        
        # Setup URL mapping routes
        logger.debug("Setting up URL mapping routes")
        url_mapping_router = setup_url_mapping_routes(url_mappings_db, url_configuration_db)
        main_router.include_router(url_mapping_router)
        
        # Setup crawler configuration routes
        logger.debug("Setting up crawler configuration routes")
        crawler_router = setup_crawler_routes(crawler_db)
        main_router.include_router(crawler_router)
        
        # Setup crawl job routes
        logger.debug("Setting up crawl job routes")
        # Create a GenericAsyncCrawler instance for crawl jobs
        from ..crypto_crawler.crawler import GenericAsyncCrawler
        crawler = GenericAsyncCrawler()
        crawl_job_router = setup_crawl_job_routes(url_configuration_db, crawler)
        main_router.include_router(crawl_job_router)
        
        # Include extractor routes (no setup function needed)
        logger.debug("Including extractor routes")
        main_router.include_router(extractors_router)
        
        # Include test URL routes
        logger.debug("Including test URL routes")
        main_router.include_router(test_url_router)
        
        # Include OpenRouter routes
        logger.debug("Including OpenRouter routes")
        openrouter_router = setup_openrouter_routes()
        main_router.include_router(openrouter_router)
        
        logger.info("Successfully created main API router with all endpoints")
        return main_router
        
    except Exception as e:
        logger.error(f"Failed to create API router: {str(e)}", exc_info=True)
        raise