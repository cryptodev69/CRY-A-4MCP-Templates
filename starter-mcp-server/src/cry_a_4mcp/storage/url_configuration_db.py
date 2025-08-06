"""URL Configuration Database Manager.

This module provides database operations for URL configurations, which handle the
business aspects of URL management. This is separate from the URL Mapping system
which handles technical extraction configurations.

The URL Configuration system focuses purely on business metadata:
- Business categorization and profiling
- Cost analysis and recommendations
- Target data descriptions
- Business rationale and priorities
"""

import aiosqlite
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging


class URLConfigurationDatabase:
    """Database manager for URL configurations with business metadata.
    
    This class handles all database operations for URL configurations, which store
    the business aspects of URL management. It maintains separation from the
    technical URL mapping system.
    
    Attributes:
        db_path (str): Path to the SQLite database file
        logger (logging.Logger): Logger instance for this class
    """
    
    def __init__(self, db_path: str = "url_configurations.db"):
        """Initialize the URL configuration database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize the database and create the business-focused table schema."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create the business-focused url_configurations table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS url_configurations (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        url TEXT NOT NULL,
                        profile_type TEXT NOT NULL,
                        category TEXT NOT NULL,
                        business_priority INTEGER DEFAULT 1,
                        scraping_difficulty TEXT,
                        has_official_api BOOLEAN DEFAULT 0,
                        api_pricing TEXT,
                        recommendation TEXT,
                        key_data_points TEXT,  -- JSON array
                        target_data TEXT,  -- JSON object
                        rationale TEXT,
                        cost_analysis TEXT,  -- JSON object
                        business_value TEXT,
                        compliance_notes TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        metadata TEXT,  -- JSON object for business metadata
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
            
                # Create performance indexes for business queries
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_url_configs_profile_type 
                    ON url_configurations(profile_type)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_url_configs_category 
                    ON url_configurations(category)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_url_configs_business_priority 
                    ON url_configurations(business_priority DESC)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_url_configs_active 
                    ON url_configurations(is_active)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_url_configs_url 
                    ON url_configurations(url)
                """)
                
                await db.commit()
                self.logger.info("URL configuration database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize URL configuration database: {e}")
            raise
    
    def _generate_id(self) -> str:
        """Generate a unique ID for new configurations."""
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def _serialize_json_field(self, value: Any) -> str:
        """Serialize a value to JSON string for database storage."""
        if value is None:
            return json.dumps(None)
        if isinstance(value, str):
            try:
                # If it's already a JSON string, validate it
                json.loads(value)
                return value
            except json.JSONDecodeError:
                # If it's a plain string, convert to JSON
                return json.dumps(value)
        return json.dumps(value)
    
    def _deserialize_json_field(self, value: Optional[str]) -> Any:
        """Deserialize a JSON string from database storage."""
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            # Fallback to original value if not valid JSON
            return value
    
    async def create_configuration(
        self,
        name: str,
        url: str,
        profile_type: str,
        category: str,
        description: Optional[str] = None,
        business_priority: int = 1,
        scraping_difficulty: Optional[str] = None,
        has_official_api: bool = False,
        api_pricing: Optional[str] = None,
        recommendation: Optional[str] = None,
        key_data_points: Optional[List[str]] = None,
        target_data: Optional[Dict[str, Any]] = None,
        rationale: Optional[str] = None,
        cost_analysis: Optional[Dict[str, Any]] = None,
        business_value: Optional[str] = None,
        compliance_notes: Optional[str] = None,
        is_active: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new URL configuration with business metadata.
        
        Args:
            name: Name/title of the configuration
            url: Primary URL for this configuration
            profile_type: Target user profile type
            category: Business category classification
            description: Business description
            business_priority: Business priority level (higher = more important)
            scraping_difficulty: Business assessment of difficulty
            has_official_api: Whether an official API is available
            api_pricing: API pricing information
            recommendation: Business recommendation
            key_data_points: List of key business data points
            target_data: Target business data structure
            rationale: Business rationale for inclusion
            cost_analysis: Business cost analysis
            business_value: Assessment of business value
            compliance_notes: Compliance and legal notes
            is_active: Whether this configuration is active
            metadata: Additional business metadata
        
        Returns:
            The ID of the newly created configuration
        """
        config_id = self._generate_id()
        timestamp = self._get_timestamp()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO url_configurations (
                    id, name, description, url, profile_type, category,
                    business_priority, scraping_difficulty, has_official_api, api_pricing,
                    recommendation, key_data_points, target_data, rationale,
                    cost_analysis, business_value, compliance_notes, is_active, 
                    metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                config_id, name, description, url,
                profile_type, category, business_priority, scraping_difficulty,
                has_official_api, api_pricing, recommendation,
                self._serialize_json_field(key_data_points or []),
                self._serialize_json_field(target_data or {}),
                rationale,
                self._serialize_json_field(cost_analysis or {}),
                business_value, compliance_notes, is_active,
                self._serialize_json_field(metadata or {}),
                timestamp, timestamp
            ))
            
            await db.commit()
            self.logger.info(f"Created URL configuration: {name} (ID: {config_id})")
            return config_id
    
    async def get_configuration(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Get a URL configuration by ID.
        
        Args:
            config_id: The configuration ID
        
        Returns:
            Dictionary containing the configuration data, or None if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM url_configurations WHERE id = ?", (config_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return self._row_to_dict(row)
            return None
    
    async def get_all_configurations(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all URL configurations.
        
        Args:
            active_only: If True, only return active configurations
        
        Returns:
            List of dictionaries containing configuration data
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if active_only:
                cursor = await db.execute(
                    "SELECT * FROM url_configurations WHERE is_active = 1 ORDER BY business_priority DESC, name ASC"
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM url_configurations ORDER BY business_priority DESC, name ASC"
                )
            
            rows = await cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    async def get_configurations_by_profile(self, profile_type: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get URL configurations for a specific profile type.
        
        Args:
            profile_type: The profile type to filter by
            active_only: If True, only return active configurations
        
        Returns:
            List of dictionaries containing configuration data
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if active_only:
                cursor = await db.execute(
                    "SELECT * FROM url_configurations WHERE profile_type = ? AND is_active = 1 ORDER BY business_priority DESC, name ASC",
                    (profile_type,)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM url_configurations WHERE profile_type = ? ORDER BY business_priority DESC, name ASC",
                    (profile_type,)
                )
            
            rows = await cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    async def get_configurations_by_category(self, category: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get URL configurations for a specific category.
        
        Args:
            category: The category to filter by
            active_only: If True, only return active configurations
        
        Returns:
            List of dictionaries containing configuration data
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if active_only:
                cursor = await db.execute(
                    "SELECT * FROM url_configurations WHERE category = ? AND is_active = 1 ORDER BY business_priority DESC, name ASC",
                    (category,)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM url_configurations WHERE category = ? ORDER BY business_priority DESC, name ASC",
                    (category,)
                )
            
            rows = await cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    async def update_configuration(self, config_id: str, **kwargs) -> bool:
        """Update a URL configuration.
        
        Args:
            config_id: The configuration ID to update
            **kwargs: Fields to update
        
        Returns:
            True if the configuration was updated, False if not found
        """
        if not kwargs:
            return False
        
        # Handle JSON fields
        json_fields = {
            'key_data_points', 'target_data', 'cost_analysis', 'metadata'
        }
        
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
        values.append(config_id)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"UPDATE url_configurations SET {', '.join(set_clauses)} WHERE id = ?",
                values
            )
            
            await db.commit()
            updated = cursor.rowcount > 0
            
            if updated:
                self.logger.info(f"Updated URL configuration: {config_id}")
            
            return updated
    
    async def delete_configuration(self, config_id: str) -> bool:
        """Delete a URL configuration.
        
        Args:
            config_id: The configuration ID to delete
        
        Returns:
            True if the configuration was deleted, False if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM url_configurations WHERE id = ?", (config_id,)
            )
            
            await db.commit()
            deleted = cursor.rowcount > 0
            
            if deleted:
                self.logger.info(f"Deleted URL configuration: {config_id}")
            
            return deleted
    
    async def search_configurations(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Search URL configurations by text query.
        
        Args:
            query: Search query
            fields: List of fields to search in (default: name, description, url)
            active_only: If True, only search active configurations
        
        Returns:
            List of matching configurations
        """
        if fields is None:
            fields = ['name', 'description', 'url']
        
        search_conditions = []
        search_values = []
        
        for field in fields:
            search_conditions.append(f"{field} LIKE ?")
            search_values.append(f"%{query}%")
        
        where_clause = f"({' OR '.join(search_conditions)})"
        if active_only:
            where_clause += " AND is_active = 1"
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                f"SELECT * FROM url_configurations WHERE {where_clause} ORDER BY business_priority DESC, name ASC",
                search_values
            )
            
            rows = await cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def _row_to_dict(self, row: aiosqlite.Row) -> Dict[str, Any]:
        """Convert a database row to a dictionary with proper JSON deserialization."""
        data = dict(row)
        
        # Deserialize JSON fields
        json_fields = {
            'key_data_points', 'target_data', 'cost_analysis', 'metadata'
        }
        
        for field in json_fields:
            if field in data:
                data[field] = self._deserialize_json_field(data[field])
        
        # Convert boolean fields
        if 'has_official_api' in data:
            data['has_official_api'] = bool(data['has_official_api'])
        if 'is_active' in data:
            data['is_active'] = bool(data['is_active'])
        
        return data
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Total configurations
            cursor = await db.execute("SELECT COUNT(*) FROM url_configurations")
            total_count = (await cursor.fetchone())[0]
            
            # Active configurations
            cursor = await db.execute("SELECT COUNT(*) FROM url_configurations WHERE is_active = 1")
            active_count = (await cursor.fetchone())[0]
            
            # Configurations by profile type
            cursor = await db.execute(
                "SELECT profile_type, COUNT(*) FROM url_configurations GROUP BY profile_type"
            )
            profile_counts = dict(await cursor.fetchall())
            
            # Configurations by category
            cursor = await db.execute(
                "SELECT category, COUNT(*) FROM url_configurations GROUP BY category"
            )
            category_counts = dict(await cursor.fetchall())
            
            return {
                'total_configurations': total_count,
                'active_configurations': active_count,
                'inactive_configurations': total_count - active_count,
                'configurations_by_profile': profile_counts,
                'configurations_by_category': category_counts
            }