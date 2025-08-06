"""URL Configuration endpoints for CRY-A-4MCP API.

This module provides RESTful API endpoints for managing business-focused URL configurations
within the CRY-A-4MCP platform. URL configurations define the business metadata and
requirements for content sources, focusing on business value, compliance, and strategic
priority rather than technical implementation details.

Key Features:
    - CRUD operations for business-focused URL configurations
    - Filtering by profile type, category, and business priority
    - Business value assessment and compliance tracking
    - Strategic recommendation management
    - Comprehensive error handling and logging
    - Type-safe request/response models

Endpoints:
    GET /api/url-configurations - List all URL configurations with optional filtering
    GET /api/url-configurations/{id} - Get specific URL configuration
    POST /api/url-configurations - Create new URL configuration
    PUT /api/url-configurations/{id} - Update existing URL configuration
    DELETE /api/url-configurations/{id} - Delete URL configuration
    POST /api/url-configurations/initialize - Load predefined URLs
    GET /api/url-configurations/search - Search configurations by pattern

Example:
    ```python
    # Create a new business-focused URL configuration
    config_data = {
        "name": "CoinDesk News Configuration",
        "url": "https://www.coindesk.com/news",
        "profile_type": "news",
        "category": "cryptocurrency",
        "business_priority": 8,
        "business_value": "High-quality crypto news for market analysis",
        "compliance_notes": "Public content, no special compliance requirements",
        "is_active": true
    }
    response = await client.post("/api/url-configurations", json=config_data)
    ```

Author: CRY-A-4MCP Development Team
Version: 3.0.0
"""

# Standard library imports
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Third-party imports
from fastapi import APIRouter, HTTPException, Query

# Local imports
from ...storage.url_configuration_db import URLConfigurationDatabase
from ..models import (
    URLConfigurationBase,
    URLConfigurationCreate,
    URLConfigurationUpdate,
    URLConfigurationResponse
)# Configure logging for this module
logger = logging.getLogger(__name__)


def _convert_db_to_response(db_config: Dict[str, Any]) -> URLConfigurationResponse:
    """Convert database record to URLConfigurationResponse model.
    
    Args:
        db_config: Database record dictionary
        
    Returns:
        URLConfigurationResponse: Pydantic response model
    """
    # Parse JSON fields safely
    key_data_points = db_config.get('key_data_points', [])
    if isinstance(key_data_points, str):
        try:
            import json
            key_data_points = json.loads(key_data_points)
        except (json.JSONDecodeError, TypeError):
            key_data_points = []
    
    target_data = db_config.get('target_data', {})
    if isinstance(target_data, str):
        try:
            import json
            target_data = json.loads(target_data)
        except (json.JSONDecodeError, TypeError):
            target_data = {}
    
    cost_analysis = db_config.get('cost_analysis', {})
    if isinstance(cost_analysis, str):
        try:
            import json
            cost_analysis = json.loads(cost_analysis)
        except (json.JSONDecodeError, TypeError):
            cost_analysis = {}
    
    metadata = db_config.get('metadata', {})
    if isinstance(metadata, str):
        try:
            import json
            metadata = json.loads(metadata)
        except (json.JSONDecodeError, TypeError):
            metadata = {}
    
    # Parse datetime fields
    created_at = db_config.get('created_at')
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            created_at = datetime.now()
    elif not isinstance(created_at, datetime):
        created_at = datetime.now()
    
    updated_at = db_config.get('updated_at')
    if isinstance(updated_at, str):
        try:
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            updated_at = datetime.now()
    elif not isinstance(updated_at, datetime):
        updated_at = datetime.now()
    
    return URLConfigurationResponse(
        id=db_config['id'],
        name=db_config.get('name', ''),
        url=db_config.get('url', ''),
        profile_type=db_config.get('profile_type', ''),
        category=db_config.get('category', ''),
        description=db_config.get('description'),
        business_priority=db_config.get('business_priority', 5),
        business_value=db_config.get('business_value'),
        compliance_notes=db_config.get('compliance_notes'),
        scraping_difficulty=db_config.get('scraping_difficulty', 5),
        has_official_api=db_config.get('has_official_api', False),
        api_pricing=db_config.get('api_pricing'),
        recommendation=db_config.get('recommendation', 'Medium'),
        key_data_points=key_data_points,
        target_data=target_data,
        rationale=db_config.get('rationale', ''),
        cost_analysis=cost_analysis,
        is_active=db_config.get('is_active', True),
        metadata=metadata,
        created_at=created_at,
        updated_at=updated_at
    )


