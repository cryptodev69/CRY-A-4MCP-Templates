"""Custom exceptions for URL Mapping Service.

This module defines all custom exception classes used throughout the service,
providing clear error handling and appropriate HTTP status codes.
"""

from typing import Any, Dict, Optional


class URLMappingBaseError(Exception):
    """Base exception class for URL Mapping Service.
    
    All custom exceptions should inherit from this class.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        """Initialize base exception.
        
        Args:
            message: Human-readable error message.
            error_code: Machine-readable error code.
            details: Additional error details.
            status_code: HTTP status code.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary.
        
        Returns:
            Dict containing error information.
        """
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }
    
    def __str__(self) -> str:
        """String representation of the exception."""
        return f"{self.error_code}: {self.message}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the exception."""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"status_code={self.status_code}, "
            f"details={self.details})"
        )


class URLMappingNotFoundError(URLMappingBaseError):
    """Exception raised when a URL mapping is not found."""
    
    def __init__(
        self,
        mapping_id: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs
    ):
        """Initialize not found exception.
        
        Args:
            mapping_id: ID of the missing mapping.
            message: Custom error message.
            **kwargs: Additional arguments for base class.
        """
        if message is None:
            if mapping_id:
                message = f"URL mapping with ID '{mapping_id}' not found"
            else:
                message = "URL mapping not found"
        
        details = kwargs.pop("details", {})
        if mapping_id:
            details["mapping_id"] = mapping_id
        
        super().__init__(
            message=message,
            error_code="URL_MAPPING_NOT_FOUND",
            details=details,
            status_code=404,
            **kwargs
        )


class URLMappingValidationError(URLMappingBaseError):
    """Exception raised when URL mapping validation fails."""
    
    def __init__(
        self,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        message: Optional[str] = None,
        validation_errors: Optional[list] = None,
        **kwargs
    ):
        """Initialize validation exception.
        
        Args:
            field: Field that failed validation.
            value: Invalid value.
            message: Custom error message.
            validation_errors: List of validation errors.
            **kwargs: Additional arguments for base class.
        """
        if message is None:
            if field:
                message = f"Validation failed for field '{field}'"
            else:
                message = "URL mapping validation failed"
        
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        if validation_errors:
            details["validation_errors"] = validation_errors
        
        super().__init__(
            message=message,
            error_code="URL_MAPPING_VALIDATION_ERROR",
            details=details,
            status_code=422,
            **kwargs
        )


