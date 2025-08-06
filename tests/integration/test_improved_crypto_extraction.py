#!/usr/bin/env python3
"""
Test script for the improved CryptoLLMExtractionStrategy.

This script demonstrates the enhanced features:
1. Improved error handling and logging
2. Performance optimization
3. Model and provider flexibility
"""

import asyncio
import os
import sys
import json
import logging
import time
from typing import Dict, Optional, Any
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the improved extraction strategies
from cry_a_4mcp.crawl4ai.extraction_strategy_improved import LLMExtractionStrategy, APIConnectionError, APIResponseError
from cry_a_4mcp.crawl4ai.crypto_extraction_strategy import CryptoLLMExtractionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('extraction_test.log')
    ]
)
logger = logging.getLogger('test_extraction')

# Sample crypto content for testing
SAMPLE_CONTENT = """
Bitcoin Surges Past $60,000 as Institutional Adoption Accelerates

Bitcoin has surpassed the $60,000 mark for the first time in two weeks, driven by increasing institutional adoption and positive market sentiment. The cryptocurrency market has shown strong recovery following recent regulatory clarity from several major economies.

Key developments include:

1. BlackRock's Bitcoin ETF saw inflows of over $500 million in the past week
2. El Salvador announced plans to build a "Bitcoin City" funded by crypto-bonds
3. Major payment processor Stripe expanded its cryptocurrency payment options
4. Federal Reserve Chairman Jerome Powell stated that the U.S. has no intention to ban cryptocurrencies

Market analysts suggest this could be the beginning of a new bull run, with some predicting Bitcoin could reach $100,000 by year-end. However, others caution that volatility remains high and regulatory challenges persist in some regions.

Trading volume across major exchanges has increased by 30% compared to last month, indicating renewed interest from both retail and institutional investors.

Ethereum has also shown strong performance, climbing above $4,000 as the network prepares for its next major upgrade. The DeFi sector continues to grow, with total value locked (TVL) reaching new all-time highs.

Meme coins like Dogecoin and Shiba Inu have seen increased volatility, with social media mentions driving price action more than fundamental developments.
"""


async def test_provider_flexibility():
    """Test the flexibility to use different providers and models."""
    logger.info("=== Testing Provider and Model Flexibility ===")
    
    # Get API keys from environment variables
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        return
    
    # Get available providers and models
    providers = LLMExtractionStrategy.get_available_providers()
    logger.info(f"Available providers: {', '.join(providers)}")
    
    # Test with OpenRouter provider
    logger.info("Testing with OpenRouter provider...")
    openrouter_models = LLMExtractionStrategy.get_available_models("openrouter")
    logger.info(f"Available OpenRouter models: {', '.join(openrouter_models)}")
    
    # Create extraction strategy with OpenRouter
    # Try different models in case of rate limiting
    models_to_try = [
        "moonshotai/kimi-k2:free",
        "qwen/qwen-2.5-72b-instruct:free",
        "mistralai/mistral-small-24b-instruct-2501:free"
    ]
    
    # Try each model until one works
    extraction_strategy = None
    last_error = None
    
    for model in models_to_try:
        try:
            logger.info(f"Attempting to use model: {model}")
            extraction_strategy = CryptoLLMExtractionStrategy(
                provider="openrouter",
                api_token=openrouter_api_key,
                model=model
            )
            
            # Validate connection
            success, error = await extraction_strategy.validate_provider_connection()
            if success:
                logger.info(f"Successfully connected to OpenRouter with model {model}")
                break
            else:
                logger.warning(f"Failed to connect with model {model}: {error}")
                last_error = error
        except Exception as e:
            logger.warning(f"Error initializing with model {model}: {str(e)}")
            last_error = str(e)
    
    if extraction_strategy is None:
        logger.error(f"Failed to initialize with any model: {last_error}")
        return
    
    # Validate connection
    success, error = await extraction_strategy.validate_provider_connection()
    if success:
        logger.info("Successfully connected to OpenRouter")
    else:
        logger.error(f"Failed to connect to OpenRouter: {error}")
        return
    
    # Test extraction
    try:
        result = await extraction_strategy.extract(
            url="https://example.com/crypto-news",
            html=SAMPLE_CONTENT
        )
        logger.info(f"Extraction successful with OpenRouter model {result.get('_metadata', {}).get('model', 'unknown')}")
        print_extraction_result(result)
    except Exception as e:
        logger.error(f"Extraction failed with OpenRouter: {str(e)}")


