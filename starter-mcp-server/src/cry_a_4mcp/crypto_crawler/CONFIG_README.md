# CryptoCrawler Configuration Guide

## Overview

The CryptoCrawler component now supports loading website configurations from a JSON file, making it more flexible and easier to maintain. This document explains how to use this new configuration-based approach.

## Configuration File Structure

The configuration file should be a JSON file with the following structure:

```json
{
  "crypto_websites": [
    {
      "name": "Website Name",
      "url": "https://example.com",
      "content_type": "news",
      "priority": "high",
      "crawl_frequency": "hourly",
      "extraction_focus": ["focus1", "focus2"],
      "persona_relevance": {
        "persona1": 0.8,
        "persona2": 0.5
      }
    },
    // More websites...
  ],
  "crawl4ai_configuration": {
    "user_agent": "CryptoCrawler/1.0",
    "headless": true,
    "bypass_cache": false,
    "word_count_threshold": 100,
    "capture_screenshot": true,
    "extract_images": true,
    "concurrent_crawlers": 5,
    "rate_limiting": {
      "requests_per_minute": 10,
      "delay_between_requests": 6
    }
  }
}
```

### Website Configuration Fields

- `name`: Name of the website (required)
- `url`: URL of the website (required)
- `rss_feed`: RSS feed URL (optional)
- `content_type`: Type of content (e.g., news, market_data, defi_metrics) (required)
- `priority`: Priority level (high, medium, low) (required)
- `crawl_frequency`: How often to crawl (hourly, daily, weekly) (required)
- `extraction_focus`: List of content aspects to focus on (optional)
- `persona_relevance`: Relevance scores for different personas (optional)

### Crawler Configuration Fields

- `user_agent`: User agent string for the crawler
- `headless`: Whether to run the browser in headless mode
- `bypass_cache`: Whether to bypass the cache
- `word_count_threshold`: Minimum word count for content quality
- `capture_screenshot`: Whether to capture screenshots
- `extract_images`: Whether to extract images
- `concurrent_crawlers`: Maximum number of concurrent crawlers
- `rate_limiting`: Rate limiting configuration

## Using the Configuration-Based Approach

### Initializing the Crawler with a Configuration File

```python
from cry_a_4mcp.crawl4ai.crawler import CryptoCrawler

# Initialize with a configuration file
crawler = CryptoCrawler(config_file_path="path/to/config.json")

# Initialize with both a configuration file and additional config parameters
crawler = CryptoCrawler(
    config={"user_agent": "CustomCrawler/1.0"},
    config_file_path="path/to/config.json"
)
```

### Accessing Website Configurations

```python
# Get all websites
all_websites = crawler.websites

# Get a specific website by name
website = crawler.get_website_by_name("Altcoin Season Index")

# Get a specific website by URL
website = crawler.get_website_by_url("https://www.blockchaincenter.net/en/altcoin-season-index/")

# Get websites by content type
news_websites = crawler.get_websites_by_content_type("news")

# Get websites by priority
high_priority_websites = crawler.get_websites_by_priority("high")

# Get websites by crawl frequency
hourly_websites = crawler.get_websites_by_crawl_frequency("hourly")
```

### Crawling Websites

```python
# Crawl a specific website
result = await crawler.crawl_crypto_website(
    url=website["url"],
    content_type=website["content_type"],
    extract_entities=True,
    generate_triples=True
)

# Crawl all websites matching specific criteria
results = await crawler.crawl_all_websites(
    priority="high",
    content_type="news",
    frequency="hourly"
)
```

## Integration with LLMExtractionStrategy

In a future update, the CryptoCrawler will be integrated with the LLMExtractionStrategy to provide AI-powered content extraction and analysis. This will allow for more sophisticated content processing, including:

- Sentiment analysis
- Category classification
- Persona relevance scoring
- Key entity extraction
- Urgency scoring

Stay tuned for updates on this integration.

## Example Usage

See the `test_crypto_crawler_with_config.py` file for a complete example of how to use the configuration-based approach.