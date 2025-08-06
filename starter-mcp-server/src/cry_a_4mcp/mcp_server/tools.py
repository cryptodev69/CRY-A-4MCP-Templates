"""
MCP Tools implementation for CRY-A-4MCP server.

This module contains all the cryptocurrency analysis tools that implement
the hybrid RAG+Knowledge Graph approach using Crawl4AI as the foundation.
"""

import json
from typing import Any, Dict, List, Optional

from ..crawl4ai.crawler import CryptoCrawler
from ..retrieval.hybrid_search import HybridSearchEngine
from ..processing.crypto_analyzer import CryptoAnalyzer
from ..storage.knowledge_graph_manager import KnowledgeGraphManager
from .base_tool import BaseTool


class CrawlWebsiteTool(BaseTool):
    """
    Tool for crawling cryptocurrency websites using Crawl4AI.
    
    This tool provides intelligent web crawling with cryptocurrency-specific
    content extraction and dual-output generation (markdown + triples).
    """
    
    def __init__(self, settings) -> None:
        super().__init__(settings)
        self.crawler: Optional[CryptoCrawler] = None
    
    @property
    def name(self) -> str:
        return "crawl_website"
    
    @property
    def description(self) -> str:
        return (
            "Crawl cryptocurrency websites using Crawl4AI with domain-specific "
            "content extraction. Generates both markdown for embeddings and "
            "entity-relation triples for knowledge graphs."
        )
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL of the cryptocurrency website to crawl",
                    "format": "uri"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["news", "exchange", "analytics", "social", "documentation"],
                    "description": "Type of content expected on the website"
                },
                "extract_entities": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to extract cryptocurrency entities"
                },
                "generate_triples": {
                    "type": "boolean", 
                    "default": True,
                    "description": "Whether to generate knowledge graph triples"
                }
            },
            "required": ["url", "content_type"]
        }
    
    async def _initialize_impl(self) -> None:
        """Initialize the Crawl4AI crawler."""
        self.crawler = CryptoCrawler(self.settings)
        await self.crawler.initialize()
    
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute website crawling."""
        url = arguments["url"]
        content_type = arguments["content_type"]
        extract_entities = arguments.get("extract_entities", True)
        generate_triples = arguments.get("generate_triples", True)
        
        if not self.crawler:
            raise RuntimeError("Crawler not initialized")
        
        # Crawl the website
        result = await self.crawler.crawl_crypto_website(
            url=url,
            content_type=content_type,
            extract_entities=extract_entities,
            generate_triples=generate_triples,
        )
        
        # Convert Pydantic models to dictionaries for JSON serialization
        entities_dict = []
        for entity in result.entities:
            entities_dict.append({
                "name": entity.name,
                "entity_type": entity.entity_type,
                "symbol": entity.symbol,
                "address": entity.address,
                "network": entity.network,
                "confidence": entity.confidence,
                "context": entity.context,
                "properties": entity.properties
            })
        
        triples_dict = []
        for triple in result.triples:
            triples_dict.append({
                "subject": triple.subject,
                "predicate": triple.predicate,
                "object": triple.object,
                "confidence": triple.confidence,
                "source": triple.source,
                "timestamp": triple.timestamp.isoformat(),
                "properties": triple.properties
            })
        
        metadata_dict = {
            "url": result.metadata.url,
            "content_type": result.metadata.content_type,
            "content_length": result.metadata.content_length,
            "processing_time": result.metadata.processing_time,
            "success": result.metadata.success,
            "text_quality_score": result.metadata.text_quality_score,
            "entity_density": result.metadata.entity_density,
            "relationship_density": result.metadata.relationship_density,
            "language": result.metadata.language,
            "has_structured_data": result.metadata.has_structured_data,
            "has_tables": result.metadata.has_tables,
            "has_charts": result.metadata.has_charts
        }
        
        return {
            "success": True,
            "url": url,
            "content_type": content_type,
            "markdown": result.markdown,
            "entities": entities_dict,
            "triples": triples_dict,
            "metadata": metadata_dict,
            "quality_score": result.quality_score,
        }


class HybridSearchTool(BaseTool):
    """
    Tool for hybrid search combining vector search and knowledge graph traversal.
    
    This tool implements the core hybrid retrieval approach, intelligently
    routing queries between RAG and Knowledge Graph systems.
    """
    
    def __init__(self, settings) -> None:
        super().__init__(settings)
        self.search_engine: Optional[HybridSearchEngine] = None
    
    @property
    def name(self) -> str:
        return "hybrid_search"
    
    @property
    def description(self) -> str:
        return (
            "Perform hybrid search combining vector similarity search (RAG) "
            "with knowledge graph traversal for comprehensive cryptocurrency analysis."
        )
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for cryptocurrency information"
                },
                "search_mode": {
                    "type": "string",
                    "enum": ["hybrid", "vector_only", "graph_only", "auto"],
                    "default": "auto",
                    "description": "Search mode to use"
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                    "description": "Maximum number of results to return"
                },
                "include_sources": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to include source attribution"
                },
                "confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.7,
                    "description": "Minimum confidence score for results"
                }
            },
            "required": ["query"]
        }
    
    async def _initialize_impl(self) -> None:
        """Initialize the hybrid search engine."""
        self.search_engine = HybridSearchEngine(self.settings)
        await self.search_engine.initialize()
    
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hybrid search."""
        query = arguments["query"]
        search_mode = arguments.get("search_mode", "auto")
        max_results = arguments.get("max_results", 10)
        include_sources = arguments.get("include_sources", True)
        confidence_threshold = arguments.get("confidence_threshold", 0.7)
        
        if not self.search_engine:
            raise RuntimeError("Search engine not initialized")
        
        # Perform hybrid search
        results = await self.search_engine.search(
            query=query,
            mode=search_mode,
            max_results=max_results,
            confidence_threshold=confidence_threshold,
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_result = {
                "content": result.content,
                "confidence": result.confidence,
                "source_type": result.source_type,
            }
            
            if include_sources:
                formatted_result["sources"] = result.sources
                formatted_result["reasoning_path"] = result.reasoning_path
            
            formatted_results.append(formatted_result)
        
        return {
            "success": True,
            "query": query,
            "search_mode": search_mode,
            "results_count": len(formatted_results),
            "results": formatted_results,
        }


class AnalyzeCryptoTool(BaseTool):
    """
    Tool for comprehensive cryptocurrency analysis.
    
    This tool provides high-level cryptocurrency analysis combining
    market data, news sentiment, and technical indicators.
    """
    
    def __init__(self, settings) -> None:
        super().__init__(settings)
        self.analyzer: Optional[CryptoAnalyzer] = None
    
    @property
    def name(self) -> str:
        return "analyze_crypto"
    
    @property
    def description(self) -> str:
        return (
            "Perform comprehensive cryptocurrency analysis including market data, "
            "news sentiment, technical indicators, and risk assessment."
        )
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Cryptocurrency symbol (e.g., BTC, ETH)",
                    "pattern": "^[A-Z]{2,10}$"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["comprehensive", "technical", "fundamental", "sentiment"],
                    "default": "comprehensive",
                    "description": "Type of analysis to perform"
                },
                "timeframe": {
                    "type": "string",
                    "enum": ["1h", "4h", "1d", "1w", "1m"],
                    "default": "1d",
                    "description": "Analysis timeframe"
                },
                "include_predictions": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to include price predictions"
                }
            },
            "required": ["symbol"]
        }
    
    async def _initialize_impl(self) -> None:
        """Initialize the crypto analyzer."""
        self.analyzer = CryptoAnalyzer(self.settings)
        await self.analyzer.initialize()
    
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cryptocurrency analysis."""
        symbol = arguments["symbol"].upper()
        analysis_type = arguments.get("analysis_type", "comprehensive")
        timeframe = arguments.get("timeframe", "1d")
        include_predictions = arguments.get("include_predictions", False)
        
        if not self.analyzer:
            raise RuntimeError("Analyzer not initialized")
        
        # Perform analysis
        analysis = await self.analyzer.analyze(
            symbol=symbol,
            analysis_type=analysis_type,
            timeframe=timeframe,
            include_predictions=include_predictions,
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "analysis_type": analysis_type,
            "timeframe": timeframe,
            "timestamp": analysis.timestamp,
            "market_data": analysis.market_data,
            "technical_indicators": analysis.technical_indicators,
            "sentiment_analysis": analysis.sentiment_analysis,
            "risk_assessment": analysis.risk_assessment,
            "predictions": analysis.predictions if include_predictions else None,
            "confidence": analysis.confidence,
        }


class UpdateKnowledgeGraphTool(BaseTool):
    """
    Tool for updating the knowledge graph with new information.
    
    This tool manages the knowledge graph updates from crawled content
    and maintains entity relationships.
    """
    
    def __init__(self, settings) -> None:
        super().__init__(settings)
        self.kg_manager: Optional[KnowledgeGraphManager] = None
    
    @property
    def name(self) -> str:
        return "update_knowledge_graph"
    
    @property
    def description(self) -> str:
        return (
            "Update the knowledge graph with new cryptocurrency entities "
            "and relationships from crawled content."
        )
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "properties": {"type": "object"}
                        },
                        "required": ["name", "type"]
                    },
                    "description": "List of entities to add/update"
                },
                "relationships": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "target": {"type": "string"},
                            "type": {"type": "string"},
                            "properties": {"type": "object"}
                        },
                        "required": ["source", "target", "type"]
                    },
                    "description": "List of relationships to add/update"
                },
                "source_url": {
                    "type": "string",
                    "description": "Source URL for provenance tracking"
                },
                "update_mode": {
                    "type": "string",
                    "enum": ["merge", "replace", "append"],
                    "default": "merge",
                    "description": "How to handle existing data"
                }
            },
            "required": ["entities"]
        }
    
    async def _initialize_impl(self) -> None:
        """Initialize the knowledge graph manager."""
        self.kg_manager = KnowledgeGraphManager(self.settings)
        await self.kg_manager.initialize()
    
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute knowledge graph update."""
        entities = arguments["entities"]
        relationships = arguments.get("relationships", [])
        source_url = arguments.get("source_url")
        update_mode = arguments.get("update_mode", "merge")
        
        if not self.kg_manager:
            raise RuntimeError("Knowledge graph manager not initialized")
        
        # Update knowledge graph
        result = await self.kg_manager.update(
            entities=entities,
            relationships=relationships,
            source_url=source_url,
            mode=update_mode,
        )
        
        return {
            "success": True,
            "entities_added": result.entities_added,
            "entities_updated": result.entities_updated,
            "relationships_added": result.relationships_added,
            "relationships_updated": result.relationships_updated,
            "source_url": source_url,
            "update_mode": update_mode,
        }

