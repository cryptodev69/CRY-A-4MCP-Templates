#!/usr/bin/env python3
"""
Comprehensive test suite for extraction strategies.

This module provides tests for different extraction strategies,
including comparison testing and benchmarking.
"""

import os
import sys
import json
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import argparse
import statistics

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cry_a_4mcp.crawl4ai.extraction_strategy_improved import LLMExtractionStrategy
from src.cry_a_4mcp.crawl4ai.crypto_extraction_strategy import CryptoLLMExtractionStrategy
from src.cry_a_4mcp.crawl4ai.content_preprocessor import preprocess_html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Sample content for testing
SAMPLE_CONTENT = """
# Bitcoin Surges Past $50,000 as Institutional Adoption Grows

Bitcoin has surged past the $50,000 mark for the first time in several weeks, 
driven by growing institutional adoption and positive market sentiment. 
The cryptocurrency market has been showing signs of recovery after a period of volatility.

Analysts at major investment banks have revised their price targets upward, 
with some suggesting Bitcoin could reach $75,000 by the end of the year. 
The positive outlook comes as more financial institutions announce plans to offer 
cryptocurrency services to their clients.

"We're seeing unprecedented interest from traditional financial players," 
said Jane Smith, crypto analyst at InvestBank. "This is no longer just about retail investors."

Ethereum has also performed well, climbing above $3,000 as the network prepares for 
its next major upgrade. The overall cryptocurrency market capitalization has increased 
by 15% in the past week alone.

However, regulatory concerns remain, with authorities in several countries 
considering new frameworks for cryptocurrency oversight.
"""

# Sample HTML content for testing preprocessing
SAMPLE_HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Bitcoin Surges Past $50,000 as Institutional Adoption Grows</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .hidden { display: none; }
    </style>
    <script>
        console.log("This should be removed");
    </script>
</head>
<body>
    <h1>Bitcoin Surges Past $50,000 as Institutional Adoption Grows</h1>
    
    <p>Bitcoin has surged past the $50,000 mark for the first time in several weeks, 
    driven by growing institutional adoption and positive market sentiment. 
    The cryptocurrency market has been showing signs of recovery after a period of volatility.</p>
    
    <p>Analysts at major investment banks have revised their price targets upward, 
    with some suggesting Bitcoin could reach $75,000 by the end of the year. 
    The positive outlook comes as more financial institutions announce plans to offer 
    cryptocurrency services to their clients.</p>
    
    <blockquote>
        "We're seeing unprecedented interest from traditional financial players," 
        said Jane Smith, crypto analyst at InvestBank. "This is no longer just about retail investors."
    </blockquote>
    
    <p>Ethereum has also performed well, climbing above $3,000 as the network prepares for 
    its next major upgrade. The overall cryptocurrency market capitalization has increased 
    by 15% in the past week alone.</p>
    
    <h2>Market Data</h2>
    <table border="1">
        <caption>Top Cryptocurrencies by Market Cap</caption>
        <thead>
            <tr>
                <th>Cryptocurrency</th>
                <th>Price (USD)</th>
                <th>24h Change</th>
                <th>Market Cap (USD)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Bitcoin (BTC)</td>
                <td>$50,235</td>
                <td>+5.2%</td>
                <td>$950B</td>
            </tr>
            <tr>
                <td>Ethereum (ETH)</td>
                <td>$3,120</td>
                <td>+3.8%</td>
                <td>$365B</td>
            </tr>
            <tr>
                <td>Binance Coin (BNB)</td>
                <td>$420</td>
                <td>+2.1%</td>
                <td>$70B</td>
            </tr>
        </tbody>
    </table>
    
    <h2>Key Factors Driving the Rally</h2>
    <ul>
        <li>Increased institutional adoption</li>
        <li>Positive regulatory developments in some jurisdictions</li>
        <li>Technical breakout above key resistance levels</li>
        <li>Reduced selling pressure from miners</li>
    </ul>
    
    <h2>Potential Risks</h2>
    <ol>
        <li>Regulatory crackdowns in major markets</li>
        <li>Macroeconomic factors affecting risk assets</li>
        <li>Technical correction after rapid price increase</li>
    </ol>
    
    <div class="hidden">
        This content should not be visible or extracted.
    </div>
    
    <!-- This is a comment that should be removed -->
    
    <p>However, regulatory concerns remain, with authorities in several countries 
    considering new frameworks for cryptocurrency oversight.</p>
