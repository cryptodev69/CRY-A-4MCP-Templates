#!/usr/bin/env python3
"""
Test suite for the UI extraction functionality.

This module provides tests for the UI extraction functionality in the new strategy UI,
specifically focusing on the 'Run Extraction' button and related components.
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the UI module
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui import NewStrategyUI
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper
from src.cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory


class TestUIExtraction(unittest.TestCase):
    """Test case for the UI extraction functionality."""

    def setUp(self):
        """Set up the test case."""
        # Mock the Streamlit components
        self.streamlit_mock = patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.st').start()
        
        # Mock session state as a dictionary with all required keys
        self.streamlit_mock.session_state = {
            'selected_strategy': None,
            'edit_mode': False,
            'delete_confirmation': False,
            'view_code': False,
            'test_mode': False,
            'create_mode': False,
            'filter_category': 'All',
            'search_query': ''
        }
        
        # Mock the NewStrategyManager
        self.manager_mock = patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.NewStrategyManager').start()
        self.manager_instance = self.manager_mock.return_value
        
        # Create a UI instance
        self.ui = NewStrategyUI()
        
        # Replace the manager with our mock
        self.ui.manager = self.manager_instance
        
        # Sample strategy for testing
        self.sample_strategy = {
            'name': 'TestStrategy',
            'description': 'A test strategy',
            'category': 'test',
            'default_provider': 'openai',
            'file_path': '/path/to/test_strategy.py',
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'summary': {'type': 'string'}
                },
                'required': ['title', 'summary']
            },
            'instruction': 'Extract the title and summary from the content.'
        }
        
        # Sample extraction result
        self.sample_result = {
            'title': 'Test Title',
            'summary': 'Test Summary'
        }
    
    def tearDown(self):
        """Clean up after the test case."""
        patch.stopall()
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_load_strategy_module(self, mock_importlib, mock_inspect):
        """Test loading a strategy module."""
        # Mock the imported module
        mock_module = MagicMock()
        mock_importlib.import_module.return_value = mock_module
        
        # Mock the strategy class
        mock_strategy_class = MagicMock()
        mock_strategy_class.SCHEMA = self.sample_strategy['schema']
        mock_strategy_class.INSTRUCTION = self.sample_strategy['instruction']
        
        # Set up the inspect.getmembers to return our mock class
        mock_inspect.isclass.return_value = True
        mock_inspect.getmembers.return_value = [("TestStrategy", mock_strategy_class)]
        
        # Call the method
        result = self.ui._load_strategy_module(self.sample_strategy['file_path'])
        
        # Assertions
        self.assertEqual(result, mock_module)
        mock_importlib.import_module.assert_called()
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.SyncExtractionStrategyWrapper')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.StrategyFactory')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_run_extraction(self, mock_importlib, mock_inspect, mock_factory, mock_wrapper):
        """Test running an extraction."""
        # Mock the session state
        self.streamlit_mock.session_state = {}
        
        # Mock the text input
        self.streamlit_mock.text_area.return_value = "Test content"
        
        # Mock the button click
        self.streamlit_mock.button.return_value = True
        
        # Mock the progress bar and status text
        mock_progress_bar = MagicMock()
        self.streamlit_mock.progress.return_value = mock_progress_bar
        mock_status_text = MagicMock()
        self.streamlit_mock.empty.return_value = mock_status_text
        
        # Mock the imported module
        mock_module = MagicMock()
        mock_importlib.import_module.return_value = mock_module
        
        # Mock the strategy class
        mock_strategy_class = MagicMock()
        mock_strategy_class.SCHEMA = self.sample_strategy['schema']
        mock_strategy_class.INSTRUCTION = self.sample_strategy['instruction']
        
        # Set up the inspect.getmembers to return our mock class
        mock_inspect.isclass.return_value = True
        mock_inspect.getmembers.return_value = [("TestStrategy", mock_strategy_class)]
        
        # Mock the factory and strategy instance
        mock_strategy_instance = MagicMock()
        mock_factory.return_value.create_strategy.return_value = mock_strategy_instance
        
        # Mock the wrapper
        mock_sync_strategy = MagicMock()
        mock_wrapper.return_value = mock_sync_strategy
        mock_sync_strategy.extract.return_value = self.sample_result
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Assertions
        mock_progress_bar.progress.assert_called()
        mock_status_text.text.assert_called()
        mock_factory.return_value.create_strategy.assert_called()
        mock_wrapper.assert_called_with(mock_strategy_instance)
        mock_sync_strategy.extract.assert_called()
        self.streamlit_mock.json.assert_called_with(self.sample_result)
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.SyncExtractionStrategyWrapper')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.StrategyFactory')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
    def test_run_extraction_error(self, mock_importlib, mock_inspect, mock_factory, mock_wrapper):
        """Test running an extraction with an error."""
        # Mock the session state
        self.streamlit_mock.session_state = {}
        
        # Mock the text input
        self.streamlit_mock.text_area.return_value = "Test content"
        
        # Mock the button click
        self.streamlit_mock.button.return_value = True
        
        # Mock the progress bar and status text
        mock_progress_bar = MagicMock()
        self.streamlit_mock.progress.return_value = mock_progress_bar
        mock_status_text = MagicMock()
        self.streamlit_mock.empty.return_value = mock_status_text
        
        # Mock the imported module
        mock_module = MagicMock()
        mock_importlib.import_module.return_value = mock_module
        
        # Mock the strategy class
        mock_strategy_class = MagicMock()
        mock_strategy_class.SCHEMA = self.sample_strategy['schema']
        mock_strategy_class.INSTRUCTION = self.sample_strategy['instruction']
        
        # Set up the inspect.getmembers to return our mock class
        mock_inspect.isclass.return_value = True
        mock_inspect.getmembers.return_value = [("TestStrategy", mock_strategy_class)]
        
        # Mock the factory and strategy instance
        mock_strategy_instance = MagicMock()
        mock_factory.return_value.create_strategy.return_value = mock_strategy_instance
        
        # Mock the wrapper to raise an exception
        mock_sync_strategy = MagicMock()
        mock_wrapper.return_value = mock_sync_strategy
        mock_sync_strategy.extract.side_effect = Exception("Test error")
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Assertions
        mock_progress_bar.progress.assert_called()
        mock_status_text.text.assert_called()
        mock_factory.return_value.create_strategy.assert_called()
        mock_wrapper.assert_called_with(mock_strategy_instance)
        mock_sync_strategy.extract.assert_called()
        self.streamlit_mock.error.assert_called()


if __name__ == '__main__':
    unittest.main()