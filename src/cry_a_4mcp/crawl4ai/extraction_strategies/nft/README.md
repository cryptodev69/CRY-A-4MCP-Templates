# NFT Extraction Strategy

This module provides specialized extraction strategies for NFT (Non-Fungible Token) related content. The primary strategy is `NFTLLMExtractionStrategy`, which extends the base `LLMExtractionStrategy` with NFT-specific schema, instructions, and processing logic.

## Features

- Specialized schema for NFT content extraction
- Pre-processing to identify NFT collections, prices, marketplaces, and blockchains
- Post-processing for validation and enhancement of extraction results
- Content type detection for NFT-related content

## Schema

The NFT extraction schema includes the following fields:

- **headline**: The title or headline of the content
- **summary**: A concise summary of the content
- **sentiment**: The overall sentiment (positive, negative, neutral, mixed)
- **category**: The category of NFT content (e.g., sales_data, collection_launch, marketplace_update)
- **market_impact**: Impact on the NFT market (short-term, long-term, affected_sectors)
- **key_entities**: Important entities mentioned (name, type, relevance, description)
- **nft_data**: Specific NFT collection data (collection_name, floor_price, volume, blockchain, notable_sales)
- **technology_aspects**: Technical aspects of the NFTs (standards, features, innovations)
- **metaverse_integration**: Information about metaverse integration
- **key_points**: List of key points from the content
- **urgency_score**: Numeric score indicating urgency (1-10)
- **content_type**: Type of content (news, analysis, announcement, tutorial, etc.)
- **publication_date**: Date of publication
- **sources**: Sources of information
- **reliability_score**: Numeric score indicating reliability (1-10)

## Usage

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import NFTLLMExtractionStrategy

# Create an instance of the strategy
strategy = NFTLLMExtractionStrategy(
    provider="openrouter",  # LLM provider
    api_token="your_api_token",  # API token for the provider
    model="gpt-4"  # Optional: Specify a model
)

# Extract information from NFT content
result = await strategy.extract(
    url="https://example.com/nft-article",
    content="Article content about NFTs..."
)

# Access extracted information
print(result["headline"])
print(result["summary"])
print(result["nft_data"])
```

## Factory Creation

You can also create the strategy using the `StrategyFactory`:

```python
from cry_a_4mcp.crawl4ai.extraction_strategies import StrategyFactory

# Create a strategy using the factory
strategy = await StrategyFactory.create(
    "NFTLLMExtractionStrategy",
    {
        "provider": "openrouter",
        "api_token": "your_api_token",
        "model": "gpt-4"  # Optional
    }
)
```

## Example

See `nft_extraction_example.py` for a complete example of using the NFT extraction strategy.