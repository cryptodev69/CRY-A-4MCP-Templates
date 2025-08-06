"""
Configuration management for CRY-A-4MCP server.

This module provides environment-based configuration with validation
and type safety for all server components.
"""

import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be overridden via environment variables with
    the prefix 'CRYA4MCP_'.
    """
    
    # Application
    version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "console"] = "console"
    
    # Crawl4AI Configuration
    crawl4ai_cache_dir: Path = Field(default_factory=lambda: Path("./cache/crawl4ai"))
    crawl4ai_max_concurrent: int = 5
    crawl4ai_timeout: int = 30
    crawl4ai_user_agent: str = "CRY-A-4MCP-Bot/1.0 (Cryptocurrency Analysis)"
    
    # Vector Database (Qdrant)
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "crypto_documents"
    qdrant_vector_size: int = 384  # sentence-transformers/all-MiniLM-L6-v2
    
    # Knowledge Graph (Neo4j)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"
    
    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_size: int = 10
    
    # Cryptocurrency APIs
    coinmarketcap_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None
    
    # Security
    api_key: Optional[str] = None
    cors_origins: list[str] = ["*"]
    
    # Performance
    max_workers: int = 4
    request_timeout: int = 30
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "CRYA4MCP_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("crawl4ai_cache_dir")
    def create_cache_dir(cls, v: Path) -> Path:
        """Ensure cache directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        return v.upper()
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        return v.lower()
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


# Global settings instance
settings = Settings()

