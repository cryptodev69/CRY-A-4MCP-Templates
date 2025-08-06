"""Integration tests for URL Manager API endpoints.

This module provides comprehensive integration testing for the URL Manager API
endpoints within the CRY-A-4MCP platform, including:
    - Business URL configuration CRUD operations
    - Business workflow validation
    - API endpoint integration
    - Business logic validation
    - Error handling and edge cases

The tests use real API calls and database operations to ensure
end-to-end business functionality works correctly.

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
from src.cry_a_4mcp.storage.url_configuration_db import URLConfigurationDatabase


class TestURLManagerAPI:
    """Test suite for URL Manager API integration.
    
    This class contains comprehensive integration tests for the URL Manager API
    endpoints, covering business workflows and API functionality.
    """
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing.
        
        Returns:
            TestClient: FastAPI test client instance
        """
        return TestClient(app)
    
    @pytest.fixture
    def sample_business_config(self):
        """Sample business URL configuration for testing.
        
        Returns:
            dict: Sample business configuration data
        """
        return {
            "name": "CoinGecko Market Data",
            "description": "Extract comprehensive cryptocurrency market data from CoinGecko",
            "url": "https://api.coingecko.com/api/v3/coins/markets",
            "profile_type": "market_data",
            "category": "cryptocurrency",
            "business_priority": "high",
            "scraping_difficulty": "low",
            "has_official_api": True,
            "api_pricing": "free",
            "recommendation": "Use official API - reliable and free",
            "key_data_points": [
                "market_cap",
                "current_price",
                "total_volume",
                "price_change_percentage_24h"
            ],
            "target_data": {
                "primary": "Real-time market data for top cryptocurrencies",
                "secondary": "Historical price trends and volume analysis",
                "frequency": "Every 10 minutes",
                "data_format": "JSON",
                "expected_fields": [
                    "id", "symbol", "name", "current_price", "market_cap",
                    "total_volume", "price_change_percentage_24h"
                ]
            },
            "rationale": "Essential for portfolio tracking and trading decisions",
            "cost_analysis": {
                "api_cost_monthly": 0,
                "scraping_cost_monthly": 0,
                "maintenance_hours_monthly": 1,
                "recommended_approach": "API",
                "cost_benefit_ratio": "excellent",
                "scalability": "high"
            },
            "business_value": "high",
            "compliance_notes": "Free tier allows 50 calls/minute, no authentication required",
            "is_active": True,
            "metadata": {
                "created_by": "data_team",
                "department": "analytics",
                "approval_status": "approved",
                "business_owner": "portfolio_manager",
                "technical_owner": "data_engineer"
            }
        }
    
    def test_create_url_configuration_success(self, client, sample_business_config):
        """Test successful creation of business URL configuration via API.
        
        Validates that the API correctly:
        - Accepts business configuration data
        - Creates configuration in database
        - Returns complete configuration with ID
        - Sets proper timestamps
        """
        # Act: Create configuration via API
        response = client.post("/api/v1/url-configurations", json=sample_business_config)
        
        # Assert: Verify successful creation
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["name"] == sample_business_config["name"]
        assert data["description"] == sample_business_config["description"]
        assert data["url"] == sample_business_config["url"]
        assert data["profile_type"] == sample_business_config["profile_type"]
        assert data["category"] == sample_business_config["category"]
        assert data["business_priority"] == sample_business_config["business_priority"]
        assert data["scraping_difficulty"] == sample_business_config["scraping_difficulty"]
        assert data["has_official_api"] == sample_business_config["has_official_api"]
        assert data["api_pricing"] == sample_business_config["api_pricing"]
        assert data["recommendation"] == sample_business_config["recommendation"]
        assert data["key_data_points"] == sample_business_config["key_data_points"]
        assert data["target_data"] == sample_business_config["target_data"]
        assert data["rationale"] == sample_business_config["rationale"]
        assert data["cost_analysis"] == sample_business_config["cost_analysis"]
        assert data["business_value"] == sample_business_config["business_value"]
        assert data["compliance_notes"] == sample_business_config["compliance_notes"]
        assert data["is_active"] == sample_business_config["is_active"]
        assert data["metadata"] == sample_business_config["metadata"]
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_url_configuration_minimal_data(self, client):
        """Test creation with minimal business data.
        
        Validates that configurations can be created with only required fields
        and that business defaults are applied correctly.
        """
        # Arrange: Minimal business data
        minimal_data = {
            "name": "Minimal Business Config",
            "url": "https://minimal-business.com",
            "profile_type": "basic"
        }
        
        # Act: Create configuration
        response = client.post("/api/v1/url-configurations", json=minimal_data)
        
        # Assert: Verify creation with business defaults
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == minimal_data["name"]
        assert data["url"] == minimal_data["url"]
        assert data["profile_type"] == minimal_data["profile_type"]
        assert data["is_active"] is True  # Business default
        assert data["business_priority"] in [None, "medium"]  # Business default
    
    def test_create_url_configuration_validation_error(self, client):
        """Test creation with invalid business data.
        
        Validates that the API correctly:
        - Validates business data
        - Returns appropriate error messages
        - Handles business validation failures
        """
        # Test missing required business fields
        invalid_data = {
            "description": "Missing name and URL",
            "category": "test"
        }
        
        response = client.post("/api/v1/url-configurations", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # Test invalid business data types
        invalid_types = {
            "name": "Test Config",
            "url": "https://test.com",
            "has_official_api": "not_boolean",  # Should be boolean
            "key_data_points": "not_array"  # Should be array
        }
        
        response = client.post("/api/v1/url-configurations", json=invalid_types)
        assert response.status_code == 422
    
    def test_get_url_configuration_success(self, client, sample_business_config):
        """Test successful retrieval of business URL configuration.
        
        Validates that the API correctly:
        - Retrieves configuration by ID
        - Returns complete business data
        - Maintains business data integrity
        """
        # Arrange: Create configuration first
        create_response = client.post("/api/v1/url-configurations", json=sample_business_config)
        config_id = create_response.json()["id"]
        
        # Act: Retrieve configuration
        response = client.get(f"/api/v1/url-configurations/{config_id}")
        
        # Assert: Verify retrieval
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == config_id
        assert data["name"] == sample_business_config["name"]
        assert data["target_data"] == sample_business_config["target_data"]
        assert data["cost_analysis"] == sample_business_config["cost_analysis"]
        assert data["metadata"] == sample_business_config["metadata"]
    
    def test_get_url_configuration_not_found(self, client):
        """Test retrieval of non-existent business configuration.
        
        Validates that the API correctly:
        - Returns 404 for non-existent configurations
        - Provides appropriate error message
        """
        # Act: Try to get non-existent configuration
        response = client.get("/api/v1/url-configurations/non_existent_id")
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_url_configuration_success(self, client, sample_business_config):
        """Test successful update of business URL configuration.
        
        Validates that the API correctly:
        - Updates business fields
        - Preserves unchanged business data
        - Updates business timestamps
        - Returns updated business data
        """
        # Arrange: Create configuration first
        create_response = client.post("/api/v1/url-configurations", json=sample_business_config)
        config_id = create_response.json()["id"]
        
        # Prepare business update data
        update_data = {
            "business_priority": "critical",
            "is_active": False,
            "cost_analysis": {
                "api_cost_monthly": 100,
                "scraping_cost_monthly": 500,
                "maintenance_hours_monthly": 8,
                "recommended_approach": "hybrid",
                "cost_benefit_ratio": "good",
                "scalability": "medium"
            },
            "recommendation": "Use hybrid approach for critical business operations",
            "business_value": "critical",
            "metadata": {
                "created_by": "data_team",
                "department": "analytics",
                "approval_status": "pending_review",
                "business_owner": "cto",
                "technical_owner": "senior_data_engineer",
                "last_reviewed": "2024-01-15"
            }
        }
        
        # Act: Update configuration
        response = client.put(f"/api/v1/url-configurations/{config_id}", json=update_data)
        
        # Assert: Verify update
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == config_id
        assert data["business_priority"] == update_data["business_priority"]
        assert data["is_active"] == update_data["is_active"]
        assert data["cost_analysis"] == update_data["cost_analysis"]
        assert data["recommendation"] == update_data["recommendation"]
        assert data["business_value"] == update_data["business_value"]
        assert data["metadata"] == update_data["metadata"]
        # Verify unchanged business fields
        assert data["name"] == sample_business_config["name"]
        assert data["url"] == sample_business_config["url"]
        assert data["profile_type"] == sample_business_config["profile_type"]
        assert data["category"] == sample_business_config["category"]
    
    def test_update_url_configuration_not_found(self, client):
        """Test update of non-existent business configuration.
        
        Validates that the API correctly:
        - Returns 404 for non-existent configurations
        - Handles business update attempts gracefully
        """
        # Act: Try to update non-existent configuration
        response = client.put("/api/v1/url-configurations/non_existent_id", json={"business_priority": "high"})
        
        # Assert: Verify 404 response
        assert response.status_code == 404
    
    def test_delete_url_configuration_success(self, client, sample_business_config):
        """Test successful deletion of business URL configuration.
        
        Validates that the API correctly:
        - Deletes business configuration by ID
        - Returns appropriate success response
        - Removes configuration from database
        """
        # Arrange: Create configuration first
        create_response = client.post("/api/v1/url-configurations", json=sample_business_config)
        config_id = create_response.json()["id"]
        
        # Act: Delete configuration
        response = client.delete(f"/api/v1/url-configurations/{config_id}")
        
        # Assert: Verify deletion
        assert response.status_code == 204
        
        # Verify configuration is gone
        get_response = client.get(f"/api/v1/url-configurations/{config_id}")
        assert get_response.status_code == 404
    
    def test_delete_url_configuration_not_found(self, client):
        """Test deletion of non-existent business configuration.
        
        Validates that the API correctly:
        - Returns 404 for non-existent configurations
        - Handles business deletion attempts gracefully
        """
        # Act: Try to delete non-existent configuration
        response = client.delete("/api/v1/url-configurations/non_existent_id")
        
        # Assert: Verify 404 response
        assert response.status_code == 404
    
    def test_get_all_url_configurations(self, client, sample_business_config):
        """Test retrieval of all business URL configurations.
        
        Validates that the API correctly:
        - Returns all business configurations
        - Handles empty business database
        - Maintains business data integrity for multiple configurations
        """
        # Test empty database
        response = client.get("/api/v1/url-configurations")
        assert response.status_code == 200
        assert response.json() == []
        
        # Create multiple business configurations
        config1_response = client.post("/api/v1/url-configurations", json=sample_business_config)
        
        config2_data = sample_business_config.copy()
        config2_data["name"] = "Binance Business Data"
        config2_data["url"] = "https://api.binance.com/api/v3/ticker/24hr"
        config2_data["profile_type"] = "trading_data"
        config2_data["category"] = "exchange"
        config2_response = client.post("/api/v1/url-configurations", json=config2_data)
        
        # Act: Get all configurations
        response = client.get("/api/v1/url-configurations")
        
        # Assert: Verify all business configurations returned
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        config_ids = [c["id"] for c in data]
        assert config1_response.json()["id"] in config_ids
        assert config2_response.json()["id"] in config_ids
    
    def test_get_configurations_by_business_category(self, client, sample_business_config):
        """Test retrieval of configurations by business category.
        
        Validates that the API correctly:
        - Filters configurations by business category
        - Returns matching business configurations only
        - Handles business category queries
        """
        # Create configurations with different business categories
        crypto_config = sample_business_config.copy()
        crypto_config["category"] = "cryptocurrency"
        client.post("/api/v1/url-configurations", json=crypto_config)
        
        news_config = sample_business_config.copy()
        news_config["name"] = "Crypto Business News"
        news_config["category"] = "news"
        news_config["url"] = "https://cryptonews.com/api"
        client.post("/api/v1/url-configurations", json=news_config)
        
        # Test filtering by business category
        response = client.get("/api/v1/url-configurations?category=cryptocurrency")
        assert response.status_code == 200
        crypto_results = response.json()
        assert len(crypto_results) == 1
        assert crypto_results[0]["category"] == "cryptocurrency"
        
        response = client.get("/api/v1/url-configurations?category=news")
        assert response.status_code == 200
        news_results = response.json()
        assert len(news_results) == 1
        assert news_results[0]["category"] == "news"
    
    def test_get_configurations_by_business_priority(self, client, sample_business_config):
        """Test retrieval of configurations by business priority.
        
        Validates that the API correctly:
        - Filters configurations by business priority
        - Returns matching business configurations only
        - Handles business priority queries
        """
        # Create configurations with different business priorities
        high_config = sample_business_config.copy()
        high_config["business_priority"] = "high"
        client.post("/api/v1/url-configurations", json=high_config)
        
        low_config = sample_business_config.copy()
        low_config["name"] = "Low Priority Business Config"
        low_config["business_priority"] = "low"
        low_config["url"] = "https://low-priority.com"
        client.post("/api/v1/url-configurations", json=low_config)
        
        # Test filtering by business priority
        response = client.get("/api/v1/url-configurations?business_priority=high")
        assert response.status_code == 200
        high_results = response.json()
        assert len(high_results) == 1
        assert high_results[0]["business_priority"] == "high"
        
        response = client.get("/api/v1/url-configurations?business_priority=low")
        assert response.status_code == 200
        low_results = response.json()
        assert len(low_results) == 1
        assert low_results[0]["business_priority"] == "low"
    
    def test_business_workflow_integration(self, client):
        """Test complete business workflow integration.
        
        Validates that the API correctly:
        - Supports complete business configuration lifecycle
        - Maintains business data consistency
        - Handles business workflow transitions
        """
        # Step 1: Business analyst creates initial configuration
        initial_config = {
            "name": "Business Workflow Test",
            "description": "Test configuration for business workflow",
            "url": "https://business-workflow.com",
            "profile_type": "market_analysis",
            "category": "research",
            "business_priority": "medium",
            "scraping_difficulty": "medium",
            "has_official_api": False,
            "api_pricing": "unknown",
            "recommendation": "Investigate API availability",
            "business_value": "medium",
            "is_active": False,  # Start inactive for review
            "metadata": {
                "created_by": "business_analyst",
                "department": "research",
                "approval_status": "pending"
            }
        }
        
        create_response = client.post("/api/v1/url-configurations", json=initial_config)
        assert create_response.status_code == 201
        config_id = create_response.json()["id"]
        
        # Step 2: Technical team reviews and updates with technical details
        technical_update = {
            "scraping_difficulty": "low",
            "has_official_api": True,
            "api_pricing": "free",
            "recommendation": "Use official API - well documented and reliable",
            "key_data_points": [
                "market_trends",
                "sentiment_analysis",
                "volume_indicators"
            ],
            "target_data": {
                "primary": "Market sentiment and trend analysis",
                "frequency": "Every 30 minutes",
                "data_format": "JSON",
                "api_endpoint": "/api/v1/market-analysis"
            },
            "cost_analysis": {
                "api_cost_monthly": 0,
                "scraping_cost_monthly": 0,
                "maintenance_hours_monthly": 2,
                "recommended_approach": "API"
            },
            "metadata": {
                "created_by": "business_analyst",
                "department": "research",
                "approval_status": "technical_review_complete",
                "technical_reviewer": "senior_engineer",
                "review_date": "2024-01-15"
            }
        }
        
        update_response = client.put(f"/api/v1/url-configurations/{config_id}", json=technical_update)
        assert update_response.status_code == 200
        
        # Step 3: Business owner approves and activates
        approval_update = {
            "business_priority": "high",
            "business_value": "high",
            "is_active": True,
            "metadata": {
                "created_by": "business_analyst",
                "department": "research",
                "approval_status": "approved",
                "technical_reviewer": "senior_engineer",
                "business_approver": "research_director",
                "approval_date": "2024-01-16",
                "activation_date": "2024-01-16"
            }
        }
        
        final_response = client.put(f"/api/v1/url-configurations/{config_id}", json=approval_update)
        assert final_response.status_code == 200
        
        # Verify final business state
        final_data = final_response.json()
        assert final_data["business_priority"] == "high"
        assert final_data["business_value"] == "high"
        assert final_data["is_active"] is True
        assert final_data["has_official_api"] is True
        assert final_data["metadata"]["approval_status"] == "approved"
        assert "business_approver" in final_data["metadata"]
        assert "activation_date" in final_data["metadata"]
    
    def test_business_error_handling(self, client):
        """Test business error handling scenarios.
        
        Validates that the API correctly:
        - Handles business validation errors
        - Provides meaningful business error messages
        - Maintains business data consistency during errors
        """
        # Test business constraint violations
        invalid_business_data = {
            "name": "",  # Empty name
            "url": "invalid-url",  # Invalid URL format
            "business_priority": "invalid_priority",  # Invalid priority
            "has_official_api": "maybe",  # Invalid boolean
            "cost_analysis": "not_an_object"  # Invalid object type
        }
        
        response = client.post("/api/v1/url-configurations", json=invalid_business_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert isinstance(error_detail, list)
        assert len(error_detail) > 0
        
        # Verify specific business validation errors
        error_fields = [error["loc"][-1] for error in error_detail]
        assert "name" in error_fields or "url" in error_fields
    
    def test_business_data_consistency(self, client, sample_business_config):
        """Test business data consistency across operations.
        
        Validates that the API correctly:
        - Maintains business data consistency
        - Preserves business relationships
        - Handles business data integrity
        """
        # Create configuration with complex business data
        complex_business_data = sample_business_config.copy()
        complex_business_data["target_data"] = {
            "primary": "Complex business metrics",
            "kpis": {
                "revenue_impact": {"target": 100000, "measurement": "monthly"},
                "cost_savings": {"target": 25000, "measurement": "monthly"},
                "efficiency_gain": {"target": 0.15, "measurement": "percentage"}
            },
            "business_rules": [
                {"rule": "data_freshness", "threshold": "5_minutes", "action": "alert"},
                {"rule": "data_quality", "threshold": 0.95, "action": "fallback"}
            ]
        }
        
        # Create and verify business data integrity
        create_response = client.post("/api/v1/url-configurations", json=complex_business_data)
        assert create_response.status_code == 201
        
        config_id = create_response.json()["id"]
        
        # Retrieve and verify business data consistency
        get_response = client.get(f"/api/v1/url-configurations/{config_id}")
        assert get_response.status_code == 200
        
        retrieved_data = get_response.json()
        assert retrieved_data["target_data"] == complex_business_data["target_data"]
        
        # Verify nested business data structure
        assert retrieved_data["target_data"]["kpis"]["revenue_impact"]["target"] == 100000
        assert retrieved_data["target_data"]["business_rules"][0]["rule"] == "data_freshness"
        
        # Update business data and verify consistency
        business_update = {
            "target_data": {
                "primary": "Updated business metrics",
                "kpis": {
                    "revenue_impact": {"target": 150000, "measurement": "monthly"},
                    "cost_savings": {"target": 35000, "measurement": "monthly"},
                    "efficiency_gain": {"target": 0.20, "measurement": "percentage"},
                    "customer_satisfaction": {"target": 0.90, "measurement": "score"}
                },
                "business_rules": [
                    {"rule": "data_freshness", "threshold": "3_minutes", "action": "alert"},
                    {"rule": "data_quality", "threshold": 0.98, "action": "fallback"},
                    {"rule": "business_hours", "threshold": "9-17_EST", "action": "schedule"}
                ]
            }
        }
        
        update_response = client.put(f"/api/v1/url-configurations/{config_id}", json=business_update)
        assert update_response.status_code == 200
        
        updated_data = update_response.json()
        assert updated_data["target_data"] == business_update["target_data"]
        assert updated_data["target_data"]["kpis"]["revenue_impact"]["target"] == 150000
        assert len(updated_data["target_data"]["business_rules"]) == 3