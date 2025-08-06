"""Custom exceptions for the URL mapping service.

This module defines domain-specific exceptions that provide clear error handling
and appropriate HTTP status codes for the API layer.
"""


class URLMappingBaseError(Exception):
    """Base exception for URL mapping related errors."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class URLMappingNotFoundError(URLMappingBaseError):
    """Raised when a URL mapping is not found.
    
    HTTP Status: 404 Not Found
    """
    pass


class URLMappingValidationError(URLMappingBaseError):
    """Raised when URL mapping validation fails.
    
    HTTP Status: 422 Unprocessable Entity
    """
    pass


class URLMappingDuplicateError(URLMappingBaseError):
    """Raised when attempting to create a duplicate URL mapping.
    
    HTTP Status: 409 Conflict
    """
    pass


class DatabaseError(URLMappingBaseError):
    """Raised when database operations fail.
    
    HTTP Status: 500 Internal Server Error
    """
    pass


class ExtractorNotFoundError(URLMappingBaseError):
    """Raised when an extractor is not found.
    
    HTTP Status: 404 Not Found
    """
    pass


class URLConfigNotFoundError(URLMappingBaseError):
    """Raised when a URL configuration is not found.
    
    HTTP Status: 404 Not Found
    """
    pass


class RateLimitExceededError(URLMappingBaseError):
    """Raised when rate limit is exceeded.
    
    HTTP Status: 429 Too Many Requests
    """
    pass


class PermissionDeniedError(URLMappingBaseError):
    """Raised when user doesn't have permission for the operation.
    
    HTTP Status: 403 Forbidden
    """
    pass


class InvalidParameterError(URLMappingBaseError):
    """Raised when invalid parameters are provided.
    
    HTTP Status: 400 Bad Request
    """
    pass