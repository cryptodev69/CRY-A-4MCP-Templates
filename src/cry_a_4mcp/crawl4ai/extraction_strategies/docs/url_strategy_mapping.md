# URL-to-Extractor Mapping

## Overview

The URL-to-Extractor mapping feature provides a straightforward way to configure which URLs should be processed by which extractors. This system allows a single URL to be associated with multiple extractors for different target groups, enabling more flexible and targeted information extraction.

## Key Benefits

- **Direct Configuration**: Simple UI-based configuration of URL-to-extractor mappings
- **Multiple Extractors Per URL**: Ability to associate a single URL with multiple extractors
- **Target Group Specification**: Extractors can be assigned to specific target groups
- **Flexible Mapping**: Support for various URL patterns and configurations
- **Integrated with Existing UI**: Seamlessly extends the current strategy management interface
- **User-Friendly Management**: Easy to add, edit, and remove URL-to-extractor mappings

## Architecture

The URL-to-Extractor mapping system consists of several components:

### 1. URL Mapping Configuration

The core of the system is a simple configuration structure that defines which URLs should be processed by which extractors. This configuration includes:

- URL patterns to match against
- Associated extractor IDs
- Target group specifications

### 2. UI Integration

The mapping configuration is integrated into the existing `StrategyManagerUI` with a dedicated section for managing URL-to-extractor mappings. This includes:

- Interface for creating new mappings
- Tools for editing existing mappings
- Visualization of current mappings
- Validation of mapping configurations

### 3. Data Structure

The mapping data structure supports one-to-many relationships between URLs and extractors:

```json
{
  "url_pattern": "example.com/news",
  "extractors": [
    {
      "extractor_id": "news_extractor",
      "target_group": "general_news"
    },
    {
      "extractor_id": "sentiment_extractor",
      "target_group": "sentiment_analysis"
    }
  ]
}
```

### 4. Configuration Storage

The mapping configurations are stored in a persistent format that can be loaded and saved through the UI, ensuring that mappings are preserved between sessions.

## Implementation Details

### URL Mapping Configuration

The URL mapping configuration is implemented as a simple data structure that can be easily serialized to and from JSON or YAML. The structure includes:

```python
class URLExtractorMapping:
    def __init__(self, url_pattern, extractors):
        self.url_pattern = url_pattern  # String pattern to match URLs
        self.extractors = extractors    # List of ExtractorConfig objects

class ExtractorConfig:
    def __init__(self, extractor_id, target_group):
        self.extractor_id = extractor_id  # ID of the extractor to use
        self.target_group = target_group  # Target group for extraction
```

### UI Components

The UI for managing URL-to-extractor mappings includes the following components:

1. **Mapping List View**: Displays all configured mappings with options to edit or delete
2. **Mapping Creation Form**: Form for creating new mappings with fields for:
   - URL pattern
   - Extractor selection (multiple)
   - Target group specification
3. **Mapping Editor**: Interface for editing existing mappings
4. **Validation Logic**: Ensures that mappings are valid before saving

### URL Pattern Matching

URL patterns can be specified in several formats:

- **Exact URLs**: Match only the specific URL
- **Domain-based**: Match all URLs from a specific domain
- **Path-based**: Match URLs with specific path patterns
- **Query Parameter-based**: Match URLs with specific query parameters

### Configuration Storage

The mapping configurations are stored in a JSON file with the following structure:

```json
[
  {
    "url_pattern": "example.com/news",
    "extractors": [
      {
        "extractor_id": "news_extractor",
        "target_group": "general_news"
      },
      {
        "extractor_id": "sentiment_extractor",
        "target_group": "sentiment_analysis"
      }
    ]
  },
  {
    "url_pattern": "blog.example.com",
    "extractors": [
      {
        "extractor_id": "blog_extractor",
        "target_group": "blog_content"
      }
    ]
  }
]
```

## Usage Examples

### Configuring URL-to-Extractor Mappings in the UI

1. Navigate to the Strategy Manager UI
2. Select the "URL Mapping" tab
3. Click "Create New Mapping"
4. Enter the URL pattern (e.g., "example.com/news")
5. Select one or more extractors from the dropdown
6. Specify target groups for each extractor
7. Click "Save Mapping"

