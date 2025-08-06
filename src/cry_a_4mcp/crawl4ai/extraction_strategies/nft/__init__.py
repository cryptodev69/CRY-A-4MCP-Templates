#!/usr/bin/env python3
"""
NFT-specific extraction strategies for the cry_a_4mcp.crawl4ai package.

This module provides specialized extraction strategies for NFT content,
with detailed schemas for extracting relevant information from NFT news articles.
"""

from .nft_llm import NFTLLMExtractionStrategy

__all__ = ['NFTLLMExtractionStrategy']