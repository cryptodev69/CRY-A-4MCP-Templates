#!/usr/bin/env python3
"""
Test suite for the extraction process in the UI.

This module provides comprehensive tests for the entire extraction process,
focusing on the integration between UI components, strategy factory, and sync wrapper.
"""

import os
import sys
import json
import time
import unittest
from unittest.mock import patch, MagicMock, AsyncMock, call, PropertyMock
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the necessary modules
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui import NewStrategyUI
from src.cry_a_4mcp.crawl4ai.extraction_strategies.base import ExtractionError, APIConnectionError, APIResponseError
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper
from src.cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory


class MockStrategy:
    """Mock strategy class for testing."""
    
    SCHEMA = {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
            'summary': {'type': 'string'}
        },
        'required': ['title', 'summary']
    }
    
    INSTRUCTION = "Extract the title and summary from the content."
    
    def __init__(self, provider=None, api_token=None, model=None, **kwargs):
        self.provider = provider
        self.api_token = api_token
        self.model = model
        self.kwargs = kwargs
    
    async def extract(self, url=None, content=None):
        """Mock extract method."""
        if not self.api_token and self.provider != "ollama":
            raise APIConnectionError("No API token provided")
        
        if not content:
            raise ExtractionError("No content provided")
        
        if "error" in content.lower():
            raise ExtractionError("Content contains error keyword")
        
        if "timeout" in content.lower():
            raise APIResponseError("API request timed out")
        
        return {
            'title': f"Title from {self.provider} {self.model}",
            'summary': f"Summary of: {content[:50]}..."
        }


