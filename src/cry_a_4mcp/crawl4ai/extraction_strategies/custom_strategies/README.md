# URL-to-Extractor Mapping

This directory contains components for the URL-to-extractor mapping functionality. This system allows configuring which URLs should be processed by which extractors, with support for associating a single URL with multiple extractors for different target groups.

## Overview

The URL-to-extractor mapping system provides a straightforward way to configure which URLs should be processed by which extractors. This is particularly useful for targeting specific extractors to specific content sources and organizing extraction results by target groups.

The system consists of:

1. **URL Mapping Configuration**: Simple data structures for defining URL-to-extractor mappings.
2. **UI Integration**: Components that integrate with the existing Strategy Manager UI.
3. **Mapping Manager**: Utilities for managing and applying URL-to-extractor mappings.
4. **Configuration Storage**: Mechanisms for persisting mapping configurations.

## Key Components

### `url_mapping.py`

This file contains the core classes for URL-to-extractor mapping:

- `URLExtractorMapping`: Data class for storing URL pattern to extractor mappings.
- `ExtractorConfig`: Configuration for an extractor, including ID and target group.
- `URLMappingManager`: Manages URL-to-extractor mappings, including loading, saving, and applying mappings.

### `url_mapping_ui.py`

This file contains the UI components for managing URL-to-extractor mappings:

- `URLMappingUI`: Integration with the Strategy Manager UI.
- `MappingListView`: Component for displaying and managing existing mappings.
- `MappingCreationForm`: Form for creating new URL-to-extractor mappings.
- `MappingEditor`: Interface for editing existing mappings.

## Usage

### Using the UI

The URL-to-extractor mapping system is integrated with the Strategy Manager UI, allowing you to configure mappings through a user-friendly interface:

1. Navigate to the Strategy Manager UI
2. Select the "URL Mappings" tab
3. Create new mappings by clicking "Add Mapping"
4. Configure the URL pattern, select extractors, and specify target groups
5. Save the configuration

### Programmatic Usage

```python
from cry_a_4mcp.crawl4ai.extraction_strategies.custom_strategies.url_mapping import URLExtractorMapping, ExtractorConfig, URLMappingManager

# Create a mapping manager
mapping_manager = URLMappingManager()

# Create extractor configurations
extractor_configs = [
    ExtractorConfig(extractor_id="CryptoEntityExtractor", target_group="entities"),
    ExtractorConfig(extractor_id="CryptoTripleExtractor", target_group="triples")
]

# Create a URL mapping
mapping = URLExtractorMapping(
    url_pattern="coindesk.com",
    pattern_type="domain",
    extractors=extractor_configs
)

# Add the mapping
mapping_manager.add_mapping(mapping)

# Save the configuration
mapping_manager.save_config()

# Use the mapping in a processing pipeline
url = "https://www.coindesk.com/markets/2023/04/15/bitcoin-price-analysis/"
content = "Bitcoin price has been fluctuating..."

# Get applicable extractors for this URL
applicable_extractors = mapping_manager.get_extractors_for_url(url)

# Process with each applicable extractor
results = {}
for config in applicable_extractors:
    extractor = factory.create(config.extractor_id)
    result = await extractor.extract(content, url=url)
    results[config.target_group] = result
```

## Examples

For complete examples of how to use URL-to-extractor mappings, see the `examples/url_mapping_example.py` file.

## Integration with Existing UI

The URL-to-extractor mapping system is fully integrated with the existing Strategy Manager UI, providing a seamless experience for configuring and managing mappings. The system leverages the existing UI components and extends them with new functionality specific to URL mappings.

This integration allows for:

1. **Centralized configuration**: All URL-to-extractor mappings can be managed in one place.
2. **Target-specific processing**: Different extractors can be applied to the same URL for different target groups.
3. **User-friendly interface**: Non-technical users can configure mappings without coding.
4. **Flexible configuration**: Mappings can be easily updated through the UI without changing the core code.

## Best Practices

1. **Use domain patterns for broad matching**: Domain patterns (e.g., "example.com") are useful for matching all content from a specific site.
2. **Use path patterns for specific content**: Path patterns (e.g., "/news/crypto/") help target specific sections of websites.
3. **Organize by target groups**: Group extractors by their purpose (entities, triples, sentiment, etc.) for better organization.
4. **Regularly review mappings**: Periodically review and update mappings to ensure they remain relevant.
5. **Test new mappings**: Always test new mappings with sample URLs to ensure they match as expected.
6. **Document your mapping strategy**: Keep documentation of which URLs are mapped to which extractors and why.