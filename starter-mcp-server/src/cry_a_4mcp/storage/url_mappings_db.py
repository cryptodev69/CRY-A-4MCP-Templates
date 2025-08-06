"""URL Mappings Database for CRY-A-4MCP.

This module provides database operations for URL mappings, which handle the technical
aspects of URL-to-extractor associations. This is part of the separated architecture
where URL Manager handles business concerns (WHAT/WHY to crawl) and URL Mappings
handles technical concerns (HOW to extract).

Key Features:
    - Technical configuration management (extractors, rate limits, crawler settings)
    - Foreign key relationship to URL configurations
    - CRUD operations for URL mappings
    - JSON field serialization/deserialization
    - Comprehensive error handling and logging
    - Performance indexes for efficient querying

Database Schema:
    url_mappings table with fields:
    - id: Primary key
    - url_config_id: Foreign key to url_configurations.id
    - extractor_id: ID of the extractor to use
    - rate_limit: Rate limiting configuration
    - crawler_settings: Technical crawler parameters
    - validation_rules: Data validation rules
    - is_active: Active status flag
    - metadata: Additional technical metadata
    - created_at/updated_at: Timestamps

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import aiosqlite


class URLMappingsDatabase:
    """Database manager for URL mappings with technical configurations.
    
    This class handles all database operations for URL mappings, which store
    the technical aspects of how to extract data from URLs. It maintains
    a foreign key relationship to the URL configurations managed by the
    URL Manager system.
    
    Attributes:
        db_path (str): Path to the SQLite database file
        logger (logging.Logger): Logger instance for this class
    """
    
    def __init__(self, db_path: str = "url_mappings.db"):
        """Initialize the URL Mappings database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        # Ensure the database directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Create url_mappings table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS url_mappings (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    url_config_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    extractor_ids TEXT NOT NULL,
                    rate_limit INTEGER DEFAULT 60,
                    priority INTEGER DEFAULT 1,
                    crawler_settings TEXT,
                    validation_rules TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    tags TEXT,
                    notes TEXT,
                    category TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create indexes for performance
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_url_mappings_url_config_id ON url_mappings(url_config_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_url_mappings_extractor_ids ON url_mappings(extractor_ids)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_url_mappings_is_active ON url_mappings(is_active)"
            )
            await db.execute("CREATE INDEX IF NOT EXISTS idx_url_mappings_url ON url_mappings(url)")
            
            await db.commit()
            self.logger.info(f"URL Mappings database initialized at {self.db_path}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat()
    
    def _serialize_json_field(self, value: Any) -> str:
        """Serialize a value to JSON string for database storage."""
        if value is None:
            return "{}"
        return json.dumps(value, ensure_ascii=False)
    
    def _deserialize_json_field(self, value: str) -> Any:
        """Deserialize a JSON string from database storage."""
        if not value:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            self.logger.warning(f"Failed to deserialize JSON field: {value}")
            return {}
    
    async def create_mapping(
        self,
        url_config_id: str,
        url: str,
        extractor_ids: List[str],
        name: Optional[str] = None,
        rate_limit: int = 60,
        priority: int = 1,
        crawler_settings: Optional[Dict[str, Any]] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        is_active: bool = True,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new URL mapping.
        
        Args:
            url_config_id: Foreign key to URL configuration
            url: The actual URL to be mapped
            extractor_ids: List of extractor IDs to use
            name: Optional name for the mapping
            rate_limit: Rate limit for requests (default: 60)
            priority: Priority level (1-10, higher = more important, default: 1)
            crawler_settings: Technical crawler parameters
            validation_rules: Data validation rules
            is_active: Whether the mapping is active
            tags: Optional list of tags
            notes: Optional notes
            category: Optional category
            metadata: Additional technical metadata
            
        Returns:
            The ID of the created mapping
        """
        mapping_id = str(uuid.uuid4())
        timestamp = self._get_timestamp()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO url_mappings (
                    id, name, url_config_id, url, extractor_ids, rate_limit, priority,
                    crawler_settings, validation_rules, is_active, tags, notes, category,
                    metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mapping_id,
                name,
                url_config_id,
                url,
                self._serialize_json_field(extractor_ids),
                rate_limit,
                priority,
                self._serialize_json_field(crawler_settings or {}),
                self._serialize_json_field(validation_rules or {}),
                is_active,
                self._serialize_json_field(tags or []),
                notes or "",
                category or "",
                self._serialize_json_field(metadata or {}),
                timestamp,
                timestamp
            ))
            
            await db.commit()
            self.logger.info(f"Created URL mapping: {mapping_id} for config {url_config_id}")
            return mapping_id
    
    async def get_mapping(self, mapping_id: str) -> Optional[Dict[str, Any]]:
        """Get a URL mapping by ID.
        
        Args:
            mapping_id: The mapping ID
            
        Returns:
            Dictionary containing the mapping data, or None if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM url_mappings WHERE id = ?", (mapping_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return self._row_to_dict(row)
            return None
    
    async def get_all_mappings(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all URL mappings.
        
        Args:
            active_only: If True, only return active mappings
            
        Returns:
            List of dictionaries containing mapping data
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if active_only:
                cursor = await db.execute(
                    "SELECT * FROM url_mappings WHERE is_active = 1 ORDER BY created_at DESC"
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM url_mappings ORDER BY created_at DESC"
                )
            
            rows = await cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    async def get_mappings_by_url_config(self, url_config_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get URL mappings for a specific URL configuration.
        
        Args:
            url_config_id: The URL configuration ID
            active_only: If True, only return active mappings
            
        Returns:
            List of dictionaries containing mapping data
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if active_only:
                cursor = await db.execute(
                    "SELECT * FROM url_mappings WHERE url_config_id = ? AND is_active = 1 ORDER BY created_at DESC",
                    (url_config_id,)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM url_mappings WHERE url_config_id = ? ORDER BY created_at DESC",
                    (url_config_id,)
                )
            
            rows = await cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    async def get_mappings_by_extractor(self, extractor_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get URL mappings for a specific extractor.
        
        Args:
            extractor_id: The extractor ID
            active_only: If True, only return active mappings
            
        Returns:
            List of dictionaries containing mapping data
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if active_only:
                cursor = await db.execute(
                    "SELECT * FROM url_mappings WHERE json_extract(extractor_ids, '$') LIKE ? AND is_active = 1 ORDER BY created_at DESC",
                    (f'%"{extractor_id}"%',)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM url_mappings WHERE json_extract(extractor_ids, '$') LIKE ? ORDER BY created_at DESC",
                    (f'%"{extractor_id}"%',)
                )
            
            rows = await cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    async def update_mapping(self, mapping_id: str, **kwargs) -> bool:
        """Update a URL mapping.
        
        Args:
            mapping_id: The mapping ID to update
            **kwargs: Fields to update
            
        Returns:
            True if the mapping was updated, False if not found
        """
        if not kwargs:
            return False
        
        # Handle JSON fields
        json_fields = {'crawler_settings', 'validation_rules', 'metadata', 'tags', 'extractor_ids'}
        
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in json_fields:
                set_clauses.append(f"{key} = ?")
                values.append(self._serialize_json_field(value))
            else:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        # Add updated_at timestamp
        set_clauses.append("updated_at = ?")
        values.append(self._get_timestamp())
        values.append(mapping_id)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"UPDATE url_mappings SET {', '.join(set_clauses)} WHERE id = ?",
                values
            )
            
            await db.commit()
            updated = cursor.rowcount > 0
            
            if updated:
                self.logger.info(f"Updated URL mapping: {mapping_id}")
            
            return updated
    
    async def delete_mapping(self, mapping_id: str) -> bool:
        """Delete a URL mapping.
        
        Args:
            mapping_id: The mapping ID to delete
            
        Returns:
            True if the mapping was deleted, False if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM url_mappings WHERE id = ?", (mapping_id,)
            )
            
            await db.commit()
            deleted = cursor.rowcount > 0
            
            if deleted:
                self.logger.info(f"Deleted URL mapping: {mapping_id}")
            
            return deleted
    
    async def delete_mappings_by_url_config(self, url_config_id: str) -> int:
        """Delete all URL mappings for a specific URL configuration.
        
        Args:
            url_config_id: The URL configuration ID
            
        Returns:
            Number of mappings deleted
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM url_mappings WHERE url_config_id = ?", (url_config_id,)
            )
            
            await db.commit()
            deleted_count = cursor.rowcount
            
            if deleted_count > 0:
                self.logger.info(f"Deleted {deleted_count} URL mappings for config {url_config_id}")
            
            return deleted_count
    
    def _row_to_dict(self, row: aiosqlite.Row) -> Dict[str, Any]:
        """Convert a database row to a dictionary with proper JSON deserialization."""
        data = dict(row)
        
        # Deserialize JSON fields
        json_fields = {'crawler_settings', 'validation_rules', 'metadata', 'tags', 'extractor_ids'}
        
        for field in json_fields:
            if field in data:
                data[field] = self._deserialize_json_field(data[field])
        
        # Convert boolean fields
        if 'is_active' in data:
            data['is_active'] = bool(data['is_active'])
        
        return data
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Total mappings
            cursor = await db.execute("SELECT COUNT(*) FROM url_mappings")
            total_count = (await cursor.fetchone())[0]
            
            # Active mappings
            cursor = await db.execute("SELECT COUNT(*) FROM url_mappings WHERE is_active = 1")
            active_count = (await cursor.fetchone())[0]
            
            # Mappings by extractor
            cursor = await db.execute(
                "SELECT extractor_ids, COUNT(*) FROM url_mappings GROUP BY extractor_ids"
            )
            extractor_counts = dict(await cursor.fetchall())
            
            return {
                'total_mappings': total_count,
                'active_mappings': active_count,
                'inactive_mappings': total_count - active_count,
                'mappings_by_extractor': extractor_counts
            }