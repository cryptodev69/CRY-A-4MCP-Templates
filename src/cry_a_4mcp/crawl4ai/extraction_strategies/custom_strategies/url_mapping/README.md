# URL-to-Extractor Mapping System

This module provides a flexible system for mapping URLs to appropriate content extractors based on domain, path, or exact URL patterns. It allows for dynamic selection of extractors based on the URL being processed.

## Key Components

### ExtractorConfig

Represents the configuration for a specific extractor, including:
- `extractor_id`: The identifier for the extractor to be created by the ExtractorFactory
- `target_group`: The group name under which extraction results will be stored
- `params`: Additional parameters to pass to the extractor

### URLExtractorMapping

Defines a mapping between a URL pattern and a set of extractors, with:
- `url_pattern`: The pattern to match against URLs
- `pattern_type`: The type of pattern matching to use ("domain", "path", or "exact")
- `extractors`: List of ExtractorConfig objects to apply when the pattern matches
- `priority`: Priority value for resolving conflicts when multiple patterns match

### URLMappingManager

Manages a collection of URL-to-extractor mappings, providing methods to:
- Add and remove mappings
- Find applicable extractors for a given URL
- Save and load mapping configurations

## Pattern Matching Types

1. **Domain Matching**: Matches URLs based on their domain name, including subdomains
   - Example: `coindesk.com` will match `https://www.coindesk.com/markets/...`

2. **Path Matching**: Matches URLs based on path components
   - Example: `/product/` will match any URL containing "/product/" in its path

3. **Exact Matching**: Uses regular expressions for precise pattern matching
   - Example: `.*\.pdf$` will match any URL ending with ".pdf"

## Usage Example

```python
# Create a URL mapping manager
mapping_manager = URLMappingManager()

# Configure extractors for a specific domain
crypto_extractors = [
    ExtractorConfig(extractor_id="TitleExtractor", target_group="title"),
    ExtractorConfig(extractor_id="CryptoContentExtractor", target_group="content")
]

# Add a domain-based mapping
mapping_manager.add_mapping(URLExtractorMapping(
    url_pattern="coindesk.com",
    pattern_type="domain",
    extractors=crypto_extractors,
    priority=100
))

# Get extractors for a specific URL
extractors = mapping_manager.get_extractors_for_url("https://www.coindesk.com/markets/2023/01/01/bitcoin-price-surges/")

# Use the extractors to process content
for extractor_config in extractors:
    extractor = factory.create(extractor_config.extractor_id)
    result = await extractor.extract(content, **extractor_config.params)
    # Store result under target_group
```

## Integration

The URL-to-extractor mapping system can be integrated into content extraction pipelines to automatically select and apply the appropriate extractors based on the URL being processed. See the example files for detailed integration examples:

- `url_extractor_mapping_example.py`: Basic usage example
- `url_extractor_mapping_integration.py`: Complete integration example with batch processing and interactive mode

## UI Component

A Tkinter-based UI is available for managing URL-to-extractor mappings visually. The UI allows users to:

- View existing mappings
- Create new mappings
- Edit or delete existing mappings
- Save and load mapping configurations

To launch the UI, run the `url_mapping_ui.py` script.