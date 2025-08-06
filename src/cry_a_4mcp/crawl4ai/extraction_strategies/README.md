# Extraction Strategies Framework

This directory contains the extraction strategies framework for the `cry_a_4mcp.crawl4ai` package. The framework provides a modular and extensible way to extract structured information from web content using various strategies, including LLM-based extraction.

## Overview

The extraction strategies framework is designed to be:

- **Modular**: Each strategy is a separate class that can be used independently.
- **Extensible**: New strategies can be easily added by subclassing the base classes.
- **Configurable**: Strategies can be configured with various parameters.
- **Discoverable**: Strategies can register themselves with the registry for dynamic discovery.
- **Composable**: Multiple strategies can be combined using the composite pattern.

## Directory Structure

```
extraction_strategies/
├── __init__.py                 # Package initialization and exports
├── base.py                     # Base classes for extraction strategies
├── registry.py                 # Registry system for strategy discovery
├── factory.py                  # Factory for creating strategy instances
├── crypto/                     # Cryptocurrency-specific strategies
│   ├── __init__.py             # Crypto package initialization
│   ├── crypto_llm.py           # Crypto LLM extraction strategy
│   └── xcryptohunterllmextractionstrategy_llm.py # Custom crypto strategy
├── news/                       # News-specific strategies
│   ├── __init__.py             # News package initialization
│   └── news_llm.py             # News LLM extraction strategy
├── financial/                  # Financial-specific strategies
│   ├── __init__.py             # Financial package initialization
│   └── financial_llm.py        # Financial LLM extraction strategy
├── social/                     # Social media-specific strategies
│   ├── __init__.py             # Social media package initialization
│   └── social_llm.py           # Social media LLM extraction strategy
├── academic/                   # Academic-specific strategies
│   ├── __init__.py             # Academic package initialization
│   └── academic_llm.py         # Academic LLM extraction strategy
├── product/                    # Product-specific strategies
│   ├── __init__.py             # Product package initialization
│   └── product_llm.py          # Product LLM extraction strategy
├── general/                    # General-purpose strategies
│   └── __init__.py             # General package initialization
├── composite/                  # Composite strategies
│   ├── __init__.py             # Composite package initialization
│   └── comprehensive_llm.py    # Comprehensive LLM extraction strategy
├── ui/                         # UI components
│   ├── __init__.py             # UI package initialization
│   ├── strategy_manager.py     # Web-based strategy manager
│   └── templates/              # Templates for strategy generation
│       ├── __init__.py         # Templates package initialization
│       ├── strategy_generator.py # Strategy generator
│       └── strategy_template.py.tmpl # Strategy template
├── custom_strategies/          # User-defined custom strategies
│   └── __init__.py             # Custom strategies initialization
├── docs/                       # Documentation
│   └── migration_guide.md      # Guide for migrating to the framework
├── examples/                   # Example scripts
│   ├── __init__.py             # Examples package initialization
│   └── migration_example.py    # Example of migrating to the framework
└── README.md                   # This file
```

## Key Components

### Base Classes

- `ExtractionStrategy`: Abstract base class for all extraction strategies.
- `LLMExtractionStrategy`: Base class for LLM-based extraction strategies.

### Registry System

- `StrategyRegistry`: Registry for extraction strategies.
- `register_strategy`: Decorator for registering strategies with the registry.

### Factory Pattern

- `StrategyFactory`: Factory for creating strategy instances.
- `CompositeExtractionStrategy`: Composite strategy that combines multiple strategies.

### Domain-Specific Strategies

- `CryptoLLMExtractionStrategy`: Specialized strategy for cryptocurrency content.
- `NewsLLMExtractionStrategy`: Specialized strategy for news content.
- `FinancialLLMExtractionStrategy`: Specialized strategy for financial content.
- `SocialMediaLLMExtractionStrategy`: Specialized strategy for social media content.
- `AcademicLLMExtractionStrategy`: Specialized strategy for academic and research content.
- `ProductLLMExtractionStrategy`: Specialized strategy for product and e-commerce content.

### Composite Strategies

- `ComprehensiveLLMExtractionStrategy`: Combines multiple domain-specific strategies for comprehensive extraction.

### UI Components

