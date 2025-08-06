#!/usr/bin/env python3
"""
Comprehensive test suite for extraction strategies with mocked API responses.

This script tests various aspects of the extraction strategies:
1. Basic extraction with named parameters
2. Error handling for API failures
3. Handling of malformed API responses
4. Testing with different content types
"""

import json
import unittest
from unittest.mock import patch, AsyncMock

from src.cry_a_4mcp.crawl4ai.extraction_strategies.crypto.xcryptohunter_llm import XCryptoHunterLLMExtractionStrategy
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper
from src.cry_a_4mcp.crawl4ai.extraction_strategies.base import APIResponseError, APIConnectionError, ContentParsingError

# Sample mock response data for successful extraction
SUCCESS_RESPONSE = {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677858242,
    "model": "moonshotai/kimi-k2:free",
    "usage": {
        "prompt_tokens": 13,
        "completion_tokens": 7,
        "total_tokens": 20
    },
    "choices": [{
        "message": {
            "role": "assistant",
            "content": json.dumps({
                "tweet_metadata": {
                    "author": "CryptoAnalyst",
                    "timestamp": "2023-07-15T10:30:00Z",
                    "platform": "Twitter",
                    "engagement": {
                        "likes": 150,
                        "retweets": 45,
                        "comments": 20
                    }
                },
                "crypto_tokens": [
                    {
                        "name": "Bitcoin",
                        "ticker_symbol": "BTC",
                        "contract_address": "",
                        "blockchain": "Bitcoin",
                        "market_cap_category": "large",
                        "mention_context": "positive"
                    }
                ],
                "_metadata": {
                    "extraction_timestamp": 1677858242
                }
            })
        },
        "finish_reason": "stop",
        "index": 0
    }]
}

# Sample mock response with malformed JSON in content
MALFORMED_RESPONSE = {
    "id": "chatcmpl-456",
    "object": "chat.completion",
    "created": 1677858242,
    "model": "moonshotai/kimi-k2:free",
    "usage": {
        "prompt_tokens": 13,
        "completion_tokens": 7,
        "total_tokens": 20
    },
    "choices": [{
        "message": {
            "role": "assistant",
            "content": "This is not valid JSON data"
        },
        "finish_reason": "stop",
        "index": 0
    }]
}

# Sample error response
ERROR_RESPONSE = {
    "error": {
        "message": "The API key provided is invalid",
        "code": 401
    }
}

class TestExtractionStrategy(unittest.TestCase):
    
    def setUp(self):
        # Create a strategy instance for each test
        self.strategy = XCryptoHunterLLMExtractionStrategy(provider='openrouter', api_token='test_token')
        self.sync_strategy = SyncExtractionStrategyWrapper(self.strategy)
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.retry_async')
    def test_successful_extraction(self, mock_retry):
        """Test successful extraction with valid response"""
        # Configure the mock to return success response
        async def mock_success(*args, **kwargs):
            return SUCCESS_RESPONSE
        
        mock_retry.side_effect = mock_success
        
        # Test with named parameters
        result = self.sync_strategy.extract(url='https://example.com', content='Test content')
        
        # Verify the result contains expected fields
        self.assertIn('tweet_metadata', result)
        self.assertIn('crypto_tokens', result)
        self.assertEqual(result['crypto_tokens'][0]['ticker_symbol'], 'BTC')
        
        # Verify metadata was added
        self.assertIn('_metadata', result)
        self.assertIn('model', result['_metadata'])
        self.assertIn('usage', result['_metadata'])
        self.assertIn('timestamp', result['_metadata'])
        self.assertIn('performance', result['_metadata'])
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.retry_async')
    def test_api_error_handling(self, mock_retry):
        """Test handling of API errors"""
        # Configure the mock to raise an APIResponseError
        async def mock_api_error(*args, **kwargs):
            raise APIResponseError(401, "The API key provided is invalid")
        
        mock_retry.side_effect = mock_api_error
        
        # Test that the error is properly propagated
        with self.assertRaises(APIResponseError) as context:
            self.sync_strategy.extract(url='https://example.com', content='Test content')
        
        # Verify error details
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.message, "The API key provided is invalid")
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.retry_async')
    def test_connection_error_handling(self, mock_retry):
        """Test handling of connection errors"""
        # Configure the mock to raise an APIConnectionError
        async def mock_connection_error(*args, **kwargs):
            raise APIConnectionError("Failed to connect to API")
        
        mock_retry.side_effect = mock_connection_error
        
        # Test that the error is properly propagated
        with self.assertRaises(APIConnectionError) as context:
            self.sync_strategy.extract(url='https://example.com', content='Test content')
        
        # Verify error message
        self.assertIn("Failed to connect to API", str(context.exception))
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.retry_async')
    def test_malformed_response_handling(self, mock_retry):
        """Test handling of malformed JSON in API response"""
        # Configure the mock to return malformed response
        async def mock_malformed(*args, **kwargs):
            return MALFORMED_RESPONSE
        
        mock_retry.side_effect = mock_malformed
        
        # Test that ContentParsingError is raised
        with self.assertRaises(ContentParsingError):
            self.sync_strategy.extract(url='https://example.com', content='Test content')
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.retry_async')
    def test_different_content_types(self, mock_retry):
        """Test extraction with different content types"""
        # Configure the mock to return success response
        async def mock_success(*args, **kwargs):
            return SUCCESS_RESPONSE
        
        mock_retry.side_effect = mock_success
        
        # Test with HTML content
        html_content = "<html><body><h1>Crypto News</h1><p>Bitcoin price surges!</p></body></html>"
        result_html = self.sync_strategy.extract(url='https://example.com', content=html_content)
        self.assertIn('crypto_tokens', result_html)
        
        # Test with plain text content
        text_content = "Breaking: Bitcoin price reaches new all-time high!"
        result_text = self.sync_strategy.extract(url='https://example.com', content=text_content)
        self.assertIn('crypto_tokens', result_text)
        
        # Test with JSON content
        json_content = json.dumps({"headline": "Crypto Market Update", "body": "Bitcoin and Ethereum show strong gains."})
        result_json = self.sync_strategy.extract(url='https://example.com', content=json_content)
        self.assertIn('crypto_tokens', result_json)

# Run the tests if this script is executed directly
if __name__ == '__main__':
    unittest.main()