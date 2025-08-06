#!/usr/bin/env python3
"""
NFTLLMExtractionStrategy extraction strategy for the cry_a_4mcp.crawl4ai package.

This module provides a specialized extraction strategy for NFTLLMExtractionStrategy content,
with a detailed schema for extracting relevant information from NFTLLMExtractionStrategy sources.
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
logger = logging.getLogger('nft_extraction_strategy')

class NFTLLMExtractionStrategy(LLMExtractionStrategy):
    """Specialized extraction strategy for NFTLLMExtractionStrategy content.
    
    Specialized extraction strategy for NFT content.
    
    This strategy extends the base LLMExtractionStrategy with a specialized schema
    and instruction for extracting information from NFT news articles, marketplace updates,
    and project announcements.
    
    """
    
    # Define the NFTLLMExtractionStrategy-specific schema as a class attribute
    SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {
            "type": "string",
            "description": "The main headline or title of the article"
        },
        "summary": {
            "type": "string",
            "description": "A concise summary of the article's main points"
        },
        "sentiment": {
            "type": "string",
            "enum": [
                "very_negative",
                "negative",
                "neutral",
                "positive",
                "very_positive"
            ],
            "description": "The overall sentiment of the article towards NFTs"
        },
        "category": {
            "type": "string",
            "enum": [
                "marketplace",
                "project_launch",
                "artist_spotlight",
                "sales_data",
                "technology",
                "regulation",
                "adoption",
                "investment",
                "metaverse",
                "gaming",
                "other"
            ],
            "description": "The primary category of the NFT article"
        },
        "market_impact": {
            "type": "object",
            "properties": {
                "short_term": {
                    "type": "string",
                    "description": "Potential short-term impact on NFT markets"
                },
                "long_term": {
                    "type": "string",
                    "description": "Potential long-term impact on NFT markets"
                },
                "affected_sectors": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Sectors of the NFT market likely to be affected"
                }
            },
            "description": "Analysis of potential market impact"
        },
        "key_entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the entity (NFT collection, marketplace, artist, etc.)"
                    },
                    "type": {
                        "type": "string",
                        "enum": [
                            "collection",
                            "marketplace",
                            "artist",
                            "platform",
                            "company",
                            "investor",
                            "project",
                            "other"
                        ],
                        "description": "Type of entity"
                    },
                    "relevance": {
                        "type": "string",
                        "enum": [
                            "primary",
                            "secondary",
                            "mentioned"
                        ],
                        "description": "Relevance of the entity to the article"
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description of the entity"
                    }
                },
                "required": [
                    "name",
                    "type"
                ]
            },
            "description": "Key entities mentioned in the article"
        },
        "nft_data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the NFT collection"
                    },
                    "floor_price": {
                        "type": "string",
                        "description": "Floor price of the collection (with currency)"
                    },
                    "volume": {
                        "type": "string",
                        "description": "Trading volume (with currency and time period)"
                    },
                    "blockchain": {
                        "type": "string",
                        "description": "Blockchain the collection is on (Ethereum, Solana, etc.)"
                    },
                    "notable_sales": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_name": {
                                    "type": "string",
                                    "description": "Name or ID of the NFT item"
                                },
                                "price": {
                                    "type": "string",
                                    "description": "Sale price (with currency)"
                                },
                                "date": {
                                    "type": "string",
                                    "description": "Date of the sale"
                                },
                                "buyer": {
                                    "type": "string",
                                    "description": "Buyer information (if available)"
                                },
                                "seller": {
                                    "type": "string",
                                    "description": "Seller information (if available)"
                                }
                            }
                        },
                        "description": "Notable sales mentioned in the article"
                    }
                },
                "required": [
                    "collection_name"
                ]
            },
            "description": "Specific NFT collection data mentioned in the article"
        },
        "technology_aspects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the technology or feature"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the technology or feature"
                    },
                    "impact": {
                        "type": "string",
                        "description": "Potential impact of this technology"
                    }
                },
                "required": [
                    "name",
                    "description"
                ]
            },
            "description": "Technical aspects or innovations mentioned"
        },
        "metaverse_integration": {
            "type": "object",
            "properties": {
                "platforms": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Metaverse platforms mentioned"
                },
                "features": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Features of metaverse integration"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the metaverse integration"
                }
            },
            "description": "Information about metaverse integration"
        },
        "key_points": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Key points from the article"
        },
        "urgency_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 10,
            "description": "How urgent or time-sensitive the information is (0-10)"
        },
        "content_type": {
            "type": "string",
            "enum": [
                "news",
                "analysis",
                "announcement",
                "interview",
                "opinion",
                "tutorial",
                "market_report",
                "other"
            ],
            "description": "The type of content"
        },
        "publication_date": {
            "type": "string",
            "description": "Publication date of the article"
        },
        "sources": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Sources cited in the article"
        },
        "reliability_score": {
            "type": "number",
            "minimum": 1,
            "maximum": 10,
            "description": "Estimated reliability of the information (1-10)"
        }
    },
    "required": [
        "headline",
        "summary",
        "sentiment",
        "key_points"
    ]
}
        
    # Define the instruction for the LLM as a class attribute
    INSTRUCTION = """
    You are an NFT market analyst. Your task is to extract key information from the provided NFT-related content.
    
    Analyze the content carefully and extract the following information:
    1. The main headline
    2. A concise summary of the content
    3. The overall sentiment towards NFTs (very_negative, negative, neutral, positive, very_positive)!
    4. The primary category of the content
    5. Potential market impact (short-term and long-term)
    6. Key entities mentioned (NFT collections, marketplaces, artists, etc.)
    7. Specific NFT data (collection names, prices, volumes, notable sales)
    8. Technical aspects or innovations mentioned
    9. Metaverse integration details if applicable
    10. Key points from the content
    11. How urgent or time-sensitive the information is
    12. The type of content
    13. Publication date, sources, and reliability assessment
    
    Provide your extraction in a structured JSON format according to the provided schema.
    Be objective and factual in your analysis.
    
    For NFT collections, include as much specific data as mentioned in the content, such as floor prices,
    trading volumes, blockchain platforms, and notable sales.
    
    For metaverse integrations, note any specific platforms mentioned and features described!
    
    If the content discusses technological aspects, extract details about innovations, features, or technical changes!
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
        """Initialize the NFTLLMExtractionStrategy extraction strategy.
        
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
        # Initialize the base class with the schema and instruction class attributes
        super().__init__(
            provider=provider,
            api_token=api_token,
            instruction=self.INSTRUCTION,
            schema=self.SCHEMA,
            base_url=base_url,
            model=model,
            extra_args=extra_args,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs
        )

# Class has been renamed directly, no need for alias