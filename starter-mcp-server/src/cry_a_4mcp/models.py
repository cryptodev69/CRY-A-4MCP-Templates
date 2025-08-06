"""Pydantic models for the Crypto AI platform.

This module defines the data models for both URL Configuration and URL Mapping
systems, maintaining clear separation between business and technical concerns.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


# URL Configuration Models (Business-focused)
class URLConfigurationCreate(BaseModel):
    """Model for creating a new URL configuration with business metadata."""
    name: str = Field(..., description="Name/title of the configuration")
    description: Optional[str] = Field(None, description="Business description")
    url: str = Field(..., description="Primary URL for this configuration")
    profile_type: str = Field(..., description="Target user profile type")
    category: str = Field(..., description="Business category classification")
    business_priority: int = Field(1, ge=1, le=10, description="Business priority level")
    scraping_difficulty: Optional[str] = Field(None, description="Business assessment of difficulty")
    has_official_api: bool = Field(False, description="Whether an official API is available")
    api_pricing: Optional[str] = Field(None, description="API pricing information")
    recommendation: Optional[str] = Field(None, description="Business recommendation")
    key_data_points: Optional[List[str]] = Field(default_factory=list, description="Key business data points")
    target_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Target business data structure")
    rationale: Optional[str] = Field(None, description="Business rationale for inclusion")
    cost_analysis: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Business cost analysis")
    business_value: Optional[str] = Field(None, description="Assessment of business value")
    compliance_notes: Optional[str] = Field(None, description="Compliance and legal notes")
    is_active: bool = Field(True, description="Whether this configuration is active")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional business metadata")

    @validator('url')
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        return v.strip()

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class URLConfigurationUpdate(BaseModel):
    """Model for updating an existing URL configuration."""
    name: Optional[str] = Field(None, description="Name/title of the configuration")
    description: Optional[str] = Field(None, description="Business description")
    url: Optional[str] = Field(None, description="Primary URL for this configuration")
    profile_type: Optional[str] = Field(None, description="Target user profile type")
    category: Optional[str] = Field(None, description="Business category classification")
    business_priority: Optional[int] = Field(None, ge=1, le=10, description="Business priority level")
    scraping_difficulty: Optional[str] = Field(None, description="Business assessment of difficulty")
    has_official_api: Optional[bool] = Field(None, description="Whether an official API is available")
    api_pricing: Optional[str] = Field(None, description="API pricing information")
    recommendation: Optional[str] = Field(None, description="Business recommendation")
    key_data_points: Optional[List[str]] = Field(None, description="Key business data points")
    target_data: Optional[Dict[str, Any]] = Field(None, description="Target business data structure")
    rationale: Optional[str] = Field(None, description="Business rationale for inclusion")
    cost_analysis: Optional[Dict[str, Any]] = Field(None, description="Business cost analysis")
    business_value: Optional[str] = Field(None, description="Assessment of business value")
    compliance_notes: Optional[str] = Field(None, description="Compliance and legal notes")
    is_active: Optional[bool] = Field(None, description="Whether this configuration is active")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional business metadata")


class URLConfiguration(BaseModel):
    """Model representing a complete URL configuration with business metadata."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name/title of the configuration")
    description: Optional[str] = Field(None, description="Business description")
    url: str = Field(..., description="Primary URL for this configuration")
    profile_type: str = Field(..., description="Target user profile type")
    category: str = Field(..., description="Business category classification")
    business_priority: int = Field(..., description="Business priority level")
    scraping_difficulty: Optional[str] = Field(None, description="Business assessment of difficulty")
    has_official_api: bool = Field(..., description="Whether an official API is available")
    api_pricing: Optional[str] = Field(None, description="API pricing information")
    recommendation: Optional[str] = Field(None, description="Business recommendation")
    key_data_points: List[str] = Field(..., description="Key business data points")
    target_data: Dict[str, Any] = Field(..., description="Target business data structure")
    rationale: Optional[str] = Field(None, description="Business rationale for inclusion")
    cost_analysis: Dict[str, Any] = Field(..., description="Business cost analysis")
    business_value: Optional[str] = Field(None, description="Assessment of business value")
    compliance_notes: Optional[str] = Field(None, description="Compliance and legal notes")
    is_active: bool = Field(..., description="Whether this configuration is active")
    metadata: Dict[str, Any] = Field(..., description="Additional business metadata")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


