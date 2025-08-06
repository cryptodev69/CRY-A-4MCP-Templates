# URL Mapping Integration Testing

This directory contains comprehensive test scripts to validate the URL mapping persistence functionality in the CRY-A-4MCP crawler system.

## 🚨 Critical Issue Being Tested

The URL mapping persistence issue where `url_mapping_id` and `target_urls` fields are `null` or empty in backend responses, despite frontend data being sent correctly.

## 📁 Test Files

### `test_url_mapping_integration.py`
Comprehensive integration test suite that validates:
- Backend API endpoints for URL mappings and crawlers
- Data transformation between frontend and backend
- Persistence of URL mapping data in crawler configurations
- Error handling and edge cases
- Complete CRUD operations for crawlers with URL mappings

### `run_tests.py`
Simple test runner script for quick validation of URL mapping services.

## 🚀 Quick Start

### Prerequisites
1. Backend server running on `localhost:4001`
2. Python 3.7+ with `aiohttp` installed

```bash
# Install required dependencies
pip install aiohttp

# Make scripts executable
chmod +x test_url_mapping_integration.py
chmod +x run_tests.py
```

### Running Tests

#### Option 1: Quick Test Run
```bash
python run_tests.py
```

#### Option 2: Direct Integration Test
```bash
python test_url_mapping_integration.py
```

#### Option 3: Custom Backend URL
```bash
python run_tests.py --backend-url http://localhost:4001
```

#### Option 4: Verbose Output
```bash
python run_tests.py --verbose
```

## 🧪 Test Coverage

The integration tests cover the following scenarios:

### 1. Backend Health Check
- Verifies backend server is running and responsive
- Tests basic connectivity

### 2. URL Mapping Creation
- Creates a test URL mapping via API
- Validates response structure and ID generation
- Tests data persistence

### 3. Crawler Creation with URL Mapping
- Creates a crawler with URL mapping reference
- **CRITICAL**: Tests if `urlMappingId` and `targetUrls` from frontend are properly stored
- Validates that `url_mapping_id` and `target_urls` are not null in response

### 4. URL Mapping Persistence Verification
- Retrieves created crawler and verifies URL mapping data persists
- **CRITICAL**: Checks if `url_mapping_id` and `target_urls` fields contain expected values
- Tests JSON serialization/deserialization of URL arrays

### 5. Crawler List Validation
- Verifies crawler list endpoint includes URL mapping data
- Tests data consistency across different API endpoints

### 6. Update Operations
- Tests updating crawler URL mapping configuration
- Validates that updates persist correctly

### 7. Cleanup
- Removes test data to avoid pollution
- Tests delete operations

## 📊 Expected Test Results

### ✅ If URL Mapping Persistence is Working
```
✅ Backend Health Check: PASS
✅ Create URL Mapping: PASS
✅ Create Crawler with URL Mapping: PASS
✅ Retrieve Crawler - URL Mapping Persistence: PASS
✅ Crawler List - URL Mapping Data: PASS
✅ Update Crawler URL Mapping: PASS
✅ Cleanup Test Data: PASS

📊 TEST SUMMARY
============================================================
Total Tests: 7
✅ Passed: 7
❌ Failed: 0
⏭️ Skipped: 0
Success Rate: 100.0%

✅ ALL INTEGRATION TESTS PASSED - URL mapping persistence is working correctly!
```

### ❌ If URL Mapping Persistence is Broken
```
✅ Backend Health Check: PASS
✅ Create URL Mapping: PASS
❌ Create Crawler with URL Mapping: FAIL
   Error: URL mapping data not properly stored. Got: url_mapping_id=None, target_urls=None
⏭️ Retrieve Crawler - URL Mapping Persistence: SKIP
⏭️ Crawler List - URL Mapping Data: SKIP
⏭️ Update Crawler URL Mapping: SKIP
✅ Cleanup Test Data: PASS

📊 TEST SUMMARY
============================================================
Total Tests: 7
✅ Passed: 3
❌ Failed: 1
⏭️ Skipped: 3
Success Rate: 42.9%

🔍 FAILED TESTS:
  • Create Crawler with URL Mapping: URL mapping data not properly stored. Got: url_mapping_id=None, target_urls=None

❌ INTEGRATION TESTS FAILED - URL mapping persistence is not working correctly!
```

