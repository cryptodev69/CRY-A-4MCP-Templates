# Synchronous Extraction Strategy Wrapper

This module provides a wrapper for asynchronous extraction strategies to make them usable in synchronous contexts, such as Streamlit UIs or other frameworks that don't natively support asynchronous code.

## Overview

The extraction strategies in this library are designed to be asynchronous by default, using Python's `async`/`await` syntax. This is optimal for high-performance applications, especially when making network requests to LLM APIs. However, there are many situations where you need to use these strategies in a synchronous context, such as:

- Streamlit UIs (like the Strategy Manager UI)
- Integration with synchronous libraries or frameworks
- Scripts that aren't designed to use asynchronous code

The `SyncExtractionStrategyWrapper` class provides a simple way to convert any asynchronous extraction strategy into a synchronous one.

## Usage

### Direct Usage

You can directly wrap any extraction strategy instance:

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import CryptoLLMExtractionStrategy
from cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper

# Create an asynchronous strategy
async_strategy = CryptoLLMExtractionStrategy(
    provider="openai",
    api_token="your-api-key",
    model="gpt-3.5-turbo"
)

# Wrap it with the synchronous wrapper
sync_strategy = SyncExtractionStrategyWrapper(async_strategy)

# Use it synchronously
result = sync_strategy.extract("https://example.com", "content to extract from")
```

### Using the Factory

The `StrategyFactory` class provides methods to create synchronized strategies directly:

```python
from cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory

# Create a synchronized strategy directly
sync_strategy = StrategyFactory.create_sync(
    "CryptoLLMExtractionStrategy",
    config={
        "api_token": "your-api-key",
        "provider": "openai",
        "model": "gpt-3.5-turbo"
    }
)

# Create from a configuration dictionary
config = {
    "strategy": "CryptoLLMExtractionStrategy",
    "config": {
        "api_token": "your-api-key",
        "provider": "openai",
        "model": "gpt-3.5-turbo"
    }
}
sync_strategy = StrategyFactory.create_from_config_sync(config)

# Create from a JSON string
json_config = '{"strategy": "CryptoLLMExtractionStrategy", "config": {"api_token": "your-api-key", "provider": "openai", "model": "gpt-3.5-turbo"}}'
sync_strategy = StrategyFactory.create_from_json_sync(json_config)

# Create a synchronized composite strategy
composite_config = [
    {
        "strategy": "CryptoLLMExtractionStrategy",
        "config": {"api_token": "your-api-key", "provider": "openai"}
    },
    {
        "strategy": "NewsLLMExtractionStrategy",
        "config": {"api_token": "your-api-key", "provider": "openai"}
    }
]
sync_composite = StrategyFactory.create_composite_sync(composite_config)
```

## Implementation Details

The wrapper works by creating a new event loop for each synchronous method call, running the asynchronous method to completion in that loop, and then returning the result. This approach ensures that the asynchronous code is properly executed in a synchronous context.

The wrapper provides synchronous versions of the following methods:

- `extract`: Extract information from content
- `validate_provider_connection`: Validate the connection to the LLM provider

## Example

See the `examples/sync_extraction_example.py` script for a complete example of using the synchronous wrapper.