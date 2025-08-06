#!/usr/bin/env python3
"""Quick API test to verify POST and GET functionality."""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastapi.testclient import TestClient
    from cry_a_4mcp.config import Settings
    from cry_a_4mcp.web_api import WebAPIServer
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def main():
    print("🚀 Quick API Test")
    
    try:
        # Create server without async initialization
        settings = Settings()
        server = WebAPIServer(settings)
        print("✅ Server created")
        
        # Create test client
        client = TestClient(server.app)
        print("✅ TestClient created")
        
        # Test basic GET endpoint
        print("\n📊 Testing GET /api/url-configs...")
        response = client.get("/api/url-configs")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET successful: {len(data)} items")
        else:
            print(f"⚠️  GET returned status {response.status_code}")
        
        # Test basic POST endpoint
        print("\n📝 Testing POST /api/url-configs...")
        test_data = {
            "name": "Test Config",
            "url": "https://example.com",
            "description": "Test description",
            "category": "test",
            "extraction_strategy": "test_strategy",
            "update_frequency": "hourly",
            "is_active": True
        }
        
        response = client.post("/api/url-configs", json=test_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ POST successful: Created item with ID {data.get('id')}")
        else:
            print(f"⚠️  POST returned status {response.status_code}")
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Error text: {response.text}")
        
        print("\n✅ Quick API test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Test passed!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)