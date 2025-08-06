"""URL Mapping Database Manager.

This module provides database operations for URL mappings, which handle the
technical aspects of associating URLs with extraction strategies. This is
separate from the URL Configuration system which handles business metadata.

The URL Mapping system focuses purely on technical configuration:
- Which extractor to use for a URL
- Rate limiting settings
- Technical validation rules
- Crawler-specific settings
"""

import aiosqlite
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging


class URLMappingDatabase:
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
        """Initialize the URL mapping database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS url_mappings (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        url TEXT NOT NULL,
                        url_config_id TEXT,
                        extractor_id TEXT NOT NULL,
                        priority INTEGER DEFAULT 5,
                        rate_limit INTEGER DEFAULT 60,
                        config TEXT,
                        validation_rules TEXT,
                        crawler_settings TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        metadata TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        FOREIGN KEY (url_config_id) REFERENCES url_configurations(id)
                    )
                """)
                
                # Create indexes for performance
                await db.execute("CREATE INDEX IF NOT EXISTS idx_url_mappings_url_config_id ON url_mappings(url_config_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_url_mappings_extractor_id ON url_mappings(extractor_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_url_mappings_is_active ON url_mappings(is_active)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_url_mappings_url ON url_mappings(url)")
                
                await db.commit()
                self.logger.info("URL mappings database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize URL mappings database: {e}")
            raise
    
    def _generate_id(self) -> str:
        """Generate a unique ID for URL mappings."""
        return f"mapping_{uuid.uuid4()}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat() + "Z"
    
    def _serialize_json_field(self, value: Any) -> str:
        """Serialize a value to JSON string for database storage."""
        if value is None:
            return "{}"
        if isinstance(value, str):
            try:
                # Validate it's valid JSON
                json.loads(value)
                return value
            except json.JSONDecodeError:
                # If it's not valid JSON, wrap it
                return json.dumps(value)
        return json.dumps(value)
    
    def _deserialize_json_field(self, value: str) -> Any:
        """Deserialize a JSON string from database."""
        if not value:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}
    
    async def create_mapping(
        self,
        name: str,
        url: str,
        extractor_id: str,
        url_config_id: Optional[str] = None,
        priority: int = 5,
        rate_limit: int = 60,
        config: Optional[Dict[str, Any]] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        crawler_settings: Optional[Dict[str, Any]] = None,
        is_active: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new URL mapping.
        
        Args:
            name: Name/title of the mapping
            url: URL for mapping to extractor
            extractor_id: Which extractor to use
            url_config_id: Foreign key to url_configurations.id
            priority: Technical processing priority
            rate_limit: Rate limiting setting
            config: Extractor-specific configuration
            validation_rules: Technical validation rules
            crawler_settings: Crawler-specific settings
            is_active: Whether this mapping is active
            metadata: Additional technical metadata
        
        Returns:
            The ID of the newly created mapping
        """
        mapping_id = self._generate_id()
        timestamp = self._get_timestamp()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO url_mappings (
                    id, name, url, url_config_id, extractor_id, priority,
                    rate_limit, config, validation_rules, crawler_settings,
                    is_active, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mapping_id, name, url, url_config_id, extractor_id, priority,
                rate_limit, self._serialize_json_field(config),
                self._serialize_json_field(validation_rules),
                self._serialize_json_field(crawler_settings),
                is_active, self._serialize_json_field(metadata),
                timestamp, timestamp
            ))
            await db.commit()
        
        self.logger.info(f"Created URL mapping: {mapping_id}")
        return mapping_id
    
    async def get_mapping(self, mapping_id: str) -> Optional[Dict[str, Any]]:
        """Get a URL mapping by ID.
        
        Args:
            mapping_id: The mapping ID to retrieve
        
        Returns:
            Dictionary containing the mapping data, or None if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM url_mappings WHERE id = ?", (mapping_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return self._row_to_dict(row)
                return None
    
    async def get_all_mappings(self) -> List[Dict[str, Any]]:
        """Get all URL mappings.
        
        Returns:
            List of dictionaries containing mapping data
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM url_mappings ORDER BY created_at DESC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
    
    async def get_mappings_by_url_config(self, url_config_id: str) -> List[Dict[str, Any]]:
        """Get all mappings for a specific URL configuration.
        
        Args:
            url_config_id: The URL configuration ID
        
        Returns:
            List of dictionaries containing mapping data
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM url_mappings WHERE url_config_id = ? ORDER BY priority DESC",
                (url_config_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
    
    async def get_mappings_by_extractor(self, extractor_id: str) -> List[Dict[str, Any]]:
        """Get all mappings for a specific extractor.
        
        Args:
            extractor_id: The extractor ID
        
        Returns:
            List of dictionaries containing mapping data
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM url_mappings WHERE json_extract(extractor_ids, '$') LIKE ? ORDER BY priority DESC",
                (f'%"{extractor_id}"%',)
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
    
    async def update_mapping(self, mapping_id: str, **kwargs) -> bool:
        """Update an existing URL mapping.
        
        Args:
            mapping_id: The mapping ID to update
            **kwargs: Fields to update
        
        Returns:
            True if update was successful, False otherwise
        """
        if not kwargs:
            return True
        
        # Handle JSON fields
        json_fields = ['config', 'validation_rules', 'crawler_settings', 'metadata']
        for field in json_fields:
            if field in kwargs:
                kwargs[field] = self._serialize_json_field(kwargs[field])
        
        # Add updated timestamp
        kwargs['updated_at'] = self._get_timestamp()
        
        # Build dynamic update query
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [mapping_id]
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"UPDATE url_mappings SET {set_clause} WHERE id = ?",
                values
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def delete_mapping(self, mapping_id: str) -> bool:
        """Delete a URL mapping.
        
        Args:
            mapping_id: The mapping ID to delete
        
        Returns:
            True if deletion was successful, False otherwise
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM url_mappings WHERE id = ?", (mapping_id,)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def delete_mappings_by_url_config(self, url_config_id: str) -> int:
        """Delete all mappings for a specific URL configuration.
        
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
            return cursor.rowcount
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert a database row to a dictionary.
        
        Args:
            row: SQLite row object
        
        Returns:
            Dictionary representation of the row
        """
        columns = [
            'id', 'name', 'url', 'url_config_id', 'extractor_id', 'priority',
            'rate_limit', 'config', 'validation_rules', 'crawler_settings',
            'is_active', 'metadata', 'created_at', 'updated_at'
        ]
        
        result = dict(zip(columns, row))
        
        # Deserialize JSON fields
        json_fields = ['config', 'validation_rules', 'crawler_settings', 'metadata']
        for field in json_fields:
            if result[field]:
                result[field] = self._deserialize_json_field(result[field])
        
        return result
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary containing database statistics
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Total mappings
            async with db.execute("SELECT COUNT(*) FROM url_mappings") as cursor:
                total_mappings = (await cursor.fetchone())[0]
            
            # Active mappings
            async with db.execute("SELECT COUNT(*) FROM url_mappings WHERE is_active = 1") as cursor:
                active_mappings = (await cursor.fetchone())[0]
            
            # Mappings by extractor
            async with db.execute("""
                SELECT extractor_id, COUNT(*) as count 
                FROM url_mappings 
                GROUP BY extractor_id 
                ORDER BY count DESC
            """) as cursor:
                extractor_stats = await cursor.fetchall()
            
            return {
                "total_mappings": total_mappings,
                "active_mappings": active_mappings,
                "inactive_mappings": total_mappings - active_mappings,
                "extractor_distribution": dict(extractor_stats)
            }