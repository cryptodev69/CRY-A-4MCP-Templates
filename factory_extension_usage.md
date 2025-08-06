# Factory Extension Usage Guide

## Overview

The `factory_extension` module extends the `StrategyFactory` class with a simplified method for creating extraction strategy instances. This extension makes it easier to create strategies by providing a more intuitive interface and handling common configuration parameters.

## Key Features

- Simplified strategy creation with a single method call
- Default provider and model configuration
- Automatic handling of API key/token parameter differences
- Comprehensive error handling and logging

## Default Configuration

The `factory_extension` module comes with the following default configuration:

- **Default Provider**: `openrouter`
- **Default Model**: `deepseek/deepseek-chat-v3-0324:free`

These defaults are used when no provider or model is specified when calling `create_strategy`.

## Usage Examples

### Basic Usage

```python
from src.cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory

# Create a strategy with default provider (openrouter) and model (deepseek/deepseek-chat-v3-0324:free)
strategy = StrategyFactory.create_strategy(
    "CryptoLLMExtractionStrategy",
    api_key="your-api-key"
)
```

### Specifying Provider and Model

```python
from src.cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory

# Create a strategy with specific provider and model
strategy = StrategyFactory.create_strategy(
    "CryptoLLMExtractionStrategy",
    provider="openai",
    model="gpt-4",
    api_key="your-openai-api-key"
)
```

### Using Default Model with Specific Provider

```python
from src.cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory

# Create a strategy with openrouter provider and default model
strategy = StrategyFactory.create_strategy(
    "NFTLLMExtractionStrategy",
    provider="openrouter",
    api_key="your-openrouter-api-key"
)
```

## Parameters

- **strategy_class_name** (str): Name of the strategy class to create
- **provider** (str, optional): LLM provider (e.g., 'openai', 'anthropic', 'openrouter'). Defaults to 'openrouter'.
- **model** (str, optional): LLM model name. Defaults to 'deepseek/deepseek-chat-v3-0324:free' when provider is 'openrouter'.
- **api_key** (str, optional): API key for the provider

## Supported Strategies

The `create_strategy` method works with all registered extraction strategies, including:

- `CryptoLLMExtractionStrategy`
- `NFTLLMExtractionStrategy`
- `NewsLLMExtractionStrategy`
- `ProductLLMExtractionStrategy`
- `SocialMediaLLMExtractionStrategy`
- `FinancialLLMExtractionStrategy`
- `AcademicLLMExtractionStrategy`
- And more...

## Integration with UI

The factory extension is integrated with the Streamlit-based UI, allowing users to select providers and models through the interface. The UI will use the default provider and model when appropriate.

## Error Handling

The `create_strategy` method includes comprehensive error handling and will raise a `ValueError` with a descriptive message if strategy creation fails.