class URLMappingDuplicateError(URLMappingBaseError):
    """Exception raised when attempting to create a duplicate URL mapping."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        extractor: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs
    ):
        """Initialize duplicate exception.
        
        Args:
            url: Duplicate URL.
            extractor: Extractor name.
            message: Custom error message.
            **kwargs: Additional arguments for base class.
        """
        if message is None:
            if url and extractor:
                message = f"URL mapping already exists for URL '{url}' with extractor '{extractor}'"
            elif url:
                message = f"URL mapping already exists for URL '{url}'"
            else:
                message = "URL mapping already exists"
        
        details = kwargs.pop("details", {})
        if url:
            details["url"] = url
        if extractor:
            details["extractor"] = extractor
        
        super().__init__(
            message=message,
            error_code="URL_MAPPING_DUPLICATE",
            details=details,
            status_code=409,
            **kwargs
        )


class DatabaseError(URLMappingBaseError):
    """Exception raised when database operations fail."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        """Initialize database exception.
        
        Args:
            message: Error message.
            operation: Database operation that failed.
            table: Database table involved.
            **kwargs: Additional arguments for base class.
        """
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
            status_code=500,
            **kwargs
        )


class ExtractorNotFoundError(URLMappingBaseError):
    """Exception raised when a specified extractor is not found."""
    
    def __init__(
        self,
        extractor_name: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs
    ):
        """Initialize extractor not found exception.
        
        Args:
            extractor_name: Name of the missing extractor.
            message: Custom error message.
            **kwargs: Additional arguments for base class.
        """
        if message is None:
            if extractor_name:
                message = f"Extractor '{extractor_name}' not found"
            else:
                message = "Extractor not found"
        
        details = kwargs.pop("details", {})
        if extractor_name:
            details["extractor_name"] = extractor_name
        
        super().__init__(
            message=message,
            error_code="EXTRACTOR_NOT_FOUND",
            details=details,
            status_code=404,
            **kwargs
        )


class URLConfigNotFoundError(URLMappingBaseError):
    """Exception raised when a URL configuration is not found."""
    
    def __init__(
        self,
        config_id: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs
    ):
        """Initialize URL config not found exception.
        
        Args:
            config_id: ID of the missing URL configuration.
            message: Custom error message.
            **kwargs: Additional arguments for base class.
        """
        if message is None:
            if config_id:
                message = f"URL configuration with ID '{config_id}' not found"
            else:
                message = "URL configuration not found"
        
        details = kwargs.pop("details", {})
        if config_id:
            details["config_id"] = config_id
        
        super().__init__(
            message=message,
            error_code="URL_CONFIG_NOT_FOUND",
            details=details,
            status_code=404,
            **kwargs
        )


class RateLimitExceededError(URLMappingBaseError):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(
        self,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        retry_after: Optional[int] = None,
        message: Optional[str] = None,
        **kwargs
    ):
        """Initialize rate limit exception.
        
        Args:
            limit: Rate limit threshold.
            window: Time window in seconds.
            retry_after: Seconds to wait before retrying.
            message: Custom error message.
            **kwargs: Additional arguments for base class.
        """
        if message is None:
            if limit and window:
                message = f"Rate limit exceeded: {limit} requests per {window} seconds"
            else:
                message = "Rate limit exceeded"
        
        details = kwargs.pop("details", {})
        if limit:
            details["limit"] = limit
        if window:
            details["window"] = window
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
            status_code=429,
            **kwargs
        )


class PermissionDeniedError(URLMappingBaseError):
    """Exception raised when access is denied."""
    
    def __init__(
        self,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs
    ):
        """Initialize permission denied exception.
        
        Args:
            resource: Resource being accessed.
            action: Action being performed.
            message: Custom error message.
            **kwargs: Additional arguments for base class.
        """
        if message is None:
            if resource and action:
                message = f"Permission denied: cannot {action} {resource}"
            elif resource:
                message = f"Permission denied: access to {resource} forbidden"
            else:
                message = "Permission denied"
        
        details = kwargs.pop("details", {})
        if resource:
            details["resource"] = resource
        if action:
            details["action"] = action
        
        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED",
            details=details,
            status_code=403,
            **kwargs
        )


class InvalidParameterError(URLMappingBaseError):
    """Exception raised when invalid parameters are provided."""
    
    def __init__(
        self,
        parameter: Optional[str] = None,
        value: Optional[Any] = None,
        expected: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs
    ):
        """Initialize invalid parameter exception.
        
        Args:
            parameter: Name of the invalid parameter.
            value: Invalid value provided.
            expected: Expected value or format.
            message: Custom error message.
            **kwargs: Additional arguments for base class.
        """
        if message is None:
            if parameter and expected:
                message = f"Invalid parameter '{parameter}': expected {expected}"
            elif parameter:
                message = f"Invalid parameter '{parameter}'"
            else:
                message = "Invalid parameter provided"
        
        details = kwargs.pop("details", {})
        if parameter:
            details["parameter"] = parameter
        if value is not None:
            details["value"] = str(value)
        if expected:
            details["expected"] = expected
        
        super().__init__(
            message=message,
            error_code="INVALID_PARAMETER",
            details=details,
            status_code=400,
            **kwargs
        )


# Exception mapping for HTTP status codes
EXCEPTION_STATUS_MAP = {
    URLMappingNotFoundError: 404,
    URLConfigNotFoundError: 404,
    ExtractorNotFoundError: 404,
    URLMappingValidationError: 422,
    URLMappingDuplicateError: 409,
    RateLimitExceededError: 429,
    PermissionDeniedError: 403,
    InvalidParameterError: 400,
    DatabaseError: 500,
    URLMappingBaseError: 500,
}


def get_exception_status_code(exception: Exception) -> int:
    """Get HTTP status code for exception.
    
    Args:
        exception: Exception instance.
        
    Returns:
        int: HTTP status code.
    """
    if isinstance(exception, URLMappingBaseError):
        return exception.status_code
    
    # Check exception type mapping
    for exc_type, status_code in EXCEPTION_STATUS_MAP.items():
        if isinstance(exception, exc_type):
            return status_code
    
    # Default to 500 for unknown exceptions
    return 500