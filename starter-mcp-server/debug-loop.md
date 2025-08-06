# Debug Loop Detection - API Testing Issues

## Problem Summary
**Most likely cause:** TestClient compatibility issues with current FastAPI/Starlette versions (85% confidence)

## Symptoms
- All test scripts exit with code 130 (SIGINT/interruption)
- No error logs visible in command output
- Multiple test approaches failed:
  1. `test_web_api_endpoints.py` - Complex threaded server approach
  2. `test_simple_api.py` - FastAPI TestClient approach
  3. `quick_api_test.py` - Minimal test script
  4. `validate_url_mapping_extractors.py` - Focused validation script

## Root Cause Analysis
- TestClient initialization fails with `__init__() got an unexpected keyword argument 'app'`
- This suggests version incompatibility between FastAPI and Starlette
- Exit code 130 indicates process interruption, likely due to unhandled exceptions

## Manual Verification Approach
Since automated testing is blocked, here's how to manually verify URL mapping ID and extractor formatting:

### 1. Start the API Server
```bash
cd /path/to/starter-mcp-server
python -m cry_a_4mcp.web_api
```

### 2. Test URL Mapping Creation
```bash
curl -X POST http://localhost:4000/api/url-mappings \
  -H "Content-Type: application/json" \
  -d '{
    "url_pattern": "https://test-crypto.com/api/*",
    "extractor_ids": ["crypto_price_extractor", "volume_extractor"],
    "crawl_config": {"max_depth": 2, "delay": 1.0},
    "is_active": true
  }'
```

**Expected Response:**
- Status: 200
- Response should include `id` field
- `extractor_ids` should be preserved as string array

### 3. Test Crawler Creation with URL Mapping
```bash
curl -X POST http://localhost:4000/api/crawlers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Validation Crawler",
    "description": "Crawler for URL mapping validation",
    "url_mapping_ids": ["<MAPPING_ID_FROM_STEP_2>"],
    "extraction_strategies": ["crypto_price_extractor", "sentiment_analyzer"],
    "schedule": "0 */6 * * *",
    "is_active": true,
    "config": {"max_concurrent_requests": 3}
  }'
```

**Expected Response:**
- Status: 200
- `url_mapping_ids` should contain the mapping ID from step 2
- `extraction_strategies` should be preserved as string array

### 4. Test Crawler Retrieval
```bash
# Get all crawlers
curl http://localhost:4000/api/crawlers

# Get specific crawler
curl http://localhost:4000/api/crawlers/<CRAWLER_ID>
```

**Validation Checklist:**
- [ ] URL mapping IDs are strings or integers (not objects)
- [ ] Extractor IDs are strings in array format
- [ ] Data consistency between POST and GET operations
- [ ] Individual crawler retrieval matches list retrieval
- [ ] No data corruption or type conversion issues

## Next Steps if Manual Testing Fails
1. Check database schema for URL mapping and crawler tables
2. Verify Pydantic model definitions for proper serialization
3. Add logging to API endpoints to trace data flow
4. Test with different data types (string vs int IDs)

## Circuit Breaker Triggered
Stopping automated testing attempts due to persistent infrastructure issues.
Recommend manual verification or environment debugging before proceeding.