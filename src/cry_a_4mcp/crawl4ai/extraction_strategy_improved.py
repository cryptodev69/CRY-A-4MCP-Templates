#!/usr/bin/env python3
"""
Improved extraction strategies for the cry_a_4mcp.crawl4ai package.

This module provides enhanced implementations of extraction strategies with:
1. Improved error handling and logging
2. Performance optimizations
3. Flexible model and provider support
"""

import json
import os
import time
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('extraction_strategy')

# Define custom exceptions for better error handling
class ExtractionError(Exception):
    """Base exception for extraction errors."""
    pass

class APIConnectionError(ExtractionError):
    """Exception raised for API connection issues."""
    pass

class APIResponseError(ExtractionError):
    """Exception raised for API response errors."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API returned error {status_code}: {message}")

class ContentParsingError(ExtractionError):
    """Exception raised for content parsing errors."""
    pass

# Performance monitoring decorator
def measure_performance(func):
    """Decorator to measure and log function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {elapsed_time:.2f} seconds")
            # Add performance data to result metadata
            if isinstance(result, dict) and "_metadata" in result:
                if "performance" not in result["_metadata"]:
                    result["_metadata"]["performance"] = {}
                result["_metadata"]["performance"]["extraction_time"] = elapsed_time
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed_time:.2f} seconds: {str(e)}")
            raise
    return wrapper

# Retry mechanism for API calls
async def retry_async(func, retries=3, backoff_factor=1.5, exceptions=(APIConnectionError,)):
    """Retry an async function with exponential backoff."""
    max_retries = retries
    retry_count = 0
    last_exception = None
    
    while retry_count < max_retries:
        try:
            return await func()
        except exceptions as e:
            retry_count += 1
            last_exception = e
            if retry_count >= max_retries:
                break
                
            # Calculate backoff time
            backoff_time = backoff_factor ** (retry_count - 1)
            logger.warning(f"Retry {retry_count}/{max_retries} after {backoff_time:.2f}s due to: {str(e)}")
            await asyncio.sleep(backoff_time)
    
    # If we've exhausted retries, raise the last exception
    logger.error(f"All {max_retries} retries failed")
    raise last_exception

# Provider configuration
PROVIDER_CONFIGS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-3.5-turbo",
        "models": {
            "gpt-3.5-turbo": {"max_tokens": 4096, "supports_json": True},
            "gpt-4": {"max_tokens": 8192, "supports_json": True},
            "gpt-4-turbo": {"max_tokens": 16384, "supports_json": True}
        }
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "moonshotai/kimi-k2:free",
        "models": {
            "moonshotai/kimi-k2:free": {"max_tokens": 4096, "supports_json": True},
            "qwen/qwen-2.5-72b-instruct:free": {"max_tokens": 4096, "supports_json": True},
            "mistralai/mistral-small-24b-instruct-2501:free": {"max_tokens": 4096, "supports_json": True},
            "anthropic/claude-3-opus:beta": {"max_tokens": 8192, "supports_json": True}
        },
        "headers": {
            "HTTP-Referer": "https://crypto-news-crawler.com",
            "X-Title": "Crypto News Crawler"
        }
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama3-8b-8192",
        "models": {
            "llama3-8b-8192": {"max_tokens": 4096, "supports_json": True},
            "llama3-70b-8192": {"max_tokens": 4096, "supports_json": True},
            "mixtral-8x7b-32768": {"max_tokens": 4096, "supports_json": True}
        }
    }
}

