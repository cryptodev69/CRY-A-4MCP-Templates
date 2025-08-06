#!/usr/bin/env python3
"""
Schema validation module for the cry_a_4mcp.crawl4ai package.

This module provides utilities for validating extraction results against JSON schemas,
generating dynamic schemas based on content type, and managing specialized schemas
for different domains.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from enum import Enum
import jsonschema
from jsonschema import ValidationError, Draft7Validator, validators

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Enum representing different types of content for schema selection."""
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    BLOG = "blog"
    FORUM = "forum"
    RESEARCH = "research"
    CRYPTO = "crypto"
    GENERAL = "general"


class SchemaValidationError(Exception):
    """Exception raised when schema validation fails."""
    def __init__(self, message: str, validation_errors: List[Dict[str, Any]]):
        self.validation_errors = validation_errors
        super().__init__(message)


def extend_with_default(validator_class):
    """Extend the validator class to fill in default values."""
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property_name, subschema in properties.items():
            if "default" in subschema and property_name not in instance:
                instance[property_name] = subschema["default"]

        for error in validate_properties(validator, properties, instance, schema):
            yield error

    return validators.extend(validator_class, {"properties": set_defaults})


# Create a validator that fills in default values
DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


class SchemaRegistry:
    """Registry for managing JSON schemas for different content types."""

    # Base schema for all extraction results
    BASE_SCHEMA = {
        "type": "object",
        "properties": {
            "_metadata": {
                "type": "object",
                "properties": {
                    "strategy": {"type": "string"},
                    "strategy_version": {"type": "string"},
                    "model": {"type": "string"},
                    "timestamp": {"type": "number"},
                    "usage": {
                        "type": "object",
                        "properties": {
                            "prompt_tokens": {"type": "integer"},
                            "completion_tokens": {"type": "integer"},
                            "total_tokens": {"type": "integer"}
                        }
                    },
                    "performance": {
                        "type": "object",
                        "properties": {
                            "extraction_time": {"type": "number"}
                        }
                    }
                }
            }
        }
    }

    # Schema for news content
    NEWS_SCHEMA = {
        "type": "object",
        "required": ["headline", "summary"],
        "properties": {
            "headline": {"type": "string"},
            "summary": {"type": "string"},
            "author": {"type": "string"},
            "publication_date": {"type": "string"},
            "category": {"type": "string"},
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral"],
                "default": "neutral"
            },
            "key_points": {
                "type": "array",
                "items": {"type": "string"}
            },
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "relevance": {"type": "number"}
                    },
                    "required": ["name", "type"]
                }
            }
        }
    }

    # Schema for social media content
    SOCIAL_MEDIA_SCHEMA = {
        "type": "object",
        "required": ["content", "sentiment"],
        "properties": {
            "content": {"type": "string"},
            "username": {"type": "string"},
            "platform": {"type": "string"},
            "post_date": {"type": "string"},
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral"],
                "default": "neutral"
            },
            "engagement": {
                "type": "object",
                "properties": {
                    "likes": {"type": "integer"},
                    "shares": {"type": "integer"},
                    "comments": {"type": "integer"}
                }
            },
            "hashtags": {
                "type": "array",
                "items": {"type": "string"}
            },
            "mentions": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }

    # Schema for crypto content
    CRYPTO_SCHEMA = {
        "type": "object",
        "required": ["headline", "summary", "sentiment"],
        "properties": {
            "headline": {"type": "string"},
            "summary": {"type": "string"},
            "sentiment": {
                "type": "string",
                "enum": ["bullish", "bearish", "neutral"],
                "default": "neutral"
            },
            "category": {
                "type": "string",
                "enum": [
                    "market_analysis", "regulatory", "technology", "adoption",
                    "security", "defi", "nft", "mining", "trading", "other"
                ],
                "default": "other"
            },
            "market_impact": {
                "type": "string",
                "enum": ["high", "medium", "low", "none"],
                "default": "none"
            },
            "key_entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": [
                                "cryptocurrency", "person", "company", "exchange",
                                "project", "protocol", "regulator", "other"
                            ]
                        },
                        "relevance": {"type": "number"}
                    },
                    "required": ["name", "type"]
                }
            },
            "persona_relevance": {
                "type": "object",
                "properties": {
                    "meme_snipers": {"type": "number", "default": 0.0},
                    "gem_hunters": {"type": "number", "default": 0.0},
                    "legacy_investors": {"type": "number", "default": 0.0}
                }
            },
            "urgency_score": {"type": "number", "default": 0.0},
            "price_mentions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "token": {"type": "string"},
                        "price": {"type": "string"},
                        "change": {"type": "string"}
                    },
                    "required": ["token", "price"]
                }
            }
        }
    }

    def __init__(self):
        """Initialize the schema registry with default schemas."""
        self._schemas = {
            ContentType.NEWS: self._merge_schemas(self.BASE_SCHEMA, self.NEWS_SCHEMA),
            ContentType.SOCIAL_MEDIA: self._merge_schemas(self.BASE_SCHEMA, self.SOCIAL_MEDIA_SCHEMA),
            ContentType.CRYPTO: self._merge_schemas(self.BASE_SCHEMA, self.CRYPTO_SCHEMA),
            ContentType.GENERAL: self.BASE_SCHEMA
        }
        # Default schemas for other content types
        self._schemas[ContentType.BLOG] = self._schemas[ContentType.NEWS]
        self._schemas[ContentType.FORUM] = self._schemas[ContentType.SOCIAL_MEDIA]
        self._schemas[ContentType.RESEARCH] = self._schemas[ContentType.NEWS]

    def _merge_schemas(self, base_schema: Dict[str, Any], specific_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Merge a base schema with a content-specific schema.
        
        Args:
            base_schema: The base schema to extend
            specific_schema: The content-specific schema to merge
            
        Returns:
            The merged schema
        """
        merged = base_schema.copy()
        
        # Merge required fields
        if "required" in base_schema and "required" in specific_schema:
            merged["required"] = list(set(base_schema["required"]) | set(specific_schema["required"]))
        elif "required" in specific_schema:
            merged["required"] = specific_schema["required"]
        
        # Merge properties
        if "properties" in base_schema and "properties" in specific_schema:
            merged["properties"] = {**base_schema["properties"], **specific_schema["properties"]}
        elif "properties" in specific_schema:
            merged["properties"] = specific_schema["properties"]
        
        return merged

    def get_schema(self, content_type: Union[ContentType, str]) -> Dict[str, Any]:
        """Get the schema for a specific content type.
        
        Args:
            content_type: The content type to get the schema for
            
        Returns:
            The schema for the specified content type
        """
        if isinstance(content_type, str):
            try:
                content_type = ContentType(content_type)
            except ValueError:
                logger.warning(f"Unknown content type: {content_type}, using general schema")
                content_type = ContentType.GENERAL
        
        return self._schemas.get(content_type, self._schemas[ContentType.GENERAL])

    def register_schema(self, content_type: Union[ContentType, str], schema: Dict[str, Any]) -> None:
        """Register a new schema for a content type.
        
        Args:
            content_type: The content type to register the schema for
            schema: The schema to register
        """
        if isinstance(content_type, str):
            try:
                content_type = ContentType(content_type)
            except ValueError:
                logger.warning(f"Creating new content type: {content_type}")
                # Dynamically add new content type
                ContentType._member_map_[content_type.upper()] = content_type
                content_type = ContentType(content_type)
        
        self._schemas[content_type] = self._merge_schemas(self.BASE_SCHEMA, schema)

    def generate_dynamic_schema(self, content: str, url: Optional[str] = None) -> ContentType:
        """Generate a dynamic schema based on content analysis.
        
        Args:
            content: The content to analyze
            url: Optional URL to help determine content type
            
        Returns:
            The detected content type
        """
        # Simple heuristic-based content type detection
        content_lower = content.lower()
        
        # Check for crypto-related keywords
        crypto_keywords = [
            "bitcoin", "ethereum", "crypto", "blockchain", "token", "coin", "mining",
            "wallet", "exchange", "defi", "nft", "altcoin", "btc", "eth"
        ]
        if any(keyword in content_lower for keyword in crypto_keywords):
            return ContentType.CRYPTO
        
        # Check for social media indicators
        social_media_indicators = [
            "tweet", "posted", "shared", "liked", "commented", "followers",
            "@username", "hashtag", "#", "retweet", "thread"
        ]
        if any(indicator in content_lower for indicator in social_media_indicators):
            return ContentType.SOCIAL_MEDIA
        
        # Check URL for hints
        if url:
            url_lower = url.lower()
            if any(sm in url_lower for sm in ["twitter", "facebook", "instagram", "linkedin", "reddit"]):
                return ContentType.SOCIAL_MEDIA
            if any(blog in url_lower for blog in ["blog", "medium", "substack"]):
                return ContentType.BLOG
            if any(forum in url_lower for forum in ["forum", "community", "discuss"]):
                return ContentType.FORUM
            if any(research in url_lower for research in ["research", "paper", "study", "analysis"]):
                return ContentType.RESEARCH
        
        # Default to news if nothing else matches
        return ContentType.NEWS


class SchemaValidator:
    """Validator for extraction results against JSON schemas."""

    def __init__(self, schema_registry: Optional[SchemaRegistry] = None):
        """Initialize the schema validator.
        
        Args:
            schema_registry: Optional schema registry to use
        """
        self.schema_registry = schema_registry or SchemaRegistry()

    def validate(self, extraction: Dict[str, Any], content_type: Optional[Union[ContentType, str]] = None,
                 schema: Optional[Dict[str, Any]] = None, fill_defaults: bool = True) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate an extraction result against a schema.
        
        Args:
            extraction: The extraction result to validate
            content_type: Optional content type to determine the schema
            schema: Optional explicit schema to validate against
            fill_defaults: Whether to fill in default values
            
        Returns:
            Tuple of (is_valid, validation_errors)
        """
        # Determine which schema to use
        if schema is None:
            if content_type is None:
                content_type = ContentType.GENERAL
            schema = self.schema_registry.get_schema(content_type)
        
        # Collect validation errors
        errors = []
        
        # Use the appropriate validator
        if fill_defaults:
            validator = DefaultValidatingDraft7Validator(schema)
        else:
            validator = Draft7Validator(schema)
        
        # Validate and collect errors
        for error in validator.iter_errors(extraction):
            errors.append({
                "path": "." + ".".join(str(p) for p in error.path) if error.path else "root",
                "message": error.message,
                "schema_path": "#" + "/".join(str(p) for p in error.schema_path)
            })
        
        return len(errors) == 0, errors

    def validate_and_enhance(self, extraction: Dict[str, Any], content: str, url: Optional[str] = None,
                            content_type: Optional[Union[ContentType, str]] = None) -> Dict[str, Any]:
        """Validate and enhance an extraction result.
        
        Args:
            extraction: The extraction result to validate and enhance
            content: The original content
            url: Optional URL of the content
            content_type: Optional content type
            
        Returns:
            The validated and enhanced extraction result
            
        Raises:
            SchemaValidationError: If validation fails with critical errors
        """
        # Determine content type if not provided
        if content_type is None:
            content_type = self.schema_registry.generate_dynamic_schema(content, url)
            logger.info(f"Detected content type: {content_type.value}")
        
        # Get the appropriate schema
        schema = self.schema_registry.get_schema(content_type)
        
        # Validate with default filling
        is_valid, errors = self.validate(extraction, schema=schema, fill_defaults=True)
        
        # Filter critical errors (missing required fields that couldn't be filled)
        critical_errors = [e for e in errors if "required property" in e["message"]]
        
        if critical_errors:
            error_msg = f"Validation failed with {len(critical_errors)} critical errors"
            logger.error(error_msg)
            for err in critical_errors:
                logger.error(f"  {err['path']}: {err['message']}")
            raise SchemaValidationError(error_msg, critical_errors)
        
        # Log non-critical errors
        if errors and not critical_errors:
            logger.warning(f"Validation had {len(errors)} non-critical errors that were auto-fixed")
            for err in errors:
                logger.warning(f"  {err['path']}: {err['message']}")
        
        # Add content type to metadata
        if "_metadata" not in extraction:
            extraction["_metadata"] = {}
        extraction["_metadata"]["content_type"] = content_type.value if isinstance(content_type, ContentType) else content_type
        
        return extraction


# Global instances for easy access
default_schema_registry = SchemaRegistry()
default_validator = SchemaValidator(default_schema_registry)


def validate_extraction(extraction: Dict[str, Any], content_type: Optional[Union[ContentType, str]] = None,
                       schema: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[Dict[str, Any]]]:
    """Convenience function to validate an extraction result.
    
    Args:
        extraction: The extraction result to validate
        content_type: Optional content type to determine the schema
        schema: Optional explicit schema to validate against
        
    Returns:
        Tuple of (is_valid, validation_errors)
    """
    return default_validator.validate(extraction, content_type, schema)


def validate_and_enhance_extraction(extraction: Dict[str, Any], content: str, url: Optional[str] = None,
                                  content_type: Optional[Union[ContentType, str]] = None) -> Dict[str, Any]:
    """Convenience function to validate and enhance an extraction result.
    
    Args:
        extraction: The extraction result to validate and enhance
        content: The original content
        url: Optional URL of the content
        content_type: Optional content type
        
    Returns:
        The validated and enhanced extraction result
        
    Raises:
        SchemaValidationError: If validation fails with critical errors
    """
    return default_validator.validate_and_enhance(extraction, content, url, content_type)