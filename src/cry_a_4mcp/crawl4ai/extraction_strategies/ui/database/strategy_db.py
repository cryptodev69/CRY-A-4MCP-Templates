import os
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyDatabase:
    """Database manager for extraction strategies.
    
    This class provides methods for storing and retrieving strategy data,
    including schemas, instructions, and other metadata.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the strategy database.
        
        Args:
            db_path: Path to the SQLite database file. If None, a default path will be used.
        """
        if db_path is None:
            # Create default path in the config directory
            config_dir = Path(__file__).parent.parent / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(config_dir / "strategies.db")
        
        self.db_path = db_path
        self.conn = None
        self.initialize_db()
    
    def initialize_db(self):
        """Initialize the database schema."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Create strategies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    default_provider TEXT NOT NULL,
                    schema TEXT NOT NULL,
                    instruction TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            if self.conn:
                self.conn.close()
            raise
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def add_strategy(self, strategy_data: Dict[str, Any]) -> int:
        """Add a new strategy to the database.
        
        Args:
            strategy_data: Dictionary containing strategy data
            
        Returns:
            ID of the inserted strategy
        """
        try:
            cursor = self.conn.cursor()
            
            # Convert schema to JSON string if it's a dict
            if isinstance(strategy_data.get('schema'), dict):
                strategy_data['schema'] = json.dumps(strategy_data['schema'])
            
            cursor.execute('''
                INSERT INTO strategies 
                (name, description, category, default_provider, schema, instruction, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                strategy_data.get('name', ''),
                strategy_data.get('description', ''),
                strategy_data.get('category', 'general'),
                strategy_data.get('default_provider', 'openai'),
                strategy_data.get('schema', '{}'),
                strategy_data.get('instruction', ''),
                strategy_data.get('file_path', '')
            ))
            
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding strategy: {e}")
            self.conn.rollback()
            raise
    
    def update_strategy(self, strategy_name: str, strategy_data: Dict[str, Any]) -> bool:
        """Update an existing strategy in the database.
        
        Args:
            strategy_name: Name of the strategy to update
            strategy_data: Dictionary containing updated strategy data
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            # Convert schema to JSON string if it's a dict
            if isinstance(strategy_data.get('schema'), dict):
                strategy_data['schema'] = json.dumps(strategy_data['schema'])
            
            cursor.execute('''
                UPDATE strategies
                SET description = ?,
                    category = ?,
                    default_provider = ?,
                    schema = ?,
                    instruction = ?,
                    file_path = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            ''', (
                strategy_data.get('description', ''),
                strategy_data.get('category', 'general'),
                strategy_data.get('default_provider', 'openai'),
                strategy_data.get('schema', '{}'),
                strategy_data.get('instruction', ''),
                strategy_data.get('file_path', ''),
                strategy_name
            ))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating strategy: {e}")
            self.conn.rollback()
            return False
    
    def get_strategy(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """Get a strategy by name.
        
        Args:
            strategy_name: Name of the strategy to retrieve
            
        Returns:
            Dictionary containing strategy data or None if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, name, description, category, default_provider, schema, instruction, file_path, 
                       created_at, updated_at
                FROM strategies
                WHERE name = ?
            ''', (strategy_name,))
            
            row = cursor.fetchone()
            if row:
                strategy = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'category': row[3],
                    'default_provider': row[4],
                    'schema': json.loads(row[5]),
                    'instruction': row[6],
                    'file_path': row[7],
                    'created_at': row[8],
                    'updated_at': row[9]
                }
                return strategy
            return None
        except Exception as e:
            logger.error(f"Error getting strategy: {e}")
            return None
    
    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all strategies from the database.
        
        Returns:
            List of dictionaries containing strategy data
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, name, description, category, default_provider, schema, instruction, file_path, 
                       created_at, updated_at
                FROM strategies
                ORDER BY name
            ''')
            
            strategies = []
            for row in cursor.fetchall():
                strategy = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'category': row[3],
                    'default_provider': row[4],
                    'schema': json.loads(row[5]),
                    'instruction': row[6],
                    'file_path': row[7],
                    'created_at': row[8],
                    'updated_at': row[9]
                }
                strategies.append(strategy)
            return strategies
        except Exception as e:
            logger.error(f"Error getting all strategies: {e}")
            return []
    
    def delete_strategy(self, strategy_name: str) -> bool:
        """Delete a strategy from the database.
        
        Args:
            strategy_name: Name of the strategy to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                DELETE FROM strategies
                WHERE name = ?
            ''', (strategy_name,))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting strategy: {e}")
            self.conn.rollback()
            return False
    
    def get_strategies_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all strategies in a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of dictionaries containing strategy data
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, name, description, category, default_provider, schema, instruction, file_path, 
                       created_at, updated_at
                FROM strategies
                WHERE category = ?
                ORDER BY name
            ''', (category,))
            
            strategies = []
            for row in cursor.fetchall():
                strategy = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'category': row[3],
                    'default_provider': row[4],
                    'schema': json.loads(row[5]),
                    'instruction': row[6],
                    'file_path': row[7],
                    'created_at': row[8],
                    'updated_at': row[9]
                }
                strategies.append(strategy)
            return strategies
        except Exception as e:
            logger.error(f"Error getting strategies by category: {e}")
            return []