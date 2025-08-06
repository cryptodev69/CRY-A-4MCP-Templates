"""Composite extraction strategies.

This package contains composite extraction strategies that combine multiple
domain-specific strategies to extract information from content that may span
multiple domains.
"""

from .comprehensive_llm import ComprehensiveLLMExtractionStrategy

__all__ = ["ComprehensiveLLMExtractionStrategy"]