- `StrategyManagerUI`: Web-based UI for managing and testing extraction strategies.
- `StrategyTemplateGenerator`: Generator for creating new strategy files from templates.

### Strategy Creation and Placement

The framework includes a UI-based strategy generator that allows users to create new extraction strategies without writing code. When creating a new strategy:

1. The strategy is automatically placed in the appropriate category directory based on the selected category (e.g., crypto, news, financial).
2. The strategy is registered with the registry system when the application starts.
3. The strategy's metadata, including its category, is stored in the registry.

This organization ensures that strategies are properly categorized and can be easily discovered and managed.

## Usage Examples

### Basic Usage

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import LLMExtractionStrategy

# Create a strategy instance
strategy = LLMExtractionStrategy(
    provider="openrouter",
    api_token="your-api-token",
    instruction="Extract the main headline and a brief summary.",
    schema={
        "type": "object",
        "properties": {
            "headline": {"type": "string"},
            "summary": {"type": "string"}
        },
        "required": ["headline", "summary"]
    }
)

# Extract information from content
result = await strategy.extract(url, content)
```

### Using Domain-Specific Strategies

```python
from cry_a_4mcp.crawl4ai.extraction_strategies.crypto import CryptoLLMExtractionStrategy
from cry_a_4mcp.crawl4ai.extraction_strategies.news import NewsLLMExtractionStrategy

# Create a crypto-specific strategy
crypto_strategy = CryptoLLMExtractionStrategy(
    provider="openrouter",
    api_token="your-api-token"
)

# Extract cryptocurrency information
crypto_result = await crypto_strategy.extract(url, content)

# Create a news-specific strategy
news_strategy = NewsLLMExtractionStrategy(
    provider="openrouter",
    api_token="your-api-token"
)

# Extract news information
news_result = await news_strategy.extract(url, content)
```

### Using Composite Strategies

```python
from cry_a_4mcp.crawl4ai.extraction_strategies.composite import ComprehensiveLLMExtractionStrategy

# Create a comprehensive strategy that combines multiple domain-specific strategies
comprehensive_strategy = ComprehensiveLLMExtractionStrategy(
    provider="openrouter",
    api_token="your-api-token",
    merge_mode="smart"  # Options: "smart", "union", "intersection"
)

# Extract comprehensive information from content
result = await comprehensive_strategy.extract(url, content)
```

### Using the UI Components

```python
from cry_a_4mcp.crawl4ai.extraction_strategies.ui import StrategyManagerUI

# Create a UI instance
ui = StrategyManagerUI()

# Run the UI
ui.run()
```

### Using the Registry and Factory

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import (
    StrategyRegistry,
    StrategyFactory,
    register_strategy,
    LLMExtractionStrategy
)

# Define a custom strategy
@register_strategy(
    name="CustomStrategy",
    description="A custom extraction strategy",
    category="custom"
)
class CustomStrategy(LLMExtractionStrategy):
    # Custom implementation
    pass

# Create a strategy instance using the factory
strategy = StrategyFactory.create(
    "CustomStrategy",
    {"provider": "openrouter", "api_token": "your-api-token"}
)

# List available strategies
strategies = StrategyRegistry.get_all()
print(f"Available strategies: {', '.join(strategies.keys())}")
```

### Creating a Custom Domain-Specific Strategy

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import LLMExtractionStrategy, register_strategy

@register_strategy(
    name="CustomDomainStrategy",
    description="A custom domain-specific extraction strategy",
    category="custom_domain"
)
class CustomDomainStrategy(LLMExtractionStrategy):
    def __init__(self, provider="openrouter", api_token=None, model=None):
        # Define a domain-specific schema
        schema = {
            "type": "object",
            "properties": {
                "domain_specific_field": {"type": "string"},
                "another_field": {"type": "string"}
            },
            "required": ["domain_specific_field"]
        }
        
        # Define a domain-specific instruction
        instruction = "Extract domain-specific information from the content."
        
        # Initialize the base class
        super().__init__(
            provider=provider,
            api_token=api_token,
            model=model,
            schema=schema,
            instruction=instruction
        )
    
    async def extract(self, url, content):
        # Pre-processing specific to this domain
        processed_content = self._preprocess_content(content)
        
        # Call the base extraction method
        result = await super().extract(url, processed_content)
        
        # Post-processing specific to this domain
        enhanced_result = self._postprocess_result(result)
        
        return enhanced_result
    
    def _preprocess_content(self, content):
        # Implement domain-specific pre-processing
        return content
    
    def _postprocess_result(self, result):
        # Implement domain-specific post-processing
        return result
