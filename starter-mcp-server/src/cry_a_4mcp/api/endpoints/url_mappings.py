"""URL Mapping endpoints for CRY-A-4MCP API.

This module provides RESTful API endpoints for managing technical URL mappings
within the CRY-A-4MCP platform. URL mappings define the technical implementation
details for URL configurations, including extractor assignments, rate limiting,
crawler settings, and validation rules.

Key Features:
    - CRUD operations for technical URL mappings
    - Extractor assignment and configuration
    - Rate limiting and crawler settings management
    - Validation rules configuration
    - Technical configuration management
    - Comprehensive error handling and logging
    - Type-safe request/response models

Endpoints:
    GET /api/url-mappings - List all URL mappings
    GET /api/url-mappings/{id} - Get specific URL mapping
    POST /api/url-mappings - Create new URL mapping
    PUT /api/url-mappings/{id} - Update existing URL mapping
    DELETE /api/url-mappings/{id} - Delete URL mapping

Example:
    ```python
    # Create a new technical URL mapping
    mapping_data = {
        "url_config_id": "config_123",
        "extractor_id": "crypto_price_extractor",
        "rate_limit": 60,
        "config": {
            "max_depth": 2,
            "delay": 1.0
        },
        "validation_rules": {
            "required_fields": ["price", "timestamp"]
        },
        "is_active": True
    }
    ```

Author: CRY-A-4MCP Development Team
Version: 3.0.0
"""

# Standard library imports
import json
import logging
from typing import List, Optional
from datetime import datetime

# FastAPI imports
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, ValidationError

# Internal imports
from ..models_separated import (
    URLMappingBase,
    URLMappingCreate,
    URLMappingUpdate,
    URLMappingResponse
)
from ...storage.url_mappings_db import URLMappingsDatabase
from ...storage.url_configuration_db import URLConfigurationDatabase

# Module-level logger
logger = logging.getLogger(__name__)


