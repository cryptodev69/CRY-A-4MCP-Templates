# CryptoCrawler Component

## Overview

The CryptoCrawler component is a specialized web crawler designed for cryptocurrency websites and content sources. It extends the base Crawl4AI functionality with cryptocurrency-specific features like token detection, blockchain address recognition, protocol analysis, image extraction, and screenshot capture.

## Features

- **Cryptocurrency-specific crawling**: Optimized for extracting information from cryptocurrency websites, exchanges, news sources, and documentation.
- **Entity extraction**: Identifies cryptocurrency entities such as tokens, exchanges, protocols, addresses, and more.
- **Relationship extraction**: Extracts subject-predicate-object triples representing relationships between cryptocurrency entities.
- **Content quality assessment**: Evaluates the quality and relevance of crawled content for cryptocurrency analysis.
- **Markdown generation**: Produces clean markdown content suitable for embedding in vector databases.
- **Image extraction**: Extracts images from web pages, including URLs, alt text, and descriptions.
- **Screenshot capture**: Captures full-page screenshots of crawled websites for visual reference and analysis.
- **Media processing**: Processes and organizes different types of media (images, videos) from crawled content.

## Architecture

The CryptoCrawler component consists of the following key classes:

### Data Models

- **CryptoEntity**: Represents a cryptocurrency entity extracted from content (tokens, exchanges, protocols, etc.).
- **CryptoTriple**: Represents a knowledge graph triple for cryptocurrency relationships (subject-predicate-object).
- **CrawlMetadata**: Contains metadata about the crawling process and content quality.
- **CrawlResult**: Complete result of cryptocurrency website crawling, including markdown content, entities, triples, media, and screenshots. The media field contains a list of extracted media items (images, videos) with their URLs and metadata, while the screenshot field contains a base64-encoded image of the full webpage.

### Core Components

- **CryptoCrawler**: Main crawler class that orchestrates the crawling process.
- **CryptoEntityExtractor**: Extracts cryptocurrency entities from text.
- **CryptoTripleExtractor**: Extracts cryptocurrency relationship triples from text.

## Usage

### Basic Usage

```python
from cry_a_4mcp.crawl4ai.crawler import CryptoCrawler

# Create a CryptoCrawler instance
crawler = CryptoCrawler(config={"user_agent": "My Crypto Crawler"})

# Initialize the crawler
await crawler.initialize()

# Crawl a cryptocurrency website
result = await crawler.crawl_crypto_website(
    url="https://example.com/crypto-news",
    content_type="news",
    extract_entities=True,
    generate_triples=True
)

# Access the crawl results
print(f"Markdown content: {result.markdown}")
print(f"Extracted entities: {result.entities}")
print(f"Extracted triples: {result.triples}")
print(f"Quality score: {result.quality_score}")

# Access media and screenshots
if result.media:
    print(f"Extracted media items: {len(result.media)}")
    for item in result.media:
        print(f"Media type: {item.get('type')}, URL: {item.get('url')}")

if result.screenshot:
    # Save screenshot to file
    import base64
    with open("screenshot.png", "wb") as f:
        f.write(base64.b64decode(result.screenshot))
```

### Integration with MCP Server

The CryptoCrawler is integrated with the MCP server through the `CrawlWebsiteTool` class, which provides a standardized interface for executing crawling operations:

```python
from cry_a_4mcp.config import Settings
from cry_a_4mcp.mcp_server.tools import CrawlWebsiteTool

# Create settings
settings = Settings()

# Create the tool
tool = CrawlWebsiteTool(settings)

# Initialize the tool
await tool.initialize()

# Execute the tool
result = await tool.execute({
    "url": "https://example.com/crypto-news",
    "content_type": "news",
    "extract_entities": True,
    "generate_triples": True
})

# Parse the result
result_dict = json.loads(result)
print(result_dict)
```

## Configuration

The CryptoCrawler can be configured through the following settings in the `Settings` class:

- `crawl4ai_cache_dir`: Directory for caching crawled content
- `crawl4ai_max_concurrent`: Maximum number of concurrent crawling operations
- `crawl4ai_timeout`: Timeout for crawling operations in seconds
- `crawl4ai_user_agent`: User agent string for HTTP requests

Additionally, the CryptoCrawler can be configured with the following options when creating an instance:

```python
config = {
    "user_agent": "CryptoCrawler/1.0",  # User agent string
    "headless": True,                  # Run browser in headless mode
    "bypass_cache": False,            # Bypass the cache and force a fresh crawl
    "word_count_threshold": 100,      # Minimum word count for content to be considered valid
    "capture_screenshot": True,        # Capture a screenshot of the webpage
    "extract_images": True            # Extract images from the webpage
}

crawler = CryptoCrawler(config=config)
```

