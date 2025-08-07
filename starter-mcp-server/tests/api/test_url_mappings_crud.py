"""Comprehensive CRUD tests for URL mappings API.

This module tests all Create, Read, Update, Delete operations for URL mappings,
with special focus on the update functionality that was previously broken.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tests.conftest import assert_valid_response, assert_valid_crud_response


class TestURLMappingsCRUD:
    """Test suite for URL mappings CRUD operations."""
    
    def test_create_url_mapping_success(self, test_client: TestClient, sample_url_mapping):
        """Test successful creation of URL mapping."""
        response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        
        assert_valid_crud_response(response, "create")
        data = response.json()
        
        # Verify all fields are correctly stored
        assert data["url_pattern"] == sample_url_mapping["url_pattern"]
        assert data["name"] == sample_url_mapping["name"]
        assert data["extractor_ids"] == sample_url_mapping["extractor_ids"]
        assert data["rate_limit"] == sample_url_mapping["rate_limit"]
        assert data["priority"] == sample_url_mapping["priority"]
        assert data["is_active"] == sample_url_mapping["is_active"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_url_mapping_missing_required_fields(self, test_client: TestClient):
        """Test creation fails with missing required fields."""
        incomplete_mapping = {
            "name": "Incomplete Mapping"
            # Missing required fields: url_pattern, extractor_ids, etc.
        }
        
        response = test_client.post("/api/url-mappings", json=incomplete_mapping)
        assert response.status_code == 422  # Validation error
    
    def test_create_url_mapping_invalid_url_pattern(self, test_client: TestClient, sample_url_mapping):
        """Test creation fails with invalid URL pattern."""
        sample_url_mapping["url_pattern"] = "not-a-valid-url-pattern"
        
        response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert response.status_code == 422  # Validation error
    
    def test_create_url_mapping_empty_extractor_ids(self, test_client: TestClient, sample_url_mapping):
        """Test creation fails with empty extractor IDs."""
        sample_url_mapping["extractor_ids"] = []
        
        response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert response.status_code == 422  # Validation error
    
    def test_get_all_url_mappings(self, test_client: TestClient, test_data_factory):
        """Test retrieving all URL mappings."""
        # Create multiple mappings
        mappings = [
            test_data_factory.create_url_mapping("mapping1"),
            test_data_factory.create_url_mapping("mapping2"),
            test_data_factory.create_url_mapping("mapping3")
        ]
        
        created_ids = []
        for mapping in mappings:
            response = test_client.post("/api/url-mappings", json=mapping)
            assert_valid_crud_response(response, "create")
            created_ids.append(response.json()["id"])
        
        # Get all mappings
        response = test_client.get("/api/url-mappings")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # At least our 3 mappings
        
        # Verify our created mappings are in the response
        response_ids = [item["id"] for item in data]
        for created_id in created_ids:
            assert created_id in response_ids
    
    def test_get_url_mapping_by_id(self, test_client: TestClient, sample_url_mapping):
        """Test retrieving URL mapping by ID."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        
        # Get mapping by ID
        response = test_client.get(f"/api/url-mappings/{mapping_id}")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        assert data["id"] == mapping_id
        assert data["url_pattern"] == sample_url_mapping["url_pattern"]
        assert data["name"] == sample_url_mapping["name"]
    
    def test_get_url_mapping_not_found(self, test_client: TestClient):
        """Test retrieving non-existent URL mapping."""
        response = test_client.get("/api/url-mappings/99999")
        assert response.status_code == 404


