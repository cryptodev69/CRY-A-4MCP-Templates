"""
Data models for Crawl4AI integration.

This module defines the data structures used for cryptocurrency-specific
content extraction and processing.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class CryptoEntity(BaseModel):
    """
    Represents a cryptocurrency entity extracted from content.
    
    This includes tokens, exchanges, protocols, addresses, and other
    cryptocurrency-specific entities.
    """
    
    name: str = Field(..., description="Entity name")
    entity_type: str = Field(..., description="Type of entity (token, exchange, protocol, etc.)")
    symbol: Optional[str] = Field(None, description="Token symbol if applicable")
    address: Optional[str] = Field(None, description="Blockchain address if applicable")
    network: Optional[str] = Field(None, description="Blockchain network")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    context: str = Field(..., description="Context where entity was found")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    
    @validator("entity_type")
    def validate_entity_type(cls, v: str) -> str:
        """Validate entity type."""
        valid_types = {
            "token", "coin", "exchange", "protocol", "defi", "nft", "dao",
            "address", "wallet", "person", "organization", "event", "metric"
        }
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid entity type: {v}")
        return v.lower()
    
    @validator("symbol")
    def validate_symbol(cls, v: Optional[str]) -> Optional[str]:
        """Validate token symbol format."""
        if v is None:
            return v
        if not v.isalpha() or len(v) < 2 or len(v) > 10:
            raise ValueError(f"Invalid symbol format: {v}")
        return v.upper()


class CryptoTriple(BaseModel):
    """
    Represents a knowledge graph triple for cryptocurrency relationships.
    
    This follows the subject-predicate-object pattern for representing
    relationships between cryptocurrency entities.
    """
    
    subject: str = Field(..., description="Subject entity")
    predicate: str = Field(..., description="Relationship type")
    object: str = Field(..., description="Object entity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Relationship confidence")
    source: str = Field(..., description="Source of the relationship")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When relationship was extracted")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    
    @validator("predicate")
    def validate_predicate(cls, v: str) -> str:
        """Validate predicate format."""
        valid_predicates = {
            "is_token_of", "trades_on", "founded_by", "partnered_with",
            "competes_with", "built_on", "governed_by", "owns", "created",
            "supports", "integrates_with", "listed_on", "backed_by"
        }
        if v.lower() not in valid_predicates:
            # Allow custom predicates but log a warning
            pass
        return v.lower()


class CrawlMetadata(BaseModel):
    """
    Metadata about the crawling process and content quality.
    """
    
    url: str = Field(..., description="Source URL")
    title: Optional[str] = Field(None, description="Page title")
    content_type: str = Field(..., description="Type of content")
    crawl_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When content was crawled")
    content_length: int = Field(..., description="Length of extracted content")
    processing_time: float = Field(..., description="Processing time in seconds")
    success: bool = Field(..., description="Whether crawling was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Quality metrics
    text_quality_score: float = Field(..., ge=0.0, le=1.0, description="Text quality score")
    entity_density: float = Field(..., ge=0.0, description="Entities per 100 words")
    relationship_density: float = Field(..., ge=0.0, description="Relationships per 100 words")
    
    # Content characteristics
    language: str = Field(default="en", description="Content language")
    has_structured_data: bool = Field(default=False, description="Whether page has structured data")
    has_tables: bool = Field(default=False, description="Whether content has data tables")
    has_charts: bool = Field(default=False, description="Whether content has charts/graphs")


class CrawlResult(BaseModel):
    """
    Complete result of cryptocurrency website crawling.
    
    This includes both the raw markdown content and the extracted
    structured information (entities and triples).
    """
    
    # Raw content
    markdown: str = Field(..., description="Extracted markdown content")
    html: Optional[str] = Field(None, description="Raw HTML if requested")
    media: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Extracted media (images, charts, etc.)")
    screenshot: Optional[str] = Field(None, description="Base64-encoded screenshot of the page")
    
    # Structured extractions
    entities: List[CryptoEntity] = Field(default_factory=list, description="Extracted entities")
    triples: List[CryptoTriple] = Field(default_factory=list, description="Extracted relationships")
    
    # Metadata
    metadata: CrawlMetadata = Field(..., description="Crawling metadata")
    
    # Quality assessment
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall content quality")
    
    @property
    def entity_count(self) -> int:
        """Number of extracted entities."""
        return len(self.entities)
    
    @property
    def triple_count(self) -> int:
        """Number of extracted triples."""
        return len(self.triples)
    
    @property
    def is_high_quality(self) -> bool:
        """Whether content is considered high quality."""
        return self.quality_score >= 0.7
    
    def get_entities_by_type(self, entity_type: str) -> List[CryptoEntity]:
        """Get entities of a specific type."""
        return [e for e in self.entities if e.entity_type == entity_type.lower()]
    
    def get_triples_by_predicate(self, predicate: str) -> List[CryptoTriple]:
        """Get triples with a specific predicate."""
        return [t for t in self.triples if t.predicate == predicate.lower()]

