#!/usr/bin/env python3
"""
ProductLLMExtractionStrategy extraction strategy for the cry_a_4mcp.crawl4ai package.

This module provides a specialized extraction strategy for ProductLLMExtractionStrategy content,
with a detailed schema for extracting relevant information from ProductLLMExtractionStrategy sources.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from ..base import LLMExtractionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('product_extraction_strategy')

class ProductLLMExtractionStrategy(LLMExtractionStrategy):
    """Specialized extraction strategy for ProductLLMExtractionStrategy content.
    
    Product-specific LLM extraction strategy.
    
    This strategy is specialized for extracting structured information from product content,
    including product listings, specifications, pricing, reviews, and other e-commerce data.
    
    Attributes:
        provider (str): The LLM provider to use (e.g., "openrouter", "openai").
        api_token (str): The API token for the LLM provider.
        model (str): The model to use for extraction.
        instruction (str): The instruction for the LLM.
        schema (dict): The JSON schema for the extraction result.
        max_retries (int): Maximum number of retries for API calls.
        retry_delay (float): Delay between retries in seconds.
        timeout (float): Timeout for API calls in seconds.
    
    """
    
    def __init__(self, 
                 provider: str = "openai", 
                 api_token: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 extra_args: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3,
                 timeout: int = 60,
                 **kwargs):
        """Initialize the ProductLLMExtractionStrategy extraction strategy.
        
        Args:
            provider: LLM provider (e.g., "openai", "groq", "openrouter")
            api_token: API token for the LLM provider
            base_url: Optional base URL for the API
            model: Model to use for extraction
            extra_args: Additional arguments to pass to the API
            max_retries: Maximum number of retries for API calls
            timeout: Timeout for API calls in seconds
            **kwargs: Additional configuration options
        """
        # Define the ProductLLMExtractionStrategy-specific schema
        product_schema = {
    "type": "object",
    "properties": {
        "product_name": {
            "type": "string",
            "description": "The name or title of the product"
        },
        "brand": {
            "type": "string",
            "description": "The brand or manufacturer of the product"
        },
        "description": {
            "type": "string",
            "description": "A description of the product"
        },
        "summary": {
            "type": "string",
            "description": "A concise summary of the product (2-3 sentences)"
        },
        "category": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Product categories or classifications"
        },
        "price": {
            "type": "object",
            "properties": {
                "current": {
                    "type": "number"
                },
                "currency": {
                    "type": "string"
                },
                "original": {
                    "type": "number"
                },
                "discount_percentage": {
                    "type": "number"
                },
                "discount_amount": {
                    "type": "number"
                },
                "unit": {
                    "type": "string"
                }
            },
            "description": "Price information"
        },
        "availability": {
            "type": "string",
            "enum": [
                "in_stock",
                "out_of_stock",
                "pre_order",
                "limited",
                "unknown"
            ],
            "description": "Product availability status"
        },
        "specifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "value": {
                        "type": "string"
                    },
                    "unit": {
                        "type": "string"
                    }
                },
                "required": [
                    "name",
                    "value"
                ]
            },
            "description": "Technical specifications of the product"
        },
        "features": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Key features or selling points of the product"
        },
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string"
                    },
                    "alt_text": {
                        "type": "string"
                    },
                    "is_primary": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "url"
                ]
            },
            "description": "Product images"
        },
        "variants": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "options": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "name",
                    "options"
                ]
            },
            "description": "Product variants (e.g., colors, sizes)"
        },
        "reviews": {
            "type": "object",
            "properties": {
                "average_rating": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 5
                },
                "count": {
                    "type": "integer"
                },
                "distribution": {
                    "type": "object",
                    "properties": {
                        "5_star": {
                            "type": "integer"
                        },
                        "4_star": {
                            "type": "integer"
                        },
                        "3_star": {
                            "type": "integer"
                        },
                        "2_star": {
                            "type": "integer"
                        },
                        "1_star": {
                            "type": "integer"
                        }
                    }
                },
                "highlights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string"
                            },
                            "sentiment": {
                                "type": "string",
                                "enum": [
                                    "positive",
                                    "negative",
                                    "neutral"
                                ]
                            }
                        },
                        "required": [
                            "text",
                            "sentiment"
                        ]
                    }
                }
            },
            "description": "Product review information"
        },
        "seller": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "rating": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 5
                },
                "is_official": {
                    "type": "boolean"
                }
            },
            "description": "Information about the seller"
        },
        "shipping": {
            "type": "object",
            "properties": {
                "free_shipping": {
                    "type": "boolean"
                },
                "estimated_delivery": {
                    "type": "string"
                },
                "options": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string"
                            },
                            "cost": {
                                "type": "number"
                            },
                            "currency": {
                                "type": "string"
                            },
                            "estimated_days": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "method"
                        ]
                    }
                }
            },
            "description": "Shipping information"
        },
        "warranty": {
            "type": "string",
            "description": "Warranty information"
        },
        "return_policy": {
            "type": "string",
            "description": "Return policy information"
        },
        "certifications": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Product certifications (e.g., Energy Star, Organic)"
        },
        "pros": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Positive aspects of the product"
        },
        "cons": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Negative aspects of the product"
        },
        "best_uses": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Recommended uses for the product"
        },
        "target_audience": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Target audience or user groups for the product"
        },
        "competitor_products": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Mentioned competitor products"
        },
        "promotion": {
            "type": "object",
            "properties": {
                "has_promotion": {
                    "type": "boolean"
                },
                "promotion_type": {
                    "type": "string"
                },
                "details": {
                    "type": "string"
                },
                "expiry": {
                    "type": "string"
                }
            },
            "description": "Promotional information"
        }
    },
    "required": [
        "product_name",
        "description",
        "summary"
    ]
}
        
        # Define the instruction for the LLM
        instruction = """
        Extract structured information from the provided product listing or e-commerce content.
        Focus on identifying the product name, brand, and creating a concise summary.
        Extract the product description, categories, and price information.
        Identify the product's availability status.
        Extract technical specifications and key features.
        Note any product variants (e.g., colors, sizes)
        Extract review information including average rating and highlights.
        Identify seller information if available.
        Extract shipping, warranty, and return policy information.
        Note any certifications the product has.
        Identify pros and cons of the product.
        Determine the best uses and target audience for the product.
        Note any competitor products mentioned.
        Identify any promotional offers.
        
        Ensure the extraction is objective and based solely on the content provided.
        Do not include information not present in the product listing.
        """
        
        # Initialize the base class with the schema and instruction
        super().__init__(
            provider=provider,
            api_token=api_token,
            instruction=instruction,
            schema=product_schema,
            base_url=base_url,
            model=model,
            extra_args=extra_args,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs
        )

# Class is already correctly named, no alias needed