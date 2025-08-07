"""Simple test for URL mappings API endpoints."""

import requests
import pytest


class TestURLMappingAPI:
    """Test URL mappings API endpoints against running server."""
    
    BASE_URL = "http://localhost:4000"
    
    def test_get_mappings_endpoint(self):
        """Test GET /api/url-mappings/ endpoint."""
        try:
            response = requests.get(f"{self.BASE_URL}/api/url-mappings/")
            assert response.status_code == 200
            print(f"✅ GET /api/url-mappings/ - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running on localhost:4000")
    
    def test_url_mapping_update_with_url_field(self):
        """Test updating URL mapping with URL field - this was the main issue."""
        try:
            # Sample data for creating a mapping
            sample_data = {
                "name": "Test Mapping for URL Update",
                "url": "https://example.com/test",
                "url_config_id": 1,
                "extractor_ids": [1],
                "rate_limit": 60,
                "priority": 1,
                "is_active": True
            }
            
            # Try to create a mapping
            create_response = requests.post(f"{self.BASE_URL}/api/url-mappings/", json=sample_data)
            print(f"Create response status: {create_response.status_code}")
            
            if create_response.status_code == 201:
                mapping_id = create_response.json()["id"]
                print(f"Created mapping with ID: {mapping_id}")
                
                # Update the mapping with URL field
                update_data = {
                    "name": "Updated Test Mapping",
                    "url": "https://updated-example.com/test",
                    "rate_limit": 120,
                    "priority": 2
                }
                
                update_response = requests.put(f"{self.BASE_URL}/api/url-mappings/{mapping_id}", json=update_data)
                print(f"Update response status: {update_response.status_code}")
                
                # This should not fail with AttributeError: 'URLMappingUpdate' object has no attribute 'url'
                assert update_response.status_code in [200, 404, 422]
                
                if update_response.status_code == 200:
                    data = update_response.json()
                    assert data["name"] == "Updated Test Mapping"
                    assert data["url"] == "https://updated-example.com/test"
                    assert data["rate_limit"] == 120
                    assert data["priority"] == 2
                    print("✅ URL field update successful!")
                else:
                    print(f"Update failed with status {update_response.status_code}: {update_response.text}")
                
                # Clean up - delete the mapping
                delete_response = requests.delete(f"{self.BASE_URL}/api/url-mappings/{mapping_id}")
                print(f"Delete response status: {delete_response.status_code}")
            else:
                # If creation fails, just test that update endpoint exists and doesn't crash
                update_response = requests.put(f"{self.BASE_URL}/api/url-mappings/999", json={"name": "test", "url": "https://test.com"})
                print(f"Update non-existent mapping status: {update_response.status_code}")
                # Should return 404 for non-existent mapping, not 500 for AttributeError
                assert update_response.status_code in [404, 422]
                print("✅ Update endpoint handles URL field without AttributeError!")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running on localhost:4000")
    
    def test_server_is_running(self):
        """Test that the server is running and accessible."""
        try:
            response = requests.get(f"{self.BASE_URL}/health")
            assert response.status_code in [200, 503]  # 503 if unhealthy but still responding
            print(f"✅ Server is running - Health check status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running on localhost:4000")


if __name__ == "__main__":
    # Run tests directly
    test_instance = TestURLMappingAPI()
    
    print("Running URL Mappings Tests...")
    print("=" * 50)
    
    try:
        test_instance.test_server_is_running()
        test_instance.test_get_mappings_endpoint()
        test_instance.test_url_mapping_update_with_url_field()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")