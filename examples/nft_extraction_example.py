#!/usr/bin/env python3
"""
Example script demonstrating the use of the NFT extraction strategy.

This script shows how to use the NFT extraction strategy to extract
information from NFT-related content.
"""

import asyncio
import json
import os
import sys
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

# Import the extraction strategies
from src.cry_a_4mcp.crawl4ai.extraction_strategies import (
    NFTLLMExtractionStrategy,
    StrategyRegistry,
    StrategyFactory
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('nft_extraction_example')

# Example NFT content for extraction
EXAMPLE_URL = "https://example.com/nft-news"
EXAMPLE_CONTENT = """
# Bored Ape Yacht Club Floor Price Surges Following Yuga Labs' Otherside Metaverse Announcement

The floor price of the popular Bored Ape Yacht Club (BAYC) NFT collection has surged by over 25% in the past 24 hours, reaching 120 ETH (approximately $360,000) following Yuga Labs' highly anticipated announcement about their upcoming Otherside metaverse project.

Yuga Labs, the company behind BAYC, revealed detailed plans for Otherside, a gamified metaverse that will integrate various NFT collections, starting with their own BAYC, Mutant Ape Yacht Club (MAYC), and Bored Ape Kennel Club (BAKC). The announcement has generated significant excitement in the NFT community.

"This is a transformative moment for the BAYC ecosystem," said Gordon Goner, one of the founders of Yuga Labs. "Otherside will bring utility and interactivity to NFTs in ways we've only dreamed of until now."

The metaverse project will feature land sales, with BAYC and MAYC holders receiving priority access. The initial land sale is expected to generate over $300 million, according to industry analysts.

Trading volume on OpenSea for BAYC has increased by 400% since the announcement, with several notable sales including Ape #8817 selling for a record 200 ETH ($600,000) to a prominent NFT collector known as Pranksy.

Other blue-chip NFT collections have also seen price increases following the news, with CryptoPunks up 15% and Azuki rising 30%, suggesting a broader market impact.

The Otherside metaverse will be built on Ethereum with layer-2 integration to address gas fee concerns. It will feature an immersive 3D environment where users can interact, play games, and build experiences using their NFT avatars.

Industry experts view this development as a significant step forward for NFT utility beyond simple profile pictures.

"What Yuga Labs is building could redefine how we think about digital ownership and interaction in virtual worlds," said Jane Smith, blockchain analyst at Digital Asset Research. "The integration of multiple collections into a cohesive metaverse experience could set new standards for the industry."

The first phase of Otherside is scheduled to launch in Q3 2022, with early access for BAYC and MAYC holders starting next month.
"""

async def run_nft_extraction_example():
    """Run an example of the NFT extraction strategy."""
    # Get API token from environment variable
    api_token = os.environ.get("OPENROUTER_API_KEY")
    if not api_token:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        return
    
    logger.info("Starting NFT extraction example")
    
    # Create an instance of the NFT extraction strategy
    nft_strategy = NFTLLMExtractionStrategy(
        provider="openrouter",
        api_token=api_token
    )
    
    try:
        # Extract information from the example content
        nft_result = await nft_strategy.extract(EXAMPLE_URL, EXAMPLE_CONTENT)
        logger.info(f"NFT extraction result:\n{json.dumps(nft_result, indent=2)}")
    except Exception as e:
        logger.error(f"NFT extraction failed: {str(e)}")
    
    # Example using the strategy factory
    logger.info("\nUsing StrategyFactory to create NFT extraction strategy")
    try:
        factory_strategy = await StrategyFactory.create(
            "NFTLLMExtractionStrategy",
            {"provider": "openrouter", "api_token": api_token}
        )
        factory_result = await factory_strategy.extract(EXAMPLE_URL, EXAMPLE_CONTENT)
        logger.info(f"Factory-created strategy result:\n{json.dumps(factory_result, indent=2)}")
    except Exception as e:
        logger.error(f"Factory-created strategy failed: {str(e)}")
    
    # List available strategies from the registry
    logger.info("\nListing available strategies from the registry")
    strategies = StrategyRegistry.get_all()
    logger.info(f"Available strategies: {', '.join(strategies.keys())}")
    
    categories = StrategyRegistry.get_categories()
    logger.info(f"Available categories: {', '.join(categories)}")
    
    # Check if our new NFT category is available
    if "nft" in categories:
        nft_strategies = StrategyRegistry.get_by_category("nft")
        logger.info(f"Strategies in category 'nft': {', '.join(nft_strategies.keys())}")
    
    logger.info("NFT extraction example completed")

if __name__ == "__main__":
    asyncio.run(run_nft_extraction_example())