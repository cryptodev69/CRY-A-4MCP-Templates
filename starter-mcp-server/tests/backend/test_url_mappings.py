"""Comprehensive test suite for URL Mapping Service.

This module contains comprehensive tests for all components of the URL mapping service,
following Test-Driven Development (TDD) principles.
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import our modules
from url_mapping_service.config import Settings
from url_mapping_service.database import DatabaseManager, get_db_session
from url_mapping_service.exceptions import (
    DatabaseError,
    ExtractorNotFoundError,
    URLConfigNotFoundError,
    URLMappingDuplicateError,
    URLMappingNotFoundError,
    URLMappingValidationError,
)
from url_mapping_service.main import app
from url_mapping_service.models import (
    URLMapping,
    URLMappingExtractor,
    URLMappingCreate,
    URLMappingResponse,
    URLMappingUpdate,
    URLMappingListResponse,
    URLMappingStats,
)
from url_mapping_service.service import URLMappingService


# Test Configuration
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def test_settings():
    """Create test settings."""
    return Settings(
        database_url=TEST_DATABASE_URL,
        sql_debug=True,
        environment="development",
        enable_metrics=False,
    )


@pytest.fixture
def test_engine(test_settings):
    """Create test database engine."""
    engine = create_engine(
        test_settings.database_url,
        echo=test_settings.database_echo,
        connect_args={"check_same_thread": False},
    )
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create test database session."""
    # Create tables
    URLMapping.metadata.create_all(test_engine)
    
    # Create session
    TestSessionLocal = sessionmaker(bind=test_engine)
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables
        URLMapping.metadata.drop_all(test_engine)


@pytest.fixture
def test_service(test_session):
    """Create test URL mapping service."""
    return URLMappingService(test_session)


@pytest.fixture
def test_client(test_session):
    """Create test FastAPI client."""
    def override_get_db():
        try:
            yield test_session
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_url_mapping_data():
    """Sample URL mapping data for testing."""
    return {
        "name": "Test Mapping",
        "url_config_id": 1,
        "extractor_ids": [1, 2],
        "rate_limit": 60,
        "crawler_settings": {
            "delay": 1.0,
            "timeout": 30,
            "user_agent": "TestBot/1.0"
        },
        "validation_rules": {
            "required_fields": ["title", "content"],
            "min_content_length": 100
        },
        "priority": 1,
        "tags": ["test", "sample"],
        "technical_metadata": {
            "description": "Test mapping for unit tests",
            "created_by": "test_user"
        }
    }


