#!/usr/bin/env python3
"""
Extraction strategies package for the cry_a_4mcp.crawl4ai module.

This package provides a framework for extracting structured information from web content
using various strategies, including LLM-based extraction.
"""

# Import the base strategy classes
from .base import ExtractionStrategy, LLMExtractionStrategy

# Import the registry and factory components
from .registry import StrategyRegistry, register_strategy
from .factory import StrategyFactory, CompositeExtractionStrategy

# Import factory extension to add create_strategy method
from . import factory_extension

# Import domain-specific strategies
from .crypto.crypto_llm import CryptoLLMExtractionStrategy
from .crypto.xcryptohunter_llm import XCryptoHunterLLMExtractionStrategy
from .nft.nft_llm import NFTLLMExtractionStrategy
from .financial.financial_llm import FinancialLLMExtractionStrategy
from .academic.academic_llm import AcademicLLMExtractionStrategy
from .news.news_llm import NewsLLMExtractionStrategy
from .product.product_llm import ProductLLMExtractionStrategy
from .social.social_llm import SocialMediaLLMExtractionStrategy

# Define package exports
__all__ = [
    'ExtractionStrategy',
    'LLMExtractionStrategy',
    'StrategyRegistry',
    'register_strategy',
    'StrategyFactory',
    'CompositeExtractionStrategy',
    'CryptoLLMExtractionStrategy',
    'XCryptoHunterLLMExtractionStrategy',
    'NFTLLMExtractionStrategy',
    'FinancialLLMExtractionStrategy',
    'AcademicLLMExtractionStrategy',
    'NewsLLMExtractionStrategy',
    'ProductLLMExtractionStrategy',
    'SocialMediaLLMExtractionStrategy',
]

# Register built-in strategies
register_strategy(
    name="LLMExtractionStrategy",
    description="Base LLM extraction strategy for general content",
    category="general"
)(LLMExtractionStrategy)

register_strategy(
    name="CryptoLLMExtractionStrategy",
    description="Specialized extraction strategy for cryptocurrency content",
    category="crypto"
)(CryptoLLMExtractionStrategy)

register_strategy(
    name="NFTLLMExtractionStrategy",
    description="Specialized extraction strategy for NFT content",
    category="nft"
)(NFTLLMExtractionStrategy)

register_strategy(
    name="XCryptoHunterLLMExtractionStrategy",
    description="Specialized extraction strategy for cryptocurrency gem hunters",
    category="crypto"
)(XCryptoHunterLLMExtractionStrategy)

register_strategy(
    name="FinancialLLMExtractionStrategy",
    description="Specialized extraction strategy for financial content",
    category="financial"
)(FinancialLLMExtractionStrategy)

register_strategy(
    name="AcademicLLMExtractionStrategy",
    description="Specialized extraction strategy for academic content",
    category="academic"
)(AcademicLLMExtractionStrategy)

register_strategy(
    name="NewsLLMExtractionStrategy",
    description="Specialized extraction strategy for news content",
    category="news"
)(NewsLLMExtractionStrategy)

register_strategy(
    name="ProductLLMExtractionStrategy",
    description="Specialized extraction strategy for product content",
    category="product"
)(ProductLLMExtractionStrategy)

register_strategy(
    name="SocialMediaLLMExtractionStrategy",
    description="Specialized extraction strategy for social media content",
    category="social"
)(SocialMediaLLMExtractionStrategy)