```

### Creating a Custom Composite Strategy

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import CompositeExtractionStrategy, register_strategy
from cry_a_4mcp.crawl4ai.extraction_strategies.crypto import CryptoLLMExtractionStrategy
from cry_a_4mcp.crawl4ai.extraction_strategies.news import NewsLLMExtractionStrategy

@register_strategy(
    name="CustomCompositeStrategy",
    description="A custom composite extraction strategy",
    category="composite"
)
class CustomCompositeStrategy(CompositeExtractionStrategy):
    def __init__(self, provider="openrouter", api_token=None, model=None):
        # Create component strategies
        crypto_strategy = CryptoLLMExtractionStrategy(
            provider=provider,
            api_token=api_token,
            model=model
        )
        
        news_strategy = NewsLLMExtractionStrategy(
            provider=provider,
            api_token=api_token,
            model=model
        )
        
        # Initialize the base class with component strategies
        super().__init__(
            strategies=[crypto_strategy, news_strategy],
            merge_mode="smart"  # Options: "smart", "union", "intersection"
        )
    
    async def extract(self, url, content):
        # Custom content classification logic
        content_type = self._classify_content(content)
        
        # Select strategies based on content type
        if content_type == "crypto":
            selected_strategies = [s for s in self.strategies if isinstance(s, CryptoLLMExtractionStrategy)]
        elif content_type == "news":
            selected_strategies = [s for s in self.strategies if isinstance(s, NewsLLMExtractionStrategy)]
        else:
            # Use all strategies for unknown content types
            selected_strategies = self.strategies
        
        # Extract using selected strategies
        results = []
        for strategy in selected_strategies:
            try:
                result = await strategy.extract(url, content)
                results.append(result)
            except Exception as e:
                # Handle extraction errors
                print(f"Error extracting with {strategy.__class__.__name__}: {e}")
        
        # Merge results using custom logic
        merged_result = self._custom_merge(results)
        
        return merged_result
    
    def _classify_content(self, content):
        # Implement content classification logic
        if "bitcoin" in content.lower() or "ethereum" in content.lower():
            return "crypto"
        elif "breaking news" in content.lower() or "reported" in content.lower():
            return "news"
        else:
            return "unknown"
    
    def _custom_merge(self, results):
        # Implement custom result merging logic
        if not results:
            return {}
        
        # Start with the first result as the base
        merged = results[0].copy()
        
        # Merge in additional results
        for result in results[1:]:
            for key, value in result.items():
                if key not in merged:
                    # Add missing fields
                    merged[key] = value
                elif isinstance(merged[key], list) and isinstance(value, list):
                    # Combine lists without duplicates
                    merged[key] = list(set(merged[key] + value))
                elif merged[key] is None or merged[key] == "":
                    # Replace empty values
                    merged[key] = value
        
        return merged
```

## Creating a New Strategy

To create a new extraction strategy, follow these steps:

1. Decide whether you need a domain-specific strategy or a composite strategy.
2. Create a new file in the appropriate subdirectory.
3. Implement your strategy by subclassing the appropriate base class.
4. Register your strategy with the registry using the `@register_strategy` decorator.
5. Export your strategy in the package's `__init__.py` file.

Detailed steps:

1. **Choose the right base class**:
   - For domain-specific strategies: `LLMExtractionStrategy`
   - For composite strategies: `CompositeExtractionStrategy`

2. **Define your schema and instruction**:
   - For domain-specific strategies, define a JSON schema that captures the structure of the data you want to extract.
   - Write a clear instruction that guides the LLM in extracting the information.

3. **Implement domain-specific methods**:
   - `_preprocess_content`: Prepare the content for extraction.
   - `_validate_extraction`: Ensure the extracted data meets your requirements.
   - `_enhance_extraction`: Add additional information or transform the extracted data.

4. **Register your strategy**:
   - Use the `@register_strategy` decorator to make your strategy discoverable.
   - Provide a name, description, and category for your strategy.

