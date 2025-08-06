#!/usr/bin/env python3
"""
Integration tests for URL mapping persistence in crawler configuration.

This module tests the complete flow from frontend crawler creation
to backend persistence and retrieval of URL mapping data.
"""

import pytest
import asyncio
import json
import aiohttp
from typing import Dict, Any, List
from datetime import datetime


class TestURLMappingPersistence:
    """Integration tests for URL mapping persistence functionality."""
    
    BASE_URL = "http://localhost:4001"
    
    @pytest.fixture
    async def http_session(self):
        """Create an HTTP session for API calls."""
        async with aiohttp.ClientSession() as session:
            yield session
    
    @pytest.fixture
    def sample_url_mapping(self) -> Dict[str, Any]:
        """Create a sample URL mapping for testing."""
        return {
            "name": "Test Crypto News Mapping",
            "description": "Test mapping for crypto news sites",
            "urls": ["https://coindesk.com", "https://cointelegraph.com"],
            "extractor_ids": ["crypto_news_extractor", "price_extractor"],
            "priority": 1,
            "rate_limit": 2,
            "crawler_settings": {
                "timeout": 30,
                "retry_attempts": 3,
                "user_agent": "CRY-A-4MCP-Bot/1.0"
            },
            "validation_rules": {
                "required_elements": ["title", "content"],
                "min_content_length": 100
            }
        }
    
    @pytest.fixture
    def sample_crawler_config(self, sample_url_mapping) -> Dict[str, Any]:
        """Create a sample crawler configuration with URL mapping."""
        return {
            "name": "Test Crypto Crawler",
            "description": "Test crawler with URL mapping integration",
            "crawler_type": "llm",
            "is_active": True,
            "urlMappingId": "test-mapping-id",  # Will be set after creating mapping
            "targetUrls": ["https://coindesk.com/news", "https://cointelegraph.com/news"],
            "config": {
                "timeout": 30,
                "retry_attempts": 3,
                "concurrent_requests": 5
            },
            "llm_config": {
                "model": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 2000
            },
            "extraction_strategies": ["crypto_news_extractor"]
        }
    
    async def test_create_url_mapping(self, http_session, sample_url_mapping):
        """Test creating a URL mapping via API."""
        async with http_session.post(
            f"{self.BASE_URL}/api/url-mappings",
            json=sample_url_mapping
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            # Verify response structure
            assert "id" in data
            assert data["name"] == sample_url_mapping["name"]
            assert data["urls"] == sample_url_mapping["urls"]
            assert data["extractor_ids"] == sample_url_mapping["extractor_ids"]
            
            return data["id"]
    
    async def test_create_crawler_with_url_mapping(
        self, 
        http_session, 
        sample_crawler_config, 
        sample_url_mapping
    ):
        """Test creating a crawler with URL mapping reference."""
        # First create the URL mapping
        mapping_id = await self.test_create_url_mapping(http_session, sample_url_mapping)
        
        # Update crawler config with the actual mapping ID
        sample_crawler_config["urlMappingId"] = mapping_id
        
        # Create the crawler
        async with http_session.post(
            f"{self.BASE_URL}/api/crawlers",
            json=sample_crawler_config
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            # Verify crawler was created with URL mapping data
            assert "id" in data
            assert data["name"] == sample_crawler_config["name"]
            assert data["url_mapping_id"] == mapping_id
            assert data["target_urls"] == sample_crawler_config["targetUrls"]
            
            return data["id"], mapping_id
    
    async def test_retrieve_crawler_with_url_mapping(
        self, 
        http_session, 
        sample_crawler_config, 
        sample_url_mapping
    ):
        """Test retrieving a crawler and verifying URL mapping persistence."""
        # Create crawler with URL mapping
        crawler_id, mapping_id = await self.test_create_crawler_with_url_mapping(
            http_session, sample_crawler_config, sample_url_mapping
        )
        
        # Retrieve the crawler
        async with http_session.get(
            f"{self.BASE_URL}/api/crawlers/{crawler_id}"
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            # Verify URL mapping data is persisted
            assert data["url_mapping_id"] == mapping_id
            assert data["target_urls"] == sample_crawler_config["targetUrls"]
            assert data["url_mapping_ids"] is not None
            
            # Verify the URL mapping ID is in the list
            if isinstance(data["url_mapping_ids"], list):
                assert mapping_id in data["url_mapping_ids"]
            elif isinstance(data["url_mapping_ids"], str):
                mapping_ids = json.loads(data["url_mapping_ids"])
                assert mapping_id in mapping_ids
    
    async def test_update_crawler_url_mapping(
        self, 
        http_session, 
        sample_crawler_config, 
        sample_url_mapping
    ):
        """Test updating a crawler's URL mapping configuration."""
        # Create crawler with URL mapping
        crawler_id, original_mapping_id = await self.test_create_crawler_with_url_mapping(
            http_session, sample_crawler_config, sample_url_mapping
        )
        
        # Create a new URL mapping
        new_mapping = sample_url_mapping.copy()
        new_mapping["name"] = "Updated Test Mapping"
        new_mapping["urls"] = ["https://decrypt.co", "https://theblock.co"]
        
        new_mapping_id = await self.test_create_url_mapping(http_session, new_mapping)
        
        # Update the crawler with new URL mapping
        update_data = {
            "urlMappingId": new_mapping_id,
            "targetUrls": ["https://decrypt.co/news", "https://theblock.co/news"]
        }
        
        async with http_session.put(
            f"{self.BASE_URL}/api/crawlers/{crawler_id}",
            json=update_data
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            # Verify the update was successful
            assert data["url_mapping_id"] == new_mapping_id
            assert data["target_urls"] == update_data["targetUrls"]
    
    async def test_crawler_list_includes_url_mapping_data(
        self, 
        http_session, 
        sample_crawler_config, 
        sample_url_mapping
    ):
        """Test that crawler list endpoint includes URL mapping data."""
        # Create crawler with URL mapping
        crawler_id, mapping_id = await self.test_create_crawler_with_url_mapping(
            http_session, sample_crawler_config, sample_url_mapping
        )
        
        # Get crawler list
        async with http_session.get(
            f"{self.BASE_URL}/api/crawlers"
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            # Find our crawler in the list
            test_crawler = None
            for crawler in data:
                if crawler["id"] == crawler_id:
                    test_crawler = crawler
                    break
            
            assert test_crawler is not None
            assert test_crawler["url_mapping_id"] == mapping_id
            assert test_crawler["target_urls"] == sample_crawler_config["targetUrls"]
    
    async def test_error_handling_invalid_url_mapping(
        self, 
        http_session, 
        sample_crawler_config
    ):
        """Test error handling when creating crawler with invalid URL mapping ID."""
        # Try to create crawler with non-existent URL mapping ID
        sample_crawler_config["urlMappingId"] = "non-existent-mapping-id"
        
        async with http_session.post(
            f"{self.BASE_URL}/api/crawlers",
            json=sample_crawler_config
        ) as response:
            # Should handle gracefully (either create without mapping or return error)
            assert response.status in [200, 400, 404]
            
            if response.status == 200:
                data = await response.json()
                # If created, URL mapping fields should be null or empty
                assert data["url_mapping_id"] in [None, ""]
    
    async def test_data_transformation_consistency(
        self, 
        http_session, 
        sample_crawler_config, 
        sample_url_mapping
    ):
        """Test that data transformation between frontend and backend is consistent."""
        # Create crawler with URL mapping
        crawler_id, mapping_id = await self.test_create_crawler_with_url_mapping(
            http_session, sample_crawler_config, sample_url_mapping
        )
        
        # Retrieve the crawler
        async with http_session.get(
            f"{self.BASE_URL}/api/crawlers/{crawler_id}"
        ) as response:
            assert response.status == 200
            backend_data = await response.json()
        
        # Verify data transformation consistency
        # Frontend sends: urlMappingId -> Backend stores: url_mapping_id
        assert backend_data["url_mapping_id"] == sample_crawler_config["urlMappingId"]
        
        # Frontend sends: targetUrls -> Backend stores: target_urls
        assert backend_data["target_urls"] == sample_crawler_config["targetUrls"]
        
        # Verify JSON serialization/deserialization
        if "url_mapping_ids" in backend_data and backend_data["url_mapping_ids"]:
            if isinstance(backend_data["url_mapping_ids"], str):
                # Should be valid JSON
                mapping_ids = json.loads(backend_data["url_mapping_ids"])
                assert isinstance(mapping_ids, list)
        
        if "target_urls" in backend_data and backend_data["target_urls"]:
            if isinstance(backend_data["target_urls"], str):
                # Should be valid JSON
                target_urls = json.loads(backend_data["target_urls"])
                assert isinstance(target_urls, list)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])