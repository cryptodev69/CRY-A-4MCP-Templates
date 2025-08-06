import asyncio
import json
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.openrouter_utils import get_openrouter_models, format_openrouter_models

async def test():
    print("Testing OpenRouter Utilities with Price Handling Fix")
    print("-" * 50)
    
    # Create sample model data with string prices
    sample_models = [
        {
            "id": "test/model-1",
            "context_length": "2000000",
            "pricing": {
                "prompt": "0.00000125",
                "completion": "0.000005"
            }
        },
        {
            "id": "test/model-2:free",
            "context_length": 1000000,
            "pricing": {
                "prompt": "0",
                "completion": "0"
            }
        },
        {
            "id": "test/model-3",
            "context_length": "invalid",
            "pricing": {
                "prompt": "invalid",
                "completion": "invalid"
            }
        }
    ]
    
    print("Sample Models:")
    print(json.dumps(sample_models, indent=2))
    print()
    
    # Test formatting without filtering
    print("Formatted Models (No Filter):")
    formatted = format_openrouter_models(sample_models, filter_free=False)
    print(json.dumps(formatted, indent=2))
    print()
    
    # Test formatting with free filter
    print("Formatted Models (Free Only):")
    formatted_free = format_openrouter_models(sample_models, filter_free=True)
    print(json.dumps(formatted_free, indent=2))
    print()
    
    # Test with real API if API key is provided
    api_key = input('Enter OpenRouter API key to test with real data (press Enter to skip): ')
    if api_key:
        print("\nTesting with real API data...")
        success, models, message = await get_openrouter_models(api_key)
        if success and models:
            print(f"Retrieved {len(models)} models from API")
            
            # Test a few models with different price formats
            print("\nSample of real models:")
            for i, model in enumerate(models[:3]):
                print(f"Model {i+1}: {model['id']}")
                print(f"  Context Length: {model.get('context_length')}")
                print(f"  Pricing: {model.get('pricing', {})}")
            
            # Format and filter
            formatted_real = format_openrouter_models(models, filter_free=False)
            formatted_real_free = format_openrouter_models(models, filter_free=True)
            
            print(f"\nFormatted {len(formatted_real)} models")
            print(f"Formatted {len(formatted_real_free)} free models")
            
            # Show a few formatted models
            if formatted_real:
                print("\nSample of formatted models:")
                for i, model in enumerate(formatted_real[:3]):
                    print(f"Model {i+1}: {model['id']}")
                    print(f"  Context Length: {model['context_length']}")
                    print(f"  Prompt Price: {model['prompt_price_formatted']}")
                    print(f"  Completion Price: {model['completion_price_formatted']}")
                    print(f"  Is Free: {model['is_free']}")
        else:
            print(f"Failed to get models: {message}")

if __name__ == "__main__":
    asyncio.run(test())