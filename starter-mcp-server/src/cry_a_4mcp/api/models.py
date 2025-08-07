"""Pydantic data models for the CRY-A-4MCP API platform.

This module defines all the data models used throughout the CRY-A-4MCP (Crypto AI for
Model Context Protocol) platform's REST API. It provides comprehensive Pydantic models
for request validation, response serialization, and data transfer between API layers.

The module is organized into logical sections:
    - Extractor Models: For managing extraction strategy configurations
    - URL Configuration Models: For URL pattern and profile management
    - URL Mapping Models: For associating URLs with specific extractors
    - Crawler Configuration Models: For web crawler setup and management
    - Crawl Job Models: For individual crawling task execution
    - Test URL Models: For testing and validation of extraction processes
    - OpenRouter Models: For AI model integration and configuration

Key Features:
    - Comprehensive field validation using Pydantic constraints
    - Consistent naming conventions across all models
    - Proper type hints for enhanced IDE support and runtime validation
    - Optional fields with sensible defaults for flexible API usage
    - Separate models for create, update, and response operations
    - Built-in serialization/deserialization for JSON API responses

Usage:
    These models are automatically used by FastAPI for:
    - Request body validation and parsing
    - Response serialization and documentation
    - OpenAPI schema generation
    - Type checking and IDE autocompletion

Example:
    from cry_a_4mcp.api.models import CrawlerConfigCreate
    
    # Create a new crawler configuration
    crawler_config = CrawlerConfigCreate(
        name="News Crawler",
        description="Crawls cryptocurrency news sites",
        url_patterns=["https://cryptonews.com/*"],
        max_pages=100
    )

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

# Standard library imports for type hints and datetime handling
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# Pydantic imports for data validation and serialization
from pydantic import BaseModel, Field


# ============================================================================
# EXTRACTOR MODELS
# ============================================================================
# Models for managing extraction strategy configurations and metadata

class ExtractorResponse(BaseModel):
    """Response model for extraction strategy information.
    
    This model represents the standardized response format for extraction strategies
    discovered and managed by the CRY-A-4MCP platform. It provides comprehensive
    metadata about each available extraction strategy implementation.
    
    Attributes:
        id (str): Unique identifier for the extraction strategy, typically
                 matching the class name of the strategy implementation.
                 Used for API routing and strategy selection.
        
        name (str): Human-readable display name of the extraction strategy.
                   Usually matches the id but may be formatted for presentation.
                   Used in user interfaces and documentation.
        
        description (str): Detailed description of the extraction strategy's
                          purpose, capabilities, and intended use cases.
                          Derived from the strategy's instructions or docstring.
        
        schema (str): Data schema definition describing the structure of
                     extracted data. May be in various formats (CSV headers,
                     JSON schema, etc.) depending on the strategy implementation.
                     Empty string if no schema is defined.
        
        file_path (str): Relative path to the source file containing the
                        strategy implementation. Used for debugging, auditing,
                        and development purposes.
    
    Example:
        {
            "id": "CryptoNewsExtractor",
            "name": "CryptoNewsExtractor",
            "description": "Extract cryptocurrency news with sentiment analysis",
            "schema": "title,content,timestamp,sentiment,source",
            "file_path": "crypto_news.py"
        }
    
    Note:
        This model is used exclusively for API responses and should not be
        used for creating or updating extractor configurations. The actual
        extraction strategies are implemented as separate Python classes.
    """
    # Unique identifier for the extraction strategy
    id: str = Field(
        ...,
        description="Unique identifier for the extraction strategy",
        example="CryptoNewsExtractor"
    )
    
    # Human-readable display name
    name: str = Field(
        ...,
        description="Human-readable name of the extraction strategy",
        example="Crypto News Extractor"
    )
    
    # Detailed description of the strategy's purpose and capabilities
    description: str = Field(
        ...,
        description="Detailed description of the extraction strategy",
        example="Extracts cryptocurrency news articles with sentiment analysis"
    )
    
    # Data schema definition (optional, may be empty)
    schema: Union[str, Dict[str, Any]] = Field(
        default="",
        description="Data schema definition for extracted content",
        example={"type": "object", "properties": {"title": {"type": "string"}}}
    )
    
    # Source file path for the strategy implementation
    file_path: str = Field(
        ...,
        description="Path to the source file containing the strategy",
        example="crypto_news.py"
    )


# ============================================================================
# UNIFIED URL CONFIGURATION MODELS
# ============================================================================
# Models for the unified URL configuration system that handles both
# predefined URL configurations and dynamic URL-to-extractor mappings

class URLConfigurationBase(BaseModel):
    """Base model for unified URL configuration management.
    
    This model defines the core structure for URL configurations within the
    CRY-A-4MCP platform. It unifies the previous separate url_configs and
    url_mappings schemas into a single, comprehensive model that can handle
    both predefined URL configurations and dynamic URL-to-extractor mappings.
    
    Attributes:
        name (str): Human-readable name for the configuration.
        url (str): Primary URL for this configuration.
        profile_type (str): Type of profile or data source.
        category (str): Category classification for organization.
        description (Optional[str]): Human-readable description.
        url_patterns (Optional[List[str]]): List of URL patterns for matching.
        priority (int): Priority level (higher = more important).
        scraping_difficulty (Optional[str]): Difficulty level assessment.
        has_official_api (bool): Whether an official API is available.
        api_pricing (Optional[str]): API pricing information.
        recommendation (Optional[str]): Recommendation for this configuration.
        key_data_points (Optional[List[str]]): List of key data points available.
        target_data (Optional[Dict[str, Any]]): Target data structure description.
        rationale (Optional[str]): Rationale for including this configuration.
        cost_analysis (Optional[Dict[str, Any]]): Cost analysis information.
        extractor_ids (Optional[List[str]]): List of extractor IDs to use.
        crawler_settings (Optional[Dict[str, Any]]): Crawler-specific settings.
        rate_limit (int): Rate limit for requests.
        validation_rules (Optional[Dict[str, Any]]): Validation rules for extracted data.
        is_active (bool): Whether this configuration is active.
        metadata (Optional[Dict[str, Any]]): Additional metadata.
    
    Note:
        This is a base model and should not be instantiated directly.
        Use URLConfigurationCreate, URLConfigurationUpdate, or URLConfigurationResponse instead.
    """
    # Human-readable name for the configuration
    name: str = Field(
        ...,
        description="Human-readable name for the configuration",
        example="CoinDesk News Configuration",
        min_length=1
    )
    
    # Primary URL for this configuration
    url: str = Field(
        ...,
        description="Primary URL for this configuration",
        example="https://www.coindesk.com/news",
        min_length=1
    )
    
    # Profile type for extraction strategy selection
    profile_type: str = Field(
        ...,
        description="Type of profile or data source",
        example="news",
        min_length=1
    )
    
    # Category for organization and filtering
    category: str = Field(
        ...,
        description="Category classification for organization",
        example="cryptocurrency",
        min_length=1
    )
    
    # Optional human-readable description
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the configuration",
        example="Configuration for extracting cryptocurrency news from CoinDesk"
    )
    
    # Note: url_patterns field removed as it's not part of the database schema
    # The primary URL field is sufficient for URL configuration management
    
    # Priority level (higher = more important)
    priority: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Priority level (1-10, higher = more important)",
        example=5
    )
    
    # Scraping difficulty assessment
    scraping_difficulty: Optional[str] = Field(
        default=None,
        description="Difficulty level assessment for scraping",
        example="Medium"
    )
    
    # Whether an official API is available
    has_official_api: bool = Field(
        default=False,
        description="Whether an official API is available",
        example=True
    )
    
    # API pricing information
    api_pricing: Optional[str] = Field(
        default=None,
        description="API pricing information if available",
        example="Free tier available, paid plans start at $10/month"
    )
    
    # Recommendation for this configuration
    recommendation: Optional[str] = Field(
        default=None,
        description="Recommendation level for this configuration",
        example="High"
    )
    
    # List of key data points available
    key_data_points: Optional[List[str]] = Field(
        default=None,
        description="List of key data points available from this source",
        example=["Article headlines", "Publication dates", "Author information", "Market sentiment"]
    )
    
    # Target data structure description
    target_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Target data structure description",
        example={
            "articles": {"title": "string", "content": "string", "date": "datetime"},
            "sentiment": {"score": "float", "label": "string"}
        }
    )
    
    # Rationale for including this configuration
    rationale: Optional[str] = Field(
        default=None,
        description="Rationale for including this configuration",
        example="Leading cryptocurrency news source with high-quality, timely content"
    )
    
    # Cost analysis information
    cost_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Cost analysis information",
        example={
            "scraping_cost": "Low",
            "api_cost": "Medium",
            "maintenance_effort": "Low",
            "value_rating": "High"
        }
    )
    
    # List of extractor IDs to use
    extractor_ids: Optional[List[str]] = Field(
        default=None,
        description="List of extractor IDs to use for this configuration",
        example=["NewsExtractor", "SentimentExtractor"]
    )
    
    # Crawler-specific settings
    crawler_settings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Crawler-specific settings and parameters",
        example={
            "user_agent": "CRY-A-4MCP Bot",
            "timeout": 30,
            "retries": 3,
            "headers": {"Accept": "text/html"}
        }
    )
    
    # Rate limit for requests
    rate_limit: int = Field(
        default=60,
        ge=1,
        description="Rate limit for requests (requests per minute)",
        example=60
    )
    
    # Validation rules for extracted data
    validation_rules: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Validation rules for extracted data",
        example={
            "required_fields": ["title", "content"],
            "min_content_length": 100,
            "allowed_languages": ["en"]
        }
    )
    
    # Whether this configuration is active
    is_active: bool = Field(
        default=True,
        description="Whether this configuration is currently active",
        example=True
    )
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional configuration metadata",
        example={
            "tags": ["news", "crypto", "finance"],
            "last_tested": "2024-01-15T10:30:00Z",
            "success_rate": 0.95
        }
    )


class URLConfigurationCreate(URLConfigurationBase):
    """Model for creating new URL configurations.
    
    This model extends URLConfigurationBase with validation rules and constraints
    specific to the creation process. It ensures that all required fields
    are provided and validates the data before database insertion.
    
    Inherits all fields from URLConfigurationBase with comprehensive validation.
    
    Example:
        {
            "name": "CoinDesk News Configuration",
            "url": "https://www.coindesk.com/news",
            "profile_type": "news",
            "category": "cryptocurrency",
            "description": "Configuration for extracting cryptocurrency news from CoinDesk",
            "url_patterns": ["https://www.coindesk.com/news/*"],
            "priority": 5,
            "has_official_api": true,
            "extractor_ids": ["NewsExtractor"],
            "is_active": true
        }
    """
    pass  # Inherits all validation from URLConfigurationBase


class URLConfigurationUpdate(BaseModel):
    """Model for updating existing URL configurations.
    
    This model allows partial updates to existing URL configurations.
    All fields are optional, enabling selective updates without requiring
    the full configuration data.
    
    Example:
        {
            "priority": 8,
            "is_active": false,
            "metadata": {
                "last_tested": "2024-01-16T10:30:00Z",
                "success_rate": 0.98
            }
        }
    """
    # All fields are optional for partial updates
    name: Optional[str] = Field(
        default=None,
        description="Updated name for the configuration",
        example="Updated CoinDesk Configuration",
        min_length=1
    )
    
    url: Optional[str] = Field(
        default=None,
        description="Updated primary URL",
        example="https://www.coindesk.com/markets",
        min_length=1
    )
    
    profile_type: Optional[str] = Field(
        default=None,
        description="Updated profile type",
        example="market_data",
        min_length=1
    )
    
    category: Optional[str] = Field(
        default=None,
        description="Updated category",
        example="finance",
        min_length=1
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Updated description",
        example="Enhanced configuration with market data extraction"
    )
    
    # Note: url_patterns field removed as it's not part of the database schema
    
    priority: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Updated priority level",
        example=8
    )
    
    scraping_difficulty: Optional[str] = Field(
        default=None,
        description="Updated scraping difficulty",
        example="High"
    )
    
    has_official_api: Optional[bool] = Field(
        default=None,
        description="Updated API availability status",
        example=False
    )
    
    api_pricing: Optional[str] = Field(
        default=None,
        description="Updated API pricing information",
        example="Premium tier required for full access"
    )
    
    recommendation: Optional[str] = Field(
        default=None,
        description="Updated recommendation",
        example="Medium"
    )
    
    key_data_points: Optional[List[str]] = Field(
        default=None,
        description="Updated key data points",
        example=["Price data", "Volume metrics", "Market trends"]
    )
    
    target_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated target data structure",
        example={"prices": {"symbol": "string", "price": "float", "change": "float"}}
    )
    
    rationale: Optional[str] = Field(
        default=None,
        description="Updated rationale",
        example="Comprehensive market data source with real-time updates"
    )
    
    cost_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated cost analysis",
        example={"scraping_cost": "Medium", "value_rating": "Very High"}
    )
    
    extractor_ids: Optional[List[str]] = Field(
        default=None,
        description="Updated extractor IDs",
        example=["MarketDataExtractor", "PriceExtractor"]
    )
    
    crawler_settings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated crawler settings",
        example={"timeout": 45, "retries": 5}
    )
    
    rate_limit: Optional[int] = Field(
        default=None,
        ge=1,
        description="Updated rate limit",
        example=120
    )
    
    validation_rules: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated validation rules",
        example={"required_fields": ["symbol", "price"], "min_price": 0}
    )
    
    is_active: Optional[bool] = Field(
        default=None,
        description="Updated active status",
        example=False
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated metadata",
        example={"tags": ["markets", "crypto"], "last_tested": "2024-01-16T10:30:00Z"}
    )


class URLConfigurationResponse(URLConfigurationBase):
    """Model for URL configuration API responses.
    
    This model extends URLConfigurationBase with additional fields that are
    automatically generated by the system, such as ID and timestamps.
    Used for returning URL configuration data from API endpoints.
    
    Example:
        {
            "id": "config_123e4567-e89b-12d3-a456-426614174000",
            "name": "CoinDesk News Configuration",
            "url": "https://www.coindesk.com/news",
            "profile_type": "news",
            "category": "cryptocurrency",
            "priority": 5,
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    """
    # System-generated unique identifier
    id: str = Field(
        ...,
        description="Unique identifier for the URL configuration",
        example="config_123e4567-e89b-12d3-a456-426614174000"
    )
    
    # System-generated timestamps
    created_at: datetime = Field(
        ...,
        description="Timestamp when the configuration was created",
        example="2024-01-15T10:30:00Z"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the configuration was last updated",
        example="2024-01-15T10:30:00Z"
    )


# ============================================================================
# URL MAPPING MODELS
# ============================================================================
# Models for associating URL patterns with specific extraction strategies

class URLMappingBase(BaseModel):
    """Base model for URL-to-extractor mapping configurations.
    
    This model defines the core structure for mapping URL patterns to specific
    extraction strategies within the CRY-A-4MCP platform. URL mappings enable
    automatic selection of appropriate extractors based on URL patterns.
    
    Attributes:
        name (str): Human-readable name for the URL mapping.
        url_pattern (str): Regular expression or glob pattern for matching URLs.
        url (str): Specific URL or base URL for this mapping.
        extractor_id (str): Identifier of the extraction strategy to use.
        profile_type (str): Type of profile or data source (e.g., "news", "social", "exchange").
        category (str): Category classification for the data source.
        priority (int): Priority level for this mapping (1-10, higher = more priority).
        scraping_difficulty (str): Difficulty level for scraping this source.
        has_official_api (bool): Whether the source has an official API available.
        api_pricing (Optional[str]): Pricing information for official API if available.
        recommendation (str): Recommendation level for using this source.
        key_data_points (List[str]): List of key data points available from this source.
        target_data (List[str]): List of target data types to extract.
        rationale (str): Rationale for including this source in the system.
        cost_analysis (str): Cost analysis for using this source.
        is_active (bool): Whether this mapping is currently active.
        description (Optional[str]): Human-readable description of this mapping's purpose.
        config (Optional[Dict[str, Any]]): Extractor-specific configuration overrides.
    
    Note:
        This is a base model and should not be instantiated directly.
        Use URLMappingCreate, URLMappingUpdate, or URLMappingResponse instead.
    """
    # Human-readable name for the mapping
    name: str = Field(
        ...,
        description="Human-readable name for the URL mapping",
        example="CoinDesk News Extractor",
        min_length=1
    )
    
    # URL pattern for matching target URLs
    url_pattern: str = Field(
        ...,
        description="URL pattern for matching target URLs",
        example="*.coindesk.com/*",
        min_length=1
    )
    
    # Specific URL or base URL
    url: str = Field(
        ...,
        description="Specific URL or base URL for this mapping",
        example="https://www.coindesk.com",
        min_length=1
    )
    
    # Identifier of the extraction strategy to use
    extractor_id: str = Field(
        ...,
        description="ID of the extraction strategy to use",
        example="CryptoNewsExtractor",
        min_length=1
    )
    
    # Profile type classification
    profile_type: str = Field(
        ...,
        description="Type of profile or data source",
        example="news"
    )
    
    # Category classification
    category: str = Field(
        ...,
        description="Category classification for the data source",
        example="Cryptocurrency News"
    )
    
    # Priority level for mapping selection (1-10)
    priority: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Priority level for this mapping (1-10, higher = more priority)",
        example=5
    )
    
    # Scraping difficulty level
    scraping_difficulty: str = Field(
        ...,
        description="Difficulty level for scraping this source",
        example="Medium"
    )
    
    # Whether official API is available
    has_official_api: bool = Field(
        default=False,
        description="Whether the source has an official API available",
        example=True
    )
    
    # API pricing information
    api_pricing: Optional[str] = Field(
        default=None,
        description="Pricing information for official API if available",
        example="Free tier available, paid plans start at $10/month"
    )
    
    # Recommendation level
    recommendation: str = Field(
        ...,
        description="Recommendation level for using this source",
        example="High"
    )
    
    # Key data points available
    key_data_points: List[str] = Field(
        default_factory=list,
        description="List of key data points available from this source",
        example=["Article headlines", "Publication dates", "Author information"]
    )
    
    # Target data types
    target_data: List[str] = Field(
        default_factory=list,
        description="List of target data types to extract",
        example=["News articles", "Market sentiment", "Price mentions"]
    )
    
    # Rationale for inclusion
    rationale: str = Field(
        ...,
        description="Rationale for including this source in the system",
        example="Leading cryptocurrency news source with high-quality content"
    )
    
    # Cost analysis
    cost_analysis: str = Field(
        ...,
        description="Cost analysis for using this source",
        example="Low cost, high value - free access to quality content"
    )
    
    # Whether this mapping is currently active
    is_active: bool = Field(
        default=True,
        description="Whether this mapping is currently active",
        example=True
    )
    
    # Optional human-readable description
    description: Optional[str] = Field(
        default=None,
        description="Description of this mapping's purpose",
        example="Mapping for cryptocurrency news sites"
    )
    
    # Optional extractor-specific configuration
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Extractor-specific configuration overrides",
        example={"sentiment_analysis": True, "extract_images": False}
    )


class URLMappingCreate(URLMappingBase):
    """Model for creating new URL-to-extractor mappings.
    
    This model is used when creating new URL mappings through the API.
    It inherits all fields from URLMappingBase and enforces validation rules
    for new mapping creation.
    
    Validation:
        - url_pattern must be a non-empty string
        - extractor_id must reference an existing extraction strategy
        - priority must be between 1 and 10 (inclusive)
        - is_active defaults to True if not specified
    
    Example:
        {
            "url_pattern": "*.coindesk.com/*",
            "extractor_id": "NewsExtractor",
            "priority": 8,
            "is_active": true,
            "description": "CoinDesk articles extraction mapping",
            "config": {
                "extract_author": true,
                "extract_tags": true
            }
        }
    """
    pass  # Inherits all validation from URLMappingBase


class URLMappingUpdate(BaseModel):
    """Model for updating existing URL-to-extractor mappings.
    
    This model allows partial updates to existing URL mappings.
    All fields are optional, enabling clients to update only specific
    attributes without affecting others.
    
    Validation:
        - If provided, fields must meet the same validation as creation
        - Config can be completely replaced or set to null
    
    Example:
        {
            "priority": 9,
            "is_active": false,
            "recommendation": "Medium",
            "config": {
                "extract_sentiment": true,
                "language": "en"
            }
        }
    
    Note:
        Setting a field to null will remove it from the mapping.
        Omitting a field will leave it unchanged.
    """
    # All fields are optional for partial updates
    name: Optional[str] = Field(
        default=None,
        description="Updated name",
        example="Updated Extractor Name",
        min_length=1
    )
    
    url_pattern: Optional[str] = Field(
        default=None,
        description="Updated URL pattern",
        example="*.updated-site.com/*",
        min_length=1
    )
    
    url: Optional[str] = Field(
        default=None,
        description="Updated URL",
        example="https://www.updated-site.com",
        min_length=1
    )
    
    extractor_id: Optional[str] = Field(
        default=None,
        description="Updated extractor ID",
        example="UpdatedExtractor",
        min_length=1
    )
    
    profile_type: Optional[str] = Field(
        default=None,
        description="Updated profile type",
        example="social"
    )
    
    category: Optional[str] = Field(
        default=None,
        description="Updated category",
        example="Social Media"
    )
    
    priority: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Updated priority level",
        example=7
    )
    
    scraping_difficulty: Optional[str] = Field(
        default=None,
        description="Updated scraping difficulty",
        example="High"
    )
    
    has_official_api: Optional[bool] = Field(
        default=None,
        description="Updated API availability status",
        example=True
    )
    
    api_pricing: Optional[str] = Field(
        default=None,
        description="Updated API pricing information",
        example="$20/month for premium access"
    )
    
    recommendation: Optional[str] = Field(
        default=None,
        description="Updated recommendation level",
        example="Medium"
    )
    
    key_data_points: Optional[List[str]] = Field(
        default=None,
        description="Updated key data points",
        example=["User posts", "Engagement metrics", "Follower counts"]
    )
    
    target_data: Optional[List[str]] = Field(
        default=None,
        description="Updated target data types",
        example=["Social sentiment", "User behavior", "Trending topics"]
    )
    
    rationale: Optional[str] = Field(
        default=None,
        description="Updated rationale",
        example="Updated reasoning for including this source"
    )
    
    cost_analysis: Optional[str] = Field(
        default=None,
        description="Updated cost analysis",
        example="Medium cost, high value for social data"
    )
    
    is_active: Optional[bool] = Field(
        default=None,
        description="Updated active status",
        example=False
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Updated description",
        example="Updated mapping description"
    )
    
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated configuration overrides",
        example={"timeout": 30, "retries": 3}
    )


class URLMappingResponse(URLMappingBase):
    """Response model for URL-to-extractor mapping data.
    
    This model extends URLMappingBase with additional fields that are
    automatically managed by the system, such as unique identifiers
    and timestamps for creation and modification tracking.
    
    Attributes:
        id (int): Unique identifier assigned by the database.
                 Used for referencing this mapping in other operations.
        
        created_at (Optional[str]): ISO 8601 timestamp of when the
                                   mapping was created.
                                   Automatically set by the system.
        
        updated_at (Optional[str]): ISO 8601 timestamp of the last
                                   modification to this mapping.
                                   Updated automatically on changes.
    
    Example:
        {
            "id": 456,
            "url_pattern": "*.cryptonews.com/*",
            "extractor_id": "CryptoNewsExtractor",
            "priority": 8,
            "is_active": true,
            "description": "Crypto news extraction mapping",
            "config": {"sentiment_analysis": true},
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T14:45:00Z"
        }
    """
    # Unique database identifier
    id: str = Field(
        ...,
        description="Unique identifier for the URL mapping",
        example="d16de410-659e-4f52-94cf-f9db5b8ab013"
    )
    
    # System-managed timestamps
    created_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of creation",
        example="2024-01-15T10:30:00Z"
    )
    
    updated_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of last update",
        example="2024-01-15T14:45:00Z"
    )


# ============================================================================
# CRAWLER CONFIGURATION MODELS
# ============================================================================
# Models for defining web crawler behavior and settings

class CrawlerConfigBase(BaseModel):
    """Base model for web crawler configuration settings.
    
    This model defines the comprehensive configuration structure for web crawlers
    within the CRY-A-4MCP platform. It encompasses all aspects of crawler behavior
    including performance settings, politeness policies, and content filtering.
    
    Attributes:
        name (str): Human-readable name for the crawler configuration.
                   Used for identification and management purposes.
        
        description (Optional[str]): Detailed description of the crawler's
                                    purpose, target sites, and expected behavior.
        
        url_patterns (List[str]): List of URL patterns to crawl.
                                 Uses glob or regex patterns to define target URLs.
                                 Empty list means no specific patterns.
        
        extractor_mappings (List[Dict[str, Any]]): Mappings between URL patterns
                                                  and specific extractors to use.
                                                  Enables targeted extraction strategies.
        
        schedule (Optional[str]): Cron expression for automated scheduling.
                                 When provided, crawler runs on this schedule.
                                 Format: "minute hour day month weekday"
        
        max_pages (Optional[int]): Maximum number of pages to crawl.
                                  Prevents runaway crawling and controls resource usage.
                                  Must be at least 1 if specified.
        
        delay_seconds (Optional[float]): Delay in seconds between HTTP requests.
                                        Implements politeness policy to avoid
                                        overwhelming target servers. Minimum 0.1.
        
        concurrent_requests (Optional[int]): Number of simultaneous HTTP requests (1-10).
                                            Higher values increase speed but may stress
                                            target servers. Default is 1.
        
        headers (Optional[Dict[str, str]]): Additional HTTP headers to include
                                           in all requests. Useful for authentication
                                           or custom requirements.
        
        cookies (Optional[Dict[str, str]]): Session cookies to include in requests.
                                           Enables crawling of authenticated content.
        
        proxy_config (Optional[Dict[str, Any]]): Proxy configuration for requests.
                                                Can include proxy URL, authentication,
                                                and rotation settings.
        
        retry_config (Optional[Dict[str, Any]]): Retry policy configuration.
                                                Defines how to handle failed requests,
                                                including retry counts and backoff.
        
        output_format (str): Format for extracted data output.
                            Supported formats: "json", "csv", "xml".
                            Default is "json".
        
        storage_config (Optional[Dict[str, Any]]): Storage configuration for results.
                                                  Can include database settings,
                                                  file paths, and retention policies.
        
        notification_config (Optional[Dict[str, Any]]): Notification settings for
                                                       crawler events. Can include
                                                       webhooks, emails, and alerts.
        
        status (str): Current status of the crawler configuration.
                     Values: "active", "inactive", "paused", "error".
                     Default is "inactive".
    
    Note:
        This is a base model and should not be instantiated directly.
        Use CrawlerConfigCreate, CrawlerConfigUpdate, or CrawlerConfigResponse instead.
    """
    # Human-readable crawler name
    name: str = Field(
        ...,
        description="Human-readable name for the crawler",
        example="CryptoNews Daily Crawler",
        min_length=1,
        max_length=100
    )
    
    # Optional description of crawler purpose
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of crawler purpose and scope",
        example="Daily crawler for cryptocurrency news and market updates",
        max_length=500
    )
    
    # URL patterns to crawl
    url_patterns: List[str] = Field(
        default_factory=list,
        description="List of URL patterns to crawl",
        example=["https://cryptonews.com/*", "https://coindesk.com/news/*"]
    )
    
    # Extractor mappings for targeted extraction
    extractor_mappings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Mappings between URL patterns and extractors",
        example=[
            {"pattern": "*/news/*", "extractor": "NewsExtractor"},
            {"pattern": "*/blog/*", "extractor": "BlogExtractor"}
        ]
    )
    
    # Cron schedule for automated crawling
    schedule: Optional[str] = Field(
        default=None,
        description="Cron expression for automated scheduling",
        example="0 9 * * *",
        pattern=r'^[0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+$'
    )
    
    # Maximum number of pages to crawl
    max_pages: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum number of pages to crawl",
        example=500
    )
    
    # Delay between HTTP requests
    delay_seconds: Optional[float] = Field(
        default=1.0,
        ge=0.1,
        description="Delay in seconds between requests (minimum 0.1)",
        example=2.5
    )
    
    # Number of concurrent requests
    concurrent_requests: Optional[int] = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of simultaneous requests (1-10)",
        example=3
    )
    
    # Additional HTTP headers
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional HTTP headers for requests",
        example={"Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate"}
    )
    
    # Session cookies
    cookies: Optional[Dict[str, str]] = Field(
        default=None,
        description="Session cookies for authenticated crawling",
        example={"session_id": "abc123", "auth_token": "xyz789"}
    )
    
    # Proxy configuration
    proxy_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Proxy configuration for requests",
        example={"http": "http://proxy.example.com:8080", "https": "https://proxy.example.com:8080"}
    )
    
    # Retry policy configuration
    retry_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Retry policy configuration for failed requests",
        example={"max_retries": 3, "backoff_factor": 2.0, "retry_on": [500, 502, 503, 504]}
    )
    
    # Output format for extracted data
    output_format: str = Field(
        default="json",
        description="Format for extracted data output",
        example="json",
        pattern=r'^(json|csv|xml)$'
    )
    
    # Storage configuration
    storage_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Storage configuration for crawler results",
        example={"type": "database", "connection": "postgresql://...", "table": "crawl_results"}
    )
    
    # Notification settings
    notification_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Notification settings for crawler events",
        example={"webhook_url": "https://api.example.com/webhook", "on_completion": True, "on_error": True}
    )
    
    # Crawler status
    status: str = Field(
        default="inactive",
        description="Current status of the crawler configuration",
        example="active",
        pattern=r'^(active|inactive|paused|error)$'
    )


class CrawlerConfigCreate(CrawlerConfigBase):
    """Model for creating new web crawler configurations.
    
    This model is used when creating new crawler configurations through the API.
    It inherits all fields from CrawlerConfigBase and enforces validation rules
    for new configuration creation.
    
    Validation:
        - name must be non-empty and should be unique within the system
        - url_patterns should contain at least one valid URL pattern
        - schedule must be a valid cron expression if provided
        - All numeric constraints are enforced (pages, delays, etc.)
        - output_format must be one of: json, csv, xml
        - status must be one of: active, inactive, paused, error
    
    Example:
        {
            "name": "Bitcoin News Crawler",
            "description": "Crawls major Bitcoin news sources daily",
            "url_patterns": ["https://bitcoin.com/news/*", "https://bitcoinmagazine.com/*"],
            "extractor_mappings": [
                {"pattern": "*/news/*", "extractor": "NewsExtractor"}
            ],
            "schedule": "0 8 * * *",
            "max_pages": 200,
            "delay_seconds": 1.5,
            "concurrent_requests": 2,
            "output_format": "json",
            "status": "active"
        }
    """
    pass  # Inherits all validation from CrawlerConfigBase


class CrawlerConfigUpdate(BaseModel):
    """Model for updating existing web crawler configurations.
    
    This model allows partial updates to existing crawler configurations.
    All fields are optional, enabling clients to update only specific
    settings without affecting others.
    
    Validation:
        - If provided, name must be non-empty
        - If provided, schedule must be a valid cron expression
        - All numeric constraints are enforced when fields are provided
        - If provided, output_format must be valid
        - If provided, status must be valid
    
    Example:
        {
            "max_pages": 500,
            "delay_seconds": 2.0,
            "status": "paused",
            "notification_config": {
                "email": "admin@example.com",
                "on_error": True
            }
        }
    
    Note:
        Setting a field to null will remove it from the configuration.
        Omitting a field will leave it unchanged.
    """
    # All fields are optional for partial updates
    name: Optional[str] = Field(
        default=None,
        description="Updated crawler name",
        example="Updated Crypto News Crawler",
        min_length=1,
        max_length=100
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Updated description",
        example="Updated crawler for comprehensive crypto coverage",
        max_length=500
    )
    
    url_patterns: Optional[List[str]] = Field(
        default=None,
        description="Updated URL patterns to crawl",
        example=["https://newcryptosite.com/*"]
    )
    
    extractor_mappings: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Updated extractor mappings",
        example=[{"pattern": "*/crypto/*", "extractor": "CryptoExtractor"}]
    )
    
    schedule: Optional[str] = Field(
        default=None,
        description="Updated cron schedule",
        example="0 12 * * *",
        pattern=r'^[0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+$'
    )
    
    max_pages: Optional[int] = Field(
        default=None,
        ge=1,
        description="Updated maximum pages to crawl",
        example=750
    )
    
    delay_seconds: Optional[float] = Field(
        default=None,
        ge=0.1,
        description="Updated delay between requests",
        example=1.8
    )
    
    concurrent_requests: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Updated concurrent requests count",
        example=4
    )
    
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Updated HTTP headers",
        example={"Authorization": "Bearer token123"}
    )
    
    cookies: Optional[Dict[str, str]] = Field(
        default=None,
        description="Updated session cookies",
        example={"new_session": "updated_value"}
    )
    
    proxy_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated proxy configuration",
        example={"http": "http://newproxy.com:8080"}
    )
    
    retry_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated retry policy configuration",
        example={"max_retries": 5, "backoff_factor": 1.5}
    )
    
    output_format: Optional[str] = Field(
        default=None,
        description="Updated output format",
        example="csv",
        pattern=r'^(json|csv|xml)$'
    )
    
    storage_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated storage configuration",
        example={"type": "file", "path": "/data/crawl_results"}
    )
    
    notification_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated notification settings",
        example={"slack_webhook": "https://hooks.slack.com/...", "on_completion": True}
    )
    
    status: Optional[str] = Field(
        default=None,
        description="Updated crawler status",
        example="paused",
        pattern=r'^(active|inactive|paused|error)$'
    )


class CrawlerConfigResponse(CrawlerConfigBase):
    """Response model for web crawler configuration data.
    
    This model extends CrawlerConfigBase with additional fields that are
    automatically managed by the system, such as unique identifiers
    and timestamps for creation and modification tracking.
    
    Attributes:
        id (int): Unique identifier assigned by the database.
                 Used for referencing this configuration in crawl jobs
                 and other operations.
        
        created_at (Optional[str]): ISO 8601 timestamp of when the
                                   configuration was created.
                                   Automatically set by the system.
        
        updated_at (Optional[str]): ISO 8601 timestamp of the last
                                   modification to this configuration.
                                   Updated automatically on changes.
        
        last_run_at (Optional[str]): ISO 8601 timestamp of the last
                                    time this crawler was executed.
                                    Updated after each crawl completion.
        
        next_run_at (Optional[str]): ISO 8601 timestamp of the next
                                    scheduled crawl execution.
                                    Calculated based on schedule configuration.
    
    Example:
        {
            "id": 789,
            "name": "Ethereum News Crawler",
            "description": "Daily Ethereum ecosystem news crawler",
            "url_patterns": ["https://ethereum.org/news/*"],
            "schedule": "0 9 * * *",
            "max_pages": 300,
            "delay_seconds": 1.0,
            "concurrent_requests": 2,
            "output_format": "json",
            "status": "active",
            "created_at": "2024-01-15T09:00:00Z",
            "updated_at": "2024-01-15T15:30:00Z",
            "last_run_at": "2024-01-16T09:00:00Z",
            "next_run_at": "2024-01-17T09:00:00Z"
        }
    """
    # Unique database identifier
    id: str = Field(
        ...,
        description="Unique identifier for the crawler configuration",
        example="7e0bb2bd-7f77-4b2f-a99b-896eaa8bd217"
    )
    
    # System-managed timestamps
    created_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of creation",
        example="2024-01-15T09:00:00Z"
    )
    
    updated_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of last update",
        example="2024-01-15T15:30:00Z"
    )
    
    last_run_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of last crawl execution",
        example="2024-01-16T09:00:00Z"
    )
    
    next_run_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of next scheduled execution",
        example="2024-01-17T09:00:00Z"
    )


# ============================================================================
# CRAWL JOB MODELS
# ============================================================================
# Models for managing individual crawl job executions

class CrawlJobBase(BaseModel):
    """Base model for crawl job execution configurations.
    
    This model defines the structure for individual crawl job instances within
    the CRY-A-4MCP platform. Crawl jobs represent specific executions of crawler
    configurations, with their own lifecycle, priority, and monitoring settings.
    
    Attributes:
        crawler_id (int): Reference to the crawler configuration to use.
                         Must correspond to an existing CrawlerConfig.
                         Defines the crawling behavior and settings.
        
        name (Optional[str]): Human-readable name for this specific crawl job.
                             If not provided, a name will be auto-generated
                             based on the crawler configuration and timestamp.
        
        description (Optional[str]): Detailed description of this crawl job's
                                    specific purpose, scope, or special requirements.
                                    Useful for tracking and auditing purposes.
        
        urls (List[str]): List of specific URLs to crawl for this job.
                         Can override or supplement the crawler configuration's
                         URL patterns. Empty list uses configuration patterns.
        
        priority (int): Execution priority for this job (1-10, higher = more priority).
                       When multiple jobs are queued, higher priority jobs
                       are executed first. Default is 5 (medium priority).
        
        max_pages (Optional[int]): Maximum number of pages to crawl for this job.
                                  Overrides the crawler configuration's max_pages
                                  setting if specified. Must be at least 1.
        
        max_depth (Optional[int]): Maximum crawl depth from starting URLs.
                                  Controls how many levels deep the crawler
                                  will follow links. Must be at least 1.
        
        config_overrides (Optional[Dict[str, Any]]): Job-specific configuration overrides.
                                                    Allows customizing crawler behavior
                                                    for this specific job execution.
        
        scheduled_at (Optional[str]): ISO 8601 timestamp for scheduled execution.
                                     If provided, job will be queued for execution
                                     at this time instead of immediately.
        
        timeout_seconds (Optional[int]): Maximum execution time in seconds.
                                        Job will be terminated if it exceeds this limit.
                                        Prevents runaway jobs from consuming resources.
    
    Note:
        This is a base model and should not be instantiated directly.
        Use CrawlJobCreate, CrawlJobUpdate, or CrawlJobResponse instead.
    """
    # Reference to crawler configuration
    crawler_id: int = Field(
        ...,
        description="ID of the crawler configuration to use",
        example=123,
        gt=0
    )
    
    # Optional job name
    name: Optional[str] = Field(
        default=None,
        description="Human-readable name for this crawl job",
        example="Daily Crypto News Crawl - 2024-01-15",
        max_length=200
    )
    
    # Optional job description
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of this crawl job's purpose",
        example="Emergency crawl to capture breaking news about Bitcoin ETF approval",
        max_length=1000
    )
    
    # Specific URLs to crawl
    urls: List[str] = Field(
        default_factory=list,
        description="List of specific URLs to crawl for this job",
        example=["https://cryptonews.com/breaking", "https://coindesk.com/latest"]
    )
    
    # Job execution priority
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Execution priority (1-10, higher = more priority)",
        example=8
    )
    
    # Maximum pages to crawl
    max_pages: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum number of pages to crawl",
        example=100
    )
    
    # Maximum crawl depth
    max_depth: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum crawl depth from starting URLs",
        example=3
    )
    
    # Configuration overrides
    config_overrides: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Job-specific configuration overrides",
        example={"delay_seconds": 0.5, "extract_images": True}
    )
    
    # Scheduled execution time
    scheduled_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp for scheduled execution",
        example="2024-01-16T09:00:00Z"
    )
    
    # Execution timeout
    timeout_seconds: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum execution time in seconds",
        example=3600
    )


class CrawlJobCreate(CrawlJobBase):
    """Model for creating new crawl job executions.
    
    This model is used when creating new crawl jobs through the API.
    It inherits all fields from CrawlJobBase and enforces validation rules
    for new job creation.
    
    Validation:
        - crawler_id must reference an existing, active crawler configuration
        - priority must be between 1 and 10 (inclusive)
        - max_pages and max_depth must be at least 1 if specified
        - timeout_seconds must be at least 1 if specified
        - scheduled_at must be a valid ISO 8601 timestamp if provided
        - urls must contain valid URL formats if provided
    
    Example:
        {
            "crawler_id": 456,
            "name": "Urgent Market Analysis Crawl",
            "description": "High-priority crawl for market crash analysis",
            "urls": ["https://coindesk.com/markets", "https://cryptonews.com/market"],
            "priority": 9,
            "max_pages": 50,
            "max_depth": 2,
            "timeout_seconds": 1800,
            "config_overrides": {
                "delay_seconds": 0.5,
                "extract_sentiment": true
            }
        }
    """
    pass  # Inherits all validation from CrawlJobBase


class CrawlJobUpdate(BaseModel):
    """Model for updating existing crawl job configurations.
    
    This model allows partial updates to existing crawl jobs.
    All fields are optional, enabling clients to update only specific
    attributes without affecting others. Note that some fields may not
    be updatable once a job is running.
    
    Validation:
        - If provided, priority must be between 1 and 10
        - If provided, max_pages and max_depth must be at least 1
        - If provided, timeout_seconds must be at least 1
        - Status updates are restricted based on current job state
        - URLs must be valid formats if provided
    
    Example:
        {
            "priority": 10,
            "max_pages": 200,
            "status": "paused",
            "config_overrides": {
                "concurrent_requests": 1,
                "delay_seconds": 2.0
            }
        }
    
    Note:
        Some fields cannot be updated while a job is running.
        Status transitions must follow valid state machine rules.
    """
    # All fields are optional for partial updates
    name: Optional[str] = Field(
        default=None,
        description="Updated job name",
        example="Updated Crypto Analysis Crawl",
        max_length=200
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Updated job description",
        example="Updated description with new requirements",
        max_length=1000
    )
    
    urls: Optional[List[str]] = Field(
        default=None,
        description="Updated list of URLs to crawl",
        example=["https://newsite.com/crypto", "https://updated-source.com/news"]
    )
    
    priority: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Updated execution priority",
        example=7
    )
    
    max_pages: Optional[int] = Field(
        default=None,
        ge=1,
        description="Updated maximum pages to crawl",
        example=150
    )
    
    max_depth: Optional[int] = Field(
        default=None,
        ge=1,
        description="Updated maximum crawl depth",
        example=4
    )
    
    config_overrides: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated configuration overrides",
        example={"extract_metadata": True, "follow_redirects": False}
    )
    
    scheduled_at: Optional[str] = Field(
        default=None,
        description="Updated scheduled execution time",
        example="2024-01-17T10:00:00Z"
    )
    
    timeout_seconds: Optional[int] = Field(
        default=None,
        ge=1,
        description="Updated execution timeout",
        example=7200
    )
    
    status: Optional[str] = Field(
        default=None,
        description="Updated job status (limited transitions allowed)",
        example="paused",
        pattern=r'^(pending|running|paused|completed|failed|cancelled)$'
    )


class CrawlJobResponse(CrawlJobBase):
    """Response model for crawl job execution data.
    
    This model extends CrawlJobBase with additional fields that track
    the job's execution state, progress, and results. These fields are
    automatically managed by the system during job execution.
    
    Attributes:
        id (int): Unique identifier assigned by the database.
                 Used for referencing this job in status checks and operations.
        
        status (str): Current execution status of the job.
                     Values: "pending", "running", "paused", "completed", "failed", "cancelled"
                     Automatically updated as the job progresses.
        
        created_at (Optional[str]): ISO 8601 timestamp of when the job was created.
                                   Automatically set by the system.
        
        updated_at (Optional[str]): ISO 8601 timestamp of the last update.
                                   Updated whenever job properties change.
        
        started_at (Optional[str]): ISO 8601 timestamp of when job execution began.
                                   Set when the job transitions to "running" status.
        
        completed_at (Optional[str]): ISO 8601 timestamp of when job execution finished.
                                     Set when the job reaches a terminal state.
        
        progress (Optional[Dict[str, Any]]): Real-time progress information.
                                           Includes metrics like pages crawled,
                                           current URL, and completion percentage.
        
        results_count (Optional[int]): Number of successful extraction results.
                                      Updated in real-time during job execution.
        
        error_message (Optional[str]): Error message if the job failed.
                                      Contains detailed information about the failure
                                      for debugging and troubleshooting.
        
        logs (Optional[List[str]]): Recent log entries from job execution.
                                   Useful for monitoring progress and debugging issues.
                                   Limited to most recent entries to prevent bloat.
    
    Example:
        {
            "id": 1001,
            "crawler_id": 456,
            "name": "Market Analysis Crawl",
            "description": "Emergency market data collection",
            "urls": ["https://coindesk.com/markets"],
            "priority": 9,
            "max_pages": 50,
            "status": "completed",
            "created_at": "2024-01-15T14:00:00Z",
            "started_at": "2024-01-15T14:01:00Z",
            "completed_at": "2024-01-15T14:25:00Z",
            "progress": {
                "pages_crawled": 45,
                "pages_extracted": 42,
                "completion_percentage": 100,
                "current_url": null
            },
            "results_count": 42,
            "logs": [
                "2024-01-15T14:25:00Z: Job completed successfully",
                "2024-01-15T14:24:55Z: Extracted data from final page",
                "2024-01-15T14:24:50Z: Processing page 45 of 45"
            ]
        }
    """
    # Unique database identifier
    id: int = Field(
        ...,
        description="Unique identifier for the crawl job",
        example=1001
    )
    
    # Current job status
    status: str = Field(
        ...,
        description="Current execution status of the job",
        example="running",
        pattern=r'^(pending|running|paused|completed|failed|cancelled)$'
    )
    
    # System-managed timestamps
    created_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of job creation",
        example="2024-01-15T14:00:00Z"
    )
    
    updated_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of last update",
        example="2024-01-15T14:25:00Z"
    )
    
    started_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of job start",
        example="2024-01-15T14:01:00Z"
    )
    
    completed_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of job completion",
        example="2024-01-15T14:25:00Z"
    )
    
    # Progress and results information
    progress: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Real-time progress information",
        example={
            "pages_crawled": 45,
            "pages_extracted": 42,
            "completion_percentage": 90,
            "current_url": "https://coindesk.com/markets/page-45",
            "estimated_time_remaining": 120
        }
    )
    
    results_count: Optional[int] = Field(
        default=None,
        description="Number of successful extraction results",
        example=42,
        ge=0
    )
    
    # Error information
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if job failed",
        example="Connection timeout after 30 seconds",
        max_length=2000
    )
    
    # Execution logs
    logs: Optional[List[str]] = Field(
        default=None,
        description="Recent log entries from job execution",
        example=[
            "2024-01-15T14:25:00Z: Job completed successfully",
            "2024-01-15T14:24:55Z: Extracted data from page 45",
            "2024-01-15T14:24:50Z: Processing final batch of URLs"
        ]
    )


# ============================================================================
# TEST URL MODELS
# ============================================================================
# Models for testing and validating URL extraction processes

class LLMConfig(BaseModel):
    """Configuration for LLM-based extraction.
    
    This model defines the configuration parameters for LLM-based extraction,
    including provider settings, model selection, and processing parameters.
    """
    provider: str = Field(
        ...,
        description="LLM provider (e.g., 'openai', 'anthropic', 'openrouter')",
        example="openrouter"
    )
    model: str = Field(
        ...,
        description="Model identifier for the LLM provider",
        example="anthropic/claude-3.5-sonnet"
    )
    api_key: str = Field(
        ...,
        description="API key for the LLM provider",
        example="your-api-key"
    )
    temperature: float = Field(
        default=0.1,
        description="Temperature for LLM generation (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    max_tokens: int = Field(
        default=4000,
        description="Maximum tokens for LLM response",
        gt=0,
        le=8000
    )
    timeout: int = Field(
        default=30,
        description="Timeout in seconds for LLM requests",
        gt=0,
        le=300
    )

class TestURLRequest(BaseModel):
    """Model for testing URL extraction capabilities.
    
    This model defines the structure for testing URL extraction through the API.
    It allows users to test extraction strategies against specific URLs before
    setting up full crawl jobs, enabling validation and debugging of extraction logic.
    
    The testing functionality is crucial for:
    - Validating extractor configurations before deployment
    - Debugging extraction issues with specific URLs
    - Experimenting with different AI models and instructions
    - Quality assurance for new extraction strategies
    - Performance benchmarking and optimization
    
    Attributes:
        url (str): The target URL to test extraction against.
                  Must be a valid, accessible URL with proper HTTP/HTTPS protocol.
                  The URL will be fetched and processed using the specified extractor.
                  Should represent typical content that will be crawled in production.
        
        extractor_id (Optional[str]): Specific extractor to use for testing.
                                     If not provided, the system will automatically
                                     select the best extractor based on URL patterns
                                     and configured URL mappings. Use this to test
                                     specific extractors or override automatic selection.
        
        model (Optional[str]): AI model to use for extraction processing.
                              Defaults to "openrouter/anthropic/claude-3.5-sonnet".
                              Must be a valid OpenRouter model identifier.
                              Different models may produce different extraction results.
        
        custom_instructions (Optional[str]): Custom extraction instructions.
                                           Overrides the default extractor instructions
                                           for this specific test. Useful for experimenting
                                           with different extraction approaches, testing
                                           new instruction formats, or debugging issues.
    
    Validation:
        - URL must be a valid HTTP/HTTPS URL format
        - extractor_id must reference an existing extractor if provided
        - model must be available in the OpenRouter catalog
        - custom_instructions should be clear and specific
    
    Example:
        {
            "url": "https://cryptonews.com/news/bitcoin-reaches-new-high",
            "extractor_id": "CryptoNewsExtractor",
            "model": "openrouter/anthropic/claude-3.5-sonnet",
            "custom_instructions": "Extract title, content, and sentiment. Focus on price mentions and market analysis."
        }
    
    Usage Tips:
        - Test with representative URLs from your target domains
        - Try different models to compare extraction quality
        - Use custom instructions to refine extraction behavior
        - Test edge cases like paywalled content or dynamic pages
    """
    # Target URL for extraction testing
    url: str = Field(
        ...,
        description="Target URL to test extraction against",
        example="https://cryptonews.com/news/bitcoin-reaches-new-high",
        min_length=1,
        pattern=r'^https?://[^\s/$.?#].[^\s]*$'
    )
    
    # Optional specific extractor to use
    extractor_id: Optional[str] = Field(
        default=None,
        description="Specific extractor ID to use for testing",
        example="CryptoNewsExtractor",
        max_length=100
    )
    
    # AI model for extraction processing
    model: Optional[str] = Field(
        default="openrouter/anthropic/claude-3.5-sonnet",
        description="AI model to use for extraction processing",
        example="openrouter/anthropic/claude-3.5-sonnet",
        max_length=200
    )
    
    # Custom extraction instructions
    custom_instructions: Optional[str] = Field(
        default=None,
        description="Custom extraction instructions for this test",
        example="Extract title, content, author, and publication date. Include sentiment analysis and identify key price mentions.",
        max_length=2000
    )
    
    # LLM configuration for LLM-based extraction
    llm_config: Optional[LLMConfig] = Field(
        default=None,
        description="LLM configuration for AI-based extraction"
    )
    
    # Extraction instruction for LLM
    instruction: Optional[str] = Field(
        default=None,
        description="Extraction instruction for LLM-based extraction",
        example="Extract the main content and key information from this webpage.",
        max_length=2000
    )
    
    # JSON schema for structured extraction
    schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional JSON schema for structured extraction",
        example={"title": "string", "content": "string", "author": "string"}
    )


class TestURLResponse(BaseModel):
    """Response model for URL extraction testing results.
    
    This model provides comprehensive feedback about URL extraction testing,
    including the extracted data, metadata about the extraction process,
    and any errors or issues encountered during testing.
    
    Attributes:
        url (str): The original URL that was tested.
                  Echoed back for reference and correlation.
        
        extractor_used (str): The actual extractor that was used for extraction.
                             May differ from the requested extractor if automatic
                             selection was used or if the requested extractor was not available.
        
        extraction_result (Dict[str, Any]): The structured data extracted from the URL.
                                           Format depends on the extractor used.
                                           Contains the actual extracted content and metadata.
        
        metadata (Dict[str, Any]): Additional metadata about the extraction process.
                                  Includes timing information, content statistics,
                                  processing details, and quality metrics.
        
        success (bool): Whether the extraction was successful.
                       True if data was extracted without critical errors.
                       False if extraction failed or encountered major issues.
        
        error_message (Optional[str]): Detailed error message if extraction failed.
                                      Contains information for debugging and troubleshooting.
                                      Only present when success is False.
    
    Example:
        {
            "url": "https://cryptonews.com/news/bitcoin-reaches-new-high",
            "extractor_used": "CryptoNewsExtractor",
            "extraction_result": {
                "title": "Bitcoin Reaches New All-Time High",
                "content": "Bitcoin has surged to a new record...",
                "author": "John Crypto",
                "published_date": "2024-01-15T10:30:00Z",
                "sentiment": "positive",
                "price_mentions": ["$50,000", "$49,500"]
            },
            "metadata": {
                "extraction_time_ms": 1250,
                "content_length": 2048,
                "model_used": "claude-3.5-sonnet",
                "confidence_score": 0.95,
                "tokens_used": 1500
            },
            "success": true
        }
    """
    # Original URL that was tested
    url: str = Field(
        ...,
        description="The original URL that was tested",
        example="https://cryptonews.com/news/bitcoin-reaches-new-high"
    )
    
    # Extractor that was actually used
    extractor_used: str = Field(
        ...,
        description="The actual extractor used for extraction",
        example="CryptoNewsExtractor"
    )
    
    # Extracted data results
    extraction_result: Dict[str, Any] = Field(
        ...,
        description="The structured data extracted from the URL",
        example={
            "title": "Bitcoin Reaches New All-Time High",
            "content": "Bitcoin has surged to a new record high...",
            "author": "John Crypto",
            "published_date": "2024-01-15T10:30:00Z",
            "sentiment": "positive",
            "tags": ["bitcoin", "cryptocurrency", "price", "market"]
        }
    )
    
    # Extraction process metadata
    metadata: Dict[str, Any] = Field(
        ...,
        description="Additional metadata about the extraction process",
        example={
            "extraction_time_ms": 1250,
            "content_length": 2048,
            "model_used": "claude-3.5-sonnet",
            "confidence_score": 0.95,
            "tokens_used": 1500,
            "http_status": 200,
            "content_type": "text/html",
            "page_load_time_ms": 850
        }
    )
    
    # Success indicator
    success: bool = Field(
        ...,
        description="Whether the extraction was successful",
        example=True
    )
    
    # Error message if extraction failed
    error_message: Optional[str] = Field(
        default=None,
        description="Detailed error message if extraction failed",
        example="Failed to connect to URL: Connection timeout after 30 seconds",
        max_length=1000
    )


# ============================================================================
# OPENROUTER MODELS
# ============================================================================
# Models for AI model integration and configuration through OpenRouter

class OpenRouterModel(BaseModel):
    """Model for OpenRouter AI model information and capabilities.
    
    This model represents the comprehensive information about AI models available
    through the OpenRouter platform for use in the CRY-A-4MCP extraction system.
    It provides detailed specifications, pricing, and capability information.
    
    Attributes:
        id (str): Unique identifier for the model in OpenRouter.
                 Used for API calls and model selection.
                 Format typically follows "provider/model-name" pattern.
        
        name (str): Human-readable display name of the model.
               Used in user interfaces and documentation.
               May include version information and provider details.
        
        description (Optional[str]): Detailed description of the model's
                                   capabilities, strengths, and intended use cases.
                                   Helps users select appropriate models for their needs.
        
        pricing (Optional[Dict[str, Any]]): Pricing information for model usage.
                                          Includes costs per token, request, or other metrics.
                                          Structure varies by provider and model type.
        
        context_length (Optional[int]): Maximum context length in tokens.
                                      Determines how much text can be processed
                                      in a single request. Critical for large documents.
        
        architecture (Optional[Dict[str, Any]]): Technical details about the model architecture.
                                               Includes information like model type,
                                               parameter count, and training details.
        
        top_provider (Optional[Dict[str, Any]]): Information about the primary provider.
                                               Includes provider name, reliability metrics,
                                               and service level details.
        
        per_request_limits (Optional[Dict[str, Any]]): Rate limiting and usage constraints.
                                                     Includes request limits, token limits,
                                                     and cooldown periods.
    
    Example:
        {
            "id": "openrouter/anthropic/claude-3.5-sonnet",
            "name": "Claude 3.5 Sonnet",
            "description": "Anthropic's most capable model for complex reasoning and analysis",
            "pricing": {
                "prompt": "0.000003",
                "completion": "0.000015",
                "currency": "USD",
                "unit": "token"
            },
            "context_length": 200000,
            "architecture": {
                "modality": "text",
                "tokenizer": "claude",
                "instruct_type": "claude"
            },
            "top_provider": {
                "name": "Anthropic",
                "max_completion_tokens": 4096,
                "is_moderated": true
            },
            "per_request_limits": {
                "prompt_tokens": 200000,
                "completion_tokens": 4096
            }
        }
    
    Note:
        This model is used for displaying available AI models and their
        capabilities. It helps users make informed decisions about which
        models to use for their specific extraction requirements.
    """
    # Unique model identifier
    id: str = Field(
        ...,
        description="Unique identifier for the model in OpenRouter",
        example="openrouter/anthropic/claude-3.5-sonnet"
    )
    
    # Human-readable model name
    name: str = Field(
        ...,
        description="Human-readable display name of the model",
        example="Claude 3.5 Sonnet"
    )
    
    # Model description and capabilities
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of model capabilities and use cases",
        example="Anthropic's most capable model for complex reasoning, analysis, and creative tasks"
    )
    
    # Pricing information
    pricing: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Pricing information for model usage",
        example={
            "prompt": "0.000003",
            "completion": "0.000015",
            "currency": "USD",
            "unit": "token",
            "requests": "0.01"
        }
    )
    
    # Maximum context length
    context_length: Optional[int] = Field(
        default=None,
        description="Maximum context length in tokens",
        example=200000,
        ge=1
    )
    
    # Model architecture details
    architecture: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Technical details about model architecture",
        example={
            "modality": "text",
            "tokenizer": "claude",
            "instruct_type": "claude",
            "parameters": "175B"
        }
    )
    
    # Provider information
    top_provider: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Information about the primary model provider",
        example={
            "name": "Anthropic",
            "max_completion_tokens": 4096,
            "is_moderated": True,
            "uptime": 0.999
        }
    )
    
    # Usage limits and constraints
    per_request_limits: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Rate limiting and usage constraints per request",
        example={
            "prompt_tokens": 200000,
            "completion_tokens": 4096,
            "requests_per_minute": 60,
            "requests_per_day": 1000
        }
    )