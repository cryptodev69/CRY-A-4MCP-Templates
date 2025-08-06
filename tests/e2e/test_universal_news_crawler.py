import asyncio
import os
import sys
from typing import Dict, List, Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from cry_a_4mcp.crawl4ai.universal_news_crawler import UniversalNewsCrawler


async def test_universal_news_crawler():
    """Test the UniversalNewsCrawler class."""
    # Path to the configuration file
    config_file_path = os.path.join(
        os.path.dirname(__file__),
        'sample-data/crawled_content/universal_news_crawler_config.json'
    )
    
    print(f"Loading configuration from: {config_file_path}")
    
    # Create a UniversalNewsCrawler instance
    # Note: Replace with your actual API token if using LLM extraction
    crawler = UniversalNewsCrawler(
        config_file_path=config_file_path,
        llm_api_token=None  # Set to your API token to enable LLM extraction
    )
    
    try:
        # Print information about loaded sources
        all_sources = crawler.get_all_sources()
        print(f"Loaded {len(all_sources)} sources from configuration")
        
        # Print sources by tier
        for tier in ["tier_1_crypto_news", "tier_2_crypto_news", "crypto_aggregators", "market_indicators"]:
            tier_sources = crawler.get_sources_by_tier(tier)
            print(f"\n{tier} sources ({len(tier_sources)}):")
            for source in tier_sources[:3]:  # Print first 3 sources
                print(f"  - {source['name']} (frequency: {source.get('crawl_frequency', 'N/A')})")
            if len(tier_sources) > 3:
                print(f"  ... and {len(tier_sources) - 3} more sources")
        
        # Print high priority sources
        high_priority_sources = crawler.get_sources_by_priority("high")
        print(f"\nHigh priority sources ({len(high_priority_sources)}):")
        for source in high_priority_sources[:5]:  # Print first 5 sources
            print(f"  - {source['name']} ({source.get('tier', 'unknown')})")
        if len(high_priority_sources) > 5:
            print(f"  ... and {len(high_priority_sources) - 5} more sources")
        
        # Print sources by crawl frequency
        for frequency in ["2_minutes", "5_minutes", "1_hour", "daily"]:
            freq_sources = crawler.get_sources_by_crawl_frequency(frequency)
            if freq_sources:
                print(f"\nSources with {frequency} frequency ({len(freq_sources)}):")
                for source in freq_sources[:3]:  # Print first 3 sources
                    print(f"  - {source['name']} ({source.get('tier', 'unknown')})")
                if len(freq_sources) > 3:
                    print(f"  ... and {len(freq_sources) - 3} more sources")
        
        # Print sources by persona relevance
        for persona in ["meme_snipers", "gem_hunters", "legacy_investors"]:
            persona_sources = crawler.get_sources_by_persona_relevance(persona, 0.7)
            if persona_sources:
                print(f"\nSources relevant to {persona} ({len(persona_sources)}):")
                for source in persona_sources[:3]:  # Print first 3 sources
                    relevance = source.get("persona_relevance", {}).get(persona, 0)
                    print(f"  - {source['name']} (relevance: {relevance})")
                if len(persona_sources) > 3:
                    print(f"  ... and {len(persona_sources) - 3} more sources")
        
        # Run a limited crawl cycle (uncomment to test actual crawling)
        # print("\nRunning a limited crawl cycle...")
        # await crawler.run_crawl_cycle()
        
    finally:
        # Ensure crawler is properly closed
        await crawler.close()
        print("\nCrawler closed properly")


if __name__ == "__main__":
    asyncio.run(test_universal_news_crawler())