5. **Export your strategy**:
   - Add your strategy to the `__init__.py` file in your package.
   - Add it to the `__all__` list to make it available for import.

## Migrating to the New Framework

If you have existing extraction code, you can migrate it to the new framework by following these steps:

1. Identify the domain-specific extraction logic in your existing code.
2. Create a new strategy class that extends the appropriate base class.
3. Move your extraction logic to the new strategy class.
4. Update your code to use the new strategy instead of the old extraction logic.

For detailed migration instructions, see the [Migration Guide](docs/migration_guide.md) and the [Migration Example](examples/migration_example.py).

## Complete Example

Here's a complete example that demonstrates how to create, register, and use a new extraction strategy:

```python
# File: extraction_strategies/custom/custom_llm.py
from cry_a_4mcp.crawl4ai.extraction_strategies import LLMExtractionStrategy, register_strategy

@register_strategy(
    name="CustomLLMStrategy",
    description="A custom LLM-based extraction strategy",
    category="custom"
)
class CustomLLMStrategy(LLMExtractionStrategy):
    def __init__(self, provider="openrouter", api_token=None, model=None):
        # Define a custom schema
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content_summary": {"type": "string"},
                "custom_field": {"type": "string"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["title", "content_summary"]
        }
        
        # Define a custom instruction
        instruction = """
        Extract the following information from the content:
        1. The title of the content
        2. A brief summary of the content
        3. Any custom field specific to this content
        4. A list of relevant tags
        """
        
        # Initialize the base class
        super().__init__(
            provider=provider,
            api_token=api_token,
            model=model,
            schema=schema,
            instruction=instruction
        )
    
    async def extract(self, url, content):
        # Pre-processing
        processed_content = self._preprocess_content(content)
        
        # Call the base extraction method
        result = await super().extract(url, processed_content)
        
        # Post-processing
        validated_result = self._validate_extraction(result)
        enhanced_result = self._enhance_extraction(validated_result, url)
        
        return enhanced_result
    
    def _preprocess_content(self, content):
        # Clean up the content
        cleaned_content = content.strip()
        
        # Add any custom preprocessing logic here
        
        return cleaned_content
    
    def _validate_extraction(self, result):
        # Ensure required fields are present
        if "title" not in result or not result["title"]:
            result["title"] = "Untitled"
        
        if "content_summary" not in result or not result["content_summary"]:
            result["content_summary"] = "No summary available"
        
        # Ensure tags is a list
        if "tags" in result and not isinstance(result["tags"], list):
            if isinstance(result["tags"], str):
                # Convert comma-separated string to list
                result["tags"] = [tag.strip() for tag in result["tags"].split(",")]
            else:
                result["tags"] = []
        
        return result
    
    def _enhance_extraction(self, result, url):
        # Add metadata
        result["metadata"] = {
            "strategy": "CustomLLMStrategy",
            "version": "1.0.0",
            "timestamp": datetime.datetime.now().isoformat(),
            "source_url": url
        }
        
        # Add any additional enhancements
        
        return result

# File: extraction_strategies/custom/__init__.py
from .custom_llm import CustomLLMStrategy

__all__ = ["CustomLLMStrategy"]

# Usage example
async def main():
    from cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory
    
    # Create a strategy instance using the factory
    strategy = StrategyFactory.create(
        "CustomLLMStrategy",
        {"provider": "openrouter", "api_token": "your-api-token"}
    )
    
    # Extract information from content
    url = "https://example.com/article"
    content = "This is a sample article about extraction strategies."
    
    result = await strategy.extract(url, content)
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Advanced Topics

### Customizing the Registry

You can customize the registry behavior by extending the `StrategyRegistry` class:

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import StrategyRegistry

class CustomRegistry(StrategyRegistry):
    def register(self, strategy_class, name, description, category):
        # Add custom registration logic
        super().register(strategy_class, name, description, category)
        
        # Additional actions after registration
        print(f"Registered strategy: {name}")
    
    def get_strategies_by_custom_criteria(self, criteria):
        # Implement custom filtering logic
        return [s for s in self.strategies.values() if criteria(s)]

# Replace the default registry
from cry_a_4mcp.crawl4ai.extraction_strategies import registry
registry.REGISTRY = CustomRegistry()
```

