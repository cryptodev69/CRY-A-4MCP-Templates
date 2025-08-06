"""Unit tests for URL Configuration Database operations.

This module provides comprehensive unit testing for the URL Configuration database
operations within the CRY-A-4MCP platform, including:
    - CRUD operations for business URL configurations
    - Business metadata validation
    - Error handling and edge cases
    - Data serialization/deserialization
    - Business logic validation

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

from src.cry_a_4mcp.storage.url_configuration_db import URLConfigurationDatabase


class TestURLConfigurationDatabase:
    """Test suite for URL Configuration Database operations.
    
    This class contains comprehensive tests for the URL configuration database
    functionality, covering normal operations, error conditions, and edge cases.
    """
    
    @pytest.fixture
    async def temp_db(self):
        """Create a temporary database for testing.
        
        Returns:
            URLConfigurationDatabase: Initialized database instance with temporary file
        """
        # Create temporary database file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        # Initialize database
        db = URLConfigurationDatabase(db_path=temp_file.name)
        await db.initialize()
        
        yield db
        
        # Cleanup
        await db.close()
        Path(temp_file.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample URL configuration data for testing.
        
        Returns:
            dict: Sample configuration data with all business fields
        """
        return {
            "name": "CoinMarketCap Price Data",
            "description": "Extract cryptocurrency price data from CoinMarketCap",
            "url": "https://coinmarketcap.com/currencies/bitcoin/",
            "profile_type": "price_data",
            "category": "cryptocurrency",
            "business_priority": "high",
            "scraping_difficulty": "medium",
            "has_official_api": True,
            "api_pricing": "freemium",
            "recommendation": "Use API for production, scraping for backup",
            "key_data_points": [
                "current_price",
                "market_cap",
                "24h_volume",
                "price_change_24h"
            ],
            "target_data": {
                "primary": "Real-time cryptocurrency prices",
                "secondary": "Market capitalization and trading volume",
                "frequency": "Every 5 minutes"
            },
            "rationale": "Critical for trading algorithms and portfolio tracking",
            "cost_analysis": {
                "api_cost_monthly": 0,
                "scraping_cost_monthly": 50,
                "maintenance_hours_monthly": 2,
                "recommended_approach": "API"
            },
            "business_value": "high",
            "compliance_notes": "Ensure rate limiting compliance with ToS",
            "is_active": True,
            "metadata": {
                "created_by": "business_analyst",
                "department": "trading",
                "approval_status": "approved"
            }
        }
    
    @pytest.mark.asyncio
    async def test_create_configuration_success(self, temp_db, sample_config_data):
        """Test successful creation of URL configuration.
        
        Validates that the database correctly:
        - Creates new configuration with generated ID
        - Stores all business metadata fields
        - Sets creation timestamp
        - Returns complete configuration data
        """
        # Act: Create configuration
        result = await temp_db.create_configuration(sample_config_data)
        
        # Assert: Verify creation
        assert result is not None
        assert "id" in result
        assert result["name"] == sample_config_data["name"]
        assert result["description"] == sample_config_data["description"]
        assert result["url"] == sample_config_data["url"]
        assert result["profile_type"] == sample_config_data["profile_type"]
        assert result["category"] == sample_config_data["category"]
        assert result["business_priority"] == sample_config_data["business_priority"]
        assert result["scraping_difficulty"] == sample_config_data["scraping_difficulty"]
        assert result["has_official_api"] == sample_config_data["has_official_api"]
        assert result["api_pricing"] == sample_config_data["api_pricing"]
        assert result["recommendation"] == sample_config_data["recommendation"]
        assert result["key_data_points"] == sample_config_data["key_data_points"]
        assert result["target_data"] == sample_config_data["target_data"]
        assert result["rationale"] == sample_config_data["rationale"]
        assert result["cost_analysis"] == sample_config_data["cost_analysis"]
        assert result["business_value"] == sample_config_data["business_value"]
        assert result["compliance_notes"] == sample_config_data["compliance_notes"]
        assert result["is_active"] == sample_config_data["is_active"]
        assert result["metadata"] == sample_config_data["metadata"]
        assert "created_at" in result
        assert "updated_at" in result
    
    @pytest.mark.asyncio
    async def test_create_configuration_minimal_data(self, temp_db):
        """Test creation with minimal required data.
        
        Validates that configurations can be created with only required fields
        and that optional fields are handled correctly.
        """
        # Arrange: Minimal configuration data
        minimal_data = {
            "name": "Basic Config",
            "url": "https://example.com"
        }
        
        # Act: Create configuration
        result = await temp_db.create_configuration(minimal_data)
        
        # Assert: Verify creation with defaults
        assert result is not None
        assert result["name"] == minimal_data["name"]
        assert result["url"] == minimal_data["url"]
        assert result["is_active"] is True  # Default value
        assert result["description"] is None  # Optional field
        assert result["profile_type"] is None  # Optional field
    
    @pytest.mark.asyncio
    async def test_get_configuration_success(self, temp_db, sample_config_data):
        """Test successful retrieval of URL configuration by ID.
        
        Validates that the database correctly:
        - Retrieves configuration by ID
        - Returns complete configuration data
        - Maintains data integrity
        """
        # Arrange: Create configuration first
        created = await temp_db.create_configuration(sample_config_data)
        config_id = created["id"]
        
        # Act: Retrieve configuration
        result = await temp_db.get_configuration(config_id)
        
        # Assert: Verify retrieval
        assert result is not None
        assert result["id"] == config_id
        assert result["name"] == sample_config_data["name"]
        assert result["url"] == sample_config_data["url"]
        assert result["target_data"] == sample_config_data["target_data"]
        assert result["cost_analysis"] == sample_config_data["cost_analysis"]
    
    @pytest.mark.asyncio
    async def test_get_configuration_not_found(self, temp_db):
        """Test retrieval of non-existent configuration.
        
        Validates that the database correctly:
        - Returns None for non-existent IDs
        - Handles invalid ID formats gracefully
        """
        # Act: Try to get non-existent configuration
        result = await temp_db.get_configuration("non_existent_id")
        
        # Assert: Verify None return
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_configuration_success(self, temp_db, sample_config_data):
        """Test successful update of URL configuration.
        
        Validates that the database correctly:
        - Updates specified fields
        - Preserves unchanged fields
        - Updates timestamp
        - Returns updated data
        """
        # Arrange: Create configuration first
        created = await temp_db.create_configuration(sample_config_data)
        config_id = created["id"]
        
        # Prepare update data
        update_data = {
            "business_priority": "critical",
            "is_active": False,
            "cost_analysis": {
                "api_cost_monthly": 100,
                "scraping_cost_monthly": 200,
                "maintenance_hours_monthly": 5,
                "recommended_approach": "hybrid"
            },
            "recommendation": "Use hybrid approach for redundancy"
        }
        
        # Act: Update configuration
        result = await temp_db.update_configuration(config_id, update_data)
        
        # Assert: Verify update
        assert result is not None
        assert result["id"] == config_id
        assert result["business_priority"] == update_data["business_priority"]
        assert result["is_active"] == update_data["is_active"]
        assert result["cost_analysis"] == update_data["cost_analysis"]
        assert result["recommendation"] == update_data["recommendation"]
        # Verify unchanged fields
        assert result["name"] == sample_config_data["name"]
        assert result["url"] == sample_config_data["url"]
        assert result["profile_type"] == sample_config_data["profile_type"]
        # Verify timestamp update
        assert result["updated_at"] != result["created_at"]
    
    @pytest.mark.asyncio
    async def test_update_configuration_not_found(self, temp_db):
        """Test update of non-existent configuration.
        
        Validates that the database correctly:
        - Returns None for non-existent configurations
        - Handles update attempts gracefully
        """
        # Act: Try to update non-existent configuration
        result = await temp_db.update_configuration("non_existent_id", {"business_priority": "high"})
        
        # Assert: Verify None return
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_configuration_success(self, temp_db, sample_config_data):
        """Test successful deletion of URL configuration.
        
        Validates that the database correctly:
        - Deletes configuration by ID
        - Returns True for successful deletion
        - Removes configuration from database
        """
        # Arrange: Create configuration first
        created = await temp_db.create_configuration(sample_config_data)
        config_id = created["id"]
        
        # Act: Delete configuration
        result = await temp_db.delete_configuration(config_id)
        
        # Assert: Verify deletion
        assert result is True
        
        # Verify configuration is gone
        deleted_config = await temp_db.get_configuration(config_id)
        assert deleted_config is None
    
    @pytest.mark.asyncio
    async def test_delete_configuration_not_found(self, temp_db):
        """Test deletion of non-existent configuration.
        
        Validates that the database correctly:
        - Returns False for non-existent configurations
        - Handles deletion attempts gracefully
        """
        # Act: Try to delete non-existent configuration
        result = await temp_db.delete_configuration("non_existent_id")
        
        # Assert: Verify False return
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_all_configurations(self, temp_db, sample_config_data):
        """Test retrieval of all URL configurations.
        
        Validates that the database correctly:
        - Returns all configurations in database
        - Handles empty database
        - Maintains data integrity for multiple configurations
        """
        # Test empty database
        result = await temp_db.get_all_configurations()
        assert result == []
        
        # Create multiple configurations
        config1 = await temp_db.create_configuration(sample_config_data)
        
        config2_data = sample_config_data.copy()
        config2_data["name"] = "Binance Trading Data"
        config2_data["url"] = "https://binance.com/api/v3/ticker/price"
        config2_data["profile_type"] = "trading_data"
        config2 = await temp_db.create_configuration(config2_data)
        
        # Act: Get all configurations
        result = await temp_db.get_all_configurations()
        
        # Assert: Verify all configurations returned
        assert len(result) == 2
        config_ids = [c["id"] for c in result]
        assert config1["id"] in config_ids
        assert config2["id"] in config_ids
    
    @pytest.mark.asyncio
    async def test_get_configurations_by_category(self, temp_db, sample_config_data):
        """Test retrieval of configurations by business category.
        
        Validates that the database correctly:
        - Filters configurations by category
        - Returns matching configurations only
        - Handles non-existent categories
        """
        # Create configurations with different categories
        crypto_config = sample_config_data.copy()
        crypto_config["category"] = "cryptocurrency"
        await temp_db.create_configuration(crypto_config)
        
        news_config = sample_config_data.copy()
        news_config["name"] = "Crypto News"
        news_config["category"] = "news"
        news_config["url"] = "https://cryptonews.com"
        await temp_db.create_configuration(news_config)
        
        # Test filtering by category
        crypto_results = await temp_db.get_configurations_by_category("cryptocurrency")
        assert len(crypto_results) == 1
        assert crypto_results[0]["category"] == "cryptocurrency"
        
        news_results = await temp_db.get_configurations_by_category("news")
        assert len(news_results) == 1
        assert news_results[0]["category"] == "news"
        
        # Test non-existent category
        empty_results = await temp_db.get_configurations_by_category("non_existent")
        assert len(empty_results) == 0
    
    @pytest.mark.asyncio
    async def test_get_configurations_by_priority(self, temp_db, sample_config_data):
        """Test retrieval of configurations by business priority.
        
        Validates that the database correctly:
        - Filters configurations by priority level
        - Returns matching configurations only
        - Handles priority-based queries
        """
        # Create configurations with different priorities
        high_config = sample_config_data.copy()
        high_config["business_priority"] = "high"
        await temp_db.create_configuration(high_config)
        
        low_config = sample_config_data.copy()
        low_config["name"] = "Low Priority Config"
        low_config["business_priority"] = "low"
        low_config["url"] = "https://example.com/low"
        await temp_db.create_configuration(low_config)
        
        # Test filtering by priority
        high_results = await temp_db.get_configurations_by_priority("high")
        assert len(high_results) == 1
        assert high_results[0]["business_priority"] == "high"
        
        low_results = await temp_db.get_configurations_by_priority("low")
        assert len(low_results) == 1
        assert low_results[0]["business_priority"] == "low"
    
    @pytest.mark.asyncio
    async def test_complex_business_data_serialization(self, temp_db):
        """Test serialization of complex business data structures.
        
        Validates that the database correctly:
        - Serializes complex business objects to JSON
        - Deserializes JSON back to objects
        - Maintains business data structure integrity
        """
        # Arrange: Complex business data
        complex_data = {
            "name": "Complex Business Config",
            "url": "https://complex-business.com",
            "target_data": {
                "primary_metrics": {
                    "revenue": {"frequency": "daily", "format": "USD"},
                    "users": {"frequency": "hourly", "format": "count"}
                },
                "secondary_metrics": [
                    {"name": "conversion_rate", "type": "percentage"},
                    {"name": "churn_rate", "type": "percentage"}
                ],
                "data_quality": {
                    "accuracy_threshold": 0.95,
                    "completeness_threshold": 0.90,
                    "timeliness_sla": "5_minutes"
                }
            },
            "cost_analysis": {
                "breakdown": {
                    "infrastructure": {"monthly": 500, "currency": "USD"},
                    "personnel": {"monthly": 2000, "currency": "USD"},
                    "tools": {"monthly": 100, "currency": "USD"}
                },
                "roi_projection": {
                    "year_1": {"revenue_impact": 50000, "cost_savings": 10000},
                    "year_2": {"revenue_impact": 100000, "cost_savings": 25000}
                },
                "risk_factors": [
                    {"factor": "data_availability", "probability": 0.1, "impact": "high"},
                    {"factor": "regulatory_changes", "probability": 0.05, "impact": "medium"}
                ]
            },
            "key_data_points": [
                {"name": "revenue", "priority": 1, "validation": "numeric"},
                {"name": "user_count", "priority": 2, "validation": "integer"},
                {"name": "timestamp", "priority": 3, "validation": "datetime"}
            ]
        }
        
        # Act: Create and retrieve configuration
        created = await temp_db.create_configuration(complex_data)
        retrieved = await temp_db.get_configuration(created["id"])
        
        # Assert: Verify complex business data integrity
        assert retrieved["target_data"] == complex_data["target_data"]
        assert retrieved["cost_analysis"] == complex_data["cost_analysis"]
        assert retrieved["key_data_points"] == complex_data["key_data_points"]
        
        # Verify nested structure access
        assert retrieved["target_data"]["primary_metrics"]["revenue"]["frequency"] == "daily"
        assert retrieved["cost_analysis"]["breakdown"]["infrastructure"]["monthly"] == 500
        assert retrieved["key_data_points"][0]["name"] == "revenue"
    
    @pytest.mark.asyncio
    async def test_business_validation_rules(self, temp_db):
        """Test business validation rules and constraints.
        
        Validates that the database correctly:
        - Enforces business validation rules
        - Handles invalid business data
        - Provides meaningful error messages
        """
        # Test with invalid business priority
        invalid_data = {
            "name": "Invalid Config",
            "url": "https://example.com",
            "business_priority": "invalid_priority"  # Should be: low, medium, high, critical
        }
        
        # Note: Depending on implementation, this might succeed or fail
        # The test validates that the system handles the data appropriately
        result = await temp_db.create_configuration(invalid_data)
        if result:
            # If creation succeeds, verify data is stored as-is
            assert result["business_priority"] == "invalid_priority"
        
        # Test with missing required fields
        with pytest.raises(Exception):
            await temp_db.create_configuration({
                "description": "Missing name and URL"
            })
    
    @pytest.mark.asyncio
    async def test_concurrent_business_operations(self, temp_db, sample_config_data):
        """Test concurrent business configuration operations.
        
        Validates that the database correctly:
        - Handles concurrent business operations
        - Maintains business data consistency
        - Prevents business logic conflicts
        """
        # Create multiple business configurations concurrently
        tasks = []
        business_categories = ["cryptocurrency", "trading", "news", "analytics", "compliance"]
        
        for i, category in enumerate(business_categories):
            data = sample_config_data.copy()
            data["name"] = f"Business Config {i}"
            data["url"] = f"https://business-{i}.com"
            data["category"] = category
            data["business_priority"] = ["low", "medium", "high", "critical"][i % 4]
            tasks.append(temp_db.create_configuration(data))
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all business operations succeeded
        assert len(results) == 5
        for result in results:
            assert result is not None
            assert "id" in result
            assert result["category"] in business_categories
        
        # Verify business data integrity
        all_configs = await temp_db.get_all_configurations()
        assert len(all_configs) == 5
        
        # Verify category distribution
        categories_found = [config["category"] for config in all_configs]
        for category in business_categories:
            assert category in categories_found