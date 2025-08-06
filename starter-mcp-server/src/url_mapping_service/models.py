"""Separated data models for URL Manager and URL Mappings.

This module defines the separated data models following the architectural plan
where URL Manager handles business concerns (WHAT/WHY to crawl) and URL Mappings
handles technical concerns (HOW to extract).

URL Manager Models:
    - Focus on business metadata and rationale
    - Fields: cost_analysis, key_data_points, rationale, etc.
    - Excludes technical fields like extractor_ids, rate_limit, crawler_settings

URL Mappings Models:
    - Focus on technical configuration
    - Fields: extractor_id, rate_limit, crawler_settings, validation_rules
    - Includes foreign key reference to URL configurations

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# SQLAlchemy Base
Base = declarative_base()


class URLMappingStatus(str, Enum):
    """Status enumeration for URL mappings."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    FAILED = "failed"
    ARCHIVED = "archived"


class URLMappingExtractor(str, Enum):
    """Supported extractors for URL mappings."""
    CRAWL4AI = "crawl4ai"
    SCRAPY = "scrapy"
    SELENIUM = "selenium"
    REQUESTS = "requests"
    PLAYWRIGHT = "playwright"
    CUSTOM = "custom"


# ============================================================================
# SQLALCHEMY ORM MODELS
# ============================================================================

class URLConfiguration(Base):
    """SQLAlchemy model for URL configurations (business focus)."""
    
    __tablename__ = "url_configurations"
    
    # Primary key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique identifier for the URL configuration"
    )
    
    # Core identification fields
    name = Column(
        String(255),
        nullable=False,
        comment="Human-readable name for the URL configuration"
    )
    
    url = Column(
        Text,
        nullable=False,
        comment="Primary URL for this configuration"
    )
    
    # Business classification fields
    profile_type = Column(
        String(100),
        nullable=False,
        comment="Type of profile or data source"
    )
    
    category = Column(
        String(100),
        nullable=False,
        comment="Category classification for organization"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Human-readable description of the configuration"
    )
    
    # Business priority and assessment
    priority = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Business priority level (1-10, higher = more important)"
    )
    
    scraping_difficulty = Column(
        String(50),
        nullable=True,
        comment="Difficulty level assessment for scraping"
    )
    
    # API availability and business considerations
    has_official_api = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether an official API is available"
    )
    
    api_pricing = Column(
        Text,
        nullable=True,
        comment="API pricing information if available"
    )
    
    recommendation = Column(
        String(50),
        nullable=True,
        comment="Business recommendation level for this configuration"
    )
    
    # Business-focused data fields
    key_data_points = Column(
        JSON,
        nullable=True,
        comment="List of key business data points available from this source"
    )
    
    target_data = Column(
        JSON,
        nullable=True,
        comment="Target business data structure description"
    )
    
    # Business rationale and analysis
    rationale = Column(
        Text,
        nullable=True,
        comment="Business rationale for including this configuration"
    )
    
    cost_analysis = Column(
        JSON,
        nullable=True,
        comment="Business cost analysis information"
    )
    
    # Status and metadata
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this configuration is currently active"
    )
    
    business_metadata = Column(
        JSON,
        nullable=True,
        comment="Additional business metadata"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        comment="Creation timestamp"
    )
    
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        comment="Last update timestamp"
    )


class URLMapping(Base):
    """SQLAlchemy model for URL mappings (technical focus)."""
    
    __tablename__ = "url_mappings"
    
    # Primary key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique identifier for the URL mapping"
    )
    
    # Foreign key to URL configuration
    url_config_id = Column(
        String(36),
        nullable=False,
        comment="Foreign key reference to URL configuration ID"
    )
    
    # Technical extractor configuration
    extractor_id = Column(
        String(100),
        nullable=False,
        comment="ID of the extractor to use for this mapping"
    )
    
    # Technical rate limiting
    rate_limit = Column(
        Integer,
        nullable=False,
        default=60,
        comment="Rate limit for requests (requests per minute)"
    )
    
    # Technical crawler settings
    crawler_settings = Column(
        JSON,
        nullable=True,
        comment="Technical crawler-specific settings and parameters"
    )
    
    # Technical validation rules
    validation_rules = Column(
        JSON,
        nullable=True,
        comment="Technical validation rules for extracted data"
    )
    
    # Status and technical metadata
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this mapping is currently active"
    )
    
    technical_metadata = Column(
        JSON,
        nullable=True,
        comment="Additional technical metadata"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        comment="Creation timestamp"
    )
    
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        comment="Last update timestamp"
    )


