import sys
import os
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Define the same classes as in the original file but without dependencies
class SearchMode(str, Enum):
    """Search mode for hybrid search."""
    HYBRID = "hybrid"
    VECTOR_ONLY = "vector_only"
    GRAPH_ONLY = "graph_only"
    AUTO = "auto"


@dataclass
class SearchResult:
    """Result from hybrid search."""
    content: str
    confidence: float
    source_type: str
    sources: List[Dict[str, Any]]
    reasoning_path: Optional[List[str]] = None


class HybridSearchEngine:
    """Simplified hybrid search engine for testing."""
    
    def __init__(self, settings=None) -> None:
        """Initialize the hybrid search engine."""
        self.settings = settings
        self.vector_store = None
        self.graph_store = None
        self.entity_extractor = None


# Test the classes
print("Successfully defined HybridSearchEngine")
print(f"SearchMode: {SearchMode.__members__}")
print(f"SearchResult fields: {SearchResult.__annotations__}")

# Create a SearchResult instance to verify the constructor
result = SearchResult(
    content="Test content",
    confidence=0.95,
    source_type="document",
    sources=[{"name": "test_source"}],
    reasoning_path=["Test path"]
)

print("\nCreated SearchResult instance:")
print(f"  content: {result.content}")
print(f"  confidence: {result.confidence}")
print(f"  source_type: {result.source_type}")
print(f"  sources: {result.sources}")
print(f"  reasoning_path: {result.reasoning_path}")

# Create a mock settings object
class MockSettings:
    def __init__(self):
        pass

# Create a HybridSearchEngine instance
engine = HybridSearchEngine(settings=MockSettings())

# Set mock values for testing
engine.vector_store = "mock_vector_store"
engine.graph_store = "mock_graph_store"
engine.entity_extractor = "mock_entity_extractor"

print("\nCreated HybridSearchEngine instance:")
print(f"  settings: {engine.settings}")
print(f"  vector_store: {engine.vector_store}")
print(f"  graph_store: {engine.graph_store}")
print(f"  entity_extractor: {engine.entity_extractor}")