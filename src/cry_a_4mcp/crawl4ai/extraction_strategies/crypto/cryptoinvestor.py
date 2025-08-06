#!/usr/bin/env python3
# pyright: ignore
# type: ignore
# basedpyright: ignore
# This is a template file and not valid Python syntax
# It contains template variables that will be replaced by the template generator
# The following line ensures this file is not treated as Python code by linters
# pyright: strict-optional=false
"""
CryptoInvestor extraction strategy for the cry_a_4mcp.crawl4ai package.

This module provides a specialized extraction strategy for CryptoInvestor content,
with a detailed schema for extracting relevant information from CryptoInvestor sources.
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
logger = logging.getLogger('cryptoinvestor_extraction_strategy')

# type: ignore
class CryptoinvestorLLMExtractionStrategy(LLMExtractionStrategy):
    """Specialized extraction strategy for CryptoInvestor content.
    
    This description positions the extraction framework for institutional investors who prioritize:

Fundamental value indicators (protocol revenue, TVL trends)
Institutional capital flow analysis
Regulatory intelligence across jurisdictions
Macroeconomic correlation patterns
Market structure assessmen
    """
    
    # type: ignore
    def __init__(self, 
                 provider: str = "openrouter", 
                 api_token: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 extra_args: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3,
                 timeout: int = 60,
                 **kwargs):
        """Initialize the CryptoInvestor extraction strategy.
        
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
        # Define the CryptoInvestor-specific schema
        # type: ignore
        cryptoinvestor_schema = {
    "article_metadata": {
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "description": "Publication source of the article"
            },
            "author": {
                "type": "string",
                "description": "Author of the article"
            },
            "publication_date": {
                "type": "string",
                "format": "date-time",
                "description": "Publication timestamp"
            },
            "credibility_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Credibility rating of the publication source"
            }
        },
        "description": "Metadata about the article source and publication"
    },
    "market_fundamentals": {
        "type": "object",
        "properties": {
            "mentioned_assets": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "Full name of the cryptocurrency asset"
                        },
                        "ticker": {
                            "type": "string",
                            "description": "Trading symbol of the asset"
                        },
                        "market_cap": {
                            "type": "number",
                            "description": "Market capitalization in USD if mentioned"
                        },
                        "trading_volume": {
                            "type": "number",
                            "description": "24h trading volume if mentioned"
                        },
                        "tvl": {
                            "type": "number",
                            "description": "Total Value Locked for DeFi protocols if mentioned"
                        }
                    },
                    "required": [
                        "asset_name"
                    ]
                },
                "description": "Cryptocurrency assets mentioned in the article"
            },
            "valuation_metrics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "metric_type": {
                            "type": "string",
                            "enum": [
                                "pe_ratio",
                                "nvt_ratio",
                                "revenue_growth",
                                "user_growth",
                                "transaction_volume"
                            ],
                            "description": "Type of fundamental valuation metric"
                        },
                        "value": {
                            "type": "string",
                            "description": "Value of the metric as mentioned"
                        },
                        "comparison": {
                            "type": "string",
                            "description": "Comparative context (e.g., 'up 20% YoY', 'below industry average')"
                        }
                    },
                    "required": [
                        "metric_type"
                    ]
                },
                "description": "Fundamental valuation metrics mentioned"
            }
        },
        "description": "Fundamental market data and metrics"
    },
    "institutional_developments": {
        "type": "object",
        "properties": {
            "investments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "investor": {
                            "type": "string",
                            "description": "Name of institutional investor or VC firm"
                        },
                        "investment_target": {
                            "type": "string",
                            "description": "Project or company receiving investment"
                        },
                        "amount": {
                            "type": "string",
                            "description": "Investment amount"
                        },
                        "investment_stage": {
                            "type": "string",
                            "enum": [
                                "seed",
                                "series_a",
                                "series_b",
                                "series_c",
                                "strategic",
                                "other"
                            ],
                            "description": "Stage of investment"
                        }
                    },
                    "required": [
                        "investor",
                        "investment_target"
                    ]
                },
                "description": "Institutional investment activities mentioned"
            },
            "adoption_signals": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "entity": {
                            "type": "string",
                            "description": "Name of institution, corporation or government"
                        },
                        "adoption_type": {
                            "type": "string",
                            "enum": [
                                "treasury_allocation",
                                "payment_integration",
                                "infrastructure_development",
                                "research_initiative"
                            ],
                            "description": "Type of institutional adoption"
                        },
                        "details": {
                            "type": "string",
                            "description": "Specific details of the adoption"
                        }
                    },
                    "required": [
                        "entity",
                        "adoption_type"
                    ]
                },
                "description": "Institutional adoption signals"
            }
        },
        "description": "Institutional investment and adoption developments"
    },
    "regulatory_developments": {
        "type": "object",
        "properties": {
            "regulatory_events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "jurisdiction": {
                            "type": "string",
                            "description": "Country or regulatory body"
                        },
                        "regulation_type": {
                            "type": "string",
                            "enum": [
                                "legislation",
                                "enforcement",
                                "guidance",
                                "licensing",
                                "taxation"
                            ],
                            "description": "Type of regulatory action"
                        },
                        "impact": {
                            "type": "string",
                            "enum": [
                                "positive",
                                "negative",
                                "neutral",
                                "mixed"
                            ],
                            "description": "Assessed impact on the market"
                        },
                        "timeline": {
                            "type": "string",
                            "description": "Implementation timeline if mentioned"
                        },
                        "affected_sectors": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Sectors of crypto industry affected"
                        }
                    },
                    "required": [
                        "jurisdiction",
                        "regulation_type"
                    ]
                },
                "description": "Regulatory developments and their impacts"
            }
        },
        "description": "Regulatory and legal developments affecting the market"
    },
    "macroeconomic_factors": {
        "type": "object",
        "properties": {
            "economic_indicators": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "indicator": {
                            "type": "string",
                            "enum": [
                                "inflation",
                                "interest_rates",
                                "gdp_growth",
                                "monetary_policy",
                                "fiscal_policy",
                                "currency_devaluation"
                            ],
                            "description": "Type of economic indicator"
                        },
                        "region": {
                            "type": "string",
                            "description": "Geographic region affected"
                        },
                        "correlation": {
                            "type": "string",
                            "description": "Described correlation with crypto markets"
                        }
                    },
                    "required": [
                        "indicator"
                    ]
                },
                "description": "Macroeconomic indicators affecting crypto markets"
            }
        },
        "description": "Macroeconomic factors and their market correlations"
    },
    "technology_developments": {
        "type": "object",
        "properties": {
            "protocol_updates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Name of the blockchain or protocol"
                        },
                        "update_type": {
                            "type": "string",
                            "enum": [
                                "consensus_change",
                                "scaling_solution",
                                "security_enhancement",
                                "feature_addition",
                                "governance_change"
                            ],
                            "description": "Type of technical update"
                        },
                        "development_stage": {
                            "type": "string",
                            "enum": [
                                "research",
                                "testnet",
                                "audit",
                                "mainnet",
                                "post_implementation"
                            ],
                            "description": "Current stage of development"
                        },
                        "expected_impact": {
                            "type": "string",
                            "description": "Expected impact on performance, security, or adoption"
                        }
                    },
                    "required": [
                        "project",
                        "update_type"
                    ]
                },
                "description": "Technical developments and protocol updates"
            },
            "interoperability_developments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "protocols_involved": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Protocols or blockchains involved in interoperability"
                        },
                        "integration_type": {
                            "type": "string",
                            "enum": [
                                "bridge",
                                "cross_chain_messaging",
                                "shared_security",
                                "asset_wrapping"
                            ],
                            "description": "Type of interoperability solution"
                        },
                        "maturity": {
                            "type": "string",
                            "enum": [
                                "concept",
                                "development",
                                "testnet",
                                "mainnet",
                                "production"
                            ],
                            "description": "Maturity level of the integration"
                        }
                    },
                    "required": [
                        "protocols_involved"
                    ]
                },
                "description": "Cross-chain and interoperability developments"
            }
        },
        "description": "Technical developments and innovations"
    },
    "analysis_metadata": {
        "type": "object",
        "properties": {
            "extraction_timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "When this data was extracted"
            },
            "confidence_level": {
                "type": "string",
                "enum": [
                    "high",
                    "medium",
                    "low"
                ],
                "description": "Overall confidence in extraction accuracy"
            },
            "key_insights": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Summary of key insights from the article"
            }
        },
        "required": [
            "extraction_timestamp",
            "confidence_level"
        ],
        "description": "Metadata about the extraction process"
    }
}
        
        # Define the instruction for the LLM
        # type: ignore
        instruction = """Professional Cryptocurrency Market Intelligence Extractor

You are a professional-grade cryptocurrency market analyst. Your task is to extract high-value intelligence from financial news articles, research reports, and industry publications.

Analyze the content methodically and extract the following information:

Extract the publication source, author, and publication date
Identify all cryptocurrency assets mentioned with their full names and tickers
Extract fundamental market metrics (market cap, trading volume, TVL) for mentioned assets
Identify institutional investment activities (investors, targets, amounts, stages)
Extract regulatory developments across jurisdictions with impact assessments
Identify macroeconomic factors correlated with crypto markets
Extract technical protocol updates and development milestones
Assess interoperability developments between blockchains
Identify valuation metrics mentioned (P/E ratios, NVT ratios, revenue growth)
Extract institutional adoption signals (treasury allocations, payment integrations)
Determine the credibility of the source on a scale from 0 to 1
Summarize key insights from the article

Provide your extraction in a structured JSON format according to the provided schema.

Focus exclusively on factual information from credible sources. Ignore speculative price predictions, social media sentiment, and unverified rumors.

For institutional developments, include specific details about investment amounts, stages, and strategic rationales when available.

For regulatory developments, note specific jurisdictions, implementation timelines, and potential market impacts across different sectors.

For technical developments, extract concrete information about development stages, expected performance improvements, and security enhancements.

Prioritize information that impacts long-term fundamental value rather than short-term price movements."""
        
        # Initialize the base class with the schema and instruction
        super().__init__(
            provider=provider,
            api_token=api_token,
            instruction=instruction,
            schema=cryptoinvestor_schema,
            base_url=base_url,
            model=model,
            extra_args=extra_args,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs
        )