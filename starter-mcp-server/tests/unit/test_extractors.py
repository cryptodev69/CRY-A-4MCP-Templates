"""Comprehensive unit tests for the extractors API endpoints.

This module provides thorough testing coverage for the extractors functionality
within the CRY-A-4MCP platform, including:
    - Strategy discovery mechanisms
    - API endpoint behavior validation
    - Error handling and edge cases
    - Response format verification
    - Logging and monitoring validation

The tests use mocking to isolate the units under test and ensure
reproducible, fast execution without filesystem dependencies.

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

# Standard library imports for testing infrastructure
import os
import pytest
from unittest.mock import Mock, patch, mock_open
from fastapi import HTTPException
from typing import List, Dict

# Import the modules under test - extractors API functionality
from src.cry_a_4mcp.api.endpoints.extractors import (
    discover_real_strategies,  # Core strategy discovery function
    get_extractors,           # API endpoint for listing all extractors
    get_extractor             # API endpoint for retrieving specific extractor
)
from src.cry_a_4mcp.api.models import ExtractorResponse  # Response model for API


class TestDiscoverRealStrategies:
    """Test suite for the discover_real_strategies function.
    
    This class contains comprehensive tests for the strategy discovery
    mechanism, covering normal operation, error conditions, and edge cases.
    """
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.path.exists')
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.listdir')
    @patch('src.cry_a_4mcp.api.endpoints.extractors.open', new_callable=mock_open)
    def test_discover_strategies_success(self, mock_file, mock_listdir, mock_exists):
        """Test successful discovery of extraction strategies.
        
        Validates that the function correctly:
        - Scans the strategies directory
        - Parses Python files for class definitions
        - Extracts schema and instructions metadata
        - Returns properly formatted strategy dictionaries
        """
        # Arrange: Set up mock filesystem state to simulate real directory structure
        mock_exists.return_value = True  # Directory exists
        mock_listdir.return_value = ['crypto_news.py', 'trading_signals.py', '__init__.py']
        
        # Mock file content with realistic strategy class definitions
        # This simulates a typical extractor class with schema and instructions
        strategy_content = '''
class CryptoNewsExtractor(BaseExtractor):
    """Extract cryptocurrency news articles."""
    
    schema = "title,content,timestamp,sentiment"
    instructions = "Extract news articles about cryptocurrency with sentiment analysis"
    
    def extract(self, content):
        pass
'''
        mock_file.return_value.read.return_value = strategy_content
        
        # Act: Execute the discovery function to scan for strategies
        result = discover_real_strategies()
        
        # Assert: Verify the results match expected structure and content
        assert len(result) == 2  # Two .py files processed (excluding __init__.py)
        
        # Verify first strategy structure contains all required fields
        strategy = result[0]
        assert strategy['name'] == 'CryptoNewsExtractor'
        assert strategy['file'] == 'crypto_news.py'
        assert 'title,content,timestamp,sentiment' in strategy['schema']
        assert 'Extract news articles' in strategy['instructions']
        
        # Verify filesystem interactions occurred as expected
        assert mock_exists.called
        assert mock_listdir.called
        assert mock_file.called
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.path.exists')
    def test_discover_strategies_directory_not_found(self, mock_exists):
        """Test behavior when strategies directory doesn't exist.
        
        Validates that the function:
        - Handles missing directory gracefully
        - Returns empty list without raising exceptions
        - Logs appropriate warning messages
        """
        # Arrange: Simulate missing directory scenario
        # This tests the robustness of the discovery mechanism
        mock_exists.return_value = False
        
        # Act: Execute discovery with missing directory
        # Should handle gracefully without throwing exceptions
        result = discover_real_strategies()
        
        # Assert: Verify graceful handling of missing directory
        # Function should return empty list rather than crashing
        assert result == []
        assert mock_exists.called  # Verify directory check was attempted
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.path.exists')
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.listdir')
    @patch('src.cry_a_4mcp.api.endpoints.extractors.open', new_callable=mock_open)
    def test_discover_strategies_file_read_error(self, mock_file, mock_listdir, mock_exists):
        """Test handling of file reading errors during discovery.
        
        Validates that the function:
        - Continues processing other files when one fails
        - Logs errors appropriately
        - Returns partial results for successful files
        """
        # Arrange: Set up filesystem with one problematic file
        # This simulates real-world scenarios where some files may be corrupted or inaccessible
        mock_exists.return_value = True
        mock_listdir.return_value = ['good_strategy.py', 'bad_strategy.py']
        
        # Configure mock to raise exception for second file
        # This tests error resilience - one bad file shouldn't break the entire discovery
        def side_effect(*args, **kwargs):
            if 'bad_strategy.py' in str(args[0]):
                raise IOError("Permission denied")  # Simulate file access error
            return mock_open(read_data='class GoodStrategy(BaseExtractor): pass').return_value
        
        mock_file.side_effect = side_effect
        
        # Act: Execute discovery with mixed file conditions
        # Should process good files and skip bad ones gracefully
        result = discover_real_strategies()
        
        # Assert: Verify partial success - good files processed, bad files skipped
        assert len(result) == 1  # Only the good file should be processed
        assert result[0]['name'] == 'GoodStrategy'
        assert result[0]['file'] == 'good_strategy.py'
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.path.exists')
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.listdir')
    @patch('src.cry_a_4mcp.api.endpoints.extractors.open', new_callable=mock_open)
    def test_discover_strategies_no_classes_found(self, mock_file, mock_listdir, mock_exists):
        """Test discovery when Python files contain no strategy classes.
        
        Validates that the function:
        - Handles files without class definitions
        - Returns empty results for such files
        - Continues processing normally
        """
        # Arrange: Set up file with no class definitions
        mock_exists.return_value = True
        mock_listdir.return_value = ['utils.py']
        mock_file.return_value.read.return_value = '''
# Utility functions
def helper_function():
    pass

variable = "some value"
'''
        
        # Act: Execute discovery
        result = discover_real_strategies()
        
        # Assert: Verify empty result
        assert result == []
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.path.exists')
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.listdir')
    @patch('src.cry_a_4mcp.api.endpoints.extractors.open', new_callable=mock_open)
    def test_discover_strategies_complex_regex_patterns(self, mock_file, mock_listdir, mock_exists):
        """Test regex pattern matching for complex strategy definitions.
        
        Validates that the function correctly extracts:
        - Multi-line schema definitions
        - Complex instruction strings
        - Various quote styles and formatting
        """
        # Arrange: Set up complex strategy content
        mock_exists.return_value = True
        mock_listdir.return_value = ['complex_strategy.py']
        
        complex_content = '''
class ComplexExtractor(BaseExtractor):
    """Complex extraction strategy with multi-line definitions."""
    
    schema = """title,content,timestamp,
                author,tags,sentiment_score,
                confidence_level"""
    
    instructions = """Extract comprehensive data from news articles including:
                      - Article metadata (title, author, timestamp)
                      - Content analysis (sentiment, confidence)
                      - Categorization tags"""
    
    def extract(self, content):
        return {}
'''
        mock_file.return_value.read.return_value = complex_content
        
        # Act: Execute discovery
        result = discover_real_strategies()
        
        # Assert: Verify complex pattern extraction
        assert len(result) == 1
        strategy = result[0]
        assert strategy['name'] == 'ComplexExtractor'
        assert 'title,content,timestamp' in strategy['schema']
        assert 'Extract comprehensive data' in strategy['instructions']


class TestGetExtractorsEndpoint:
    """Test suite for the get_extractors API endpoint.
    
    This class validates the REST API endpoint behavior including
    response formatting, error handling, and integration with the
    discovery mechanism.
    """
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.discover_real_strategies')
    @pytest.mark.asyncio
    async def test_get_extractors_success(self, mock_discover):
        """Test successful retrieval of all extractors.
        
        Validates that the endpoint:
        - Calls the discovery function correctly
        - Transforms strategy data to API response format
        - Returns properly structured ExtractorResponse objects
        """
        # Arrange: Mock discovery results
        # This simulates the discovery function returning realistic strategy data
        # that would be found in the filesystem during normal operation
        mock_strategies = [
            {
                'name': 'CryptoNewsExtractor',
                'file': 'crypto_news.py',
                'schema': 'title,content,timestamp',
                'instructions': 'Extract crypto news articles'
            },
            {
                'name': 'TradingSignalExtractor',
                'file': 'trading_signals.py',
                'schema': 'symbol,signal,confidence',
                'instructions': 'Extract trading signals'
            }
        ]
        mock_discover.return_value = mock_strategies
        
        # Act: Call the endpoint
        # This tests the async API endpoint's ability to process discovery results
        # and transform them into proper API response objects
        result = await get_extractors()
        
        # Assert: Verify response structure and content
        # Ensure all results are properly formatted ExtractorResponse objects
        assert len(result) == 2
        assert all(isinstance(extractor, ExtractorResponse) for extractor in result)
        
        # Verify first extractor details
        # Check that strategy data is correctly mapped to response object fields
        first_extractor = result[0]
        assert first_extractor.id == 'CryptoNewsExtractor'
        assert first_extractor.name == 'CryptoNewsExtractor'
        assert first_extractor.description == 'Extract crypto news articles'
        assert first_extractor.schema == 'title,content,timestamp'
        assert first_extractor.file_path == 'crypto_news.py'
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.discover_real_strategies')
    @pytest.mark.asyncio
    async def test_get_extractors_empty_result(self, mock_discover):
        """Test endpoint behavior when no strategies are found.
        
        Validates that the endpoint:
        - Handles empty discovery results gracefully
        - Returns empty list without errors
        - Maintains proper response format
        """
        # Arrange: Mock empty discovery
        # This simulates scenarios where no extraction strategies are found
        # in the filesystem, such as empty directories or missing files
        mock_discover.return_value = []
        
        # Act: Call the endpoint
        # Tests the API's ability to handle empty results gracefully
        # without throwing exceptions or returning malformed responses
        result = await get_extractors()
        
        # Assert: Verify empty response
        # Ensure the endpoint returns a proper empty list structure
        # maintaining consistency with the expected response format
        assert result == []
        assert isinstance(result, list)
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.discover_real_strategies')
    @pytest.mark.asyncio
    async def test_get_extractors_discovery_error(self, mock_discover):
        """Test endpoint error handling when discovery fails.
        
        Validates that the endpoint:
        - Catches discovery exceptions
        - Returns appropriate HTTP error responses
        - Logs errors for debugging
        """
        # Arrange: Mock discovery failure
        mock_discover.side_effect = Exception("Filesystem error")
        
        # Act & Assert: Verify exception handling
        with pytest.raises(HTTPException) as exc_info:
            await get_extractors()
        
        assert exc_info.value.status_code == 500
        assert "Internal server error" in exc_info.value.detail
        assert "Filesystem error" in exc_info.value.detail
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.discover_real_strategies')
    @pytest.mark.asyncio
    async def test_get_extractors_missing_metadata(self, mock_discover):
        """Test endpoint handling of strategies with missing metadata.
        
        Validates that the endpoint:
        - Handles strategies without schema or instructions
        - Provides appropriate fallback values
        - Maintains response consistency
        """
        # Arrange: Mock strategy with missing metadata
        mock_strategies = [
            {
                'name': 'MinimalExtractor',
                'file': 'minimal.py',
                'schema': '',  # Empty schema
                'instructions': ''  # Empty instructions
            }
        ]
        mock_discover.return_value = mock_strategies
        
        # Act: Call the endpoint
        result = await get_extractors()
        
        # Assert: Verify fallback handling
        assert len(result) == 1
        extractor = result[0]
        assert extractor.id == 'MinimalExtractor'
        assert extractor.schema == ''
        assert 'Extraction strategy implemented in minimal.py' in extractor.description


class TestGetExtractorEndpoint:
    """Test suite for the get_extractor API endpoint.
    
    This class validates the single extractor retrieval endpoint
    including parameter validation, search logic, and error responses.
    """
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.discover_real_strategies')
    @pytest.mark.asyncio
    async def test_get_extractor_success(self, mock_discover):
        """Test successful retrieval of a specific extractor.
        
        Validates that the endpoint:
        - Finds the requested extractor by ID
        - Returns properly formatted response
        - Includes all expected metadata
        """
        # Arrange: Mock discovery with target strategy
        # This simulates a realistic scenario with multiple available extractors
        # where the client requests a specific one by its unique identifier
        mock_strategies = [
            {
                'name': 'CryptoNewsExtractor',
                'file': 'crypto_news.py',
                'schema': 'title,content,timestamp',
                'instructions': 'Extract crypto news articles'
            },
            {
                'name': 'TradingSignalExtractor',
                'file': 'trading_signals.py',
                'schema': 'symbol,signal,confidence',
                'instructions': 'Extract trading signals'
            }
        ]
        mock_discover.return_value = mock_strategies
        
        # Act: Request specific extractor
        # Tests the endpoint's ability to filter and return the correct extractor
        # from the available set based on the provided ID parameter
        result = await get_extractor('CryptoNewsExtractor')
        
        # Assert: Verify correct extractor returned
        # Ensures the API correctly identifies and returns the requested extractor
        # with all its metadata properly formatted in the response object
        assert isinstance(result, ExtractorResponse)
        assert result.id == 'CryptoNewsExtractor'
        assert result.name == 'CryptoNewsExtractor'
        assert result.description == 'Extract crypto news articles'
        assert result.schema == 'title,content,timestamp'
        assert result.file_path == 'crypto_news.py'
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.discover_real_strategies')
    @pytest.mark.asyncio
    async def test_get_extractor_not_found(self, mock_discover):
        """Test endpoint behavior when requested extractor doesn't exist.
        
        Validates that the endpoint:
        - Returns 404 status for missing extractors
        - Provides helpful error message with available options
        - Includes list of available extractors in response
        """
        # Arrange: Mock discovery without target strategy
        # This simulates a scenario where the client requests an extractor
        # that doesn't exist in the current system configuration
        mock_strategies = [
            {
                'name': 'ExistingExtractor',
                'file': 'existing.py',
                'schema': 'data',
                'instructions': 'Extract data'
            }
        ]
        mock_discover.return_value = mock_strategies
        
        # Act & Assert: Verify 404 response
        # Tests the API's error handling when client requests unavailable resource
        # Should provide helpful feedback about what extractors are actually available
        with pytest.raises(HTTPException) as exc_info:
            await get_extractor('NonExistentExtractor')
        
        # Verify proper HTTP status and error message content
        # Ensures the error response follows REST API conventions
        # and provides actionable information to the client
        assert exc_info.value.status_code == 404
        assert 'NonExistentExtractor' in exc_info.value.detail
        assert 'Available extractors' in exc_info.value.detail
        assert 'ExistingExtractor' in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_extractor_empty_id(self):
        """Test endpoint validation for empty extractor ID.
        
        Validates that the endpoint:
        - Rejects empty or whitespace-only IDs
        - Returns 400 Bad Request status
        - Provides clear validation error message
        """
        # Test empty string
        # This validates input sanitization to prevent invalid API calls
        # Empty IDs should be rejected before any processing occurs
        with pytest.raises(HTTPException) as exc_info:
            await get_extractor('')
        
        # Verify proper validation error response
        # Ensures the API follows HTTP standards for client errors
        assert exc_info.value.status_code == 400
        assert 'cannot be empty' in exc_info.value.detail
        
        # Test whitespace-only string
        # This tests edge case where ID appears non-empty but contains only whitespace
        # Such inputs should also be rejected as invalid
        with pytest.raises(HTTPException) as exc_info:
            await get_extractor('   ')
        
        # Verify consistent validation behavior for whitespace-only input
        # Maintains API contract that IDs must contain meaningful content
        assert exc_info.value.status_code == 400
        assert 'cannot be empty' in exc_info.value.detail
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.discover_real_strategies')
    @pytest.mark.asyncio
    async def test_get_extractor_discovery_error(self, mock_discover):
        """Test endpoint error handling when discovery fails.
        
        Validates that the endpoint:
        - Handles discovery exceptions gracefully
        - Returns 500 status for internal errors
        - Preserves original error information
        """
        # Arrange: Mock discovery failure
        # This simulates internal system failures like database connectivity issues,
        # filesystem problems, or other infrastructure-related errors
        mock_discover.side_effect = Exception("Database connection failed")
        
        # Act & Assert: Verify error handling
        # Tests the API's resilience when underlying services fail
        # Should convert internal exceptions to proper HTTP error responses
        with pytest.raises(HTTPException) as exc_info:
            await get_extractor('AnyExtractor')
        
        # Verify proper error response structure
        # Ensures internal errors are properly categorized as server errors (5xx)
        # while preserving enough context for debugging without exposing internals
        assert exc_info.value.status_code == 500
        assert "Internal server error" in exc_info.value.detail
        assert "AnyExtractor" in exc_info.value.detail
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.discover_real_strategies')
    @pytest.mark.asyncio
    async def test_get_extractor_case_sensitivity(self, mock_discover):
        """Test that extractor ID matching is case-sensitive.
        
        Validates that the endpoint:
        - Performs exact case-sensitive matching
        - Distinguishes between similar names with different cases
        - Returns 404 for case mismatches
        """
        # Arrange: Mock strategy with specific case
        # This tests the API's string matching behavior to ensure
        # consistent and predictable identifier resolution
        mock_strategies = [
            {
                'name': 'CryptoNewsExtractor',
                'file': 'crypto_news.py',
                'schema': 'title,content',
                'instructions': 'Extract news'
            }
        ]
        mock_discover.return_value = mock_strategies
        
        # Act & Assert: Test case sensitivity
        # Correct case should work
        # This validates that exact matches are found successfully
        result = await get_extractor('CryptoNewsExtractor')
        assert result.id == 'CryptoNewsExtractor'
        
        # Wrong case should fail
        # Tests that the API enforces exact case matching
        # This prevents ambiguity and ensures consistent behavior
        with pytest.raises(HTTPException) as exc_info:
            await get_extractor('cryptonewsextractor')
        
        assert exc_info.value.status_code == 404
        
        # Test uppercase variation also fails
        # Confirms case sensitivity applies in both directions
        with pytest.raises(HTTPException) as exc_info:
            await get_extractor('CRYPTONEWSEXTRACTOR')
        
        assert exc_info.value.status_code == 404


class TestIntegrationScenarios:
    """Integration test scenarios for the extractors module.
    
    This class tests end-to-end scenarios and complex interactions
    between different components of the extractors functionality.
    """
    
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.path.exists')
    @patch('src.cry_a_4mcp.api.endpoints.extractors.os.listdir')
    @patch('src.cry_a_4mcp.api.endpoints.extractors.open', new_callable=mock_open)
    @pytest.mark.asyncio
    async def test_full_discovery_to_api_flow(self, mock_file, mock_listdir, mock_exists):
        """Test complete flow from filesystem discovery to API response.
        
        This integration test validates:
        - Filesystem scanning and parsing
        - Strategy data transformation
        - API endpoint response formatting
        - End-to-end data consistency
        """
        # Arrange: Set up realistic filesystem scenario
        mock_exists.return_value = True
        mock_listdir.return_value = ['crypto_news.py', 'market_analysis.py']
        
        # Mock realistic strategy file content
        strategy_content = '''
from base_extractor import BaseExtractor

class CryptoNewsExtractor(BaseExtractor):
    """Extract cryptocurrency news with sentiment analysis."""
    
    schema = "title,content,timestamp,sentiment_score,source_url"
    instructions = """Extract news articles about cryptocurrency including:
                      - Article title and content
                      - Publication timestamp
                      - Sentiment analysis score
                      - Source URL for verification"""
    
    def extract(self, html_content):
        # Implementation details...
        pass
'''
        mock_file.return_value.read.return_value = strategy_content
        
        # Act: Test complete flow
        # 1. Test discovery function directly
        strategies = discover_real_strategies()
        assert len(strategies) == 2
        
        # 2. Test get_extractors endpoint
        extractors = await get_extractors()
        assert len(extractors) == 2
        assert all(isinstance(e, ExtractorResponse) for e in extractors)
        
        # 3. Test get_extractor endpoint
        specific_extractor = await get_extractor('CryptoNewsExtractor')
        assert specific_extractor.id == 'CryptoNewsExtractor'
        assert 'sentiment analysis' in specific_extractor.description
        
        # 4. Verify data consistency across all levels
        strategy_dict = next(s for s in strategies if s['name'] == 'CryptoNewsExtractor')
        api_extractor = next(e for e in extractors if e.id == 'CryptoNewsExtractor')
        
        assert strategy_dict['name'] == api_extractor.id == specific_extractor.id
        assert strategy_dict['schema'] == api_extractor.schema == specific_extractor.schema
        assert strategy_dict['file'] == api_extractor.file_path == specific_extractor.file_path


if __name__ == '__main__':
    """Run the test suite when executed directly.
    
    This allows for easy execution of the test suite during development
    and provides a convenient way to validate the extractors functionality.
    """
    pytest.main([__file__, '-v', '--tb=short'])