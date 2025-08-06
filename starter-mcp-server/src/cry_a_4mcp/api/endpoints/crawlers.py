"""Crawlers API Endpoints Module.

This module provides RESTful API endpoints for managing web crawler configurations
within the CRY-A-4MCP platform. It handles the complete lifecycle of crawler
configurations including creation, retrieval, updates, deletion, and status management.

Key Features:
    - CRUD operations for crawler configurations
    - Pagination and filtering for crawler listings
    - Status management (active/inactive toggle)
    - Comprehensive error handling and logging
    - Input validation and sanitization
    - RESTful API design patterns

API Endpoints:
    GET /api/crawlers - List all crawler configurations with pagination
    GET /api/crawlers/{id} - Retrieve specific crawler configuration
    POST /api/crawlers - Create new crawler configuration
    PUT /api/crawlers/{id} - Update existing crawler configuration
    DELETE /api/crawlers/{id} - Delete crawler configuration
    POST /api/crawlers/{id}/toggle-status - Toggle crawler active status

Typical Usage:
    The endpoints are automatically registered when the FastAPI application
    starts up through the setup_crawler_routes function, which injects
    the database dependency.

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

# Standard library imports for type hints and optional values
from typing import List, Optional

# FastAPI framework imports for API routing, error handling, and query parameters
from fastapi import APIRouter, HTTPException, Query

# Python logging module for structured application logging
import logging

# Internal database layer for URL configuration persistence
from ...storage.url_configuration_db import URLConfigurationDatabase

# Pydantic models for request/response validation and serialization
from ..models import CrawlerConfigCreate, CrawlerConfigUpdate, CrawlerConfigResponse

# FastAPI router instance with URL prefix and OpenAPI tags for documentation
router = APIRouter(prefix="/api/crawlers", tags=["Crawlers"])

# Module-level logger for tracking API operations and debugging
logger = logging.getLogger(__name__)


def setup_crawler_routes(url_db: URLConfigurationDatabase):
    """Configure and register all crawler-related API endpoints.
    
    This function sets up the complete set of RESTful API endpoints for managing
    web crawler configurations. It injects the database dependency into all route
    handlers and configures proper error handling, logging, and response formatting.
    
    The function creates a closure over the database instance, allowing all endpoint
    handlers to access the database without explicit dependency injection in each
    route definition. This pattern ensures consistent database access patterns and
    simplifies testing and maintenance.
    
    Args:
        url_db (URLConfigurationDatabase): The database instance for crawler configuration
            persistence. Must be properly initialized and connected before passing
            to this function.
    
    Returns:
        APIRouter: Configured FastAPI router instance with all crawler endpoints
            registered and ready for inclusion in the main application.
    
    Raises:
        None: This function itself doesn't raise exceptions, but the individual
            endpoint handlers may raise HTTPException for various error conditions.
    
    Example:
        >>> from cry_a_4mcp.storage.url_configuration_db import URLConfigurationDatabase
        >>> db = URLConfigurationDatabase("sqlite:///crawlers.db")
        >>> router = setup_crawler_routes(db)
        >>> app.include_router(router)
    
    Note:
        This function must be called during application startup to register
        the routes. The database instance should remain alive for the entire
        application lifecycle.
    """
    
    @router.get("", response_model=List[CrawlerConfigResponse])
    async def get_crawlers(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Items per page"),
        status: Optional[str] = Query(None, description="Filter by status"),
        name: Optional[str] = Query(None, description="Filter by name")
    ):
        """Retrieve paginated list of crawler configurations with optional filtering.
        
        This endpoint provides a paginated view of all crawler configurations in the
        system with support for filtering by status and name. It implements efficient
        pagination to handle large datasets and provides flexible filtering options
        for better user experience.
        
        The endpoint supports both server-side pagination (via database queries) and
        client-side filtering (for status and name). This hybrid approach balances
        performance with flexibility, allowing for efficient data retrieval while
        maintaining responsive filtering capabilities.
        
        Args:
            page (int): Page number for pagination, starting from 1. Must be positive.
            limit (int): Number of items per page, between 1 and 100. Default is 10.
            status (Optional[str]): Filter crawlers by their current status
                (e.g., 'active', 'inactive'). Case-sensitive matching.
            name (Optional[str]): Filter crawlers by name using case-insensitive
                substring matching. Partial matches are supported.
        
        Returns:
            List[CrawlerConfigResponse]: List of crawler configurations matching
                the specified criteria, formatted according to the response model.
        
        Raises:
            HTTPException: 500 status code for database errors or unexpected failures.
        
        Example:
            GET /api/crawlers?page=1&limit=20&status=active&name=news
            Returns active crawlers with 'news' in their name, first 20 results.
        
        Note:
            Filtering is applied after pagination retrieval, which may result in
            fewer items than the specified limit when filters are active.
        """
        try:
            # Log the incoming request for debugging and monitoring purposes
            logger.info(f"Fetching crawlers: page={page}, limit={limit}, status={status}, name={name}")
            
            # Calculate database offset for pagination (zero-based indexing)
            offset = (page - 1) * limit
            
            # Retrieve paginated crawler data from database
            # This performs the primary data fetch with database-level pagination
            crawlers = await url_db.get_crawlers_paginated(offset=offset, limit=limit)
            
            # Apply client-side status filtering if specified
            # Note: This filtering happens after pagination, which may reduce result count
            if status:
                crawlers = [c for c in crawlers if c.get('status') == status]
                logger.debug(f"Applied status filter '{status}', {len(crawlers)} crawlers remaining")
            
            # Apply client-side name filtering with case-insensitive substring matching
            if name:
                crawlers = [c for c in crawlers if name.lower() in c.get('name', '').lower()]
                logger.debug(f"Applied name filter '{name}', {len(crawlers)} crawlers remaining")
            
            logger.info(f"Successfully retrieved {len(crawlers)} crawler configurations")
            return crawlers
            
        except Exception as e:
            # Log the error with full context for debugging
            logger.error(f"Error retrieving crawlers (page={page}, limit={limit}): {e}")
            # Return generic error to client while preserving detailed logs
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/{crawler_id}", response_model=CrawlerConfigResponse)
    async def get_crawler(crawler_id: int):
        """Retrieve a specific crawler configuration by its unique identifier.
        
        This endpoint fetches detailed information about a single crawler configuration
        using its unique database identifier. It provides complete crawler details
        including configuration parameters, current status, and metadata.
        
        The endpoint implements proper error handling for both missing resources
        (404 Not Found) and system errors (500 Internal Server Error), ensuring
        clients receive appropriate HTTP status codes and error messages.
        
        Args:
            crawler_id (int): Unique identifier of the crawler configuration to retrieve.
                Must be a positive integer corresponding to an existing crawler.
        
        Returns:
            CrawlerConfigResponse: Complete crawler configuration data including
                all settings, status information, and metadata.
        
        Raises:
            HTTPException: 
                - 404 status code if the crawler with the specified ID doesn't exist
                - 500 status code for database errors or unexpected failures
        
        Example:
            GET /api/crawlers/123
            Returns the complete configuration for crawler with ID 123.
        
        Note:
            This endpoint is typically used for displaying detailed crawler information
            in administrative interfaces or for retrieving configuration before updates.
        """
        try:
            # Log the request for audit and debugging purposes
            logger.info(f"Retrieving crawler configuration for ID: {crawler_id}")
            
            # Attempt to fetch the crawler from the database
            crawler = await url_db.get_crawler(crawler_id)
            
            # Check if the crawler exists and return appropriate error if not found
            if not crawler:
                logger.warning(f"Crawler with ID {crawler_id} not found")
                raise HTTPException(status_code=404, detail="Crawler not found")
            
            logger.info(f"Successfully retrieved crawler {crawler_id}: {crawler.get('name', 'Unknown')}")
            return crawler
            
        except HTTPException:
            # Re-raise HTTP exceptions (like 404) without modification
            # This preserves the specific error status and message
            raise
        except Exception as e:
            # Log unexpected errors with full context for debugging
            logger.error(f"Unexpected error retrieving crawler {crawler_id}: {e}")
            # Convert to HTTP 500 error for client response
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("", response_model=CrawlerConfigResponse)
    async def create_crawler(crawler: CrawlerConfigCreate):
        """Create a new crawler configuration in the system.
        
        This endpoint accepts a new crawler configuration and persists it to the
        database. It validates the input data using Pydantic models, creates the
        crawler record, and returns the complete configuration including the
        auto-generated ID and any default values.
        
        The endpoint follows the RESTful pattern of returning the created resource
        with a 200 status code. Input validation is handled automatically by
        FastAPI using the Pydantic model, ensuring data integrity before persistence.
        
        Args:
            crawler (CrawlerConfigCreate): Crawler configuration data to create.
                Must include all required fields as defined in the Pydantic model.
                Optional fields will use their default values if not provided.
        
        Returns:
            CrawlerConfigResponse: The complete created crawler configuration
                including the auto-generated ID, timestamps, and any computed fields.
        
        Raises:
            HTTPException: 
                - 422 status code for validation errors (handled by FastAPI)
                - 500 status code for database errors or unexpected failures
        
        Example:
            POST /api/crawlers
            {
                "name": "News Crawler",
                "url_pattern": "https://news.example.com/*",
                "status": "active"
            }
            Returns the created crawler with ID and timestamps.
        
        Note:
            The crawler will be created with default settings for any optional
            fields not specified in the request. The response includes the
            complete configuration for immediate use.
        """
        try:
            # Log the creation request for audit and debugging
            logger.info(f"Creating new crawler configuration: {crawler.name if hasattr(crawler, 'name') else 'Unknown'}")
            
            # Convert Pydantic model to dictionary for database storage
            # This ensures all validation has passed and data is properly formatted
            crawler_data = crawler.dict()
            logger.debug(f"Crawler data prepared for creation: {crawler_data}")
            
            # Create the crawler record in the database and get the new ID
            crawler_id = await url_db.create_crawler(crawler_data)
            logger.info(f"Crawler created successfully with ID: {crawler_id}")
            
            # Retrieve the complete created crawler to return to client
            # This ensures the response includes all computed fields and defaults
            created_crawler = await url_db.get_crawler(crawler_id)
            
            if not created_crawler:
                # This should not happen but provides safety check
                logger.error(f"Failed to retrieve newly created crawler {crawler_id}")
                raise HTTPException(status_code=500, detail="Failed to retrieve created crawler")
            
            logger.info(f"Successfully created and retrieved crawler {crawler_id}")
            return created_crawler
            
        except Exception as e:
            # Log the error with context for debugging
            logger.error(f"Error creating crawler configuration: {e}")
            # Return generic error to client while preserving detailed logs
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.put("/{crawler_id}", response_model=CrawlerConfigResponse)
    async def update_crawler(crawler_id: int, crawler: CrawlerConfigUpdate):
        """Update an existing crawler configuration with partial or complete data.
        
        This endpoint allows modification of an existing crawler configuration using
        a partial update approach. Only fields provided in the request body will be
        updated, while omitted fields retain their current values. This enables
        flexible updates without requiring clients to send complete configurations.
        
        The endpoint implements proper validation by checking for crawler existence
        before attempting updates, ensuring atomic operations and consistent error
        handling. It follows RESTful patterns with appropriate HTTP status codes.
        
        Args:
            crawler_id (int): Unique identifier of the crawler to update.
                Must correspond to an existing crawler configuration.
            crawler (CrawlerConfigUpdate): Partial crawler configuration data.
                Only non-null fields will be updated in the database.
        
        Returns:
            CrawlerConfigResponse: The complete updated crawler configuration
                with all current values including both updated and unchanged fields.
        
        Raises:
            HTTPException:
                - 404 status code if the crawler doesn't exist
                - 422 status code for validation errors (handled by FastAPI)
                - 500 status code for database errors or unexpected failures
        
        Example:
            PUT /api/crawlers/123
            {
                "status": "inactive",
                "name": "Updated News Crawler"
            }
            Updates only the status and name, leaving other fields unchanged.
        
        Note:
            This endpoint uses the HTTP PUT method but implements PATCH semantics
            for partial updates. Null values in the request are ignored rather
            than being set as null in the database.
        """
        try:
            # Log the update request for audit and debugging
            logger.info(f"Updating crawler configuration for ID: {crawler_id}")
            
            # Verify the crawler exists before attempting update
            # This provides early validation and better error messages
            existing_crawler = await url_db.get_crawler(crawler_id)
            if not existing_crawler:
                logger.warning(f"Attempted to update non-existent crawler {crawler_id}")
                raise HTTPException(status_code=404, detail="Crawler not found")
            
            logger.debug(f"Found existing crawler: {existing_crawler.get('name', 'Unknown')}")
            
            # Extract only non-null fields for partial update
            # This implements PATCH semantics within a PUT endpoint
            update_data = {k: v for k, v in crawler.dict().items() if v is not None}
            logger.debug(f"Update data prepared: {update_data}")
            
            # Perform the database update operation
            success = await url_db.update_crawler(crawler_id, update_data)
            if not success:
                # This should not happen given the existence check above
                logger.error(f"Database update failed for crawler {crawler_id}")
                raise HTTPException(status_code=404, detail="Crawler not found")
            
            logger.info(f"Crawler {crawler_id} updated successfully")
            
            # Retrieve and return the complete updated configuration
            # This ensures the client receives all current values
            updated_crawler = await url_db.get_crawler(crawler_id)
            
            if not updated_crawler:
                # Safety check - should not happen but provides robustness
                logger.error(f"Failed to retrieve updated crawler {crawler_id}")
                raise HTTPException(status_code=500, detail="Failed to retrieve updated crawler")
            
            logger.info(f"Successfully updated and retrieved crawler {crawler_id}")
            return updated_crawler
            
        except HTTPException:
            # Re-raise HTTP exceptions (like 404) without modification
            raise
        except Exception as e:
            # Log unexpected errors with full context
            logger.error(f"Unexpected error updating crawler {crawler_id}: {e}")
            # Convert to HTTP 500 error for client response
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/{crawler_id}")
    async def delete_crawler(crawler_id: int):
        """Permanently delete a crawler configuration from the system.
        
        This endpoint removes a crawler configuration and all associated data from
        the database. The operation is irreversible and should be used with caution.
        It implements proper validation to ensure the crawler exists before deletion
        and provides appropriate error handling for various failure scenarios.
        
        The endpoint follows RESTful conventions by returning a success message
        upon successful deletion and appropriate HTTP status codes for different
        error conditions. It includes comprehensive logging for audit trails.
        
        Args:
            crawler_id (int): Unique identifier of the crawler configuration to delete.
                Must correspond to an existing crawler in the database.
        
        Returns:
            dict: Success message confirming the deletion operation.
                Format: {"message": "Crawler deleted successfully"}
        
        Raises:
            HTTPException:
                - 404 status code if the crawler doesn't exist
                - 500 status code for database errors or unexpected failures
        
        Example:
            DELETE /api/crawlers/123
            Returns: {"message": "Crawler deleted successfully"}
        
        Warning:
            This operation is irreversible. All crawler configuration data
            will be permanently lost. Consider implementing soft deletion
            or backup mechanisms for production environments.
        
        Note:
            The endpoint does not check if the crawler is currently active
            or running. Clients should ensure crawlers are stopped before
            deletion to prevent orphaned processes.
        """
        try:
            # Log the deletion request for audit and security purposes
            logger.info(f"Attempting to delete crawler configuration: {crawler_id}")
            
            # Attempt to delete the crawler from the database
            # The database layer handles the actual existence check
            success = await url_db.delete_crawler(crawler_id)
            
            # Check if the deletion was successful
            if not success:
                logger.warning(f"Attempted to delete non-existent crawler {crawler_id}")
                raise HTTPException(status_code=404, detail="Crawler not found")
            
            # Log successful deletion for audit trail
            logger.info(f"Crawler {crawler_id} deleted successfully")
            
            # Return confirmation message to client
            return {"message": "Crawler deleted successfully"}
            
        except HTTPException:
            # Re-raise HTTP exceptions (like 404) without modification
            # This preserves the specific error status and message
            raise
        except Exception as e:
            # Log unexpected errors with full context for debugging
            logger.error(f"Unexpected error deleting crawler {crawler_id}: {e}")
            # Convert to HTTP 500 error for client response
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/{crawler_id}/toggle-status")
    async def toggle_crawler_status(crawler_id: int):
        """Toggle crawler status between active and inactive states.
        
        This endpoint provides a convenient way to switch a crawler's operational
        status without requiring a full update operation. It automatically determines
        the opposite state and applies the change, making it ideal for quick
        enable/disable operations in administrative interfaces.
        
        The endpoint implements atomic status changes by first verifying the
        crawler exists, determining the current status, calculating the new status,
        and then applying the update. This ensures consistent state transitions
        and proper error handling throughout the process.
        
        Args:
            crawler_id (int): Unique identifier of the crawler whose status
                should be toggled. Must correspond to an existing crawler.
        
        Returns:
            dict: Confirmation message indicating the new status.
                Format: {"message": "Crawler status changed to {new_status}"}
        
        Raises:
            HTTPException:
                - 404 status code if the crawler doesn't exist
                - 500 status code for database errors or unexpected failures
        
        Example:
            POST /api/crawlers/123/toggle-status
            If crawler is currently 'active', returns:
            {"message": "Crawler status changed to inactive"}
        
        Note:
            The endpoint assumes only two status values: 'active' and 'inactive'.
            If the current status is anything other than 'active', it will be
            changed to 'active'. This provides a safe default behavior.
        
        Behavior:
            - 'active' → 'inactive'
            - 'inactive' → 'active'
            - null/undefined → 'active'
            - any other value → 'active'
        """
        try:
            # Log the status toggle request for audit and debugging
            logger.info(f"Toggling status for crawler: {crawler_id}")
            
            # Retrieve the current crawler configuration to check existence and status
            crawler = await url_db.get_crawler(crawler_id)
            if not crawler:
                logger.warning(f"Attempted to toggle status of non-existent crawler {crawler_id}")
                raise HTTPException(status_code=404, detail="Crawler not found")
            
            # Determine current status with safe default handling
            current_status = crawler.get('status', 'inactive')
            logger.debug(f"Current status for crawler {crawler_id}: {current_status}")
            
            # Calculate the new status using simple toggle logic
            # Any status other than 'active' becomes 'active'
            new_status = 'inactive' if current_status == 'active' else 'active'
            logger.info(f"Changing crawler {crawler_id} status from '{current_status}' to '{new_status}'")
            
            # Apply the status update to the database
            success = await url_db.update_crawler(crawler_id, {'status': new_status})
            if not success:
                # This should not happen given the existence check above
                logger.error(f"Failed to update status for crawler {crawler_id}")
                raise HTTPException(status_code=404, detail="Crawler not found")
            
            # Log successful status change for audit trail
            logger.info(f"Successfully toggled crawler {crawler_id} status to '{new_status}'")
            
            # Return confirmation message with the new status
            return {"message": f"Crawler status changed to {new_status}"}
            
        except HTTPException:
            # Re-raise HTTP exceptions (like 404) without modification
            raise
        except Exception as e:
            # Log unexpected errors with full context for debugging
            logger.error(f"Unexpected error toggling crawler {crawler_id} status: {e}")
            # Convert to HTTP 500 error for client response
            raise HTTPException(status_code=500, detail=str(e))
    
    return router