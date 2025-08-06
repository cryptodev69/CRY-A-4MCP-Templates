import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging
from .strategy_db import StrategyDatabase
from .async_strategy_db import AsyncStrategyDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyDatabaseManager:
    """Manager class for handling both synchronous and asynchronous database operations.
    
    This class provides a unified interface for working with strategy databases,
    supporting both synchronous and asynchronous operations as needed.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the strategy database manager.
        
        Args:
            db_path: Path to the SQLite database file. If None, a default path will be used.
        """
        self.db_path = db_path
        self.sync_db = StrategyDatabase(db_path)
        self.async_db = None
    
    async def initialize_async(self):
        """Initialize the asynchronous database connection."""
        self.async_db = AsyncStrategyDatabase(self.db_path)
        await self.async_db.initialize()
        return self.async_db
    
    async def cleanup_async(self):
        """Cleanup asynchronous database connections."""
        if self.async_db:
            await self.async_db.cleanup()
    
    def cleanup_sync(self):
        """Cleanup synchronous database connections."""
        if self.sync_db:
            self.sync_db.close()
    
    # Synchronous methods
    def add_strategy(self, strategy_data: Dict[str, Any]) -> int:
        """Add a new strategy to the database synchronously."""
        return self.sync_db.add_strategy(strategy_data)
    
    def update_strategy(self, strategy_name: str, strategy_data: Dict[str, Any]) -> bool:
        """Update an existing strategy in the database synchronously."""
        return self.sync_db.update_strategy(strategy_name, strategy_data)
    
    def get_strategy(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """Get a strategy by name synchronously."""
        return self.sync_db.get_strategy(strategy_name)
    
    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all strategies from the database synchronously."""
        return self.sync_db.get_all_strategies()
    
    def delete_strategy(self, strategy_name: str) -> bool:
        """Delete a strategy from the database synchronously."""
        return self.sync_db.delete_strategy(strategy_name)
    
    def get_strategies_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all strategies in a specific category synchronously."""
        return self.sync_db.get_strategies_by_category(category)
    
    # Asynchronous methods
    async def aadd_strategy(self, strategy_data: Dict[str, Any]) -> int:
        """Add a new strategy to the database asynchronously."""
        if not self.async_db:
            await self.initialize_async()
        return await self.async_db.aadd_strategy(strategy_data)
    
    async def aupdate_strategy(self, strategy_name: str, strategy_data: Dict[str, Any]) -> bool:
        """Update an existing strategy in the database asynchronously."""
        if not self.async_db:
            await self.initialize_async()
        return await self.async_db.aupdate_strategy(strategy_name, strategy_data)
    
    async def aget_strategy(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """Get a strategy by name asynchronously."""
        if not self.async_db:
            await self.initialize_async()
        return await self.async_db.aget_strategy(strategy_name)
    
    async def aget_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all strategies from the database asynchronously."""
        if not self.async_db:
            await self.initialize_async()
        return await self.async_db.aget_all_strategies()
    
    async def adelete_strategy(self, strategy_name: str) -> bool:
        """Delete a strategy from the database asynchronously."""
        if not self.async_db:
            await self.initialize_async()
        return await self.async_db.adelete_strategy(strategy_name)
    
    async def aget_strategies_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all strategies in a specific category asynchronously."""
        if not self.async_db:
            await self.initialize_async()
        return await self.async_db.aget_strategies_by_category(category)