"""Services package for CRY-A-4MCP.

This package contains all service classes and business logic components,
including adaptive crawling services, data processing services, and integration services.
"""

from .adaptive_strategy_service import AdaptiveStrategyService

__all__ = [
    "AdaptiveStrategyService"
]