# ============================================================================
# URL MANAGER MODELS (Business Focus)
# ============================================================================

class URLManagerBase(BaseModel):
    """Base model for URL Manager - focuses on business concerns.
    
    This model handles the WHAT and WHY of crawling:
    - What URLs to crawl
    - Why they are valuable
    - Business rationale and cost analysis
    - Key data points and target information
    
    Excludes technical implementation details like extractors and crawler settings.
    """
    # Core identification fields
    name: str = Field(
        ...,
        description="Human-readable name for the URL configuration",
        example="CoinDesk News Configuration",
        min_length=1
    )
    
    url: str = Field(
        ...,
        description="Primary URL for this configuration",
        example="https://www.coindesk.com/news",
        min_length=1
    )
    
    # Business classification fields
    profile_type: str = Field(
        ...,
        description="Type of profile or data source",
        example="news",
        min_length=1
    )
    
    category: str = Field(
        ...,
        description="Category classification for organization",
        example="cryptocurrency",
        min_length=1
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the configuration",
        example="Configuration for extracting cryptocurrency news from CoinDesk"
    )
    
    # Business priority and assessment
    priority: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Business priority level (1-10, higher = more important)",
        example=5
    )
    
    scraping_difficulty: Optional[str] = Field(
        default=None,
        description="Difficulty level assessment for scraping",
        example="Medium"
    )
    
    # API availability and business considerations
    has_official_api: bool = Field(
        default=False,
        description="Whether an official API is available",
        example=True
    )
    
    api_pricing: Optional[str] = Field(
        default=None,
        description="API pricing information if available",
        example="Free tier available, paid plans start at $10/month"
    )
    
    recommendation: Optional[str] = Field(
        default=None,
        description="Business recommendation level for this configuration",
        example="High"
    )
    
    # Business-focused data fields
    key_data_points: Optional[List[str]] = Field(
        default=None,
        description="List of key business data points available from this source",
        example=["Article headlines", "Publication dates", "Author information", "Market sentiment"]
    )
    
    target_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Target business data structure description",
        example={
            "articles": {"title": "string", "content": "string", "date": "datetime"},
            "sentiment": {"score": "float", "label": "string"}
        }
    )
    
    # Business rationale and analysis
    rationale: Optional[str] = Field(
        default=None,
        description="Business rationale for including this configuration",
        example="Leading cryptocurrency news source with high-quality, timely content"
    )
    
    cost_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Business cost analysis information",
        example={
            "scraping_cost": "Low",
            "api_cost": "Medium",
            "maintenance_effort": "Low",
            "value_rating": "High",
            "roi_estimate": "Very High"
        }
    )
    
    # Status and metadata
    is_active: bool = Field(
        default=True,
        description="Whether this configuration is currently active",
        example=True
    )
    
    business_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional business metadata",
        example={
            "tags": ["news", "crypto", "finance"],
            "business_value": "high",
            "strategic_importance": "critical"
        }
    )


class URLManagerCreate(URLManagerBase):
    """Model for creating new URL Manager configurations.
    
    Inherits all business-focused fields from URLManagerBase.
    Used for POST requests to create new URL configurations.
    """
    pass


