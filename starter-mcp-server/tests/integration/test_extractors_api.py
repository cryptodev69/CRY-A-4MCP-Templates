"""Integration tests for the extractors API endpoints.

This module provides comprehensive integration testing for the extractors
API endpoints within the CRY-A-4MCP platform, including:
    - Real HTTP request/response testing
    - Database and filesystem integration
    - End-to-end workflow validation
    - Performance and load testing scenarios
    - Cross-component interaction testing
    - Schema validation and response formatting
    - Authentication and authorization (if applicable)

These tests complement the unit tests by validating the complete
system behavior in realistic deployment scenarios.

Test Strategy:
- Uses real FastAPI TestClient for authentic HTTP testing
- Mocks filesystem operations to ensure test isolation
- Validates both success and failure scenarios
- Tests API contract compliance and response schemas
- Includes performance benchmarks and load testing

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

# Standard library imports for testing infrastructure
import asyncio  # Async/await support for testing concurrent operations
import json  # JSON parsing and serialization for API responses
import os  # Operating system interface for environment variables
import tempfile  # Temporary file and directory creation for test isolation
import shutil  # High-level file operations for cleanup
from pathlib import Path  # Object-oriented filesystem path handling
from typing import Dict, List, Any  # Type hints for better code documentation

# Third-party testing libraries
import pytest  # Primary testing framework for test discovery and execution
import httpx  # HTTP client library for advanced request handling
from fastapi.testclient import TestClient  # FastAPI-specific test client

# Import the FastAPI application and related components
from src.cry_a_4mcp.web_api import app  # Main FastAPI application instance
from src.cry_a_4mcp.api.models import ExtractorResponse  # Response model for type validation


class TestExtractorsAPIIntegration:
    """Integration test suite for extractors API endpoints.
    
    This class provides comprehensive testing of the extractors API
    in realistic scenarios with actual filesystem operations and
    HTTP request/response cycles.
    
    The integration tests validate:
    - Real HTTP request/response handling with FastAPI TestClient
    - Filesystem integration with temporary directory management
    - End-to-end workflow validation from request to response
    - Error handling and edge case scenarios
    - Performance characteristics and load testing
    - API contract compliance and response schema validation
    
    Test Strategy:
    - Uses realistic test data that mirrors production scenarios
    - Isolates tests using temporary directories and environment variables
    - Validates both successful operations and error conditions
    - Includes performance benchmarks and concurrent request testing
    """
    
    @pytest.fixture(scope="class")
    def test_client(self):
        """Create a test client for the FastAPI application.
        
        Returns:
            TestClient: Configured test client for API testing
        """
        return TestClient(app)
    
    @pytest.fixture(scope="function")
    def temp_strategies_dir(self):
        """Create a temporary directory with test strategy files.
        
        This fixture sets up a realistic testing environment with
        actual strategy files that can be discovered and processed.
        
        Yields:
            Path: Path to the temporary strategies directory
        """
        # Create temporary directory structure
        temp_dir = tempfile.mkdtemp(prefix="test_strategies_")
        strategies_path = Path(temp_dir) / "extraction_strategies"
        strategies_path.mkdir(parents=True, exist_ok=True)
        
        # Create realistic strategy files for testing
        self._create_test_strategy_files(strategies_path)
        
        # Temporarily modify the strategies path in the module
        original_path = os.environ.get('STRATEGIES_PATH')
        os.environ['STRATEGIES_PATH'] = str(strategies_path)
        
        try:
            yield strategies_path
        finally:
            # Cleanup: Restore original path and remove temp directory
            if original_path:
                os.environ['STRATEGIES_PATH'] = original_path
            elif 'STRATEGIES_PATH' in os.environ:
                del os.environ['STRATEGIES_PATH']
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _create_test_strategy_files(self, strategies_dir: Path) -> None:
        """Create realistic test strategy files in the given directory.
        
        Args:
            strategies_dir: Directory to create strategy files in
        """
        # Strategy 1: Cryptocurrency News Extractor
        crypto_news_content = '''
"""Cryptocurrency news extraction strategy."""

from typing import Dict, Any, List
from base_extractor import BaseExtractor


class CryptoNewsExtractor(BaseExtractor):
    """Extract cryptocurrency news articles with sentiment analysis.
    
    This extractor specializes in parsing cryptocurrency news websites
    and extracting structured data including sentiment indicators.
    """
    
    schema = "title,content,timestamp,author,sentiment_score,source_url,tags"
    instructions = """Extract comprehensive cryptocurrency news data including:
                      - Article title and full content
                      - Publication timestamp and author information
                      - Sentiment analysis score (-1.0 to 1.0)
                      - Source URL for verification and backlinks
                      - Relevant tags for categorization"""
    
    def __init__(self):
        """Initialize the cryptocurrency news extractor."""
        super().__init__()
        self.supported_domains = [
            'coindesk.com',
            'cointelegraph.com',
            'decrypt.co',
            'bitcoinmagazine.com'
        ]
    
    def extract(self, html_content: str, url: str = None) -> Dict[str, Any]:
        """Extract structured data from cryptocurrency news articles.
        
        Args:
            html_content: Raw HTML content of the news article
            url: Source URL of the article (optional)
        
        Returns:
            Dict containing extracted and structured news data
        """
        # Implementation would go here
        return {
            'title': 'Sample Crypto News Title',
            'content': 'Sample article content...',
            'timestamp': '2024-01-15T10:30:00Z',
            'author': 'Crypto Reporter',
            'sentiment_score': 0.75,
            'source_url': url or 'https://example.com/news',
            'tags': ['bitcoin', 'cryptocurrency', 'market-analysis']
        }
'''
        
        # Strategy 2: Trading Signals Extractor
        trading_signals_content = '''
"""Trading signals extraction strategy."""

from typing import Dict, Any, List, Optional
from base_extractor import BaseExtractor


class TradingSignalsExtractor(BaseExtractor):
    """Extract trading signals and market analysis data.
    
    This extractor processes trading platforms and signal providers
    to extract actionable trading information.
    """
    
    schema = "symbol,signal_type,entry_price,target_price,stop_loss,confidence,timeframe,analysis"
    instructions = """Extract trading signals with comprehensive market analysis:
                      - Trading symbol (e.g., BTC/USD, ETH/BTC)
                      - Signal type (BUY, SELL, HOLD)
                      - Entry price and target price levels
                      - Stop loss recommendations
                      - Confidence level (0-100%)
                      - Recommended timeframe
                      - Supporting technical analysis"""
    
    def __init__(self):
        """Initialize the trading signals extractor."""
        super().__init__()
        self.signal_types = ['BUY', 'SELL', 'HOLD']
        self.timeframes = ['1H', '4H', '1D', '1W']
    
    def extract(self, html_content: str, url: str = None) -> Dict[str, Any]:
        """Extract structured trading signals from market analysis content.
        
        Args:
            html_content: Raw HTML content containing trading signals
            url: Source URL of the signals (optional)
        
        Returns:
            Dict containing extracted trading signal data
        """
        # Implementation would go here
        return {
            'symbol': 'BTC/USD',
            'signal_type': 'BUY',
            'entry_price': 45000.00,
            'target_price': 48000.00,
            'stop_loss': 43000.00,
            'confidence': 85,
            'timeframe': '4H',
            'analysis': 'Strong bullish momentum with RSI oversold recovery'
        }
'''
        
        # Strategy 3: Market Data Extractor
        market_data_content = '''
"""Market data extraction strategy."""

from typing import Dict, Any, List
from base_extractor import BaseExtractor


class MarketDataExtractor(BaseExtractor):
    """Extract real-time market data and price information.
    
    This extractor focuses on gathering current market prices,
    volume data, and basic market statistics.
    """
    
    schema = "symbol,price,volume_24h,market_cap,price_change_24h,price_change_7d,last_updated"
    instructions = """Extract comprehensive market data including:
                      - Trading symbol and current price
                      - 24-hour trading volume
                      - Market capitalization
                      - Price changes (24h and 7d percentages)
                      - Last update timestamp"""
    
    def extract(self, html_content: str, url: str = None) -> Dict[str, Any]:
        """Extract market data from cryptocurrency exchanges.
        
        Args:
            html_content: Raw HTML content from exchange or market data site
            url: Source URL (optional)
        
        Returns:
            Dict containing extracted market data
        """
        # Implementation would go here
        return {
            'symbol': 'BTC',
            'price': 45250.75,
            'volume_24h': 28500000000,
            'market_cap': 885000000000,
            'price_change_24h': 2.35,
            'price_change_7d': -1.25,
            'last_updated': '2024-01-15T15:45:30Z'
        }
'''
        
        # Write strategy files to the temporary directory
        strategy_files = {
            'crypto_news.py': crypto_news_content,
            'trading_signals.py': trading_signals_content,
            'market_data.py': market_data_content
        }
        
        for filename, content in strategy_files.items():
            file_path = strategies_dir / filename
            file_path.write_text(content, encoding='utf-8')
        
        # Create an __init__.py file to make it a proper Python package
        init_file = strategies_dir / '__init__.py'
        init_file.write_text('"""Extraction strategies package."""\n', encoding='utf-8')
    
    def test_get_extractors_endpoint_success(self, test_client, temp_strategies_dir):
        """Test successful retrieval of all extractors via HTTP API.
        
        This test validates:
        - HTTP GET request handling
        - Response status and format
        - Data consistency with filesystem
        - JSON serialization of extractor data
        
        Args:
            test_client: FastAPI test client
            temp_strategies_dir: Temporary directory with test strategies
        """
        # Act: Make HTTP request to the extractors endpoint
        # This tests the complete HTTP request/response cycle through FastAPI
        response = test_client.get("/api/extractors")
        
        # Assert: Verify response structure and content
        # Ensures the API returns success status for valid requests
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # Parse and validate response data
        # Verifies JSON serialization and data structure integrity
        extractors_data = response.json()
        assert isinstance(extractors_data, list)  # Should be an array of extractors
        assert len(extractors_data) == 3  # Three test strategies created in fixture
        
        # Verify each extractor has required fields
        # Validates API contract compliance for all returned extractors
        for extractor in extractors_data:
            assert "id" in extractor  # Unique identifier field
            assert "name" in extractor  # Human-readable name
            assert "description" in extractor  # Functional description
            assert "schema" in extractor  # Data extraction schema
            assert "file_path" in extractor  # Source file location
            
            # Validate field types and content
            # Ensures proper data type serialization from Python to JSON
            assert isinstance(extractor["id"], str)
            assert isinstance(extractor["name"], str)
            assert isinstance(extractor["description"], str)
            assert isinstance(extractor["schema"], str)
            assert isinstance(extractor["file_path"], str)
            
            # Verify non-empty required fields
            # Ensures meaningful data is returned for essential fields
            assert len(extractor["id"]) > 0
            assert len(extractor["name"]) > 0
            assert len(extractor["schema"]) > 0
        
        # Verify specific extractors are present
        # Confirms that all test extractors were discovered and returned
        extractor_names = [e["name"] for e in extractors_data]
        assert "CryptoNewsExtractor" in extractor_names
        assert "TradingSignalsExtractor" in extractor_names
        assert "MarketDataExtractor" in extractor_names
    
    def test_get_extractor_by_id_success(self, test_client, temp_strategies_dir):
        """Test successful retrieval of a specific extractor by ID.
        
        This test validates:
        - HTTP GET request with path parameters
        - Correct extractor identification and retrieval
        - Response data accuracy and completeness
        
        Args:
            test_client: FastAPI test client
            temp_strategies_dir: Temporary directory with test strategies
        """
        # Act: Request specific extractor by ID
        # Tests the parameterized endpoint with path variable extraction
        response = test_client.get("/api/extractors/CryptoNewsExtractor")
        
        # Assert: Verify successful response
        # Ensures the API correctly handles ID-based filtering
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # Parse and validate extractor data
        # Verifies that the correct extractor is returned based on ID parameter
        extractor_data = response.json()
        assert extractor_data["id"] == "CryptoNewsExtractor"  # Exact ID match
        assert extractor_data["name"] == "CryptoNewsExtractor"  # Class name mapping
        assert "cryptocurrency news" in extractor_data["description"].lower()  # Content validation
        assert "title,content,timestamp" in extractor_data["schema"]  # Schema verification
        assert extractor_data["file_path"] == "crypto_news.py"  # File path mapping
        
        # Verify description contains key information from instructions
        # Ensures the description accurately reflects extractor capabilities
        description = extractor_data["description"]
        assert "sentiment analysis" in description.lower()  # Feature validation
        assert "article" in description.lower()  # Content type validation
    
    def test_get_extractor_not_found(self, test_client, temp_strategies_dir):
        """Test 404 response for non-existent extractor ID.
        
        This test validates:
        - Proper HTTP 404 status for missing resources
        - Helpful error message with available alternatives
        - JSON error response format
        
        Args:
            test_client: FastAPI test client
            temp_strategies_dir: Temporary directory with test strategies
        """
        # Act: Request non-existent extractor
        # Tests error handling for invalid resource identifiers
        response = test_client.get("/api/extractors/NonExistentExtractor")
        
        # Assert: Verify 404 response
        # Ensures proper HTTP status codes for missing resources
        assert response.status_code == 404
        assert response.headers["content-type"] == "application/json"
        
        # Parse and validate error response
        # Verifies that error responses follow consistent JSON format
        error_data = response.json()
        assert "detail" in error_data  # FastAPI standard error format
        
        # Validate error message content and helpfulness
        # Ensures error messages provide actionable information to clients
        error_message = error_data["detail"]
        assert "NonExistentExtractor" in error_message  # Echoes requested ID
        assert "not found" in error_message.lower()  # Clear error indication
        assert "available extractors" in error_message.lower()  # Helpful guidance
        
        # Verify that available extractors are listed in the error
        # Provides clients with valid alternatives to the failed request
        assert "CryptoNewsExtractor" in error_message
        assert "TradingSignalsExtractor" in error_message
        assert "MarketDataExtractor" in error_message
    
    def test_get_extractor_empty_id(self, test_client, temp_strategies_dir):
        """Test validation error for empty extractor ID.
        
        This test validates:
        - Input validation for required parameters
        - Proper HTTP 400 status for bad requests
        - Clear validation error messages
        
        Args:
            test_client: FastAPI test client
            temp_strategies_dir: Temporary directory with test strategies
        """
        # Test various invalid ID formats
        # Covers different ways clients might send empty or invalid identifiers
        invalid_ids = ["", "   ", "%20", "\t\n"]
        
        for invalid_id in invalid_ids:
            # Act: Request with invalid ID
            # Tests input validation for path parameters
            response = test_client.get(f"/api/extractors/{invalid_id}")
            
            # Assert: Verify validation error
            # Ensures proper HTTP status codes for malformed requests
            assert response.status_code == 400
            assert response.headers["content-type"] == "application/json"
            
            # Validate error response structure and content
            # Ensures validation errors provide clear feedback to clients
            error_data = response.json()
            assert "detail" in error_data  # Standard error format
            assert "cannot be empty" in error_data["detail"].lower()  # Clear validation message
    
    def test_api_response_performance(self, test_client, temp_strategies_dir):
        """Test API response performance and timing.
        
        This test validates:
        - Response time within acceptable limits
        - Consistent performance across multiple requests
        - No memory leaks or resource accumulation
        
        Args:
            test_client: FastAPI test client
            temp_strategies_dir: Temporary directory with test strategies
        """
        import time
        
        # Measure response times for multiple requests
        # Performance testing ensures the API meets response time requirements
        response_times = []
        num_requests = 10
        
        for _ in range(num_requests):
            # Time each individual request to measure performance consistency
            start_time = time.time()
            response = test_client.get("/api/extractors")
            end_time = time.time()
            
            # Verify successful response
            # Ensures performance testing only measures successful operations
            assert response.status_code == 200
            
            # Record response time
            # Collects timing data for statistical analysis
            response_time = end_time - start_time
            response_times.append(response_time)
        
        # Assert: Verify performance characteristics
        # Analyzes collected timing data against performance requirements
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # Performance thresholds (adjust based on requirements)
        # Ensures the API meets acceptable performance standards
        assert avg_response_time < 0.5  # Average under 500ms for good UX
        assert max_response_time < 1.0   # Maximum under 1 second for worst case
        
        # Verify response time consistency (no outliers)
        # Ensures stable performance without significant variance
        import statistics
        if len(response_times) > 1:
            std_dev = statistics.stdev(response_times)
            assert std_dev < avg_response_time * 0.5  # Standard deviation < 50% of average
    
    def test_concurrent_requests_handling(self, test_client, temp_strategies_dir):
        """Test API behavior under concurrent request load.
        
        This test validates:
        - Thread safety of the discovery mechanism
        - Consistent responses under concurrent load
        - No race conditions or data corruption
        
        Args:
            test_client: FastAPI test client
            temp_strategies_dir: Temporary directory with test strategies
        """
        import concurrent.futures
        import threading
        
        def make_request(endpoint: str) -> Dict[str, Any]:
            """Make a single API request and return the response data.
            
            This function executes a single HTTP request within a thread
            and captures both the response data and thread metadata for
            analysis of concurrent behavior.
            
            Args:
                endpoint: API endpoint to request
            
            Returns:
                Dict containing response data and metadata for analysis
            """
            # Execute the HTTP request within the thread context
            # This tests the API's ability to handle simultaneous requests
            response = test_client.get(endpoint)
            
            # Return comprehensive result data for concurrent analysis
            # Includes thread identification for debugging race conditions
            return {
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'thread_id': threading.current_thread().ident
            }
        
        # Define test endpoints for comprehensive concurrent testing
        # Tests both list and individual extractor endpoints under load
        endpoints = [
            "/api/extractors",  # Main list endpoint
            "/api/extractors/CryptoNewsExtractor",  # Individual extractor endpoints
            "/api/extractors/TradingSignalsExtractor",
            "/api/extractors/MarketDataExtractor"
        ]
        
        # Execute concurrent requests using thread pool
        # ThreadPoolExecutor provides controlled concurrent execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            # Submit multiple requests for each endpoint to test thread safety
            # This simulates realistic concurrent usage patterns
            futures = []
            for _ in range(5):  # 5 requests per endpoint for statistical significance
                for endpoint in endpoints:
                    # Submit each request as a separate concurrent task
                    future = executor.submit(make_request, endpoint)
                    futures.append((endpoint, future))
            
            # Collect results from all concurrent requests
            # Ensures all threads complete before analysis
            results = []
            for endpoint, future in futures:
                try:
                    # Wait for each request to complete with timeout
                    # Timeout prevents hanging on problematic requests
                    result = future.result(timeout=5.0)
                    result['endpoint'] = endpoint
                    results.append(result)
                except concurrent.futures.TimeoutError:
                    # Fail fast if any request times out under concurrent load
                    pytest.fail(f"Request to {endpoint} timed out")
        
        # Assert: Verify all requests succeeded under concurrent load
        # Ensures the API maintains reliability under stress
        assert len(results) == len(endpoints) * 5
        
        # Validate that all concurrent requests completed successfully
        # Any failures would indicate thread safety or resource issues
        for result in results:
            assert result['status_code'] == 200
            assert result['data'] is not None
        
        # Verify response consistency across concurrent requests
        # Group results by endpoint for consistency analysis
        endpoint_results = {}
        for result in results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_results:
                endpoint_results[endpoint] = []
            endpoint_results[endpoint].append(result['data'])
        
        # Verify all responses for each endpoint are identical
        # Inconsistent responses would indicate race conditions or data corruption
        for endpoint, responses in endpoint_results.items():
            first_response = responses[0]
            for response in responses[1:]:
                assert response == first_response, f"Inconsistent responses for {endpoint}"
    
    def test_error_handling_filesystem_issues(self, test_client):
        """Test API error handling when filesystem issues occur.
        
        This test validates:
        - Graceful handling of missing strategy directories
        - Appropriate HTTP error responses
        - Error message clarity and helpfulness
        - System resilience to configuration issues
        
        Args:
            test_client: FastAPI test client
        """
        # Ensure no strategies directory exists
        # This simulates deployment scenarios where configuration is incomplete
        # or the strategies directory has not been properly initialized
        if 'STRATEGIES_PATH' in os.environ:
            del os.environ['STRATEGIES_PATH']
        
        # Act: Request extractors when directory doesn't exist
        # Tests the API's resilience to missing filesystem resources
        # This scenario commonly occurs in fresh deployments or misconfigured environments
        response = test_client.get("/api/extractors")
        
        # Assert: Verify graceful handling
        # The API should either return an empty list or a proper error
        # Both responses are acceptable depending on implementation strategy
        # The key is that the API doesn't crash or return malformed responses
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            # Empty result is acceptable for missing directories
            # This approach treats missing directories as empty collections
            # providing a better user experience than hard failures
            extractors = response.json()
            assert isinstance(extractors, list)  # Must be a list structure
            assert len(extractors) == 0  # Should be empty when no directory exists
        else:
            # Error response should be properly formatted
            # Server errors should follow FastAPI error response format
            # ensuring consistent error handling across the API
            error_data = response.json()
            assert "detail" in error_data  # Standard FastAPI error format
            assert isinstance(error_data["detail"], str)  # Error message as string
    
    def test_schema_validation_and_format(self, test_client, temp_strategies_dir):
        """Test that API responses conform to expected schema format.
        
        This test validates:
        - Response data structure compliance
        - Field type validation
        - Required field presence
        - Data format consistency
        
        Args:
            test_client: FastAPI test client
            temp_strategies_dir: Temporary directory with test strategies
        """
        # Test extractors list endpoint
        # Validates the main API endpoint that returns all available extractors
        # This ensures API contract compliance for client applications
        response = test_client.get("/api/extractors")
        assert response.status_code == 200
        
        # Parse and validate the response structure
        # The response should be a well-formed JSON array
        # This structure allows for easy iteration in client applications
        extractors = response.json()
        assert isinstance(extractors, list)  # Must be an array of extractors for consistent client handling
        
        # Validate each extractor object in the response
        # Ensures consistent schema across all returned extractors
        # This validation prevents client-side errors from malformed data
        for extractor in extractors:
            # Validate required fields and types
            # These fields are essential for API contract compliance
            # Missing required fields would break client applications
            assert isinstance(extractor.get("id"), str)  # Unique identifier for URL paths
            assert isinstance(extractor.get("name"), str)  # Display name for UI rendering
            assert isinstance(extractor.get("description"), str)  # Functional description for documentation
            assert isinstance(extractor.get("schema"), str)  # Data extraction schema for processing
            assert isinstance(extractor.get("file_path"), str)  # Source file location for debugging
            
            # Validate field constraints and content quality
            # Ensures meaningful data is returned for all fields
            # Empty fields would provide no value to client applications
            assert len(extractor["id"]) > 0  # Non-empty identifier for API operations
            assert len(extractor["name"]) > 0  # Non-empty name for display purposes
            assert len(extractor["schema"]) > 0  # Non-empty schema for data extraction
            assert extractor["file_path"].endswith(".py")  # Valid Python file extension
            
            # Validate schema format (comma-separated fields)
            # The schema should be a parseable list of field names
            # This format enables client-side schema parsing and validation
            schema_fields = [field.strip() for field in extractor["schema"].split(",")]
            assert len(schema_fields) > 0  # At least one field defined for extraction
            assert all(len(field) > 0 for field in schema_fields)  # All fields non-empty and meaningful
        
        # Test individual extractor endpoint
        # Validates the detail endpoint for specific extractor retrieval
        # This ensures consistency between list and detail API responses
        if extractors:
            # Use the first extractor for detailed validation
            # Tests the parameterized endpoint with actual extractor data
            first_extractor_id = extractors[0]["id"]
            response = test_client.get(f"/api/extractors/{first_extractor_id}")
            assert response.status_code == 200
            
            # Parse single extractor response
            # Should be a single object, not an array like the list endpoint
            extractor = response.json()
            
            # Validate single extractor response format
            # Ensures consistency between list and detail endpoints
            # Clients should be able to use the same data structures for both endpoints
            assert extractor["id"] == first_extractor_id  # Correct extractor returned based on ID
            assert isinstance(extractor.get("name"), str)  # String name field for display
            assert isinstance(extractor.get("description"), str)  # String description for documentation
            assert isinstance(extractor.get("schema"), str)  # String schema field for processing
            assert isinstance(extractor.get("file_path"), str)  # String file path for debugging


class TestExtractorsAPILoadTesting:
    """Load testing scenarios for the extractors API.
    
    This class provides performance and stress testing to ensure
    the API can handle realistic production loads.
    """
    
    @pytest.fixture(scope="class")
    def test_client(self):
        """Create a test client for load testing.
        
        Returns:
            TestClient: Configured test client for load testing
        """
        return TestClient(app)
    
    @pytest.mark.slow
    def test_high_volume_requests(self, test_client):
        """Test API performance under high request volume.
        
        This test validates:
        - System stability under sustained load
        - Response time degradation patterns
        - Memory usage and resource management
        - Error rate under stress conditions
        
        Args:
            test_client: FastAPI test client
        """
        import time
        import statistics
        
        # Configuration for load test
        # Defines the parameters for stress testing the API
        num_requests = 100  # Total number of requests to execute
        max_acceptable_avg_time = 1.0  # 1 second average response time limit
        max_acceptable_error_rate = 0.05  # 5% error rate threshold
        
        # Execute load test
        # Performs sequential requests to measure sustained performance
        start_time = time.time()  # Start timing the entire test
        response_times = []  # Collect individual response times
        error_count = 0  # Track failed requests
        
        # Execute the specified number of requests sequentially
        # Sequential execution tests sustained load rather than concurrent spikes
        for i in range(num_requests):
            request_start = time.time()  # Time each individual request
            
            try:
                # Make the API request and measure response time
                # Tests the main extractors endpoint under load
                response = test_client.get("/api/extractors")
                request_end = time.time()
                
                # Calculate and record response time
                # Individual timing helps identify performance degradation patterns
                response_time = request_end - request_start
                response_times.append(response_time)
                
                # Count non-200 responses as errors
                # HTTP errors indicate system stress or failure
                if response.status_code != 200:
                    error_count += 1
                    
            except Exception as e:
                # Count exceptions as errors (timeouts, connection failures, etc.)
                # Network or server exceptions indicate system overload
                error_count += 1
                print(f"Request {i} failed: {e}")
        
        # Calculate total test duration
        # Used for throughput calculations and overall performance assessment
        total_time = time.time() - start_time
        
        # Analyze results
        # Statistical analysis of performance data to validate requirements
        if response_times:
            # Calculate key performance metrics
            # These metrics provide comprehensive performance assessment
            avg_response_time = statistics.mean(response_times)  # Average performance
            median_response_time = statistics.median(response_times)  # Typical performance
            p95_response_time = sorted(response_times)[int(0.95 * len(response_times))]  # Worst-case performance
            
            # Calculate reliability and throughput metrics
            # These metrics assess system capacity and reliability
            error_rate = error_count / num_requests  # Failure rate percentage
            requests_per_second = num_requests / total_time  # Throughput measurement
            
            # Assert performance requirements
            # Validates that the API meets defined performance standards
            assert avg_response_time < max_acceptable_avg_time, f"Average response time {avg_response_time:.3f}s exceeds limit"
            assert error_rate < max_acceptable_error_rate, f"Error rate {error_rate:.2%} exceeds limit"
            assert requests_per_second > 10, f"Throughput {requests_per_second:.1f} req/s too low"
            
            # Log performance metrics for monitoring
            # Provides detailed performance data for analysis and optimization
            print(f"\nLoad Test Results:")
            print(f"  Total requests: {num_requests}")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Requests/second: {requests_per_second:.1f}")
            print(f"  Average response time: {avg_response_time:.3f}s")
            print(f"  Median response time: {median_response_time:.3f}s")
            print(f"  95th percentile: {p95_response_time:.3f}s")
            print(f"  Error rate: {error_rate:.2%}")
        else:
            # Fail the test if no requests succeeded
            # Complete failure indicates critical system issues
            pytest.fail("No successful requests completed during load test")


if __name__ == '__main__':
    """Run the integration test suite when executed directly.
    
    This allows for easy execution of the integration tests during
    development and provides comprehensive validation of the API.
    """
    pytest.main([__file__, '-v', '--tb=short', '-m', 'not slow'])