class LLMExtractionStrategy:
    """Enhanced strategy for extracting information from web pages using LLMs.
    
    Features:
    - Improved error handling with specific exception types
    - Performance monitoring and optimization
    - Flexible model and provider support
    - Automatic retries with exponential backoff
    - Detailed logging
    """
    
    def __init__(self, 
                 provider: str = "openai", 
                 api_token: Optional[str] = None,
                 instruction: Optional[str] = None,
                 schema: Optional[Dict[str, Any]] = None,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 extra_args: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3,
                 timeout: int = 60,
                 **kwargs):
        """Initialize the extraction strategy with configuration.
        
        Args:
            provider: LLM provider (e.g., "openai", "groq", "openrouter")
            api_token: API token for the LLM provider
            instruction: Custom instruction for the LLM
            schema: JSON schema for structured extraction
            base_url: Optional base URL for the API
            model: Model to use for extraction
            extra_args: Additional arguments to pass to the API
            max_retries: Maximum number of retries for API calls
            timeout: Timeout for API calls in seconds
            **kwargs: Additional configuration options
        """
        self.provider = provider.lower()
        self.api_token = api_token or os.environ.get(f"{self.provider.upper()}_API_KEY", "")
        self.instruction = instruction
        self.schema = schema
        self.extra_args = extra_args or {}
        self.config = kwargs
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Get provider configuration
        provider_config = PROVIDER_CONFIGS.get(self.provider, {})
        
        # Set base URL
        self.base_url = base_url or provider_config.get("base_url")
        if not self.base_url and self.provider == "openai":
            self.base_url = "https://api.openai.com/v1"
            
        # Set model
        self.model = model or self.extra_args.get("model") or provider_config.get("default_model")
        if not self.model:
            if self.provider == "openrouter":
                self.model = "moonshotai/kimi-k2:free"
            else:
                self.model = "gpt-3.5-turbo"
                
        # Set model-specific parameters
        model_config = provider_config.get("models", {}).get(self.model, {})
        self.max_tokens = self.extra_args.get("max_tokens", model_config.get("max_tokens", 1500))
        self.temperature = self.extra_args.get("temperature", 0.0)  # Low temperature for factual extraction
        
        # Set provider-specific headers
        self.headers = provider_config.get("headers", {})
        
        # Validate required parameters
        if not self.api_token:
            raise ValueError(f"API token must be provided for {self.provider} LLMExtractionStrategy")
            
        logger.info(f"Initialized {self.provider} extraction strategy with model {self.model}")
        
    @measure_performance
    async def extract(self, url: str, html: str, instruction: Optional[str] = None, 
                     schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract information from content using an LLM.
        
        Args:
            url: The URL of the content
            html: The HTML or markdown content to extract information from
            instruction: Optional override for the default instruction
            schema: Optional override for the default schema
            
        Returns:
            Dictionary of extracted information
        """
        logger.info(f"Starting LLM extraction for URL: {url}")
        logger.debug(f"Provider: {self.provider}, Base URL: {self.base_url}")
        logger.debug(f"Model: {self.model}")
        
        # Use provided instruction/schema or fall back to instance defaults
        instruction_text = instruction or self.instruction
        schema_obj = schema or self.schema
        
        logger.debug(f"Instruction available: {instruction_text is not None}")
        logger.debug(f"Schema available: {schema_obj is not None}")
        
        if not instruction_text:
            raise ValueError("Instruction must be provided for extraction")
        
        # Prepare the system message with instruction and schema
        system_message = instruction_text
        if schema_obj:
            system_message += f"\n\nOutput should conform to this JSON schema:\n{json.dumps(schema_obj, indent=2)}"
        
        # Prepare the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        # Add provider-specific headers
        headers.update(self.headers)
        
        # Prepare the API endpoint
        api_url = f"{self.base_url}/chat/completions" if self.base_url else "https://api.openai.com/v1/chat/completions"
        logger.debug(f"API URL: {api_url}")
        
        # Truncate content if too long to optimize token usage
        # This is a simple approach - more sophisticated content truncation could be implemented
        content_limit = 15000  # Adjust based on model context window and needs
        truncated_html = html[:content_limit] if len(html) > content_limit else html
        if len(html) > content_limit:
            logger.info(f"Content truncated from {len(html)} to {content_limit} characters")
        
        # Prepare the request payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"URL: {url}\n\nContent:\n{truncated_html}"}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"}
        }
        
        # Add any extra arguments from self.extra_args, excluding 'headers' which we handled separately
        extra_args_copy = self.extra_args.copy()
        extra_args_copy.pop("headers", None)
        payload.update(extra_args_copy)
        
        logger.debug(f"Payload prepared with model: {payload.get('model')}")
        
        # Define the API call function for retry mechanism
        async def make_api_call():
            try:
                logger.debug(f"Sending request to LLM API...")
                async with aiohttp.ClientSession() as session:
                    async with session.post(api_url, headers=headers, json=payload, timeout=self.timeout) as response:
                        logger.debug(f"Response status: {response.status}")
                        
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"API error: {response.status} - {error_text[:500]}")
                            raise APIResponseError(response.status, error_text)
                        
                        return await response.json()
            except aiohttp.ClientError as e:
                logger.error(f"API connection error: {str(e)}")
                raise APIConnectionError(f"API request failed: {str(e)}")
        
        # Make the API call with retries
        try:
            result = await retry_async(
                make_api_call,
                retries=self.max_retries,
                exceptions=(APIConnectionError,)
            )
            
            logger.debug(f"Received response from API")
            
            # Extract the content from the response
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.debug(f"Extracted content from response: {content[:100]}...")
                
                # Parse the JSON response
                try:
                    extracted_data = json.loads(content)
                    logger.debug(f"Successfully parsed JSON response")
                    
                    # Add metadata about the extraction
                    if "_metadata" not in extracted_data:
                        extracted_data["_metadata"] = {}
                        
                    # Add model information if available
                    if "model" in result:
                        extracted_data["_metadata"]["model"] = result["model"]
                        logger.debug(f"Added model info: {result['model']}")
                        
                    # Add usage information if available
                    if "usage" in result:
                        extracted_data["_metadata"]["usage"] = result["usage"]
                        logger.debug(f"Added usage info")
                        
                    # Add extraction timestamp
                    extracted_data["_metadata"]["timestamp"] = time.time()
                    
                    logger.info(f"Extraction completed successfully")
                    return extracted_data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {str(e)}")
                    logger.error(f"Raw content: {content}")
                    raise ContentParsingError(f"Failed to parse LLM response as JSON: {e}\nResponse: {content}")
            else:
                logger.error(f"No choices in response: {result}")
                raise APIResponseError(200, "No choices found in API response")
                
        except ExtractionError as e:
            # Re-raise extraction errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error during extraction: {str(e)}")
            raise ExtractionError(f"Extraction failed: {str(e)}")

    async def validate_provider_connection(self) -> Tuple[bool, Optional[str]]:
        """Validate the connection to the provider.
        
        Returns:
            Tuple of (success, error_message)
        """
        logger.info(f"Validating connection to {self.provider}")
        
        # Prepare a minimal API request to check connection
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        # Add provider-specific headers
        headers.update(self.headers)
        
        # Prepare the API endpoint for models list
        if self.provider == "openrouter":
            api_url = "https://openrouter.ai/api/v1/models"
        else:
            api_url = f"{self.base_url}/models" if self.base_url else "https://api.openai.com/v1/models"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers, timeout=self.timeout) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Provider validation failed: {response.status} - {error_text[:500]}")
                        return False, f"API returned error {response.status}: {error_text}"
                    
                    # Successfully connected
                    logger.info(f"Successfully validated connection to {self.provider}")
                    return True, None
        except Exception as e:
            logger.error(f"Provider validation failed: {str(e)}")
            return False, str(e)
            
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get a list of available providers.
        
        Returns:
            List of provider names
        """
        return list(PROVIDER_CONFIGS.keys())
    
    @classmethod
    def get_available_models(cls, provider: str) -> List[str]:
        """Get a list of available models for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List of model names
        """
        provider_config = PROVIDER_CONFIGS.get(provider.lower(), {})
        return list(provider_config.get("models", {}).keys())