### Programmatically Creating URL-to-Extractor Mappings

```python
from cry_a_4mcp.crawl4ai.extraction_strategies.url_mapping import URLExtractorMapping, ExtractorConfig
from cry_a_4mcp.crawl4ai.extraction_strategies.url_mapping import URLMappingManager

# Create extractor configurations
news_extractor = ExtractorConfig(
    extractor_id="news_extractor",
    target_group="general_news"
)

sentiment_extractor = ExtractorConfig(
    extractor_id="sentiment_extractor",
    target_group="sentiment_analysis"
)

# Create a URL mapping
news_mapping = URLExtractorMapping(
    url_pattern="example.com/news",
    extractors=[news_extractor, sentiment_extractor]
)

# Add the mapping to the manager
mapping_manager = URLMappingManager()
mapping_manager.add_mapping(news_mapping)
mapping_manager.save_mappings()
```

### Using URL Mappings in a Processing Pipeline

```python
async def process_content(url, content):
    # Get the URL mapping manager
    mapping_manager = URLMappingManager()
    
    # Find extractors for this URL
    extractors = mapping_manager.get_extractors_for_url(url)
    
    # Process with each extractor
    results = {}
    for extractor_config in extractors:
        extractor = get_extractor(extractor_config.extractor_id)
        target_group = extractor_config.target_group
        
        # Extract data with the specific extractor
        extracted_data = await extractor.extract(content, url=url)
        
        # Store results by target group
        results[target_group] = extracted_data
    
    return results
```

## Best Practices

### Creating Effective URL Patterns

1. **Be specific with URL patterns**: Create patterns that precisely target the content you want to extract.
2. **Use domain-based patterns for site-wide extraction**: When all pages on a domain should use the same extractors.
3. **Use path-based patterns for section-specific extraction**: When different sections of a site need different extractors.
4. **Test your patterns**: Verify that your patterns match the intended URLs before deploying.

### Organizing Extractors

1. **Group related extractors**: Assign meaningful target group names that reflect the purpose of the extraction.
2. **Avoid redundant extractors**: Don't assign multiple extractors that perform the same function to the same URL.
3. **Consider extraction order**: If extractors depend on each other's output, ensure they're processed in the correct order.

### UI Management

1. **Use descriptive names**: Give your mappings clear names that indicate their purpose.
2. **Document your mappings**: Add descriptions to explain what each mapping does and why.
3. **Regularly review and update**: Periodically check your mappings to ensure they're still relevant and effective.

### Performance Optimization

1. **Limit the number of extractors per URL**: Using too many extractors on a single URL can impact performance.
2. **Use efficient URL patterns**: Overly complex patterns can slow down the matching process.
3. **Cache frequently used results**: Consider caching extraction results for frequently accessed URLs.

## Integration with Existing UI

The URL-to-Extractor mapping system is designed to integrate seamlessly with the existing `StrategyManagerUI`. It adds a new tab or section to the UI that allows users to manage URL-to-extractor mappings without disrupting the existing functionality.

The integration includes:

1. **Shared Components**: Reuses existing UI components for consistency
2. **Common Data Storage**: Leverages the existing configuration storage mechanisms
3. **Unified User Experience**: Maintains the same look and feel as the rest of the UI

## Future Enhancements

1. **Advanced Pattern Matching**: Support for more complex URL matching patterns
2. **Bulk Operations**: Tools for managing multiple mappings at once
3. **Import/Export**: Functionality to import and export mapping configurations
4. **Visual Pattern Builder**: Interactive tool for creating and testing URL patterns
5. **Analytics Dashboard**: Visualize which extractors are being used for which URLs
6. **Conditional Mapping**: Apply extractors based on content characteristics in addition to URL

## Conclusion

The URL-to-Extractor mapping feature provides a straightforward and user-friendly way to configure which URLs should be processed by which extractors. By supporting one-to-many relationships between URLs and extractors with target group specification, it enables more flexible and targeted information extraction while maintaining a simple configuration interface integrated with the existing UI.