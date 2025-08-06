# Migration Guide: Transitioning to the New Extraction Strategies Framework

This guide provides instructions for migrating existing extraction code to the new extraction strategies framework. The new framework offers improved organization, extensibility, and maintainability for extraction logic.

## Table of Contents

1. [Overview of Changes](#overview-of-changes)
2. [Benefits of Migration](#benefits-of-migration)
3. [Step-by-Step Migration Process](#step-by-step-migration-process)
4. [Migration Examples](#migration-examples)
5. [Troubleshooting](#troubleshooting)

## Overview of Changes

The new extraction strategies framework introduces several architectural improvements:

- **Modular Organization**: Domain-specific extraction logic is now organized into separate modules.
- **Strategy Pattern**: Extraction logic is encapsulated in strategy classes with a consistent interface.
- **Registry System**: Strategies are registered in a central registry for discovery and management.
- **Factory Pattern**: A factory creates strategy instances based on configuration.
- **Composite Strategies**: Multiple strategies can be combined for complex extraction needs.
- **UI Integration**: A web-based UI for managing and testing strategies.

## Benefits of Migration

Migrating to the new framework provides several benefits:

- **Improved Maintainability**: Domain-specific logic is isolated, making it easier to maintain.
- **Enhanced Extensibility**: Adding new extraction capabilities is simpler with the strategy pattern.
- **Better Testing**: Strategies can be tested in isolation with clear boundaries.
- **Configuration Flexibility**: Strategies can be configured and combined at runtime.
- **UI Management**: Strategies can be managed through a user-friendly web interface.
- **Standardized Error Handling**: Consistent error handling across all strategies.

## Step-by-Step Migration Process

### 1. Identify Existing Extraction Logic

First, identify the extraction logic in your existing codebase:

```bash
# Example command to find extraction-related files
find . -name "*.py" -exec grep -l "extract" {} \;
```

### 2. Categorize Extraction Logic by Domain

Categorize your extraction logic by domain (e.g., crypto, news, financial, social media).

### 3. Create Domain-Specific Strategy Classes

For each domain, create a new strategy class that extends the appropriate base class:

```python
# Before: Standalone extraction function
def extract_crypto_data(content, api_key):
    # Extraction logic here
    return extracted_data

# After: Strategy class
from cry_a_4mcp.crawl4ai.extraction_strategies.base import LLMExtractionStrategy
from cry_a_4mcp.crawl4ai.extraction_strategies.registry import register_strategy

@register_strategy(
    name="MyCryptoExtractionStrategy",
    description="Extracts cryptocurrency information",
    category="crypto"
)
class MyCryptoExtractionStrategy(LLMExtractionStrategy):
    def __init__(self, api_token=None, model=None, **kwargs):
        # Initialize with appropriate schema and instruction
        super().__init__(
            provider="openai",
            api_token=api_token,
            model=model,
            schema=MY_CRYPTO_SCHEMA,
            instruction=MY_CRYPTO_INSTRUCTION,
            **kwargs
        )
    
    async def extract(self, url, content, **kwargs):
        # Call the base extraction method
        result = await super().extract(url, content, **kwargs)
        
        # Add domain-specific post-processing
        result = self._validate_crypto_extraction(result)
        result = self._enhance_crypto_extraction(result, url)
        
        return result
    
    def _validate_crypto_extraction(self, result):
        # Validation logic
        return result
    
    def _enhance_crypto_extraction(self, result, url):
        # Enhancement logic
        return result
```

### 4. Define JSON Schemas and Instructions

Define JSON schemas and instructions for each strategy:

```python
MY_CRYPTO_SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {"type": "string", "description": "The main headline or title"},
        "summary": {"type": "string", "description": "A brief summary of the content"},
        # Add more properties as needed
    },
    "required": ["headline", "summary"]
}

MY_CRYPTO_INSTRUCTION = """
    Extract key information from the provided cryptocurrency content.
    Focus on identifying cryptocurrencies, blockchain projects, market data,
    and key events mentioned in the content.
"""
```

### 5. Register Strategies

Ensure your strategies are registered with the registry:

```python
# This is handled by the @register_strategy decorator
# Make sure your strategy modules are imported somewhere in your application
```

### 6. Update Client Code

Update client code to use the new framework:

```python
# Before: Direct function call
result = extract_crypto_data(content, api_key)

# After: Using the factory and strategy
from cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory

factory = StrategyFactory()
strategy = factory.create_strategy(
    "MyCryptoExtractionStrategy",
    api_token=api_key,
    model="gpt-4"
)
result = await strategy.extract(url, content)
```

### 7. Test the Migration

Test the migrated code to ensure it produces the same results as the original code.

## Migration Examples

### Example 1: Simple LLM-based Extraction

#### Before:

```python
def extract_with_llm(content, api_key):
    prompt = f"Extract information from: {content}"
    response = call_openai_api(prompt, api_key)
    return parse_response(response)
```

#### After:

```python
from cry_a_4mcp.crawl4ai.extraction_strategies.base import LLMExtractionStrategy
from cry_a_4mcp.crawl4ai.extraction_strategies.registry import register_strategy

@register_strategy(
    name="GenericLLMExtractionStrategy",
    description="Generic LLM-based extraction",
    category="general"
)
class GenericLLMExtractionStrategy(LLMExtractionStrategy):
    def __init__(self, api_token=None, model=None, **kwargs):
        schema = {
            "type": "object",
            "properties": {
                "main_topic": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}},
                "entities": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        instruction = "Extract the main topic, key points, and entities from the content."
        
        super().__init__(
            provider="openai",
            api_token=api_token,
            model=model,
            schema=schema,
            instruction=instruction,
            **kwargs
        )
```

### Example 2: Composite Strategy

#### Before:

```python
def extract_comprehensive(content, api_key):
    crypto_data = extract_crypto_data(content, api_key)
    news_data = extract_news_data(content, api_key)
    
    # Merge results
    result = {}
    result.update(crypto_data)
    result.update(news_data)
    return result
```

#### After:

```python
from cry_a_4mcp.crawl4ai.extraction_strategies.factory import StrategyFactory
from cry_a_4mcp.crawl4ai.extraction_strategies.composite import ComprehensiveLLMExtractionStrategy

# Create a composite strategy
strategy = ComprehensiveLLMExtractionStrategy(
    api_token=api_key,
    model="gpt-4",
    strategies=["CryptoLLMExtractionStrategy", "NewsLLMExtractionStrategy"],
    merge_mode="smart"
)

# Extract information
result = await strategy.extract(url, content)
```

## Troubleshooting

### Common Issues

1. **Strategy Not Found**: Ensure the strategy is properly registered and imported.

   ```python
   # Check if strategy is registered
   from cry_a_4mcp.crawl4ai.extraction_strategies.registry import StrategyRegistry
   registry = StrategyRegistry()
   print(registry.get_all())
   ```

2. **API Key Issues**: Verify that API keys are correctly passed to the strategy.

3. **Schema Validation Errors**: Check that your extraction results match the defined schema.

4. **Performance Issues**: Consider using async methods for better performance with multiple strategies.

### Getting Help

If you encounter issues during migration, please:

1. Check the documentation in the `docs` directory.
2. Look at the example strategies in the `examples` directory.
3. Run the test suite to verify your implementation.
4. Contact the development team for assistance.

---

By following this guide, you should be able to successfully migrate your existing extraction code to the new framework. The migration process may require some initial effort, but the benefits in terms of maintainability, extensibility, and functionality will be worth it in the long run.