#!/usr/bin/env python3

"""
Convert Universal News Crawler config to CryptoCrawler config.

This script converts the universal_news_crawler_config.json file to a format
compatible with the CryptoCrawler class.
"""

import json
import os
import sys
from typing import Dict, List, Any


def convert_config(universal_config_path: str, output_path: str) -> None:
    """Convert Universal News Crawler config to CryptoCrawler config.
    
    Args:
        universal_config_path: Path to the universal_news_crawler_config.json file
        output_path: Path to save the converted crypto_website_config.json file
    """
    # Load the universal config
    with open(universal_config_path, 'r') as f:
        universal_config = json.load(f)
    
    # Initialize the crypto config
    crypto_config = {
        "crypto_websites": [],
        "crawl4ai_configuration": {}
    }
    
    # Extract the crawl4ai configuration
    if "universal_news_crawler" in universal_config and "crawl4ai_configuration" in universal_config["universal_news_crawler"]:
        crypto_config["crawl4ai_configuration"] = universal_config["universal_news_crawler"]["crawl4ai_configuration"]
    else:
        # Default configuration
        crypto_config["crawl4ai_configuration"] = {
            "user_agent": "CryptoCrawler/1.0",
            "headless": True,
            "cache_bypass": True,
            "word_count_threshold": 100,
            "capture_screenshot": True,
            "extract_images": True,
            "concurrent_crawlers": 10,
            "rate_limiting": {
                "default": "10_requests_per_minute"
            }
        }
    
    # Extract websites from all tiers
    for tier_key, tier_data in universal_config.get("universal_news_crawler", {}).items():
        if isinstance(tier_data, dict) and "sources" in tier_data:
            for source in tier_data["sources"]:
                # Skip sources without a URL
                if "url" not in source:
                    continue
                
                # Create a website entry
                website = {
                    "name": source.get("name", "Unknown"),
                    "url": source["url"],
                    "content_type": determine_content_type(source, tier_key),
                    "priority": source.get("priority", "medium"),
                    "crawl_frequency": source.get("crawl_frequency", "daily"),
                    "extraction_focus": source.get("extraction_focus", []),
                    "persona_relevance": source.get("persona_relevance", {})
                }
                
                crypto_config["crypto_websites"].append(website)
    
    # Save the crypto config
    with open(output_path, 'w') as f:
        json.dump(crypto_config, f, indent=2)
    
    print(f"Converted {len(crypto_config['crypto_websites'])} websites from universal config to crypto config")
    print(f"Saved to {output_path}")


def determine_content_type(source: Dict[str, Any], tier_key: str) -> str:
    """Determine the content type based on the source and tier.
    
    Args:
        source: Source dictionary
        tier_key: Tier key
        
    Returns:
        Content type string
    """
    # Check if content_type is explicitly defined
    if "content_type" in source:
        return source["content_type"]
    
    # Determine based on tier and source properties
    if "tier_1_crypto_news" in tier_key or "tier_2_crypto_news" in tier_key:
        return "news"
    elif "crypto_aggregators" in tier_key:
        return "aggregator"
    elif "market_indicators" in tier_key:
        return "market_data"
    elif "federal_reserve_macro" in tier_key:
        return "macro_data"
    elif "specialized_sources" in tier_key:
        if "defi" in source.get("name", "").lower() or any("defi" in focus.lower() for focus in source.get("extraction_focus", [])):
            return "defi"
        elif "nft" in source.get("name", "").lower() or any("nft" in focus.lower() for focus in source.get("extraction_focus", [])):
            return "nft"
        else:
            return "specialized"
    else:
        return "general"


def main():
    """Main function."""
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Set paths
    universal_config_path = os.path.join(
        project_root,
        'sample-data/crawled_content/universal_news_crawler_config.json'
    )
    output_path = os.path.join(
        project_root,
        'src/cry_a_4mcp/crawl4ai/crypto_website_config.json'
    )
    
    # Convert the config
    convert_config(universal_config_path, output_path)


if __name__ == "__main__":
    main()