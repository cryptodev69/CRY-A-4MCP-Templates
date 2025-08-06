#!/usr/bin/env python3
"""
Test module for the NFT extraction strategy.

This module contains tests for the NFT extraction strategy to ensure
it correctly extracts information from NFT-related content.
"""

import os
import sys
import pytest
import json
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

from src.cry_a_4mcp.crawl4ai.extraction_strategies import (
    NFTLLMExtractionStrategy,
    StrategyRegistry,
    StrategyFactory
)

# Sample NFT content for testing
SAMPLE_NFT_CONTENT = """
# CryptoPunks Break Records with $500M in Monthly Sales

The iconic CryptoPunks NFT collection has shattered previous records with over $500 million in trading volume this month, according to data from NFT marketplace OpenSea.

CryptoPunks, one of the earliest and most influential NFT collections on the Ethereum blockchain, has seen unprecedented demand as several high-profile sales have pushed the collection's floor price to 75 ETH (approximately $225,000).

The surge in interest follows Christie's auction house announcing an upcoming curated sale featuring five rare CryptoPunks with alien and ape traits, expected to fetch millions of dollars.

Larva Labs, the creator of CryptoPunks, has also revealed plans for additional utility for CryptoPunk holders, including exclusive access to a new metaverse project in partnership with The Sandbox.

"The cultural significance of CryptoPunks cannot be overstated," said NFT collector and investor 0xWave. "They represent the beginning of the on-chain art movement and continue to be the blue-chip standard in the space."

Notable sales this month include Punk #7804, which sold for 4,200 ETH ($12.6 million), and Punk #3100, which changed hands for 4,000 ETH ($12 million).

The CryptoPunks phenomenon has also sparked interest in other pixel art collections, with Moonbirds and Azuki also seeing significant price appreciation this month.

Industry analysts suggest this trend reflects growing institutional interest in the NFT market, particularly for historically significant collections with limited supply.
"""

# Mock LLM response for testing
MOCK_LLM_RESPONSE = {
    "headline": "CryptoPunks Break Records with $500M in Monthly Sales",
    "summary": "CryptoPunks NFT collection has achieved record-breaking sales of $500 million this month, with the floor price reaching 75 ETH. Notable sales include Punk #7804 for $12.6 million and Punk #3100 for $12 million. Christie's is planning an auction of rare CryptoPunks, and Larva Labs announced new utility features in partnership with The Sandbox.",
    "sentiment": "positive",
    "category": "sales_data",
    "market_impact": {
        "short_term": "Significant price appreciation for CryptoPunks and similar pixel art collections",
        "long_term": "Increased institutional interest in historically significant NFT collections",
        "affected_sectors": ["pixel art NFTs", "blue-chip NFTs", "art auction houses"]
    },
    "key_entities": [
        {
            "name": "CryptoPunks",
            "type": "collection",
            "relevance": "primary",
            "description": "One of the earliest and most influential NFT collections on Ethereum"
        },
        {
            "name": "Larva Labs",
            "type": "company",
            "relevance": "primary",
            "description": "Creator of the CryptoPunks NFT collection"
        },
        {
            "name": "Christie's",
            "type": "company",
            "relevance": "secondary",
            "description": "Auction house planning a sale of rare CryptoPunks"
        },
        {
            "name": "The Sandbox",
            "type": "platform",
            "relevance": "secondary",
            "description": "Metaverse platform partnering with Larva Labs"
        }
    ],
    "nft_data": [
        {
            "collection_name": "CryptoPunks",
            "floor_price": "75 ETH",
            "volume": "$500 million this month",
            "blockchain": "Ethereum",
            "notable_sales": [
                {
                    "item_name": "Punk #7804",
                    "price": "4,200 ETH ($12.6 million)",
                    "date": "This month",
                    "buyer": "Unknown",
                    "seller": "Unknown"
                },
                {
                    "item_name": "Punk #3100",
                    "price": "4,000 ETH ($12 million)",
                    "date": "This month",
                    "buyer": "Unknown",
                    "seller": "Unknown"
                }
            ]
        }
    ],
    "key_points": [
        "CryptoPunks achieved $500 million in monthly trading volume",
        "Floor price has reached 75 ETH (approximately $225,000)",
        "Christie's is planning an auction of rare CryptoPunks",
        "Larva Labs announced new utility features with The Sandbox",
        "Notable sales include Punk #7804 for $12.6 million and Punk #3100 for $12 million"
    ],
    "urgency_score": 7,
    "content_type": "news",
    "publication_date": "2023-05-15",
    "sources": ["OpenSea data"],
    "reliability_score": 8
}

