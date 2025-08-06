#!/usr/bin/env python3
"""
Tests for the synchronous extraction strategy wrapper.
"""

import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.cry_a_4mcp.crawl4ai.extraction_strategies.base import ExtractionStrategy
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper
from src.cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory


class MockExtractionStrategy(ExtractionStrategy):
    """Mock extraction strategy for testing."""
    
    def __init__(self):
        """Initialize the mock strategy."""
        self.extract = AsyncMock()
        self.validate_provider_connection = AsyncMock()


class TestSyncWrapper(unittest.TestCase):
    """Test cases for the synchronous extraction strategy wrapper."""
    
    def setUp(self):
        """Set up the test case."""
        self.mock_strategy = MockExtractionStrategy()
        self.sync_wrapper = SyncExtractionStrategyWrapper(self.mock_strategy)
        
        # Set up mock return values
        self.mock_strategy.extract.return_value = {"result": "test_result"}
        self.mock_strategy.validate_provider_connection.return_value = {"status": "connected"}
    
    def test_extract(self):
        """Test the synchronous extract method."""
        # Call the synchronous extract method
        result = self.sync_wrapper.extract("https://example.com", "test content")
        
        # Verify the async method was called with the correct arguments
        self.mock_strategy.extract.assert_called_once_with("https://example.com", "test content")
        
        # Verify the result is correct
        self.assertEqual(result, {"result": "test_result"})
    
    def test_extract_with_kwargs(self):
        """Test the synchronous extract method with additional keyword arguments."""
        # Call the synchronous extract method with additional kwargs
        result = self.sync_wrapper.extract(
            "https://example.com", 
            "test content", 
            extra_param="test"
        )
        
        # Verify the async method was called with the correct arguments
        self.mock_strategy.extract.assert_called_once_with(
            "https://example.com", 
            "test content", 
            extra_param="test"
        )
        
        # Verify the result is correct
        self.assertEqual(result, {"result": "test_result"})
    
    def test_validate_provider_connection(self):
        """Test the synchronous validate_provider_connection method."""
        # Call the synchronous validate_provider_connection method
        result = self.sync_wrapper.validate_provider_connection()
        
        # Verify the async method was called
        self.mock_strategy.validate_provider_connection.assert_called_once()
        
        # Verify the result is correct
        self.assertEqual(result, {"status": "connected"})


class TestFactorySyncMethods(unittest.TestCase):
    """Test cases for the factory's synchronous methods."""
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.factory.StrategyFactory.create')
    def test_create_sync(self, mock_create):
        """Test the create_sync method."""
        # Set up the mock
        mock_strategy = MagicMock()
        mock_create.return_value = mock_strategy
        
        # Call the create_sync method
        result = StrategyFactory.create_sync("TestStrategy", {"param": "value"})
        
        # Verify the create method was called with the correct arguments
        mock_create.assert_called_once_with("TestStrategy", {"param": "value"})
        
        # Verify the result is a SyncExtractionStrategyWrapper
        self.assertIsInstance(result, SyncExtractionStrategyWrapper)
        self.assertEqual(result.strategy, mock_strategy)
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.factory.StrategyFactory.create_from_config')
    def test_create_from_config_sync(self, mock_create_from_config):
        """Test the create_from_config_sync method."""
        # Set up the mock
        mock_strategy = MagicMock()
        mock_create_from_config.return_value = mock_strategy
        
        # Call the create_from_config_sync method
        config = {"strategy": "TestStrategy", "config": {"param": "value"}}
        result = StrategyFactory.create_from_config_sync(config)
        
        # Verify the create_from_config method was called with the correct arguments
        mock_create_from_config.assert_called_once_with(config)
        
        # Verify the result is a SyncExtractionStrategyWrapper
        self.assertIsInstance(result, SyncExtractionStrategyWrapper)
        self.assertEqual(result.strategy, mock_strategy)
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.factory.StrategyFactory.create_from_json')
    def test_create_from_json_sync(self, mock_create_from_json):
        """Test the create_from_json_sync method."""
        # Set up the mock
        mock_strategy = MagicMock()
        mock_create_from_json.return_value = mock_strategy
        
        # Call the create_from_json_sync method
        json_config = '{"strategy": "TestStrategy", "config": {"param": "value"}}'
        result = StrategyFactory.create_from_json_sync(json_config)
        
        # Verify the create_from_json method was called with the correct arguments
        mock_create_from_json.assert_called_once_with(json_config)
        
        # Verify the result is a SyncExtractionStrategyWrapper
        self.assertIsInstance(result, SyncExtractionStrategyWrapper)
        self.assertEqual(result.strategy, mock_strategy)
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.factory.StrategyFactory.create_composite')
    def test_create_composite_sync(self, mock_create_composite):
        """Test the create_composite_sync method."""
        # Set up the mock
        mock_strategy = MagicMock()
        mock_create_composite.return_value = mock_strategy
        
        # Call the create_composite_sync method
        strategies = [
            {"strategy": "TestStrategy1", "config": {"param": "value1"}},
            {"strategy": "TestStrategy2", "config": {"param": "value2"}}
        ]
        result = StrategyFactory.create_composite_sync(strategies)
        
        # Verify the create_composite method was called with the correct arguments
        mock_create_composite.assert_called_once_with(strategies)
        
        # Verify the result is a SyncExtractionStrategyWrapper
        self.assertIsInstance(result, SyncExtractionStrategyWrapper)
        self.assertEqual(result.strategy, mock_strategy)


if __name__ == "__main__":
    unittest.main()