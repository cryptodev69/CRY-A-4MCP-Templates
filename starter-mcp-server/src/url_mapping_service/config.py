"""Configuration management for URL Mapping Service.

This module handles environment variable loading and validation using Pydantic.
"""

import os
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogFormat(str, Enum):
    """Log format types."""
    JSON = "json"
    TEXT = "text"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./url_mappings.db",
        description="Database connection URL"
    )
    sql_debug: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Enable auto-reload")
    log_level: str = Field(default="info", description="Logging level")
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    trusted_hosts: Optional[List[str]] = Field(
        default=None,
        description="Trusted host headers"
    )
    
    # Metrics Configuration
    enable_metrics: bool = Field(
        default=True,
        description="Enable Prometheus metrics"
    )
    metrics_port: int = Field(
        default=8001,
        description="Metrics server port"
    )
    
    # Application Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )
    
    # Logging Configuration
    log_format: LogFormat = Field(
        default=LogFormat.JSON,
        description="Log output format"
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Log file path (optional)"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=False,
        description="Enable rate limiting"
    )
    rate_limit_requests_per_minute: int = Field(
        default=60,
        description="Rate limit requests per minute"
    )
    
    # Cache Configuration
    cache_enabled: bool = Field(
        default=False,
        description="Enable caching"
    )
    cache_ttl_seconds: int = Field(
        default=300,
        description="Cache TTL in seconds"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # External Services
    url_config_service_url: Optional[str] = Field(
        default=None,
        description="URL Configuration service URL"
    )
    extractor_service_url: Optional[str] = Field(
        default=None,
        description="Extractor service URL"
    )
    
    # Health Check Configuration
    health_check_timeout: int = Field(
        default=5,
        description="Health check timeout in seconds"
    )
    
    # Database Pool Configuration
    db_pool_size: int = Field(
        default=10,
        description="Database connection pool size"
    )
    db_max_overflow: int = Field(
        default=20,
        description="Database connection pool max overflow"
    )
    db_pool_timeout: int = Field(
        default=30,
        description="Database connection pool timeout"
    )
    db_pool_recycle: int = Field(
        default=3600,
        description="Database connection pool recycle time"
    )
    
    # Backup Configuration
    backup_enabled: bool = Field(
        default=False,
        description="Enable automatic backups"
    )
    backup_schedule: str = Field(
        default="0 2 * * *",
        description="Backup cron schedule"
    )
    backup_retention_days: int = Field(
        default=30,
        description="Backup retention period in days"
    )
    backup_location: str = Field(
        default="/backups/url_mappings",
        description="Backup storage location"
    )
    
    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins string into list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("trusted_hosts", pre=True)
    def parse_trusted_hosts(cls, v):
        """Parse comma-separated hosts string into list."""
        if isinstance(v, str) and v:
            return [host.strip() for host in v.split(",") if host.strip()]
        return v
    
    @validator("port", "metrics_port")
    def validate_port(cls, v):
        """Validate port numbers are in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    @validator("log_file", pre=True)
    def validate_log_file(cls, v):
        """Validate log file path and create directory if needed."""
        if v and v.strip():
            log_path = Path(v)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            return str(log_path)
        return None
    
    @validator("backup_location", pre=True)
    def validate_backup_location(cls, v):
        """Validate backup location and create directory if needed."""
        if v and v.strip():
            backup_path = Path(v)
            if not backup_path.is_absolute():
                backup_path = Path.cwd() / backup_path
            
            # Only try to create directory if it's writable
            try:
                backup_path.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError):
                # If we can't create the directory, just return the path
                # The actual backup functionality can handle this later
                pass
            
            return str(backup_path)
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def database_echo(self) -> bool:
        """Determine if SQLAlchemy should echo SQL queries."""
        return self.sql_debug and self.is_development
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        

# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance.
    
    Returns:
        Settings: Application settings
    """
    return settings