@pytest.mark.asyncio
async def test_nft_extraction_strategy_initialization():
    """Test that the NFT extraction strategy initializes correctly."""
    # Create an instance with default parameters
    strategy = NFTLLMExtractionStrategy(
        provider="openrouter",
        api_token="test_token"
    )
    
    # Check that the strategy is initialized with the correct parameters
    assert strategy.provider == "openrouter"
    assert strategy.api_token == "test_token"
    assert "headline" in strategy.schema["properties"]
    assert "nft_data" in strategy.schema["properties"]
    assert "metaverse_integration" in strategy.schema["properties"]

@pytest.mark.asyncio
async def test_nft_extraction_strategy_extract():
    """Test that the NFT extraction strategy extracts information correctly."""
    # Create a mock for the base class extract method
    with patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.LLMExtractionStrategy.extract') as mock_extract:
        # Configure the mock to return our predefined response
        mock_extract.return_value = MOCK_LLM_RESPONSE
        
        # Create an instance of the NFT extraction strategy
        strategy = NFTLLMExtractionStrategy(
            provider="openrouter",
            api_token="test_token"
        )
        
        # Call the extract method
        result = await strategy.extract("https://example.com", SAMPLE_NFT_CONTENT)
        
        # Verify that the base class extract method was called
        mock_extract.assert_called_once()
        
        # Check that the result contains the expected fields
        assert result["headline"] == "CryptoPunks Break Records with $500M in Monthly Sales"
        assert "summary" in result
        assert result["sentiment"] == "positive"
        assert result["category"] == "sales_data"
        assert "market_impact" in result
        assert "key_entities" in result
        assert "nft_data" in result
        assert "key_points" in result
        assert "urgency_score" in result
        assert "content_type" in result
        assert "_metadata" in result
        assert result["_metadata"]["strategy"] == "nft_llm"

@pytest.mark.asyncio
async def test_nft_extraction_strategy_validation():
    """Test that the NFT extraction strategy validates and fixes extraction results."""
    # Create an instance of the NFT extraction strategy
    strategy = NFTLLMExtractionStrategy(
        provider="openrouter",
        api_token="test_token"
    )
    
    # Create an incomplete extraction result
    incomplete_extraction = {
        "headline": "Test Headline",
        # Missing required fields: summary, sentiment, key_points
        "reliability_score": 15,  # Invalid value (should be 1-10)
        "urgency_score": "high"  # Invalid type (should be number)
    }
    
    # Validate the extraction result
    validated = strategy._validate_nft_extraction(incomplete_extraction)
    
    # Check that required fields were added
    assert "summary" in validated
    assert validated["sentiment"] == "neutral"
    assert "key_points" in validated
    assert isinstance(validated["key_points"], list)
    
    # Check that invalid values were fixed
    assert validated["reliability_score"] == 10  # Clamped to max value
    assert isinstance(validated["urgency_score"], (int, float))  # Converted to number

@pytest.mark.asyncio
async def test_nft_extraction_strategy_enhancement():
    """Test that the NFT extraction strategy enhances extraction results."""
    # Create an instance of the NFT extraction strategy
    strategy = NFTLLMExtractionStrategy(
        provider="openrouter",
        api_token="test_token"
    )
    
    # Create a basic extraction result
    basic_extraction = {
        "headline": "Test Headline",
        "summary": "Test Summary",
        "sentiment": "positive",
        "key_points": ["Point 1", "Point 2"]
    }
    
    # Enhance the extraction result
    enhanced = strategy._enhance_nft_extraction(basic_extraction)
    
    # Check that metadata was added
    assert "_metadata" in enhanced
    assert enhanced["_metadata"]["strategy"] == "nft_llm"
    assert "strategy_version" in enhanced["_metadata"]
    assert "timestamp" in enhanced["_metadata"]
    
    # Check that missing fields were initialized
    assert "key_entities" in enhanced
    assert "nft_data" in enhanced
    assert "technology_aspects" in enhanced
    assert "market_impact" in enhanced
    assert "metaverse_integration" in enhanced
    assert "content_type" in enhanced
    assert "urgency_score" in enhanced
    assert "reliability_score" in enhanced
    assert "publication_date" in enhanced