class URLManagerUpdate(BaseModel):
    """Model for updating existing URL Manager configurations.
    
    All fields are optional for partial updates.
    Only includes business-focused fields.
    """
    name: Optional[str] = Field(default=None, min_length=1)
    url: Optional[str] = Field(default=None, min_length=1)
    profile_type: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None)
    priority: Optional[int] = Field(default=None, ge=1, le=10)
    scraping_difficulty: Optional[str] = Field(default=None)
    has_official_api: Optional[bool] = Field(default=None)
    api_pricing: Optional[str] = Field(default=None)
    recommendation: Optional[str] = Field(default=None)
    key_data_points: Optional[List[str]] = Field(default=None)
    target_data: Optional[Dict[str, Any]] = Field(default=None)
    rationale: Optional[str] = Field(default=None)
    cost_analysis: Optional[Dict[str, Any]] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    business_metadata: Optional[Dict[str, Any]] = Field(default=None)


class URLManagerResponse(URLManagerBase):
    """Model for URL Manager API responses.
    
    Includes all business fields plus system-generated fields.
    """
    id: str = Field(
        ...,
        description="Unique identifier for the URL configuration",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    created_at: str = Field(
        ...,
        description="Creation timestamp in ISO format",
        example="2024-01-15T10:30:00Z"
    )
    
    updated_at: str = Field(
        ...,
        description="Last update timestamp in ISO format",
        example="2024-01-15T10:30:00Z"
    )


# ============================================================================
# URL MAPPINGS MODELS (Technical Focus)
# ============================================================================

class URLMappingBase(BaseModel):
    """Base model for URL Mappings - focuses on technical concerns.
    
    This model handles the HOW of extraction:
    - Which extractor to use
    - Technical crawler settings
    - Rate limiting configuration
    - Validation rules
    
    Includes foreign key reference to URL configurations.
    """
    # Foreign key to URL configuration
    url_config_id: str = Field(
        ...,
        description="Foreign key reference to URL configuration ID",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    # Technical extractor configuration
    extractor_id: str = Field(
        ...,
        description="ID of the extractor to use for this mapping",
        example="NewsExtractor",
        min_length=1
    )
    
    # Technical rate limiting
    rate_limit: int = Field(
        default=60,
        ge=1,
        description="Rate limit for requests (requests per minute)",
        example=60
    )
    
    # Technical crawler settings
    crawler_settings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Technical crawler-specific settings and parameters",
        example={
            "user_agent": "CRY-A-4MCP Bot",
            "timeout": 30,
            "retries": 3,
            "headers": {"Accept": "text/html"},
            "javascript_enabled": False,
            "wait_for": None
        }
    )
    
    # Technical validation rules
    validation_rules: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Technical validation rules for extracted data",
        example={
            "required_fields": ["title", "content"],
            "min_content_length": 100,
            "allowed_languages": ["en"],
            "data_quality_checks": ["no_duplicates", "valid_urls"]
        }
    )
    
    # Status and technical metadata
    is_active: bool = Field(
        default=True,
        description="Whether this mapping is currently active",
        example=True
    )
    
    technical_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional technical metadata",
        example={
            "performance_metrics": {"avg_response_time": 2.5, "success_rate": 0.95},
            "last_tested": "2024-01-15T10:30:00Z",
            "extractor_version": "1.2.0"
        }
    )


class URLMappingCreate(URLMappingBase):
    """Model for creating new URL mappings.
    
    Inherits all technical fields from URLMappingBase.
    Used for POST requests to create new URL mappings.
    """
    pass


class URLMappingUpdate(BaseModel):
    """Model for updating existing URL mappings.
    
    All fields are optional for partial updates.
    Only includes technical fields.
    """
    url_config_id: Optional[str] = Field(default=None)
    extractor_id: Optional[str] = Field(default=None, min_length=1)
    rate_limit: Optional[int] = Field(default=None, ge=1)
    crawler_settings: Optional[Dict[str, Any]] = Field(default=None)
    validation_rules: Optional[Dict[str, Any]] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    technical_metadata: Optional[Dict[str, Any]] = Field(default=None)