class TestURLMappingModels:
    """Test Pydantic models for URL mappings."""
    
    def test_url_mapping_create_valid(self, sample_url_mapping_data):
        """Test creating valid URL mapping."""
        mapping = URLMappingCreate(**sample_url_mapping_data)
        assert mapping.name == "Test Mapping"
        assert mapping.url_config_id == 1
        assert mapping.extractor_ids == [1, 2]
        assert mapping.rate_limit == 60
        assert mapping.priority == 1
        assert mapping.tags == ["test", "sample"]
    
    def test_url_mapping_create_missing_required_fields(self):
        """Test URL mapping creation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            URLMappingCreate()
        
        errors = exc_info.value.errors()
        required_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        assert "name" in required_fields
        assert "url_config_id" in required_fields
        assert "extractor_ids" in required_fields
    
    def test_url_mapping_create_invalid_rate_limit(self, sample_url_mapping_data):
        """Test URL mapping creation with invalid rate limit."""
        sample_url_mapping_data["rate_limit"] = -1
        with pytest.raises(ValidationError) as exc_info:
            URLMappingCreate(**sample_url_mapping_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("rate_limit",) for error in errors)
    
    def test_url_mapping_create_invalid_priority(self, sample_url_mapping_data):
        """Test URL mapping creation with invalid priority."""
        sample_url_mapping_data["priority"] = 0
        with pytest.raises(ValidationError) as exc_info:
            URLMappingCreate(**sample_url_mapping_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("priority",) for error in errors)
    
    def test_url_mapping_update_partial(self):
        """Test URL mapping update with partial data."""
        update_data = {
            "name": "Updated Mapping",
            "rate_limit": 120
        }
        mapping_update = URLMappingUpdate(**update_data)
        assert mapping_update.name == "Updated Mapping"
        assert mapping_update.rate_limit == 120
        assert mapping_update.url_config_id is None
    
    def test_url_mapping_response_serialization(self, sample_url_mapping_data):
        """Test URL mapping response serialization."""
        response_data = {
            "id": 1,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_active": True,
            **sample_url_mapping_data
        }
        response = URLMappingResponse(**response_data)
        assert response.id == 1
        assert response.is_active is True
        assert response.name == "Test Mapping"


class TestURLMappingDatabase:
    """Test database operations for URL mappings."""
    
    def test_create_url_mapping(self, test_service, sample_url_mapping_data):
        """Test creating URL mapping in database."""
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=True):
            
            mapping = test_service.create_mapping(mapping_data)
            
            assert mapping.id is not None
            assert mapping.name == "Test Mapping"
            assert mapping.url_config_id == 1
            assert mapping.is_active is True
            assert len(mapping.extractors) == 2
    
    def test_get_url_mapping_by_id(self, test_service, sample_url_mapping_data):
        """Test retrieving URL mapping by ID."""
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=True):
            
            created_mapping = test_service.create_mapping(mapping_data)
            retrieved_mapping = test_service.get_mapping(created_mapping.id)
            
            assert retrieved_mapping.id == created_mapping.id
            assert retrieved_mapping.name == "Test Mapping"
    
    def test_get_nonexistent_url_mapping(self, test_service):
        """Test retrieving non-existent URL mapping."""
        with pytest.raises(URLMappingNotFoundError):
            test_service.get_mapping(999)
    
    def test_list_url_mappings_with_pagination(self, test_service, sample_url_mapping_data):
        """Test listing URL mappings with pagination."""
        # Create multiple mappings
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=True):
            
            for i in range(5):
                data = sample_url_mapping_data.copy()
                data["name"] = f"Test Mapping {i}"
                mapping_data = URLMappingCreate(**data)
                test_service.create_mapping(mapping_data)
            
            # Test pagination
            result = test_service.list_mappings(skip=0, limit=3)
            assert len(result.items) == 3
            assert result.total == 5
            assert result.page == 1
            assert result.pages == 2
    
    def test_list_url_mappings_with_filters(self, test_service, sample_url_mapping_data):
        """Test listing URL mappings with filters."""
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=True):
            
            # Create mappings with different properties
            for i in range(3):
                data = sample_url_mapping_data.copy()
                data["name"] = f"Test Mapping {i}"
                data["url_config_id"] = i + 1
                mapping_data = URLMappingCreate(**data)
                test_service.create_mapping(mapping_data)
            
            # Test filtering by url_config_id
            result = test_service.list_mappings(url_config_id=1)
            assert len(result.items) == 1
            assert result.items[0].url_config_id == 1
    
    def test_update_url_mapping(self, test_service, sample_url_mapping_data):
        """Test updating URL mapping."""
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=True):
            
            created_mapping = test_service.create_mapping(mapping_data)
            
            update_data = URLMappingUpdate(
                name="Updated Mapping",
                rate_limit=120
            )
            
            updated_mapping = test_service.update_mapping(created_mapping.id, update_data)
            
            assert updated_mapping.name == "Updated Mapping"
            assert updated_mapping.rate_limit == 120
            assert updated_mapping.url_config_id == 1  # Unchanged
    
    def test_delete_url_mapping(self, test_service, sample_url_mapping_data):
        """Test deleting URL mapping."""
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=True):
            
            created_mapping = test_service.create_mapping(mapping_data)
            
            # Delete mapping
            test_service.delete_mapping(created_mapping.id)
            
            # Verify deletion
            with pytest.raises(URLMappingNotFoundError):
                test_service.get_mapping(created_mapping.id)
    
    def test_create_url_mapping_with_multiple_extractors(self, test_service, sample_url_mapping_data):
        """Test creating URL mapping with multiple extractors."""
        sample_url_mapping_data["extractor_ids"] = [1, 2, 3]
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=True):
            
            mapping = test_service.create_mapping(mapping_data)
            
            assert len(mapping.extractors) == 3
            extractor_ids = [ext.extractor_id for ext in mapping.extractors]
            assert set(extractor_ids) == {1, 2, 3}


class TestURLMappingAPI:
    """Test API endpoints for URL mappings."""
    
    def test_get_url_mappings_endpoint(self, test_client):
        """Test GET /api/url-mappings/ endpoint."""
        response = test_client.get("/api/url-mappings/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
    
    def test_create_url_mapping_endpoint(self, test_client, sample_url_mapping_data):
        """Test POST /api/url-mappings/ endpoint."""
        with patch('url_mapping_service.service.URLMappingService._validate_url_config_exists', return_value=True), \
             patch('url_mapping_service.service.URLMappingService._validate_extractors_exist', return_value=True):
            
            response = test_client.post(
                "/api/url-mappings/",
                json=sample_url_mapping_data
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            
            data = response.json()
            assert data["name"] == "Test Mapping"
            assert data["url_config_id"] == 1
            assert "id" in data
            assert "created_at" in data
    
    def test_create_url_mapping_invalid_data(self, test_client):
        """Test POST /api/url-mappings/ with invalid data."""
        invalid_data = {
            "name": "",  # Empty name
            "rate_limit": -1  # Invalid rate limit
        }
        
        response = test_client.post(
            "/api/url-mappings/",
            json=invalid_data
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_url_mapping_by_id_endpoint(self, test_client, sample_url_mapping_data):
        """Test GET /api/url-mappings/{id} endpoint."""
        with patch('url_mapping_service.service.URLMappingService._validate_url_config_exists', return_value=True), \
             patch('url_mapping_service.service.URLMappingService._validate_extractors_exist', return_value=True):
            
            # Create mapping first
            create_response = test_client.post(
                "/api/url-mappings/",
                json=sample_url_mapping_data
            )
            created_mapping = create_response.json()
            
            # Get mapping by ID
            response = test_client.get(f"/api/url-mappings/{created_mapping['id']}")
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["id"] == created_mapping["id"]
            assert data["name"] == "Test Mapping"
    
    def test_get_nonexistent_url_mapping_endpoint(self, test_client):
        """Test GET /api/url-mappings/{id} with non-existent ID."""
        response = test_client.get("/api/url-mappings/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_url_mapping_endpoint(self, test_client, sample_url_mapping_data):
        """Test PUT /api/url-mappings/{id} endpoint."""
        with patch('url_mapping_service.service.URLMappingService._validate_url_config_exists', return_value=True), \
             patch('url_mapping_service.service.URLMappingService._validate_extractors_exist', return_value=True):
            
            # Create mapping first
            create_response = test_client.post(
                "/api/url-mappings/",
                json=sample_url_mapping_data
            )
            created_mapping = create_response.json()
            
            # Update mapping
            update_data = {
                "name": "Updated Mapping",
                "rate_limit": 120
            }
            
            response = test_client.put(
                f"/api/url-mappings/{created_mapping['id']}",
                json=update_data
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["name"] == "Updated Mapping"
            assert data["rate_limit"] == 120
    
    def test_delete_url_mapping_endpoint(self, test_client, sample_url_mapping_data):
        """Test DELETE /api/url-mappings/{id} endpoint."""
        with patch('url_mapping_service.service.URLMappingService._validate_url_config_exists', return_value=True), \
             patch('url_mapping_service.service.URLMappingService._validate_extractors_exist', return_value=True):
            
            # Create mapping first
            create_response = test_client.post(
                "/api/url-mappings/",
                json=sample_url_mapping_data
            )
            created_mapping = create_response.json()
            
            # Delete mapping
            response = test_client.delete(f"/api/url-mappings/{created_mapping['id']}")
            assert response.status_code == status.HTTP_204_NO_CONTENT
            
            # Verify deletion
            get_response = test_client.get(f"/api/url-mappings/{created_mapping['id']}")
            assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_url_mappings_stats_endpoint(self, test_client):
        """Test GET /api/url-mappings/stats endpoint."""
        response = test_client.get("/api/url-mappings/stats")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "total_mappings" in data
        assert "active_mappings" in data
        assert "inactive_mappings" in data
        assert "total_extractors" in data


class TestURLMappingPerformance:
    """Test performance requirements for URL mappings."""
    
    def test_list_mappings_performance(self, test_service, sample_url_mapping_data):
        """Test that listing mappings meets performance requirements."""
        # Create multiple mappings
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=True):
            
            for i in range(100):
                data = sample_url_mapping_data.copy()
                data["name"] = f"Test Mapping {i}"
                mapping_data = URLMappingCreate(**data)
                test_service.create_mapping(mapping_data)
            
            # Test performance
            start_time = time.time()
            result = test_service.list_mappings(skip=0, limit=50)
            end_time = time.time()
            
            # Should complete within 1 second
            assert (end_time - start_time) < 1.0
            assert len(result.items) == 50
    
    def test_create_mapping_performance(self, test_service, sample_url_mapping_data):
        """Test that creating mappings meets performance requirements."""
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=True):
            
            start_time = time.time()
            mapping = test_service.create_mapping(mapping_data)
            end_time = time.time()
            
            # Should complete within 0.5 seconds
            assert (end_time - start_time) < 0.5
            assert mapping.id is not None


class TestURLMappingErrorHandling:
    """Test error handling for URL mappings."""
    
    def test_create_mapping_invalid_url_config(self, test_service, sample_url_mapping_data):
        """Test creating mapping with invalid URL config."""
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        
        with patch.object(test_service, '_validate_url_config_exists', return_value=False):
            with pytest.raises(URLConfigNotFoundError):
                test_service.create_mapping(mapping_data)
    
    def test_create_mapping_invalid_extractors(self, test_service, sample_url_mapping_data):
        """Test creating mapping with invalid extractors."""
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=False):
            
            with pytest.raises(ExtractorNotFoundError):
                test_service.create_mapping(mapping_data)
    
    def test_create_mapping_duplicate_name(self, test_service, sample_url_mapping_data):
        """Test creating mapping with duplicate name."""
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        
        with patch.object(test_service, '_validate_url_config_exists', return_value=True), \
             patch.object(test_service, '_validate_extractors_exist', return_value=True):
            
            # Create first mapping
            test_service.create_mapping(mapping_data)
            
            # Try to create duplicate
            with pytest.raises(URLMappingDuplicateError):
                test_service.create_mapping(mapping_data)
    
    @patch('url_mapping_service.service.URLMappingService._validate_url_config_exists')
    def test_database_connection_error(self, mock_validate, test_service, sample_url_mapping_data):
        """Test handling database connection errors."""
        mock_validate.side_effect = Exception("Database connection failed")
        
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        
        with pytest.raises(DatabaseError):
            test_service.create_mapping(mapping_data)


class TestURLMappingValidation:
    """Test validation logic for URL mappings."""
    
    def test_validate_extractor_ids_empty_list(self, test_service):
        """Test validation with empty extractor IDs list."""
        with pytest.raises(URLMappingValidationError):
            test_service._validate_extractors_exist([])
    
    def test_validate_extractor_ids_duplicates(self, test_service):
        """Test validation with duplicate extractor IDs."""
        with pytest.raises(URLMappingValidationError):
            test_service._validate_extractors_exist([1, 2, 1])
    
    def test_validate_json_fields(self, sample_url_mapping_data):
        """Test validation of JSON fields."""
        # Test valid JSON
        mapping_data = URLMappingCreate(**sample_url_mapping_data)
        assert isinstance(mapping_data.crawler_settings, dict)
        assert isinstance(mapping_data.validation_rules, dict)
        assert isinstance(mapping_data.metadata, dict)
        
        # Test invalid JSON structure
        invalid_data = sample_url_mapping_data.copy()
        invalid_data["crawler_settings"] = "invalid json"
        
        with pytest.raises(ValidationError):
            URLMappingCreate(**invalid_data)


class TestDatabaseManager:
    """Test database manager functionality."""
    
    def test_database_manager_initialization(self, test_settings):
        """Test database manager initialization."""
        db_manager = DatabaseManager(test_settings)
        assert db_manager.settings == test_settings
        assert db_manager.engine is not None
    
    def test_database_health_check(self, test_settings):
        """Test database health check."""
        db_manager = DatabaseManager(test_settings)
        is_healthy = db_manager.health_check()
        assert is_healthy is True
    
    def test_create_tables(self, test_settings):
        """Test table creation."""
        db_manager = DatabaseManager(test_settings)
        db_manager.create_tables()
        
        # Verify tables exist
        with db_manager.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='url_mappings'"
            ))
            tables = result.fetchall()
            assert len(tables) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])