@pytest.mark.asyncio
async def test_nft_extraction_strategy_content_type_detection():
    """Test that the NFT extraction strategy detects content type correctly."""
    # Create an instance of the NFT extraction strategy
    strategy = NFTLLMExtractionStrategy(
        provider="openrouter",
        api_token="test_token"
    )
    
    # Test news content
    news_content = "Breaking news: New NFT collection launched today"
    news_extraction = {"headline": "Test"}
    news_result = strategy._detect_content_type(news_content, news_extraction)
    assert news_result["content_type"] == "news"
    
    # Test announcement content
    announcement_content = "Announcing our upcoming NFT collection launch"
    announcement_extraction = {"headline": "Test"}
    announcement_result = strategy._detect_content_type(announcement_content, announcement_extraction)
    assert announcement_result["content_type"] == "announcement"
    
    # Test tutorial content
    tutorial_content = "How to mint your first NFT: A step by step guide"
    tutorial_extraction = {"headline": "Test"}
    tutorial_result = strategy._detect_content_type(tutorial_content, tutorial_extraction)
    assert tutorial_result["content_type"] == "tutorial"
    
    # Test with predefined content type (should not change)
    predefined_extraction = {"headline": "Test", "content_type": "interview"}
    predefined_result = strategy._detect_content_type("Any content", predefined_extraction)
    assert predefined_result["content_type"] == "interview"

@pytest.mark.asyncio
async def test_nft_extraction_strategy_preprocessing():
    """Test that the NFT extraction strategy preprocesses content correctly."""
    # Create an instance of the NFT extraction strategy
    strategy = NFTLLMExtractionStrategy(
        provider="openrouter",
        api_token="test_token"
    )
    
    # Test content with various NFT-related terms
    test_content = "The Bored Ape Yacht Club Collection sold for 100 ETH on OpenSea using Ethereum blockchain"
    
    # Preprocess the content
    preprocessed = strategy._preprocess_nft_content(test_content)
    
    # Check that markers were added
    assert "NFT_COLLECTION" in preprocessed
    assert "NFT_PRICE" in preprocessed
    assert "NFT_MARKETPLACE" in preprocessed
    assert "BLOCKCHAIN" in preprocessed

@pytest.mark.asyncio
async def test_strategy_registration():
    """Test that the NFT extraction strategy is properly registered."""
    # Check that the strategy is registered
    assert "NFTLLMExtractionStrategy" in StrategyRegistry.get_all()
    
    # Check that the strategy is in the correct category
    assert "nft" in StrategyRegistry.get_categories()
    assert "NFTLLMExtractionStrategy" in StrategyRegistry.get_by_category("nft")
    
    # Check that the strategy metadata is correct
    metadata = StrategyRegistry.get_metadata("NFTLLMExtractionStrategy")
    assert metadata["name"] == "NFTLLMExtractionStrategy"
    assert metadata["category"] == "nft"
    assert "description" in metadata

@pytest.mark.asyncio
async def test_strategy_factory_creation():
    """Test that the strategy factory can create an NFT extraction strategy."""
    # Mock the actual creation to avoid API calls
    with patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.factory.StrategyFactory._create_instance') as mock_create:
        mock_create.return_value = NFTLLMExtractionStrategy(provider="test", api_token="test")
        
        # Create a strategy using the factory
        strategy = await StrategyFactory.create(
            "NFTLLMExtractionStrategy",
            {"provider": "test", "api_token": "test"}
        )
        
        # Check that the correct strategy was created
        assert isinstance(strategy, NFTLLMExtractionStrategy)
        assert strategy.provider == "test"
        assert strategy.api_token == "test"