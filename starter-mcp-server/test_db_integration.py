#!/usr/bin/env python3
"""Test script to verify database integration after architectural separation."""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cry_a_4mcp.storage.url_configuration_db import URLConfigurationDatabase
from cry_a_4mcp.storage.url_mapping_db import URLMappingDatabase

async def test_database_integration():
    """Test that both databases can be initialized and work correctly."""
    print("🔧 Testing database integration...")
    
    # Initialize databases
    config_db = URLConfigurationDatabase()
    mapping_db = URLMappingDatabase()
    
    try:
        # Test initialization
        await config_db.initialize()
        print("✅ URL Configuration Database initialized successfully")
        
        await mapping_db.initialize()
        print("✅ URL Mapping Database initialized successfully")
        
        # Test basic operations
        configs = await config_db.get_all_configurations()
        print(f"📊 Found {len(configs)} URL configurations")
        
        mappings = await mapping_db.get_all_mappings()
        print(f"📊 Found {len(mappings)} URL mappings")
        
        print("\n🎉 Database integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_database_integration())
    sys.exit(0 if success else 1)