### Customizing the Factory

You can customize the factory behavior by extending the `StrategyFactory` class:

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory

class CustomFactory(StrategyFactory):
    @classmethod
    def create(cls, strategy_name, config=None):
        # Add custom creation logic
        print(f"Creating strategy: {strategy_name}")
        
        # Call the base implementation
        return super().create(strategy_name, config)
    
    @classmethod
    def create_with_defaults(cls, strategy_name):
        # Create with default configuration
        return cls.create(strategy_name, {})

# Replace the default factory
from cry_a_4mcp.crawl4ai.extraction_strategies import factory
factory.FACTORY = CustomFactory()
```

## Contributing

When contributing to the extraction strategies framework, please follow these guidelines:

1. Place new domain-specific strategies in their own subdirectory.
2. Follow the existing code style and patterns.
3. Write comprehensive docstrings and comments.
4. Add appropriate tests for your strategy.
5. Update the documentation to reflect your changes.
6. Register your strategy with the registry using the `@register_strategy` decorator.

## Monitoring and Metrics

The extraction strategies framework integrates with Prometheus for monitoring and metrics collection. This allows you to track the performance and health of your extraction strategies in production.

### Available Metrics

The framework provides the following metrics out of the box:

- **extraction_time_seconds**: Histogram of extraction time in seconds by strategy name
- **extraction_success_total**: Counter of successful extractions by strategy name
- **extraction_failure_total**: Counter of failed extractions by strategy name
- **extraction_count_by_domain**: Counter of extractions by domain and strategy name
- **llm_token_usage**: Counter of LLM token usage by model and operation (prompt, completion)

### Using the Metrics Exporter

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import MetricsExporter

# Initialize the metrics exporter
metrics_exporter = MetricsExporter()

# Register metrics
metrics_exporter.register_metrics()

# Track extraction time
with metrics_exporter.track_extraction_time("CryptoLLMExtractionStrategy"):
    result = await strategy.extract(url, content)

# Track extraction success/failure
metrics_exporter.track_extraction_result("CryptoLLMExtractionStrategy", success=True)

# Track extraction by domain
metrics_exporter.track_extraction_by_domain("CryptoLLMExtractionStrategy", "example.com")

# Track LLM token usage
metrics_exporter.track_llm_token_usage("gpt-4", "prompt", 100)
metrics_exporter.track_llm_token_usage("gpt-4", "completion", 50)
```

### Exposing Metrics

To expose the metrics for Prometheus to scrape, you can use the `prometheus_client` library:

```python
from prometheus_client import start_http_server

# Start the HTTP server to expose metrics
start_http_server(8000)

# Your application code here
```

### Custom Metrics

You can also define custom metrics for your specific use case:

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import MetricsExporter
from prometheus_client import Counter

# Initialize the metrics exporter
metrics_exporter = MetricsExporter()

# Define a custom metric
custom_metric = Counter('custom_metric', 'Description of custom metric', ['label1', 'label2'])

# Register the custom metric
metrics_exporter.register_custom_metric(custom_metric)

# Track the custom metric
custom_metric.labels(label1='value1', label2='value2').inc()
```

### Metrics Dashboard

You can use Grafana to create dashboards for visualizing the metrics collected by Prometheus. The framework provides a sample Grafana dashboard configuration in the `monitoring/dashboards` directory.

![Metrics Dashboard](docs/images/metrics_dashboard.png)

## Supporting UI-Based Management

The extraction strategies framework includes a web-based UI for managing and testing extraction strategies. The UI is built using Streamlit and provides the following features:

- Browse available strategies by category
- Configure API keys and other settings
- Test strategies on sample content
- Create and configure composite strategies
- View extraction results in a structured format
- Export extraction results to JSON

### Running the UI

```python
from cry_a_4mcp.crawl4ai.extraction_strategies.ui import StrategyManagerUI

# Create a UI instance
ui = StrategyManagerUI()

# Run the UI
ui.run()
```

### UI Screenshots

![Strategy Manager UI](docs/images/strategy_manager_ui.png)

### Customizing the UI

You can customize the UI by extending the `StrategyManagerUI` class:

```python
from cry_a_4mcp.crawl4ai.extraction_strategies.ui import StrategyManagerUI

