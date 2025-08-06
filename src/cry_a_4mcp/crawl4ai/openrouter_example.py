#!/usr/bin/env python3
"""
Example script demonstrating how to use OpenRouter with UniversalNewsCrawler
for cost-effective LLM extraction during development.
"""

import asyncio
import os
import sys
import re
import json
import aiohttp
from typing import Dict, List, Optional, Any, Tuple

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))  

from cry_a_4mcp.crawl4ai.universal_news_crawler import UniversalNewsCrawler


def validate_openrouter_api_key(api_key: str) -> bool:
    """Validate the format of an OpenRouter API key.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        bool: True if the key appears to be valid, False otherwise
    """
    # OpenRouter keys typically start with "sk-or-" followed by a version and a long string
    # This is a basic validation and may need updates if OpenRouter changes their key format
    if not api_key:
        return False
        
    # Check for the expected prefix
    if not api_key.startswith("sk-or-"):
        return False
        
    # Check for minimum length (typical OpenRouter keys are quite long)
    if len(api_key) < 30:
        return False
        
    # Check that it contains only valid characters
    if not re.match(r'^[a-zA-Z0-9_\-]+$', api_key):
        return False
        
    return True


def extract_model_info(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract model information from OpenRouter response if available.
    
    Args:
        results: The results from the crawler
        
    Returns:
        Dict containing model information if available, empty dict otherwise
    """
    model_info = {}
    
    if not results or not isinstance(results, list) or len(results) == 0:
        return model_info
        
    # OpenRouter typically adds model information in the metadata
    # This structure may vary depending on how the UniversalNewsCrawler processes the response
    result = results[0]
    
    # Check different possible locations for model information
    if "metadata" in result and isinstance(result["metadata"], dict):
        metadata = result["metadata"]
        if "model" in metadata:
            model_info["model"] = metadata["model"]
        if "provider" in metadata:
            model_info["provider"] = metadata["provider"]
    
    # Some implementations might include it directly in the llm_extraction
    if "llm_extraction" in result and isinstance(result["llm_extraction"], dict):
        llm_data = result["llm_extraction"]
        if "_model" in llm_data:
            model_info["model"] = llm_data["_model"]
        if "_provider" in llm_data:
            model_info["provider"] = llm_data["_provider"]
    
    return model_info


def display_available_models(models: List[Dict[str, Any]], max_display: int = 10) -> None:
    """Display available OpenRouter models in a user-friendly format.
    
    Args:
        models: List of model data from OpenRouter API
        max_display: Maximum number of models to display
    """
    if not models:
        print("No models available")
        return
    
    # Sort models by context_length (capability) and then by pricing
    sorted_models = sorted(
        models, 
        key=lambda x: (x.get("context_length", 0), -float(x.get("pricing", {}).get("prompt", 0))),
        reverse=True
    )
    
    # Limit the number of models to display
    display_models = sorted_models[:max_display]
    
    print(f"\nAvailable OpenRouter Models (showing top {min(max_display, len(models))} of {len(models)}):\n")
    print(f"{'Model ID':<40} {'Context':<10} {'Prompt $/1M':<15} {'Completion $/1M':<15}")
    print("-" * 80)
    
    for model in display_models:
        model_id = model.get("id", "Unknown")
        context_length = model.get("context_length", "Unknown")
        
        pricing = model.get("pricing", {})
        prompt_price = pricing.get("prompt", "Unknown")
        completion_price = pricing.get("completion", "Unknown")
        
        # Format prices to show in dollars per million tokens
        if isinstance(prompt_price, (int, float)):
            prompt_price = f"${prompt_price * 1000000:.2f}"
        if isinstance(completion_price, (int, float)):
            completion_price = f"${completion_price * 1000000:.2f}"
        
        print(f"{model_id:<40} {context_length:<10} {prompt_price:<15} {completion_price:<15}")
    
    print("\nTo use a specific model, modify the _initialize_llm_strategy method in UniversalNewsCrawler")
    print("Example: llm_kwargs['extra_args'] = {'model': 'anthropic/claude-3-haiku-20240307'}")
    print("\nSee OPENROUTER_INTEGRATION.md for more details.")
    print("\nNote: Pricing is in dollars per million tokens.")
    print("      Lower pricing is better for cost-efficiency.")
    print("      Higher context length allows processing more text at once.")
    print("      OpenRouter may select a different model if your preferred model is unavailable.")
    print("      Check https://openrouter.ai/docs for the most up-to-date information.")
    print("\n")


async def check_openrouter_status() -> Tuple[bool, str]:
    """Check if the OpenRouter service is operational.
    
    Returns:
        Tuple[bool, str]: A tuple containing (is_operational, status_message)
    """
    status_url = "https://openrouter.ai/api/v1/status"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(status_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if the response contains status information
                    if "status" in data and data["status"] == "ok":
                        return True, "OpenRouter service is operational"
                    
                    # If there's detailed status information, include it
                    if "message" in data:
                        return False, f"OpenRouter status issue: {data['message']}"
                    
                    # Default message if we can't determine specific status
                    return False, f"OpenRouter returned unexpected status: {json.dumps(data)}"
                else:
                    return False, f"OpenRouter status check failed with HTTP {response.status}"
    except aiohttp.ClientError as e:
        return False, f"Could not connect to OpenRouter: {str(e)}"
    except asyncio.TimeoutError:
        return False, "OpenRouter status check timed out"
    except Exception as e:
        return False, f"Error checking OpenRouter status: {str(e)}"
    
    return False, "Unknown error checking OpenRouter status"


async def get_openrouter_models(api_key: str) -> Tuple[bool, List[Dict[str, Any]], str]:
    """Get available models from OpenRouter API.
    
    Args:
        api_key: OpenRouter API key
        
    Returns:
        Tuple containing:
            - Success flag (bool)
            - List of available models (or empty list if request fails)
            - Status message (str)
    """
    models_url = "https://openrouter.ai/api/v1/models"
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/user/crypto-news-crawler",  # Required by OpenRouter
            "X-Title": "Crypto News Crawler"  # Optional but helpful for OpenRouter analytics
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(models_url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract the models list
                    if "data" in data and isinstance(data["data"], list):
                        return True, data["data"], "Successfully retrieved models"
                    else:
                        return False, [], "Unexpected response format from OpenRouter models API"
                else:
                    error_text = await response.text()
                    return False, [], f"Failed to get models: HTTP {response.status} - {error_text}"
    except aiohttp.ClientError as e:
        return False, [], f"Connection error: {str(e)}"
    except asyncio.TimeoutError:
        return False, [], "Request timed out"
    except Exception as e:
        return False, [], f"Error: {str(e)}"
    
    return False, [], "Unknown error getting models"


async def main():
    """Run the Universal News Crawler with OpenRouter integration."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="OpenRouter integration example for UniversalNewsCrawler")
    parser.add_argument("--list-models", action="store_true", help="List available models and exit")
    parser.add_argument("--url", type=str, help="URL to crawl instead of using config sources")
    args = parser.parse_args()
    
    # Path to the configuration file
    config_file_path = os.path.join(
        os.path.dirname(__file__),
        '../../../sample-data/crawled_content/universal_news_crawler_config.json'
    )
    
    print(f"Loading configuration from: {config_file_path}")
    
    # Get OpenRouter API key from environment variable or set directly
    # SECURITY NOTICE: For production use, always use environment variables for API keys
    # Example of setting environment variable:
    # export OPENROUTER_API_KEY="your-api-key-here"
    
    # First try to get from environment variable
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "")
    
    # If not found in environment, prompt the user to enter it
    # WARNING: Hardcoding API keys in source code is a security risk
    # This is only acceptable for personal development environments
    if not openrouter_api_key:
        print("WARNING: OPENROUTER_API_KEY environment variable not set.")
        print("Please set your OpenRouter API key using one of these methods:")
        print("1. Set environment variable: export OPENROUTER_API_KEY=your-api-key")
        print("2. For development only, enter your API key when prompted")
        print("You can get an API key from https://openrouter.ai/")
        
        # Prompt for API key input
        import getpass
        print("\nPlease enter your OpenRouter API key:")
        openrouter_api_key = getpass.getpass()
        
        # Exit if no API key is provided
        if not openrouter_api_key:
            print("\nERROR: No OpenRouter API key provided. Exiting.")
            sys.exit(1)
    
    # Validate the API key format
    if not validate_openrouter_api_key(openrouter_api_key):
        print(f"\nWARNING: The provided OpenRouter API key may not be valid.")
        print("OpenRouter keys typically start with 'sk-or-' followed by a version identifier and a long string.")
        print("Please check your API key and try again.")
        print("Continuing anyway, but the API call may fail...\n")
    
    # Check OpenRouter service status
    print("Checking OpenRouter service status...")
    is_operational, status_message = await check_openrouter_status()
    if is_operational:
        print(f"✅ {status_message}")
    else:
        print(f"⚠️ {status_message}")
        print("Continuing anyway, but the API call may fail if the service is down.\n")
    
    # Get available models from OpenRouter
    success, models_list, message = await get_openrouter_models(openrouter_api_key)
    if success:
        print(f"Found {len(models_list)} available models on OpenRouter")
        
        # If --list-models flag is provided, display models and exit
        if args.list_models:
            display_available_models(models_list)
            return
    else:
        print(f"Could not retrieve available models from OpenRouter: {message}")
    
    # Create a UniversalNewsCrawler instance with OpenRouter
    # Using model: qwen/qwen3-14b:free
    print("\nUsing OpenRouter with model: google/gemini-2.0-flash-exp:free")
    crawler = UniversalNewsCrawler(
        config_file_path=config_file_path,
        llm_api_token=openrouter_api_key,
        llm_provider="openai",  # Keep as "openai" since OpenRouter uses OpenAI-compatible API
        llm_base_url="https://openrouter.ai/api/v1"  # OpenRouter base URL
    )
    
    try:
        # Print information about loaded sources
        all_sources = crawler.get_all_sources()
        print(f"Loaded {len(all_sources)} sources from configuration")
        
        # If URL is provided via command line, use it instead of config sources
        if args.url:
            print(f"\nUsing command line URL: {args.url}")
            results = await crawler.crawl_web_pages([args.url])
        else:
            # Print high priority sources
            high_priority_sources = crawler.get_sources_by_priority("high")
            print(f"\nHigh priority sources ({len(high_priority_sources)}):\n")
            
            # For demonstration, only crawl one high-priority source if available
            if high_priority_sources:
                test_source = high_priority_sources[0]
                print(f"Testing crawl with source: {test_source['name']}")
                
                # Crawl a single page to test OpenRouter integration
                if "url" in test_source:
                    print(f"\nCrawling URL: {test_source['url']}")
                    print("This may take a moment...")
                    results = await crawler.crawl_web_pages([test_source["url"]])
                else:
                    print(f"No URL found for source: {test_source['name']}")
                    results = []
            else:
                print("No high-priority sources found for testing.")
                results = []
        
        # Check if LLM extraction was successful
        if results and results[0].get("llm_extraction"):
            print("\nLLM Extraction Results (via OpenRouter):")
            print("----------------------------------------")
            
            # Display model information if available
            model_info = extract_model_info(results)
            if model_info:
                print("\nModel Information:")
                for key, value in model_info.items():
                    print(f"{key.capitalize()}: {value}")
                print("")
            
            # Display extraction results
            print("Content Extraction:")
            for key, value in results[0]["llm_extraction"].items():
                if key != "key_entities" and not key.startswith("_"):  # Skip detailed entities and metadata
                    print(f"{key}: {value}")
            
            print("\nSuccess! OpenRouter integration is working correctly.")
        elif results:
            print("\nNo LLM extraction results. Possible issues:")
            print("1. OpenRouter API key may be invalid or expired")
            print("2. OpenRouter service may be experiencing issues")
            print("3. The crawled content may not be suitable for extraction")
            print("\nCheck your OpenRouter account at https://openrouter.ai/")
            
    except Exception as e:
        print(f"\nError during crawling: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify your OpenRouter API key is correct")
        print("2. Check if you have sufficient credits in your OpenRouter account")
        print("3. Ensure the URL is accessible and contains relevant content")
        print("4. Check your network connection")
        print(f"\nError details: {type(e).__name__}: {str(e)}")
    finally:
        # Ensure crawler is properly closed
        await crawler.close()
        print("\nCrawler closed properly")


if __name__ == "__main__":
    asyncio.run(main())