def setup_url_mapping_routes(url_mappings_db: URLMappingsDatabase, url_configuration_db: URLConfigurationDatabase) -> APIRouter:
    """Setup URL mapping routes with database dependencies.
    
    This function creates and configures all URL mapping-related endpoints
    with the provided database instances. It implements dependency injection
    pattern to ensure proper database connectivity.
    
    Args:
        url_mappings_db (URLMappingsDatabase): Database instance for URL mapping operations.
            Must be properly initialized and connected.
        url_configuration_db (URLConfigurationDatabase): Database instance for configuration metadata.
            Must be properly initialized and connected.
    
    Returns:
        APIRouter: Configured router with all URL mapping endpoints.
    
    Note:
        This function should be called during application startup to register
        all URL mapping routes with the main FastAPI application.
    
    Example:
        ```python
        mappings_db = URLMappingsDatabase()
        config_db = URLConfigurationDatabase()
        await mappings_db.initialize()
        await config_db.initialize()
        router = setup_url_mapping_routes(mappings_db, config_db)
        app.include_router(router)
        ```
    """
    # Initialize router with prefix and tags for OpenAPI documentation
    router = APIRouter(prefix="/api/url-mappings", tags=["URL Mappings"])
    
    # Dependencies to get database instances
    def get_mappings_db() -> URLMappingsDatabase:
        return url_mappings_db
    
    def get_config_db() -> URLConfigurationDatabase:
        return url_configuration_db
    
    @router.get("/", response_model=List[URLMappingResponse])
    async def list_url_mappings(
        active_only: bool = Query(False, description="Filter to active mappings only"),
        extractor_ids: Optional[str] = Query(None, description="Filter by extractor IDs (comma-separated)"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
        offset: int = Query(0, ge=0, description="Number of results to skip"),
        mappings_db: URLMappingsDatabase = Depends(get_mappings_db)
    ) -> List[URLMappingResponse]:
        """List technical URL mappings with optional filtering.
        
        Retrieves a paginated list of technical URL mappings with optional filtering
        by active status and extractor ID. Supports pagination through
        limit and offset parameters.
        
        Args:
            active_only: If True, only return active mappings
            extractor_id: Filter mappings by specific extractor ID
            limit: Maximum number of mappings to return (1-1000)
            offset: Number of mappings to skip for pagination
            mappings_db: Database dependency injection
            
        Returns:
            List of technical URL mapping objects matching the criteria
            
        Raises:
            HTTPException: If database operation fails
        """
        try:
            logger.info(f"Listing URL mappings - active_only: {active_only}, extractor_ids: {extractor_ids}")
            
            # Get all mappings and apply filters
            all_mappings = await mappings_db.get_all_mappings()
            
            # Apply filters
            filtered_mappings = all_mappings
            if active_only:
                filtered_mappings = [m for m in filtered_mappings if m.get('is_active', True)]
            if extractor_ids:
                extractor_id_list = [eid.strip() for eid in extractor_ids.split(',')]
                filtered_mappings = [
                    m for m in filtered_mappings 
                    if any(eid in m.get('extractor_ids', []) for eid in extractor_id_list)
                ]
            
            # Apply pagination
            paginated_mappings = filtered_mappings[offset:offset + limit]
            
            # Convert to response models
            return [
                URLMappingResponse(
                    id=mapping['id'],
                    name=mapping.get('name'),
                    url_config_id=mapping['url_config_id'],
                    url=mapping.get('url'),
                    extractor_ids=mapping.get('extractor_ids', []),
                    rate_limit=mapping.get('rate_limit'),
                    priority=mapping.get('priority', 1),
                    validation_rules=mapping.get('validation_rules'),
                    crawler_settings=mapping.get('crawler_settings'),
                    is_active=mapping.get('is_active', True),
                    metadata=mapping.get('metadata'),
                    created_at=mapping['created_at'],
                    updated_at=mapping.get('updated_at')
                )
                for mapping in paginated_mappings
            ]
            
        except Exception as e:
            logger.error(f"Failed to list URL mappings: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to retrieve URL mappings: {str(e)}")
    
    @router.get("/{mapping_id}", response_model=URLMappingResponse)
    async def get_url_mapping(
        mapping_id: str,
        mappings_db: URLMappingsDatabase = Depends(get_mappings_db)
    ):
        """Get a specific URL mapping by ID.
        
        Args:
            mapping_id: The unique identifier of the URL mapping
            
        Returns:
            The URL mapping with the specified ID
            
        Raises:
            HTTPException: If mapping not found or database operation fails
        """
        try:
            logger.info(f"Retrieving URL mapping with ID: {mapping_id}")
            
            mapping = await mappings_db.get_mapping(mapping_id)
            if not mapping:
                raise HTTPException(status_code=404, detail=f"URL mapping {mapping_id} not found")
            
            return URLMappingResponse(
                id=mapping['id'],
                name=mapping.get('name'),
                url_config_id=mapping['url_config_id'],
                url=mapping.get('url'),
                extractor_ids=mapping.get('extractor_ids', []),
                rate_limit=mapping.get('rate_limit'),
                priority=mapping.get('priority', 1),
                validation_rules=mapping.get('validation_rules'),
                crawler_settings=mapping.get('crawler_settings'),
                is_active=mapping.get('is_active', True),
                tags=mapping.get('tags', []),
                notes=mapping.get('notes'),
                category=mapping.get('category'),
                metadata=mapping.get('metadata'),
                created_at=mapping['created_at'],
                updated_at=mapping.get('updated_at')
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get URL mapping {mapping_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to retrieve URL mapping: {str(e)}")
    
    @router.post("/", response_model=URLMappingResponse)
    async def create_url_mapping(
        mapping: URLMappingCreate,
        mappings_db: URLMappingsDatabase = Depends(get_mappings_db),
        config_db: URLConfigurationDatabase = Depends(get_config_db)
    ):
        """Create a new URL mapping.
        
        Args:
            mapping: The URL mapping data to create
            
        Returns:
            The created URL mapping with assigned ID
            
        Raises:
            HTTPException: If creation fails or validation errors occur
        """
        try:
            # DETAILED LOGGING FOR DEBUGGING 422 ERRORS
            logger.info(f"=== URL MAPPING CREATION DEBUG ===")
            logger.info(f"Raw mapping object: {mapping}")
            logger.info(f"Mapping dict: {mapping.dict()}")
            logger.info(f"URL config ID: {mapping.url_config_id} (type: {type(mapping.url_config_id)})")
            logger.info(f"Extractor IDs: {mapping.extractor_ids} (type: {type(mapping.extractor_ids)})")
            logger.info(f"Rate limit: {mapping.rate_limit} (type: {type(mapping.rate_limit)})")
            logger.info(f"Priority: {mapping.priority} (type: {type(mapping.priority)})")
            logger.info(f"Is active: {mapping.is_active} (type: {type(mapping.is_active)})")
            logger.info(f"=== END DEBUG INFO ===")
            
            logger.info(f"Creating new URL mapping for config: {mapping.url_config_id}")
            
            # Retrieve the actual URL from the configuration service
            config_data = await config_db.get_configuration(mapping.url_config_id)
            if not config_data:
                raise HTTPException(
                    status_code=404, 
                    detail=f"URL configuration {mapping.url_config_id} not found"
                )
            
            actual_url = config_data.get('url')
            if not actual_url:
                raise HTTPException(
                    status_code=400, 
                    detail=f"URL configuration {mapping.url_config_id} does not have a valid URL"
                )
            
            # Create the mapping with only supported parameters
            # Parse JSON strings if they exist
            validation_rules = None
            if mapping.validation_rules:
                try:
                    validation_rules = json.loads(mapping.validation_rules) if isinstance(mapping.validation_rules, str) else mapping.validation_rules
                except (json.JSONDecodeError, TypeError):
                    validation_rules = {}
            
            crawler_settings = None
            if mapping.crawler_settings:
                try:
                    crawler_settings = json.loads(mapping.crawler_settings) if isinstance(mapping.crawler_settings, str) else mapping.crawler_settings
                except (json.JSONDecodeError, TypeError):
                    crawler_settings = {}
            
            # Prepare metadata with additional fields
            metadata_dict = {}
            if mapping.metadata:
                try:
                    metadata_dict = json.loads(mapping.metadata) if isinstance(mapping.metadata, str) else mapping.metadata
                except (json.JSONDecodeError, TypeError):
                    metadata_dict = {}
            
            # Add unsupported fields to metadata
            if mapping.name:
                metadata_dict['name'] = mapping.name
            if mapping.tags:
                metadata_dict['tags'] = mapping.tags
            if mapping.notes:
                metadata_dict['notes'] = mapping.notes
            if mapping.category:
                metadata_dict['category'] = mapping.category
            
            mapping_id = await mappings_db.create_mapping(
                url_config_id=mapping.url_config_id,
                url=actual_url,
                extractor_ids=mapping.extractor_ids,
                rate_limit=mapping.rate_limit,
                priority=mapping.priority,
                validation_rules=validation_rules,
                crawler_settings=crawler_settings,
                is_active=mapping.is_active,
                metadata=metadata_dict
            )
            
            # Get the created mapping
            created_mapping = await mappings_db.get_mapping(mapping_id)
            if not created_mapping:
                raise HTTPException(status_code=500, detail="Failed to retrieve created mapping")
            
            logger.info(f"Created URL mapping with ID: {mapping_id}")
            return URLMappingResponse(
                id=created_mapping['id'],
                name=created_mapping.get('name'),
                url_config_id=created_mapping['url_config_id'],
                url=created_mapping.get('url'),
                extractor_ids=created_mapping.get('extractor_ids', []),
                rate_limit=created_mapping.get('rate_limit'),
                priority=created_mapping.get('priority', 1),
                validation_rules=created_mapping.get('validation_rules'),
                crawler_settings=created_mapping.get('crawler_settings'),
                is_active=created_mapping.get('is_active', True),
                tags=created_mapping.get('tags', []),
                notes=created_mapping.get('notes'),
                category=created_mapping.get('category'),
                metadata=created_mapping.get('metadata'),
                created_at=created_mapping['created_at'],
                updated_at=created_mapping.get('updated_at')
            )
            
        except ValidationError as e:
            logger.error(f"=== VALIDATION ERROR DEBUG ===")
            logger.error(f"Validation error details: {e}")
            logger.error(f"Error dict: {e.errors()}")
            logger.error(f"=== END VALIDATION ERROR ===")
            raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
        except Exception as e:
            logger.error(f"Failed to create URL mapping: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create URL mapping: {str(e)}")
    
    @router.put("/{mapping_id}", response_model=URLMappingResponse)
    async def update_url_mapping(
        mapping_id: str,
        mapping: URLMappingUpdate,
        mappings_db: URLMappingsDatabase = Depends(get_mappings_db)
    ):
        """Update an existing URL mapping.
        
        Args:
            mapping_id: The unique identifier of the URL mapping to update
            mapping: The updated URL mapping data
            
        Returns:
            The updated URL mapping
            
        Raises:
            HTTPException: If mapping not found or update fails
        """
        try:
            logger.info(f"Updating URL mapping {mapping_id}")
            
            # Check if mapping exists
            existing_mapping = await mappings_db.get_mapping(mapping_id)
            if not existing_mapping:
                raise HTTPException(status_code=404, detail=f"URL mapping {mapping_id} not found")
            
            # Prepare update data
            update_data = {}
            if mapping.name is not None:
                update_data['name'] = mapping.name
            if mapping.extractor_ids is not None:
                update_data['extractor_ids'] = mapping.extractor_ids
            if mapping.rate_limit is not None:
                update_data['rate_limit'] = mapping.rate_limit
            if mapping.priority is not None:
                update_data['priority'] = mapping.priority
            if mapping.validation_rules is not None:
                update_data['validation_rules'] = mapping.validation_rules
            if mapping.crawler_settings is not None:
                update_data['crawler_settings'] = mapping.crawler_settings
            if mapping.is_active is not None:
                update_data['is_active'] = mapping.is_active
            if mapping.tags is not None:
                update_data['tags'] = mapping.tags
            if mapping.notes is not None:
                update_data['notes'] = mapping.notes
            if mapping.category is not None:
                update_data['category'] = mapping.category
            
            # Update the mapping
            update_success = await mappings_db.update_mapping(mapping_id, **update_data)
            
            if not update_success:
                raise HTTPException(status_code=500, detail="Failed to update URL mapping")
            
            # Get the updated mapping
            updated_mapping = await mappings_db.get_mapping(mapping_id)
            if not updated_mapping:
                raise HTTPException(status_code=500, detail="Failed to retrieve updated mapping")
            
            logger.info(f"Updated URL mapping: {mapping_id}")
            return URLMappingResponse(
                id=updated_mapping['id'],
                name=updated_mapping.get('name'),
                url_config_id=updated_mapping['url_config_id'],
                url=updated_mapping.get('url'),
                extractor_ids=updated_mapping.get('extractor_ids', []),
                rate_limit=updated_mapping.get('rate_limit'),
                priority=updated_mapping.get('priority', 1),
                validation_rules=updated_mapping.get('validation_rules'),
                crawler_settings=updated_mapping.get('crawler_settings'),
                is_active=updated_mapping.get('is_active', True),
                tags=updated_mapping.get('tags', []),
                notes=updated_mapping.get('notes'),
                category=updated_mapping.get('category'),
                metadata=updated_mapping.get('metadata'),
                created_at=updated_mapping['created_at'],
                updated_at=updated_mapping.get('updated_at')
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update URL mapping {mapping_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to update URL mapping: {str(e)}")
    
    @router.delete("/{mapping_id}")
    async def delete_url_mapping(
        mapping_id: str,
        mappings_db: URLMappingsDatabase = Depends(get_mappings_db)
    ):
        """Delete a URL mapping.
        
        Args:
            mapping_id: The unique identifier of the URL mapping to delete
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If mapping not found or deletion fails
        """
        try:
            logger.info(f"Deleting URL mapping {mapping_id}")
            
            # Check if mapping exists
            existing_mapping = await mappings_db.get_mapping(mapping_id)
            if not existing_mapping:
                raise HTTPException(status_code=404, detail=f"URL mapping {mapping_id} not found")
            
            # Delete the mapping
            await mappings_db.delete_mapping(mapping_id)
            
            logger.info(f"Deleted URL mapping: {mapping_id}")
            return {"message": f"URL mapping {mapping_id} deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete URL mapping {mapping_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to delete URL mapping: {str(e)}")
    
    return router