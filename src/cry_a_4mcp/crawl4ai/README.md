# Crawl4AI Extraction Strategies

## Overview

This package provides extraction strategies for processing web content using Large Language Models (LLMs). The strategies are designed to extract structured information from unstructured text, with a focus on cryptocurrency-related content.

## Key Features

### 1. Enhanced Error Handling and Logging

The improved extraction strategies include:

- **Custom exception types** for different error scenarios:
  - `ExtractionError`: Base exception for all extraction errors
  - `APIConnectionError`: For API connection issues
  - `APIResponseError`: For API response errors with status codes
  - `ContentParsingError`: For JSON parsing errors

- **Comprehensive logging** with different log levels:
  - INFO: General operation information
  - DEBUG: Detailed debugging information
  - WARNING: Potential issues that don't prevent operation
  - ERROR: Critical issues that prevent successful extraction

- **Automatic retries** with exponential backoff for transient errors

### 2. Performance Optimization

Performance improvements include:

- **Content truncation** to optimize token usage
- **Performance monitoring** with the `measure_performance` decorator
- **Metadata tracking** for extraction time and token usage
- **Configurable timeouts** to prevent hanging operations

### 3. Model and Provider Flexibility

The extraction strategies support multiple LLM providers and models:

- **Provider configuration registry** with default settings
- **Dynamic model selection** based on provider
- **Provider-specific headers** and authentication
- **Connection validation** to verify API access
- **Model capability awareness** (e.g., JSON output support)

## Usage

### Basic Usage

```python
import asyncio
from cry_a_4mcp.crawl4ai import ImprovedLLMExtractionStrategy

async def extract_content():
    strategy = ImprovedLLMExtractionStrategy(
        provider="openrouter",
        api_token="your_api_key",
        model="moonshotai/kimi-k2:free"
    )
    
    result = await strategy.extract(
        url="https://example.com/article",
        html="Article content here..."
    )
    
    print(result)

asyncio.run(extract_content())
```

### Cryptocurrency-Specific Extraction

```python
import asyncio
from cry_a_4mcp.crawl4ai import CryptoLLMExtractionStrategy

async def extract_crypto_content():
    strategy = CryptoLLMExtractionStrategy(
        provider="openrouter",
        api_token="your_api_key",
        model="moonshotai/kimi-k2:free"
    )
    
    result = await strategy.extract(
        url="https://example.com/crypto-news",
        html="Bitcoin has surpassed $60,000..."
    )
    
    print(result)

asyncio.run(extract_crypto_content())
```

### Error Handling

```python
import asyncio
from cry_a_4mcp.crawl4ai import (
    CryptoLLMExtractionStrategy,
    APIConnectionError,
    APIResponseError,
    ContentParsingError
)

async def extract_with_error_handling():
    try:
        strategy = CryptoLLMExtractionStrategy(
            provider="openrouter",
            api_token="your_api_key"
        )
        
        result = await strategy.extract(
            url="https://example.com/article",
            html="Article content here..."
        )
        
        print(result)
        
    except APIConnectionError as e:
        print(f"Connection error: {e}")
    except APIResponseError as e:
        print(f"API error {e.status_code}: {e.message}")
    except ContentParsingError as e:
        print(f"Parsing error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(extract_with_error_handling())
```

## Available Providers and Models

You can get a list of available providers and models programmatically:

```python
from cry_a_4mcp.crawl4ai import ImprovedLLMExtractionStrategy

# Get available providers
providers = ImprovedLLMExtractionStrategy.get_available_providers()
print(f"Available providers: {providers}")

# Get available models for a provider
openrouter_models = ImprovedLLMExtractionStrategy.get_available_models("openrouter")
print(f"Available OpenRouter models: {openrouter_models}")
```

## Testing

A test script is provided to demonstrate the enhanced features:

```bash
python test_improved_crypto_extraction.py
```

This script tests:
1. Provider and model flexibility
2. Error handling capabilities
3. Performance optimization features