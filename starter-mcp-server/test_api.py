#!/usr/bin/env python3
import requests
import json

# Test URL configurations endpoint
print("Testing URL configurations endpoint...")
try:
    response = requests.get("http://localhost:4000/api/url-configurations/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test URL mapping creation with a valid config ID
print("Testing URL mapping creation...")
try:
    # First, let's try to get available configurations
    configs_response = requests.get("http://localhost:4000/api/url-configurations/")
    if configs_response.status_code == 200:
        configs = configs_response.json()
        print(f"Available configurations: {configs}")
        
        if configs and len(configs) > 0:
            # Use the first available config ID
            config_id = configs[0].get('id', '1')
            print(f"Using config ID: {config_id}")
        else:
            config_id = "test-config-1"
            print(f"No configs found, using test ID: {config_id}")
    else:
        config_id = "test-config-1"
        print(f"Could not fetch configs, using test ID: {config_id}")
    
    # Test URL mapping creation
    mapping_data = {
        "url_config_id": config_id,
        "extractor_ids": ["extractor1", "extractor2"],
        "rate_limit": 60,
        "priority": 1,
        "is_active": True
    }
    
    response = requests.post(
        "http://localhost:4000/api/url-mappings/",
        json=mapping_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")