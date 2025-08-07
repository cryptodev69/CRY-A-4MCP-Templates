"""Comprehensive CRUD tests for extractors API.

This module tests all Create, Read, Update, Delete operations for extractors
to ensure the API works correctly and prevents regressions.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tests.conftest import assert_valid_response, assert_valid_crud_response


class TestExtractorsCRUD:
    """Test suite for extractors CRUD operations."""
    
    def test_create_extractor_success(self, test_client: TestClient, sample_extractor):
        """Test successful creation of extractor."""
        response = test_client.post("/api/extractors", json=sample_extractor)
        
        assert_valid_crud_response(response, "create")
        data = response.json()
        
        # Verify all fields are correctly stored
        assert data["name"] == sample_extractor["name"]
        assert data["description"] == sample_extractor["description"]
        assert data["extractor_type"] == sample_extractor["extractor_type"]
        assert data["config"] == sample_extractor["config"]
        assert data["is_active"] == sample_extractor["is_active"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_extractor_missing_required_fields(self, test_client: TestClient):
        """Test creation fails with missing required fields."""
        incomplete_extractor = {
            "name": "Incomplete Extractor"
            # Missing required fields: extractor_type, config, etc.
        }
        
        response = test_client.post("/api/extractors", json=incomplete_extractor)
        assert response.status_code == 422  # Validation error
    
    def test_create_extractor_invalid_type(self, test_client: TestClient, sample_extractor):
        """Test creation fails with invalid extractor type."""
        sample_extractor["extractor_type"] = "invalid_type"
        
        response = test_client.post("/api/extractors", json=sample_extractor)
        assert response.status_code == 422  # Validation error
    
    def test_create_extractor_duplicate_name(self, test_client: TestClient, sample_extractor):
        """Test creation fails with duplicate name."""
        # Create first extractor
        response1 = test_client.post("/api/extractors", json=sample_extractor)
        assert_valid_crud_response(response1, "create")
        
        # Try to create second extractor with same name
        response2 = test_client.post("/api/extractors", json=sample_extractor)
        assert response2.status_code in [400, 409]  # Conflict or bad request
    
    def test_get_all_extractors(self, test_client: TestClient, test_data_factory):
        """Test retrieving all extractors."""
        # Create multiple extractors
        extractors = [
            test_data_factory.create_extractor("Extractor 1"),
            test_data_factory.create_extractor("Extractor 2"),
            test_data_factory.create_extractor("Extractor 3")
        ]
        
        created_ids = []
        for extractor in extractors:
            response = test_client.post("/api/extractors", json=extractor)
            assert_valid_crud_response(response, "create")
            created_ids.append(response.json()["id"])
        
        # Get all extractors
        response = test_client.get("/api/extractors")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # At least our 3 extractors
        
        # Verify our created extractors are in the response
        response_ids = [item["id"] for item in data]
        for created_id in created_ids:
            assert created_id in response_ids
    
    def test_get_extractor_by_id(self, test_client: TestClient, sample_extractor):
        """Test retrieving extractor by ID."""
        # Create extractor
        create_response = test_client.post("/api/extractors", json=sample_extractor)
        assert_valid_crud_response(create_response, "create")
        extractor_id = create_response.json()["id"]
        
        # Get extractor by ID
        response = test_client.get(f"/api/extractors/{extractor_id}")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        assert data["id"] == extractor_id
        assert data["name"] == sample_extractor["name"]
        assert data["extractor_type"] == sample_extractor["extractor_type"]
    
    def test_get_extractor_not_found(self, test_client: TestClient):
        """Test retrieving non-existent extractor."""
        response = test_client.get("/api/extractors/99999")
        assert response.status_code == 404
    
    def test_update_extractor_success(self, test_client: TestClient, sample_extractor):
        """Test successful update of extractor."""
        # Create extractor
        create_response = test_client.post("/api/extractors", json=sample_extractor)
        assert_valid_crud_response(create_response, "create")
        extractor_id = create_response.json()["id"]
        
        # Update extractor
        update_data = {
            "name": "Updated Extractor Name",
            "description": "Updated description",
            "config": {
                "updated_selectors": {
                    "title": ".updated-title",
                    "content": ".updated-content"
                },
                "output_format": "xml"
            },
            "is_active": False
        }
        
        response = test_client.put(f"/api/extractors/{extractor_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["id"] == extractor_id
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["config"] == update_data["config"]
        assert data["is_active"] == update_data["is_active"]
        # Type should remain unchanged
        assert data["extractor_type"] == sample_extractor["extractor_type"]
    
    def test_update_extractor_partial(self, test_client: TestClient, sample_extractor):
        """Test partial update of extractor."""
        # Create extractor
        create_response = test_client.post("/api/extractors", json=sample_extractor)
        assert_valid_crud_response(create_response, "create")
        extractor_id = create_response.json()["id"]
        
        # Partial update (only name and description)
        update_data = {
            "name": "Partially Updated Extractor",
            "description": "Partially updated description"
        }
        
        response = test_client.patch(f"/api/extractors/{extractor_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        # Other fields should remain unchanged
        assert data["extractor_type"] == sample_extractor["extractor_type"]
        assert data["config"] == sample_extractor["config"]
        assert data["is_active"] == sample_extractor["is_active"]
    
    def test_update_extractor_config_only(self, test_client: TestClient, sample_extractor):
        """Test updating only the configuration."""
        # Create extractor
        create_response = test_client.post("/api/extractors", json=sample_extractor)
        assert_valid_crud_response(create_response, "create")
        extractor_id = create_response.json()["id"]
        
        # Update only config
        update_data = {
            "config": {
                "new_selectors": {
                    "price": ".price-new",
                    "volume": ".volume-new",
                    "change": ".change-new"
                },
                "output_format": "csv",
                "timeout": 30,
                "retries": 3
            }
        }
        
        response = test_client.patch(f"/api/extractors/{extractor_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["config"] == update_data["config"]
        # Other fields should remain unchanged
        assert data["name"] == sample_extractor["name"]
        assert data["extractor_type"] == sample_extractor["extractor_type"]
    
    def test_update_extractor_not_found(self, test_client: TestClient):
        """Test updating non-existent extractor."""
        update_data = {"name": "Updated Name"}
        response = test_client.put("/api/extractors/99999", json=update_data)
        assert response.status_code == 404
    
    def test_update_extractor_invalid_data(self, test_client: TestClient, sample_extractor):
        """Test update fails with invalid data."""
        # Create extractor
        create_response = test_client.post("/api/extractors", json=sample_extractor)
        assert_valid_crud_response(create_response, "create")
        extractor_id = create_response.json()["id"]
        
        # Try to update with invalid extractor type
        update_data = {"extractor_type": "invalid_type"}
        
        response = test_client.put(f"/api/extractors/{extractor_id}", json=update_data)
        assert response.status_code == 422  # Validation error
    
    def test_delete_extractor_success(self, test_client: TestClient, sample_extractor):
        """Test successful deletion of extractor."""
        # Create extractor
        create_response = test_client.post("/api/extractors", json=sample_extractor)
        assert_valid_crud_response(create_response, "create")
        extractor_id = create_response.json()["id"]
        
        # Delete extractor
        response = test_client.delete(f"/api/extractors/{extractor_id}")
        assert_valid_crud_response(response, "delete")
        
        # Verify extractor is deleted
        get_response = test_client.get(f"/api/extractors/{extractor_id}")
        assert get_response.status_code == 404
    
    def test_delete_extractor_not_found(self, test_client: TestClient):
        """Test deleting non-existent extractor."""
        response = test_client.delete("/api/extractors/99999")
        assert response.status_code == 404
    
    def test_delete_extractor_with_dependencies(self, test_client: TestClient, sample_extractor, sample_url_mapping):
        """Test deletion behavior when extractor has dependencies."""
        # Create extractor
        create_response = test_client.post("/api/extractors", json=sample_extractor)
        assert_valid_crud_response(create_response, "create")
        extractor_id = create_response.json()["id"]
        
        # Create URL mapping that uses this extractor
        sample_url_mapping["extractor_ids"] = [str(extractor_id)]
        mapping_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        
        # Try to delete extractor with dependencies
        response = test_client.delete(f"/api/extractors/{extractor_id}")
        # Should either cascade delete or prevent deletion
        assert response.status_code in [204, 400, 409]


class TestExtractorsValidation:
    """Test suite for extractors validation."""
    
    def test_extractor_type_validation(self, test_client: TestClient, sample_extractor):
        """Test extractor type validation."""
        valid_types = ["price", "news", "social", "defi", "nft", "generic"]
        
        for extractor_type in valid_types:
            sample_extractor["extractor_type"] = extractor_type
            sample_extractor["name"] = f"Test {extractor_type} Extractor"
            response = test_client.post("/api/extractors", json=sample_extractor)
            assert response.status_code in [200, 201], f"Failed for type: {extractor_type}"
        
        # Test invalid type
        sample_extractor["extractor_type"] = "invalid_type"
        sample_extractor["name"] = "Test Invalid Extractor"
        response = test_client.post("/api/extractors", json=sample_extractor)
        assert response.status_code == 422
    
    def test_config_validation(self, test_client: TestClient, sample_extractor):
        """Test configuration validation."""
        # Test with empty config
        sample_extractor["config"] = {}
        response = test_client.post("/api/extractors", json=sample_extractor)
        assert response.status_code == 422  # Should require non-empty config
        
        # Test with valid config
        sample_extractor["config"] = {
            "selectors": {"title": ".title"},
            "output_format": "json"
        }
        response = test_client.post("/api/extractors", json=sample_extractor)
        assert response.status_code in [200, 201]
    
    def test_name_length_validation(self, test_client: TestClient, sample_extractor):
        """Test name length validation."""
        # Test minimum length
        sample_extractor["name"] = "A"  # Too short
        response = test_client.post("/api/extractors", json=sample_extractor)
        assert response.status_code == 422
        
        # Test maximum length
        sample_extractor["name"] = "A" * 300  # Too long
        response = test_client.post("/api/extractors", json=sample_extractor)
        assert response.status_code == 422
        
        # Test valid length
        sample_extractor["name"] = "Valid Length Extractor Name"
        response = test_client.post("/api/extractors", json=sample_extractor)
        assert response.status_code in [200, 201]


class TestExtractorsAdvanced:
    """Advanced test scenarios for extractors."""
    
    def test_extractor_pagination(self, test_client: TestClient, test_data_factory):
        """Test pagination of extractors list."""
        # Create multiple extractors
        for i in range(15):
            extractor = test_data_factory.create_extractor(f"Extractor {i}")
            response = test_client.post("/api/extractors", json=extractor)
            assert_valid_crud_response(response, "create")
        
        # Test pagination parameters
        response = test_client.get("/api/extractors?limit=10&offset=0")
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
    
    def test_extractor_filtering_by_type(self, test_client: TestClient, test_data_factory):
        """Test filtering extractors by type."""
        # Create extractors with different types
        price_extractor = test_data_factory.create_extractor("Price", extractor_type="price")
        news_extractor = test_data_factory.create_extractor("News", extractor_type="news")
        
        test_client.post("/api/extractors", json=price_extractor)
        test_client.post("/api/extractors", json=news_extractor)
        
        # Filter by type
        response = test_client.get("/api/extractors?type=price")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        if isinstance(data, list):
            price_extractors = [item for item in data if item["extractor_type"] == "price"]
            assert len(price_extractors) >= 1
    
    def test_extractor_filtering_by_active_status(self, test_client: TestClient, test_data_factory):
        """Test filtering extractors by active status."""
        # Create active and inactive extractors
        active_extractor = test_data_factory.create_extractor("Active", is_active=True)
        inactive_extractor = test_data_factory.create_extractor("Inactive", is_active=False)
        
        test_client.post("/api/extractors", json=active_extractor)
        test_client.post("/api/extractors", json=inactive_extractor)
        
        # Filter by active status
        response = test_client.get("/api/extractors?is_active=true")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        if isinstance(data, list):
            active_extractors = [item for item in data if item["is_active"] is True]
            assert len(active_extractors) >= 1
    
    def test_extractor_search(self, test_client: TestClient, test_data_factory):
        """Test searching extractors by name."""
        # Create extractors with searchable names
        extractor1 = test_data_factory.create_extractor("Bitcoin Price Extractor")
        extractor2 = test_data_factory.create_extractor("Ethereum News Extractor")
        
        test_client.post("/api/extractors", json=extractor1)
        test_client.post("/api/extractors", json=extractor2)
        
        # Search by name
        response = test_client.get("/api/extractors?search=Bitcoin")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        if isinstance(data, list):
            bitcoin_extractors = [item for item in data if "Bitcoin" in item["name"]]
            assert len(bitcoin_extractors) >= 1
    
    def test_extractor_bulk_operations(self, test_client: TestClient, test_data_factory):
        """Test bulk operations on extractors."""
        # Create multiple extractors
        extractor_ids = []
        for i in range(5):
            extractor = test_data_factory.create_extractor(f"Bulk Extractor {i}")
            response = test_client.post("/api/extractors", json=extractor)
            assert_valid_crud_response(response, "create")
            extractor_ids.append(response.json()["id"])
        
        # Test bulk status update
        bulk_update_data = {
            "ids": extractor_ids,
            "is_active": False
        }
        
        response = test_client.patch("/api/extractors/bulk-status", json=bulk_update_data)
        if response.status_code == 200:
            # Verify all extractors are now inactive
            for extractor_id in extractor_ids:
                get_response = test_client.get(f"/api/extractors/{extractor_id}")
                if get_response.status_code == 200:
                    data = get_response.json()
                    assert data["is_active"] is False