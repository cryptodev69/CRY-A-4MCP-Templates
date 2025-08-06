"""Integration tests for URL Mappings API endpoints.

This module provides comprehensive integration testing for the URL Mappings API
endpoints within the CRY-A-4MCP platform, including:
    - Technical URL mapping CRUD operations
    - Technical configuration validation
    - API endpoint integration
    - Technical workflow validation
    - Error handling and edge cases

The tests use real API calls and database operations to ensure
end-to-end technical functionality works correctly.

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

import asyncio
import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from src.cry_a_4mcp.main import app
from src.cry_a_4mcp.storage.url_mappings_db import URLMappingsDatabase


class TestURLMappingsAPI:
    """Test suite for URL Mappings API integration.
    
    This class contains comprehensive integration tests for the URL Mappings API
    endpoints, covering technical workflows and API functionality.
    """
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing.
        
        Returns:
            TestClient: FastAPI test client instance
        """
        return TestClient(app)
    
    @pytest.fixture
    def sample_technical_mapping(self):
        """Sample technical URL mapping for testing.
        
        Returns:
            dict: Sample technical mapping data
        """
        return {
            "name": "CoinGecko API Mapping",
            "url_pattern": "https://api.coingecko.com/api/v3/coins/{coin_id}",
            "url": "https://api.coingecko.com/api/v3/coins/bitcoin",
            "url_config_id": "config_123",
            "type": "api",
            "extractor_ids": ["price_extractor", "volume_extractor"],
            "is_active": True,
            "priority": 1,
            "config": {
                "timeout": 30,
                "retry_attempts": 3,
                "rate_limit": {
                    "requests_per_minute": 50,
                    "burst_limit": 10,
                    "backoff_strategy": "exponential"
                },
                "headers": {
                    "User-Agent": "CRY-A-4MCP/1.0",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate"
                },
                "authentication": {
                    "type": "none",
                    "required": False
                },
                "response_format": "json",
                "expected_status_codes": [200, 201],
                "error_handling": {
                    "retry_on_status": [429, 500, 502, 503, 504],
                    "fail_on_status": [400, 401, 403, 404],
                    "timeout_action": "retry"
                },
                "data_validation": {
                    "required_fields": ["id", "current_price", "market_cap"],
                    "field_types": {
                        "current_price": "float",
                        "market_cap": "integer",
                        "id": "string"
                    }
                },
                "caching": {
                    "enabled": True,
                    "ttl_seconds": 300,
                    "cache_key_pattern": "coingecko_{coin_id}"
                },
                "monitoring": {
                    "track_response_time": True,
                    "track_success_rate": True,
                    "alert_on_failure_rate": 0.1
                }
            },
            "metadata": {
                "created_by": "technical_team",
                "environment": "production",
                "version": "1.0",
                "last_tested": "2024-01-15T10:00:00Z"
            }
        }
    
    def test_create_url_mapping_success(self, client, sample_technical_mapping):
        """Test successful creation of technical URL mapping via API.
        
        Validates that the API correctly:
        - Accepts technical mapping data
        - Creates mapping in database
        - Returns complete mapping with ID
        - Sets proper timestamps
        """
        # Act: Create mapping via API
        response = client.post("/api/v1/url-mappings", json=sample_technical_mapping)
        
        # Assert: Verify successful creation
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["name"] == sample_technical_mapping["name"]
        assert data["url_pattern"] == sample_technical_mapping["url_pattern"]
        assert data["url"] == sample_technical_mapping["url"]
        assert data["url_config_id"] == sample_technical_mapping["url_config_id"]
        assert data["type"] == sample_technical_mapping["type"]
        assert data["extractor_ids"] == sample_technical_mapping["extractor_ids"]
        assert data["is_active"] == sample_technical_mapping["is_active"]
        assert data["priority"] == sample_technical_mapping["priority"]
        assert data["config"] == sample_technical_mapping["config"]
        assert data["metadata"] == sample_technical_mapping["metadata"]
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_url_mapping_minimal_data(self, client):
        """Test creation with minimal technical data.
        
        Validates that mappings can be created with only required fields
        and that technical defaults are applied correctly.
        """
        # Arrange: Minimal technical data
        minimal_data = {
            "name": "Minimal Technical Mapping",
            "url": "https://minimal-tech.com/api",
            "url_config_id": "config_minimal",
            "type": "api"
        }
        
        # Act: Create mapping
        response = client.post("/api/v1/url-mappings", json=minimal_data)
        
        # Assert: Verify creation with technical defaults
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == minimal_data["name"]
        assert data["url"] == minimal_data["url"]
        assert data["url_config_id"] == minimal_data["url_config_id"]
        assert data["type"] == minimal_data["type"]
        assert data["is_active"] is True  # Technical default
        assert data["priority"] in [None, 0, 1]  # Technical default
        assert data["extractor_ids"] in [None, []]  # Technical default
    
    def test_create_url_mapping_validation_error(self, client):
        """Test creation with invalid technical data.
        
        Validates that the API correctly:
        - Validates technical data
        - Returns appropriate error messages
        - Handles technical validation failures
        """
        # Test missing required technical fields
        invalid_data = {
            "name": "Missing URL and Config ID",
            "type": "api"
        }
        
        response = client.post("/api/v1/url-mappings", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # Test invalid technical data types
        invalid_types = {
            "name": "Test Mapping",
            "url": "https://test.com",
            "url_config_id": "config_test",
            "type": "api",
            "is_active": "not_boolean",  # Should be boolean
            "priority": "not_integer",  # Should be integer
            "extractor_ids": "not_array"  # Should be array
        }
        
        response = client.post("/api/v1/url-mappings", json=invalid_types)
        assert response.status_code == 422
    
    def test_get_url_mapping_success(self, client, sample_technical_mapping):
        """Test successful retrieval of technical URL mapping.
        
        Validates that the API correctly:
        - Retrieves mapping by ID
        - Returns complete technical data
        - Maintains technical data integrity
        """
        # Arrange: Create mapping first
        create_response = client.post("/api/v1/url-mappings", json=sample_technical_mapping)
        mapping_id = create_response.json()["id"]
        
        # Act: Retrieve mapping
        response = client.get(f"/api/v1/url-mappings/{mapping_id}")
        
        # Assert: Verify retrieval
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == mapping_id
        assert data["name"] == sample_technical_mapping["name"]
        assert data["config"] == sample_technical_mapping["config"]
        assert data["metadata"] == sample_technical_mapping["metadata"]
    
    def test_get_url_mapping_not_found(self, client):
        """Test retrieval of non-existent technical mapping.
        
        Validates that the API correctly:
        - Returns 404 for non-existent mappings
        - Provides appropriate error message
        """
        # Act: Try to get non-existent mapping
        response = client.get("/api/v1/url-mappings/non_existent_id")
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_url_mapping_success(self, client, sample_technical_mapping):
        """Test successful update of technical URL mapping.
        
        Validates that the API correctly:
        - Updates technical fields
        - Preserves unchanged technical data
        - Updates technical timestamps
        - Returns updated technical data
        """
        # Arrange: Create mapping first
        create_response = client.post("/api/v1/url-mappings", json=sample_technical_mapping)
        mapping_id = create_response.json()["id"]
        
        # Prepare technical update data
        update_data = {
            "priority": 5,
            "is_active": False,
            "config": {
                "timeout": 60,
                "retry_attempts": 5,
                "rate_limit": {
                    "requests_per_minute": 100,
                    "burst_limit": 20,
                    "backoff_strategy": "linear"
                },
                "headers": {
                    "User-Agent": "CRY-A-4MCP/2.0",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Cache-Control": "no-cache"
                },
                "authentication": {
                    "type": "api_key",
                    "required": True,
                    "header_name": "X-API-Key"
                },
                "response_format": "json",
                "expected_status_codes": [200, 201, 202],
                "error_handling": {
                    "retry_on_status": [429, 500, 502, 503, 504],
                    "fail_on_status": [400, 401, 403, 404, 422],
                    "timeout_action": "fail"
                },
                "caching": {
                    "enabled": False,
                    "ttl_seconds": 0
                },
                "monitoring": {
                    "track_response_time": True,
                    "track_success_rate": True,
                    "track_data_quality": True,
                    "alert_on_failure_rate": 0.05
                }
            },
            "metadata": {
                "created_by": "technical_team",
                "environment": "production",
                "version": "2.0",
                "last_tested": "2024-01-16T15:30:00Z",
                "performance_notes": "Optimized for high-frequency requests"
            }
        }
        
        # Act: Update mapping
        response = client.put(f"/api/v1/url-mappings/{mapping_id}", json=update_data)
        
        # Assert: Verify update
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == mapping_id
        assert data["priority"] == update_data["priority"]
        assert data["is_active"] == update_data["is_active"]
        assert data["config"] == update_data["config"]
        assert data["metadata"] == update_data["metadata"]
        # Verify unchanged technical fields
        assert data["name"] == sample_technical_mapping["name"]
        assert data["url"] == sample_technical_mapping["url"]
        assert data["url_config_id"] == sample_technical_mapping["url_config_id"]
        assert data["type"] == sample_technical_mapping["type"]
    
    def test_update_url_mapping_not_found(self, client):
        """Test update of non-existent technical mapping.
        
        Validates that the API correctly:
        - Returns 404 for non-existent mappings
        - Handles technical update attempts gracefully
        """
        # Act: Try to update non-existent mapping
        response = client.put("/api/v1/url-mappings/non_existent_id", json={"priority": 10})
        
        # Assert: Verify 404 response
        assert response.status_code == 404
    
    def test_delete_url_mapping_success(self, client, sample_technical_mapping):
        """Test successful deletion of technical URL mapping.
        
        Validates that the API correctly:
        - Deletes technical mapping by ID
        - Returns appropriate success response
        - Removes mapping from database
        """
        # Arrange: Create mapping first
        create_response = client.post("/api/v1/url-mappings", json=sample_technical_mapping)
        mapping_id = create_response.json()["id"]
        
        # Act: Delete mapping
        response = client.delete(f"/api/v1/url-mappings/{mapping_id}")
        
        # Assert: Verify deletion
        assert response.status_code == 204
        
        # Verify mapping is gone
        get_response = client.get(f"/api/v1/url-mappings/{mapping_id}")
        assert get_response.status_code == 404
    
    def test_delete_url_mapping_not_found(self, client):
        """Test deletion of non-existent technical mapping.
        
        Validates that the API correctly:
        - Returns 404 for non-existent mappings
        - Handles technical deletion attempts gracefully
        """
        # Act: Try to delete non-existent mapping
        response = client.delete("/api/v1/url-mappings/non_existent_id")
        
        # Assert: Verify 404 response
        assert response.status_code == 404
    
    def test_get_all_url_mappings(self, client, sample_technical_mapping):
        """Test retrieval of all technical URL mappings.
        
        Validates that the API correctly:
        - Returns all technical mappings
        - Handles empty technical database
        - Maintains technical data integrity for multiple mappings
        """
        # Test empty database
        response = client.get("/api/v1/url-mappings")
        assert response.status_code == 200
        assert response.json() == []
        
        # Create multiple technical mappings
        mapping1_response = client.post("/api/v1/url-mappings", json=sample_technical_mapping)
        
        mapping2_data = sample_technical_mapping.copy()
        mapping2_data["name"] = "Binance Technical Mapping"
        mapping2_data["url"] = "https://api.binance.com/api/v3/ticker/24hr"
        mapping2_data["url_config_id"] = "config_binance"
        mapping2_data["type"] = "rest_api"
        mapping2_response = client.post("/api/v1/url-mappings", json=mapping2_data)
        
        # Act: Get all mappings
        response = client.get("/api/v1/url-mappings")
        
        # Assert: Verify all technical mappings returned
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        mapping_ids = [m["id"] for m in data]
        assert mapping1_response.json()["id"] in mapping_ids
        assert mapping2_response.json()["id"] in mapping_ids
    
    def test_get_mappings_by_config_id(self, client, sample_technical_mapping):
        """Test retrieval of mappings by URL configuration ID.
        
        Validates that the API correctly:
        - Filters mappings by URL config ID
        - Returns matching technical mappings only
        - Handles config ID queries
        """
        # Create mappings with different config IDs
        config1_mapping = sample_technical_mapping.copy()
        config1_mapping["url_config_id"] = "config_1"
        client.post("/api/v1/url-mappings", json=config1_mapping)
        
        config2_mapping = sample_technical_mapping.copy()
        config2_mapping["name"] = "Config 2 Technical Mapping"
        config2_mapping["url_config_id"] = "config_2"
        config2_mapping["url"] = "https://config2.com/api"
        client.post("/api/v1/url-mappings", json=config2_mapping)
        
        # Test filtering by config ID
        response = client.get("/api/v1/url-mappings?url_config_id=config_1")
        assert response.status_code == 200
        config1_results = response.json()
        assert len(config1_results) == 1
        assert config1_results[0]["url_config_id"] == "config_1"
        
        response = client.get("/api/v1/url-mappings?url_config_id=config_2")
        assert response.status_code == 200
        config2_results = response.json()
        assert len(config2_results) == 1
        assert config2_results[0]["url_config_id"] == "config_2"
    
    def test_get_mappings_by_type(self, client, sample_technical_mapping):
        """Test retrieval of mappings by technical type.
        
        Validates that the API correctly:
        - Filters mappings by technical type
        - Returns matching technical mappings only
        - Handles type queries
        """
        # Create mappings with different technical types
        api_mapping = sample_technical_mapping.copy()
        api_mapping["type"] = "api"
        client.post("/api/v1/url-mappings", json=api_mapping)
        
        scraper_mapping = sample_technical_mapping.copy()
        scraper_mapping["name"] = "Scraper Technical Mapping"
        scraper_mapping["type"] = "scraper"
        scraper_mapping["url"] = "https://scraper.com"
        scraper_mapping["url_config_id"] = "config_scraper"
        client.post("/api/v1/url-mappings", json=scraper_mapping)
        
        # Test filtering by technical type
        response = client.get("/api/v1/url-mappings?type=api")
        assert response.status_code == 200
        api_results = response.json()
        assert len(api_results) == 1
        assert api_results[0]["type"] == "api"
        
        response = client.get("/api/v1/url-mappings?type=scraper")
        assert response.status_code == 200
        scraper_results = response.json()
        assert len(scraper_results) == 1
        assert scraper_results[0]["type"] == "scraper"
    
    def test_technical_workflow_integration(self, client):
        """Test complete technical workflow integration.
        
        Validates that the API correctly:
        - Supports complete technical mapping lifecycle
        - Maintains technical data consistency
        - Handles technical workflow transitions
        """
        # Step 1: Technical team creates initial mapping configuration
        initial_mapping = {
            "name": "Technical Workflow Test",
            "url_pattern": "https://api.example.com/v1/{endpoint}",
            "url": "https://api.example.com/v1/data",
            "url_config_id": "config_workflow",
            "type": "rest_api",
            "extractor_ids": ["basic_extractor"],
            "is_active": False,  # Start inactive for testing
            "priority": 1,
            "config": {
                "timeout": 30,
                "retry_attempts": 3,
                "rate_limit": {
                    "requests_per_minute": 60,
                    "burst_limit": 10
                },
                "headers": {
                    "User-Agent": "CRY-A-4MCP/1.0"
                },
                "response_format": "json"
            },
            "metadata": {
                "created_by": "technical_team",
                "environment": "development",
                "version": "1.0"
            }
        }
        
        create_response = client.post("/api/v1/url-mappings", json=initial_mapping)
        assert create_response.status_code == 201
        mapping_id = create_response.json()["id"]
        
        # Step 2: Technical optimization and testing
        optimization_update = {
            "config": {
                "timeout": 45,
                "retry_attempts": 5,
                "rate_limit": {
                    "requests_per_minute": 120,
                    "burst_limit": 20,
                    "backoff_strategy": "exponential"
                },
                "headers": {
                    "User-Agent": "CRY-A-4MCP/1.0",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip"
                },
                "response_format": "json",
                "expected_status_codes": [200, 201],
                "error_handling": {
                    "retry_on_status": [429, 500, 502, 503],
                    "fail_on_status": [400, 401, 403, 404],
                    "timeout_action": "retry"
                },
                "caching": {
                    "enabled": True,
                    "ttl_seconds": 300
                },
                "monitoring": {
                    "track_response_time": True,
                    "track_success_rate": True
                }
            },
            "metadata": {
                "created_by": "technical_team",
                "environment": "development",
                "version": "1.1",
                "optimization_notes": "Improved rate limiting and error handling"
            }
        }
        
        update_response = client.put(f"/api/v1/url-mappings/{mapping_id}", json=optimization_update)
        assert update_response.status_code == 200
        
        # Step 3: Production deployment
        production_update = {
            "is_active": True,
            "priority": 10,
            "extractor_ids": ["basic_extractor", "advanced_extractor", "validator_extractor"],
            "metadata": {
                "created_by": "technical_team",
                "environment": "production",
                "version": "1.2",
                "deployment_date": "2024-01-16T12:00:00Z",
                "deployment_notes": "Deployed to production with full monitoring"
            }
        }
        
        final_response = client.put(f"/api/v1/url-mappings/{mapping_id}", json=production_update)
        assert final_response.status_code == 200
        
        # Verify final technical state
        final_data = final_response.json()
        assert final_data["is_active"] is True
        assert final_data["priority"] == 10
        assert len(final_data["extractor_ids"]) == 3
        assert final_data["metadata"]["environment"] == "production"
        assert "deployment_date" in final_data["metadata"]
        assert final_data["config"]["caching"]["enabled"] is True
        assert final_data["config"]["monitoring"]["track_response_time"] is True
    
    def test_technical_error_handling(self, client):
        """Test technical error handling scenarios.
        
        Validates that the API correctly:
        - Handles technical validation errors
        - Provides meaningful technical error messages
        - Maintains technical data consistency during errors
        """
        # Test technical constraint violations
        invalid_technical_data = {
            "name": "",  # Empty name
            "url": "invalid-url",  # Invalid URL format
            "url_config_id": "",  # Empty config ID
            "type": "invalid_type",  # Invalid type
            "priority": "not_a_number",  # Invalid priority
            "is_active": "maybe",  # Invalid boolean
            "extractor_ids": "not_an_array",  # Invalid array
            "config": "not_an_object"  # Invalid object
        }
        
        response = client.post("/api/v1/url-mappings", json=invalid_technical_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert isinstance(error_detail, list)
        assert len(error_detail) > 0
        
        # Verify specific technical validation errors
        error_fields = [error["loc"][-1] for error in error_detail]
        assert "name" in error_fields or "url" in error_fields or "url_config_id" in error_fields
    
    def test_technical_data_consistency(self, client, sample_technical_mapping):
        """Test technical data consistency across operations.
        
        Validates that the API correctly:
        - Maintains technical data consistency
        - Preserves technical relationships
        - Handles technical data integrity
        """
        # Create mapping with complex technical configuration
        complex_technical_data = sample_technical_mapping.copy()
        complex_technical_data["config"] = {
            "timeout": 60,
            "retry_attempts": 5,
            "rate_limit": {
                "requests_per_minute": 100,
                "burst_limit": 25,
                "backoff_strategy": "exponential",
                "backoff_multiplier": 2.0,
                "max_backoff_seconds": 300
            },
            "headers": {
                "User-Agent": "CRY-A-4MCP/1.0",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            },
            "authentication": {
                "type": "oauth2",
                "required": True,
                "token_endpoint": "https://auth.example.com/token",
                "scopes": ["read", "write"],
                "refresh_threshold_seconds": 300
            },
            "response_format": "json",
            "expected_status_codes": [200, 201, 202],
            "error_handling": {
                "retry_on_status": [429, 500, 502, 503, 504],
                "fail_on_status": [400, 401, 403, 404, 422],
                "timeout_action": "retry",
                "max_retries": 3,
                "circuit_breaker": {
                    "enabled": True,
                    "failure_threshold": 5,
                    "recovery_timeout": 60
                }
            },
            "data_validation": {
                "required_fields": ["id", "timestamp", "data"],
                "field_types": {
                    "id": "string",
                    "timestamp": "datetime",
                    "data": "object"
                },
                "validation_rules": [
                    {"field": "timestamp", "rule": "not_older_than", "value": "1_hour"},
                    {"field": "data", "rule": "not_empty", "value": True}
                ]
            },
            "caching": {
                "enabled": True,
                "ttl_seconds": 600,
                "cache_key_pattern": "api_{endpoint}_{params_hash}",
                "invalidation_rules": [
                    {"trigger": "data_update", "action": "clear_related"},
                    {"trigger": "time_based", "action": "refresh"}
                ]
            },
            "monitoring": {
                "track_response_time": True,
                "track_success_rate": True,
                "track_data_quality": True,
                "track_cache_hit_rate": True,
                "alert_on_failure_rate": 0.05,
                "alert_on_response_time": 5000,
                "metrics_retention_days": 30
            }
        }
        
        # Create and verify technical data integrity
        create_response = client.post("/api/v1/url-mappings", json=complex_technical_data)
        assert create_response.status_code == 201
        
        mapping_id = create_response.json()["id"]
        
        # Retrieve and verify technical data consistency
        get_response = client.get(f"/api/v1/url-mappings/{mapping_id}")
        assert get_response.status_code == 200
        
        retrieved_data = get_response.json()
        assert retrieved_data["config"] == complex_technical_data["config"]
        
        # Verify nested technical data structure
        assert retrieved_data["config"]["rate_limit"]["requests_per_minute"] == 100
        assert retrieved_data["config"]["authentication"]["type"] == "oauth2"
        assert retrieved_data["config"]["error_handling"]["circuit_breaker"]["enabled"] is True
        assert len(retrieved_data["config"]["data_validation"]["validation_rules"]) == 2
        
        # Update technical configuration and verify consistency
        technical_update = {
            "config": {
                "timeout": 90,
                "retry_attempts": 7,
                "rate_limit": {
                    "requests_per_minute": 200,
                    "burst_limit": 50,
                    "backoff_strategy": "linear",
                    "backoff_multiplier": 1.5,
                    "max_backoff_seconds": 600
                },
                "monitoring": {
                    "track_response_time": True,
                    "track_success_rate": True,
                    "track_data_quality": True,
                    "track_cache_hit_rate": True,
                    "track_error_patterns": True,
                    "alert_on_failure_rate": 0.03,
                    "alert_on_response_time": 3000,
                    "metrics_retention_days": 90
                }
            }
        }
        
        update_response = client.put(f"/api/v1/url-mappings/{mapping_id}", json=technical_update)
        assert update_response.status_code == 200
        
        updated_data = update_response.json()
        assert updated_data["config"]["timeout"] == 90
        assert updated_data["config"]["rate_limit"]["requests_per_minute"] == 200
        assert updated_data["config"]["monitoring"]["track_error_patterns"] is True
        assert updated_data["config"]["monitoring"]["metrics_retention_days"] == 90