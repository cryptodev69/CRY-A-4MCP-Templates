"""URL Mapping Service implementation.

This module provides the core business logic for managing URL mappings,
following the separated models architecture where URL configurations handle
business concerns and URL mappings handle technical concerns.

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import get_database_manager
from .exceptions import (
    DatabaseError,
    URLMappingDuplicateError,
    URLMappingNotFoundError,
    URLMappingValidationError,
)
from .models import (
    URLConfiguration,
    URLMapping,
    URLMappingCreate,
    URLMappingListResponse,
    URLMappingResponse,
    URLMappingStats,
    URLMappingUpdate,
    BulkStatusUpdate,
    BulkStatusUpdateResponse,
    URLMappingStatus,
    HealthCheckResponse,
)

# Configure logging
logger = logging.getLogger(__name__)


class URLMappingService:
    """Service class for managing URL mappings.
    
    This service handles the technical aspects of URL mappings,
    including CRUD operations, validation, and database interactions.
    """
    
    def __init__(self, session: Optional[Session] = None):
        """Initialize the URL mapping service.
        
        Args:
            session: Optional SQLAlchemy session. If not provided,
                    a new session will be created for each operation.
        """
        self._session = session
    

    def create_mapping(self, mapping_data: URLMappingCreate) -> URLMappingResponse:
        """Create a new URL mapping.
        
        Args:
            mapping_data: URL mapping creation data.
            
        Returns:
            Created URL mapping response.
            
        Raises:
            URLMappingValidationError: If validation fails.
            URLMappingDuplicateError: If mapping already exists.
            DatabaseError: If database operation fails.
        """
        db_manager = get_database_manager()
        
        try:
            with db_manager.get_session() as session:
                # Validate that the URL configuration exists
                url_config = session.query(URLConfiguration).filter(
                    URLConfiguration.id == mapping_data.url_config_id
                ).first()
            
                if not url_config:
                    raise URLMappingValidationError(
                        f"URL configuration with ID {mapping_data.url_config_id} not found"
                    )
                
                # Check for duplicate mapping (same url_config_id + extractor_id)
                existing = session.query(URLMapping).filter(
                    and_(
                        URLMapping.url_config_id == mapping_data.url_config_id,
                        URLMapping.extractor_id == mapping_data.extractor_id
                    )
                ).first()
                
                if existing:
                    raise URLMappingDuplicateError(
                        f"URL mapping already exists for configuration {mapping_data.url_config_id} "
                        f"with extractor {mapping_data.extractor_id}"
                    )
                
                # Create new mapping
                mapping = URLMapping(
                    url_config_id=mapping_data.url_config_id,
                    extractor_id=mapping_data.extractor_id,
                    rate_limit=mapping_data.rate_limit,
                    crawler_settings=mapping_data.crawler_settings,
                    validation_rules=mapping_data.validation_rules,
                    is_active=mapping_data.is_active,
                    technical_metadata=mapping_data.technical_metadata,
                )
                
                session.add(mapping)
                session.commit()
                session.refresh(mapping)
                
                logger.info(f"Created URL mapping {mapping.id} for config {mapping.url_config_id}")
                
                return self._mapping_to_response(mapping)
            
        except IntegrityError as e:
            logger.error(f"Integrity error creating URL mapping: {e}")
            raise URLMappingDuplicateError("URL mapping already exists") from e
        except SQLAlchemyError as e:
            logger.error(f"Database error creating URL mapping: {e}")
            raise DatabaseError(f"Failed to create URL mapping: {e}") from e
    
    def get_mapping(self, mapping_id: str) -> URLMappingResponse:
        """Get a URL mapping by ID.
        
        Args:
            mapping_id: URL mapping ID.
            
        Returns:
            URL mapping response.
            
        Raises:
            URLMappingNotFoundError: If mapping not found.
            DatabaseError: If database operation fails.
        """
        try:
            with get_database_manager().get_session() as session:
                mapping = session.query(URLMapping).filter(
                    URLMapping.id == mapping_id
                ).first()
                
                if not mapping:
                    raise URLMappingNotFoundError(f"URL mapping with ID {mapping_id} not found")
                
                return self._mapping_to_response(mapping)
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting URL mapping {mapping_id}: {e}")
            raise DatabaseError(f"Failed to get URL mapping: {e}") from e
    
    def update_mapping(self, mapping_id: str, mapping_data: URLMappingUpdate) -> URLMappingResponse:
        """Update a URL mapping.
        
        Args:
            mapping_id: URL mapping ID.
            mapping_data: URL mapping update data.
            
        Returns:
            Updated URL mapping response.
            
        Raises:
            URLMappingNotFoundError: If mapping not found.
            URLMappingValidationError: If validation fails.
            DatabaseError: If database operation fails.
        """
        try:
            with get_database_manager().get_session() as session:
                mapping = session.query(URLMapping).filter(
                    URLMapping.id == mapping_id
                ).first()
                
                if not mapping:
                    raise URLMappingNotFoundError(f"URL mapping with ID {mapping_id} not found")
                
                # Validate URL configuration if being updated
                if mapping_data.url_config_id and mapping_data.url_config_id != mapping.url_config_id:
                    url_config = session.query(URLConfiguration).filter(
                        URLConfiguration.id == mapping_data.url_config_id
                    ).first()
                    
                    if not url_config:
                        raise URLMappingValidationError(
                            f"URL configuration with ID {mapping_data.url_config_id} not found"
                        )
                
                # Update fields
                update_data = mapping_data.dict(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(mapping, field, value)
                
                mapping.updated_at = datetime.utcnow()
                
                session.commit()
                session.refresh(mapping)
                
                logger.info(f"Updated URL mapping {mapping_id}")
                
                return self._mapping_to_response(mapping)
                
        except SQLAlchemyError as e:
            logger.error(f"Database error updating URL mapping {mapping_id}: {e}")
            raise DatabaseError(f"Failed to update URL mapping: {e}") from e
    
    def delete_mapping(self, mapping_id: str) -> bool:
        """Delete a URL mapping.
        
        Args:
            mapping_id: URL mapping ID.
            
        Returns:
            True if deleted successfully.
            
        Raises:
            URLMappingNotFoundError: If mapping not found.
            DatabaseError: If database operation fails.
        """
        try:
            with get_database_manager().get_session() as session:
                mapping = session.query(URLMapping).filter(
                    URLMapping.id == mapping_id
                ).first()
                
                if not mapping:
                    raise URLMappingNotFoundError(f"URL mapping with ID {mapping_id} not found")
                
                session.delete(mapping)
                session.commit()
                
                logger.info(f"Deleted URL mapping {mapping_id}")
                
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting URL mapping {mapping_id}: {e}")
            raise DatabaseError(f"Failed to delete URL mapping: {e}") from e
    
    def list_mappings(
        self,
        page: int = 1,
        size: int = 10,
        url_config_id: Optional[str] = None,
        extractor_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> URLMappingListResponse:
        """List URL mappings with filtering and pagination.
        
        Args:
            page: Page number (1-based).
            size: Items per page.
            url_config_id: Filter by URL configuration ID.
            extractor_id: Filter by extractor ID.
            is_active: Filter by active status.
            search: Search term for extractor ID.
            
        Returns:
            Paginated list of URL mappings.
            
        Raises:
            DatabaseError: If database operation fails.
        """
        try:
            with get_database_manager().get_session() as session:
                query = session.query(URLMapping)
                
                # Apply filters
                if url_config_id:
                    query = query.filter(URLMapping.url_config_id == url_config_id)
                
                if extractor_id:
                    query = query.filter(URLMapping.extractor_id == extractor_id)
                
                if is_active is not None:
                    query = query.filter(URLMapping.is_active == is_active)
                
                if search:
                    query = query.filter(
                        or_(
                            URLMapping.extractor_id.ilike(f"%{search}%"),
                            URLMapping.url_config_id.ilike(f"%{search}%")
                        )
                    )
                
                # Get total count
                total = query.count()
                
                # Apply pagination
                offset = (page - 1) * size
                mappings = query.order_by(desc(URLMapping.created_at)).offset(offset).limit(size).all()
                
                # Calculate pagination info
                pages = (total + size - 1) // size
                
                return URLMappingListResponse(
                    items=[self._mapping_to_response(mapping) for mapping in mappings],
                    total=total,
                    page=page,
                    size=size,
                    pages=pages,
                )
                
        except SQLAlchemyError as e:
            logger.error(f"Database error listing URL mappings: {e}")
            raise DatabaseError(f"Failed to list URL mappings: {e}") from e
    
    def get_stats(self) -> URLMappingStats:
        """Get URL mapping statistics.
        
        Returns:
            URL mapping statistics.
            
        Raises:
            DatabaseError: If database operation fails.
        """
        try:
            with get_database_manager().get_session() as session:
                # Get basic counts
                total_mappings = session.query(URLMapping).count()
                active_mappings = session.query(URLMapping).filter(
                    URLMapping.is_active == True
                ).count()
                inactive_mappings = total_mappings - active_mappings
                
                # Get extractor counts
                extractor_counts = {}
                extractor_results = session.query(
                    URLMapping.extractor_id,
                    func.count(URLMapping.id)
                ).group_by(URLMapping.extractor_id).all()
                
                for extractor_id, count in extractor_results:
                    extractor_counts[extractor_id] = count
                
                return URLMappingStats(
                    total_mappings=total_mappings,
                    active_mappings=active_mappings,
                    inactive_mappings=inactive_mappings,
                    extractors_count=extractor_counts,
                )
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting URL mapping stats: {e}")
            raise DatabaseError(f"Failed to get URL mapping stats: {e}") from e
    
    def bulk_update_status(self, bulk_update: BulkStatusUpdate) -> BulkStatusUpdateResponse:
        """Bulk update status of multiple URL mappings.
        
        Args:
            bulk_update: Bulk status update data.
            
        Returns:
            Bulk update response.
            
        Raises:
            DatabaseError: If database operation fails.
        """
        try:
            with get_database_manager().get_session() as session:
                updated_count = 0
                failed_ids = []
                
                for mapping_id in bulk_update.mapping_ids:
                    try:
                        mapping = session.query(URLMapping).filter(
                            URLMapping.id == mapping_id
                        ).first()
                        
                        if mapping:
                            mapping.is_active = bulk_update.status == URLMappingStatus.ACTIVE
                            mapping.updated_at = datetime.utcnow()
                            updated_count += 1
                        else:
                            failed_ids.append(mapping_id)
                            
                    except Exception as e:
                        logger.warning(f"Failed to update mapping {mapping_id}: {e}")
                        failed_ids.append(mapping_id)
                
                session.commit()
                
                logger.info(f"Bulk updated {updated_count} URL mappings, {len(failed_ids)} failed")
                
                return BulkStatusUpdateResponse(
                    updated_count=updated_count,
                    failed_ids=failed_ids,
                )
                
        except SQLAlchemyError as e:
            logger.error(f"Database error in bulk status update: {e}")
            raise DatabaseError(f"Failed to bulk update status: {e}") from e
    
    def health_check(self) -> HealthCheckResponse:
        """Perform health check.
        
        Returns:
            Health check response.
            
        Raises:
            DatabaseError: If database is not accessible.
        """
        try:
            with get_database_manager().get_session() as session:
                # Test database connection
                session.execute(text("SELECT 1"))
                
                return HealthCheckResponse(
                    status="healthy",
                    timestamp=datetime.utcnow().isoformat(),
                    version="1.0.0",
                    database="connected",
                )
                
        except SQLAlchemyError as e:
            logger.error(f"Database health check failed: {e}")
            raise DatabaseError(f"Database health check failed: {e}") from e
    
    def _mapping_to_response(self, mapping: URLMapping) -> URLMappingResponse:
        """Convert URLMapping model to response.
        
        Args:
            mapping: URLMapping model instance.
            
        Returns:
            URLMappingResponse instance.
        """
        return URLMappingResponse(
            id=mapping.id,
            url_config_id=mapping.url_config_id,
            extractor_id=mapping.extractor_id,
            rate_limit=mapping.rate_limit,
            crawler_settings=mapping.crawler_settings,
            validation_rules=mapping.validation_rules,
            is_active=mapping.is_active,
            technical_metadata=mapping.technical_metadata,
            created_at=mapping.created_at.isoformat() if mapping.created_at else None,
            updated_at=mapping.updated_at.isoformat() if mapping.updated_at else None,
        )


# Global service instance
_service_instance: Optional[URLMappingService] = None


def get_service(session: Optional[Session] = None) -> URLMappingService:
    """Get URL mapping service instance.
    
    Args:
        session: Optional SQLAlchemy session.
        
    Returns:
        URLMappingService instance.
    """
    global _service_instance
    
    if session:
        return URLMappingService(session)
    
    if _service_instance is None:
        _service_instance = URLMappingService()
    
    return _service_instance