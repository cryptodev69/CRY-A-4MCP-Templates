import sqlite3
import json
import logging
import aiosqlite
from typing import List, Dict, Any, Optional
from datetime import datetime


class CrawlerDatabase:
    """Database manager for crawler configurations."""
    
    def __init__(self, db_path: str = "crawlers.db"):
        """Initialize the crawler database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.initialize_db()
    
    def initialize_db(self) -> None:
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS crawlers (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        url_mapping_id TEXT,
                        target_urls TEXT NOT NULL,  -- JSON array of URLs
                        crawler_type TEXT,
                        timeout INTEGER DEFAULT 30,
                        max_retries INTEGER DEFAULT 3,
                        concurrent_limit INTEGER DEFAULT 5,
                        llm_model TEXT,
                        system_prompt TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        config TEXT,  -- JSON object for additional config
                        llm_config TEXT,  -- JSON object for LLM configuration
                        extraction_strategies TEXT,  -- JSON array of extraction strategies
                        url_mapping_ids TEXT,  -- JSON array of URL mapping IDs
                        priority INTEGER DEFAULT 1,
                        stats TEXT,  -- JSON object for crawler statistics
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                self.logger.info(f"Initialized crawler database at {self.db_path}")
                
        except Exception as e:
            self.logger.error(f"Error initializing crawler database: {e}")
            raise
    
    async def get_all_crawlers(self) -> List[Dict[str, Any]]:
        """Get all crawler configurations.
        
        Returns:
            List of crawler configuration dictionaries
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT * FROM crawlers ORDER BY created_at DESC") as cursor:
                    rows = await cursor.fetchall()
                    
                    crawlers = []
                    for row in rows:
                        crawler = {
                            "id": row[0],
                            "name": row[1],
                            "description": row[2],
                            "url_mapping_id": row[3],
                            "target_urls": json.loads(row[4]) if row[4] else [],
                            "crawler_type": row[5],
                            "timeout": row[6],
                            "max_retries": row[7],
                            "concurrent_limit": row[8],
                            "llm_model": row[9],
                            "system_prompt": row[10],
                            "is_active": bool(row[11]),
                            "config": json.loads(row[12]) if row[12] else {},
                            "llm_config": json.loads(row[13]) if row[13] else {},
                            "extraction_strategies": json.loads(row[14]) if row[14] else [],
                            "url_mapping_ids": json.loads(row[15]) if row[15] else [],
                            "priority": row[16],
                            "stats": json.loads(row[17]) if row[17] else {},
                            "created_at": row[18],
                            "updated_at": row[19]
                        }
                        crawlers.append(crawler)
                    
                    return crawlers
                    
        except Exception as e:
            self.logger.error(f"Error getting all crawlers: {e}")
            raise
    
    async def get_crawler(self, crawler_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific crawler configuration.
        
        Args:
            crawler_id: The crawler ID
            
        Returns:
            Crawler configuration dictionary or None if not found
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT * FROM crawlers WHERE id = ?", (crawler_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    crawler = {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "url_mapping_id": row[3],
                        "target_urls": json.loads(row[4]) if row[4] else [],
                        "crawler_type": row[5],
                        "timeout": row[6],
                        "max_retries": row[7],
                        "concurrent_limit": row[8],
                        "llm_model": row[9],
                        "system_prompt": row[10],
                        "is_active": bool(row[11]),
                        "config": json.loads(row[12]) if row[12] else {},
                        "llm_config": json.loads(row[13]) if row[13] else {},
                        "extraction_strategies": json.loads(row[14]) if row[14] else [],
                        "url_mapping_ids": json.loads(row[15]) if row[15] else [],
                        "priority": row[16],
                        "stats": json.loads(row[17]) if row[17] else {},
                        "created_at": row[18],
                        "updated_at": row[19]
                    }
                    
                    return crawler
                    
        except Exception as e:
            self.logger.error(f"Error getting crawler {crawler_id}: {e}")
            raise
    
    async def create_crawler(self, crawler_data: Dict[str, Any]) -> str:
        """Create a new crawler configuration.
        
        Args:
            crawler_data: Dictionary containing crawler configuration
            
        Returns:
            The created crawler ID
        """
        try:
            crawler_id = crawler_data.get("id")
            if not crawler_id:
                raise ValueError("Crawler ID is required")
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO crawlers (
                        id, name, description, url_mapping_id, target_urls,
                        crawler_type, timeout, max_retries, concurrent_limit,
                        llm_model, system_prompt, is_active, config, llm_config,
                        extraction_strategies, url_mapping_ids, priority, stats
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    crawler_id,
                    crawler_data.get("name", ""),
                    crawler_data.get("description", ""),
                    crawler_data.get("url_mapping_id"),
                    json.dumps(crawler_data.get("target_urls", [])),
                    crawler_data.get("crawler_type"),
                    crawler_data.get("timeout", 30),
                    crawler_data.get("max_retries", 3),
                    crawler_data.get("concurrent_limit", 5),
                    crawler_data.get("llm_model"),
                    crawler_data.get("system_prompt"),
                    crawler_data.get("is_active", True),
                    json.dumps(crawler_data.get("config", {})),
                    json.dumps(crawler_data.get("llm_config", {})),
                    json.dumps(crawler_data.get("extraction_strategies", [])),
                    json.dumps(crawler_data.get("url_mapping_ids", [])),
                    crawler_data.get("priority", 1),
                    json.dumps(crawler_data.get("stats", {}))
                ))
                
                await db.commit()
                self.logger.info(f"Created crawler {crawler_id}")
                return crawler_id
                
        except Exception as e:
            self.logger.error(f"Error creating crawler: {e}")
            raise
    
    async def update_crawler(self, crawler_id: str, crawler_data: Dict[str, Any]) -> bool:
        """Update an existing crawler configuration.
        
        Args:
            crawler_id: The crawler ID to update
            crawler_data: Dictionary containing updated crawler configuration
            
        Returns:
            True if updated successfully, False if crawler not found
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE crawlers SET
                        name = ?, description = ?, url_mapping_id = ?, target_urls = ?,
                        crawler_type = ?, timeout = ?, max_retries = ?, concurrent_limit = ?,
                        llm_model = ?, system_prompt = ?, is_active = ?, config = ?,
                        llm_config = ?, extraction_strategies = ?, url_mapping_ids = ?,
                        priority = ?, stats = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    crawler_data.get("name", ""),
                    crawler_data.get("description", ""),
                    crawler_data.get("url_mapping_id"),
                    json.dumps(crawler_data.get("target_urls", [])),
                    crawler_data.get("crawler_type"),
                    crawler_data.get("timeout", 30),
                    crawler_data.get("max_retries", 3),
                    crawler_data.get("concurrent_limit", 5),
                    crawler_data.get("llm_model"),
                    crawler_data.get("system_prompt"),
                    crawler_data.get("is_active", True),
                    json.dumps(crawler_data.get("config", {})),
                    json.dumps(crawler_data.get("llm_config", {})),
                    json.dumps(crawler_data.get("extraction_strategies", [])),
                    json.dumps(crawler_data.get("url_mapping_ids", [])),
                    crawler_data.get("priority", 1),
                    json.dumps(crawler_data.get("stats", {})),
                    crawler_id
                ))
                
                await db.commit()
                
                # Check if any rows were affected
                cursor = await db.execute("SELECT changes()")
                changes = await cursor.fetchone()
                
                if changes[0] > 0:
                    self.logger.info(f"Updated crawler {crawler_id}")
                    return True
                else:
                    self.logger.warning(f"Crawler {crawler_id} not found for update")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error updating crawler {crawler_id}: {e}")
            raise
    
    async def delete_crawler(self, crawler_id: str) -> bool:
        """Delete a crawler configuration.
        
        Args:
            crawler_id: The crawler ID to delete
            
        Returns:
            True if deleted successfully, False if crawler not found
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM crawlers WHERE id = ?", (crawler_id,))
                await db.commit()
                
                # Check if any rows were affected
                cursor = await db.execute("SELECT changes()")
                changes = await cursor.fetchone()
                
                if changes[0] > 0:
                    self.logger.info(f"Deleted crawler {crawler_id}")
                    return True
                else:
                    self.logger.warning(f"Crawler {crawler_id} not found for deletion")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error deleting crawler {crawler_id}: {e}")
            raise
    
    async def initialize(self) -> None:
        """Async initialization method for compatibility with web API."""
        # The database is already initialized in __init__, so this is just for compatibility
        pass
    
    async def seed_sample_data(self) -> None:
        """Seed the database with sample crawler data if empty."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if database is empty
                async with db.execute("SELECT COUNT(*) FROM crawlers") as cursor:
                    row = await cursor.fetchone()
                    count = row[0] if row else 0
                
                if count == 0:
                    sample_crawlers = [
                        {
                            "id": "crawler-1",
                            "name": "News Article Crawler",
                            "description": "Crawls news articles from major news websites",
                            "url_mapping_id": "mapping-1",
                            "target_urls": ["https://example-news.com"],
                            "crawler_type": "news",
                            "timeout": 30,
                            "max_retries": 3,
                            "concurrent_limit": 5,
                            "llm_model": "gpt-4",
                            "system_prompt": "Extract news article content including title, author, date, and body text.",
                            "is_active": True,
                            "config": {},
                            "llm_config": {},
                            "extraction_strategies": [],
                            "url_mapping_ids": [],
                            "priority": 1,
                            "stats": {
                                "totalCrawls": 42,
                                "successfulCrawls": 38,
                                "successRate": 90.5,
                                "avgExtractionTime": 2.3
                            }
                        },
                        {
                            "id": "crawler-2",
                            "name": "E-commerce Product Crawler",
                            "description": "Extracts product information from e-commerce sites",
                            "url_mapping_id": "mapping-2",
                            "target_urls": ["https://example-shop.com"],
                            "crawler_type": "ecommerce",
                            "timeout": 45,
                            "max_retries": 2,
                            "concurrent_limit": 3,
                            "llm_model": "gpt-3.5-turbo",
                            "system_prompt": "Extract product details including name, price, description, and specifications.",
                            "is_active": False,
                            "config": {},
                            "llm_config": {},
                            "extraction_strategies": [],
                            "url_mapping_ids": [],
                            "priority": 1,
                            "stats": {
                                "totalCrawls": 15,
                                "successfulCrawls": 12,
                                "successRate": 80.0,
                                "avgExtractionTime": 3.1
                            }
                        }
                    ]
                    
                    for crawler in sample_crawlers:
                        await db.execute("""
                            INSERT INTO crawlers (
                                id, name, description, url_mapping_id, target_urls,
                                crawler_type, timeout, max_retries, concurrent_limit,
                                llm_model, system_prompt, is_active, config, llm_config,
                                extraction_strategies, url_mapping_ids, priority, stats
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            crawler["id"],
                            crawler["name"],
                            crawler["description"],
                            crawler["url_mapping_id"],
                            json.dumps(crawler["target_urls"]),
                            crawler["crawler_type"],
                            crawler["timeout"],
                            crawler["max_retries"],
                            crawler["concurrent_limit"],
                            crawler["llm_model"],
                            crawler["system_prompt"],
                            crawler["is_active"],
                            json.dumps(crawler["config"]),
                            json.dumps(crawler["llm_config"]),
                            json.dumps(crawler["extraction_strategies"]),
                            json.dumps(crawler["url_mapping_ids"]),
                            crawler["priority"],
                            json.dumps(crawler["stats"])
                        ))
                    
                    await db.commit()
                    self.logger.info(f"Seeded database with {len(sample_crawlers)} sample crawlers")
                    
        except Exception as e:
            self.logger.error(f"Error seeding sample data: {e}")
            raise