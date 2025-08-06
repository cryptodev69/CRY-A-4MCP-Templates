#!/usr/bin/env python3
"""
Test script to verify the extract method works with named parameters using mocked API responses.
"""

import json
import unittest
from unittest.mock import patch, AsyncMock

from src.cry_a_4mcp.crawl4ai.extraction_strategies.crypto.xcryptohunter_llm import XCryptoHunterLLMExtractionStrategy
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper

# Sample mock response data
MOCK_API_RESPONSE = {
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

# Create a simple test function that doesn't use unittest
def test_extract_with_named_params():
    # Create a strategy instance
    strategy = XCryptoHunterLLMExtractionStrategy(provider='openrouter', api_token='test_token')
    
    # Wrap it with the synchronous wrapper
    sync_strategy = SyncExtractionStrategyWrapper(strategy)
    
    print('Testing extract method with named parameters (mocked API)...')
    
    # Patch the retry_async function to return our mock response
    with patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.retry_async') as mock_retry:
        # Configure the mock to return our mock API response
        async def mock_api_call(*args, **kwargs):
            return MOCK_API_RESPONSE
        
        mock_retry.side_effect = mock_api_call
        
        try:
            # Test with named parameters
            result = sync_strategy.extract(url='https://example.com', content='Test content')
            print('Extract method called successfully with named parameters')
            print(f'Result: {json.dumps(result, indent=2)}')
            
            # Verify the result contains expected fields
            assert 'tweet_metadata' in result, "Missing tweet_metadata in result"
            assert 'crypto_tokens' in result, "Missing crypto_tokens in result"
            assert result['crypto_tokens'][0]['ticker_symbol'] == 'BTC', "Incorrect ticker symbol"
            
            print("All assertions passed!")
            return True
            
        except Exception as e:
            print(f'Error: Extract method failed with exception: {e}')
            import traceback
            traceback.print_exc()
            return False

# Run the test if this script is executed directly
if __name__ == '__main__':
    success = test_extract_with_named_params()
    if not success:
        exit(1)