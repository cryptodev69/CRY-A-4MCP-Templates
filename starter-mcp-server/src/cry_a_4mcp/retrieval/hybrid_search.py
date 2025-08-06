"""
Hybrid Search Engine for CRY-A-4MCP.

This module implements a hybrid search approach combining vector similarity search
with knowledge graph traversal for comprehensive cryptocurrency analysis.
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import structlog

from ..config import Settings
from ..storage.vector_store import VectorStore
from ..storage.graph_store import GraphStore


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
    """Hybrid search engine combining vector search and knowledge graph traversal."""
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the hybrid search engine."""
        self.settings = settings
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.vector_store: Optional[VectorStore] = None
        self.graph_store: Optional[GraphStore] = None
        self.entity_extractor = None
    
    async def initialize(self) -> None:
        """Initialize the search engine components."""
        self.logger.info("Initializing hybrid search engine")
        
        # Initialize vector store
        self.vector_store = VectorStore(self.settings)
        await self.vector_store.initialize()
        
        # Initialize graph store
        self.graph_store = GraphStore(self.settings)
        await self.graph_store.initialize()
        
        self.logger.info("Hybrid search engine initialized")
    
    async def search(self, query: str, mode: str = "auto", max_results: int = 10, 
                    confidence_threshold: float = 0.7) -> List[SearchResult]:
        """Perform hybrid search.
        
        Args:
            query: Search query
            mode: Search mode (hybrid, vector_only, graph_only, auto)
            max_results: Maximum number of results to return
            confidence_threshold: Minimum confidence score for results
            
        Returns:
            List of search results
        """
        self.logger.info("Performing hybrid search", query=query, mode=mode)
        
        # Validate search mode
        search_mode = SearchMode(mode)
        
        # Determine search strategy
        if search_mode == SearchMode.AUTO:
            search_mode = self._determine_search_mode(query)
        
        # Execute search based on mode
        if search_mode == SearchMode.HYBRID:
            results = await self._hybrid_search(query, max_results, confidence_threshold)
        elif search_mode == SearchMode.VECTOR_ONLY:
            results = await self._vector_search(query, max_results, confidence_threshold)
        elif search_mode == SearchMode.GRAPH_ONLY:
            results = await self._graph_search(query, max_results, confidence_threshold)
        else:
            raise ValueError(f"Invalid search mode: {search_mode}")
        
        # Sort results by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        # Apply confidence threshold
        results = [r for r in results if r.confidence >= confidence_threshold]
        
        # Limit results
        results = results[:max_results]
        
        self.logger.info("Hybrid search completed", results_count=len(results))
        
        return results
    
    def _determine_search_mode(self, query: str) -> SearchMode:
        """Determine the best search mode for the query.
        
        This method analyzes the query to determine whether it's better suited
        for vector search, graph search, or a hybrid approach.
        
        Args:
            query: Search query
            
        Returns:
            Recommended search mode
        """
        # Simple heuristic for now - can be improved with ML-based classification
        factual_keywords = ["price", "market cap", "volume", "exchange", "listing", 
                           "founder", "launched", "created", "when", "who", "where"]
        
        # Check for factual query indicators
        if any(keyword in query.lower() for keyword in factual_keywords):
            return SearchMode.GRAPH_ONLY
        
        # Check for complex query indicators
        if len(query.split()) > 5:
            return SearchMode.HYBRID
        
        # Default to vector search for simple queries
        return SearchMode.VECTOR_ONLY
    
    async def _vector_search(self, query: str, max_results: int, 
                           confidence_threshold: float) -> List[SearchResult]:
        """Perform vector similarity search.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            confidence_threshold: Minimum confidence score
            
        Returns:
            List of search results
        """
        if not self.vector_store:
            raise RuntimeError("Vector store not initialized")
        
        # Get vector search results
        vector_results = await self.vector_store.search(query, limit=max_results)
        
        # Convert to SearchResult objects
        results = []
        for result in vector_results:
            search_result = SearchResult(
                content=result["content"],
                confidence=result["score"],
                source_type="vector",
                sources=[{"url": result.get("url"), "title": result.get("title")}],
                reasoning_path=None
            )
            results.append(search_result)
        
        return results
    
    async def _graph_search(self, query: str, max_results: int, 
                          confidence_threshold: float) -> List[SearchResult]:
        """Perform knowledge graph search.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            confidence_threshold: Minimum confidence score
            
        Returns:
            List of search results
        """
        if not self.graph_store:
            raise RuntimeError("Graph store not initialized")
        
        # Extract entities from query
        entities = await self._extract_entities(query)
        
        # Get graph search results
        graph_results = await self.graph_store.search(entities, limit=max_results)
        
        # Convert to SearchResult objects
        results = []
        for result in graph_results:
            search_result = SearchResult(
                content=result["content"],
                confidence=result["score"],
                source_type="graph",
                sources=[{"entity": e} for e in result.get("entities", [])],
                reasoning_path=result.get("path")
            )
            results.append(search_result)
        
        return results
    
    async def _hybrid_search(self, query: str, max_results: int, 
                           confidence_threshold: float) -> List[SearchResult]:
        """Perform hybrid search combining vector and graph approaches.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            confidence_threshold: Minimum confidence score
            
        Returns:
            List of search results
        """
        # Run both search methods concurrently
        vector_task = asyncio.create_task(
            self._vector_search(query, max_results, confidence_threshold)
        )
        graph_task = asyncio.create_task(
            self._graph_search(query, max_results, confidence_threshold)
        )
        
        # Wait for both to complete
        vector_results, graph_results = await asyncio.gather(vector_task, graph_task)
        
        # Combine results
        combined_results = self._merge_results(vector_results, graph_results, max_results)
        
        return combined_results
    
    def _merge_results(self, vector_results: List[SearchResult], 
                      graph_results: List[SearchResult], 
                      max_results: int) -> List[SearchResult]:
        """Merge and deduplicate results from vector and graph search.
        
        Args:
            vector_results: Results from vector search
            graph_results: Results from graph search
            max_results: Maximum number of results
            
        Returns:
            Merged and deduplicated results
        """
        # Simple interleaving strategy - can be improved with more sophisticated ranking
        merged = []
        seen_content = set()
        
        # Interleave results, starting with highest confidence from each source
        vector_idx, graph_idx = 0, 0
        while len(merged) < max_results and (vector_idx < len(vector_results) or graph_idx < len(graph_results)):
            # Add vector result if available and not seen
            if vector_idx < len(vector_results):
                result = vector_results[vector_idx]
                if result.content not in seen_content:
                    merged.append(result)
                    seen_content.add(result.content)
                vector_idx += 1
            
            # Add graph result if available and not seen
            if graph_idx < len(graph_results) and len(merged) < max_results:
                result = graph_results[graph_idx]
                if result.content not in seen_content:
                    merged.append(result)
                    seen_content.add(result.content)
                graph_idx += 1
        
        # Sort by confidence
        merged.sort(key=lambda x: x.confidence, reverse=True)
        
        return merged
    
    async def _extract_entities(self, query: str) -> List[str]:
        """Extract cryptocurrency entities from query.
        
        Args:
            query: Search query
            
        Returns:
            List of extracted entities
        """
        # Simple extraction based on common crypto terms
        # In a real implementation, this would use a more sophisticated NER model
        common_cryptos = {
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "binance": "BNB",
            "cardano": "ADA",
            "solana": "SOL",
            "ripple": "XRP",
            "dogecoin": "DOGE",
            "polkadot": "DOT",
            "litecoin": "LTC",
            "chainlink": "LINK"
        }
        
        entities = []
        query_lower = query.lower()
        
        # Extract crypto names
        for name, symbol in common_cryptos.items():
            if name in query_lower or symbol.lower() in query_lower:
                entities.append(symbol)
        
        return entities