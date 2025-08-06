#!/usr/bin/env python3
"""
FinancialLLMExtractionStrategy extraction strategy for the cry_a_4mcp.crawl4ai package.

This module provides a specialized extraction strategy for FinancialLLMExtractionStrategy content,
with a detailed schema for extracting relevant information from FinancialLLMExtractionStrategy sources.
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
logger = logging.getLogger('financial_extraction_strategy')

class FinancialLLMExtractionStrategy(LLMExtractionStrategy):
    """Specialized extraction strategy for FinancialLLMExtractionStrategy content.
    
    Financial-specific LLM extraction strategy.
    
    This strategy is specialized for extracting structured information from financial content,
    including financial news, market analyses, investment reports, and cryptocurrency data.
    
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
        """Initialize the FinancialLLMExtractionStrategy extraction strategy.
        
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
        # Define the FinancialLLMExtractionStrategy-specific schema
        financial_schema = {
    "type": "object",
    "properties": {
        "headline": {
            "type": "string",
            "description": "The headline or title of the financial content"
        },
        "summary": {
            "type": "string",
            "description": "A concise summary of the financial content (2-3 sentences)"
        },
        "key_points": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Key points or takeaways from the financial content"
        },
        "market_impact": {
            "type": "object",
            "properties": {
                "short_term": {
                    "type": "string",
                    "enum": [
                        "very_negative",
                        "negative",
                        "neutral",
                        "positive",
                        "very_positive",
                        "mixed",
                        "uncertain"
                    ],
                    "description": "Short-term market impact assessment"
                },
                "long_term": {
                    "type": "string",
                    "enum": [
                        "very_negative",
                        "negative",
                        "neutral",
                        "positive",
                        "very_positive",
                        "mixed",
                        "uncertain"
                    ],
                    "description": "Long-term market impact assessment"
                },
                "affected_sectors": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Sectors likely to be affected"
                },
                "explanation": {
                    "type": "string",
                    "description": "Explanation of the market impact assessment"
                }
            },
            "description": "Assessment of potential market impact"
        },
        "financial_metrics": {
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
                    "previous_value": {
                        "type": "string"
                    },
                    "change": {
                        "type": "string"
                    },
                    "change_percentage": {
                        "type": "string"
                    },
                    "period": {
                        "type": "string"
                    },
                    "currency": {
                        "type": "string"
                    }
                },
                "required": [
                    "name",
                    "value"
                ]
            },
            "description": "Financial metrics mentioned (e.g., revenue, profit, EPS)"
        },
        "market_data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "asset": {
                        "type": "string"
                    },
                    "price": {
                        "type": "string"
                    },
                    "change": {
                        "type": "string"
                    },
                    "change_percentage": {
                        "type": "string"
                    },
                    "volume": {
                        "type": "string"
                    },
                    "market_cap": {
                        "type": "string"
                    },
                    "timestamp": {
                        "type": "string"
                    }
                },
                "required": [
                    "asset"
                ]
            },
            "description": "Market data for assets mentioned (stocks, cryptocurrencies, etc.)"
        },
        "companies": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "ticker": {
                        "type": "string"
                    },
                    "role": {
                        "type": "string"
                    },
                    "sentiment": {
                        "type": "string",
                        "enum": [
                            "very_negative",
                            "negative",
                            "neutral",
                            "positive",
                            "very_positive",
                            "mixed"
                        ]
                    }
                },
                "required": [
                    "name"
                ]
            },
            "description": "Companies mentioned in the content"
        },
        "cryptocurrencies": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "symbol": {
                        "type": "string"
                    },
                    "price": {
                        "type": "string"
                    },
                    "change": {
                        "type": "string"
                    },
                    "change_percentage": {
                        "type": "string"
                    },
                    "market_cap": {
                        "type": "string"
                    },
                    "volume": {
                        "type": "string"
                    },
                    "sentiment": {
                        "type": "string",
                        "enum": [
                            "very_negative",
                            "negative",
                            "neutral",
                            "positive",
                            "very_positive",
                            "mixed"
                        ]
                    }
                },
                "required": [
                    "name"
                ]
            },
            "description": "Cryptocurrencies mentioned in the content"
        },
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "date": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "importance": {
                        "type": "string",
                        "enum": [
                            "low",
                            "medium",
                            "high",
                            "critical"
                        ]
                    }
                },
                "required": [
                    "name",
                    "description"
                ]
            },
            "description": "Financial events mentioned (e.g., earnings reports, IPOs, mergers)"
        },
        "regulations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "jurisdiction": {
                        "type": "string"
                    },
                    "status": {
                        "type": "string"
                    },
                    "impact": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    }
                },
                "required": [
                    "name",
                    "description"
                ]
            },
            "description": "Regulatory developments mentioned"
        },
        "risk_factors": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Risk factors mentioned in the content"
        },
        "opportunities": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Investment opportunities mentioned"
        },
        "expert_opinions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "expert": {
                        "type": "string"
                    },
                    "organization": {
                        "type": "string"
                    },
                    "opinion": {
                        "type": "string"
                    },
                    "sentiment": {
                        "type": "string",
                        "enum": [
                            "very_negative",
                            "negative",
                            "neutral",
                            "positive",
                            "very_positive",
                            "mixed"
                        ]
                    }
                },
                "required": [
                    "expert",
                    "opinion"
                ]
            },
            "description": "Expert opinions quoted in the content"
        },
        "technical_analysis": {
            "type": "object",
            "properties": {
                "indicators": {
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
                            "signal": {
                                "type": "string",
                                "enum": [
                                    "buy",
                                    "sell",
                                    "hold",
                                    "neutral"
                                ]
                            }
                        },
                        "required": [
                            "name",
                            "signal"
                        ]
                    }
                },
                "patterns": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "support_levels": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "resistance_levels": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "overall_signal": {
                    "type": "string",
                    "enum": [
                        "strong_buy",
                        "buy",
                        "neutral",
                        "sell",
                        "strong_sell"
                    ]
                }
            },
            "description": "Technical analysis information mentioned"
        },
        "fundamental_analysis": {
            "type": "object",
            "properties": {
                "valuation_metrics": {
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
                            "comparison": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "name",
                            "value"
                        ]
                    }
                },
                "growth_metrics": {
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
                            "period": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "name",
                            "value"
                        ]
                    }
                },
                "strengths": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "weaknesses": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "overall_assessment": {
                    "type": "string"
                }
            },
            "description": "Fundamental analysis information mentioned"
        },
        "sentiment": {
            "type": "string",
            "enum": [
                "very_negative",
                "negative",
                "neutral",
                "positive",
                "very_positive",
                "mixed"
            ],
            "description": "Overall sentiment of the financial content"
        },
        "sources": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Sources cited in the financial content"
        },
        "publication_date": {
            "type": "string",
            "description": "Publication date of the financial content"
        },
        "author": {
            "type": "string",
            "description": "Author of the financial content"
        },
        "content_type": {
            "type": "string",
            "enum": [
                "news",
                "analysis",
                "report",
                "press_release",
                "earnings_call",
                "market_update",
                "research",
                "opinion",
                "forecast",
                "regulatory_filing",
                "technical_analysis",
                "fundamental_analysis",
                "crypto_analysis"
            ],
            "description": "Type of financial content"
        },
        "audience": {
            "type": "string",
            "enum": [
                "general",
                "retail_investors",
                "institutional_investors",
                "traders",
                "analysts",
                "regulators"
            ],
            "description": "Target audience of the financial content"
        },
        "reliability_score": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10,
            "description": "Estimated reliability score of the information (1-10)"
        }
    },
    "required": [
        "headline",
        "summary",
        "key_points",
        "sentiment"
    ]
}
        
        # Define the instruction for the LLM
        instruction = """
        Extract structured information from the provided financial content.
        Focus on identifying the headline, creating a concise summary, and extracting key points.
        Assess the overall sentiment of the content.
        Identify any market impact assessments, including short-term and long-term effects.
        Extract financial metrics mentioned (e.g., revenue, profit, EPS).
        Extract market data for assets mentioned (stocks, cryptocurrencies, etc.)
        Identify companies and cryptocurrencies mentioned, along with their sentiment.
        Note any financial events mentioned (e.g., earnings reports, IPOs, mergers).
        Identify regulatory developments that may impact markets.
        Extract risk factors and investment opportunities mentioned.
        Note expert opinions quoted in the content.
        Extract any technical or fundamental analysis information.
        Identify the content type and target audience.
        Assess the reliability of the information on a scale of 1-10.
        
        For cryptocurrency-specific content:
        - Pay special attention to blockchain technologies, tokens, and protocols mentioned
        - Note any technical developments, upgrades, or forks
        - Identify regulatory concerns specific to cryptocurrencies
        - Extract information about market sentiment, trading volumes, and liquidity
        - Note any security issues, hacks, or vulnerabilities mentioned
        
        Ensure the extraction is objective and based solely on the content provided.
        Do not include information not present in the financial content!
        """
        
        # Initialize the base class with the schema and instruction
        super().__init__(
            provider=provider,
            api_token=api_token,
            instruction=instruction,
            schema=financial_schema,
            base_url=base_url,
            model=model,
            extra_args=extra_args,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs
        )

# Class has been renamed directly, no alias needed