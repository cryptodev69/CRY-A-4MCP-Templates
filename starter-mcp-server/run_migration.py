#!/usr/bin/env python3
"""Run database migration to update schema for architectural separation."""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cry_a_4mcp.storage.migrate_to_unified_schema import UnifiedSchemaMigration

async def run_migration():
    """Run the database migration."""
    print("🔧 Starting database migration...")
    
    try:
        migrator = UnifiedSchemaMigration()
        result = await migrator.run_migration()
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_migration())
    sys.exit(0 if success else 1)