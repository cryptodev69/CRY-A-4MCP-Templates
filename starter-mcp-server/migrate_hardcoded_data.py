#!/usr/bin/env python3
"""
Migration script to populate URL mappings database with hardcoded data.

This script reads the backup_url_Manager_list.md file and populates the
URL mappings database with the comprehensive crypto platform data.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

from cry_a_4mcp.storage.url_mapping_db import URLMappingDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_hardcoded_data():
    """Load hardcoded URL manager data from backup file."""
    backup_file = Path(__file__).parent.parent / "docs" / "backup_url_Manager_list.md"
    
    if not backup_file.exists():
        logger.error(f"Backup file not found: {backup_file}")
        return []
    
    try:
        content = backup_file.read_text().strip()
        
        # The file contains JavaScript object notation, not JSON
        # We need to convert it to proper JSON format
        
        # Extract the array content
        json_start = content.find('[{')
        json_end = content.rfind('}]') + 2
        
        if json_start == -1 or json_end == 1:
            logger.error("Could not find JavaScript array data in backup file")
            return []
        
        js_data = content[json_start:json_end]
        
        # Convert JavaScript object notation to JSON
        import re
        
        # Fix unquoted property names
        js_data = re.sub(r'(\w+):', r'"\1":', js_data)
        
        # Fix single quotes to double quotes
        js_data = js_data.replace("'", '"')
        
        # Parse JSON
        data = json.loads(js_data)
        
        logger.info(f"Loaded {len(data)} URL manager entries from backup")
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JavaScript object notation: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading backup data: {e}")
        return []


async def transform_data_for_db(hardcoded_data):
    """Transform hardcoded data to match database schema."""
    transformed = []
    
    for item in hardcoded_data:
        # Map hardcoded fields to database schema
        db_item = {
            "name": item.get("name", ""),
            "description": item.get("description", ""),
            "url": item.get("url", ""),
            "urls": [item.get("url", "")] if item.get("url") else [],
            "profile_type": item.get("profile_type", ""),
            "category": item.get("category", ""),
            "priority": item.get("priority", 1),
            "scraping_difficulty": item.get("scraping_difficulty", ""),
            "has_official_api": item.get("has_official_api", False),
            "api_pricing": item.get("api_pricing", ""),
            "recommendation": item.get("recommendation", ""),
            "key_data_points": item.get("key_data_points", []),
            "target_data": item.get("target_data", {}),
            "rationale": item.get("rationale", ""),
            "cost_analysis": item.get("cost_analysis", {}),
            "extractor_ids": [],  # Will be populated later when extractors are created
            "crawler_settings": {},
            "rate_limit": 60,  # Default rate limit
            "validation_rules": {}
        }
        
        transformed.append(db_item)
    
    return transformed


async def migrate_data():
    """Main migration function."""
    logger.info("Starting URL mappings migration...")
    
    # Initialize database
    db = URLMappingDatabase("url_mappings.db")
    await db.initialize()
    
    # Load hardcoded data
    hardcoded_data = await load_hardcoded_data()
    if not hardcoded_data:
        logger.error("No data to migrate")
        return
    
    # Transform data for database
    db_data = await transform_data_for_db(hardcoded_data)
    
    # Check if data already exists
    existing_mappings = await db.get_all_mappings()
    if existing_mappings:
        logger.warning(f"Database already contains {len(existing_mappings)} mappings")
        response = input("Do you want to continue and add more data? (y/N): ")
        if response.lower() != 'y':
            logger.info("Migration cancelled")
            return
    
    # Insert data
    success_count = 0
    error_count = 0
    
    for item in db_data:
        try:
            mapping_id = await db.create_mapping(item)
            logger.info(f"Created mapping: {item['name']} (ID: {mapping_id})")
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to create mapping for {item['name']}: {e}")
            error_count += 1
    
    logger.info(f"Migration completed: {success_count} successful, {error_count} errors")
    
    # Verify migration
    final_mappings = await db.get_all_mappings()
    logger.info(f"Total mappings in database: {len(final_mappings)}")


if __name__ == "__main__":
    asyncio.run(migrate_data())