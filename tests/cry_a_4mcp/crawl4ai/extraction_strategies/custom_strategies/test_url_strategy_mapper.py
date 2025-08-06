#!/usr/bin/env python3
"""
Tests for URL-to-Strategy mapping functionality.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from cry_a_4mcp.crawl4ai.extraction_strategies.custom_strategies.url_strategy_mapper import (
    StrategyMatcher,
    DomainMatcher,
    PatternMatcher,
    StrategyMapping,
    URLMappingStrategy
)


class TestStrategyMatchers:
    """Tests for the StrategyMatcher classes."""
    
    def test_domain_matcher_exact_match(self):
        """Test that DomainMatcher matches exact domains."""
        matcher = DomainMatcher("example.com", include_subdomains=False)
        assert matcher.matches("https://example.com")
        assert matcher.matches("http://example.com/path")
        assert not matcher.matches("https://sub.example.com")
        assert not matcher.matches("https://example.org")
    
    def test_domain_matcher_with_subdomains(self):
        """Test that DomainMatcher matches subdomains when configured."""
        matcher = DomainMatcher("example.com", include_subdomains=True)
        assert matcher.matches("https://example.com")
        assert matcher.matches("https://sub.example.com")
        assert matcher.matches("https://sub.sub.example.com")
        assert not matcher.matches("https://example.org")
    
    def test_pattern_matcher(self):
        """Test that PatternMatcher matches based on regex patterns."""
        matcher = PatternMatcher(r"/(product|item)/")
        assert matcher.matches("https://example.com/product/123")
        assert matcher.matches("https://example.org/item/abc")
        assert not matcher.matches("https://example.com/category/123")
        
        # Test case-insensitive matching
        matcher = PatternMatcher(r"bitcoin", case_sensitive=False)
        assert matcher.matches("https://example.com/Bitcoin-news")
        assert matcher.matches("https://example.com/bitcoin-price")
        
        # Test case-sensitive matching
        matcher = PatternMatcher(r"Bitcoin", case_sensitive=True)
        assert matcher.matches("https://example.com/Bitcoin-news")
        assert not matcher.matches("https://example.com/bitcoin-price")


class TestURLMappingStrategy:
    """Tests for the URLMappingStrategy class."""
    
    @pytest.fixture
    def mock_factory(self):
        """Create a mock StrategyFactory."""
        mock = MagicMock()
        mock.create.return_value = MagicMock()
        mock.create.return_value.extract = AsyncMock(return_value={"result": "test"})
        return mock
    
    @pytest.fixture
    def url_mapping_strategy(self, mock_factory):
        """Create a URLMappingStrategy with test mappings."""
        mappings = [
            {
                "matcher_type": "domain",
                "domain": "example.com",
                "include_subdomains": True,
                "strategy_name": "TestStrategy1",
                "priority": 100
            },
            {
                "matcher_type": "pattern",
                "pattern": r"/product/",
                "strategy_name": "TestStrategy2",
                "priority": 80
            },
            {
                "matcher_type": "domain",
                "domain": "lowpriority.com",
                "include_subdomains": False,
                "strategy_name": "TestStrategy3",
                "priority": 50
            }
        ]
        
        with patch("cry_a_4mcp.crawl4ai.extraction_strategies.custom_strategies.url_strategy_mapper.StrategyFactory",
                  return_value=mock_factory):
            strategy = URLMappingStrategy(
                mappings=mappings,
                fallback_strategy="FallbackStrategy"
            )
            return strategy
    
    @pytest.mark.asyncio
    async def test_can_handle(self, url_mapping_strategy):
        """Test that can_handle returns True for URLs that match a mapping."""
        assert await url_mapping_strategy.can_handle("https://example.com")
        assert await url_mapping_strategy.can_handle("https://sub.example.com")
        assert await url_mapping_strategy.can_handle("https://other.com/product/123")
        assert await url_mapping_strategy.can_handle("https://lowpriority.com")
        
        # Should return True even for non-matching URLs because of fallback strategy
        assert await url_mapping_strategy.can_handle("https://nonmatching.com")
    
    @pytest.mark.asyncio
    async def test_get_strategy_for_url(self, url_mapping_strategy, mock_factory):
        """Test that get_strategy_for_url returns the correct strategy."""
        # Should match the highest priority strategy (TestStrategy1)
        await url_mapping_strategy.get_strategy_for_url("https://example.com")
        mock_factory.create.assert_called_with("TestStrategy1")
        
        # Reset mock
        mock_factory.create.reset_mock()
        
        # Should match the pattern strategy (TestStrategy2)
        await url_mapping_strategy.get_strategy_for_url("https://other.com/product/123")
        mock_factory.create.assert_called_with("TestStrategy2")
        
        # Reset mock
        mock_factory.create.reset_mock()
        
        # Should use fallback strategy for non-matching URL
        await url_mapping_strategy.get_strategy_for_url("https://nonmatching.com")
        mock_factory.create.assert_called_with("FallbackStrategy")
    
    @pytest.mark.asyncio
    async def test_extract(self, url_mapping_strategy, mock_factory):
        """Test that extract delegates to the correct strategy."""
        # Extract with a URL that matches TestStrategy1
        result = await url_mapping_strategy.extract("test content", url="https://example.com")
        
        # Verify that the correct strategy was created
        mock_factory.create.assert_called_with("TestStrategy1")
        
        # Verify that extract was called on the strategy
        mock_factory.create.return_value.extract.assert_called_with("test content", url="https://example.com")
        
        # Verify that the result was returned
        assert result == {"result": "test"}
        
        # Reset mocks
        mock_factory.create.reset_mock()
        mock_factory.create.return_value.extract.reset_mock()
        
        # Extract with a URL that doesn't match any mapping
        result = await url_mapping_strategy.extract("test content", url="https://nonmatching.com")
        
        # Verify that the fallback strategy was created
        mock_factory.create.assert_called_with("FallbackStrategy")
        
        # Verify that extract was called on the fallback strategy
        mock_factory.create.return_value.extract.assert_called_with("test content", url="https://nonmatching.com")
        
        # Verify that the result was returned
        assert result == {"result": "test"}
    
    @pytest.mark.asyncio
    async def test_extract_without_url(self, url_mapping_strategy, mock_factory):
        """Test that extract uses fallback strategy when no URL is provided."""
        # Extract without a URL
        result = await url_mapping_strategy.extract("test content")
        
        # Verify that the fallback strategy was created
        mock_factory.create.assert_called_with("FallbackStrategy")
        
        # Verify that extract was called on the fallback strategy
        mock_factory.create.return_value.extract.assert_called_with("test content")
        
        # Verify that the result was returned
        assert result == {"result": "test"}
    
    @pytest.mark.asyncio
    async def test_priority_ordering(self, mock_factory):
        """Test that mappings are checked in priority order."""
        # Create mappings with overlapping matches but different priorities
        mappings = [
            {
                "matcher_type": "domain",
                "domain": "example.com",
                "include_subdomains": True,
                "strategy_name": "LowPriorityStrategy",
                "priority": 50
            },
            {
                "matcher_type": "domain",
                "domain": "sub.example.com",
                "include_subdomains": False,
                "strategy_name": "HighPriorityStrategy",
                "priority": 100
            }
        ]
        
        with patch("cry_a_4mcp.crawl4ai.extraction_strategies.custom_strategies.url_strategy_mapper.StrategyFactory",
                  return_value=mock_factory):
            strategy = URLMappingStrategy(
                mappings=mappings,
                fallback_strategy="FallbackStrategy"
            )
            
            # Should match HighPriorityStrategy even though both matchers would match
            await strategy.get_strategy_for_url("https://sub.example.com")
            mock_factory.create.assert_called_with("HighPriorityStrategy")


if __name__ == "__main__":
    pytest.main(['-xvs', __file__])