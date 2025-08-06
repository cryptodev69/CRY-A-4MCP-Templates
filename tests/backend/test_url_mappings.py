"""Comprehensive test suite for URL Mappings backend service.

This test suite follows TDD principles and covers:
- Database operations with multiple extractors
- API endpoints with proper validation
- Data transformation and serialization
- Error handling and edge cases
- Performance requirements
"""

import pytest
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Import the models and services we'll be testing
# Note: These imports will be created as we implement the service
try:
    from starter_mcp_server.src.models.url_mappings import (
        URLMapping,
        URLMappingExtractor,
        URLMappingCreate,
        URLMappingUpdate,
        URLMappingResponse
    )
    from starter_mcp_server.src.services.url_mapping_service import URLMappingService
    from starter_mcp_server.src.api.url_mappings import router as url_mappings_router
except ImportError:
    # These will be implemented during TDD
    pass


class TestURLMappingModels:
    """Test Pydantic models for URL mappings."""
    
    def test_url_mapping_create_model_validation(self):
        """Test URLMappingCreate model validates required fields."""
        # Valid data
        valid_data = {
            "name": "Test Mapping",
            "url_config_id": 1,
            "extractor_ids": [1, 2],
            "rate_limit": 60,
            "priority": 1
        }
        
        # This should not raise an exception
        mapping = URLMappingCreate(**valid_data)
        assert mapping.name == "Test Mapping"
        assert mapping.extractor_ids == [1, 2]
        assert mapping.rate_limit == 60
        assert mapping.priority == 1
        assert mapping.is_active is True  # Default value
    
    def test_url_mapping_create_model_missing_required_fields(self):
        """Test URLMappingCreate model fails with missing required fields."""
        with pytest.raises(ValueError):
            URLMappingCreate()
        
        with pytest.raises(ValueError):
            URLMappingCreate(name="Test")
        
        with pytest.raises(ValueError):
            URLMappingCreate(name="Test", url_config_id=1)
    
    def test_url_mapping_create_model_empty_extractors(self):
        """Test URLMappingCreate model fails with empty extractor list."""
        with pytest.raises(ValueError, match="At least one extractor must be specified"):
            URLMappingCreate(
                name="Test Mapping",
                url_config_id=1,
                extractor_ids=[]
            )
    
    def test_url_mapping_create_model_invalid_rate_limit(self):
        """Test URLMappingCreate model validates rate limit range."""
        with pytest.raises(ValueError, match="Rate limit must be between 1 and 3600"):
            URLMappingCreate(
                name="Test Mapping",
                url_config_id=1,
                extractor_ids=[1],
                rate_limit=0
            )
        
        with pytest.raises(ValueError, match="Rate limit must be between 1 and 3600"):
            URLMappingCreate(
                name="Test Mapping",
                url_config_id=1,
                extractor_ids=[1],
                rate_limit=3601
            )
    
    def test_url_mapping_create_model_invalid_priority(self):
        """Test URLMappingCreate model validates priority range."""
        with pytest.raises(ValueError, match="Priority must be between 1 and 10"):
            URLMappingCreate(
                name="Test Mapping",
                url_config_id=1,
                extractor_ids=[1],
                priority=0
            )
        
        with pytest.raises(ValueError, match="Priority must be between 1 and 10"):
            URLMappingCreate(
                name="Test Mapping",
                url_config_id=1,
                extractor_ids=[1],
                priority=11
            )
    
    def test_url_mapping_update_model_partial_updates(self):
        """Test URLMappingUpdate model allows partial updates."""
        # Should allow updating just the name
        update = URLMappingUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.extractor_ids is None
        
        # Should allow updating just extractors
        update = URLMappingUpdate(extractor_ids=[3, 4])
        assert update.extractor_ids == [3, 4]
        assert update.name is None
    
    def test_url_mapping_response_model_serialization(self):
        """Test URLMappingResponse model serializes correctly."""
        response_data = {
            "id": 1,
            "name": "Test Mapping",
            "url_config_id": 1,
            "extractor_ids": [1, 2],
            "rate_limit": 60,
            "priority": 1,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        response = URLMappingResponse(**response_data)
        assert response.id == 1
        assert response.extractor_ids == [1, 2]
        
        # Test JSON serialization
        json_data = response.model_dump()
        assert "id" in json_data
        assert "extractor_ids" in json_data


class TestURLMappingDatabase:
    """Test database operations for URL mappings."""
    
    @pytest.fixture
    async def db_session(self):
        """Create a test database session."""
        # Use in-memory SQLite for testing
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create session
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            yield session
        
        await engine.dispose()
    
    @pytest.fixture
    async def sample_url_mapping_data(self):
        """Sample data for testing."""
        return {
            "name": "Test News Mapping",
            "url_config_id": 1,
            "extractor_ids": [1, 2],
            "rate_limit": 60,
            "priority": 1,
            "tags": ["news", "articles"],
            "category": "news",
            "notes": "Test mapping for news articles",
            "is_active": True
        }
    
    async def test_create_url_mapping_with_multiple_extractors(self, db_session, sample_url_mapping_data):
        """Test creating URL mapping with multiple extractors."""
        service = URLMappingService(db_session)
        
        # Create the mapping
        mapping = await service.create_url_mapping(URLMappingCreate(**sample_url_mapping_data))
        
        assert mapping.id is not None
        assert mapping.name == "Test News Mapping"
        assert len(mapping.extractor_ids) == 2
        assert 1 in mapping.extractor_ids
        assert 2 in mapping.extractor_ids
        assert mapping.rate_limit == 60
        assert mapping.priority == 1
        assert mapping.is_active is True
        assert mapping.created_at is not None
        assert mapping.updated_at is not None
    
    async def test_get_url_mapping_by_id(self, db_session, sample_url_mapping_data):
        """Test retrieving URL mapping by ID."""
        service = URLMappingService(db_session)
        
        # Create a mapping first
        created_mapping = await service.create_url_mapping(URLMappingCreate(**sample_url_mapping_data))
        
        # Retrieve it
        retrieved_mapping = await service.get_url_mapping(created_mapping.id)
        
        assert retrieved_mapping is not None
        assert retrieved_mapping.id == created_mapping.id
        assert retrieved_mapping.name == created_mapping.name
        assert retrieved_mapping.extractor_ids == created_mapping.extractor_ids
    
    async def test_get_nonexistent_url_mapping(self, db_session):
        """Test retrieving non-existent URL mapping returns None."""
        service = URLMappingService(db_session)
        
        mapping = await service.get_url_mapping(999)
        assert mapping is None
    
    async def test_list_url_mappings_with_pagination(self, db_session):
        """Test listing URL mappings with pagination."""
        service = URLMappingService(db_session)
        
        # Create multiple mappings
        for i in range(5):
            await service.create_url_mapping(URLMappingCreate(
                name=f"Test Mapping {i}",
                url_config_id=1,
                extractor_ids=[1]
            ))
        
        # Test pagination
        mappings_page1 = await service.list_url_mappings(skip=0, limit=3)
        assert len(mappings_page1) == 3
        
        mappings_page2 = await service.list_url_mappings(skip=3, limit=3)
        assert len(mappings_page2) == 2
    
    async def test_list_url_mappings_with_filters(self, db_session):
        """Test listing URL mappings with category and active filters."""
        service = URLMappingService(db_session)
        
        # Create mappings with different categories and statuses
        await service.create_url_mapping(URLMappingCreate(
            name="News Mapping",
            url_config_id=1,
            extractor_ids=[1],
            category="news",
            is_active=True
        ))
        
        await service.create_url_mapping(URLMappingCreate(
            name="E-commerce Mapping",
            url_config_id=2,
            extractor_ids=[2],
            category="ecommerce",
            is_active=False
        ))
        
        # Test category filter
        news_mappings = await service.list_url_mappings(category="news")
        assert len(news_mappings) == 1
        assert news_mappings[0].category == "news"
        
        # Test active filter
        active_mappings = await service.list_url_mappings(is_active=True)
        assert len(active_mappings) == 1
        assert active_mappings[0].is_active is True
    
    async def test_update_url_mapping_extractors(self, db_session, sample_url_mapping_data):
        """Test updating URL mapping extractors."""
        service = URLMappingService(db_session)
        
        # Create a mapping
        mapping = await service.create_url_mapping(URLMappingCreate(**sample_url_mapping_data))
        
        # Update extractors
        update_data = URLMappingUpdate(extractor_ids=[3, 4, 5])
        updated_mapping = await service.update_url_mapping(mapping.id, update_data)
        
        assert updated_mapping.extractor_ids == [3, 4, 5]
        assert len(updated_mapping.extractor_ids) == 3
        assert updated_mapping.updated_at > mapping.updated_at
    
    async def test_update_url_mapping_partial_fields(self, db_session, sample_url_mapping_data):
        """Test partial updates to URL mapping."""
        service = URLMappingService(db_session)
        
        # Create a mapping
        mapping = await service.create_url_mapping(URLMappingCreate(**sample_url_mapping_data))
        
        # Update only name and priority
        update_data = URLMappingUpdate(
            name="Updated Name",
            priority=5
        )
        updated_mapping = await service.update_url_mapping(mapping.id, update_data)
        
        assert updated_mapping.name == "Updated Name"
        assert updated_mapping.priority == 5
        # Other fields should remain unchanged
        assert updated_mapping.extractor_ids == mapping.extractor_ids
        assert updated_mapping.rate_limit == mapping.rate_limit
    
    async def test_delete_url_mapping(self, db_session, sample_url_mapping_data):
        """Test deleting URL mapping and its extractor relationships."""
        service = URLMappingService(db_session)
        
        # Create a mapping
        mapping = await service.create_url_mapping(URLMappingCreate(**sample_url_mapping_data))
        
        # Delete it
        success = await service.delete_url_mapping(mapping.id)
        assert success is True
        
        # Verify it's gone
        deleted_mapping = await service.get_url_mapping(mapping.id)
        assert deleted_mapping is None
    
    async def test_delete_nonexistent_url_mapping(self, db_session):
        """Test deleting non-existent URL mapping returns False."""
        service = URLMappingService(db_session)
        
        success = await service.delete_url_mapping(999)
        assert success is False


class TestURLMappingAPI:
    """Test API endpoints for URL mappings."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(url_mappings_router, prefix="/api/url-mappings")
        
        return TestClient(app)
    
    @pytest.fixture
    def mock_service(self):
        """Mock URL mapping service."""
        return AsyncMock(spec=URLMappingService)
    
    def test_get_url_mappings_endpoint(self, client, mock_service):
        """Test GET /api/url-mappings/ endpoint."""
        # Mock service response
        mock_mappings = [
            URLMappingResponse(
                id=1,
                name="Test Mapping",
                url_config_id=1,
                extractor_ids=[1, 2],
                rate_limit=60,
                priority=1,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        mock_service.list_url_mappings.return_value = mock_mappings
        
        # Make request
        response = client.get("/api/url-mappings/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Mapping"
        assert data[0]["extractor_ids"] == [1, 2]
    
    def test_get_url_mappings_with_filters(self, client, mock_service):
        """Test GET /api/url-mappings/ with query parameters."""
        mock_service.list_url_mappings.return_value = []
        
        response = client.get("/api/url-mappings/?category=news&is_active=true&skip=0&limit=10")
        
        assert response.status_code == 200
        # Verify service was called with correct parameters
        mock_service.list_url_mappings.assert_called_once_with(
            skip=0,
            limit=10,
            category="news",
            is_active=True
        )
    
    def test_create_url_mapping_endpoint(self, client, mock_service):
        """Test POST /api/url-mappings/ endpoint."""
        # Mock service response
        mock_response = URLMappingResponse(
            id=1,
            name="New Mapping",
            url_config_id=1,
            extractor_ids=[1, 2],
            rate_limit=60,
            priority=1,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_service.create_url_mapping.return_value = mock_response
        
        # Request data
        request_data = {
            "name": "New Mapping",
            "url_config_id": 1,
            "extractor_ids": [1, 2],
            "rate_limit": 60,
            "priority": 1
        }
        
        response = client.post("/api/url-mappings/", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Mapping"
        assert data["extractor_ids"] == [1, 2]
    
    def test_create_url_mapping_validation_error(self, client, mock_service):
        """Test POST /api/url-mappings/ with invalid data."""
        # Missing required fields
        request_data = {
            "name": "Incomplete Mapping"
            # Missing url_config_id and extractor_ids
        }
        
        response = client.post("/api/url-mappings/", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_get_url_mapping_by_id_endpoint(self, client, mock_service):
        """Test GET /api/url-mappings/{id} endpoint."""
        # Mock service response
        mock_mapping = URLMappingResponse(
            id=1,
            name="Test Mapping",
            url_config_id=1,
            extractor_ids=[1, 2],
            rate_limit=60,
            priority=1,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_service.get_url_mapping.return_value = mock_mapping
        
        response = client.get("/api/url-mappings/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Mapping"
    
    def test_get_url_mapping_not_found(self, client, mock_service):
        """Test GET /api/url-mappings/{id} with non-existent ID."""
        mock_service.get_url_mapping.return_value = None
        
        response = client.get("/api/url-mappings/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "URL mapping not found"
    
    def test_update_url_mapping_endpoint(self, client, mock_service):
        """Test PUT /api/url-mappings/{id} endpoint."""
        # Mock service response
        mock_updated = URLMappingResponse(
            id=1,
            name="Updated Mapping",
            url_config_id=1,
            extractor_ids=[3, 4],
            rate_limit=120,
            priority=2,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_service.update_url_mapping.return_value = mock_updated
        
        # Update data
        update_data = {
            "name": "Updated Mapping",
            "extractor_ids": [3, 4],
            "rate_limit": 120,
            "priority": 2
        }
        
        response = client.put("/api/url-mappings/1", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Mapping"
        assert data["extractor_ids"] == [3, 4]
        assert data["rate_limit"] == 120
    
    def test_delete_url_mapping_endpoint(self, client, mock_service):
        """Test DELETE /api/url-mappings/{id} endpoint."""
        mock_service.delete_url_mapping.return_value = True
        
        response = client.delete("/api/url-mappings/1")
        
        assert response.status_code == 204
    
    def test_delete_url_mapping_not_found(self, client, mock_service):
        """Test DELETE /api/url-mappings/{id} with non-existent ID."""
        mock_service.delete_url_mapping.return_value = False
        
        response = client.delete("/api/url-mappings/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "URL mapping not found"


class TestURLMappingPerformance:
    """Test performance requirements for URL mapping operations."""
    
    @pytest.mark.asyncio
    async def test_list_mappings_performance(self, db_session):
        """Test that listing mappings meets performance requirements (<500ms)."""
        service = URLMappingService(db_session)
        
        # Create a reasonable number of mappings
        for i in range(100):
            await service.create_url_mapping(URLMappingCreate(
                name=f"Performance Test Mapping {i}",
                url_config_id=1,
                extractor_ids=[1, 2]
            ))
        
        # Measure performance
        import time
        start_time = time.time()
        
        mappings = await service.list_url_mappings(limit=50)
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert len(mappings) == 50
        assert duration < 0.5  # Less than 500ms
    
    @pytest.mark.asyncio
    async def test_create_mapping_performance(self, db_session):
        """Test that creating mappings meets performance requirements."""
        service = URLMappingService(db_session)
        
        import time
        start_time = time.time()
        
        mapping = await service.create_url_mapping(URLMappingCreate(
            name="Performance Test",
            url_config_id=1,
            extractor_ids=[1, 2, 3, 4, 5]  # Multiple extractors
        ))
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert mapping.id is not None
        assert duration < 0.1  # Less than 100ms for single create


class TestURLMappingErrorHandling:
    """Test error handling and edge cases."""
    
    async def test_create_mapping_with_invalid_url_config(self, db_session):
        """Test creating mapping with non-existent URL config."""
        service = URLMappingService(db_session)
        
        with pytest.raises(ValueError, match="URL configuration not found"):
            await service.create_url_mapping(URLMappingCreate(
                name="Invalid Config Mapping",
                url_config_id=999,  # Non-existent
                extractor_ids=[1]
            ))
    
    async def test_create_mapping_with_invalid_extractors(self, db_session):
        """Test creating mapping with non-existent extractors."""
        service = URLMappingService(db_session)
        
        with pytest.raises(ValueError, match="Extractor\(s\) not found"):
            await service.create_url_mapping(URLMappingCreate(
                name="Invalid Extractor Mapping",
                url_config_id=1,
                extractor_ids=[999, 998]  # Non-existent
            ))
    
    async def test_create_mapping_with_duplicate_name(self, db_session):
        """Test creating mapping with duplicate name."""
        service = URLMappingService(db_session)
        
        # Create first mapping
        await service.create_url_mapping(URLMappingCreate(
            name="Duplicate Name",
            url_config_id=1,
            extractor_ids=[1]
        ))
        
        # Try to create another with same name
        with pytest.raises(ValueError, match="URL mapping with this name already exists"):
            await service.create_url_mapping(URLMappingCreate(
                name="Duplicate Name",
                url_config_id=2,
                extractor_ids=[2]
            ))
    
    async def test_update_mapping_with_invalid_id(self, db_session):
        """Test updating non-existent mapping."""
        service = URLMappingService(db_session)
        
        with pytest.raises(ValueError, match="URL mapping not found"):
            await service.update_url_mapping(
                999,
                URLMappingUpdate(name="Updated Name")
            )
    
    async def test_database_connection_error_handling(self):
        """Test handling of database connection errors."""
        # Mock a database session that raises connection errors
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Database connection failed")
        
        service = URLMappingService(mock_session)
        
        with pytest.raises(Exception, match="Database connection failed"):
            await service.list_url_mappings()


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        "--cov=starter_mcp_server.src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
        "-v",
        __file__
    ])