#!/usr/bin/env python3
"""
Test suite specifically for the extraction button functionality in the UI.

This module provides comprehensive tests for the 'Run Extraction' button
and its associated functionality in the strategy testing UI.
"""

import os
import sys
import json
import time
import unittest
from unittest.mock import patch, MagicMock, AsyncMock, call
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the UI module
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui import NewStrategyUI
from src.cry_a_4mcp.crawl4ai.extraction_strategies.base import ExtractionError, APIConnectionError
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper
from src.cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory


class TestExtractionButton(unittest.TestCase):
    """Test case specifically for the extraction button functionality."""

    def setUp(self):
        """Set up the test case with all necessary mocks."""
        # Mock Streamlit components
        self.st_patcher = patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.st')
        self.mock_st = self.st_patcher.start()
        
        # Mock session state as a dictionary with all required keys
        self.mock_st.session_state = {
            'selected_strategy': None,
            'edit_mode': False,
            'delete_confirmation': False,
            'view_code': False,
            'test_mode': False,
            'create_mode': False,
            'filter_category': 'All',
            'search_query': ''
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
        
        # Mock importlib and inspect
        self.importlib_patcher = patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.importlib')
        self.mock_importlib = self.importlib_patcher.start()
        
        self.inspect_patcher = patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.inspect')
        self.mock_inspect = self.inspect_patcher.start()
        
        # Mock StrategyFactory
        self.factory_patcher = patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.StrategyFactory')
        self.mock_factory_class = self.factory_patcher.start()
        self.mock_factory = self.mock_factory_class.return_value
        
        # Mock SyncExtractionStrategyWrapper
        self.wrapper_patcher = patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.SyncExtractionStrategyWrapper')
        self.mock_wrapper_class = self.wrapper_patcher.start()
        self.mock_wrapper = self.mock_wrapper_class.return_value
        
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
        
        # Mock the module and strategy class
        self.mock_module = MagicMock()
        self.mock_importlib.import_module.return_value = self.mock_module
        
        self.mock_strategy_class = MagicMock()
        self.mock_strategy_class.SCHEMA = self.sample_strategy['schema']
        self.mock_strategy_class.INSTRUCTION = self.sample_strategy['instruction']
        
        # Set up inspect.getmembers to return our mock class
        self.mock_inspect.isclass.return_value = True
        self.mock_inspect.getmembers.return_value = [("TestStrategy", self.mock_strategy_class)]
        
        # Mock strategy instance
        self.mock_strategy_instance = MagicMock()
        self.mock_factory.create_strategy.return_value = self.mock_strategy_instance
        
        # Sample extraction result
        self.sample_result = {
            'title': 'Test Title',
            'summary': 'Test Summary'
        }
        
        # Set the wrapper to return our sample result
        self.mock_wrapper.extract.return_value = self.sample_result
    
    def tearDown(self):
        """Clean up after the test case."""
        self.st_patcher.stop()
        self.manager_patcher.stop()
        self.importlib_patcher.stop()
        self.inspect_patcher.stop()
        self.factory_patcher.stop()
        self.wrapper_patcher.stop()
    
    def test_extraction_button_not_clicked(self):
        """Test when the extraction button is not clicked."""
        # Mock the button not being clicked
        self.mock_st.button.return_value = False
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify that extraction was not attempted
        self.mock_wrapper_class.assert_not_called()
        self.mock_wrapper.extract.assert_not_called()
    
    def test_extraction_button_clicked_no_content(self):
        """Test when the extraction button is clicked but no content is provided."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock empty content
        self.mock_st.text_area.return_value = ""
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify that an error was shown
        self.mock_st.error.assert_called_with("Please enter content to extract from.")
        
        # Verify that extraction was not attempted
        self.mock_wrapper_class.assert_not_called()
        self.mock_wrapper.extract.assert_not_called()
    
    def test_extraction_button_clicked_no_api_key(self):
        """Test when the extraction button is clicked but no API key is provided."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock content but no API key
        self.mock_st.text_area.return_value = "Test content"
        self.mock_st.text_input.return_value = ""
        
        # Set provider that requires API key
        self.mock_st.selectbox.side_effect = ["openai", "gpt-4"]
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify that an error was shown
        self.mock_st.error.assert_called_with("Please enter an API key.")
        
        # Verify that extraction was not attempted
        self.mock_wrapper_class.assert_not_called()
        self.mock_wrapper.extract.assert_not_called()
    
    def test_extraction_button_clicked_success(self):
        """Test when the extraction button is clicked and extraction succeeds."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock content and API key
        self.mock_st.text_area.return_value = "Test content"
        self.mock_st.text_input.return_value = "test-api-key"
        
        # Set provider and model
        self.mock_st.selectbox.side_effect = ["openai", "gpt-4"]
        
        # Set up time.time for execution time measurement
        with patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.new_strategy_ui.time') as mock_time:
            mock_time.time.side_effect = [0, 1.5]  # Start time, end time
            
            # Call the method
            self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify progress updates
        expected_progress_calls = [
            call(0.2),  # Loading strategy module
            call(0.4),  # Finding strategy class
            call(0.6),  # Creating strategy instance
            call(0.8),  # Running extraction
            call(1.0)   # Completed
        ]
        self.mock_progress.progress.assert_has_calls(expected_progress_calls)
        
        # Verify status updates
        expected_status_calls = [
            call("Loading strategy module..."),
            call("Finding strategy class..."),
            call("Creating strategy instance..."),
            call("Running extraction..."),
            call("Extraction completed in 1.50 seconds.")
        ]
        self.mock_status.text.assert_has_calls(expected_status_calls)
        
        # Verify factory and wrapper calls
        self.mock_factory.create_strategy.assert_called_with(
            self.mock_strategy_class,
            provider="openai",
            model="gpt-4",
            api_token="test-api-key"
        )
        self.mock_wrapper_class.assert_called_with(self.mock_strategy_instance)
        self.mock_wrapper.extract.assert_called_with(url="dummy_url", content="Test content")
        
        # Verify result display
        self.mock_st.json.assert_called_with(self.sample_result)
        self.mock_st.download_button.assert_called()
    
    def test_extraction_button_clicked_api_error(self):
        """Test when the extraction button is clicked but API connection fails."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock content and API key
        self.mock_st.text_area.return_value = "Test content"
        self.mock_st.text_input.return_value = "test-api-key"
        
        # Set provider and model
        self.mock_st.selectbox.side_effect = ["openai", "gpt-4"]
        
        # Make the wrapper raise an API connection error
        self.mock_wrapper.extract.side_effect = APIConnectionError("Failed to connect to API")
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify that an error was shown
        self.mock_st.error.assert_called_with("Failed to connect to API")
        
        # Verify that extraction was attempted
        self.mock_wrapper_class.assert_called_with(self.mock_strategy_instance)
        self.mock_wrapper.extract.assert_called_with(url="dummy_url", content="Test content")
    
    def test_extraction_button_clicked_extraction_error(self):
        """Test when the extraction button is clicked but extraction fails."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock content and API key
        self.mock_st.text_area.return_value = "Test content"
        self.mock_st.text_input.return_value = "test-api-key"
        
        # Set provider and model
        self.mock_st.selectbox.side_effect = ["openai", "gpt-4"]
        
        # Make the wrapper raise an extraction error
        self.mock_wrapper.extract.side_effect = ExtractionError("Failed to extract data")
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify that an error was shown
        self.mock_st.error.assert_called_with("Failed to extract data")
        
        # Verify that extraction was attempted
        self.mock_wrapper_class.assert_called_with(self.mock_strategy_instance)
        self.mock_wrapper.extract.assert_called_with(url="dummy_url", content="Test content")
    
    def test_extraction_button_clicked_generic_error(self):
        """Test when the extraction button is clicked but a generic error occurs."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock content and API key
        self.mock_st.text_area.return_value = "Test content"
        self.mock_st.text_input.return_value = "test-api-key"
        
        # Set provider and model
        self.mock_st.selectbox.side_effect = ["openai", "gpt-4"]
        
        # Make the wrapper raise a generic exception
        error_message = "Something went wrong"
        self.mock_wrapper.extract.side_effect = Exception(error_message)
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify that an error was shown
        self.mock_st.error.assert_called_with(f"Error: {error_message}")
        
        # Verify that extraction was attempted
        self.mock_wrapper_class.assert_called_with(self.mock_strategy_instance)
        self.mock_wrapper.extract.assert_called_with(url="dummy_url", content="Test content")
    
    def test_extraction_button_clicked_ollama_provider(self):
        """Test when the extraction button is clicked with Ollama provider (no API key needed)."""
        # Mock the button being clicked
        self.mock_st.button.return_value = True
        
        # Mock content but no API key
        self.mock_st.text_area.return_value = "Test content"
        self.mock_st.text_input.return_value = ""
        
        # Set provider to Ollama (which doesn't require an API key)
        self.mock_st.selectbox.side_effect = ["ollama", "llama2"]
        
        # Call the method
        self.ui._show_test_strategy(self.sample_strategy)
        
        # Verify that no API key error was shown
        for call_args in self.mock_st.error.call_args_list:
            self.assertNotEqual(call_args, call("Please enter an API key."))
        
        # Verify that extraction was attempted
        self.mock_wrapper_class.assert_called_with(self.mock_strategy_instance)
        self.mock_wrapper.extract.assert_called_with(url="dummy_url", content="Test content")


if __name__ == '__main__':
    unittest.main()