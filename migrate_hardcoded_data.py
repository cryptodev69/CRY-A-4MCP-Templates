#!/usr/bin/env python3
"""
Migration script to populate URL mappings database with hardcoded data.

This script reads the backup_url_Manager_list.md file and populates the
URL mappings database with the predefined data.
"""

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add the src directory to the Python path
src_path = Path(__file__).parent / "starter-mcp-server" / "src"
sys.path.insert(0, str(src_path))

from cry_a_4mcp.storage.url_mapping_db import URLMappingDatabase


def load_hardcoded_data() -> List[Dict[str, Any]]:
    """
    Load hardcoded URL mapping data from the backup file.
        
    Returns:
        List of dictionaries containing URL mapping data
    """
    backup_file = Path(__file__).parent / "docs" / "backup_url_Manager_list.md"
    
    if not backup_file.exists():
        print(f"Backup file not found: {backup_file}")
        return []
    
    try:
        content = backup_file.read_text(encoding='utf-8')
        
        # The file contains a JavaScript array - convert to valid JSON
        # Remove any leading/trailing whitespace and find the array
        content = content.strip()
        
        print(f"Content length: {len(content)}")
        print(f"Content starts with: {repr(content[:20])}")
        print(f"Content ends with: {repr(content[-20:])}")
        
        # Check if content starts with '[' (JavaScript array)
        if not content.startswith('['):
            print("Content does not start with '[' - not a JavaScript array")
            return []
        
        # If content doesn't end with ']', try to fix it by finding the last '}' and adding ']'
        if not content.endswith(']'):
            print("Content doesn't end with ']' - attempting to fix...")
            last_brace_index = content.rfind('}')
            if last_brace_index != -1:
                content = content[:last_brace_index + 1] + '\n]'
                print(f"Fixed content, now ends with: {repr(content[-10:])}")
            else:
                print("Could not find closing brace to fix array")
                return []
        
        # Convert JavaScript object notation to JSON
        # Step 1: Replace unquoted property names with quoted ones
        js_content = re.sub(r'(\s+|\{\s*)(\w+)\s*:', r'\1"\2":', content)
        
        # Step 2: Replace single quotes with double quotes for string values
        # This regex handles strings that may contain escaped quotes or apostrophes
        js_content = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'(?=\s*[,}\]])", 
                           lambda m: '"' + m.group(1).replace('\\"', '"').replace('"', '\\"') + '"', 
                           js_content)
        
        # Parse as JSON
        data = json.loads(js_content)
        print(f"Successfully loaded {len(data)} URL mappings from backup file")
        return data
        
    except Exception as e:
        print(f"Error loading backup data: {e}")
        print(f"Content length: {len(content) if 'content' in locals() else 'unknown'}")
        if 'content' in locals():
            print(f"Content starts with: {repr(content[:50])}")
            print(f"Content ends with: {repr(content[-50:])}")
        return []


def transform_data_for_db(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform raw data to match database schema.
    
    Args:
        raw_data: Raw data from backup file
        
    Returns:
        Transformed data ready for database insertion
    """
    transformed = []
    
    for item in raw_data:
        # Map to database schema
        db_item = {
            'name': item.get('name', ''),
            'description': item.get('description', ''),
            'url': item.get('url', ''),
            'urls': [item.get('url', '')] if item.get('url') else [],  # Single URL as array
            'profile_type': item.get('profile_type', ''),
            'category': item.get('category', ''),
            'extractor_ids': ['default'],  # Default extractor as array
            'crawler_settings': {},  # Empty settings for now
            'priority': item.get('priority', 1),
            'scraping_difficulty': item.get('scraping_difficulty', ''),
            'has_official_api': item.get('has_official_api', False),
            'api_pricing': item.get('api_pricing', ''),
            'recommendation': item.get('recommendation', ''),
            'key_data_points': item.get('key_data_points', '').split(', ') if item.get('key_data_points') else [],
            'target_data': {'description': item.get('target_data', '')},
            'rationale': item.get('rationale', ''),
            'cost_analysis': {'description': item.get('cost_analysis', '')},
            'rate_limit': 60,  # Default rate limit
            'validation_rules': {}  # Empty validation rules for now
        }
        
        transformed.append(db_item)
    
    return transformed


async def migrate_data():
    """
    Main migration function.
    """
    print("Starting URL mapping data migration...")
    
    # Initialize database
    db = URLMappingDatabase()
    await db.initialize()
    
    # Load hardcoded data
    raw_data = load_hardcoded_data()
    
    if not raw_data:
        print("No data to migrate")
        return
    
    # Transform data
    transformed_data = transform_data_for_db(raw_data)
    
    # Insert/update data
    created_count = 0
    updated_count = 0
    
    for mapping_data in transformed_data:
        try:
            # Check if mapping already exists by name
            existing = None
            try:
                # Try to find by name (we'll need to implement this or use a different approach)
                # For now, just try to create and handle conflicts
                mapping_id = await db.create_mapping(mapping_data)
                print(f"Created mapping: {mapping_data['name']} (ID: {mapping_id})")
                created_count += 1
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"Mapping already exists: {mapping_data['name']} - skipping")
                else:
                    print(f"Error creating mapping {mapping_data['name']}: {e}")
        except Exception as e:
            print(f"Error processing mapping {mapping_data.get('name', 'unknown')}: {e}")
    
    print(f"Migration completed: {created_count} created, {updated_count} updated")


if __name__ == "__main__":
    asyncio.run(migrate_data())