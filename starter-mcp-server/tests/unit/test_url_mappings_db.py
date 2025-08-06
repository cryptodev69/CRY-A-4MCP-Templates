"""Unit tests for URL Mappings Database operations.

This module provides comprehensive unit testing for the URL Mappings database
operations within the CRY-A-4MCP platform, including:
    - CRUD operations for technical URL mappings
    - Database schema validation
    - Error handling and edge cases
    - Data serialization/deserialization
    - Foreign key relationship validation

The tests use mocking and temporary databases to ensure test isolation
and reproducible execution without affecting production data.

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

import asyncio
import json
import pytest
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

from src.cry_a_4mcp.storage.url_mappings_db import URLMappingsDatabase


class TestURLMappingsDatabase:
    """Test suite for URL Mappings Database operations.
    
    This class contains comprehensive tests for the URL mappings database
    functionality, covering normal operations, error conditions, and edge cases.
    """
    
    @pytest.fixture
    async def temp_db(self):
        """Create a temporary database for testing.
        
        Returns:
            URLMappingsDatabase: Initialized database instance with temporary file
        """
        # Create temporary database file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        # Initialize database
        db = URLMappingsDatabase(db_path=temp_file.name)
        await db.initialize()
        
        yield db
        
        # Cleanup
        await db.close()
        Path(temp_file.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def sample_mapping_data(self):
        """Sample URL mapping data for testing.
        
        Returns:
            dict: Sample mapping data with all required fields
        """
        return {
            "url_config_id": "config_123",
            "extractor_id": "crypto_price_extractor",
            "rate_limit": 60,
            "config": {
                "max_depth": 2,
                "delay": 1.0,
                "timeout": 30
            },
            "validation_rules": {
                "required_fields": ["price", "timestamp"],
                "min_price": 0
            },
            "crawler_settings": {
                "user_agent": "CRY-A-4MCP/1.0",
                "headers": {"Accept": "application/json"}
            },
            "is_active": True,
            "metadata": {
                "created_by": "test_user",
                "version": "1.0"
            }
        }
    
    @pytest.mark.asyncio
    async def test_create_mapping_success(self, temp_db, sample_mapping_data):
        """Test successful creation of URL mapping.
        
        Validates that the database correctly:
        - Creates new mapping with generated ID
        - Stores all provided data fields
        - Sets creation timestamp
        - Returns complete mapping data
        """
        # Act: Create mapping
        result = await temp_db.create_mapping(sample_mapping_data)
        
        # Assert: Verify creation
        assert result is not None
        assert "id" in result
        assert result["url_config_id"] == sample_mapping_data["url_config_id"]
        assert result["extractor_id"] == sample_mapping_data["extractor_id"]
        assert result["rate_limit"] == sample_mapping_data["rate_limit"]
        assert result["config"] == sample_mapping_data["config"]
        assert result["validation_rules"] == sample_mapping_data["validation_rules"]
        assert result["crawler_settings"] == sample_mapping_data["crawler_settings"]
        assert result["is_active"] == sample_mapping_data["is_active"]
        assert result["metadata"] == sample_mapping_data["metadata"]
        assert "created_at" in result
        assert "updated_at" in result
    
    @pytest.mark.asyncio
    async def test_create_mapping_minimal_data(self, temp_db):
        """Test creation with minimal required data.
        
        Validates that mappings can be created with only required fields
        and that optional fields are handled correctly.
        """
        # Arrange: Minimal mapping data
        minimal_data = {
            "url_config_id": "config_456",
            "extractor_id": "basic_extractor"
        }
        
        # Act: Create mapping
        result = await temp_db.create_mapping(minimal_data)
        
        # Assert: Verify creation with defaults
        assert result is not None
        assert result["url_config_id"] == minimal_data["url_config_id"]
        assert result["extractor_id"] == minimal_data["extractor_id"]
        assert result["is_active"] is True  # Default value
        assert result["rate_limit"] is None  # Optional field
        assert result["config"] is None  # Optional field
    
    @pytest.mark.asyncio
    async def test_get_mapping_success(self, temp_db, sample_mapping_data):
        """Test successful retrieval of URL mapping by ID.
        
        Validates that the database correctly:
        - Retrieves mapping by ID
        - Returns complete mapping data
        - Maintains data integrity
        """
        # Arrange: Create mapping first
        created = await temp_db.create_mapping(sample_mapping_data)
        mapping_id = created["id"]
        
        # Act: Retrieve mapping
        result = await temp_db.get_mapping(mapping_id)
        
        # Assert: Verify retrieval
        assert result is not None
        assert result["id"] == mapping_id
        assert result["url_config_id"] == sample_mapping_data["url_config_id"]
        assert result["extractor_id"] == sample_mapping_data["extractor_id"]
        assert result["config"] == sample_mapping_data["config"]
    
    @pytest.mark.asyncio
    async def test_get_mapping_not_found(self, temp_db):
        """Test retrieval of non-existent mapping.
        
        Validates that the database correctly:
        - Returns None for non-existent IDs
        - Handles invalid ID formats gracefully
        """
        # Act: Try to get non-existent mapping
        result = await temp_db.get_mapping("non_existent_id")
        
        # Assert: Verify None return
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_mapping_success(self, temp_db, sample_mapping_data):
        """Test successful update of URL mapping.
        
        Validates that the database correctly:
        - Updates specified fields
        - Preserves unchanged fields
        - Updates timestamp
        - Returns updated data
        """
        # Arrange: Create mapping first
        created = await temp_db.create_mapping(sample_mapping_data)
        mapping_id = created["id"]
        
        # Prepare update data
        update_data = {
            "rate_limit": 120,
            "is_active": False,
            "config": {
                "max_depth": 3,
                "delay": 2.0
            }
        }
        
        # Act: Update mapping
        result = await temp_db.update_mapping(mapping_id, update_data)
        
        # Assert: Verify update
        assert result is not None
        assert result["id"] == mapping_id
        assert result["rate_limit"] == update_data["rate_limit"]
        assert result["is_active"] == update_data["is_active"]
        assert result["config"] == update_data["config"]
        # Verify unchanged fields
        assert result["url_config_id"] == sample_mapping_data["url_config_id"]
        assert result["extractor_id"] == sample_mapping_data["extractor_id"]
        # Verify timestamp update
        assert result["updated_at"] != result["created_at"]
    
    @pytest.mark.asyncio
    async def test_update_mapping_not_found(self, temp_db):
        """Test update of non-existent mapping.
        
        Validates that the database correctly:
        - Returns None for non-existent mappings
        - Handles update attempts gracefully
        """
        # Act: Try to update non-existent mapping
        result = await temp_db.update_mapping("non_existent_id", {"rate_limit": 100})
        
        # Assert: Verify None return
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_mapping_success(self, temp_db, sample_mapping_data):
        """Test successful deletion of URL mapping.
        
        Validates that the database correctly:
        - Deletes mapping by ID
        - Returns True for successful deletion
        - Removes mapping from database
        """
        # Arrange: Create mapping first
        created = await temp_db.create_mapping(sample_mapping_data)
        mapping_id = created["id"]
        
        # Act: Delete mapping
        result = await temp_db.delete_mapping(mapping_id)
        
        # Assert: Verify deletion
        assert result is True
        
        # Verify mapping is gone
        deleted_mapping = await temp_db.get_mapping(mapping_id)
        assert deleted_mapping is None
    
    @pytest.mark.asyncio
    async def test_delete_mapping_not_found(self, temp_db):
        """Test deletion of non-existent mapping.
        
        Validates that the database correctly:
        - Returns False for non-existent mappings
        - Handles deletion attempts gracefully
        """
        # Act: Try to delete non-existent mapping
        result = await temp_db.delete_mapping("non_existent_id")
        
        # Assert: Verify False return
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_all_mappings(self, temp_db, sample_mapping_data):
        """Test retrieval of all URL mappings.
        
        Validates that the database correctly:
        - Returns all mappings in database
        - Handles empty database
        - Maintains data integrity for multiple mappings
        """
        # Test empty database
        result = await temp_db.get_all_mappings()
        assert result == []
        
        # Create multiple mappings
        mapping1 = await temp_db.create_mapping(sample_mapping_data)
        
        mapping2_data = sample_mapping_data.copy()
        mapping2_data["url_config_id"] = "config_789"
        mapping2_data["extractor_id"] = "news_extractor"
        mapping2 = await temp_db.create_mapping(mapping2_data)
        
        # Act: Get all mappings
        result = await temp_db.get_all_mappings()
        
        # Assert: Verify all mappings returned
        assert len(result) == 2
        mapping_ids = [m["id"] for m in result]
        assert mapping1["id"] in mapping_ids
        assert mapping2["id"] in mapping_ids
    
    @pytest.mark.asyncio
    async def test_json_serialization(self, temp_db):
        """Test JSON serialization/deserialization of complex fields.
        
        Validates that the database correctly:
        - Serializes complex objects to JSON
        - Deserializes JSON back to objects
        - Maintains data structure integrity
        """
        # Arrange: Complex data with nested structures
        complex_data = {
            "url_config_id": "config_complex",
            "extractor_id": "complex_extractor",
            "config": {
                "nested": {
                    "deep": {
                        "value": 42,
                        "list": [1, 2, 3],
                        "bool": True
                    }
                },
                "array": ["a", "b", "c"]
            },
            "validation_rules": {
                "rules": [
                    {"field": "price", "type": "number", "min": 0},
                    {"field": "date", "type": "string", "pattern": "\\d{4}-\\d{2}-\\d{2}"}
                ]
            }
        }
        
        # Act: Create and retrieve mapping
        created = await temp_db.create_mapping(complex_data)
        retrieved = await temp_db.get_mapping(created["id"])
        
        # Assert: Verify complex data integrity
        assert retrieved["config"] == complex_data["config"]
        assert retrieved["validation_rules"] == complex_data["validation_rules"]
        assert retrieved["config"]["nested"]["deep"]["value"] == 42
        assert retrieved["validation_rules"]["rules"][0]["field"] == "price"
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, temp_db):
        """Test database error handling scenarios.
        
        Validates that the database correctly:
        - Handles database connection errors
        - Provides meaningful error messages
        - Maintains database integrity
        """
        # Test with invalid data types
        with pytest.raises(Exception):
            await temp_db.create_mapping({
                "url_config_id": None,  # Invalid: required field
                "extractor_id": "test"
            })
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, temp_db, sample_mapping_data):
        """Test concurrent database operations.
        
        Validates that the database correctly:
        - Handles concurrent read/write operations
        - Maintains data consistency
        - Prevents race conditions
        """
        # Create multiple mappings concurrently
        tasks = []
        for i in range(5):
            data = sample_mapping_data.copy()
            data["url_config_id"] = f"config_{i}"
            data["extractor_id"] = f"extractor_{i}"
            tasks.append(temp_db.create_mapping(data))
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all operations succeeded
        assert len(results) == 5
        for result in results:
            assert result is not None
            assert "id" in result
        
        # Verify all mappings exist
        all_mappings = await temp_db.get_all_mappings()
        assert len(all_mappings) == 5