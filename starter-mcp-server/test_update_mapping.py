#!/usr/bin/env python3

import asyncio
import json
import aiohttp

async def test_update_mapping():
    """Test URL mapping update with the new schema."""
    
    # Update data that matches what the frontend is sending
    update_data = {
        "name": "Updated Test Mapping",
        "url_config_id": "7b185ecc-3182-4363-8367-a5bb4ff88d72",
        "extractor_ids": [
            "CompositeExtractionStrategy",
            "ExtractionError",
            "APIResponseError"
        ],
        "rate_limit": 60,
        "priority": 1,
        "crawler_settings": {
            "timeout": 30000,
            "retryAttempts": 3,
            "retryDelay": 1000
        },
        "validation_rules": {},
        "is_active": True,
        "tags": ["updated", "test"],
        "notes": "Updated test notes",
        "category": "updated"
    }
    
    # Use the mapping ID from the previous creation
    mapping_id = "cbfffc2e-f202-4638-99bc-458a137b97f3"
    
    async with aiohttp.ClientSession() as session:
        print(f"🔄 Testing update for mapping ID: {mapping_id}")
        async with session.put(
            f'http://localhost:4000/api/url-mappings/{mapping_id}',
            json=update_data,
            headers={'Content-Type': 'application/json'}
        ) as update_response:
            print(f"📡 Update response status: {update_response.status}")
            
            if update_response.status == 200:
                result = await update_response.json()
                print("✅ Update successful!")
                print(f"📋 Updated mapping name: {result.get('name')}")
                print(f"📋 Updated mapping notes: {result.get('notes')}")
                print(f"📋 Updated mapping category: {result.get('category')}")
                print(f"📋 Updated mapping tags: {result.get('tags')}")
                print(f"📋 Full response: {json.dumps(result, indent=2)}")
            else:
                error_text = await update_response.text()
                print(f"❌ Update failed: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_update_mapping())