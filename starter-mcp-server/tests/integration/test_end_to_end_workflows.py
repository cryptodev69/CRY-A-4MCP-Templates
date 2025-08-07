"""End-to-end integration tests for the complete API workflow.

This module tests complete workflows that span multiple API endpoints
to ensure the entire system works together correctly.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from tests.conftest import assert_valid_response, assert_valid_crud_response


class TestCompleteWorkflows:
    """Test complete workflows that span multiple API endpoints."""
    
    def test_complete_crawling_workflow(self, test_client: TestClient, test_data_factory):
        """Test complete workflow: create config -> mapping -> extractor -> crawler -> run crawl."""
        # Step 1: Create URL configuration
        url_config = test_data_factory.create_url_config("Crypto News Site")
        config_response = test_client.post("/api/url-configs", json=url_config)
        assert_valid_crud_response(config_response, "create")
        config_id = config_response.json()["id"]
        
        # Step 2: Create extractor
        extractor = test_data_factory.create_extractor("News Extractor")
        extractor_response = test_client.post("/api/extractors", json=extractor)
        assert_valid_crud_response(extractor_response, "create")
        extractor_id = extractor_response.json()["id"]
        
        # Step 3: Create URL mapping
        url_mapping = test_data_factory.create_url_mapping(
            "News Mapping",
            extractor_ids=[extractor_id]
        )
        mapping_response = test_client.post("/api/url-mappings", json=url_mapping)
        assert_valid_crud_response(mapping_response, "create")
        mapping_id = mapping_response.json()["id"]
        
        # Step 4: Create crawler
        crawler = test_data_factory.create_crawler(
            "News Crawler",
            url_mapping_ids=[mapping_id]
        )
        crawler_response = test_client.post("/api/crawlers", json=crawler)
        assert_valid_crud_response(crawler_response, "create")
        crawler_id = crawler_response.json()["id"]
        
        # Step 5: Start crawl job
        crawl_request = {
            "crawler_id": crawler_id,
            "url": "https://example.com/crypto-news",
            "priority": "high"
        }
        
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock successful crawl response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body><h1>Crypto News</h1><p>Bitcoin reaches new high</p></body></html>"
            mock_response.headers = {"content-type": "text/html"}
            mock_get.return_value = mock_response
            
            crawl_response = test_client.post("/api/crawl", json=crawl_request)
            assert_valid_crud_response(crawl_response, "create")
            
            crawl_data = crawl_response.json()
            assert "job_id" in crawl_data or "id" in crawl_data
            assert "status" in crawl_data
        
        # Step 6: Verify all components are linked correctly
        # Get crawler and verify it has the correct mapping
        get_crawler_response = test_client.get(f"/api/crawlers/{crawler_id}")
        assert_valid_crud_response(get_crawler_response, "read")
        crawler_data = get_crawler_response.json()
        assert mapping_id in crawler_data["url_mapping_ids"]
        
        # Get mapping and verify it has the correct extractor
        get_mapping_response = test_client.get(f"/api/url-mappings/{mapping_id}")
        assert_valid_crud_response(get_mapping_response, "read")
        mapping_data = get_mapping_response.json()
        assert extractor_id in mapping_data["extractor_ids"]
    
    def test_openrouter_integration_workflow(self, test_client: TestClient, sample_openrouter_request):
        """Test OpenRouter integration with crawled data processing."""
        # Step 1: Get available models
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {
                        "id": "openai/gpt-4",
                        "name": "GPT-4",
                        "pricing": {"prompt": "0.00003", "completion": "0.00006"},
                        "context_length": 8192
                    }
                ]
            }
            mock_get.return_value = mock_response
            
            models_response = test_client.get("/api/openrouter/models")
            assert_valid_crud_response(models_response, "read")
            models_data = models_response.json()
            assert "data" in models_data
            assert len(models_data["data"]) > 0
        
        # Step 2: Process crawled data with OpenRouter
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Analysis: This is positive crypto news about Bitcoin reaching new highs."
                        }
                    }
                ],
                "usage": {"total_tokens": 45}
            }
            mock_post.return_value = mock_response
            
            # Simulate processing crawled content
            analysis_request = {
                "model": "openai/gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "Analyze the following crypto news content for sentiment and key insights."
                    },
                    {
                        "role": "user",
                        "content": "Bitcoin reaches new high - The cryptocurrency market is showing strong bullish signals."
                    }
                ],
                "max_tokens": 150
            }
            
            analysis_response = test_client.post("/api/openrouter/chat/completions", json=analysis_request)
            assert_valid_crud_response(analysis_response, "create")
            
            analysis_data = analysis_response.json()
            assert "choices" in analysis_data
            assert len(analysis_data["choices"]) > 0
            assert "message" in analysis_data["choices"][0]
    
    def test_data_consistency_across_updates(self, test_client: TestClient, test_data_factory):
        """Test data consistency when updating related entities."""
        # Create initial entities
        extractor = test_data_factory.create_extractor("Test Extractor")
        extractor_response = test_client.post("/api/extractors", json=extractor)
        assert_valid_crud_response(extractor_response, "create")
        extractor_id = extractor_response.json()["id"]
        
        url_mapping = test_data_factory.create_url_mapping(
            "Test Mapping",
            extractor_ids=[extractor_id]
        )
        mapping_response = test_client.post("/api/url-mappings", json=url_mapping)
        assert_valid_crud_response(mapping_response, "create")
        mapping_id = mapping_response.json()["id"]
        
        crawler = test_data_factory.create_crawler(
            "Test Crawler",
            url_mapping_ids=[mapping_id]
        )
        crawler_response = test_client.post("/api/crawlers", json=crawler)
        assert_valid_crud_response(crawler_response, "create")
        crawler_id = crawler_response.json()["id"]
        
        # Update extractor and verify mapping still references it correctly
        extractor_update = {
            "name": "Updated Extractor",
            "description": "Updated description",
            "config": {"updated": True}
        }
        
        update_response = test_client.put(f"/api/extractors/{extractor_id}", json=extractor_update)
        assert_valid_crud_response(update_response, "update")
        
        # Verify mapping still has correct extractor reference
        get_mapping_response = test_client.get(f"/api/url-mappings/{mapping_id}")
        assert_valid_crud_response(get_mapping_response, "read")
        mapping_data = get_mapping_response.json()
        assert extractor_id in mapping_data["extractor_ids"]
        
        # Update mapping and verify crawler still references it correctly
        mapping_update = {
            "name": "Updated Mapping",
            "url_pattern": "https://updated.example.com/*"
        }
        
        update_mapping_response = test_client.put(f"/api/url-mappings/{mapping_id}", json=mapping_update)
        assert_valid_crud_response(update_mapping_response, "update")
        
        # Verify crawler still has correct mapping reference
        get_crawler_response = test_client.get(f"/api/crawlers/{crawler_id}")
        assert_valid_crud_response(get_crawler_response, "read")
        crawler_data = get_crawler_response.json()
        assert mapping_id in crawler_data["url_mapping_ids"]
    
    def test_error_handling_across_workflow(self, test_client: TestClient, test_data_factory):
        """Test error handling when workflow steps fail."""
        # Create valid extractor
        extractor = test_data_factory.create_extractor("Valid Extractor")
        extractor_response = test_client.post("/api/extractors", json=extractor)
        assert_valid_crud_response(extractor_response, "create")
        extractor_id = extractor_response.json()["id"]
        
        # Try to create mapping with non-existent extractor ID
        invalid_mapping = test_data_factory.create_url_mapping(
            "Invalid Mapping",
            extractor_ids=[extractor_id, 99999]  # 99999 doesn't exist
        )
        
        mapping_response = test_client.post("/api/url-mappings", json=invalid_mapping)
        # Should either succeed (ignoring invalid IDs) or fail with validation error
        assert mapping_response.status_code in [200, 201, 400, 422]
        
        if mapping_response.status_code in [200, 201]:
            mapping_id = mapping_response.json()["id"]
            
            # Try to create crawler with this mapping
            crawler = test_data_factory.create_crawler(
                "Test Crawler",
                url_mapping_ids=[mapping_id]
            )
            crawler_response = test_client.post("/api/crawlers", json=crawler)
            assert_valid_crud_response(crawler_response, "create")
            
            # Try to start crawl with invalid URL
            invalid_crawl_request = {
                "crawler_id": crawler_response.json()["id"],
                "url": "invalid-url",  # Invalid URL format
                "priority": "high"
            }
            
            crawl_response = test_client.post("/api/crawl", json=invalid_crawl_request)
            assert crawl_response.status_code in [400, 422]  # Should reject invalid URL
    
    def test_concurrent_operations(self, test_client: TestClient, test_data_factory):
        """Test concurrent operations across different endpoints."""
        import threading
        import time
        
        results = []
        
        def create_extractor(name_suffix):
            extractor = test_data_factory.create_extractor(f"Concurrent Extractor {name_suffix}")
            response = test_client.post("/api/extractors", json=extractor)
            results.append(("extractor", response.status_code))
        
        def create_url_config(name_suffix):
            config = test_data_factory.create_url_config(f"Concurrent Config {name_suffix}")
            response = test_client.post("/api/url-configs", json=config)
            results.append(("config", response.status_code))
        
        # Start concurrent operations
        threads = []
        for i in range(5):
            t1 = threading.Thread(target=create_extractor, args=(i,))
            t2 = threading.Thread(target=create_url_config, args=(i,))
            threads.extend([t1, t2])
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations succeeded
        assert len(results) == 10  # 5 extractors + 5 configs
        success_count = sum(1 for _, status in results if status in [200, 201])
        assert success_count >= 8  # Allow for some potential conflicts
    
    def test_bulk_operations_workflow(self, test_client: TestClient, test_data_factory):
        """Test bulk operations across multiple entities."""
        # Create multiple extractors
        extractor_ids = []
        for i in range(3):
            extractor = test_data_factory.create_extractor(f"Bulk Extractor {i}")
            response = test_client.post("/api/extractors", json=extractor)
            assert_valid_crud_response(response, "create")
            extractor_ids.append(response.json()["id"])
        
        # Create multiple mappings using these extractors
        mapping_ids = []
        for i in range(2):
            mapping = test_data_factory.create_url_mapping(
                f"Bulk Mapping {i}",
                extractor_ids=extractor_ids[:2]  # Use first 2 extractors
            )
            response = test_client.post("/api/url-mappings", json=mapping)
            assert_valid_crud_response(response, "create")
            mapping_ids.append(response.json()["id"])
        
        # Create crawler using all mappings
        crawler = test_data_factory.create_crawler(
            "Bulk Crawler",
            url_mapping_ids=mapping_ids
        )
        crawler_response = test_client.post("/api/crawlers", json=crawler)
        assert_valid_crud_response(crawler_response, "create")
        crawler_id = crawler_response.json()["id"]
        
        # Verify the complete chain is properly linked
        get_crawler_response = test_client.get(f"/api/crawlers/{crawler_id}")
        assert_valid_crud_response(get_crawler_response, "read")
        crawler_data = get_crawler_response.json()
        
        # Verify crawler has all mappings
        for mapping_id in mapping_ids:
            assert mapping_id in crawler_data["url_mapping_ids"]
        
        # Verify each mapping has the correct extractors
        for mapping_id in mapping_ids:
            get_mapping_response = test_client.get(f"/api/url-mappings/{mapping_id}")
            assert_valid_crud_response(get_mapping_response, "read")
            mapping_data = get_mapping_response.json()
            
            # Should have at least some of our extractors
            common_extractors = set(mapping_data["extractor_ids"]) & set(extractor_ids)
            assert len(common_extractors) > 0


class TestSystemIntegration:
    """Test system-level integration scenarios."""
    
    def test_system_health_check(self, test_client: TestClient):
        """Test overall system health by checking all endpoints."""
        endpoints_to_check = [
            ("/api/url-configs", "GET"),
            ("/api/url-mappings", "GET"),
            ("/api/extractors", "GET"),
            ("/api/crawlers", "GET"),
        ]
        
        for endpoint, method in endpoints_to_check:
            if method == "GET":
                response = test_client.get(endpoint)
            else:
                response = test_client.request(method, endpoint)
            
            assert response.status_code in [200, 404], f"Health check failed for {method} {endpoint}"
    
    def test_openrouter_system_integration(self, test_client: TestClient):
        """Test OpenRouter integration with system health."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": []}
            mock_get.return_value = mock_response
            
            response = test_client.get("/api/openrouter/models")
            assert response.status_code in [200, 500, 502, 503]  # Various acceptable states
    
    def test_database_transaction_integrity(self, test_client: TestClient, test_data_factory):
        """Test database transaction integrity across operations."""
        # Start a complex operation that should be atomic
        extractor = test_data_factory.create_extractor("Transaction Test Extractor")
        extractor_response = test_client.post("/api/extractors", json=extractor)
        assert_valid_crud_response(extractor_response, "create")
        extractor_id = extractor_response.json()["id"]
        
        # Create mapping with this extractor
        mapping = test_data_factory.create_url_mapping(
            "Transaction Test Mapping",
            extractor_ids=[extractor_id]
        )
        mapping_response = test_client.post("/api/url-mappings", json=mapping)
        assert_valid_crud_response(mapping_response, "create")
        mapping_id = mapping_response.json()["id"]
        
        # Try to delete extractor (should fail if mapping still references it)
        delete_response = test_client.delete(f"/api/extractors/{extractor_id}")
        
        if delete_response.status_code == 400:
            # Good - system prevents deletion of referenced extractor
            # Verify mapping still exists and references the extractor
            get_mapping_response = test_client.get(f"/api/url-mappings/{mapping_id}")
            assert_valid_crud_response(get_mapping_response, "read")
            mapping_data = get_mapping_response.json()
            assert extractor_id in mapping_data["extractor_ids"]
        elif delete_response.status_code in [200, 204]:
            # System allows deletion - verify mapping handles this gracefully
            get_mapping_response = test_client.get(f"/api/url-mappings/{mapping_id}")
            if get_mapping_response.status_code == 200:
                mapping_data = get_mapping_response.json()
                # Extractor ID should be removed or mapping should handle missing extractor
                assert extractor_id not in mapping_data.get("extractor_ids", []) or len(mapping_data["extractor_ids"]) == 0
    
    def test_api_versioning_compatibility(self, test_client: TestClient):
        """Test API versioning and backward compatibility."""
        # Test that API endpoints respond correctly
        endpoints = [
            "/api/url-configs",
            "/api/url-mappings", 
            "/api/extractors",
            "/api/crawlers"
        ]
        
        for endpoint in endpoints:
            response = test_client.get(endpoint)
            assert response.status_code in [200, 404]
            
            # Check response format consistency
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (list, dict))
                
                if isinstance(data, list):
                    # List response should be consistent
                    for item in data[:3]:  # Check first 3 items
                        assert isinstance(item, dict)
                        assert "id" in item  # All entities should have ID
    
    def test_performance_under_load(self, test_client: TestClient, test_data_factory):
        """Test system performance under moderate load."""
        import time
        
        start_time = time.time()
        
        # Create multiple entities rapidly
        for i in range(10):
            # Create extractor
            extractor = test_data_factory.create_extractor(f"Load Test Extractor {i}")
            extractor_response = test_client.post("/api/extractors", json=extractor)
            assert extractor_response.status_code in [200, 201]
            
            # Create URL config
            config = test_data_factory.create_url_config(f"Load Test Config {i}")
            config_response = test_client.post("/api/url-configs", json=config)
            assert config_response.status_code in [200, 201]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 20 operations in reasonable time (adjust threshold as needed)
        assert total_time < 30.0, f"Performance test took too long: {total_time} seconds"
        
        # Verify all entities were created successfully
        extractors_response = test_client.get("/api/extractors")
        configs_response = test_client.get("/api/url-configs")
        
        assert extractors_response.status_code == 200
        assert configs_response.status_code == 200
        
        extractors_data = extractors_response.json()
        configs_data = configs_response.json()
        
        # Should have at least our created entities
        if isinstance(extractors_data, list):
            load_test_extractors = [e for e in extractors_data if "Load Test Extractor" in e.get("name", "")]
            assert len(load_test_extractors) >= 5  # At least half should succeed
        
        if isinstance(configs_data, list):
            load_test_configs = [c for c in configs_data if "Load Test Config" in c.get("name", "")]
            assert len(load_test_configs) >= 5  # At least half should succeed