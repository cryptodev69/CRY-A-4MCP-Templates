import os
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class URLConfigDatabase:
    """Database manager for URL configurations.
    
    This class provides methods for storing and retrieving URL configuration data,
    including metadata, scraping difficulty, API information, and target data points.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the URL configuration database.
        
        Args:
            db_path: Path to the SQLite database file. If None, a default path will be used.
        """
        if db_path is None:
            # Create default path in the config directory
            config_dir = Path(__file__).parent.parent / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(config_dir / "url_configs.db")
        
        self.db_path = db_path
        self.conn = None
        self.initialize_db()
    
    def initialize_db(self):
        """Initialize the database schema."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Create url_configs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS url_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    profile_type TEXT NOT NULL,
                    description TEXT,
                    scraping_difficulty INTEGER NOT NULL,
                    has_official_api BOOLEAN DEFAULT FALSE,
                    api_pricing TEXT,
                    recommendation TEXT,
                    key_data_points TEXT,
                    target_data TEXT,
                    rationale TEXT,
                    cost_analysis TEXT,
                    third_party_apis TEXT,
                    category TEXT,
                    priority INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info(f"URL Config Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            if self.conn:
                self.conn.close()
            raise
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def add_url_config(self, config_data: Dict[str, Any]) -> int:
        """Add a new URL configuration to the database.
        
        Args:
            config_data: Dictionary containing URL configuration data
            
        Returns:
            ID of the inserted configuration
        """
        try:
            cursor = self.conn.cursor()
            
            # Convert lists/dicts to JSON strings
            for field in ['key_data_points', 'target_data', 'third_party_apis']:
                if isinstance(config_data.get(field), (list, dict)):
                    config_data[field] = json.dumps(config_data[field])
            
            cursor.execute('''
                INSERT INTO url_configs 
                (name, url, profile_type, description, scraping_difficulty, has_official_api,
                 api_pricing, recommendation, key_data_points, target_data, rationale,
                 cost_analysis, third_party_apis, category, priority, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                config_data.get('name', ''),
                config_data.get('url', ''),
                config_data.get('profile_type', ''),
                config_data.get('description', ''),
                config_data.get('scraping_difficulty', 1),
                config_data.get('has_official_api', False),
                config_data.get('api_pricing', ''),
                config_data.get('recommendation', ''),
                config_data.get('key_data_points', '[]'),
                config_data.get('target_data', '[]'),
                config_data.get('rationale', ''),
                config_data.get('cost_analysis', ''),
                config_data.get('third_party_apis', '[]'),
                config_data.get('category', 'general'),
                config_data.get('priority', 1),
                config_data.get('is_active', True)
            ))
            
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding URL config: {e}")
            self.conn.rollback()
            raise
    
    def update_url_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Update an existing URL configuration in the database.
        
        Args:
            config_name: Name of the configuration to update
            config_data: Dictionary containing updated configuration data
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            # Convert lists/dicts to JSON strings
            for field in ['key_data_points', 'target_data', 'third_party_apis']:
                if isinstance(config_data.get(field), (list, dict)):
                    config_data[field] = json.dumps(config_data[field])
            
            cursor.execute('''
                UPDATE url_configs
                SET url = ?,
                    profile_type = ?,
                    description = ?,
                    scraping_difficulty = ?,
                    has_official_api = ?,
                    api_pricing = ?,
                    recommendation = ?,
                    key_data_points = ?,
                    target_data = ?,
                    rationale = ?,
                    cost_analysis = ?,
                    third_party_apis = ?,
                    category = ?,
                    priority = ?,
                    is_active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            ''', (
                config_data.get('url', ''),
                config_data.get('profile_type', ''),
                config_data.get('description', ''),
                config_data.get('scraping_difficulty', 1),
                config_data.get('has_official_api', False),
                config_data.get('api_pricing', ''),
                config_data.get('recommendation', ''),
                config_data.get('key_data_points', '[]'),
                config_data.get('target_data', '[]'),
                config_data.get('rationale', ''),
                config_data.get('cost_analysis', ''),
                config_data.get('third_party_apis', '[]'),
                config_data.get('category', 'general'),
                config_data.get('priority', 1),
                config_data.get('is_active', True),
                config_name
            ))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating URL config: {e}")
            self.conn.rollback()
            return False
    
    def get_url_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get a URL configuration by name.
        
        Args:
            config_name: Name of the configuration to retrieve
            
        Returns:
            Dictionary containing configuration data or None if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, name, url, profile_type, description, scraping_difficulty,
                       has_official_api, api_pricing, recommendation, key_data_points,
                       target_data, rationale, cost_analysis, third_party_apis,
                       category, priority, is_active, created_at, updated_at
                FROM url_configs
                WHERE name = ?
            ''', (config_name,))
            
            row = cursor.fetchone()
            if row:
                config = {
                    'id': row[0],
                    'name': row[1],
                    'url': row[2],
                    'profile_type': row[3],
                    'description': row[4],
                    'scraping_difficulty': row[5],
                    'has_official_api': bool(row[6]),
                    'api_pricing': row[7],
                    'recommendation': row[8],
                    'key_data_points': json.loads(row[9]) if row[9] else [],
                    'target_data': json.loads(row[10]) if row[10] else [],
                    'rationale': row[11],
                    'cost_analysis': row[12],
                    'third_party_apis': json.loads(row[13]) if row[13] else [],
                    'category': row[14],
                    'priority': row[15],
                    'is_active': bool(row[16]),
                    'created_at': row[17],
                    'updated_at': row[18]
                }
                return config
            return None
        except Exception as e:
            logger.error(f"Error getting URL config: {e}")
            return None
    
    def get_all_url_configs(self, profile_type: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all URL configurations from the database.
        
        Args:
            profile_type: Filter by profile type (optional)
            active_only: Only return active configurations
            
        Returns:
            List of dictionaries containing configuration data
        """
        try:
            cursor = self.conn.cursor()
            
            query = '''
                SELECT id, name, url, profile_type, description, scraping_difficulty,
                       has_official_api, api_pricing, recommendation, key_data_points,
                       target_data, rationale, cost_analysis, third_party_apis,
                       category, priority, is_active, created_at, updated_at
                FROM url_configs
            '''
            
            conditions = []
            params = []
            
            if active_only:
                conditions.append("is_active = ?")
                params.append(True)
            
            if profile_type:
                conditions.append("profile_type = ?")
                params.append(profile_type)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY priority DESC, name ASC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            configs = []
            for row in rows:
                config = {
                    'id': row[0],
                    'name': row[1],
                    'url': row[2],
                    'profile_type': row[3],
                    'description': row[4],
                    'scraping_difficulty': row[5],
                    'has_official_api': bool(row[6]),
                    'api_pricing': row[7],
                    'recommendation': row[8],
                    'key_data_points': json.loads(row[9]) if row[9] else [],
                    'target_data': json.loads(row[10]) if row[10] else [],
                    'rationale': row[11],
                    'cost_analysis': row[12],
                    'third_party_apis': json.loads(row[13]) if row[13] else [],
                    'category': row[14],
                    'priority': row[15],
                    'is_active': bool(row[16]),
                    'created_at': row[17],
                    'updated_at': row[18]
                }
                configs.append(config)
            
            return configs
        except Exception as e:
            logger.error(f"Error getting URL configs: {e}")
            return []
    
    def delete_url_config(self, config_name: str) -> bool:
        """Delete a URL configuration from the database.
        
        Args:
            config_name: Name of the configuration to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM url_configs WHERE name = ?', (config_name,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting URL config: {e}")
            self.conn.rollback()
            return False
    
    def get_profile_types(self) -> List[str]:
        """Get all unique profile types from the database.
        
        Returns:
            List of profile type strings
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT DISTINCT profile_type FROM url_configs ORDER BY profile_type')
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            logger.error(f"Error getting profile types: {e}")
            return []
    
    def bulk_insert_configs(self, configs: List[Dict[str, Any]]) -> int:
        """Bulk insert multiple URL configurations.
        
        Args:
            configs: List of configuration dictionaries
            
        Returns:
            Number of configurations inserted
        """
        inserted_count = 0
        for config in configs:
            try:
                self.add_url_config(config)
                inserted_count += 1
            except Exception as e:
                logger.warning(f"Failed to insert config {config.get('name', 'unknown')}: {e}")
        
        return inserted_count