</body>
</html>
"""

# Sample social media content for testing
SAMPLE_SOCIAL_MEDIA_CONTENT = """
@CryptoExpert: Just bought more #Bitcoin at $50k! This rally has legs. Institutions are just getting started. 🚀 #BTC #Crypto

Replies:
@Trader123: Brave move! I'm waiting for a pullback to $45k before adding to my position.
@BTCSkeptic: Be careful, this looks like a bull trap. Remember 2017?
@CryptoExpert: @BTCSkeptic The fundamentals are completely different now. Institutional money changes everything.

Likes: 1,245
Retweets: 328
Timestamp: 2023-04-15 14:32:00
"""

# Sample news article for testing
SAMPLE_NEWS_CONTENT = """
# SEC Approves Bitcoin ETF Applications from Multiple Firms

In a landmark decision, the U.S. Securities and Exchange Commission (SEC) has approved 
Bitcoin exchange-traded fund (ETF) applications from several major financial firms. 
This decision comes after years of rejections and delays, marking a significant milestone 
for cryptocurrency adoption in traditional finance.

The approved ETFs will allow investors to gain exposure to Bitcoin through regulated 
investment vehicles without directly owning the cryptocurrency. Analysts expect this 
development to bring billions of dollars of new investment into the crypto market.

"This is a watershed moment for cryptocurrency," said Michael Johnson, Chief Investment 
Officer at Global Investments. "It legitimizes Bitcoin as an asset class and opens the 
door for institutional investors who have been sitting on the sidelines."

Trading of the new Bitcoin ETFs is expected to begin next week on major exchanges. 
The price of Bitcoin surged by over 10% following the announcement, reaching a new 
all-time high.

The SEC's decision includes strict requirements for custody, surveillance sharing, 
and investor protection. Commissioner Hester Peirce, known as "Crypto Mom" for her 
supportive stance on digital assets, called the approval "long overdue."

