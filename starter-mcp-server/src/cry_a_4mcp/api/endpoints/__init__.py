"""API endpoints module for CRY-A-4MCP."""

from .url_configurations import setup_url_configuration_routes
from .url_mappings import setup_url_mapping_routes
from .crawlers import setup_crawler_routes
from .crawl_jobs import setup_crawl_job_routes
from .extractors import router as extractors_router
from .test_url import router as test_url_router
from .openrouter import setup_openrouter_routes
from .adaptive_crawling import setup_adaptive_routes

__all__ = [
    "setup_url_configuration_routes",
    "setup_url_mapping_routes",
    "setup_crawler_routes",
    "setup_crawl_job_routes",
    "extractors_router",
    "test_url_router",
    "setup_openrouter_routes",
    "setup_adaptive_routes"
]