## 🔧 Debugging Failed Tests

### Common Issues and Solutions

#### 1. Backend Not Running
```
❌ Backend Health Check: FAIL
   Error: Cannot connect to backend: Connection refused
```
**Solution**: Start the backend server on `localhost:4001`

#### 2. URL Mapping Data Not Persisting
```
❌ Create Crawler with URL Mapping: FAIL
   Error: URL mapping data not properly stored. Got: url_mapping_id=None, target_urls=None
```
**This is the critical issue!** Check:
- `web_api.py` - ensure `urlMappingId` and `targetUrls` are correctly mapped
- `crawler_db.py` - verify `url_mapping_id` and `target_urls` are in SQL statements
- Database schema - ensure columns exist and accept the data types

#### 3. JSON Serialization Issues
```
❌ Retrieve Crawler - URL Mapping Persistence: FAIL
   Error: target_urls is not valid JSON: ["url1", "url2"]
```
**Solution**: Check JSON encoding/decoding in database operations

## 🛠️ Manual Testing

If automated tests fail, you can manually test using curl:

### 1. Create URL Mapping
```bash
curl -X POST http://localhost:4001/api/url-mappings \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Manual Test Mapping",
    "urls": ["https://test.com"],
    "extractor_ids": ["cryptoinvestorllmextractionstrategy"]
  }'
```

### 2. Create Crawler with URL Mapping
```bash
curl -X POST http://localhost:4001/api/crawlers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Manual Test Crawler",
    "crawler_type": "llm",
    "urlMappingId": "<mapping_id_from_step_1>",
    "targetUrls": ["https://test.com/page1"]
  }'
```

### 3. Verify Persistence
```bash
curl http://localhost:4001/api/crawlers/<crawler_id_from_step_2>
```

Check if the response contains non-null values for `url_mapping_id` and `target_urls`.

## 📝 Test Data Structure

The tests use the following data structures:

### URL Mapping
```json
{
  "name": "Test Integration Mapping",
  "description": "Test mapping for integration testing",
  "urls": ["https://test-crypto-news.com", "https://test-market-data.com"],
  "extractor_ids": ["cryptoinvestorllmextractionstrategy", "xcryptohunterllmextractionstrategy"],
  "priority": 1,
  "rate_limit": 2,
  "crawler_settings": {
    "timeout": 30,
    "retry_attempts": 3,
    "user_agent": "CRY-A-4MCP-Test/1.0"
  }
}
```

### Crawler with URL Mapping
```json
{
  "name": "Test Integration Crawler",
  "description": "Test crawler with URL mapping integration",
  "crawler_type": "llm",
  "is_active": true,
  "urlMappingId": "<generated_mapping_id>",
  "targetUrls": ["https://test-crypto-news.com/latest", "https://test-market-data.com/prices"],
  "config": {
    "timeout": 30,
    "retry_attempts": 3,
    "concurrent_requests": 5
  }
}
```

## 🎯 Success Criteria

The URL mapping persistence is considered **WORKING** when:

1. ✅ All 7 integration tests pass
2. ✅ `url_mapping_id` field contains the correct mapping ID (not null)
3. ✅ `target_urls` field contains the correct URL array (not null/empty)
4. ✅ Data persists across API calls (create → retrieve → list)
5. ✅ Updates to URL mapping data work correctly
6. ✅ No data loss during frontend-backend communication

## 🚨 Current Status

As documented in `CRY-A-4MCP_Crawler_Architecture_README.md`, the URL mapping persistence is currently **BROKEN**. These tests will help identify exactly where the data flow is failing and validate when the issue is resolved.

---

**Run these tests after any changes to URL mapping functionality to ensure the critical persistence issue is resolved!**