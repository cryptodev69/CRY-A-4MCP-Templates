import asyncio
import json
from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.openrouter_utils import get_openrouter_models, format_openrouter_models

async def test():
    api_key = input('Enter OpenRouter API key (press Enter to skip): ')
    success, models, message = await get_openrouter_models(api_key)
    print(f'Success: {success}')
    print(f'Message: {message}')
    
    if models:
        # Print first two models with full details
        print(f'Sample Models (2): {json.dumps(models[:2], indent=2)}')
        
        # Format models and show pricing information
        formatted = format_openrouter_models(models)
        print(f'\nFormatted Models Sample (2): {json.dumps(formatted[:2], indent=2)}')
        
        # Check for models with unknown pricing
        unknown_price_models = [m for m in formatted if m["prompt_price_formatted"] == "Unknown" or m["completion_price_formatted"] == "Unknown"]
        print(f'\nModels with Unknown Pricing: {len(unknown_price_models)} out of {len(formatted)}')
        if unknown_price_models:
            print(f'Sample Unknown Price Model: {json.dumps(unknown_price_models[0], indent=2)}')
            
            # Check original model data for this model
            model_id = unknown_price_models[0]["id"]
            original_model = next((m for m in models if m.get("id") == model_id), None)
            if original_model:
                print(f'\nOriginal API data for this model: {json.dumps(original_model, indent=2)}')

if __name__ == "__main__":
    asyncio.run(test())