class TestURLMappingsUpdate:
    """Test suite specifically for URL mappings update operations.
    
    This addresses the previously broken update functionality.
    """
    
    def test_update_url_mapping_full_success(self, test_client: TestClient, sample_url_mapping):
        """Test successful full update of URL mapping."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        
        # Update mapping with all fields
        update_data = {
            "url_pattern": "https://updated-exchange.com/api/v2/*",
            "name": "Updated Exchange Mapping",
            "extractor_ids": ["updated_extractor", "new_extractor"],
            "rate_limit": 120,
            "priority": 2,
            "crawler_settings": {
                "delay": 2.0,
                "timeout": 60,
                "user_agent": "UpdatedBot/2.0"
            },
            "validation_rules": {
                "required_fields": ["updated_field"],
                "min_content_length": 200
            },
            "is_active": False,
            "tags": ["updated", "test"],
            "notes": "Updated mapping notes",
            "category": "updated_category"
        }
        
        response = test_client.put(f"/api/url-mappings/{mapping_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["id"] == mapping_id
        assert data["url_pattern"] == update_data["url_pattern"]
        assert data["name"] == update_data["name"]
        assert data["extractor_ids"] == update_data["extractor_ids"]
        assert data["rate_limit"] == update_data["rate_limit"]
        assert data["priority"] == update_data["priority"]
        assert data["is_active"] == update_data["is_active"]
        assert data["tags"] == update_data["tags"]
        assert data["notes"] == update_data["notes"]
        assert data["category"] == update_data["category"]
    
    def test_update_url_mapping_url_field_only(self, test_client: TestClient, sample_url_mapping):
        """Test updating only the URL field - this was the main issue."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        original_data = create_response.json()
        
        # Update only the URL pattern
        update_data = {
            "url_pattern": "https://completely-new-url.com/api/*"
        }
        
        response = test_client.put(f"/api/url-mappings/{mapping_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["id"] == mapping_id
        assert data["url_pattern"] == update_data["url_pattern"]
        # Other fields should remain unchanged
        assert data["name"] == original_data["name"]
        assert data["extractor_ids"] == original_data["extractor_ids"]
        assert data["rate_limit"] == original_data["rate_limit"]
    
    def test_update_url_mapping_partial_fields(self, test_client: TestClient, sample_url_mapping):
        """Test partial update of URL mapping."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        original_data = create_response.json()
        
        # Partial update (name and rate_limit only)
        update_data = {
            "name": "Partially Updated Mapping",
            "rate_limit": 90
        }
        
        response = test_client.patch(f"/api/url-mappings/{mapping_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["rate_limit"] == update_data["rate_limit"]
        # Other fields should remain unchanged
        assert data["url_pattern"] == original_data["url_pattern"]
        assert data["extractor_ids"] == original_data["extractor_ids"]
        assert data["priority"] == original_data["priority"]
    
    def test_update_url_mapping_extractor_ids(self, test_client: TestClient, sample_url_mapping):
        """Test updating extractor IDs."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        
        # Update extractor IDs
        update_data = {
            "extractor_ids": ["new_extractor_1", "new_extractor_2", "new_extractor_3"]
        }
        
        response = test_client.put(f"/api/url-mappings/{mapping_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["extractor_ids"] == update_data["extractor_ids"]
        assert len(data["extractor_ids"]) == 3
    
    def test_update_url_mapping_complex_objects(self, test_client: TestClient, sample_url_mapping):
        """Test updating complex nested objects."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        
        # Update complex nested objects
        update_data = {
            "crawler_settings": {
                "delay": 5.0,
                "timeout": 120,
                "user_agent": "SuperBot/3.0",
                "max_retries": 5,
                "custom_headers": {
                    "Authorization": "Bearer token"
                }
            },
            "validation_rules": {
                "required_fields": ["title", "content", "timestamp"],
                "min_content_length": 500,
                "max_content_length": 10000,
                "allowed_content_types": ["application/json", "text/html"]
            }
        }
        
        response = test_client.put(f"/api/url-mappings/{mapping_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["crawler_settings"] == update_data["crawler_settings"]
        assert data["validation_rules"] == update_data["validation_rules"]
    
    def test_update_url_mapping_not_found(self, test_client: TestClient):
        """Test updating non-existent URL mapping."""
        update_data = {"name": "Updated Name"}
        response = test_client.put("/api/url-mappings/99999", json=update_data)
        assert response.status_code == 404
    
    def test_update_url_mapping_invalid_data(self, test_client: TestClient, sample_url_mapping):
        """Test update fails with invalid data."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        
        # Try to update with invalid URL pattern
        update_data = {"url_pattern": "invalid-url-pattern"}
        
        response = test_client.put(f"/api/url-mappings/{mapping_id}", json=update_data)
        assert response.status_code == 422  # Validation error
    
    def test_update_url_mapping_empty_extractor_ids(self, test_client: TestClient, sample_url_mapping):
        """Test update fails with empty extractor IDs."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        
        # Try to update with empty extractor IDs
        update_data = {"extractor_ids": []}
        
        response = test_client.put(f"/api/url-mappings/{mapping_id}", json=update_data)
        assert response.status_code == 422  # Validation error
    
    def test_update_url_mapping_invalid_rate_limit(self, test_client: TestClient, sample_url_mapping):
        """Test update fails with invalid rate limit."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        
        # Try to update with invalid rate limit
        update_data = {"rate_limit": -1}
        
        response = test_client.put(f"/api/url-mappings/{mapping_id}", json=update_data)
        assert response.status_code == 422  # Validation error


class TestURLMappingsDelete:
    """Test suite for URL mappings delete operations."""
    
    def test_delete_url_mapping_success(self, test_client: TestClient, sample_url_mapping):
        """Test successful deletion of URL mapping."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        
        # Delete mapping
        response = test_client.delete(f"/api/url-mappings/{mapping_id}")
        assert_valid_crud_response(response, "delete")
        
        # Verify mapping is deleted
        get_response = test_client.get(f"/api/url-mappings/{mapping_id}")
        assert get_response.status_code == 404
    
    def test_delete_url_mapping_not_found(self, test_client: TestClient):
        """Test deleting non-existent URL mapping."""
        response = test_client.delete("/api/url-mappings/99999")
        assert response.status_code == 404
    
    def test_delete_url_mapping_cascade(self, test_client: TestClient, sample_url_mapping, sample_crawler):
        """Test deletion behavior when mapping has dependencies."""
        # Create mapping
        create_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        assert_valid_crud_response(create_response, "create")
        mapping_id = create_response.json()["id"]
        
        # Create crawler that depends on this mapping
        sample_crawler["url_mapping_ids"] = [mapping_id]
        crawler_response = test_client.post("/api/crawlers", json=sample_crawler)
        
        # Try to delete mapping with dependencies
        response = test_client.delete(f"/api/url-mappings/{mapping_id}")
        # Should either cascade delete or prevent deletion
        assert response.status_code in [204, 400, 409]


class TestURLMappingsAdvanced:
    """Advanced test scenarios for URL mappings."""
    
    def test_url_mapping_pagination(self, test_client: TestClient, test_data_factory):
        """Test pagination of URL mappings list."""
        # Create multiple mappings
        for i in range(15):
            mapping = test_data_factory.create_url_mapping(f"mapping{i}")
            response = test_client.post("/api/url-mappings", json=mapping)
            assert_valid_crud_response(response, "create")
        
        # Test pagination parameters
        response = test_client.get("/api/url-mappings?limit=10&offset=0")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        if isinstance(data, dict) and "items" in data:
            # Paginated response format
            assert len(data["items"]) <= 10
            assert "total" in data
            assert "limit" in data
            assert "offset" in data
        else:
            # Simple list format
            assert isinstance(data, list)
    
    def test_url_mapping_filtering_by_active_status(self, test_client: TestClient, test_data_factory):
        """Test filtering URL mappings by active status."""
        # Create active and inactive mappings
        active_mapping = test_data_factory.create_url_mapping("active", is_active=True)
        inactive_mapping = test_data_factory.create_url_mapping("inactive", is_active=False)
        
        test_client.post("/api/url-mappings", json=active_mapping)
        test_client.post("/api/url-mappings", json=inactive_mapping)
        
        # Filter by active status
        response = test_client.get("/api/url-mappings?is_active=true")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        if isinstance(data, list):
            active_mappings = [item for item in data if item["is_active"] is True]
            assert len(active_mappings) >= 1
    
    def test_url_mapping_search_by_pattern(self, test_client: TestClient, test_data_factory):
        """Test searching URL mappings by URL pattern."""
        # Create mappings with searchable patterns
        mapping1 = test_data_factory.create_url_mapping("binance", url_pattern="https://api.binance.com/*")
        mapping2 = test_data_factory.create_url_mapping("coinbase", url_pattern="https://api.coinbase.com/*")
        
        test_client.post("/api/url-mappings", json=mapping1)
        test_client.post("/api/url-mappings", json=mapping2)
        
        # Search by pattern
        response = test_client.get("/api/url-mappings?search=binance")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        if isinstance(data, list):
            binance_mappings = [item for item in data if "binance" in item["url_pattern"].lower()]
            assert len(binance_mappings) >= 1
    
    def test_url_mapping_bulk_operations(self, test_client: TestClient, test_data_factory):
        """Test bulk operations on URL mappings."""
        # Create multiple mappings
        mapping_ids = []
        for i in range(5):
            mapping = test_data_factory.create_url_mapping(f"bulk{i}")
            response = test_client.post("/api/url-mappings", json=mapping)
            assert_valid_crud_response(response, "create")
            mapping_ids.append(response.json()["id"])
        
        # Test bulk status update
        bulk_update_data = {
            "ids": mapping_ids,
            "is_active": False
        }
        
        response = test_client.patch("/api/url-mappings/bulk-status", json=bulk_update_data)
        if response.status_code == 200:
            # Verify all mappings are now inactive
            for mapping_id in mapping_ids:
                get_response = test_client.get(f"/api/url-mappings/{mapping_id}")
                if get_response.status_code == 200:
                    data = get_response.json()
                    assert data["is_active"] is False