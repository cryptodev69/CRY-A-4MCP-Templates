#!/usr/bin/env python3
"""
Simple FastAPI Web Server for URL Configuration Management

This module provides a lightweight REST API for managing URL configurations
without complex dependencies.
"""

import asyncio
import logging
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class URLConfigCreate(BaseModel):
    """Model for creating URL configurations."""
    name: str
    url: str
    profile_type: str
    description: Optional[str] = None
    scraping_difficulty: Optional[str] = None
    has_official_api: Optional[bool] = None
    api_pricing: Optional[str] = None
    recommendation: Optional[str] = None
    key_data_points: Optional[List[str]] = None
    target_data: Optional[str] = None
    rationale: Optional[str] = None
    cost_analysis: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[int] = None

class URLConfigResponse(BaseModel):
    """Model for URL configuration responses."""
    id: int
    name: str
    url: str
    profile_type: str
    description: Optional[str] = None
    scraping_difficulty: Optional[str] = None
    has_official_api: Optional[bool] = None
    api_pricing: Optional[str] = None
    recommendation: Optional[str] = None
    key_data_points: Optional[List[str]] = None
    target_data: Optional[str] = None
    rationale: Optional[str] = None
    cost_analysis: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[int] = None
    created_at: str
    updated_at: str

class SimpleURLConfigDatabase:
    """Simple SQLite database for URL configurations."""
    
    def __init__(self, db_path: str = "url_configs.db"):
        """Initialize the database connection."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS url_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                profile_type TEXT NOT NULL,
                description TEXT,
                scraping_difficulty TEXT,
                has_official_api BOOLEAN,
                api_pricing TEXT,
                recommendation TEXT,
                key_data_points TEXT,
                target_data TEXT,
                rationale TEXT,
                cost_analysis TEXT,
                category TEXT,
                priority INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_config(self, config: URLConfigCreate) -> int:
        """Add a new URL configuration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        key_data_points_json = json.dumps(config.key_data_points) if config.key_data_points else None
        
        cursor.execute("""
            INSERT INTO url_configs (
                name, url, profile_type, description, scraping_difficulty,
                has_official_api, api_pricing, recommendation, key_data_points,
                target_data, rationale, cost_analysis, category, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config.name, config.url, config.profile_type, config.description,
            config.scraping_difficulty, config.has_official_api, config.api_pricing,
            config.recommendation, key_data_points_json, config.target_data,
            config.rationale, config.cost_analysis, config.category, config.priority
        ))
        
        config_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return config_id
    
    def get_all_configs(self) -> List[URLConfigResponse]:
        """Get all URL configurations."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM url_configs ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        configs = []
        for row in rows:
            key_data_points = json.loads(row['key_data_points']) if row['key_data_points'] else None
            
            config = URLConfigResponse(
                id=row['id'],
                name=row['name'],
                url=row['url'],
                profile_type=row['profile_type'],
                description=row['description'],
                scraping_difficulty=row['scraping_difficulty'],
                has_official_api=bool(row['has_official_api']) if row['has_official_api'] is not None else None,
                api_pricing=row['api_pricing'],
                recommendation=row['recommendation'],
                key_data_points=key_data_points,
                target_data=row['target_data'],
                rationale=row['rationale'],
                cost_analysis=row['cost_analysis'],
                category=row['category'],
                priority=row['priority'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            configs.append(config)
        
        return configs
    
    def load_predefined_configs(self):
        """Load predefined URL configurations."""
        predefined_configs = [
            {
                "name": "CoinGecko API",
                "url": "https://api.coingecko.com/api/v3",
                "profile_type": "Traditional Investor",
                "description": "Comprehensive cryptocurrency market data API",
                "scraping_difficulty": "Easy",
                "has_official_api": True,
                "api_pricing": "Free tier available, paid plans from $129/month",
                "recommendation": "Highly Recommended",
                "key_data_points": ["Market cap", "Price", "Volume", "Historical data"],
                "target_data": "Real-time and historical cryptocurrency market data",
                "rationale": "Most comprehensive and reliable crypto data source",
                "cost_analysis": "Free tier sufficient for basic needs",
                "category": "Market Data",
                "priority": 5
            },
            {
                "name": "DeFiPulse",
                "url": "https://defipulse.com",
                "profile_type": "DeFi Yield Farmer",
                "description": "DeFi protocol analytics and TVL tracking",
                "scraping_difficulty": "Medium",
                "has_official_api": False,
                "api_pricing": "N/A",
                "recommendation": "Recommended",
                "key_data_points": ["TVL", "Protocol rankings", "Yield rates"],
                "target_data": "DeFi protocol total value locked and metrics",
                "rationale": "Essential for DeFi investment decisions",
                "cost_analysis": "Free web scraping",
                "category": "DeFi Analytics",
                "priority": 4
            },
            {
                "name": "CryptoTwitter Sentiment",
                "url": "https://twitter.com/search",
                "profile_type": "Degen Gambler",
                "description": "Social sentiment analysis from crypto Twitter",
                "scraping_difficulty": "Hard",
                "has_official_api": True,
                "api_pricing": "Twitter API v2: $100/month for basic access",
                "recommendation": "Use with Caution",
                "key_data_points": ["Sentiment scores", "Mention volume", "Influencer activity"],
                "target_data": "Social media sentiment and buzz metrics",
                "rationale": "Important for short-term trading signals",
                "cost_analysis": "High API costs, consider alternatives",
                "category": "Social Sentiment",
                "priority": 3
            }
        ]
        
        for config_data in predefined_configs:
            config = URLConfigCreate(**config_data)
            self.add_config(config)

# Initialize FastAPI app
app = FastAPI(
    title="CRY-A-4MCP URL Configuration API",
    description="REST API for managing cryptocurrency data source URLs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = SimpleURLConfigDatabase()

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting CRY-A-4MCP URL Configuration API")
    
    # Check if we need to load predefined configs
    configs = db.get_all_configs()
    if not configs:
        logger.info("Loading predefined URL configurations")
        db.load_predefined_configs()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "CRY-A-4MCP URL Configuration API", "version": "1.0.0"}

@app.get("/api/url-configs/", response_model=List[URLConfigResponse])
async def get_url_configs(
    profile_type: Optional[str] = Query(None, description="Filter by profile type"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get all URL configurations with optional filtering."""
    try:
        configs = db.get_all_configs()
        
        # Apply filters
        if profile_type:
            configs = [c for c in configs if c.profile_type == profile_type]
        if category:
            configs = [c for c in configs if c.category == category]
        
        return configs
    except Exception as e:
        logger.error(f"Error retrieving URL configurations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/url-configs/", response_model=URLConfigResponse)
async def create_url_config(config: URLConfigCreate):
    """Create a new URL configuration."""
    try:
        config_id = db.add_config(config)
        configs = db.get_all_configs()
        created_config = next((c for c in configs if c.id == config_id), None)
        
        if not created_config:
            raise HTTPException(status_code=500, detail="Failed to create configuration")
        
        return created_config
    except Exception as e:
        logger.error(f"Error creating URL configuration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/profile-types/")
async def get_profile_types():
    """Get available profile types."""
    return {
        "profile_types": [
            "Degen Gambler",
            "Gem Hunter", 
            "Traditional Investor",
            "DeFi Yield Farmer"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "simple_web_api:app",
        host="0.0.0.0",
        port=4000,
        reload=True,
        log_level="info"
    )