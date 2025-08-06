"""URL Mapping Service Package.

This package provides a comprehensive URL mapping service with support for
multiple extractors, rate limiting, validation, and monitoring.
"""

__version__ = "0.1.0"
__author__ = "URL Mapping Service Team"
__email__ = "team@urlmapping.service"

from .config import Settings, get_settings
from .exceptions import (
    URLMappingBaseError,
    URLMappingNotFoundError,
    URLMappingValidationError,
    URLMappingDuplicateError,
    DatabaseError,
    ExtractorNotFoundError,
    URLConfigNotFoundError,
)
from .models import (
    URLMapping,
    URLMappingExtractor,
    URLMappingCreate,
    URLMappingUpdate,
    URLMappingResponse,
    URLMappingListResponse,
    URLMappingStats,
)
from .service import URLMappingService

__all__ = [
    "Settings",
    "get_settings",
    "URLMappingBaseError",
    "URLMappingNotFoundError",
    "URLMappingValidationError",
    "URLMappingDuplicateError",
    "DatabaseError",
    "ExtractorNotFoundError",
    "URLConfigNotFoundError",
    "URLMapping",
    "URLMappingExtractor",
    "URLMappingCreate",
    "URLMappingUpdate",
    "URLMappingResponse",
    "URLMappingListResponse",
    "URLMappingStats",
    "URLMappingService",
]