def setup_url_configuration_routes(url_db: URLConfigurationDatabase):
    """Setup URL configuration routes with database dependency.
    
    This function creates and configures all URL configuration-related endpoints
    with the provided database instance. It implements dependency injection
    pattern to ensure proper database connectivity.
    
    Args:
        url_db (URLConfigurationDatabase): Database instance for URL configuration operations.
            Must be properly initialized and connected.
    
    Returns:
        APIRouter: Configured router with all URL configuration endpoints.
    
    Note:
        This function should be called during application startup to register
        all URL configuration routes with the main FastAPI application.
    
    Example:
        ```python
        url_db = URLConfigurationDatabase()
        await url_db.initialize()
        router = setup_url_configuration_routes(url_db)
        app.include_router(router)
        ```
    """
    # Initialize router with prefix and tags for OpenAPI documentation
    router = APIRouter(prefix="/api/url-configurations", tags=["URL Configurations"])
    
    @router.get("/", response_model=List[URLConfigurationResponse])
    async def list_url_configurations(
        profile_type: Optional[str] = Query(None, description="Filter by profile type"),
        category: Optional[str] = Query(None, description="Filter by category"),
        is_active: Optional[bool] = Query(None, description="Filter by active status"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
        offset: int = Query(0, ge=0, description="Number of results to skip")
    ):
        """List all URL configurations with optional filtering.
        
        Returns a paginated list of URL configurations with optional filtering
        by profile type, category, and active status.
        
        Args:
            profile_type: Optional filter by profile type (e.g., 'news', 'social')
            category: Optional filter by category (e.g., 'cryptocurrency')
            is_active: Optional filter by active status
            limit: Maximum number of results to return (1-1000)
            offset: Number of results to skip for pagination
            
        Returns:
            List[URLConfigurationResponse]: List of URL configurations
            
        Raises:
            HTTPException: If database operation fails
        """
        try:
            logger.info(f"Listing URL configurations with filters: profile_type={profile_type}, category={category}, is_active={is_active}")
            
            # Build filter conditions
            filters = {}
            if profile_type is not None:
                filters['profile_type'] = profile_type
            if category is not None:
                filters['category'] = category
            if is_active is not None:
                filters['is_active'] = is_active
            
            # Get configurations from database
            if filters:
                # For now, use get_all_configurations and filter in memory
                # TODO: Implement proper filtering in database layer
                db_configs = await url_db.get_all_configurations(active_only=filters.get('is_active', False))
                
                # Apply additional filters
                if 'profile_type' in filters:
                    db_configs = [c for c in db_configs if c.get('profile_type') == filters['profile_type']]
                if 'category' in filters:
                    db_configs = [c for c in db_configs if c.get('category') == filters['category']]
                
                # Apply pagination
                db_configs = db_configs[offset:offset + limit]
            else:
                db_configs = await url_db.get_all_configurations(active_only=True)
            
            # Convert to response models
            configurations = [_convert_db_to_response(config) for config in db_configs]
            
            logger.info(f"Successfully retrieved {len(configurations)} URL configurations")
            return configurations
            
        except Exception as e:
            logger.error(f"Failed to list URL configurations: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve URL configurations: {str(e)}")
    
    @router.get("/{config_id}", response_model=URLConfigurationResponse)
    async def get_url_configuration(config_id: str):
        """Get a specific URL configuration by ID.
        
        Args:
            config_id: Unique identifier of the URL configuration
            
        Returns:
            URLConfigurationResponse: The requested URL configuration
            
        Raises:
            HTTPException: If configuration not found or database operation fails
        """
        try:
            logger.info(f"Retrieving URL configuration: {config_id}")
            
            db_config = await url_db.get_configuration(config_id)
            if not db_config:
                logger.warning(f"URL configuration not found: {config_id}")
                raise HTTPException(status_code=404, detail=f"URL configuration {config_id} not found")
            
            configuration = _convert_db_to_response(db_config)
            logger.info(f"Successfully retrieved URL configuration: {config_id}")
            return configuration
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get URL configuration {config_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve URL configuration: {str(e)}")
    
    @router.post("/", response_model=URLConfigurationResponse, status_code=201)
    async def create_url_configuration(config: URLConfigurationCreate):
        """Create a new URL configuration.
        
        Args:
            config: URL configuration data to create
            
        Returns:
            URLConfigurationResponse: The created URL configuration
            
        Raises:
            HTTPException: If creation fails or validation errors occur
        """
        try:
            logger.info(f"Creating new URL configuration: {config.name}")
            
            # Convert Pydantic model to dict for database
            config_data = config.model_dump()
            
            # Create configuration in database
            config_id = await url_db.create_configuration(**config_data)
            
            # Retrieve the created configuration
            db_config = await url_db.get_configuration(config_id)
            if not db_config:
                raise HTTPException(status_code=500, detail="Failed to retrieve created configuration")
            
            configuration = _convert_db_to_response(db_config)
            logger.info(f"Successfully created URL configuration: {config_id}")
            return configuration
            
        except Exception as e:
            logger.error(f"Failed to create URL configuration: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create URL configuration: {str(e)}")
    
    @router.put("/{config_id}", response_model=URLConfigurationResponse)
    async def update_url_configuration(config_id: str, config: URLConfigurationUpdate):
        """Update an existing URL configuration.
        
        Args:
            config_id: Unique identifier of the URL configuration to update
            config: Updated URL configuration data
            
        Returns:
            URLConfigurationResponse: The updated URL configuration
            
        Raises:
            HTTPException: If configuration not found or update fails
        """
        try:
            logger.info(f"Updating URL configuration: {config_id}")
            
            # Check if configuration exists
            existing_config = await url_db.get_configuration(config_id)
            if not existing_config:
                logger.warning(f"URL configuration not found for update: {config_id}")
                raise HTTPException(status_code=404, detail=f"URL configuration {config_id} not found")
            
            # Convert Pydantic model to dict, excluding None values
            update_data = config.model_dump(exclude_none=True)
            
            # Update configuration in database
            success = await url_db.update_configuration(config_id, **update_data)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update configuration")
            
            # Retrieve the updated configuration
            db_config = await url_db.get_configuration(config_id)
            if not db_config:
                raise HTTPException(status_code=500, detail="Failed to retrieve updated configuration")
            
            configuration = _convert_db_to_response(db_config)
            logger.info(f"Successfully updated URL configuration: {config_id}")
            return configuration
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update URL configuration {config_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update URL configuration: {str(e)}")
    
    @router.delete("/{config_id}", status_code=204)
    async def delete_url_configuration(config_id: str):
        """Delete a URL configuration.
        
        Args:
            config_id: Unique identifier of the URL configuration to delete
            
        Raises:
            HTTPException: If configuration not found or deletion fails
        """
        try:
            logger.info(f"Deleting URL configuration: {config_id}")
            
            # Check if configuration exists
            existing_config = await url_db.get_configuration(config_id)
            if not existing_config:
                logger.warning(f"URL configuration not found for deletion: {config_id}")
                raise HTTPException(status_code=404, detail=f"URL configuration {config_id} not found")
            
            # Delete configuration from database
            success = await url_db.delete_configuration(config_id)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to delete configuration")
            
            logger.info(f"Successfully deleted URL configuration: {config_id}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete URL configuration {config_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete URL configuration: {str(e)}")
    
    @router.get("/search/", response_model=List[URLConfigurationResponse])
    async def search_url_configurations(
        query: str = Query(..., description="Search query for URL patterns or names"),
        limit: int = Query(50, ge=1, le=500, description="Maximum number of results")
    ):
        """Search URL configurations by pattern or name.
        
        Args:
            query: Search query to match against URL patterns, names, or descriptions
            limit: Maximum number of results to return
            
        Returns:
            List[URLConfigurationResponse]: List of matching URL configurations
            
        Raises:
            HTTPException: If search operation fails
        """
        try:
            logger.info(f"Searching URL configurations with query: {query}")
            
            # Search configurations in database
            db_configs = await url_db.search_configurations(query, limit=limit)
            
            # Convert to response models
            configurations = [_convert_db_to_response(config) for config in db_configs]
            
            logger.info(f"Search returned {len(configurations)} URL configurations")
            return configurations
            
        except Exception as e:
            logger.error(f"Failed to search URL configurations: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to search URL configurations: {str(e)}")
    
    @router.post("/initialize", status_code=201)
    async def initialize_predefined_configurations():
        """Initialize the database with predefined URL configurations.
        
        This endpoint loads a set of predefined URL configurations for common
        cryptocurrency and financial data sources. Useful for initial setup.
        
        Returns:
            Dict: Summary of initialization results
            
        Raises:
            HTTPException: If initialization fails
        """
        try:
            logger.info("Initializing predefined URL configurations")
            
            # Define predefined configurations
            predefined_configs = [
                {
                    "name": "CoinDesk News",
                    "url": "https://www.coindesk.com/news",
                    "url_patterns": ["https://www.coindesk.com/news/*"],
                    "profile_type": "news",
                    "category": "cryptocurrency",
                    "description": "Leading cryptocurrency news and analysis",
                    "priority": 9,
                    "scraping_difficulty": 6,
                    "has_official_api": False,
                    "recommendation": "High",
                    "key_data_points": ["title", "content", "publish_date", "author"],
                    "target_data": {"articles": "news_content", "sentiment": "market_sentiment"},
                    "rationale": "Premier source for cryptocurrency news and market analysis",
                    "cost_analysis": {"requests_per_day": 100, "bandwidth_mb": 50},
                    "extractor_ids": ["crypto_news_extractor"],
                    "is_active": True
                },
                {
                    "name": "CoinGecko API",
                    "url": "https://api.coingecko.com/api/v3",
                    "url_patterns": ["https://api.coingecko.com/api/v3/*"],
                    "profile_type": "market_data",
                    "category": "cryptocurrency",
                    "description": "Comprehensive cryptocurrency market data API",
                    "priority": 10,
                    "scraping_difficulty": 2,
                    "has_official_api": True,
                    "api_pricing": "Free tier available, paid plans from $129/month",
                    "recommendation": "Very High",
                    "key_data_points": ["price", "market_cap", "volume", "price_change"],
                    "target_data": {"prices": "real_time_data", "market_data": "historical_data"},
                    "rationale": "Most comprehensive and reliable crypto market data source",
                    "cost_analysis": {"api_calls_per_day": 1000, "cost_per_month": 0},
                    "extractor_ids": ["coingecko_api_extractor"],
                    "rate_limit": 50,
                    "is_active": True
                },
                {
                    "name": "CryptoCompare",
                    "url": "https://www.cryptocompare.com",
                    "url_patterns": ["https://www.cryptocompare.com/*"],
                    "profile_type": "market_data",
                    "category": "cryptocurrency",
                    "description": "Cryptocurrency market data and news platform",
                    "priority": 8,
                    "scraping_difficulty": 7,
                    "has_official_api": True,
                    "api_pricing": "Free tier with limits, paid plans available",
                    "recommendation": "High",
                    "key_data_points": ["price", "volume", "market_cap", "news"],
                    "target_data": {"market_data": "price_volume", "news": "market_news"},
                    "rationale": "Reliable source for both market data and cryptocurrency news",
                    "cost_analysis": {"requests_per_day": 200, "api_cost_monthly": 50},
                    "extractor_ids": ["cryptocompare_extractor"],
                    "is_active": True
                }
            ]
            
            created_count = 0
            errors = []
            
            for config_data in predefined_configs:
                try:
                    config_id = await url_db.create_configuration(**config_data)
                    created_count += 1
                    logger.info(f"Created predefined configuration: {config_data['name']} ({config_id})")
                except Exception as e:
                    error_msg = f"Failed to create {config_data['name']}: {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
            
            result = {
                "message": "Predefined URL configurations initialization completed",
                "created_count": created_count,
                "total_attempted": len(predefined_configs),
                "errors": errors
            }
            
            logger.info(f"Initialization completed: {created_count}/{len(predefined_configs)} configurations created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to initialize predefined configurations: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize configurations: {str(e)}")
    
    return router