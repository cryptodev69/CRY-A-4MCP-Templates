"""FastAPI router for URL mapping endpoints.

This module implements RESTful API endpoints for URL mapping management,
including CRUD operations, filtering, pagination, and statistics.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.url_mapping_service import URLMappingService
from ..models.url_mappings import (
    URLMappingCreate, URLMappingUpdate, URLMappingResponse, 
    URLMappingListResponse, URLMappingStats
)
from ..exceptions import (
    URLMappingNotFoundError, URLMappingValidationError,
    URLMappingDuplicateError, DatabaseError
)


router = APIRouter(prefix="/api/url-mappings", tags=["URL Mappings"])


def get_url_mapping_service(db: Session = Depends(get_db)) -> URLMappingService:
    """Dependency to get URL mapping service."""
    return URLMappingService(db)


@router.get(
    "/",
    response_model=URLMappingListResponse,
    summary="List URL mappings",
    description="Retrieve a paginated list of URL mappings with optional filtering"
)
async def list_url_mappings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    url_config_id: Optional[int] = Query(None, ge=1, description="Filter by URL config ID"),
    extractor_id: Optional[int] = Query(None, ge=1, description="Filter by extractor ID"),
    search: Optional[str] = Query(None, description="Search in name and notes"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    service: URLMappingService = Depends(get_url_mapping_service)
):
    """List URL mappings with filtering and pagination."""
    try:
        return service.list_url_mappings(
            skip=skip,
            limit=limit,
            is_active=is_active,
            category=category,
            url_config_id=url_config_id,
            extractor_id=extractor_id,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list URL mappings: {str(e)}"
        )


@router.post(
    "/",
    response_model=URLMappingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create URL mapping",
    description="Create a new URL mapping with multiple extractors"
)
async def create_url_mapping(
    mapping_data: URLMappingCreate,
    service: URLMappingService = Depends(get_url_mapping_service)
):
    """Create a new URL mapping."""
    try:
        print(f"🔍 CREATE URL MAPPING - Received data: {mapping_data.dict()}")
        print(f"🔍 Field validation:")
        print(f"  - name: {mapping_data.name} (type: {type(mapping_data.name)})")
        print(f"  - url_config_id: {mapping_data.url_config_id} (type: {type(mapping_data.url_config_id)})")
        print(f"  - extractor_ids: {mapping_data.extractor_ids} (type: {type(mapping_data.extractor_ids)})")
        print(f"  - rate_limit: {mapping_data.rate_limit} (type: {type(mapping_data.rate_limit)})")
        print(f"  - priority: {mapping_data.priority} (type: {type(mapping_data.priority)})")
        print(f"  - is_active: {mapping_data.is_active} (type: {type(mapping_data.is_active)})")
        
        result = service.create_url_mapping(mapping_data)
        print(f"🔍 CREATE URL MAPPING - Success: {result.dict()}")
        return result
    except URLMappingDuplicateError as e:
        print(f"❌ CREATE URL MAPPING - Duplicate error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except URLMappingValidationError as e:
        print(f"❌ CREATE URL MAPPING - Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except DatabaseError as e:
        print(f"❌ CREATE URL MAPPING - Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ CREATE URL MAPPING - Unexpected error: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/{mapping_id}",
    response_model=URLMappingResponse,
    summary="Get URL mapping",
    description="Retrieve a specific URL mapping by ID"
)
async def get_url_mapping(
    mapping_id: int,
    service: URLMappingService = Depends(get_url_mapping_service)
):
    """Get URL mapping by ID."""
    try:
        return service.get_url_mapping(mapping_id)
    except URLMappingNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{mapping_id}",
    response_model=URLMappingResponse,
    summary="Update URL mapping",
    description="Update an existing URL mapping"
)
async def update_url_mapping(
    mapping_id: int,
    mapping_data: URLMappingUpdate,
    service: URLMappingService = Depends(get_url_mapping_service)
):
    """Update URL mapping."""
    try:
        return service.update_url_mapping(mapping_id, mapping_data)
    except URLMappingNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except URLMappingDuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except URLMappingValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{mapping_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete URL mapping",
    description="Delete a URL mapping and all its extractor associations"
)
async def delete_url_mapping(
    mapping_id: int,
    service: URLMappingService = Depends(get_url_mapping_service)
):
    """Delete URL mapping."""
    try:
        service.delete_url_mapping(mapping_id)
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
    except URLMappingNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/stats/overview",
    response_model=URLMappingStats,
    summary="Get URL mapping statistics",
    description="Retrieve statistics about URL mappings"
)
async def get_url_mapping_stats(
    service: URLMappingService = Depends(get_url_mapping_service)
):
    """Get URL mapping statistics."""
    try:
        return service.get_url_mapping_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get(
    "/by-extractor/{extractor_id}",
    response_model=List[URLMappingResponse],
    summary="Get mappings by extractor",
    description="Retrieve all URL mappings that use a specific extractor"
)
async def get_mappings_by_extractor(
    extractor_id: int,
    service: URLMappingService = Depends(get_url_mapping_service)
):
    """Get mappings by extractor ID."""
    try:
        return service.get_mappings_by_extractor(extractor_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mappings by extractor: {str(e)}"
        )


@router.get(
    "/by-url-config/{url_config_id}",
    response_model=List[URLMappingResponse],
    summary="Get mappings by URL config",
    description="Retrieve all URL mappings for a specific URL configuration"
)
async def get_mappings_by_url_config(
    url_config_id: int,
    service: URLMappingService = Depends(get_url_mapping_service)
):
    """Get mappings by URL config ID."""
    try:
        return service.get_mappings_by_url_config(url_config_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mappings by URL config: {str(e)}"
        )


@router.patch(
    "/bulk-status",
    response_model=List[URLMappingResponse],
    summary="Bulk update status",
    description="Update the active status of multiple URL mappings"
)
async def bulk_update_status(
    mapping_ids: List[int],
    is_active: bool,
    service: URLMappingService = Depends(get_url_mapping_service)
):
    """Bulk update the active status of URL mappings."""
    try:
        if not mapping_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one mapping ID must be provided"
            )
        
        if len(mapping_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update more than 100 mappings at once"
            )
        
        return service.bulk_update_status(mapping_ids, is_active)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update status: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the URL mapping service is healthy"
)
async def health_check(
    service: URLMappingService = Depends(get_url_mapping_service)
):
    """Health check endpoint."""
    try:
        # Try to perform a simple database operation
        stats = service.get_url_mapping_stats()
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "total_mappings": stats.total_mappings
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


# Note: Exception handlers are defined in main.py for the FastAPI app
# APIRouter doesn't support exception_handler decorator