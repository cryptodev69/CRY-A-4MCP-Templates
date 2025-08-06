# Extraction Strategies Guide

## Overview

This guide explains how to use and configure the extraction strategies in the CRY-A-4MCP platform, particularly focusing on the `XCryptoHunterLLMExtractionStrategy` for cryptocurrency data extraction.

## Setup

### 1. OpenRouter API Key

To use the LLM-based extraction strategies, you need an OpenRouter API key:

1. Sign up at [OpenRouter](https://openrouter.ai/) and get your API key
2. Add it to the `.env` file as `OPENROUTER_API_KEY=your_api_key_here`
3. Or set it as an environment variable before running scripts

```bash
export OPENROUTER_API_KEY=your_api_key_here
```

### 2. Install Dependencies

Ensure you have the required dependencies:

```bash
pip install python-dotenv
```

## Using Extraction Strategies

### Basic Usage

```python
from src.cry_a_4mcp.crawl4ai.extraction_strategies.crypto.xcryptohunter_llm import XCryptoHunterLLMExtractionStrategy
from src.cry_a_4mcp.crawl4ai.extraction_strategies.sync_wrapper import SyncExtractionStrategyWrapper
import os

# Get API key from environment
api_token = os.environ.get('OPENROUTER_API_KEY')

# Create strategy instance
strategy = XCryptoHunterLLMExtractionStrategy(
    provider='openrouter', 
    api_token=api_token,
    model='openai/gpt-3.5-turbo'  # You can specify different models
)

# Create synchronous wrapper
wrapper = SyncExtractionStrategyWrapper(strategy)

# Extract data
result = wrapper.sync_extract(
    url="https://example.com",
    content="This is the content to analyze for crypto information."
)

print(result)
```

### Available Models

You can specify different models when creating a strategy instance:

```python
# OpenAI models
model='openai/gpt-3.5-turbo'
model='openai/gpt-4-turbo'

# Anthropic models
model='anthropic/claude-3-haiku-20240307'
model='anthropic/claude-3-opus-20240229'

# Google models
model='google/gemini-1.5-pro-latest'

# Meta models
model='meta-llama/llama-3-8b-instruct'
model='meta-llama/llama-3-70b-instruct'
```

See the [OpenRouter documentation](https://openrouter.ai/docs#models) for a complete list of available models.

## Managing Strategies

### Strategy UI

You can manage strategies using the Improved Strategy UI:

```bash
python run_improved_strategy_ui.py
```

This will start a Streamlit web interface where you can view, edit, and delete strategies.

### Testing Strategies

You can test strategies using the provided test scripts:

```bash
python test_extract_params.py
```

## Troubleshooting

### API Errors

- **401 Unauthorized**: Check your API key is valid and correctly set in the `.env` file
- **429 Rate Limit**: The free tier of OpenRouter has rate limits. Wait a few minutes or try a different model
- **500+ Server Error**: This is likely a temporary issue with the OpenRouter service

### Strategy Not Found

If you encounter a "Strategy class not found" error in the UI:

1. Make sure the strategy class is correctly defined in the appropriate file
2. Check that the file name matches the expected naming convention
3. Refresh the strategy cache in the UI

## Additional Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)