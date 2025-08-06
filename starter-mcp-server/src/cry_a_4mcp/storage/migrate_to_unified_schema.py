"""Migration script to unify url_configs and url_mappings into url_configurations.

This script migrates data from the existing separate url_configs and url_mappings
tables into the new unified url_configurations table, handling data type
conversions and schema differences.
"""

import asyncio
import aiosqlite
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .url_configuration_db import URLConfigurationDatabase


class UnifiedSchemaMigration:
    """Handles migration from separate schemas to unified schema."""
    
    def __init__(self, 
                 old_url_configs_db: str = "url_configs.db",
                 old_url_mappings_db: str = "url_mappings.db",
                 new_unified_db: str = "url_configurations.db"):
        """Initialize migration with database paths.
        
        Args:
            old_url_configs_db: Path to existing url_configs database
            old_url_mappings_db: Path to existing url_mappings database
            new_unified_db: Path to new unified database
        """
        self.old_url_configs_db = old_url_configs_db
        self.old_url_mappings_db = old_url_mappings_db
        self.new_unified_db = new_unified_db
        self.logger = logging.getLogger(__name__)
        
        # Initialize the new unified database manager
        self.unified_db = URLConfigurationDatabase(new_unified_db)
    
    def _convert_text_to_json(self, value: Any, default: Any = None) -> str:
        """Convert text fields to JSON format for the unified schema.
        
        Args:
            value: The value to convert
            default: Default value if conversion fails
        
        Returns:
            JSON string representation
        """
        if value is None:
            return json.dumps(default)
        
        if isinstance(value, str):
            # Try to parse as JSON first
            try:
                parsed = json.loads(value)
                return json.dumps(parsed)
            except json.JSONDecodeError:
                # If it's a plain string, convert based on expected type
                if default is None:
                    return json.dumps(value)
                elif isinstance(default, list):
                    # Convert comma-separated string to list
                    if ',' in value:
                        return json.dumps([item.strip() for item in value.split(',')])
                    else:
                        return json.dumps([value.strip()])
                elif isinstance(default, dict):
                    # Try to create a simple dict structure
                    return json.dumps({"value": value})
                else:
                    return json.dumps(value)
        
        return json.dumps(value)
    
    def _generate_id(self) -> str:
        """Generate a unique ID for migrated records."""
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    async def check_existing_databases(self) -> Dict[str, bool]:
        """Check which databases exist and are accessible.
        
        Returns:
            Dictionary indicating which databases exist
        """
        status = {
            'url_configs_exists': False,
            'url_mappings_exists': False,
            'url_configs_accessible': False,
            'url_mappings_accessible': False
        }
        
        # Check url_configs database
        if Path(self.old_url_configs_db).exists():
            status['url_configs_exists'] = True
            try:
                async with aiosqlite.connect(self.old_url_configs_db) as db:
                    cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='url_configs'")
                    if await cursor.fetchone():
                        status['url_configs_accessible'] = True
            except Exception as e:
                self.logger.warning(f"Cannot access url_configs database: {e}")
        
        # Check url_mappings database
        if Path(self.old_url_mappings_db).exists():
            status['url_mappings_exists'] = True
            try:
                async with aiosqlite.connect(self.old_url_mappings_db) as db:
                    cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='url_mappings'")
                    if await cursor.fetchone():
                        status['url_mappings_accessible'] = True
            except Exception as e:
                self.logger.warning(f"Cannot access url_mappings database: {e}")
        
        return status
    
    async def migrate_url_configs(self) -> int:
        """Migrate data from url_configs table to unified schema.
        
        Returns:
            Number of records migrated
        """
        migrated_count = 0
        
        try:
            async with aiosqlite.connect(self.old_url_configs_db) as old_db:
                old_db.row_factory = aiosqlite.Row
                cursor = await old_db.execute("SELECT * FROM url_configs")
                rows = await cursor.fetchall()
                
                for row in rows:
                    row_dict = dict(row)
                    
                    # Map old schema to new schema
                    config_data = {
                        'name': row_dict.get('name', 'Migrated Config'),
                        'url': row_dict.get('url', ''),
                        'profile_type': row_dict.get('profile_type', 'unknown'),
                        'category': row_dict.get('category', 'general'),
                        'description': row_dict.get('description'),
                        'priority': row_dict.get('priority', 1),
                        'scraping_difficulty': row_dict.get('scraping_difficulty'),
                        'has_official_api': bool(row_dict.get('has_official_api', False)),
                        'api_pricing': row_dict.get('api_pricing'),
                        'recommendation': row_dict.get('recommendation'),
                        'rationale': row_dict.get('rationale'),
                        'is_active': True,  # Default to active for migrated configs
                    }
                    
                    # Handle JSON fields - convert from TEXT to JSON
                    config_data['key_data_points'] = self._parse_json_field(
                        row_dict.get('key_data_points'), []
                    )
                    config_data['target_data'] = self._parse_json_field(
                        row_dict.get('target_data'), {}
                    )
                    config_data['cost_analysis'] = self._parse_json_field(
                        row_dict.get('cost_analysis'), {}
                    )
                    
                    # Set defaults for fields not in old schema
                    config_data['url_patterns'] = [row_dict.get('url', '')]
                    config_data['extractor_ids'] = []
                    config_data['crawler_settings'] = {}
                    config_data['rate_limit'] = 60
                    config_data['validation_rules'] = {}
                    config_data['metadata'] = {
                        'migrated_from': 'url_configs',
                        'original_id': row_dict.get('id'),
                        'migration_timestamp': self._get_timestamp()
                    }
                    
                    # Create the configuration in the unified database
                    await self.unified_db.create_configuration(**config_data)
                    migrated_count += 1
                    
                self.logger.info(f"Migrated {migrated_count} records from url_configs")
                
        except Exception as e:
            self.logger.error(f"Error migrating url_configs: {e}")
            raise
        
        return migrated_count
    
    async def migrate_url_mappings(self) -> int:
        """Migrate data from url_mappings table to unified schema.
        
        Returns:
            Number of records migrated
        """
        migrated_count = 0
        
        try:
            async with aiosqlite.connect(self.old_url_mappings_db) as old_db:
                old_db.row_factory = aiosqlite.Row
                cursor = await old_db.execute("SELECT * FROM url_mappings")
                rows = await cursor.fetchall()
                
                for row in rows:
                    row_dict = dict(row)
                    
                    # Map old schema to new schema
                    config_data = {
                        'name': row_dict.get('name', 'Migrated Mapping'),
                        'url': row_dict.get('url', ''),
                        'profile_type': row_dict.get('profile_type', 'unknown'),
                        'category': row_dict.get('category', 'general'),
                        'description': row_dict.get('description'),
                        'priority': row_dict.get('priority', 1),
                        'scraping_difficulty': row_dict.get('scraping_difficulty'),
                        'has_official_api': bool(row_dict.get('has_official_api', False)),
                        'api_pricing': row_dict.get('api_pricing'),
                        'recommendation': row_dict.get('recommendation'),
                        'rationale': row_dict.get('rationale'),
                        'rate_limit': row_dict.get('rate_limit', 60),
                        'is_active': True,  # Default to active for migrated mappings
                    }
                    
                    # Handle JSON fields - these should already be JSON in url_mappings
                    config_data['url_patterns'] = self._parse_json_field(
                        row_dict.get('urls'), [row_dict.get('url', '')]
                    )
                    config_data['key_data_points'] = self._parse_json_field(
                        row_dict.get('key_data_points'), []
                    )
                    config_data['target_data'] = self._parse_json_field(
                        row_dict.get('target_data'), {}
                    )
                    config_data['cost_analysis'] = self._parse_json_field(
                        row_dict.get('cost_analysis'), {}
                    )
                    config_data['extractor_ids'] = self._parse_json_field(
                        row_dict.get('extractor_ids'), []
                    )
                    config_data['crawler_settings'] = self._parse_json_field(
                        row_dict.get('crawler_settings'), {}
                    )
                    config_data['validation_rules'] = self._parse_json_field(
                        row_dict.get('validation_rules'), {}
                    )
                    
                    # Set metadata for tracking migration
                    config_data['metadata'] = {
                        'migrated_from': 'url_mappings',
                        'original_id': row_dict.get('id'),
                        'migration_timestamp': self._get_timestamp()
                    }
                    
                    # Create the configuration in the unified database
                    await self.unified_db.create_configuration(**config_data)
                    migrated_count += 1
                    
                self.logger.info(f"Migrated {migrated_count} records from url_mappings")
                
        except Exception as e:
            self.logger.error(f"Error migrating url_mappings: {e}")
            raise
        
        return migrated_count
    
    def _parse_json_field(self, value: Any, default: Any) -> Any:
        """Parse a JSON field from the old database.
        
        Args:
            value: The value to parse
            default: Default value if parsing fails
        
        Returns:
            Parsed value or default
        """
        if value is None:
            return default
        
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # If it's not valid JSON, try to convert based on default type
                if isinstance(default, list) and ',' in value:
                    return [item.strip() for item in value.split(',')]
                elif isinstance(default, dict):
                    return {"value": value}
                else:
                    return default
        
        return value if value is not None else default
    
    async def create_backup(self) -> Dict[str, str]:
        """Create backups of existing databases before migration.
        
        Returns:
            Dictionary with backup file paths
        """
        backup_paths = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup url_configs if it exists
        if Path(self.old_url_configs_db).exists():
            backup_path = f"{self.old_url_configs_db}.backup_{timestamp}"
            import shutil
            shutil.copy2(self.old_url_configs_db, backup_path)
            backup_paths['url_configs'] = backup_path
            self.logger.info(f"Created backup: {backup_path}")
        
        # Backup url_mappings if it exists
        if Path(self.old_url_mappings_db).exists():
            backup_path = f"{self.old_url_mappings_db}.backup_{timestamp}"
            import shutil
            shutil.copy2(self.old_url_mappings_db, backup_path)
            backup_paths['url_mappings'] = backup_path
            self.logger.info(f"Created backup: {backup_path}")
        
        return backup_paths
    
    async def run_migration(self, create_backups: bool = True) -> Dict[str, Any]:
        """Run the complete migration process.
        
        Args:
            create_backups: Whether to create backups before migration
        
        Returns:
            Migration results summary
        """
        self.logger.info("Starting unified schema migration")
        
        # Check existing databases
        db_status = await self.check_existing_databases()
        self.logger.info(f"Database status: {db_status}")
        
        # Create backups if requested
        backup_paths = {}
        if create_backups:
            backup_paths = await self.create_backup()
        
        # Initialize the new unified database
        await self.unified_db.initialize()
        
        # Migrate data
        url_configs_migrated = 0
        url_mappings_migrated = 0
        
        if db_status['url_configs_accessible']:
            url_configs_migrated = await self.migrate_url_configs()
        
        if db_status['url_mappings_accessible']:
            url_mappings_migrated = await self.migrate_url_mappings()
        
        # Get final statistics
        stats = await self.unified_db.get_database_stats()
        
        migration_result = {
            'success': True,
            'database_status': db_status,
            'backup_paths': backup_paths,
            'records_migrated': {
                'url_configs': url_configs_migrated,
                'url_mappings': url_mappings_migrated,
                'total': url_configs_migrated + url_mappings_migrated
            },
            'final_stats': stats,
            'unified_database_path': self.new_unified_db
        }
        
        self.logger.info(f"Migration completed successfully: {migration_result}")
        return migration_result


async def main():
    """Main migration function for command-line execution."""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize migration
    migration = UnifiedSchemaMigration()
    
    try:
        # Run migration
        result = await migration.run_migration(create_backups=True)
        
        print("\n" + "="*50)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"Total records migrated: {result['records_migrated']['total']}")
        print(f"  - From url_configs: {result['records_migrated']['url_configs']}")
        print(f"  - From url_mappings: {result['records_migrated']['url_mappings']}")
        print(f"\nUnified database: {result['unified_database_path']}")
        
        if result['backup_paths']:
            print("\nBackup files created:")
            for db_name, backup_path in result['backup_paths'].items():
                print(f"  - {db_name}: {backup_path}")
        
        print(f"\nFinal database statistics:")
        for key, value in result['final_stats'].items():
            print(f"  - {key}: {value}")
        
    except Exception as e:
        print(f"\nMIGRATION FAILED: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())