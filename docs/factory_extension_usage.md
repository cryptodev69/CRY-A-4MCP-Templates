# Factory Extension Usage Guide

## Overview

The `factory_extension` module extends the `StrategyFactory` class with a `create_strategy` method that simplifies the creation of strategy instances with specific provider, model, and API key parameters. It now uses OpenRouter with the DeepSeek model (deepseek/deepseek-chat-v3-0324:free) as the default provider and model.

## Usage

The `create_strategy` method is automatically added to the `StrategyFactory` class when the extraction strategies package is imported. You can use it as follows:

```python
from src.cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory

# Create a strategy instance with default provider (openrouter) and model (deepseek/deepseek-chat-v3-0324:free)
strategy = StrategyFactory.create_strategy(
    "CryptoLLMExtractionStrategy",
    api_key="your-api-key"
)

# Or create a strategy instance with specific provider, model, and API key
strategy = StrategyFactory.create_strategy(
    "CryptoLLMExtractionStrategy",
    provider="openai",
    model="gpt-4",
    api_key="your-api-key"
)

# Use the strategy
result = strategy.extract(content)
```

## Parameters

- `strategy_class_name`: Name of the strategy class to create (e.g., "CryptoLLMExtractionStrategy")
- `provider`: LLM provider (e.g., "openai", "anthropic", "groq"). Defaults to "openrouter" if not specified.
- `model`: LLM model name (e.g., "gpt-4", "claude-3-opus"). Defaults to "deepseek/deepseek-chat-v3-0324:free" if not specified.
- `api_key`: API key for the provider

## Supported Strategies

The `create_strategy` method works with all registered extraction strategies, including:

- `CryptoLLMExtractionStrategy`: Specialized extraction strategy for cryptocurrency content
- `NFTLLMExtractionStrategy`: Specialized extraction strategy for NFT content
- `XCryptoHunterLLMExtractionStrategy`: Specialized extraction strategy for cryptocurrency gem hunters
- `FinancialLLMExtractionStrategy`: Specialized extraction strategy for financial content
- `AcademicLLMExtractionStrategy`: Specialized extraction strategy for academic content
- `NewsLLMExtractionStrategy`: Specialized extraction strategy for news content
- `ProductLLMExtractionStrategy`: Specialized extraction strategy for product content
- `SocialMediaLLMExtractionStrategy`: Specialized extraction strategy for social media content

## Example: Creating Multiple Strategies

```python
from src.cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory

# Create a crypto strategy
crypto_strategy = StrategyFactory.create_strategy(
    "CryptoLLMExtractionStrategy",
    provider="openai",
    model="gpt-4",
    api_key="your-openai-api-key"
)

# Create an NFT strategy
nft_strategy = StrategyFactory.create_strategy(
    "NFTLLMExtractionStrategy",
    provider="anthropic",
    model="claude-3-opus",
    api_key="your-anthropic-api-key"
)

# Use the strategies
crypto_result = crypto_strategy.extract(crypto_content)
nft_result = nft_strategy.extract(nft_content)
```

## Integration with UI

The `create_strategy` method is used by the Strategy Manager UI to create strategy instances for testing and execution. It simplifies the process of creating strategy instances with specific provider, model, and API key parameters.