#!/usr/bin/env python3
"""
Tests for URL-to-Extractor mapping functionality.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from cry_a_4mcp.crawl4ai.extraction_strategies.custom_strategies.url_mapping import (
    URLExtractorMapping,
    ExtractorConfig,
    URLMappingManager
)


class TestURLExtractorMapping:
    """Tests for the URLExtractorMapping class."""
    
    def test_domain_pattern_matching(self):
        """Test that domain pattern matching works correctly."""
        # Create a mapping with domain pattern
        extractors = [
            ExtractorConfig(extractor_id="TestExtractor", target_group="test")
        ]
        mapping = URLExtractorMapping(
            url_pattern="example.com",
            pattern_type="domain",
            extractors=extractors
        )
        
        # Test matching
        assert mapping.matches("https://example.com")
        assert mapping.matches("http://example.com/path")
        assert mapping.matches("https://sub.example.com")
        assert not mapping.matches("https://example.org")
    
    def test_path_pattern_matching(self):
        """Test that path pattern matching works correctly."""
        # Create a mapping with path pattern
        extractors = [
            ExtractorConfig(extractor_id="TestExtractor", target_group="test")
        ]
        mapping = URLExtractorMapping(
            url_pattern="/product/",
            pattern_type="path",
            extractors=extractors
        )
        
        # Test matching
        assert mapping.matches("https://example.com/product/123")
        assert mapping.matches("https://example.org/product/abc")
        assert not mapping.matches("https://example.com/category/123")
    
    def test_exact_pattern_matching(self):
        """Test that exact pattern matching works correctly."""
        # Create a mapping with exact pattern
        extractors = [
            ExtractorConfig(extractor_id="TestExtractor", target_group="test")
        ]
        mapping = URLExtractorMapping(
            url_pattern="https://example.com/specific-page.html",
            pattern_type="exact",
            extractors=extractors
        )
        
        # Test matching
        assert mapping.matches("https://example.com/specific-page.html")
        assert not mapping.matches("https://example.com/specific-page.html?param=value")
        assert not mapping.matches("https://example.com/other-page.html")


class TestURLMappingManager:
    """Tests for the URLMappingManager class."""
    
    @pytest.fixture
    def mapping_manager(self):
        """Create a URLMappingManager with test mappings."""
        manager = URLMappingManager()
        
        # Add domain mapping
        domain_extractors = [
            ExtractorConfig(extractor_id="DomainExtractor", target_group="domain")
        ]
        manager.add_mapping(URLExtractorMapping(
            url_pattern="example.com",
            pattern_type="domain",
            extractors=domain_extractors
        ))
        
        # Add path mapping
        path_extractors = [
            ExtractorConfig(extractor_id="PathExtractor", target_group="path")
        ]
        manager.add_mapping(URLExtractorMapping(
            url_pattern="/product/",
            pattern_type="path",
            extractors=path_extractors
        ))
        
        # Add exact mapping
        exact_extractors = [
            ExtractorConfig(extractor_id="ExactExtractor", target_group="exact")
        ]
        manager.add_mapping(URLExtractorMapping(
            url_pattern="https://example.com/specific-page.html",
            pattern_type="exact",
            extractors=exact_extractors
        ))
        
        return manager
    
    def test_get_extractors_for_url(self, mapping_manager):
        """Test that get_extractors_for_url returns the correct extractors."""
        # Test domain matching
        extractors = mapping_manager.get_extractors_for_url("https://example.com")
        assert len(extractors) == 1
        assert extractors[0].extractor_id == "DomainExtractor"
        assert extractors[0].target_group == "domain"
        
        # Test path matching
        extractors = mapping_manager.get_extractors_for_url("https://other.com/product/123")
        assert len(extractors) == 1
        assert extractors[0].extractor_id == "PathExtractor"
        assert extractors[0].target_group == "path"
        
        # Test exact matching
        extractors = mapping_manager.get_extractors_for_url("https://example.com/specific-page.html")
        assert len(extractors) == 2  # Should match both domain and exact
        extractor_ids = [e.extractor_id for e in extractors]
        assert "DomainExtractor" in extractor_ids
        assert "ExactExtractor" in extractor_ids
        
        # Test no matching
        extractors = mapping_manager.get_extractors_for_url("https://nonmatching.com")
        assert len(extractors) == 0
    
    def test_add_and_remove_mapping(self):
        """Test adding and removing mappings."""
        manager = URLMappingManager()
        
        # Add a mapping
        extractors = [
            ExtractorConfig(extractor_id="TestExtractor", target_group="test")
        ]
        mapping = URLExtractorMapping(
            url_pattern="example.com",
            pattern_type="domain",
            extractors=extractors
        )
        manager.add_mapping(mapping)
        
        # Verify it was added
        assert len(manager.mappings) == 1
        assert manager.get_extractors_for_url("https://example.com") == extractors
        
        # Remove the mapping
        manager.remove_mapping(mapping)
        
        # Verify it was removed
        assert len(manager.mappings) == 0
        assert len(manager.get_extractors_for_url("https://example.com")) == 0
    
    def test_save_and_load_config(self, tmp_path):
        """Test saving and loading configuration."""
        manager = URLMappingManager()
        
        # Add a mapping
        extractors = [
            ExtractorConfig(extractor_id="TestExtractor", target_group="test")
        ]
        mapping = URLExtractorMapping(
            url_pattern="example.com",
            pattern_type="domain",
            extractors=extractors
        )
        manager.add_mapping(mapping)
        
        # Save configuration
        config_path = tmp_path / "url_mappings.json"
        manager.save_config(str(config_path))
        
        # Create a new manager and load configuration
        new_manager = URLMappingManager()
        new_manager.load_config(str(config_path))
        
        # Verify configuration was loaded correctly
        assert len(new_manager.mappings) == 1
        loaded_extractors = new_manager.get_extractors_for_url("https://example.com")
        assert len(loaded_extractors) == 1
        assert loaded_extractors[0].extractor_id == "TestExtractor"
        assert loaded_extractors[0].target_group == "test"


if __name__ == "__main__":
    pytest.main(['-xvs', __file__])