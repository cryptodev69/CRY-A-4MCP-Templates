"""Service layer for URL mapping operations.

This module provides the business logic for URL mapping CRUD operations,
including support for multiple extractors, validation, and performance optimization.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.exc import IntegrityError

from ..models.url_mappings import (
    URLMapping, URLMappingExtractor, URLMappingCreate, URLMappingUpdate, 
    URLMappingResponse, URLMappingListResponse, URLMappingStats
)
from ..exceptions import (
    URLMappingNotFoundError, URLMappingValidationError, 
    URLMappingDuplicateError, DatabaseError
)


class URLMappingService:
    """Service class for URL mapping operations."""
    
    def __init__(self, db: Session):
        """Initialize the service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create_url_mapping(self, mapping_data: URLMappingCreate) -> URLMappingResponse:
        """Create a new URL mapping with multiple extractors.
        
        Args:
            mapping_data: URL mapping creation data
            
        Returns:
            Created URL mapping response
            
        Raises:
            URLMappingDuplicateError: If mapping name already exists
            URLMappingValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Check if name already exists
            existing = self.db.query(URLMapping).filter(
                URLMapping.name == mapping_data.name
            ).first()
            
            if existing:
                raise URLMappingDuplicateError(f"URL mapping with name '{mapping_data.name}' already exists")
            
            # Create URL mapping
            db_mapping = URLMapping(
                name=mapping_data.name,
                url_config_id=mapping_data.url_config_id,
                rate_limit=mapping_data.rate_limit,
                priority=mapping_data.priority,
                notes=mapping_data.notes,
                category=mapping_data.category,
                is_active=mapping_data.is_active
            )
            
            # Set JSON fields
            if mapping_data.crawler_settings:
                db_mapping.set_crawler_settings(mapping_data.crawler_settings)
            if mapping_data.validation_rules:
                db_mapping.set_validation_rules(mapping_data.validation_rules)
            if mapping_data.config:
                db_mapping.set_config(mapping_data.config)
            if mapping_data.metadata:
                db_mapping.set_metadata(mapping_data.metadata)
            if mapping_data.tags:
                db_mapping.set_tags(mapping_data.tags)
            
            self.db.add(db_mapping)
            self.db.flush()  # Get the ID
            
            # Create extractor mappings
            for extractor_id in mapping_data.extractor_ids:
                extractor_mapping = URLMappingExtractor(
                    url_mapping_id=db_mapping.id,
                    extractor_id=extractor_id
                )
                self.db.add(extractor_mapping)
            
            self.db.commit()
            
            # Reload with relationships
            self.db.refresh(db_mapping)
            return URLMappingResponse.from_db_model(db_mapping)
            
        except IntegrityError as e:
            self.db.rollback()
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                raise URLMappingDuplicateError(f"URL mapping with name '{mapping_data.name}' already exists")
            raise DatabaseError(f"Database integrity error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (URLMappingDuplicateError, URLMappingValidationError)):
                raise
            raise DatabaseError(f"Failed to create URL mapping: {str(e)}")
    
    def get_url_mapping(self, mapping_id: int) -> URLMappingResponse:
        """Get URL mapping by ID.
        
        Args:
            mapping_id: URL mapping ID
            
        Returns:
            URL mapping response
            
        Raises:
            URLMappingNotFoundError: If mapping not found
        """
        db_mapping = self.db.query(URLMapping).options(
            joinedload(URLMapping.extractor_mappings)
        ).filter(URLMapping.id == mapping_id).first()
        
        if not db_mapping:
            raise URLMappingNotFoundError(f"URL mapping with ID {mapping_id} not found")
        
        return URLMappingResponse.from_db_model(db_mapping)
    
    def list_url_mappings(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        url_config_id: Optional[int] = None,
        extractor_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> URLMappingListResponse:
        """List URL mappings with filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            category: Filter by category
            url_config_id: Filter by URL config ID
            extractor_id: Filter by extractor ID
            search: Search in name and notes
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            
        Returns:
            Paginated list of URL mappings
        """
        query = self.db.query(URLMapping).options(
            joinedload(URLMapping.extractor_mappings)
        )
        
        # Apply filters
        if is_active is not None:
            query = query.filter(URLMapping.is_active == is_active)
        
        if category:
            query = query.filter(URLMapping.category == category)
        
        if url_config_id:
            query = query.filter(URLMapping.url_config_id == url_config_id)
        
        if extractor_id:
            query = query.join(URLMappingExtractor).filter(
                URLMappingExtractor.extractor_id == extractor_id
            )
        
        if search:
            search_filter = or_(
                URLMapping.name.ilike(f"%{search}%"),
                URLMapping.notes.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Apply sorting
        sort_column = getattr(URLMapping, sort_by, URLMapping.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        mappings = query.offset(skip).limit(limit).all()
        
        # Convert to response models
        items = [URLMappingResponse.from_db_model(mapping) for mapping in mappings]
        
        return URLMappingListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    
    def update_url_mapping(
        self, 
        mapping_id: int, 
        mapping_data: URLMappingUpdate
    ) -> URLMappingResponse:
        """Update URL mapping.
        
        Args:
            mapping_id: URL mapping ID
            mapping_data: Update data
            
        Returns:
            Updated URL mapping response
            
        Raises:
            URLMappingNotFoundError: If mapping not found
            URLMappingDuplicateError: If name already exists
            DatabaseError: If database operation fails
        """
        try:
            db_mapping = self.db.query(URLMapping).options(
                joinedload(URLMapping.extractor_mappings)
            ).filter(URLMapping.id == mapping_id).first()
            
            if not db_mapping:
                raise URLMappingNotFoundError(f"URL mapping with ID {mapping_id} not found")
            
            # Check for name conflicts if name is being updated
            if mapping_data.name and mapping_data.name != db_mapping.name:
                existing = self.db.query(URLMapping).filter(
                    and_(
                        URLMapping.name == mapping_data.name,
                        URLMapping.id != mapping_id
                    )
                ).first()
                
                if existing:
                    raise URLMappingDuplicateError(
                        f"URL mapping with name '{mapping_data.name}' already exists"
                    )
            
            # Update basic fields
            update_data = mapping_data.dict(exclude_unset=True, exclude={'extractor_ids'})
            print(f"🔍 Backend update_url_mapping - Received data: {update_data}")
            print(f"🔍 Backend update_url_mapping - Current priority: {db_mapping.priority}")
            
            for field, value in update_data.items():
                print(f"🔍 Backend update_url_mapping - Updating field '{field}' to '{value}'")
                if field in ['crawler_settings', 'validation_rules', 'config', 'metadata', 'tags']:
                    # Handle JSON fields
                    if field == 'crawler_settings':
                        db_mapping.set_crawler_settings(value)
                    elif field == 'validation_rules':
                        db_mapping.set_validation_rules(value)
                    elif field == 'config':
                        db_mapping.set_config(value)
                    elif field == 'metadata':
                        db_mapping.set_metadata(value)
                    elif field == 'tags':
                        db_mapping.set_tags(value)
                else:
                    setattr(db_mapping, field, value)
                    if field == 'priority':
                        print(f"🔍 Backend update_url_mapping - Priority updated to: {db_mapping.priority}")
            
            # Update extractor mappings if provided
            if mapping_data.extractor_ids is not None:
                # Remove existing mappings
                self.db.query(URLMappingExtractor).filter(
                    URLMappingExtractor.url_mapping_id == mapping_id
                ).delete()
                
                # Add new mappings
                for extractor_id in mapping_data.extractor_ids:
                    extractor_mapping = URLMappingExtractor(
                        url_mapping_id=mapping_id,
                        extractor_id=extractor_id
                    )
                    self.db.add(extractor_mapping)
            
            # Update timestamp
            db_mapping.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_mapping)
            
            print(f"🔍 Backend update_url_mapping - Final priority after commit: {db_mapping.priority}")
            
            response = URLMappingResponse.from_db_model(db_mapping)
            print(f"🔍 Backend update_url_mapping - Response priority: {response.priority}")
            
            return response
            
        except IntegrityError as e:
            self.db.rollback()
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                raise URLMappingDuplicateError(
                    f"URL mapping with name '{mapping_data.name}' already exists"
                )
            raise DatabaseError(f"Database integrity error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (URLMappingNotFoundError, URLMappingDuplicateError)):
                raise
            raise DatabaseError(f"Failed to update URL mapping: {str(e)}")
    
    def delete_url_mapping(self, mapping_id: int) -> bool:
        """Delete URL mapping.
        
        Args:
            mapping_id: URL mapping ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            URLMappingNotFoundError: If mapping not found
            DatabaseError: If database operation fails
        """
        try:
            db_mapping = self.db.query(URLMapping).filter(
                URLMapping.id == mapping_id
            ).first()
            
            if not db_mapping:
                raise URLMappingNotFoundError(f"URL mapping with ID {mapping_id} not found")
            
            # Delete extractor mappings (cascade should handle this, but explicit is better)
            self.db.query(URLMappingExtractor).filter(
                URLMappingExtractor.url_mapping_id == mapping_id
            ).delete()
            
            # Delete the mapping
            self.db.delete(db_mapping)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            if isinstance(e, URLMappingNotFoundError):
                raise
            raise DatabaseError(f"Failed to delete URL mapping: {str(e)}")
    
    def get_url_mapping_stats(self) -> URLMappingStats:
        """Get statistics about URL mappings.
        
        Returns:
            URL mapping statistics
        """
        # Basic counts
        total_mappings = self.db.query(URLMapping).count()
        active_mappings = self.db.query(URLMapping).filter(
            URLMapping.is_active == True
        ).count()
        inactive_mappings = total_mappings - active_mappings
        
        # Category distribution
        category_query = self.db.query(
            URLMapping.category,
            func.count(URLMapping.id).label('count')
        ).group_by(URLMapping.category).all()
        
        categories = {}
        for category, count in category_query:
            categories[category or 'Uncategorized'] = count
        
        # Extractor usage
        extractor_query = self.db.query(
            URLMappingExtractor.extractor_id,
            func.count(URLMappingExtractor.id).label('count')
        ).group_by(URLMappingExtractor.extractor_id).all()
        
        extractors_usage = {extractor_id: count for extractor_id, count in extractor_query}
        
        # Average extractors per mapping
        total_extractor_mappings = self.db.query(URLMappingExtractor).count()
        avg_extractors_per_mapping = (
            total_extractor_mappings / total_mappings if total_mappings > 0 else 0
        )
        
        return URLMappingStats(
            total_mappings=total_mappings,
            active_mappings=active_mappings,
            inactive_mappings=inactive_mappings,
            categories=categories,
            extractors_usage=extractors_usage,
            avg_extractors_per_mapping=round(avg_extractors_per_mapping, 2)
        )
    
    def get_mappings_by_extractor(self, extractor_id: int) -> List[URLMappingResponse]:
        """Get all mappings that use a specific extractor.
        
        Args:
            extractor_id: Extractor ID
            
        Returns:
            List of URL mappings using the extractor
        """
        mappings = self.db.query(URLMapping).options(
            joinedload(URLMapping.extractor_mappings)
        ).join(URLMappingExtractor).filter(
            URLMappingExtractor.extractor_id == extractor_id
        ).all()
        
        return [URLMappingResponse.from_db_model(mapping) for mapping in mappings]
    
    def get_mappings_by_url_config(self, url_config_id: int) -> List[URLMappingResponse]:
        """Get all mappings for a specific URL configuration.
        
        Args:
            url_config_id: URL configuration ID
            
        Returns:
            List of URL mappings for the configuration
        """
        mappings = self.db.query(URLMapping).options(
            joinedload(URLMapping.extractor_mappings)
        ).filter(
            URLMapping.url_config_id == url_config_id
        ).all()
        
        return [URLMappingResponse.from_db_model(mapping) for mapping in mappings]
    
    def bulk_update_status(
        self, 
        mapping_ids: List[int], 
        is_active: bool
    ) -> List[URLMappingResponse]:
        """Bulk update the active status of multiple mappings.
        
        Args:
            mapping_ids: List of mapping IDs to update
            is_active: New active status
            
        Returns:
            List of updated URL mappings
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            # Update the mappings
            self.db.query(URLMapping).filter(
                URLMapping.id.in_(mapping_ids)
            ).update(
                {URLMapping.is_active: is_active, URLMapping.updated_at: datetime.utcnow()},
                synchronize_session=False
            )
            
            self.db.commit()
            
            # Return updated mappings
            mappings = self.db.query(URLMapping).options(
                joinedload(URLMapping.extractor_mappings)
            ).filter(URLMapping.id.in_(mapping_ids)).all()
            
            return [URLMappingResponse.from_db_model(mapping) for mapping in mappings]
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to bulk update mappings: {str(e)}")