# Testing Framework for CRY-A-4MCP

This directory contains a comprehensive testing framework for the CRY-A-4MCP extraction strategies and related components.

## Directory Structure

```
tests/
├── README.md                       # This file
├── test_extraction_strategies.py   # Main test suite for extraction strategies
├── samples/                        # Sample content for testing
│   ├── crypto_news.txt             # Sample cryptocurrency news articles
│   ├── social_media.txt            # Sample social media content
│   └── html_content.html           # Sample HTML content for preprocessing tests
├── benchmarks/                     # Benchmarking results and tools
│   └── README.md                   # Benchmarking documentation
└── comparison/                     # Comparison test results
    └── README.md                   # Comparison testing documentation
```

## Running Tests

To run the tests, you need to have the required API keys set as environment variables:

```bash
export OPENAI_API_KEY="your_openai_api_key"
export OPENROUTER_API_KEY="your_openrouter_api_key"
export GROQ_API_KEY="your_groq_api_key"
```

Then, you can run the tests using:

```bash
python tests/test_extraction_strategies.py
```

You can also run specific tests by using the `--test` argument:

```bash
python tests/test_extraction_strategies.py --test provider  # Test provider flexibility
python tests/test_extraction_strategies.py --test error      # Test error handling
python tests/test_extraction_strategies.py --test preprocessing  # Test content preprocessing
python tests/test_extraction_strategies.py --test schema     # Test schema validation
python tests/test_extraction_strategies.py --test comparison # Test comparison between strategies
python tests/test_extraction_strategies.py --test benchmark  # Run benchmarking tests
```

## Test Descriptions

### Provider Flexibility Test

Tests the ability to use different LLM providers (OpenAI, OpenRouter, Groq) with the extraction strategies. It checks:

- Connection to different providers
- Listing available models
- Extraction with different providers

### Error Handling Test

Tests how the extraction strategies handle various error conditions:

- Invalid API keys
- Empty content
- Malformed content

### Content Preprocessing Test

Tests the content preprocessing functionality:

- HTML cleaning and normalization
- Table and list extraction
- Content segmentation
- Extraction from preprocessed content

### Schema Validation Test

Tests the schema validation for extraction results:

- Required fields validation
- Field type validation
- Default values for missing fields
- Schema enhancement

### Comparison Test

Compares different extraction strategies:

- Different providers (OpenAI, OpenRouter, Groq)
- Different models (GPT-3.5, GPT-4, Mistral, etc.)
- Compares extraction quality, speed, and token usage

### Benchmarking Test

Benchmarks the performance of extraction strategies:

- Tests with different content sizes
- Measures extraction time
- Tracks token usage
- Calculates costs

## Adding New Tests

To add new tests, follow these guidelines:

1. Create a new test function in `test_extraction_strategies.py` or a new test file if needed
2. Add the test to the `main()` function with a new command-line option
3. Update this README with information about the new test

## Sample Content

The `samples/` directory contains various sample content for testing. You can add your own sample content to test specific scenarios.

## Benchmarking

The benchmarking tests measure the performance of different extraction strategies and configurations. Results are stored in the `benchmarks/` directory.

## Comparison Testing

The comparison tests compare the results of different extraction strategies on the same content. This helps identify which strategies perform best for different types of content.
## Test Directory Structure

- `unit/`: Unit tests for individual components
- `integration/`: Tests for component interactions
- `e2e/`: End-to-end tests for complete workflows
- `ui/`: Tests for user interface components
- `extraction/`: Tests for extraction functionality
- `strategy/`: Tests for strategy functionality
- `utils/`: Tests for utility functions
- `benchmarks/`: Performance benchmarks
- `comparison/`: Comparison tests
- `samples/`: Sample data for tests

## Running Tests

To run all tests:

```bash
python -m pytest
```

To run tests in a specific directory:

```bash
python -m pytest tests/unit
```
