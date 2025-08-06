#!/usr/bin/env python3
"""
Test script to verify the extract method works with named parameters.

Note: This script makes actual API calls. For testing without making API calls,
see test_extract_params_mock.py and test_extraction_strategy_comprehensive.py.
Also refer to README_TESTING.md for more information on testing approaches.
"""

import os
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print("✅ Successfully loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed. Environment variables will only be loaded from the system.")
    print("   To install: pip install python-dotenv")

from src.cry_a_4mcp.crawl4ai.extraction_strategies.crypto.xcryptohunter_llm import XCryptoHunterLLMExtractionStrategy
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper

# Create a strategy instance
# Get the OpenRouter API key from environment variables
# To set up your API key:
# 1. Sign up at https://openrouter.ai/ and get your API key
# 2. Add it to the .env file as OPENROUTER_API_KEY=your_api_key_here
# 3. Or set it as an environment variable before running this script
api_token = os.environ.get('OPENROUTER_API_KEY', 'YOUR_OPENROUTER_API_KEY')

# Check if the API key is set
if api_token == 'YOUR_OPENROUTER_API_KEY':
    print("⚠️ Warning: You need to set your OpenRouter API key in the .env file or as an environment variable.")
    print("   Sign up at https://openrouter.ai/ to get your API key.")
    print("   Then add it to the .env file as OPENROUTER_API_KEY=your_api_key_here")
    print("   Or set it as an environment variable before running this script.")
    print("   Continuing with test_token, but this will likely fail with a 401 error.")
    api_token = 'test_token'  # Fallback to test_token for demonstration purposes
# Create a strategy instance with a specific model
# You can try different models if one is rate-limited
# Available models: https://openrouter.ai/docs#models
strategy = XCryptoHunterLLMExtractionStrategy(
    provider='openrouter', 
    api_token=api_token,
    # Try different models if one is rate-limited
    # model='anthropic/claude-3-haiku-20240307'
    # model='google/gemini-1.5-pro-latest'
    # model='meta-llama/llama-3-8b-instruct'
    model='openai/gpt-3.5-turbo'  # This model is often more reliable
)

# Wrap it with the synchronous wrapper
sync_strategy = SyncExtractionStrategyWrapper(strategy)

print('Testing extract method with named parameters...')

try:
    # Test with named parameters
    result = sync_strategy.extract(url='https://example.com', content='Test content')
    print('Extract method called successfully with named parameters')
    print(f'Result: {result}')
except Exception as e:
    print(f'Error: {e}')
    # Print more detailed error information
    import traceback
    print('\nDetailed error traceback:')
    traceback.print_exc()
    
    # Check if it's an API error and print more information
    from src.cry_a_4mcp.crawl4ai.extraction_strategies.base import APIResponseError
    if isinstance(e, APIResponseError):
        print(f'\nAPI Error Details:')
        print(f'Status Code: {e.status_code}')
        print(f'Error Message: {e.message}')
    
        # Provide suggestions based on error type
        if 'No auth credentials found' in str(e):
            print('\nSuggestion: The API token provided is invalid or missing. Please check your API token.')
            print('For testing purposes, you can use a valid API token or mock the API response.')
        elif e.status == 429:
            print('\nSuggestions for Rate Limit Error:')
            print('1. The free tier of OpenRouter has rate limits')
            print('2. Wait a few minutes before trying again')
            print('3. Sign up for a paid plan at https://openrouter.ai/settings/integrations')
            print('4. Try using a different model by modifying the strategy initialization')
        elif e.status == 401:
            print('\nSuggestions for Authentication Error:')
            print('1. Your API key is invalid or has been revoked')
            print('2. Get a new API key from https://openrouter.ai/settings/integrations')
            print('3. Update the OPENROUTER_API_KEY in your .env file')
            print('4. Make sure the API key is correctly formatted (no extra spaces, etc.)')
        elif e.status >= 500:
            print('\nSuggestions for Server Error:')
            print('1. This is likely a temporary issue with the OpenRouter service')
            print('2. Wait a few minutes and try again')
            print('3. Check the OpenRouter status page for any ongoing incidents')