"""OpenRouter API endpoints for model management.

This module provides FastAPI endpoints for interacting with OpenRouter API,
including fetching available models and handling API key management.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ...crypto_crawler.extraction_strategies.ui.openrouter_utils import (
    get_openrouter_models,
    format_openrouter_models,
    save_api_keys_to_file,
    load_api_keys_from_file
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/openrouter", tags=["openrouter"])


class OpenRouterModelsRequest(BaseModel):
    """Request model for fetching OpenRouter models."""
    api_key: str = Field(..., description="OpenRouter API key")
    filter_free: bool = Field(default=False, description="Filter to show only free models")


class OpenRouterModelResponse(BaseModel):
    """Response model for OpenRouter model information."""
    id: str
    context_length: Any
    prompt_price: float
    completion_price: float
    prompt_price_formatted: str
    completion_price_formatted: str
    is_free: bool


class OpenRouterModelsResponse(BaseModel):
    """Response model for OpenRouter models list."""
    success: bool
    models: List[OpenRouterModelResponse]
    message: str


class SaveApiKeyRequest(BaseModel):
    """Request model for saving API key."""
    provider: str = Field(..., description="API provider name (e.g., 'openrouter')")
    api_key: str = Field(..., description="API key to save")


class SaveApiKeyResponse(BaseModel):
    """Response model for API key save operation."""
    success: bool
    message: str


@router.post("/models", response_model=OpenRouterModelsResponse)
async def get_models(request: OpenRouterModelsRequest):
    """Fetch available models from OpenRouter API.
    
    Args:
        request: Request containing API key and filter options
        
    Returns:
        OpenRouterModelsResponse: List of available models with pricing info
        
    Raises:
        HTTPException: If API key is invalid or request fails
    """
    try:
        logger.info(f"Fetching OpenRouter models with filter_free={request.filter_free}")
        
        # Validate API key
        if not request.api_key or not request.api_key.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key is required"
            )
        
        # Fetch models from OpenRouter
        success, models_data, message = await get_openrouter_models(request.api_key)
        
        if not success:
            logger.error(f"Failed to fetch OpenRouter models: {message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch models: {message}"
            )
        
        # Format models for response
        formatted_models = format_openrouter_models(models_data, request.filter_free)
        
        logger.info(f"Successfully fetched {len(formatted_models)} OpenRouter models")
        
        return OpenRouterModelsResponse(
            success=True,
            models=[OpenRouterModelResponse(**model) for model in formatted_models],
            message=f"Successfully retrieved {len(formatted_models)} models"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching OpenRouter models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/save-api-key", response_model=SaveApiKeyResponse)
async def save_api_key(request: SaveApiKeyRequest):
    """Save API key to configuration file.
    
    Args:
        request: Request containing provider name and API key
        
    Returns:
        SaveApiKeyResponse: Success status and message
        
    Raises:
        HTTPException: If saving fails
    """
    try:
        logger.info(f"Saving API key for provider: {request.provider}")
        
        # Validate inputs
        if not request.provider or not request.provider.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider name is required"
            )
        
        if not request.api_key or not request.api_key.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key is required"
            )
        
        # Get the config file path
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "crawl4ai", "extraction_strategies", "ui", "config", "api_keys.json"
        )
        config_path = os.path.abspath(config_path)
        
        # Load existing API keys
        existing_keys = load_api_keys_from_file(config_path)
        
        # Update with new key
        existing_keys[request.provider] = request.api_key
        
        # Save updated keys
        success = save_api_keys_to_file(existing_keys, config_path)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save API key"
            )
        
        logger.info(f"Successfully saved API key for provider: {request.provider}")
        
        return SaveApiKeyResponse(
            success=True,
            message=f"API key for {request.provider} saved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


def setup_openrouter_routes() -> APIRouter:
    """Setup OpenRouter routes.
    
    Returns:
        APIRouter: Configured router with OpenRouter endpoints
    """
    logger.info("Setting up OpenRouter API routes")
    return router