## Extension Points

### Custom Entity Extractors

You can extend the `CryptoEntityExtractor` class to implement custom entity extraction logic:

```python
from cry_a_4mcp.crawl4ai.extractors import CryptoEntityExtractor

class CustomEntityExtractor(CryptoEntityExtractor):
    def extract(self, text: str) -> List[CryptoEntity]:
        # Custom extraction logic
        pass
```

### Custom Triple Extractors

You can extend the `CryptoTripleExtractor` class to implement custom relationship extraction logic:

```python
from cry_a_4mcp.crawl4ai.extractors import CryptoTripleExtractor

class CustomTripleExtractor(CryptoTripleExtractor):
    def extract(self, text: str) -> List[CryptoTriple]:
        # Custom extraction logic
        pass
```

## Media Handling

The CryptoCrawler component provides robust media handling capabilities:

### Image Extraction

Images are extracted from web pages using the following process:

1. The `AsyncWebCrawler.arun()` method is called with `screenshot=True` and `extract_images=True` parameters.
2. The crawler processes the webpage and extracts images, including their URLs, alt text, and descriptions.
3. The extracted images are stored in the `media` field of the `CrawlResult` object as a list of dictionaries.

Each image in the `media` list has the following structure:

```python
{
    'type': 'image',
    'url': 'https://example.com/image.jpg',  # URL of the image
    'alt': 'Description of the image',        # Alt text from the image tag
    'description': 'Additional description'    # Description extracted from context
}
```

### Screenshot Capture

The CryptoCrawler can capture a full-page screenshot of the crawled website:

1. When `capture_screenshot` is set to `True` in the configuration, the crawler captures a screenshot of the entire webpage.
2. The screenshot is stored as a base64-encoded string in the `screenshot` field of the `CrawlResult` object.
3. This base64-encoded string can be decoded and saved as a PNG file for viewing or analysis.

### Fallback Mechanism

If the primary image extraction method doesn't yield results, the CryptoCrawler includes a fallback mechanism:

1. If the `media` list is empty but the HTML content is available, the crawler will attempt to extract image URLs directly from the HTML using regular expressions.
2. This ensures that even when the primary extraction method fails, the crawler can still provide some media content.

## Future Enhancements

- **Advanced NLP**: Integration with more sophisticated NLP models for entity and relationship extraction.
- **Multi-language support**: Expansion to support cryptocurrency content in multiple languages.
- **Structured data extraction**: Enhanced extraction of tables, charts, and other structured data from cryptocurrency websites.
- **Real-time crawling**: Support for real-time monitoring and crawling of cryptocurrency news and market data.
- **Advanced media analysis**: Implementation of image recognition and classification for cryptocurrency-related visual content.
- **Video content extraction**: Enhanced support for extracting and analyzing video content from cryptocurrency websites.

## Troubleshooting

### Image Extraction Issues

If you're experiencing issues with image extraction, check the following:

1. **Configuration Parameters**: Ensure that both `capture_screenshot` and `extract_images` are set to `True` in your configuration:

   ```python
   config = {
       # Other parameters...
       "capture_screenshot": True,
       "extract_images": True
   }
   ```

2. **Parameter Passing**: The `CryptoCrawler` class passes these parameters to the underlying `AsyncWebCrawler.arun()` method. If you're extending the `CryptoCrawler` class, ensure that these parameters are correctly passed:

   ```python
   # In your crawl method
   crawl_result = await crawler.arun(
       # Other parameters...
       screenshot=self.capture_screenshot,
       **({'extract_images': self.extract_images} if self.extract_images else {})
   )
   ```

3. **Media Structure**: The `media` field in the `CrawlResult` can be either a dictionary with 'images' and 'videos' keys or a list of media items. Make sure your code handles both structures:

   ```python
   if isinstance(crawl_result.media, dict):
       # Handle dictionary structure
       if 'images' in crawl_result.media:
           # Process images
   elif isinstance(crawl_result.media, list):
       # Handle list structure
       for media_item in crawl_result.media:
           # Process media item
   ```

### Screenshot Capture Issues

If screenshots are not being captured, check the following:

1. **Browser Configuration**: Ensure that the headless browser is properly configured and has permission to capture screenshots.

2. **Memory Constraints**: Screenshot capture can be memory-intensive. If you're processing many pages, consider reducing the frequency of screenshot captures or implementing a cleanup mechanism.

3. **Base64 Encoding**: The screenshot is stored as a base64-encoded string. When saving to a file, ensure you're properly decoding it:

   ```python
   import base64
   if result.screenshot:
       with open("screenshot.png", "wb") as f:
           f.write(base64.b64decode(result.screenshot))
   ```