#!/usr/bin/env python3
"""
Extraction strategies for the cry_a_4mcp.crawl4ai package.
"""

import json
import os
import aiohttp
from typing import Dict, List, Optional, Any, Union


class LLMExtractionStrategy:
    """
    Strategy for extracting information from web pages using LLMs.
    This implementation supports OpenAI-compatible APIs including OpenRouter.
    """
    
    def __init__(self, 
                 provider: str = "openai", 
                 api_token: Optional[str] = None,
                 instruction: Optional[str] = None,
                 schema: Optional[Dict[str, Any]] = None,
                 base_url: Optional[str] = None,
                 extra_args: Optional[Dict[str, Any]] = None,
                 **kwargs):
        """
        Initialize the extraction strategy with configuration.
        
        Args:
            provider: LLM provider (e.g., "openai", "groq", "openrouter")
            api_token: API token for the LLM provider
            instruction: Custom instruction for the LLM
            schema: JSON schema for structured extraction
            base_url: Optional base URL for the API (useful for OpenRouter)
            extra_args: Additional arguments to pass to the API
            **kwargs: Additional configuration options
        """
        self.provider = provider
        self.api_token = api_token or os.environ.get("OPENAI_API_KEY", "")
        self.instruction = instruction
        self.schema = schema
        self.base_url = base_url
        self.extra_args = extra_args or {}
        self.config = kwargs
        
        # Default model settings
        # If using OpenRouter, default to a free model that supports JSON output
        if self.base_url and "openrouter.ai" in self.base_url:
            # Use one of these free models that support JSON output format
            self.model = self.extra_args.get("model", "moonshotai/kimi-k2:free")
            # Alternative free models that support JSON output:
            # - "qwen/qwen-2.5-72b-instruct:free"
            # - "mistralai/mistral-small-24b-instruct-2501:free"
        else:
            self.model = self.extra_args.get("model", "gpt-3.5-turbo")
            
        self.temperature = self.extra_args.get("temperature", 0.0)  # Low temperature for factual extraction
        self.max_tokens = self.extra_args.get("max_tokens", 1500)
        
        # Validate required parameters
        if not self.api_token:
            raise ValueError("API token must be provided for LLMExtractionStrategy")
        
    async def extract(self, url: str, html: str, instruction: Optional[str] = None, 
                       schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract information from content using an LLM.
        
        Args:
            url: The URL of the content
            html: The HTML or markdown content to extract information from
            instruction: Optional override for the default instruction
            schema: Optional override for the default schema
            
        Returns:
            Dictionary of extracted information
        """
        print(f"\n[DEBUG] Starting LLM extraction for URL: {url}")
        print(f"[DEBUG] Provider: {self.provider}, Base URL: {self.base_url}")
        print(f"[DEBUG] Model: {self.model}")
        
        # Use provided instruction/schema or fall back to instance defaults
        instruction_text = instruction or self.instruction
        schema_obj = schema or self.schema
        
        print(f"[DEBUG] Instruction available: {instruction_text is not None}")
        print(f"[DEBUG] Schema available: {schema_obj is not None}")
        
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
        
        # Add OpenRouter specific headers if needed
        if self.base_url and "openrouter.ai" in self.base_url:
            headers.update({
                "HTTP-Referer": self.extra_args.get("headers", {}).get("HTTP-Referer", "https://crypto-news-crawler.com"),
                "X-Title": self.extra_args.get("headers", {}).get("X-Title", "Crypto News Crawler")
            })
            print(f"[DEBUG] Added OpenRouter specific headers")
        
        # Prepare the API endpoint
        api_url = f"{self.base_url}/chat/completions" if self.base_url else "https://api.openai.com/v1/chat/completions"
        print(f"[DEBUG] API URL: {api_url}")
        
        # Prepare the request payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"URL: {url}\n\nContent:\n{html[:500]}... (content truncated for debug)"}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"}
        }
        
        # Add any extra arguments from self.extra_args, excluding 'headers' which we handled separately
        extra_args_copy = self.extra_args.copy()
        extra_args_copy.pop("headers", None)
        payload.update(extra_args_copy)
        
        print(f"[DEBUG] Payload prepared with model: {payload.get('model')}")
        
        try:
            print(f"[DEBUG] Sending request to LLM API...")
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload, timeout=60) as response:
                    print(f"[DEBUG] Response status: {response.status}")
                    
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"[DEBUG] Error response: {error_text[:500]}")
                        raise Exception(f"API request failed with status {response.status}: {error_text}")
                    
                    result = await response.json()
                    print(f"[DEBUG] Received response from API")
                    
                    # Extract the content from the response
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0]["message"]["content"]
                        print(f"[DEBUG] Extracted content from response: {content[:100]}...")
                        
                        # Parse the JSON response
                        try:
                            extracted_data = json.loads(content)
                            print(f"[DEBUG] Successfully parsed JSON response")
                            
                            # Add metadata about the extraction
                            if "_metadata" not in extracted_data:
                                extracted_data["_metadata"] = {}
                                
                            # Add model information if available
                            if "model" in result:
                                extracted_data["_metadata"]["model"] = result["model"]
                                print(f"[DEBUG] Added model info: {result['model']}")
                                
                            # Add usage information if available
                            if "usage" in result:
                                extracted_data["_metadata"]["usage"] = result["usage"]
                                print(f"[DEBUG] Added usage info")
                                
                            print(f"[DEBUG] Extraction completed successfully")
                            return extracted_data
                        except json.JSONDecodeError as e:
                            print(f"[DEBUG] JSON parse error: {str(e)}")
                            print(f"[DEBUG] Raw content: {content}")
                            raise Exception(f"Failed to parse LLM response as JSON: {e}\nResponse: {content}")
                    else:
                        print(f"[DEBUG] No choices in response: {result}")
                        raise Exception("No choices found in API response")
                        
        except aiohttp.ClientError as e:
            print(f"[DEBUG] Client error: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            print(f"[DEBUG] Exception: {str(e)}")
            raise Exception(f"Extraction failed: {str(e)}")