class TestExtractionProcess(unittest.TestCase):
    """Test case for the extraction process in the UI."""

    def setUp(self):
        """Set up the test case with all necessary mocks."""
        # Mock Streamlit components
        self.st_patcher = patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.st')
        self.mock_st = self.st_patcher.start()
        
        # Mock session state as a dictionary with the required keys
        self.mock_st.session_state = {
            'selected_strategy': None,
            'edit_mode': False,
            'delete_confirmation': False,
            'view_code': False,
            'test_mode': False,
            'create_mode': False,
            'filter_category': 'All',
            'search_query': '',
            'operation_result': None,
            'operation_error': None,
            'api_tokens': {},
            'openrouter_models': {}
        }
        
        # Mock UI components
        self.mock_progress = MagicMock()
        self.mock_st.progress.return_value = self.mock_progress
        
        self.mock_status = MagicMock()
        self.mock_st.empty.return_value = self.mock_status
        
        # Mock the NewStrategyManager
        self.manager_patcher = patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.NewStrategyManager')
        self.mock_manager_class = self.manager_patcher.start()
        self.mock_manager = self.mock_manager_class.return_value
        
        # Create a UI instance
        self.ui = NewStrategyUI()
        
        # Replace the manager with our mock
        self.ui.manager = self.mock_manager
        
        # Sample strategy for testing
        self.sample_strategy = {
            'name': 'TestStrategy',
            'description': 'A test strategy',
            'category': 'test',
            'default_provider': 'openai',
            'file_path': '/path/to/test_strategy.py',
            'schema': MockStrategy.SCHEMA,
            'instruction': MockStrategy.INSTRUCTION
        }
    
    def tearDown(self):
        """Clean up after the test case."""
        self.st_patcher.stop()
        self.manager_patcher.stop()
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_load_strategy_module_success(self, mock_importlib, mock_inspect):
        """Test successfully loading a strategy module."""
        # Mock the imported module
        mock_module = MagicMock()
        mock_importlib.import_module.return_value = mock_module
        
        # Mock inspect to find our strategy class
        mock_inspect.isclass.return_value = True
        mock_inspect.getmembers.return_value = [("TestStrategy", MockStrategy)]
        
        # Mock the _load_strategy_module method to return the mock module
        with patch.object(self.ui, '_load_strategy_module', return_value=mock_module) as mock_load:
            # Call the method
            result = self.ui._load_strategy_module(self.sample_strategy['file_path'])
            
            # Assertions
            self.assertEqual(result, mock_module)
            # We don't assert on importlib.import_module since we've mocked the entire method
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_load_strategy_module_import_error(self, mock_importlib, mock_inspect):
        """Test handling import errors when loading a strategy module."""
        # Make importlib raise an ImportError
        mock_importlib.import_module.side_effect = ImportError("Module not found")
        
        # Create a side effect function that raises ImportError
        def mock_load_side_effect(file_path):
            raise ImportError("Module not found")
        
        # Mock the _load_strategy_module method to raise ImportError
        with patch.object(self.ui, '_load_strategy_module', side_effect=mock_load_side_effect) as mock_load:
            # Call the method and assert it raises ImportError
            with self.assertRaises(ImportError):
                self.ui._load_strategy_module(self.sample_strategy['file_path'])
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_find_strategy_class_success(self, mock_importlib, mock_inspect):
        """Test successfully finding a strategy class in a module."""
        # Mock the imported module
        mock_module = MagicMock()
        
        # Mock inspect to find our strategy class
        mock_inspect.isclass.return_value = True
        mock_inspect.getmembers.return_value = [("TestStrategy", MockStrategy)]
        
        # Mock the _load_strategy_module method to return the mock module
        with patch.object(self.ui, '_load_strategy_module', return_value=mock_module) as mock_load:
            # Mock the _find_strategy_class method to return MockStrategy
            with patch.object(self.ui, '_find_strategy_class', return_value=MockStrategy) as mock_find:
                # Call the methods
                module = self.ui._load_strategy_module(self.sample_strategy['file_path'])
                strategy_class = self.ui._find_strategy_class(module, self.sample_strategy['name'])
                
                # Assertions
                self.assertEqual(strategy_class, MockStrategy)
                mock_find.assert_called_once_with(module, self.sample_strategy['name'])
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_find_strategy_class_not_found(self, mock_importlib, mock_inspect):
        """Test handling when a strategy class is not found in a module."""
        # Mock the imported module
        mock_module = MagicMock()
        mock_importlib.import_module.return_value = mock_module
        
        # Mock inspect to not find our strategy class
        mock_inspect.isclass.return_value = True
        mock_inspect.getmembers.return_value = [("OtherClass", MagicMock())]
        
        # Call the methods
        module = self.ui._load_strategy_module(self.sample_strategy['file_path'])
        
        # Assertions
        with self.assertRaises(ValueError):
            self.ui._find_strategy_class(module, self.sample_strategy['name'])
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper.SyncExtractionStrategyWrapper.extract')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.StrategyFactory')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_run_extraction_integration(self, mock_importlib, mock_inspect, mock_factory, mock_extract):
        """Test the integration of the extraction process."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock content and API key
        test_content = "Test content for extraction"
        test_api_key = "test-api-key"
        self.mock_st.text_area.return_value = test_content
        self.mock_st.text_input.return_value = test_api_key
        
        # Set provider and model
        test_provider = "openai"
        test_model = "gpt-4"
        self.mock_st.selectbox.side_effect = [test_provider, test_model]
        
        # Mock the imported module
        mock_module = MagicMock()
        mock_importlib.import_module.return_value = mock_module
        
        # Mock inspect to find our strategy class
        mock_inspect.isclass.return_value = True
        mock_inspect.getmembers.return_value = [("TestStrategy", MockStrategy)]
        
        # Mock the factory
        mock_strategy = MockStrategy(provider=test_provider, api_token=test_api_key, model=test_model)
        mock_factory.return_value.create_strategy.return_value = mock_strategy
        
        # Mock the extraction result
        expected_result = {
            'title': f"Title from {test_provider} {test_model}",
            'summary': f"Summary of: {test_content[:50]}..."
        }
        mock_extract.return_value = expected_result
        
        # Set up time.time for execution time measurement
        with patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.time') as mock_time:
            mock_time.time.side_effect = [0, 2.5]  # Start time, end time
            
            # Call the method
            self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify factory call
        mock_factory.return_value.create_strategy.assert_called_with(
            MockStrategy,
            provider=test_provider,
            model=test_model,
            api_token=test_api_key
        )
        
        # Verify extraction call
        mock_extract.assert_called_with(url="dummy_url", content=test_content)
        
        # Verify result display
        self.mock_st.json.assert_called_with(expected_result)
        self.mock_st.download_button.assert_called()
        
        # Verify execution time display
        self.mock_status.text.assert_any_call("Extraction completed in 2.50 seconds.")
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper.SyncExtractionStrategyWrapper.extract')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.StrategyFactory')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_run_extraction_api_error(self, mock_importlib, mock_inspect, mock_factory, mock_extract):
        """Test handling API errors during extraction."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock content and API key
        self.mock_st.text_area.return_value = "Test content"
        self.mock_st.text_input.return_value = "test-api-key"
        
        # Set provider and model
        self.mock_st.selectbox.side_effect = ["openai", "gpt-4"]
        
        # Mock the imported module
        mock_module = MagicMock()
        mock_importlib.import_module.return_value = mock_module
        
        # Mock inspect to find our strategy class
        mock_inspect.isclass.return_value = True
        mock_inspect.getmembers.return_value = [("TestStrategy", MockStrategy)]
        
        # Mock the factory
        mock_strategy = MockStrategy(provider="openai", api_token="test-api-key", model="gpt-4")
        mock_factory.return_value.create_strategy.return_value = mock_strategy
        
        # Make the extraction raise an API error
        error_message = "API connection failed"
        mock_extract.side_effect = APIConnectionError(error_message)
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify error display
        self.mock_st.error.assert_called_with(error_message)
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper.SyncExtractionStrategyWrapper.extract')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.StrategyFactory')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_run_extraction_response_error(self, mock_importlib, mock_inspect, mock_factory, mock_extract):
        """Test handling API response errors during extraction."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock content and API key
        self.mock_st.text_area.return_value = "Test content with timeout"
        self.mock_st.text_input.return_value = "test-api-key"
        
        # Set provider and model
        self.mock_st.selectbox.side_effect = ["openai", "gpt-4"]
        
        # Mock the imported module
        mock_module = MagicMock()
        mock_importlib.import_module.return_value = mock_module
        
        # Mock inspect to find our strategy class
        mock_inspect.isclass.return_value = True
        mock_inspect.getmembers.return_value = [("TestStrategy", MockStrategy)]
        
        # Mock the factory
        mock_strategy = MockStrategy(provider="openai", api_token="test-api-key", model="gpt-4")
        mock_factory.return_value.create_strategy.return_value = mock_strategy
        
        # Make the extraction raise an API response error
        error_message = "API request timed out"
        mock_extract.side_effect = APIResponseError(error_message)
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify error display
        self.mock_st.error.assert_called_with(error_message)
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper.SyncExtractionStrategyWrapper.extract')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.StrategyFactory')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_run_extraction_unexpected_error(self, mock_importlib, mock_inspect, mock_factory, mock_extract):
        """Test handling unexpected errors during extraction."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock content and API key
        self.mock_st.text_area.return_value = "Test content"
        self.mock_st.text_input.return_value = "test-api-key"
        
        # Set provider and model
        self.mock_st.selectbox.side_effect = ["openai", "gpt-4"]
        
        # Mock the imported module
        mock_module = MagicMock()
        mock_importlib.import_module.return_value = mock_module
        
        # Mock inspect to find our strategy class
        mock_inspect.isclass.return_value = True
        mock_inspect.getmembers.return_value = [("TestStrategy", MockStrategy)]
        
        # Mock the factory
        mock_factory.return_value.create_strategy.side_effect = Exception("Unexpected error")
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify error display
        self.mock_st.error.assert_called_with("Error: Unexpected error")


if __name__ == '__main__':
    unittest.main()