class CustomStrategyManagerUI(StrategyManagerUI):
    def __init__(self):
        super().__init__()
        self.title = "Custom Strategy Manager"
        self.theme = "dark"
    
    def add_custom_page(self):
        # Add a custom page to the UI
        pass
    
    def customize_sidebar(self):
        # Customize the sidebar
        pass

# Create a custom UI instance
ui = CustomStrategyManagerUI()

# Run the custom UI
ui.run()
```

The extraction strategies framework is designed to support UI-based management of strategies. The registry system allows the UI to discover available strategies, and the factory pattern allows the UI to create and configure strategy instances.

## Conclusion

The extraction strategies framework provides a powerful, flexible, and extensible way to extract structured information from web content. By leveraging the modular architecture, you can easily create domain-specific strategies, combine them into composite strategies, and manage them through a web-based UI.

Key benefits of the framework include:

- **Modularity**: Each strategy is a separate class that can be used independently.
- **Extensibility**: New strategies can be easily added by subclassing the base classes.
- **Configurability**: Strategies can be configured with various parameters.
- **Discoverability**: Strategies can register themselves with the registry for dynamic discovery.
- **Composability**: Multiple strategies can be combined using the composite pattern.
- **Monitorability**: Integration with Prometheus for monitoring and metrics collection.
- **UI Support**: Web-based UI for managing and testing strategies.

By following the guidelines in this README and the provided examples, you can quickly get started with the extraction strategies framework and adapt it to your specific needs.

## Registry and Discovery

The registry system is a key component of the extraction strategies framework. It provides a way to discover available strategies and their capabilities.

### Registry Metadata

The registry provides metadata about each strategy, including:

- **Name**: The unique name of the strategy.
- **Description**: A human-readable description of the strategy.
- **Category**: The category of the strategy (e.g., "crypto", "news", "financial").
- **Configuration Schema**: A JSON schema describing the configuration options for the strategy.

This metadata can be used by the UI to generate appropriate forms for configuring strategies and to provide documentation to users.

### Accessing the Registry

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import StrategyRegistry

# Get all registered strategies
all_strategies = StrategyRegistry.get_all()

# Get strategies by category
crypto_strategies = StrategyRegistry.get_by_category("crypto")

# Get a specific strategy by name
crypto_strategy = StrategyRegistry.get_strategy("CryptoLLMExtractionStrategy")

# Get the configuration schema for a strategy
config_schema = StrategyRegistry.get_config_schema("CryptoLLMExtractionStrategy")
```

### Dynamic Discovery

The registry system allows for dynamic discovery of strategies at runtime. This means that you can add new strategies to the framework without modifying the core code.

To make a strategy discoverable, simply register it with the registry using the `@register_strategy` decorator:

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import register_strategy

@register_strategy(
    name="MyStrategy",
    description="My custom strategy",
    category="custom"
)
class MyStrategy(ExtractionStrategy):
    # Implementation
    pass
```

### Factory Pattern

The factory pattern allows the UI to create strategy instances based on user input. The `StrategyFactory` class provides methods for creating strategy instances from configuration dictionaries.

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory

# Create a strategy instance from a configuration dictionary
config = {
    "strategy_name": "CryptoLLMExtractionStrategy",
    "api_key": "your-api-key",
    "model": "gpt-4"
}
strategy = StrategyFactory.create_strategy(config)

# Create a composite strategy from a configuration dictionary
composite_config = {
    "strategy_name": "ComprehensiveLLMExtractionStrategy",
    "component_strategies": [
        {
            "strategy_name": "CryptoLLMExtractionStrategy",
            "api_key": "your-api-key",
            "model": "gpt-4"
        },
        {
            "strategy_name": "NewsLLMExtractionStrategy",
            "api_key": "your-api-key",
            "model": "gpt-4"
        }
    ],
    "merge_mode": "smart"
}
composite_strategy = StrategyFactory.create_strategy(composite_config)
```

The factory pattern, combined with the registry system, allows for a flexible and extensible architecture that can be easily adapted to different use cases.

## Migration from Old Structure

If you're migrating from the old extraction strategy structure, use the migration script in the `scripts` directory:

