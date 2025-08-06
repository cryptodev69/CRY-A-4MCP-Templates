"""OpenRouter Utilities for the Strategy Manager UI.

This module provides utility functions for working with OpenRouter API.
"""

import os
import json
from typing import Dict, Any, List, Tuple, Optional
import aiohttp
import asyncio

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


def format_openrouter_models(models: List[Dict[str, Any]], filter_free: bool = False) -> List[Dict[str, Any]]:
    """Format OpenRouter models for display in the UI.
    
    Args:
        models: List of model data from OpenRouter API
        filter_free: Whether to only include free models
        
    Returns:
        List of formatted model data
    """
    if not models:
        return []
    
    formatted_models = []
    
    for model in models:
        model_id = model.get("id", "Unknown")
        context_length = model.get("context_length", "Unknown")
        
        pricing = model.get("pricing", {})
        prompt_price = pricing.get("prompt", 0)
        completion_price = pricing.get("completion", 0)
        
        # Convert string prices to float if possible
        try:
            if isinstance(prompt_price, str):
                # Handle negative values (like "-1") as 0 for pricing purposes
                prompt_price = max(0, float(prompt_price))
        except (ValueError, TypeError):
            prompt_price = 0
            
        try:
            if isinstance(completion_price, str):
                # Handle negative values (like "-1") as 0 for pricing purposes
                completion_price = max(0, float(completion_price))
        except (ValueError, TypeError):
            completion_price = 0
        
        # Format prices to show in dollars per million tokens
        prompt_price_formatted = f"${prompt_price * 1000000:.4f}" if isinstance(prompt_price, (int, float)) else "Unknown"
        completion_price_formatted = f"${completion_price * 1000000:.4f}" if isinstance(completion_price, (int, float)) else "Unknown"
        
        # Skip non-free models if filter_free is True
        if filter_free and (prompt_price > 0 or completion_price > 0):
            continue
        
        formatted_models.append({
            "id": model_id,
            "context_length": context_length,
            "prompt_price": prompt_price,
            "completion_price": completion_price,
            "prompt_price_formatted": prompt_price_formatted,
            "completion_price_formatted": completion_price_formatted,
            "is_free": prompt_price == 0 and completion_price == 0
        })
    
    # Sort models by context_length (capability) and then by pricing
    return sorted(
        formatted_models, 
        key=lambda x: (
            # Try to convert context_length to int for sorting
            try_convert_to_int(x.get("context_length", 0)),
            # Sort by negative prompt price (higher prices first)
            -try_convert_to_float(x.get("prompt_price", 0))
        ),
        reverse=True
    )


def try_convert_to_int(value):
    """Try to convert a value to int for sorting purposes.
    
    Args:
        value: Value to convert
        
    Returns:
        Integer value or 0 if conversion fails
    """
    if isinstance(value, (int, float)):
        return int(value)
    elif isinstance(value, str):
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    return 0


def try_convert_to_float(value):
    """Try to convert a value to float for sorting purposes.
    
    Args:
        value: Value to convert
        
    Returns:
        Float value or 0.0 if conversion fails
    """
    if isinstance(value, (int, float)):
        # Handle negative values as 0 for consistent sorting
        return max(0.0, float(value))
    elif isinstance(value, str):
        try:
            # Handle negative values as 0 for consistent sorting
            return max(0.0, float(value))
        except (ValueError, TypeError):
            return 0.0
    return 0.0


def save_api_keys_to_file(api_keys: Dict[str, str], file_path: str) -> bool:
    """Save API keys to a JSON file.
    
    Args:
        api_keys: Dictionary of API keys
        file_path: Path to save the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w") as f:
            json.dump(api_keys, f, indent=2)
        return True
    except Exception:
        return False


def load_api_keys_from_file(file_path: str) -> Dict[str, str]:
    """Load API keys from a JSON file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary of API keys
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
    except Exception:
        pass
    
    return {}