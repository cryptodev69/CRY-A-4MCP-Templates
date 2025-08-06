#!/usr/bin/env python3
"""Update database schema to support the new business-focused architecture."""

import asyncio
import aiosqlite
import sys
import os
from pathlib import Path

async def update_url_configurations_schema():
    """Update the url_configurations database schema."""
    print("🔧 Updating URL configurations database schema...")
    
    db_path = "url_configurations.db"
    
    try:
        async with aiosqlite.connect(db_path) as db:
            # Check if the table exists
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='url_configurations'"
            )
            table_exists = await cursor.fetchone()
            
            if not table_exists:
                print("📋 Creating new url_configurations table...")
                # Create the new table with the complete schema
                await db.execute("""
                    CREATE TABLE url_configurations (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        url TEXT NOT NULL,
                        profile_type TEXT NOT NULL,
                        category TEXT NOT NULL,
                        description TEXT,
                        business_priority INTEGER DEFAULT 1,
                        business_value TEXT,
                        compliance_notes TEXT,
                        url_patterns TEXT DEFAULT '[]',
                        extractor_ids TEXT DEFAULT '[]',
                        crawler_settings TEXT DEFAULT '{}',
                        rate_limit INTEGER DEFAULT 60,
                        validation_rules TEXT DEFAULT '{}',
                        key_data_points TEXT DEFAULT '[]',
                        target_data TEXT DEFAULT '{}',
                        cost_analysis TEXT DEFAULT '{}',
                        scraping_difficulty TEXT,
                        has_official_api BOOLEAN DEFAULT FALSE,
                        api_pricing TEXT,
                        recommendation TEXT,
                        rationale TEXT,
                        metadata TEXT DEFAULT '{}',
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Created new url_configurations table")
            else:
                print("📋 Table exists, checking for missing columns...")
                
                # Get current table schema
                cursor = await db.execute("PRAGMA table_info(url_configurations)")
                columns = await cursor.fetchall()
                existing_columns = {col[1] for col in columns}  # col[1] is column name
                
                # Define required columns with their definitions
                required_columns = {
                    'business_priority': 'INTEGER DEFAULT 1',
                    'business_value': 'TEXT',
                    'compliance_notes': 'TEXT'
                }
                
                # Add missing columns
                for column_name, column_def in required_columns.items():
                    if column_name not in existing_columns:
                        print(f"➕ Adding column: {column_name}")
                        await db.execute(f"ALTER TABLE url_configurations ADD COLUMN {column_name} {column_def}")
                
                # Check if we need to remove old columns (priority -> business_priority)
                if 'priority' in existing_columns and 'business_priority' in existing_columns:
                    print("🔄 Migrating priority data to business_priority...")
                    await db.execute("UPDATE url_configurations SET business_priority = priority WHERE business_priority IS NULL")
            
            await db.commit()
            print("✅ URL configurations database schema updated successfully!")
            
            # Verify the schema
            cursor = await db.execute("PRAGMA table_info(url_configurations)")
            columns = await cursor.fetchall()
            print(f"📊 URL configurations table now has {len(columns)} columns")
            
            return True
            
    except Exception as e:
        print(f"❌ URL configurations schema update failed: {e}")
        return False

async def update_url_mappings_schema():
    """Update the url_mappings database schema."""
    print("🔧 Updating URL mappings database schema...")
    
    db_path = "url_mappings.db"
    
    try:
        async with aiosqlite.connect(db_path) as db:
            # Check if the table exists
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='url_mappings'"
            )
            table_exists = await cursor.fetchone()
            
            if not table_exists:
                print("📋 Creating new url_mappings table...")
                # Create the new table with the complete schema
                await db.execute("""
                    CREATE TABLE url_mappings (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        url TEXT NOT NULL,
                        config_id TEXT NOT NULL,
                        extractor_id TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        priority INTEGER DEFAULT 1,
                        tags TEXT DEFAULT '[]',
                        notes TEXT,
                        category TEXT,
                        rate_limit INTEGER DEFAULT 60,
                        crawler_settings TEXT DEFAULT '{}',
                        validation_rules TEXT DEFAULT '{}',
                        is_active BOOLEAN DEFAULT 1,
                        last_crawled TEXT,
                        crawl_frequency INTEGER DEFAULT 3600,
                        success_rate REAL DEFAULT 0.0,
                        error_count INTEGER DEFAULT 0,
                        metadata TEXT DEFAULT '{}',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (config_id) REFERENCES url_configurations (id)
                    )
                """)
                print("✅ Created new url_mappings table")
            else:
                print("📋 URL mappings table exists, checking for missing columns...")
                
                # Get current table schema
                cursor = await db.execute("PRAGMA table_info(url_mappings)")
                columns = await cursor.fetchall()
                existing_columns = {col[1] for col in columns}  # col[1] is column name
                
                # Define required columns with their definitions
                required_columns = {
                    'name': 'TEXT',
                    'url': 'TEXT',
                    'config_id': 'TEXT',
                    'extractor_id': 'TEXT',
                    'status': 'TEXT DEFAULT "active"',
                    'priority': 'INTEGER DEFAULT 1',
                    'tags': 'TEXT DEFAULT "[]"',
                    'notes': 'TEXT',
                    'category': 'TEXT',
                    'rate_limit': 'INTEGER DEFAULT 60',
                    'crawler_settings': 'TEXT DEFAULT "{}"',
                    'validation_rules': 'TEXT DEFAULT "{}"',
                    'is_active': 'BOOLEAN DEFAULT 1',
                    'last_crawled': 'TEXT',
                    'crawl_frequency': 'INTEGER DEFAULT 3600',
                    'success_rate': 'REAL DEFAULT 0.0',
                    'error_count': 'INTEGER DEFAULT 0',
                    'metadata': 'TEXT DEFAULT "{}"',
                    'created_at': 'TEXT DEFAULT CURRENT_TIMESTAMP',
                    'updated_at': 'TEXT DEFAULT CURRENT_TIMESTAMP'
                }
                
                # Add missing columns
                for column_name, column_def in required_columns.items():
                    if column_name not in existing_columns:
                        print(f"➕ Adding column: {column_name}")
                        await db.execute(f"ALTER TABLE url_mappings ADD COLUMN {column_name} {column_def}")
            
            await db.commit()
            print("✅ URL mappings database schema updated successfully!")
            
            # Verify the schema
            cursor = await db.execute("PRAGMA table_info(url_mappings)")
            columns = await cursor.fetchall()
            print(f"📊 URL mappings table now has {len(columns)} columns")
            
            return True
            
    except Exception as e:
        print(f"❌ URL mappings schema update failed: {e}")
        return False

async def update_database_schema():
    """Update both database schemas."""
    print("🔧 Starting database schema updates...")
    
    success1 = await update_url_configurations_schema()
    success2 = await update_url_mappings_schema()
    
    if success1 and success2:
        print("✅ All database schemas updated successfully!")
        return True
    else:
        print("❌ Some database schema updates failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(update_database_schema())
    sys.exit(0 if success else 1)