# Universal News Crawler

The Universal News Crawler is a comprehensive solution for crawling and analyzing cryptocurrency news and data from various sources. It leverages a JSON configuration file to define sources, crawl frequencies, and extraction parameters.

## Features

- **Configuration-based approach**: All websites, APIs, and crawl settings are defined in a JSON file
- **Multi-tier source management**: Organize sources into tiers (Tier 1, Tier 2, etc.)
- **Persona-based content routing**: Route content to different crypto investor personas
- **LLM-powered content analysis**: Extract structured data from crawled content using LLMs
- **Flexible source filtering**: Filter sources by tier, priority, crawl frequency, or persona relevance
- **Comprehensive crawling**: Support for RSS feeds, web pages, and API endpoints

## Configuration File Structure

The configuration file (`universal_news_crawler_config.json`) has the following structure:

```json
{
  "universal_news_crawler": {
    "description": "Comprehensive news ingestion for all crypto personas",
    "crawl_frequency": "5_minutes",
    "ai_routing": "persona_classification_enabled",
    
    "tier_1_crypto_news": {
      "description": "Primary crypto news sources - highest priority",
      "sources": [
        {
          "name": "CoinDesk",
          "url": "https://www.coindesk.com",
          "rss_feed": "https://www.coindesk.com/arc/outboundfeeds/rss/",
          "api_endpoint": "https://www.coindesk.com/api/v1/articles",
          "priority": "high",
          "crawl_frequency": "2_minutes",
          "extraction_focus": ["breaking_news", "institutional", "regulatory"],
          "persona_relevance": {
            "meme_snipers": 0.3,
            "gem_hunters": 0.8,
            "legacy_investors": 0.9
          }
        },
        // More sources...
      ]
    },
    
    // More tiers and source categories...
    
    "crawl4ai_configuration": {
      "concurrent_crawlers": 20,
      "rate_limiting": {
        "tier_1_sources": "30_requests_per_minute",
        "tier_2_sources": "20_requests_per_minute", 
        "api_sources": "varies_by_provider"
      },
      // More configuration...
    }
  }
}
```

## Source Configuration Fields

Each source in the configuration can have the following fields:

- `name`: Name of the source
- `url`: Website URL
- `rss_feed`: RSS feed URL (if available)
- `api_endpoint`: API endpoint URL (if available)
- `api_key_required`: Whether an API key is required (boolean)
- `priority`: Priority level ("high", "medium", "low")
- `crawl_frequency`: How often to crawl (e.g., "2_minutes", "hourly", "daily")
- `extraction_focus`: List of content types to focus on
- `persona_relevance`: Relevance scores for different personas
- `tier`: Added automatically based on the parent category

## Usage

### Initializing the Crawler

```python
from cry_a_4mcp.crawl4ai.universal_news_crawler import UniversalNewsCrawler

# Initialize the crawler with configuration file
crawler = UniversalNewsCrawler(
    config_file_path="path/to/universal_news_crawler_config.json",
    llm_api_token="your-openai-api-key"  # Optional, for LLM extraction
)
```

### Getting Sources

```python
# Get all sources
all_sources = crawler.get_all_sources()

# Get sources by tier
tier_1_sources = crawler.get_sources_by_tier("tier_1_crypto_news")

# Get sources by priority
high_priority_sources = crawler.get_sources_by_priority("high")

# Get sources by crawl frequency
frequent_sources = crawler.get_sources_by_crawl_frequency("2_minutes")

# Get sources by persona relevance
meme_sources = crawler.get_sources_by_persona_relevance("meme_snipers", min_score=0.7)
```

### Crawling Content

```python
import asyncio

async def run_crawler():
    # Initialize the crawler
    crawler = UniversalNewsCrawler("path/to/config.json")
    
    try:
        # Crawl RSS feeds
        rss_results = await crawler.crawl_rss_feeds(max_articles_per_source=10)
        
        # Crawl web pages
        urls = ["https://www.coindesk.com", "https://cointelegraph.com"]
        web_results = await crawler.crawl_web_pages(urls)
        
        # Fetch API data
        api_results = await crawler.fetch_api_data(["Fear & Greed Index"])
        
        # Run a complete crawl cycle
        await crawler.run_crawl_cycle()
        
        # Route content to personas
        persona_content = crawler.route_to_personas(min_score=0.7)
        print(f"Content for meme snipers: {len(persona_content['meme_snipers'])}")
    
    finally:
        # Close the crawler
        await crawler.close()

# Run the crawler
asyncio.run(run_crawler())
```

## LLM Extraction

When an LLM API token is provided, the crawler can use LLM-based extraction to analyze crawled content. The LLM extraction provides:

- Headline and summary
- Sentiment analysis (bullish, bearish, neutral)
- Content categorization
- Market impact assessment
- Key entity extraction
- Persona relevance scores
- Urgency scoring

## Integration with CryptoCrawler

The Universal News Crawler uses the CryptoCrawler internally for web page crawling. It enhances the CryptoCrawler with:

1. Configuration-based source management
2. Multi-tier source organization
3. Persona-based content routing
4. LLM-powered content analysis
5. Support for RSS feeds and API endpoints

## Running the Crawler

To run the Universal News Crawler:

```bash
python -m cry_a_4mcp.crawl4ai.universal_news_crawler
```

This will load the configuration, print information about the sources, and run a crawl cycle.