Cryptocurrency advocates have hailed the decision as validation of Bitcoin's staying 
power and importance in the modern financial ecosystem.
"""


async def test_provider_flexibility():
    """Test the flexibility of different providers."""
    logger.info("\n=== Testing Provider Flexibility ===")
    
    # Get API keys from environment variables
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    groq_api_key = os.environ.get("GROQ_API_KEY")
    
    if not any([openai_api_key, openrouter_api_key, groq_api_key]):
        logger.error("No API keys found in environment variables. Skipping test.")
        return
    
    # List available providers and models
    providers = LLMExtractionStrategy.get_available_providers()
    logger.info(f"Available providers: {providers}")
    
    for provider in providers:
        models = LLMExtractionStrategy.get_available_models(provider)
        logger.info(f"Available models for {provider}: {models}")
    
    # Try to initialize with different providers
    strategies = []
    
    if openai_api_key:
        try:
            strategy = CryptoLLMExtractionStrategy(
                provider="openai",
                api_token=openai_api_key,
                model="gpt-3.5-turbo"
            )
            await strategy.validate_provider_connection()
            strategies.append(("OpenAI", strategy))
            logger.info("Successfully connected to OpenAI")
        except Exception as e:
            logger.warning(f"Failed to connect to OpenAI: {str(e)}")
    
    if openrouter_api_key:
        try:
            strategy = CryptoLLMExtractionStrategy(
                provider="openrouter",
                api_token=openrouter_api_key,
                model="mistralai/mistral-small-24b-instruct-2501:free"
            )
            await strategy.validate_provider_connection()
            strategies.append(("OpenRouter", strategy))
            logger.info("Successfully connected to OpenRouter")
        except Exception as e:
            logger.warning(f"Failed to connect to OpenRouter: {str(e)}")
    
    if groq_api_key:
        try:
            strategy = CryptoLLMExtractionStrategy(
                provider="groq",
                api_token=groq_api_key,
                model="llama3-70b-8192"
            )
            await strategy.validate_provider_connection()
            strategies.append(("Groq", strategy))
            logger.info("Successfully connected to Groq")
        except Exception as e:
            logger.warning(f"Failed to connect to Groq: {str(e)}")
    
    if not strategies:
        logger.error("Could not connect to any provider. Skipping extraction test.")
        return
    
    # Try extraction with the first successful strategy
    provider_name, strategy = strategies[0]
    logger.info(f"Testing extraction with {provider_name}")
    
    try:
        result = await strategy.extract(SAMPLE_CONTENT)
        logger.info(f"Extraction successful with {provider_name}")
        print_extraction_result(result)
    except Exception as e:
        logger.error(f"Extraction failed with {provider_name}: {str(e)}")


async def test_error_handling():
    """Test error handling in extraction strategies."""
    logger.info("\n=== Testing Error Handling ===")
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENROUTER_API_KEY")
    
    if not api_key:
        logger.error("No API key found in environment variables. Skipping test.")
        return
    
    # Test with invalid API key
    logger.info("Testing with invalid API key")
    try:
        strategy = CryptoLLMExtractionStrategy(
            provider="openrouter",
            api_token="invalid_key",
            model="mistralai/mistral-small-24b-instruct-2501:free"
        )
        await strategy.validate_provider_connection()
        logger.error("Connection validation should have failed with invalid API key")
    except Exception as e:
        logger.info(f"Expected error occurred: {str(e)}")
    
    # Test with empty content
    logger.info("Testing with empty content")
    
    # Try to find a working model
    models = [
        "mistralai/mistral-small-24b-instruct-2501:free",
        "qwen/qwen-2.5-72b-instruct:free",
        "moonshotai/kimi-k2:free"
    ]
    
    strategy = None
    for model in models:
        try:
            strategy = CryptoLLMExtractionStrategy(
                provider="openrouter",
                api_token=api_key,
                model=model
            )
            await strategy.validate_provider_connection()
            logger.info(f"Successfully connected with model {model}")
            break
        except Exception as e:
            logger.warning(f"Failed to connect with model {model}: {str(e)}")
    
    if not strategy:
        logger.error("Could not connect to any model. Skipping empty content test.")
        return
    
    try:
        result = await strategy.extract("")
        logger.error("Extraction should have failed with empty content")
    except Exception as e:
        logger.info(f"Expected error occurred: {str(e)}")


async def test_content_preprocessing():
    """Test content preprocessing before extraction."""
    logger.info("\n=== Testing Content Preprocessing ===")
    
    # Preprocess HTML content
    try:
        preprocessed = preprocess_html(SAMPLE_HTML_CONTENT, url="https://example.com/bitcoin-news")
        
        logger.info(f"Preprocessed content length: {len(preprocessed.text)}")
        logger.info(f"Number of segments: {len(preprocessed.segments)}")
        logger.info(f"Number of tables: {len(preprocessed.tables)}")
        logger.info(f"Number of lists: {len(preprocessed.lists)}")
        
        # Print the first segment
        if preprocessed.segments:
            logger.info(f"First segment type: {preprocessed.segments[0].segment_type}")
            logger.info(f"First segment preview: {preprocessed.segments[0].text[:100]}...")
        
        # Print the first table if available
        if preprocessed.tables:
            table = preprocessed.tables[0]
            logger.info(f"Table caption: {table.caption}")
            logger.info(f"Table headers: {table.headers}")
            logger.info(f"Table rows: {len(table.rows)}")
        
        # Print the first list if available
        if preprocessed.lists:
            lst = preprocessed.lists[0]
            logger.info(f"List type: {'Ordered' if lst.ordered else 'Unordered'}")
            logger.info(f"List items: {len(lst.items)}")
            logger.info(f"First few items: {lst.items[:3]}")
        
        # Get API key from environment variable
        api_key = os.environ.get("OPENROUTER_API_KEY")
        
        if not api_key:
            logger.error("No API key found in environment variables. Skipping extraction test.")
            return
        
        # Try to find a working model
        models = [
            "mistralai/mistral-small-24b-instruct-2501:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "moonshotai/kimi-k2:free"
        ]
        
        strategy = None
        for model in models:
            try:
                strategy = CryptoLLMExtractionStrategy(
                    provider="openrouter",
                    api_token=api_key,
                    model=model
                )
                await strategy.validate_provider_connection()
                logger.info(f"Successfully connected with model {model}")
                break
            except Exception as e:
                logger.warning(f"Failed to connect with model {model}: {str(e)}")
        
        if not strategy:
            logger.error("Could not connect to any model. Skipping extraction test.")
            return
        
        # Extract from preprocessed content
        result = await strategy.extract(preprocessed.get_combined_text())
        logger.info("Extraction from preprocessed content successful")
        print_extraction_result(result)
        
    except Exception as e:
        logger.error(f"Error in content preprocessing test: {str(e)}")


async def test_schema_validation():
    """Test schema validation for extraction results."""
    logger.info("\n=== Testing Schema Validation ===")
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENROUTER_API_KEY")
    
    if not api_key:
        logger.error("No API key found in environment variables. Skipping test.")
        return
    
    # Try to find a working model
    models = [
        "mistralai/mistral-small-24b-instruct-2501:free",
        "qwen/qwen-2.5-72b-instruct:free",
        "moonshotai/kimi-k2:free"
    ]
    
    strategy = None
    for model in models:
        try:
            strategy = CryptoLLMExtractionStrategy(
                provider="openrouter",
                api_token=api_key,
                model=model
            )
            await strategy.validate_provider_connection()
            logger.info(f"Successfully connected with model {model}")
            break
        except Exception as e:
            logger.warning(f"Failed to connect with model {model}: {str(e)}")
    
    if not strategy:
        logger.error("Could not connect to any model. Skipping schema validation test.")
        return
    
    try:
        # Extract from sample content
        result = await strategy.extract(SAMPLE_CONTENT)
        logger.info("Extraction successful")
        
        # Check if required fields are present
        required_fields = ["headline", "summary", "sentiment"]
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
        else:
            logger.info("All required fields are present")
        
        # Check if sentiment is valid
        valid_sentiments = ["positive", "negative", "neutral"]
        if "sentiment" in result and result["sentiment"].lower() not in valid_sentiments:
            logger.warning(f"Invalid sentiment value: {result['sentiment']}")
        else:
            logger.info("Sentiment value is valid")
        
        # Check if enhancement fields are present
        enhancement_fields = ["persona_relevance", "urgency_score", "_metadata"]
        missing_enhancements = [field for field in enhancement_fields if field not in result]
        
        if missing_enhancements:
            logger.warning(f"Missing enhancement fields: {missing_enhancements}")
        else:
            logger.info("All enhancement fields are present")
        
        print_extraction_result(result)
        
    except Exception as e:
        logger.error(f"Error in schema validation test: {str(e)}")


async def test_comparison():
    """Compare different extraction strategies."""
    logger.info("\n=== Testing Comparison Between Strategies ===")
    
    # Get API keys from environment variables
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    groq_api_key = os.environ.get("GROQ_API_KEY")
    
    if not any([openai_api_key, openrouter_api_key, groq_api_key]):
        logger.error("No API keys found in environment variables. Skipping test.")
        return
    
    strategies = []
    
    # Initialize strategies with different providers and models
    if openai_api_key:
        try:
            strategy = CryptoLLMExtractionStrategy(
                provider="openai",
                api_token=openai_api_key,
                model="gpt-3.5-turbo"
            )
            await strategy.validate_provider_connection()
            strategies.append(("OpenAI/gpt-3.5-turbo", strategy))
            
            # Add GPT-4 if testing with it
            try:
                strategy_gpt4 = CryptoLLMExtractionStrategy(
                    provider="openai",
                    api_token=openai_api_key,
                    model="gpt-4"
                )
                await strategy_gpt4.validate_provider_connection()
                strategies.append(("OpenAI/gpt-4", strategy_gpt4))
            except Exception as e:
                logger.warning(f"Failed to connect to OpenAI GPT-4: {str(e)}")
                
        except Exception as e:
            logger.warning(f"Failed to connect to OpenAI: {str(e)}")
    
    if openrouter_api_key:
        openrouter_models = [
            "mistralai/mistral-small-24b-instruct-2501:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "moonshotai/kimi-k2:free"
        ]
        
        for model in openrouter_models:
            try:
                strategy = CryptoLLMExtractionStrategy(
                    provider="openrouter",
                    api_token=openrouter_api_key,
                    model=model
                )
                await strategy.validate_provider_connection()
                strategies.append((f"OpenRouter/{model}", strategy))
            except Exception as e:
                logger.warning(f"Failed to connect to OpenRouter with model {model}: {str(e)}")
    
    if groq_api_key:
        groq_models = ["llama3-70b-8192", "llama3-8b-8192"]
        
        for model in groq_models:
            try:
                strategy = CryptoLLMExtractionStrategy(
                    provider="groq",
                    api_token=groq_api_key,
                    model=model
                )
                await strategy.validate_provider_connection()
                strategies.append((f"Groq/{model}", strategy))
            except Exception as e:
                logger.warning(f"Failed to connect to Groq with model {model}: {str(e)}")
    
    if not strategies:
        logger.error("Could not connect to any provider. Skipping comparison test.")
        return
    
    logger.info(f"Comparing {len(strategies)} different strategies")
    
    # Run extraction with each strategy and compare results
    results = []
    
    for name, strategy in strategies:
        try:
            start_time = time.time()
            result = await strategy.extract(SAMPLE_CONTENT)
            end_time = time.time()
            
            # Add metadata about the extraction
            result["_comparison"] = {
                "strategy_name": name,
                "extraction_time": end_time - start_time
            }
            
            results.append(result)
            logger.info(f"Extraction with {name} successful in {end_time - start_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Extraction with {name} failed: {str(e)}")
    
    if not results:
        logger.error("No successful extractions. Skipping comparison.")
        return
    
    # Compare sentiment across strategies
    sentiments = [result.get("sentiment", "unknown").lower() for result in results]
    logger.info(f"Sentiment comparison: {sentiments}")
    
    if len(set(sentiments)) == 1:
        logger.info("All strategies agree on sentiment")
    else:
        logger.info("Strategies disagree on sentiment")
    
    # Compare extraction times
    extraction_times = [result["_comparison"]["extraction_time"] for result in results]
    logger.info(f"Extraction time comparison (seconds): {[f'{t:.2f}' for t in extraction_times]}")
    logger.info(f"Fastest strategy: {results[extraction_times.index(min(extraction_times))]['_comparison']['strategy_name']}")
    
    # Compare key entities identified
    all_entities = set()
    for result in results:
        entities = result.get("key_entities", [])
        if isinstance(entities, list):
            all_entities.update(entities)
    
    logger.info(f"All entities identified across strategies: {all_entities}")
    
    # Print detailed results for each strategy
    for result in results:
        logger.info(f"\nResults from {result['_comparison']['strategy_name']}:")
        print_extraction_result(result)


async def test_benchmarking():
    """Benchmark extraction performance."""
    logger.info("\n=== Benchmarking Extraction Performance ===")
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENROUTER_API_KEY")
    
    if not api_key:
        logger.error("No API key found in environment variables. Skipping test.")
        return
    
    # Try to find a working model
    models = [
        "mistralai/mistral-small-24b-instruct-2501:free",
        "qwen/qwen-2.5-72b-instruct:free",
        "moonshotai/kimi-k2:free"
    ]
    
    strategy = None
    for model in models:
        try:
            strategy = CryptoLLMExtractionStrategy(
                provider="openrouter",
                api_token=api_key,
                model=model
            )
            await strategy.validate_provider_connection()
            logger.info(f"Successfully connected with model {model}")
            break
        except Exception as e:
            logger.warning(f"Failed to connect with model {model}: {str(e)}")
    
    if not strategy:
        logger.error("Could not connect to any model. Skipping benchmarking test.")
        return
    
    # Prepare test contents of different sizes
    test_contents = {
        "small": SAMPLE_CONTENT,
        "medium": SAMPLE_CONTENT * 3,
        "large": SAMPLE_CONTENT * 5
    }
    
    # Run benchmarks
    results = {}
    
    for size, content in test_contents.items():
        logger.info(f"Benchmarking with {size} content ({len(content)} characters)")
        
        # Run multiple iterations for more accurate benchmarking
        times = []
        token_counts = []
        
        # Limit iterations to avoid excessive API usage
        iterations = 1 if size == "large" else (2 if size == "medium" else 3)
        
        for i in range(iterations):
            try:
                start_time = time.time()
                result = await strategy.extract(content)
                end_time = time.time()
                
                extraction_time = end_time - start_time
                times.append(extraction_time)
                
                # Get token usage if available
                if "_metadata" in result and "usage" in result["_metadata"]:
                    token_counts.append(result["_metadata"]["usage"].get("total_tokens", 0))
                
                logger.info(f"Iteration {i+1}: {extraction_time:.2f} seconds")
                
                # Only print detailed results for the first iteration
                if i == 0:
                    print_extraction_result(result)
                
            except Exception as e:
                logger.error(f"Error in iteration {i+1}: {str(e)}")
        
        if times:
            avg_time = statistics.mean(times)
            results[size] = {
                "avg_time": avg_time,
                "min_time": min(times),
                "max_time": max(times),
                "iterations": len(times)
            }
            
            if token_counts:
                results[size]["avg_tokens"] = statistics.mean(token_counts)
            
            logger.info(f"Average extraction time for {size} content: {avg_time:.2f} seconds")
            if token_counts:
                logger.info(f"Average token usage for {size} content: {results[size]['avg_tokens']:.0f} tokens")
    
    # Compare results across different content sizes
    if len(results) > 1:
        logger.info("\nPerformance comparison across content sizes:")
        for size, metrics in results.items():
            logger.info(f"{size.capitalize()} content: {metrics['avg_time']:.2f} seconds, "
                       f"{metrics.get('avg_tokens', 'N/A')} tokens")


def print_extraction_result(result: Dict[str, Any]):
    """Print the extraction result in a readable format."""
    print("\nExtraction Result:")
    print(f"Headline: {result.get('headline', 'N/A')}")
    print(f"Summary: {result.get('summary', 'N/A')}")
    print(f"Sentiment: {result.get('sentiment', 'N/A')}")
    print(f"Category: {result.get('category', 'N/A')}")
    print(f"Market Impact: {result.get('market_impact', 'N/A')}")
    
    key_entities = result.get('key_entities', [])
    if key_entities:
        print("Key Entities:")
        for entity in key_entities:
            print(f"  - {entity}")
    
    persona_relevance = result.get('persona_relevance', {})
    if persona_relevance:
        print("Persona Relevance:")
        for persona, score in persona_relevance.items():
            print(f"  - {persona}: {score}")
    
    print(f"Urgency Score: {result.get('urgency_score', 'N/A')}")
    
    price_mentions = result.get('price_mentions', [])
    if price_mentions:
        print("Price Mentions:")
        for mention in price_mentions:
            print(f"  - {mention}")
    
    # Print metadata if available
    if "_metadata" in result:
        metadata = result["_metadata"]
        print("\nMetadata:")
        print(f"Model: {metadata.get('model', 'N/A')}")
        print(f"Timestamp: {metadata.get('timestamp', 'N/A')}")
        
        if "usage" in metadata:
            usage = metadata["usage"]
            print("Token Usage:")
            print(f"  - Prompt Tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"  - Completion Tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"  - Total Tokens: {usage.get('total_tokens', 'N/A')}")
        
        if "performance" in metadata:
            performance = metadata["performance"]
            print("Performance:")
            print(f"  - Extraction Time: {performance.get('extraction_time', 'N/A'):.2f} seconds")
            print(f"  - Retries: {performance.get('retries', 'N/A')}")


async def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test extraction strategies")
    parser.add_argument("--test", choices=["all", "provider", "error", "preprocessing", "schema", "comparison", "benchmark"],
                        default="all", help="Specify which test to run")
    args = parser.parse_args()
    
    if args.test in ["all", "provider"]:
        await test_provider_flexibility()
    
    if args.test in ["all", "error"]:
        await test_error_handling()
    
    if args.test in ["all", "preprocessing"]:
        await test_content_preprocessing()
    
    if args.test in ["all", "schema"]:
        await test_schema_validation()
    
    if args.test in ["all", "comparison"]:
        await test_comparison()
    
    if args.test in ["all", "benchmark"]:
        await test_benchmarking()


if __name__ == "__main__":
    asyncio.run(main())