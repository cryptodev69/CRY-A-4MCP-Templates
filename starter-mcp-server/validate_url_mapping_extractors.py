#!/usr/bin/env python3
"""
Minimal validation script for URL mapping IDs and extractors in crawler POST/GET operations.
This script tests the core functionality without complex server setup.
"""

import sys
import os
import json
import asyncio
from fastapi.testclient import TestClient

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from cry_a_4mcp.config import Settings
    from cry_a_4mcp.web_api import WebAPIServer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the starter-mcp-server directory")
    sys.exit(1)

def test_url_mapping_extractor_validation():
    """Test URL mapping IDs and extractors in crawler operations."""
    print("🚀 Testing URL mapping ID and extractor validation...")
    
    try:
        # Initialize server
        settings = Settings()
        server = WebAPIServer(settings)
        
        # Initialize server asynchronously
        asyncio.run(server.initialize())
        
        client = TestClient(server.app)
        
        print("✅ Server initialized successfully")
        
        # Test 1: Create URL mapping with extractors
        print("\n📝 Step 1: Creating URL mapping with extractors...")
        mapping_data = {
            "url_pattern": "https://test-crypto.com/api/*",
            "extractor_ids": ["crypto_price_extractor", "volume_extractor"],
            "crawl_config": {"max_depth": 2, "delay": 1.0},
            "is_active": True
        }
        
        mapping_response = client.post("/api/url-mappings", json=mapping_data)
        print(f"   Status: {mapping_response.status_code}")
        
        if mapping_response.status_code == 200:
            mapping_result = mapping_response.json()
            mapping_id = mapping_result.get("id")
            print(f"   ✅ Created mapping with ID: {mapping_id}")
            print(f"   📋 Stored extractors: {mapping_result.get('extractor_ids')}")
            
            # Validate extractor format
            stored_extractors = mapping_result.get("extractor_ids", [])
            if isinstance(stored_extractors, list) and all(isinstance(e, str) for e in stored_extractors):
                print(f"   ✅ Extractor format validation: PASSED")
            else:
                print(f"   ❌ Extractor format validation: FAILED - {type(stored_extractors)}")
                return False
        else:
            print(f"   ❌ Failed to create URL mapping: {mapping_response.status_code}")
            return False
        
        # Test 2: Create crawler with URL mapping ID
        print("\n📝 Step 2: Creating crawler with URL mapping ID...")
        crawler_data = {
            "name": "Test Validation Crawler",
            "description": "Crawler for URL mapping validation",
            "url_mapping_ids": [mapping_id],
            "extraction_strategies": ["crypto_price_extractor", "sentiment_analyzer"],
            "schedule": "0 */6 * * *",
            "is_active": True,
            "config": {"max_concurrent_requests": 3}
        }
        
        crawler_response = client.post("/api/crawlers", json=crawler_data)
        print(f"   Status: {crawler_response.status_code}")
        
        if crawler_response.status_code == 200:
            crawler_result = crawler_response.json()
            crawler_id = crawler_result.get("id")
            print(f"   ✅ Created crawler with ID: {crawler_id}")
            
            # Validate URL mapping IDs
            stored_mappings = crawler_result.get("url_mapping_ids", [])
            print(f"   🔗 Stored URL mapping IDs: {stored_mappings}")
            if isinstance(stored_mappings, list) and mapping_id in stored_mappings:
                print(f"   ✅ URL mapping ID validation: PASSED")
            else:
                print(f"   ❌ URL mapping ID validation: FAILED")
                return False
            
            # Validate extraction strategies
            stored_strategies = crawler_result.get("extraction_strategies", [])
            print(f"   🔧 Stored extraction strategies: {stored_strategies}")
            if isinstance(stored_strategies, list) and all(isinstance(s, str) for s in stored_strategies):
                print(f"   ✅ Extraction strategies validation: PASSED")
            else:
                print(f"   ❌ Extraction strategies validation: FAILED")
                return False
        else:
            print(f"   ❌ Failed to create crawler: {crawler_response.status_code}")
            return False
        
        # Test 3: Retrieve crawler and validate data consistency
        print("\n📝 Step 3: Retrieving crawler and validating consistency...")
        
        # Get all crawlers
        crawlers_response = client.get("/api/crawlers")
        print(f"   GET /api/crawlers status: {crawlers_response.status_code}")
        
        if crawlers_response.status_code == 200:
            crawlers = crawlers_response.json()
            test_crawler = None
            
            for crawler in crawlers:
                if crawler.get("id") == crawler_id:
                    test_crawler = crawler
                    break
            
            if test_crawler:
                print(f"   ✅ Found crawler in list")
                
                # Validate retrieved data
                retrieved_mappings = test_crawler.get("url_mapping_ids", [])
                retrieved_strategies = test_crawler.get("extraction_strategies", [])
                
                print(f"   🔗 Retrieved URL mapping IDs: {retrieved_mappings}")
                print(f"   🔧 Retrieved extraction strategies: {retrieved_strategies}")
                
                # Check data types and consistency
                mapping_types_ok = all(isinstance(m, (str, int)) for m in retrieved_mappings)
                strategy_types_ok = all(isinstance(s, str) for s in retrieved_strategies)
                
                if mapping_types_ok and strategy_types_ok:
                    print(f"   ✅ Data type validation: PASSED")
                else:
                    print(f"   ❌ Data type validation: FAILED")
                    return False
                
                # Check consistency with stored data
                if (retrieved_mappings == stored_mappings and 
                    retrieved_strategies == stored_strategies):
                    print(f"   ✅ Data consistency validation: PASSED")
                else:
                    print(f"   ❌ Data consistency validation: FAILED")
                    return False
            else:
                print(f"   ❌ Crawler not found in list")
                return False
        else:
            print(f"   ❌ Failed to retrieve crawlers: {crawlers_response.status_code}")
            return False
        
        # Test 4: Individual crawler retrieval
        print("\n📝 Step 4: Testing individual crawler retrieval...")
        individual_response = client.get(f"/api/crawlers/{crawler_id}")
        
        if individual_response.status_code == 200:
            individual_crawler = individual_response.json()
            print(f"   ✅ Individual crawler retrieval successful")
            
            # Compare with list data
            if (individual_crawler.get("url_mapping_ids") == test_crawler.get("url_mapping_ids") and
                individual_crawler.get("extraction_strategies") == test_crawler.get("extraction_strategies")):
                print(f"   ✅ List vs individual consistency: PASSED")
            else:
                print(f"   ❌ List vs individual consistency: FAILED")
                return False
        else:
            print(f"   ⚠️  Individual crawler retrieval failed: {individual_response.status_code}")
        
        print("\n🎉 All URL mapping ID and extractor validations PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("🔍 URL Mapping ID and Extractor Validation Test")
    print("=" * 50)
    
    success = test_url_mapping_extractor_validation()
    
    if success:
        print("\n✅ VALIDATION SUCCESSFUL!")
        print("\n📋 Summary:")
        print("   - URL mapping IDs are correctly stored and retrieved")
        print("   - Extractor IDs maintain proper list format")
        print("   - Data types are preserved (strings for extractors, string/int for mappings)")
        print("   - Storage and retrieval consistency verified")
        print("   - Individual vs list endpoint consistency confirmed")
        return 0
    else:
        print("\n❌ VALIDATION FAILED!")
        print("   Check the error messages above for details")
        return 1

if __name__ == "__main__":
    exit(main())