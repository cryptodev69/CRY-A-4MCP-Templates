"""Comprehensive CRUD tests for URL configurations API.

This module tests all Create, Read, Update, Delete operations for URL configurations
to ensure the API works correctly and prevents regressions.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tests.conftest import assert_valid_response, assert_valid_crud_response


class TestURLConfigurationsCRUD:
    """Test suite for URL configurations CRUD operations."""
    
    def test_create_url_config_success(self, test_client: TestClient, sample_url_config):
        """Test successful creation of URL configuration."""
        response = test_client.post("/api/url-configs", json=sample_url_config)
        
        assert_valid_crud_response(response, "create")
        data = response.json()
        
        # Verify all fields are correctly stored
        assert data["name"] == sample_url_config["name"]
        assert data["url"] == sample_url_config["url"]
        assert data["description"] == sample_url_config["description"]
        assert data["category"] == sample_url_config["category"]
        assert data["is_active"] == sample_url_config["is_active"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_url_config_missing_required_fields(self, test_client: TestClient):
        """Test creation fails with missing required fields."""
        incomplete_config = {
            "name": "Incomplete Config"
            # Missing required fields: url, category, etc.
        }
        
        response = test_client.post("/api/url-configs", json=incomplete_config)
        assert response.status_code == 422  # Validation error
    
    def test_create_url_config_invalid_url(self, test_client: TestClient, sample_url_config):
        """Test creation fails with invalid URL format."""
        sample_url_config["url"] = "not-a-valid-url"
        
        response = test_client.post("/api/url-configs", json=sample_url_config)
        assert response.status_code == 422  # Validation error
    
    def test_create_url_config_duplicate_name(self, test_client: TestClient, sample_url_config):
        """Test creation fails with duplicate name."""
        # Create first config
        response1 = test_client.post("/api/url-configs", json=sample_url_config)
        assert_valid_crud_response(response1, "create")
        
        # Try to create second config with same name
        response2 = test_client.post("/api/url-configs", json=sample_url_config)
        assert response2.status_code in [400, 409]  # Conflict or bad request
    
    def test_get_all_url_configs(self, test_client: TestClient, test_data_factory):
        """Test retrieving all URL configurations."""
        # Create multiple configs
        configs = [
            test_data_factory.create_url_config("Config 1"),
            test_data_factory.create_url_config("Config 2"),
            test_data_factory.create_url_config("Config 3")
        ]
        
        created_ids = []
        for config in configs:
            response = test_client.post("/api/url-configs", json=config)
            assert_valid_crud_response(response, "create")
            created_ids.append(response.json()["id"])
        
        # Get all configs
        response = test_client.get("/api/url-configs")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # At least our 3 configs
        
        # Verify our created configs are in the response
        response_ids = [item["id"] for item in data]
        for created_id in created_ids:
            assert created_id in response_ids
    
    def test_get_url_config_by_id(self, test_client: TestClient, sample_url_config):
        """Test retrieving URL configuration by ID."""
        # Create config
        create_response = test_client.post("/api/url-configs", json=sample_url_config)
        assert_valid_crud_response(create_response, "create")
        config_id = create_response.json()["id"]
        
        # Get config by ID
        response = test_client.get(f"/api/url-configs/{config_id}")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        assert data["id"] == config_id
        assert data["name"] == sample_url_config["name"]
        assert data["url"] == sample_url_config["url"]
    
    def test_get_url_config_not_found(self, test_client: TestClient):
        """Test retrieving non-existent URL configuration."""
        response = test_client.get("/api/url-configs/99999")
        assert response.status_code == 404
    
    def test_update_url_config_success(self, test_client: TestClient, sample_url_config):
        """Test successful update of URL configuration."""
        # Create config
        create_response = test_client.post("/api/url-configs", json=sample_url_config)
        assert_valid_crud_response(create_response, "create")
        config_id = create_response.json()["id"]
        
        # Update config
        update_data = {
            "name": "Updated Config Name",
            "description": "Updated description",
            "is_active": False
        }
        
        response = test_client.put(f"/api/url-configs/{config_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["id"] == config_id
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["is_active"] == update_data["is_active"]
        # URL should remain unchanged
        assert data["url"] == sample_url_config["url"]
    
    def test_update_url_config_partial(self, test_client: TestClient, sample_url_config):
        """Test partial update of URL configuration."""
        # Create config
        create_response = test_client.post("/api/url-configs", json=sample_url_config)
        assert_valid_crud_response(create_response, "create")
        config_id = create_response.json()["id"]
        
        # Partial update (only name)
        update_data = {"name": "Partially Updated Name"}
        
        response = test_client.patch(f"/api/url-configs/{config_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["name"] == update_data["name"]
        # Other fields should remain unchanged
        assert data["url"] == sample_url_config["url"]
        assert data["description"] == sample_url_config["description"]
    
    def test_update_url_config_not_found(self, test_client: TestClient):
        """Test updating non-existent URL configuration."""
        update_data = {"name": "Updated Name"}
        response = test_client.put("/api/url-configs/99999", json=update_data)
        assert response.status_code == 404
    
    def test_update_url_config_invalid_data(self, test_client: TestClient, sample_url_config):
        """Test update fails with invalid data."""
        # Create config
        create_response = test_client.post("/api/url-configs", json=sample_url_config)
        assert_valid_crud_response(create_response, "create")
        config_id = create_response.json()["id"]
        
        # Try to update with invalid URL
        update_data = {"url": "invalid-url-format"}
        
        response = test_client.put(f"/api/url-configs/{config_id}", json=update_data)
        assert response.status_code == 422  # Validation error
    
    def test_delete_url_config_success(self, test_client: TestClient, sample_url_config):
        """Test successful deletion of URL configuration."""
        # Create config
        create_response = test_client.post("/api/url-configs", json=sample_url_config)
        assert_valid_crud_response(create_response, "create")
        config_id = create_response.json()["id"]
        
        # Delete config
        response = test_client.delete(f"/api/url-configs/{config_id}")
        assert_valid_crud_response(response, "delete")
        
        # Verify config is deleted
        get_response = test_client.get(f"/api/url-configs/{config_id}")
        assert get_response.status_code == 404
    
    def test_delete_url_config_not_found(self, test_client: TestClient):
        """Test deleting non-existent URL configuration."""
        response = test_client.delete("/api/url-configs/99999")
        assert response.status_code == 404
    
    def test_delete_url_config_with_dependencies(self, test_client: TestClient, sample_url_config, sample_url_mapping):
        """Test deletion behavior when config has dependencies."""
        # Create config
        create_response = test_client.post("/api/url-configs", json=sample_url_config)
        assert_valid_crud_response(create_response, "create")
        config_id = create_response.json()["id"]
        
        # Create mapping that depends on this config
        sample_url_mapping["url_config_id"] = config_id
        mapping_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        
        # Try to delete config with dependencies
        response = test_client.delete(f"/api/url-configs/{config_id}")
        # Should either cascade delete or prevent deletion
        assert response.status_code in [204, 400, 409]
    
    def test_url_config_pagination(self, test_client: TestClient, test_data_factory):
        """Test pagination of URL configurations list."""
        # Create multiple configs
        for i in range(15):
            config = test_data_factory.create_url_config(f"Config {i}")
            response = test_client.post("/api/url-configs", json=config)
            assert_valid_crud_response(response, "create")
        
        # Test pagination parameters
        response = test_client.get("/api/url-configs?limit=10&offset=0")
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
    
    def test_url_config_filtering(self, test_client: TestClient, test_data_factory):
        """Test filtering URL configurations by category."""
        # Create configs with different categories
        news_config = test_data_factory.create_url_config("News", category="news")
        exchange_config = test_data_factory.create_url_config("Exchange", category="exchange")
        
        test_client.post("/api/url-configs", json=news_config)
        test_client.post("/api/url-configs", json=exchange_config)
        
        # Filter by category
        response = test_client.get("/api/url-configs?category=news")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        if isinstance(data, list):
            news_configs = [item for item in data if item["category"] == "news"]
            assert len(news_configs) >= 1
    
    def test_url_config_search(self, test_client: TestClient, test_data_factory):
        """Test searching URL configurations by name."""
        # Create configs with searchable names
        config1 = test_data_factory.create_url_config("Bitcoin News Source")
        config2 = test_data_factory.create_url_config("Ethereum Exchange")
        
        test_client.post("/api/url-configs", json=config1)
        test_client.post("/api/url-configs", json=config2)
        
        # Search by name
        response = test_client.get("/api/url-configs?search=Bitcoin")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        if isinstance(data, list):
            bitcoin_configs = [item for item in data if "Bitcoin" in item["name"]]
            assert len(bitcoin_configs) >= 1


class TestURLConfigurationsValidation:
    """Test suite for URL configurations validation."""
    
    def test_url_validation_schemes(self, test_client: TestClient, sample_url_config):
        """Test URL validation for different schemes."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://subdomain.example.com/path",
            "https://example.com:8080/api/v1"
        ]
        
        for url in valid_urls:
            sample_url_config["url"] = url
            sample_url_config["name"] = f"Test {url}"
            response = test_client.post("/api/url-configs", json=sample_url_config)
            assert response.status_code in [200, 201], f"Failed for URL: {url}"
    
    def test_url_validation_invalid_schemes(self, test_client: TestClient, sample_url_config):
        """Test URL validation rejects invalid schemes."""
        invalid_urls = [
            "ftp://example.com",
            "file:///path/to/file",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>"
        ]
        
        for url in invalid_urls:
            sample_url_config["url"] = url
            sample_url_config["name"] = f"Test {url}"
            response = test_client.post("/api/url-configs", json=sample_url_config)
            assert response.status_code == 422, f"Should reject URL: {url}"
    
    def test_name_length_validation(self, test_client: TestClient, sample_url_config):
        """Test name length validation."""
        # Test minimum length
        sample_url_config["name"] = "A"  # Too short
        response = test_client.post("/api/url-configs", json=sample_url_config)
        assert response.status_code == 422
        
        # Test maximum length
        sample_url_config["name"] = "A" * 300  # Too long
        response = test_client.post("/api/url-configs", json=sample_url_config)
        assert response.status_code == 422
        
        # Test valid length
        sample_url_config["name"] = "Valid Length Name"
        response = test_client.post("/api/url-configs", json=sample_url_config)
        assert response.status_code in [200, 201]
    
    def test_category_validation(self, test_client: TestClient, sample_url_config):
        """Test category validation."""
        valid_categories = ["news", "exchange", "defi", "nft", "analytics", "social"]
        
        for category in valid_categories:
            sample_url_config["category"] = category
            sample_url_config["name"] = f"Test {category}"
            response = test_client.post("/api/url-configs", json=sample_url_config)
            assert response.status_code in [200, 201], f"Failed for category: {category}"
        
        # Test invalid category
        sample_url_config["category"] = "invalid_category"
        sample_url_config["name"] = "Test Invalid"
        response = test_client.post("/api/url-configs", json=sample_url_config)
        assert response.status_code == 422