class URLMappingResponse(URLMappingBase):
    """Model for URL Mapping API responses.
    
    Includes all technical fields plus system-generated fields.
    """
    id: str = Field(
        ...,
        description="Unique identifier for the URL mapping",
        example="660e8400-e29b-41d4-a716-446655440001"
    )
    
    created_at: str = Field(
        ...,
        description="Creation timestamp in ISO format",
        example="2024-01-15T10:30:00Z"
    )
    
    updated_at: str = Field(
        ...,
        description="Last update timestamp in ISO format",
        example="2024-01-15T10:30:00Z"
    )


# ============================================================================
# COMBINED RESPONSE MODELS (For UI Integration)
# ============================================================================

class URLConfigurationWithMappings(URLManagerResponse):
    """Combined model showing URL configuration with its associated mappings.
    
    Used for UI components that need to display both business and technical information.
    """
    mappings: List[URLMappingResponse] = Field(
        default=[],
        description="List of URL mappings associated with this configuration"
    )


class URLMappingWithConfiguration(URLMappingResponse):
    """Combined model showing URL mapping with its associated configuration.
    
    Used for UI components that need to display technical mapping with business context.
    """
    url_configuration: Optional[URLManagerResponse] = Field(
        default=None,
        description="URL configuration associated with this mapping"
    )


# ============================================================================
# DROPDOWN/SELECTION MODELS (For UI Components)
# ============================================================================

class URLConfigurationOption(BaseModel):
    """Simplified model for URL configuration dropdown options.
    
    Used by the URL Mappings UI to load URL options from the URL Configuration service.
    """
    id: str = Field(
        ...,
        description="URL configuration ID",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    name: str = Field(
        ...,
        description="Display name for the configuration",
        example="CoinDesk News Configuration"
    )
    
    url: str = Field(
        ...,
        description="Primary URL",
        example="https://www.coindesk.com/news"
    )
    
    profile_type: str = Field(
        ...,
        description="Profile type",
        example="news"
    )
    
    category: str = Field(
        ...,
        description="Category",
        example="cryptocurrency"
    )
    
    is_active: bool = Field(
        ...,
        description="Whether the configuration is active",
        example=True
    )


# ============================================================================
# LEGACY COMPATIBILITY MODELS
# ============================================================================

# For backward compatibility with existing tests and services
class URLMappingListResponse(BaseModel):
    """Response model for listing URL mappings."""
    items: List[URLMappingResponse] = Field(
        default=[],
        description="List of URL mappings"
    )
    total: int = Field(
        default=0,
        description="Total number of items"
    )
    page: int = Field(
        default=1,
        description="Current page number"
    )
    size: int = Field(
        default=10,
        description="Items per page"
    )
    pages: int = Field(
        default=0,
        description="Total number of pages"
    )


class URLMappingStats(BaseModel):
    """Statistics model for URL mappings."""
    total_mappings: int = Field(
        default=0,
        description="Total number of URL mappings"
    )
    active_mappings: int = Field(
        default=0,
        description="Number of active URL mappings"
    )
    inactive_mappings: int = Field(
        default=0,
        description="Number of inactive URL mappings"
    )
    extractors_count: Dict[str, int] = Field(
        default={},
        description="Count of mappings by extractor type"
    )


class BulkStatusUpdate(BaseModel):
    """Model for bulk status updates."""
    mapping_ids: List[str] = Field(
        ...,
        description="List of mapping IDs to update"
    )
    status: URLMappingStatus = Field(
        ...,
        description="New status to apply"
    )


class BulkStatusUpdateResponse(BaseModel):
    """Response model for bulk status updates."""
    updated_count: int = Field(
        ...,
        description="Number of mappings updated"
    )
    failed_ids: List[str] = Field(
        default=[],
        description="List of mapping IDs that failed to update"
    )


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(
        ...,
        description="Service status",
        example="healthy"
    )
    timestamp: str = Field(
        ...,
        description="Health check timestamp",
        example="2024-01-15T10:30:00Z"
    )
    version: str = Field(
        ...,
        description="Service version",
        example="1.0.0"
    )
    database: str = Field(
        ...,
        description="Database status",
        example="connected"
    )