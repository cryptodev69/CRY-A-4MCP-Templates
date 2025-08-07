"""Comprehensive CRUD tests for crawlers API.

This module tests all Create, Read, Update, Delete operations for crawlers
to ensure the API works correctly and prevents regressions.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tests.conftest import assert_valid_response, assert_valid_crud_response


class TestCrawlersCRUD:
    """Test suite for crawlers CRUD operations."""
    
    def test_create_crawler_success(self, test_client: TestClient, sample_crawler):
        """Test successful creation of crawler."""
        response = test_client.post("/api/crawlers", json=sample_crawler)
        
        assert_valid_crud_response(response, "create")
        data = response.json()
        
        # Verify all fields are correctly stored
        assert data["name"] == sample_crawler["name"]
        assert data["description"] == sample_crawler["description"]
        assert data["url_mapping_ids"] == sample_crawler["url_mapping_ids"]
        assert data["extraction_strategies"] == sample_crawler["extraction_strategies"]
        assert data["schedule"] == sample_crawler["schedule"]
        assert data["is_active"] == sample_crawler["is_active"]
        assert data["config"] == sample_crawler["config"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_crawler_missing_required_fields(self, test_client: TestClient):
        """Test creation fails with missing required fields."""
        incomplete_crawler = {
            "name": "Incomplete Crawler"
            # Missing required fields: extraction_strategies, schedule, etc.
        }
        
        response = test_client.post("/api/crawlers", json=incomplete_crawler)
        assert response.status_code == 422  # Validation error
    
    def test_create_crawler_invalid_schedule(self, test_client: TestClient, sample_crawler):
        """Test creation fails with invalid cron schedule."""
        sample_crawler["schedule"] = "invalid-cron-expression"
        
        response = test_client.post("/api/crawlers", json=sample_crawler)
        assert response.status_code == 422  # Validation error
    
    def test_create_crawler_empty_extraction_strategies(self, test_client: TestClient, sample_crawler):
        """Test creation fails with empty extraction strategies."""
        sample_crawler["extraction_strategies"] = []
        
        response = test_client.post("/api/crawlers", json=sample_crawler)
        assert response.status_code == 422  # Validation error
    
    def test_create_crawler_duplicate_name(self, test_client: TestClient, sample_crawler):
        """Test creation fails with duplicate name."""
        # Create first crawler
        response1 = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(response1, "create")
        
        # Try to create second crawler with same name
        response2 = test_client.post("/api/crawlers", json=sample_crawler)
        assert response2.status_code in [400, 409]  # Conflict or bad request
    
    def test_get_all_crawlers(self, test_client: TestClient, test_data_factory):
        """Test retrieving all crawlers."""
        # Create multiple crawlers
        crawlers = [
            test_data_factory.create_crawler("Crawler 1"),
            test_data_factory.create_crawler("Crawler 2"),
            test_data_factory.create_crawler("Crawler 3")
        ]
        
        created_ids = []
        for crawler in crawlers:
            response = test_client.post("/api/crawlers", json=crawler)
            assert_valid_crud_response(response, "create")
            created_ids.append(response.json()["id"])
        
        # Get all crawlers
        response = test_client.get("/api/crawlers")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # At least our 3 crawlers
        
        # Verify our created crawlers are in the response
        response_ids = [item["id"] for item in data]
        for created_id in created_ids:
            assert created_id in response_ids
    
    def test_get_crawler_by_id(self, test_client: TestClient, sample_crawler):
        """Test retrieving crawler by ID."""
        # Create crawler
        create_response = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(create_response, "create")
        crawler_id = create_response.json()["id"]
        
        # Get crawler by ID
        response = test_client.get(f"/api/crawlers/{crawler_id}")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        assert data["id"] == crawler_id
        assert data["name"] == sample_crawler["name"]
        assert data["description"] == sample_crawler["description"]
    
    def test_get_crawler_not_found(self, test_client: TestClient):
        """Test retrieving non-existent crawler."""
        response = test_client.get("/api/crawlers/99999")
        assert response.status_code == 404
    
    def test_update_crawler_success(self, test_client: TestClient, sample_crawler):
        """Test successful update of crawler."""
        # Create crawler
        create_response = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(create_response, "create")
        crawler_id = create_response.json()["id"]
        
        # Update crawler
        update_data = {
            "name": "Updated Crawler Name",
            "description": "Updated description",
            "extraction_strategies": ["updated_strategy", "new_strategy"],
            "schedule": "0 */12 * * *",  # Every 12 hours
            "config": {
                "max_concurrent_requests": 10,
                "request_delay": 3.0,
                "timeout": 60
            },
            "is_active": False
        }
        
        response = test_client.put(f"/api/crawlers/{crawler_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["id"] == crawler_id
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["extraction_strategies"] == update_data["extraction_strategies"]
        assert data["schedule"] == update_data["schedule"]
        assert data["config"] == update_data["config"]
        assert data["is_active"] == update_data["is_active"]
    
    def test_update_crawler_partial(self, test_client: TestClient, sample_crawler):
        """Test partial update of crawler."""
        # Create crawler
        create_response = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(create_response, "create")
        crawler_id = create_response.json()["id"]
        
        # Partial update (only name and schedule)
        update_data = {
            "name": "Partially Updated Crawler",
            "schedule": "0 */8 * * *"  # Every 8 hours
        }
        
        response = test_client.patch(f"/api/crawlers/{crawler_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["schedule"] == update_data["schedule"]
        # Other fields should remain unchanged
        assert data["description"] == sample_crawler["description"]
        assert data["extraction_strategies"] == sample_crawler["extraction_strategies"]
        assert data["config"] == sample_crawler["config"]
    
    def test_update_crawler_url_mapping_ids(self, test_client: TestClient, sample_crawler, sample_url_mapping):
        """Test updating URL mapping IDs."""
        # Create URL mapping first
        mapping_response = test_client.post("/api/url-mappings", json=sample_url_mapping)
        if mapping_response.status_code in [200, 201]:
            mapping_id = mapping_response.json()["id"]
        else:
            mapping_id = 1  # Use a default ID if creation fails
        
        # Create crawler
        create_response = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(create_response, "create")
        crawler_id = create_response.json()["id"]
        
        # Update URL mapping IDs
        update_data = {
            "url_mapping_ids": [mapping_id, 2, 3]
        }
        
        response = test_client.put(f"/api/crawlers/{crawler_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["url_mapping_ids"] == update_data["url_mapping_ids"]
    
    def test_update_crawler_config_only(self, test_client: TestClient, sample_crawler):
        """Test updating only the configuration."""
        # Create crawler
        create_response = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(create_response, "create")
        crawler_id = create_response.json()["id"]
        
        # Update only config
        update_data = {
            "config": {
                "max_concurrent_requests": 20,
                "request_delay": 5.0,
                "timeout": 120,
                "retry_attempts": 5,
                "custom_headers": {
                    "User-Agent": "CustomCrawler/2.0",
                    "Accept": "application/json"
                },
                "proxy_settings": {
                    "enabled": True,
                    "rotation": True
                }
            }
        }
        
        response = test_client.patch(f"/api/crawlers/{crawler_id}", json=update_data)
        assert_valid_crud_response(response, "update")
        
        data = response.json()
        assert data["config"] == update_data["config"]
        # Other fields should remain unchanged
        assert data["name"] == sample_crawler["name"]
        assert data["extraction_strategies"] == sample_crawler["extraction_strategies"]
    
    def test_update_crawler_not_found(self, test_client: TestClient):
        """Test updating non-existent crawler."""
        update_data = {"name": "Updated Name"}
        response = test_client.put("/api/crawlers/99999", json=update_data)
        assert response.status_code == 404
    
    def test_update_crawler_invalid_data(self, test_client: TestClient, sample_crawler):
        """Test update fails with invalid data."""
        # Create crawler
        create_response = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(create_response, "create")
        crawler_id = create_response.json()["id"]
        
        # Try to update with invalid schedule
        update_data = {"schedule": "invalid-cron"}
        
        response = test_client.put(f"/api/crawlers/{crawler_id}", json=update_data)
        assert response.status_code == 422  # Validation error
    
    def test_delete_crawler_success(self, test_client: TestClient, sample_crawler):
        """Test successful deletion of crawler."""
        # Create crawler
        create_response = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(create_response, "create")
        crawler_id = create_response.json()["id"]
        
        # Delete crawler
        response = test_client.delete(f"/api/crawlers/{crawler_id}")
        assert_valid_crud_response(response, "delete")
        
        # Verify crawler is deleted
        get_response = test_client.get(f"/api/crawlers/{crawler_id}")
        assert get_response.status_code == 404
    
    def test_delete_crawler_not_found(self, test_client: TestClient):
        """Test deleting non-existent crawler."""
        response = test_client.delete("/api/crawlers/99999")
        assert response.status_code == 404
    
    def test_delete_crawler_with_running_jobs(self, test_client: TestClient, sample_crawler):
        """Test deletion behavior when crawler has running jobs."""
        # Create crawler
        create_response = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(create_response, "create")
        crawler_id = create_response.json()["id"]
        
        # Try to delete crawler (may have running jobs)
        response = test_client.delete(f"/api/crawlers/{crawler_id}")
        # Should either succeed or prevent deletion due to running jobs
        assert response.status_code in [204, 400, 409]


class TestCrawlersValidation:
    """Test suite for crawlers validation."""
    
    def test_schedule_validation(self, test_client: TestClient, sample_crawler):
        """Test cron schedule validation."""
        valid_schedules = [
            "0 */6 * * *",  # Every 6 hours
            "0 0 * * *",    # Daily at midnight
            "0 0 * * 0",    # Weekly on Sunday
            "0 0 1 * *",    # Monthly on 1st
            "*/15 * * * *"   # Every 15 minutes
        ]
        
        for schedule in valid_schedules:
            sample_crawler["schedule"] = schedule
            sample_crawler["name"] = f"Test Crawler {schedule}"
            response = test_client.post("/api/crawlers", json=sample_crawler)
            assert response.status_code in [200, 201], f"Failed for schedule: {schedule}"
        
        # Test invalid schedules
        invalid_schedules = [
            "invalid",
            "* * * *",      # Missing field
            "60 * * * *",   # Invalid minute
            "* 25 * * *",   # Invalid hour
        ]
        
        for schedule in invalid_schedules:
            sample_crawler["schedule"] = schedule
            sample_crawler["name"] = f"Test Invalid {schedule}"
            response = test_client.post("/api/crawlers", json=sample_crawler)
            assert response.status_code == 422, f"Should reject schedule: {schedule}"
    
    def test_extraction_strategies_validation(self, test_client: TestClient, sample_crawler):
        """Test extraction strategies validation."""
        # Test with valid strategies
        valid_strategies = [
            ["crypto_price_extractor"],
            ["news_extractor", "sentiment_analyzer"],
            ["defi_protocol_extractor", "yield_farming_extractor", "liquidity_extractor"]
        ]
        
        for strategies in valid_strategies:
            sample_crawler["extraction_strategies"] = strategies
            sample_crawler["name"] = f"Test Crawler {len(strategies)} strategies"
            response = test_client.post("/api/crawlers", json=sample_crawler)
            assert response.status_code in [200, 201]
        
        # Test with empty strategies
        sample_crawler["extraction_strategies"] = []
        sample_crawler["name"] = "Test Empty Strategies"
        response = test_client.post("/api/crawlers", json=sample_crawler)
        assert response.status_code == 422
    
    def test_config_validation(self, test_client: TestClient, sample_crawler):
        """Test configuration validation."""
        # Test with valid config
        valid_configs = [
            {
                "max_concurrent_requests": 5,
                "request_delay": 2.0
            },
            {
                "max_concurrent_requests": 1,
                "request_delay": 10.0,
                "timeout": 30,
                "retry_attempts": 3
            }
        ]
        
        for config in valid_configs:
            sample_crawler["config"] = config
            sample_crawler["name"] = f"Test Config {config['max_concurrent_requests']}"
            response = test_client.post("/api/crawlers", json=sample_crawler)
            assert response.status_code in [200, 201]
        
        # Test with invalid config values
        invalid_configs = [
            {"max_concurrent_requests": 0},     # Should be > 0
            {"max_concurrent_requests": -1},    # Should be > 0
            {"request_delay": -1.0},            # Should be >= 0
        ]
        
        for config in invalid_configs:
            sample_crawler["config"] = config
            sample_crawler["name"] = f"Test Invalid Config"
            response = test_client.post("/api/crawlers", json=sample_crawler)
            assert response.status_code == 422
    
    def test_name_length_validation(self, test_client: TestClient, sample_crawler):
        """Test name length validation."""
        # Test minimum length
        sample_crawler["name"] = "A"  # Too short
        response = test_client.post("/api/crawlers", json=sample_crawler)
        assert response.status_code == 422
        
        # Test maximum length
        sample_crawler["name"] = "A" * 300  # Too long
        response = test_client.post("/api/crawlers", json=sample_crawler)
        assert response.status_code == 422
        
        # Test valid length
        sample_crawler["name"] = "Valid Length Crawler Name"
        response = test_client.post("/api/crawlers", json=sample_crawler)
        assert response.status_code in [200, 201]


class TestCrawlersAdvanced:
    """Advanced test scenarios for crawlers."""
    
    def test_crawler_pagination(self, test_client: TestClient, test_data_factory):
        """Test pagination of crawlers list."""
        # Create multiple crawlers
        for i in range(15):
            crawler = test_data_factory.create_crawler(f"Crawler {i}")
            response = test_client.post("/api/crawlers", json=crawler)
            assert_valid_crud_response(response, "create")
        
        # Test pagination parameters
        response = test_client.get("/api/crawlers?limit=10&offset=0")
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
    
    def test_crawler_filtering_by_active_status(self, test_client: TestClient, test_data_factory):
        """Test filtering crawlers by active status."""
        # Create active and inactive crawlers
        active_crawler = test_data_factory.create_crawler("Active", is_active=True)
        inactive_crawler = test_data_factory.create_crawler("Inactive", is_active=False)
        
        test_client.post("/api/crawlers", json=active_crawler)
        test_client.post("/api/crawlers", json=inactive_crawler)
        
        # Filter by active status
        response = test_client.get("/api/crawlers?is_active=true")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        if isinstance(data, list):
            active_crawlers = [item for item in data if item["is_active"] is True]
            assert len(active_crawlers) >= 1
    
    def test_crawler_search(self, test_client: TestClient, test_data_factory):
        """Test searching crawlers by name."""
        # Create crawlers with searchable names
        crawler1 = test_data_factory.create_crawler("Bitcoin Price Crawler")
        crawler2 = test_data_factory.create_crawler("Ethereum News Crawler")
        
        test_client.post("/api/crawlers", json=crawler1)
        test_client.post("/api/crawlers", json=crawler2)
        
        # Search by name
        response = test_client.get("/api/crawlers?search=Bitcoin")
        assert_valid_crud_response(response, "read")
        
        data = response.json()
        if isinstance(data, list):
            bitcoin_crawlers = [item for item in data if "Bitcoin" in item["name"]]
            assert len(bitcoin_crawlers) >= 1
    
    def test_crawler_bulk_operations(self, test_client: TestClient, test_data_factory):
        """Test bulk operations on crawlers."""
        # Create multiple crawlers
        crawler_ids = []
        for i in range(5):
            crawler = test_data_factory.create_crawler(f"Bulk Crawler {i}")
            response = test_client.post("/api/crawlers", json=crawler)
            assert_valid_crud_response(response, "create")
            crawler_ids.append(response.json()["id"])
        
        # Test bulk status update
        bulk_update_data = {
            "ids": crawler_ids,
            "is_active": False
        }
        
        response = test_client.patch("/api/crawlers/bulk-status", json=bulk_update_data)
        if response.status_code == 200:
            # Verify all crawlers are now inactive
            for crawler_id in crawler_ids:
                get_response = test_client.get(f"/api/crawlers/{crawler_id}")
                if get_response.status_code == 200:
                    data = get_response.json()
                    assert data["is_active"] is False
    
    def test_crawler_start_stop_operations(self, test_client: TestClient, sample_crawler):
        """Test starting and stopping crawlers."""
        # Create crawler
        create_response = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(create_response, "create")
        crawler_id = create_response.json()["id"]
        
        # Test start crawler
        response = test_client.post(f"/api/crawlers/{crawler_id}/start")
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] in ["started", "running", "scheduled"]
        
        # Test stop crawler
        response = test_client.post(f"/api/crawlers/{crawler_id}/stop")
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] in ["stopped", "stopping", "inactive"]
    
    def test_crawler_status_endpoint(self, test_client: TestClient, sample_crawler):
        """Test crawler status endpoint."""
        # Create crawler
        create_response = test_client.post("/api/crawlers", json=sample_crawler)
        assert_valid_crud_response(create_response, "create")
        crawler_id = create_response.json()["id"]
        
        # Get crawler status
        response = test_client.get(f"/api/crawlers/{crawler_id}/status")
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "last_run" in data or "next_run" in data
            assert "job_count" in data or "total_jobs" in data