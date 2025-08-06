# Testing Extraction Strategies

This document provides guidance on testing the extraction strategies in the CRY-A-4MCP-Templates project, particularly focusing on testing with mocked API responses to avoid making actual API calls during testing.

## Overview

The extraction strategies in this project rely on external LLM APIs (like OpenAI, OpenRouter, etc.) to process content. When testing these strategies, it's often preferable to use mocked API responses rather than making actual API calls for several reasons:

1. **Cost efficiency**: Avoid incurring API usage costs during testing
2. **Reliability**: Tests don't depend on external services being available
3. **Speed**: Tests run faster without waiting for API responses
4. **Consistency**: Tests produce the same results every time

## Available Test Scripts

### 1. Simple Mock Test (`test_extract_params_mock.py`)

This script demonstrates a simple approach to testing the extraction strategy with a mocked API response. It patches the `retry_async` function in the base class to return a predefined mock response.

```python
with patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.retry_async') as mock_retry:
    async def mock_api_call(*args, **kwargs):
        return MOCK_API_RESPONSE
    
    mock_retry.side_effect = mock_api_call
    
    # Test with named parameters
    result = sync_strategy.extract(url='https://example.com', content='Test content')
```

### 2. Comprehensive Test Suite (`test_extraction_strategy_comprehensive.py`)

This script provides a more comprehensive test suite that covers various aspects of the extraction strategies:

- Basic extraction with valid responses
- Error handling for API failures
- Handling of malformed API responses
- Testing with different content types

## How to Run Tests

### Running the Simple Mock Test

```bash
python test_extract_params_mock.py
```

### Running the Comprehensive Test Suite

```bash
python test_extraction_strategy_comprehensive.py
```

### Running with unittest

You can also run the comprehensive test suite using the unittest framework:

```bash
python -m unittest test_extraction_strategy_comprehensive.py
```

## Mocking Approaches

### 1. Patching the `retry_async` Function

The most effective approach is to patch the `retry_async` function in the base class, which is responsible for making the actual API calls. This allows you to intercept the API call and return a predefined response.

```python
@patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.retry_async')
def test_successful_extraction(self, mock_retry):
    async def mock_success(*args, **kwargs):
        return SUCCESS_RESPONSE
    
    mock_retry.side_effect = mock_success
    
    # Test with named parameters
    result = self.sync_strategy.extract(url='https://example.com', content='Test content')
```

### 2. Simulating Error Conditions

You can also simulate error conditions by configuring the mock to raise exceptions:

```python
@patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.retry_async')
def test_api_error_handling(self, mock_retry):
    async def mock_api_error(*args, **kwargs):
        raise APIResponseError(401, "The API key provided is invalid")
    
    mock_retry.side_effect = mock_api_error
    
    # Test that the error is properly propagated
    with self.assertRaises(APIResponseError) as context:
        self.sync_strategy.extract(url='https://example.com', content='Test content')
```

## Creating Mock Responses

When creating mock responses, it's important to match the structure of the actual API responses. Here's an example of a mock response for the OpenRouter API:

```python
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
                    "platform": "Twitter"
                },
                "crypto_tokens": [
                    {
                        "name": "Bitcoin",
                        "ticker_symbol": "BTC",
                        "blockchain": "Bitcoin",
                        "mention_context": "positive"
                    }
                ]
            })
        },
        "finish_reason": "stop",
        "index": 0
    }]
}
```

## Best Practices

1. **Mock at the right level**: Patch the function that makes the actual API call rather than trying to mock the HTTP client directly
2. **Match response structure**: Ensure your mock responses match the structure of the actual API responses
3. **Test error handling**: Include tests for various error conditions to ensure your code handles them gracefully
4. **Use descriptive test names**: Make your test names descriptive so it's clear what each test is checking
5. **Isolate tests**: Each test should be independent and not rely on the state from previous tests

## Troubleshooting

### Common Issues

1. **Incorrect patching path**: Ensure you're patching the correct function path
2. **Mismatched response structure**: Make sure your mock response structure matches what the code expects
3. **Async/await issues**: Remember that you're testing async code, so your mock functions should also be async

### Debugging Tips

1. Use `print` statements or logging to see what's happening inside your tests
2. Check the actual API response structure if you're unsure about the format
3. Use the `unittest.mock` module's `call_args` and `call_args_list` attributes to inspect how your mocked function was called