# URL Mapping Models (Technical-focused)
class URLMappingCreate(BaseModel):
    """Model for creating a new URL mapping with technical configuration."""
    name: Optional[str] = Field(None, description="Name/title of the mapping")
    url_config_id: str = Field(..., description="Foreign key to url_configurations.id")
    extractor_id: str = Field(..., description="Which extractor to use")
    rate_limit: int = Field(60, ge=1, description="Rate limiting setting (requests per minute)")
    priority: Optional[int] = Field(1, ge=1, le=10, description="Priority level for processing")
    crawler_settings: Optional[str] = Field(None, description="Crawler-specific settings as JSON string")
    validation_rules: Optional[str] = Field(None, description="Technical validation rules as JSON string")
    is_active: bool = Field(True, description="Whether this mapping is active")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    notes: Optional[str] = Field(None, description="Additional notes")
    category: Optional[str] = Field(None, description="Category classification")
    metadata: Optional[str] = Field(None, description="Additional technical metadata as JSON string")

    @validator('url_config_id')
    def validate_url_config_id(cls, v):
        if not v or not v.strip():
            raise ValueError('URL Config ID cannot be empty')
        return v.strip()

    @validator('extractor_id')
    def validate_extractor_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Extractor ID cannot be empty')
        return v.strip()


class URLMappingUpdate(BaseModel):
    """Model for updating an existing URL mapping."""
    name: Optional[str] = Field(None, description="Name/title of the mapping")
    url_config_id: Optional[str] = Field(None, description="Foreign key to url_configurations.id")
    extractor_id: Optional[str] = Field(None, description="Which extractor to use")
    rate_limit: Optional[int] = Field(None, ge=1, description="Rate limiting setting")
    priority: Optional[int] = Field(None, ge=1, le=10, description="Priority level for processing")
    crawler_settings: Optional[str] = Field(None, description="Crawler-specific settings as JSON string")
    validation_rules: Optional[str] = Field(None, description="Technical validation rules as JSON string")
    is_active: Optional[bool] = Field(None, description="Whether this mapping is active")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    notes: Optional[str] = Field(None, description="Additional notes")
    category: Optional[str] = Field(None, description="Category classification")
    metadata: Optional[str] = Field(None, description="Additional technical metadata as JSON string")


class URLMapping(BaseModel):
    """Model representing a complete URL mapping with technical configuration."""
    id: str = Field(..., description="Unique identifier")
    name: Optional[str] = Field(None, description="Name/title of the mapping")
    url_config_id: str = Field(..., description="Foreign key to url_configurations.id")
    extractor_id: str = Field(..., description="Which extractor to use")
    rate_limit: int = Field(..., description="Rate limiting setting")
    priority: Optional[int] = Field(1, ge=1, le=10, description="Priority level for processing")
    crawler_settings: Optional[str] = Field(None, description="Crawler-specific settings as JSON string")
    validation_rules: Optional[str] = Field(None, description="Technical validation rules as JSON string")
    is_active: bool = Field(..., description="Whether this mapping is active")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    notes: Optional[str] = Field(None, description="Additional notes")
    category: Optional[str] = Field(None, description="Category classification")
    metadata: Optional[str] = Field(None, description="Additional technical metadata as JSON string")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


# Response Models
class URLConfigurationResponse(BaseModel):
    """Response model for URL configuration operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[URLConfiguration] = Field(None, description="Configuration data if applicable")


class URLConfigurationListResponse(BaseModel):
    """Response model for listing URL configurations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: List[URLConfiguration] = Field(..., description="List of configurations")
    total: int = Field(..., description="Total number of configurations")


class URLMappingResponse(BaseModel):
    """Response model for URL mapping operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[URLMapping] = Field(None, description="Mapping data if applicable")


class URLMappingListResponse(BaseModel):
    """Response model for listing URL mappings."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: List[URLMapping] = Field(..., description="List of mappings")
    total: int = Field(..., description="Total number of mappings")


# Database Statistics Models
class URLConfigurationStats(BaseModel):
    """Model for URL configuration database statistics."""
    total_configurations: int = Field(..., description="Total number of configurations")
    active_configurations: int = Field(..., description="Number of active configurations")
    inactive_configurations: int = Field(..., description="Number of inactive configurations")
    configurations_by_profile: Dict[str, int] = Field(..., description="Configurations grouped by profile type")
    configurations_by_category: Dict[str, int] = Field(..., description="Configurations grouped by category")


class URLMappingStats(BaseModel):
    """Model for URL mapping database statistics."""
    total_mappings: int = Field(..., description="Total number of mappings")
    active_mappings: int = Field(..., description="Number of active mappings")
    inactive_mappings: int = Field(..., description="Number of inactive mappings")
    extractor_distribution: Dict[str, int] = Field(..., description="Mappings grouped by extractor")


# Error Models
class ErrorResponse(BaseModel):
    """Model for error responses."""
    success: bool = Field(False, description="Always false for error responses")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")