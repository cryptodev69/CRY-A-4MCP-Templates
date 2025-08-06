#!/usr/bin/env python3
"""
URL-to-Extractor Mapping System

This module provides a simplified approach to map URLs to appropriate extractors
based on domain, path patterns, or exact URL matches. It allows for flexible
configuration where a single URL can be associated with multiple extractors
for different target groups.
"""

import re
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class ExtractorConfig:
    """Configuration for an extractor to be used with a URL mapping."""
    
    extractor_id: str
    """Identifier for the extractor to be used."""
    
    target_group: str
    """The target group this extractor is responsible for (e.g., 'price', 'description')."""
    
    params: Dict[str, Any] = field(default_factory=dict)
    """Optional parameters to be passed to the extractor."""


@dataclass
class URLExtractorMapping:
    """Maps a URL pattern to a set of extractors."""
    
    url_pattern: str
    """The pattern to match against URLs."""
    
    pattern_type: str
    """Type of pattern matching: 'domain', 'path', or 'exact'."""
    
    extractors: List[ExtractorConfig]
    """List of extractors to apply when this mapping matches."""
    
    priority: int = 0
    """Priority of this mapping (higher values take precedence)."""
    
    def matches(self, url: str) -> bool:
        """Check if the given URL matches this mapping's pattern.
        
        Args:
            url: The URL to check against this mapping's pattern.
            
        Returns:
            True if the URL matches, False otherwise.
        """
        if self.pattern_type == "domain":
            # Extract domain from URL and check if it contains or matches the pattern
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            if domain_match:
                domain = domain_match.group(1)
                return self.url_pattern in domain
            return False
        
        elif self.pattern_type == "path":
            # Check if the URL path contains the pattern
            return self.url_pattern in url
        
        elif self.pattern_type == "exact":
            # Check for exact URL match
            return url == self.url_pattern
        
        # Unknown pattern type
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this mapping to a dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'URLExtractorMapping':
        """Create a mapping from a dictionary.
        
        Args:
            data: Dictionary containing mapping configuration.
            
        Returns:
            A new URLExtractorMapping instance.
        """
        extractors = [ExtractorConfig(**e) for e in data.pop('extractors', [])]
        return cls(extractors=extractors, **data)


class URLMappingManager:
    """Manages URL-to-extractor mappings and provides lookup functionality."""
    
    def __init__(self):
        """Initialize a new URL mapping manager."""
        self.mappings: List[URLExtractorMapping] = []
    
    def add_mapping(self, mapping: URLExtractorMapping) -> None:
        """Add a new URL-to-extractor mapping.
        
        Args:
            mapping: The mapping to add.
        """
        self.mappings.append(mapping)
        # Sort mappings by priority (highest first)
        self.mappings.sort(key=lambda m: m.priority, reverse=True)
    
    def remove_mapping(self, mapping: URLExtractorMapping) -> None:
        """Remove a URL-to-extractor mapping.
        
        Args:
            mapping: The mapping to remove.
        """
        if mapping in self.mappings:
            self.mappings.remove(mapping)
    
    def get_extractors_for_url(self, url: str) -> List[ExtractorConfig]:
        """Get all extractors that should be applied to the given URL.
        
        Args:
            url: The URL to find extractors for.
            
        Returns:
            List of extractor configurations that match the URL.
        """
        matching_extractors = []
        
        for mapping in self.mappings:
            if mapping.matches(url):
                matching_extractors.extend(mapping.extractors)
        
        return matching_extractors
    
    def save_config(self, file_path: str) -> None:
        """Save the current configuration to a JSON file.
        
        Args:
            file_path: Path to save the configuration file.
        """
        config = {
            "mappings": [m.to_dict() for m in self.mappings]
        }
        
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self, file_path: str) -> None:
        """Load configuration from a JSON file.
        
        Args:
            file_path: Path to the configuration file.
        """
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        self.mappings = [URLExtractorMapping.from_dict(m) for m in config.get("mappings", [])]
        # Sort mappings by priority
        self.mappings.sort(key=lambda m: m.priority, reverse=True)


async def extract_from_url(url: str, mapping_manager: URLMappingManager, extractor_factory: Any) -> Dict[str, Any]:
    """Extract content from a URL using the appropriate extractors.
    
    Args:
        url: The URL to extract content from.
        mapping_manager: The URL mapping manager to use for finding extractors.
        extractor_factory: Factory for creating extractors.
        
    Returns:
        Dictionary of extraction results organized by target group.
    """
    # Get all applicable extractors for this URL
    extractors = mapping_manager.get_extractors_for_url(url)
    
    if not extractors:
        # No extractors found for this URL
        return {}
    
    # Organize results by target group
    results = {}
    
    for extractor_config in extractors:
        # Create the extractor
        extractor = extractor_factory.create(extractor_config.extractor_id)
        
        if not extractor:
            continue
        
        # Extract content using the extractor
        extraction_result = await extractor.extract(url, **extractor_config.params)
        
        # Store result under the target group
        target_group = extractor_config.target_group
        results[target_group] = extraction_result
    
    return results