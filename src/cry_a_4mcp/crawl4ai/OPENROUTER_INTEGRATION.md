# OpenRouter Integration for UniversalNewsCrawler

## Overview

This document explains how to use OpenRouter with the UniversalNewsCrawler to potentially reduce costs during development and testing phases. OpenRouter is a service that provides access to various LLM models through a unified API, often at lower costs than direct API access.

## Benefits of Using OpenRouter

- **Cost Efficiency**: Access to various models at potentially lower rates
- **Model Flexibility**: Easy switching between different models without changing code
- **API Compatibility**: Uses OpenAI-compatible API format
- **Development Friendly**: Ideal for testing and development phases

## Integration Steps

### 1. Sign Up for OpenRouter

1. Visit [OpenRouter](https://openrouter.ai/) and create an account
2. Generate an API key from your dashboard

### 2. Configure UniversalNewsCrawler

When initializing the UniversalNewsCrawler, use the following parameters:

```python
crawler = UniversalNewsCrawler(
    config_file_path="path/to/your/config.json",
    llm_api_token="your-openrouter-api-key",  # Your OpenRouter API key
    llm_provider="openai",  # Keep as "openai" since OpenRouter uses OpenAI-compatible API
    llm_base_url="https://openrouter.ai/api/v1"  # OpenRouter base URL
)
```

### 3. Model Selection

By default, OpenRouter will select an appropriate model based on your request. If you want to specify a particular model, you can modify the `_initialize_llm_strategy` method to include model selection in the `extra_args`:

```python
# Inside _initialize_llm_strategy method
if "openrouter.ai" in self.llm_base_url:
    llm_kwargs["extra_args"] = {
        "headers": {
            "HTTP-Referer": "https://your-site.com",  # Optional
            "X-Title": "Crypto News Crawler"  # Optional
        },
        "model": "qwen/qwen3-14b:free"  # Specify exact model (free tier)
        # Alternative: "model": "anthropic/claude-3-haiku-20240307"
    }
```

### 4. Available Models

Some cost-effective models you might consider:

- `qwen/qwen3-14b:free` - Free tier model with good performance
- `anthropic/claude-3-haiku-20240307` - Fast and cost-effective
- `google/gemini-pro` - Good balance of performance and cost
- `mistralai/mistral-7b-instruct` - Open source option
- `meta-llama/llama-3-8b-instruct` - Open source option

Check the [OpenRouter documentation](https://openrouter.ai/docs) for the current list of available models and their pricing.

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure your API key is correct and has sufficient credits
2. **Model Availability**: Some models may be temporarily unavailable
3. **Rate Limiting**: OpenRouter may have rate limits depending on your plan

### Debugging

If you encounter issues, enable verbose logging in the LLMExtractionStrategy:

```python
llm_kwargs["verbose"] = True
```

## Production Considerations

While OpenRouter is excellent for development and testing, evaluate the following for production use:

1. **Reliability**: Consider the SLA of OpenRouter vs. direct API access
2. **Latency**: There might be additional latency when using a proxy service
3. **Cost at Scale**: Calculate the cost efficiency at your expected production volume

## Using the Example Script

The `openrouter_example.py` script provides a ready-to-use example of OpenRouter integration:

```bash
# Run the script with default settings (crawls BBC News)
python openrouter_example.py

# List all available models from OpenRouter
python openrouter_example.py --list-models

# Crawl a specific URL
python openrouter_example.py --url https://example.com/article
```

The `--list-models` flag displays available models with their context lengths and pricing information, helping you choose the most cost-effective model for your needs.

The example script is configured to use the `qwen/qwen3-14b:free` model, which provides good performance at no cost, making it ideal for development and testing.

## Further Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter API Reference](https://openrouter.ai/docs/api-reference)
- [OpenRouter Pricing](https://openrouter.ai/pricing)