```bash
python scripts/migrate_extraction_strategies.py --scan-dir your/project/directory
```

This script will update imports and usage patterns to match the new structure.

## Best Practices

- Use the registry and factory patterns for creating and managing strategies.
- Define clear schemas and instructions for LLM-based strategies.
- Implement proper error handling and validation in your strategies.
- Use the composite pattern to combine multiple strategies when appropriate.
- Document your strategies with clear docstrings and examples.

## Testing Strategies

The extraction strategies framework includes utilities for testing strategies. These utilities make it easy to write unit tests for your strategies and ensure they work as expected.

### Unit Testing

```python
import unittest
from cry_a_4mcp.crawl4ai.extraction_strategies.testing import StrategyTestCase
from cry_a_4mcp.crawl4ai.extraction_strategies.crypto import CryptoLLMExtractionStrategy

class TestCryptoLLMExtractionStrategy(StrategyTestCase):
    def setUp(self):
        self.strategy = CryptoLLMExtractionStrategy(
            provider="mock",  # Use the mock provider for testing
            api_token="test-token"
        )
        self.sample_content = "Bitcoin price surged to $60,000 today."
        self.sample_url = "https://example.com/crypto-news"
    
    async def test_extract(self):
        # Set up the mock response
        self.mock_llm_response({
            "cryptocurrency": "Bitcoin",
            "price": "$60,000",
            "change_24h": "+5%",
            "market_cap": "$1.2T"
        })
        
        # Call the strategy
        result = await self.strategy.extract(self.sample_url, self.sample_content)
        
        # Assert the result
        self.assertEqual(result["cryptocurrency"], "Bitcoin")
        self.assertEqual(result["price"], "$60,000")
        self.assertEqual(result["change_24h"], "+5%")
        self.assertEqual(result["market_cap"], "$1.2T")
    
    async def test_preprocess_content(self):
        # Test the preprocessing method
        processed_content = self.strategy._preprocess_content(self.sample_content)
        self.assertIn("Bitcoin", processed_content)
        self.assertIn("$60,000", processed_content)
    
    async def test_validate_extraction(self):
        # Test the validation method
        invalid_result = {"cryptocurrency": "Bitcoin"}
        validated_result = self.strategy._validate_extraction(invalid_result)
        self.assertEqual(validated_result["cryptocurrency"], "Bitcoin")
        self.assertIn("price", validated_result)

if __name__ == "__main__":
    unittest.main()
```

### Integration Testing

```python
import unittest
from cry_a_4mcp.crawl4ai.extraction_strategies.testing import IntegrationTestCase
from cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory

class TestStrategyIntegration(IntegrationTestCase):
    async def test_crypto_strategy(self):
        # Create a strategy using the factory
        strategy = StrategyFactory.create_strategy({
            "strategy_name": "CryptoLLMExtractionStrategy",
            "provider": "openrouter",
            "api_token": self.get_api_token("openrouter")
        })
        
        # Load a sample file
        content = self.load_sample_file("crypto_article.txt")
        url = "https://example.com/crypto-article"
        
        # Extract information
        result = await strategy.extract(url, content)
        
        # Assert the result structure
        self.assertIn("cryptocurrency", result)
        self.assertIn("price", result)
    
    async def test_composite_strategy(self):
        # Create a composite strategy
        strategy = StrategyFactory.create_strategy({
            "strategy_name": "ComprehensiveLLMExtractionStrategy",
            "component_strategies": [
                {
                    "strategy_name": "CryptoLLMExtractionStrategy",
                    "provider": "openrouter",
                    "api_token": self.get_api_token("openrouter")
                },
                {
                    "strategy_name": "NewsLLMExtractionStrategy",
                    "provider": "openrouter",
                    "api_token": self.get_api_token("openrouter")
                }
            ],
            "merge_mode": "smart"
        })
        
        # Load a sample file
        content = self.load_sample_file("crypto_news.txt")
        url = "https://example.com/crypto-news"
        
        # Extract information
        result = await strategy.extract(url, content)
        
        # Assert the result structure
        self.assertIn("cryptocurrency", result)
        self.assertIn("headline", result)

if __name__ == "__main__":
    unittest.main()
```