async def test_error_handling():
    """Test the improved error handling capabilities."""
    logger.info("\n=== Testing Error Handling ===")
    
    # Get API key from environment variable
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        return
    
    # Test with invalid API key
    logger.info("Testing with invalid API key...")
    try:
        invalid_strategy = CryptoLLMExtractionStrategy(
            provider="openrouter",
            api_token="invalid_key",
            base_url="https://openrouter.ai/api/v1"
        )
        
        # First test the connection validation
        success, error = await invalid_strategy.validate_provider_connection()
        if not success:
            logger.info(f"Successfully detected invalid API key during validation: {error}")
        else:
            logger.warning("Unexpected success with invalid API key during validation")
            
        # Then test the extraction
        try:
            result = await invalid_strategy.extract(
                url="https://example.com/crypto-news",
                html=SAMPLE_CONTENT
            )
            logger.warning("Unexpected success with invalid API key during extraction")
        except APIResponseError as e:
            logger.info(f"Successfully caught API response error: {e.status_code} - {e.message[:100]}...")
        except APIConnectionError as e:
            logger.info(f"Successfully caught API connection error: {str(e)}")
        except Exception as e:
            logger.info(f"Caught unexpected error: {str(e)}")
    except Exception as e:
        logger.info(f"Error during invalid API key test: {str(e)}")
    
    # Test with empty content
    logger.info("\nTesting with empty content...")
    try:
        # Try different models in case of rate limiting
        models_to_try = [
            "moonshotai/kimi-k2:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "mistralai/mistral-small-24b-instruct-2501:free"
        ]
        
        valid_strategy = None
        
        for model in models_to_try:
            try:
                logger.info(f"Attempting to use model: {model} for empty content test")
                valid_strategy = CryptoLLMExtractionStrategy(
                    provider="openrouter",
                    api_token=openrouter_api_key,
                    base_url="https://openrouter.ai/api/v1",
                    model=model
                )
                
                # Validate connection
                success, error = await valid_strategy.validate_provider_connection()
                if success:
                    logger.info(f"Successfully connected to OpenRouter with model {model}")
                    break
                else:
                    logger.warning(f"Failed to connect with model {model}: {error}")
            except Exception as e:
                logger.warning(f"Error initializing with model {model}: {str(e)}")
        
        if valid_strategy is None:
            logger.error("Failed to initialize with any model for empty content test")
            return
        
        # Test with empty content
        try:
            result = await valid_strategy.extract(
                url="https://example.com/empty",
                html=""
            )
            logger.info("Extraction with empty content completed")
            logger.info(f"Result with empty content: {json.dumps(result)[:200]}...")
        except Exception as e:
            logger.info(f"Caught error with empty content: {str(e)}")
    except Exception as e:
        logger.info(f"Error during empty content test: {str(e)}")


