import os
import json
import aiosqlite
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncStrategyDatabase:
    """Asynchronous database manager for extraction strategies.
    
    This class provides asynchronous methods for storing and retrieving strategy data,
    including schemas, instructions, and other metadata.
    """
    
    def __init__(self, db_path: Optional[str] = None, pool_size: int = 5, max_retries: int = 3):
        """Initialize the async strategy database.
        
        Args:
            db_path: Path to the SQLite database file. If None, a default path will be used.
            pool_size: Maximum number of concurrent database connections
            max_retries: Maximum number of retry attempts for database operations
        """
        if db_path is None:
            # Create default path in the config directory
            config_dir = Path(__file__).parent.parent / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(config_dir / "strategies.db")
        
        self.db_path = db_path
        self.pool_size = pool_size
        self.max_retries = max_retries
        self.connection_pool: Dict[int, aiosqlite.Connection] = {}
        self.pool_lock = asyncio.Lock()
        self.connection_semaphore = asyncio.Semaphore(pool_size)
    
    async def initialize(self):
        """Initialize the database and connection pool."""
        await self.ainit_db()
    
    async def cleanup(self):
        """Cleanup connections when shutting down."""
        async with self.pool_lock:
            for conn in self.connection_pool.values():
                await conn.close()
            self.connection_pool.clear()
    
    @asynccontextmanager
    async def get_connection(self):
        """Connection pool manager."""
        async with self.connection_semaphore:
            task_id = id(asyncio.current_task())
            try:
                async with self.pool_lock:
                    if task_id not in self.connection_pool:
                        conn = await aiosqlite.connect(
                            self.db_path,
                            timeout=30.0
                        )
                        await conn.execute('PRAGMA journal_mode = WAL')
                        await conn.execute('PRAGMA busy_timeout = 5000')
                        self.connection_pool[task_id] = conn
                    
                yield self.connection_pool[task_id]
                
            except Exception as e:
                logger.error(f"Connection error: {e}")
                raise
            finally:
                async with self.pool_lock:
                    if task_id in self.connection_pool:
                        await self.connection_pool[task_id].close()
                        del self.connection_pool[task_id]
    
    async def execute_with_retry(self, operation, *args):
        """Execute database operations with retry logic."""
        for attempt in range(self.max_retries):
            try:
                async with self.get_connection() as db:
                    result = await operation(db, *args)
                    await db.commit()
                    return result
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Operation failed after {self.max_retries} attempts: {e}")
                    raise
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
    
    async def ainit_db(self):
        """Initialize database schema."""
        async def _init(db):
            await db.execute('''
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
        
        await self.execute_with_retry(_init)
    
    async def aadd_strategy(self, strategy_data: Dict[str, Any]) -> int:
        """Add a new strategy to the database asynchronously.
        
        Args:
            strategy_data: Dictionary containing strategy data
            
        Returns:
            ID of the inserted strategy
        """
        async def _add(db, data):
            # Convert schema to JSON string if it's a dict
            if isinstance(data.get('schema'), dict):
                data['schema'] = json.dumps(data['schema'])
            
            cursor = await db.execute('''
                INSERT INTO strategies 
                (name, description, category, default_provider, schema, instruction, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name', ''),
                data.get('description', ''),
                data.get('category', 'general'),
                data.get('default_provider', 'openai'),
                data.get('schema', '{}'),
                data.get('instruction', ''),
                data.get('file_path', '')
            ))
            
            return cursor.lastrowid
        
        try:
            return await self.execute_with_retry(_add, strategy_data)
        except Exception as e:
            logger.error(f"Error adding strategy: {e}")
            raise
    
    async def aupdate_strategy(self, strategy_name: str, strategy_data: Dict[str, Any]) -> bool:
        """Update an existing strategy in the database asynchronously.
        
        Args:
            strategy_name: Name of the strategy to update
            strategy_data: Dictionary containing updated strategy data
            
        Returns:
            True if update was successful, False otherwise
        """
        async def _update(db, name, data):
            # Convert schema to JSON string if it's a dict
            if isinstance(data.get('schema'), dict):
                data['schema'] = json.dumps(data['schema'])
            
            cursor = await db.execute('''
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
                data.get('description', ''),
                data.get('category', 'general'),
                data.get('default_provider', 'openai'),
                data.get('schema', '{}'),
                data.get('instruction', ''),
                data.get('file_path', ''),
                name
            ))
            
            return cursor.rowcount > 0
        
        try:
            return await self.execute_with_retry(_update, strategy_name, strategy_data)
        except Exception as e:
            logger.error(f"Error updating strategy: {e}")
            return False
    
    async def aget_strategy(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """Get a strategy by name asynchronously.
        
        Args:
            strategy_name: Name of the strategy to retrieve
            
        Returns:
            Dictionary containing strategy data or None if not found
        """
        async def _get(db, name):
            async with db.execute('''
                SELECT id, name, description, category, default_provider, schema, instruction, file_path, 
                       created_at, updated_at
                FROM strategies
                WHERE name = ?
            ''', (name,)) as cursor:
                row = await cursor.fetchone()
                
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
        
        try:
            return await self.execute_with_retry(_get, strategy_name)
        except Exception as e:
            logger.error(f"Error getting strategy: {e}")
            return None
    
    async def aget_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all strategies from the database asynchronously.
        
        Returns:
            List of dictionaries containing strategy data
        """
        async def _get_all(db):
            strategies = []
            async with db.execute('''
                SELECT id, name, description, category, default_provider, schema, instruction, file_path, 
                       created_at, updated_at
                FROM strategies
                ORDER BY name
            ''') as cursor:
                async for row in cursor:
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
        
        try:
            return await self.execute_with_retry(_get_all)
        except Exception as e:
            logger.error(f"Error getting all strategies: {e}")
            return []
    
    async def adelete_strategy(self, strategy_name: str) -> bool:
        """Delete a strategy from the database asynchronously.
        
        Args:
            strategy_name: Name of the strategy to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        async def _delete(db, name):
            cursor = await db.execute('''
                DELETE FROM strategies
                WHERE name = ?
            ''', (name,))
            
            return cursor.rowcount > 0
        
        try:
            return await self.execute_with_retry(_delete, strategy_name)
        except Exception as e:
            logger.error(f"Error deleting strategy: {e}")
            return False
    
    async def aget_strategies_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all strategies in a specific category asynchronously.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of dictionaries containing strategy data
        """
        async def _get_by_category(db, cat):
            strategies = []
            async with db.execute('''
                SELECT id, name, description, category, default_provider, schema, instruction, file_path, 
                       created_at, updated_at
                FROM strategies
                WHERE category = ?
                ORDER BY name
            ''', (cat,)) as cursor:
                async for row in cursor:
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
        
        try:
            return await self.execute_with_retry(_get_by_category, category)
        except Exception as e:
            logger.error(f"Error getting strategies by category: {e}")
            return []