async def test_performance_optimization():
    """Test the performance optimization features."""
    logger.info("\n=== Testing Performance Optimization ===")
    
    # Get API key from environment variable
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        return
    
    # Try different models in case of rate limiting
    models_to_try = [
        "moonshotai/kimi-k2:free",
        "qwen/qwen-2.5-72b-instruct:free",
        "mistralai/mistral-small-24b-instruct-2501:free"
    ]
    
    # Try each model until one works
    extraction_strategy = None
    last_error = None
    
    for model in models_to_try:
        try:
            logger.info(f"Attempting to use model: {model}")
            extraction_strategy = CryptoLLMExtractionStrategy(
                provider="openrouter",
                api_token=openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                model=model
            )
            
            # Validate connection
            success, error = await extraction_strategy.validate_provider_connection()
            if success:
                logger.info(f"Successfully connected to OpenRouter with model {model}")
                break
            else:
                logger.warning(f"Failed to connect with model {model}: {error}")
                last_error = error
        except Exception as e:
            logger.warning(f"Error initializing with model {model}: {str(e)}")
            last_error = str(e)
    
    if extraction_strategy is None:
        logger.error(f"Failed to initialize with any model: {last_error}")
        return
    
    # Test with normal content
    logger.info("Testing with normal content...")
    start_time = time.time()
    result = await extraction_strategy.extract(
        url="https://example.com/crypto-news",
        html=SAMPLE_CONTENT
    )
    normal_time = time.time() - start_time
    logger.info(f"Normal extraction completed in {normal_time:.2f} seconds")
    
    # Test with very long content to see content truncation
    logger.info("Testing with long content...")
    long_content = SAMPLE_CONTENT * 10  # Repeat the content 10 times
    start_time = time.time()
    result = await extraction_strategy.extract(
        url="https://example.com/long-crypto-news",
        html=long_content
    )
    long_time = time.time() - start_time
    logger.info(f"Long content extraction completed in {long_time:.2f} seconds")
    
    # Check if performance data is included in metadata
    if "_metadata" in result and "performance" in result["_metadata"]:
        perf_data = result["_metadata"]["performance"]
        logger.info(f"Performance data: {json.dumps(perf_data)}")


def print_extraction_result(extraction: Optional[Dict[str, Any]]) -> None:
    """Print details of an extraction result."""
    print("\nExtraction Result:")
    if not extraction:
        print("  No extraction result available")
        return
    
    # Print headline and summary
    if "headline" in extraction:
        print(f"Headline: {extraction['headline']}")
    if "summary" in extraction:
        print(f"Summary: {extraction['summary']}")
    
    # Print sentiment and category
    if "sentiment" in extraction:
        print(f"Sentiment: {extraction['sentiment']}")
    if "category" in extraction:
        print(f"Category: {extraction['category']}")
    if "market_impact" in extraction:
        print(f"Market Impact: {extraction['market_impact']}")
    
    # Print key entities
    if "key_entities" in extraction and extraction["key_entities"]:
        print("\nKey Entities:")
        for entity in extraction["key_entities"]:
            print(f"  - {entity['name']} ({entity['type']}): {entity.get('relevance', 'N/A')}")
    
    # Print persona relevance
    if "persona_relevance" in extraction:
        print("\nPersona Relevance:")
        for persona, score in extraction["persona_relevance"].items():
            print(f"  - {persona}: {score}")
    
    # Print urgency score
    if "urgency_score" in extraction:
        print(f"\nUrgency Score: {extraction['urgency_score']}/10")
    
    # Print price mentions
    if "price_mentions" in extraction and extraction["price_mentions"]:
        print("\nPrice Mentions:")
        for price in extraction["price_mentions"]:
            print(f"  - {price['token']}: {price['price']} ({price.get('change', 'N/A')})")
    
    # Print metadata if available
    if "_metadata" in extraction:
        print("\nMetadata:")
        metadata = extraction["_metadata"]
        if "model" in metadata:
            print(f"  Model: {metadata['model']}")
        if "usage" in metadata:
            usage = metadata["usage"]
            print(f"  Tokens: {usage.get('total_tokens', 'N/A')} (Prompt: {usage.get('prompt_tokens', 'N/A')}, Completion: {usage.get('completion_tokens', 'N/A')})")
        if "performance" in metadata:
            perf = metadata["performance"]
            print(f"  Extraction Time: {perf.get('extraction_time', 'N/A'):.2f} seconds")
        if "strategy" in metadata:
            print(f"  Strategy: {metadata['strategy']} v{metadata.get('strategy_version', 'N/A')}")
        if "timestamp" in metadata:
            timestamp = datetime.fromtimestamp(metadata["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  Timestamp: {timestamp}")


async def main():
    """Run all tests."""
    logger.info("Starting improved extraction strategy tests")
    
    try:
        # Test provider flexibility
        await test_provider_flexibility()
        
        # Test error handling
        await test_error_handling()
        
        # Test performance optimization
        await test_performance_optimization()
        
        logger.info("All tests completed")
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())