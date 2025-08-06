"""Sentiment Analysis Tool for CRY-A-4MCP.

This module provides an MCP tool for sentiment analysis of cryptocurrency
news and social media content.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union

import structlog

from ...config import Settings
from ...processing.sentiment_analyzer import (
    AggregatedSentiment,
    ContentSource,
    SentimentAnalyzer,
    SentimentResult,
    TimeFrame,
)
from ..base_tool import BaseTool


class SentimentAnalysisTool(BaseTool):
    """MCP tool for cryptocurrency sentiment analysis.
    
    This tool provides sentiment analysis capabilities for cryptocurrency
    news and social media content, supporting both real-time and historical
    sentiment queries.
    """
    
    name = "sentiment_analysis"
    description = "Analyze sentiment for cryptocurrency entities and topics from news and social media"
    
    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Cryptocurrency entity (e.g., 'Bitcoin', 'ETH') or topic to analyze"
            },
            "analysis_type": {
                "type": "string",
                "enum": ["entity", "topic", "text"],
                "description": "Type of analysis to perform: 'entity' for specific cryptocurrency, 'topic' for general query, 'text' for direct text analysis",
                "default": "entity"
            },
            "timeframe": {
                "type": "string",
                "enum": ["1h", "6h", "12h", "24h", "3d", "7d", "30d"],
                "description": "Time frame for historical sentiment analysis",
                "default": "24h"
            },
            "sources": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["news", "twitter", "reddit", "discord", "all"]
                },
                "description": "Content sources to include in analysis",
                "default": ["news", "twitter", "reddit"]
            },
            "text": {
                "type": "string",
                "description": "Text to analyze directly (only used when analysis_type is 'text')"
            },
            "include_trend": {
                "type": "boolean",
                "description": "Whether to include sentiment trend data in the response",
                "default": True
            },
            "include_sources_breakdown": {
                "type": "boolean",
                "description": "Whether to include breakdown by source in the response",
                "default": True
            }
        },
        "required": ["query"]
    }
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the sentiment analysis tool."""
        super().__init__(settings)
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.analyzer = SentimentAnalyzer(settings)
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize the sentiment analyzer."""
        if not self.initialized:
            await self.analyzer.initialize()
            self.initialized = True
    
    async def _run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run the sentiment analysis tool.
        
        Args:
            params: Tool parameters
            
        Returns:
            Sentiment analysis results
        """
        await self.initialize()
        
        # Extract parameters
        query = params.get("query")
        analysis_type = params.get("analysis_type", "entity")
        timeframe_str = params.get("timeframe", "24h")
        sources_str = params.get("sources", ["news", "twitter", "reddit"])
        text = params.get("text")
        include_trend = params.get("include_trend", True)
        include_sources_breakdown = params.get("include_sources_breakdown", True)
        
        # Convert timeframe string to enum
        timeframe = TimeFrame(timeframe_str)
        
        # Convert sources to enum
        sources = []
        if "all" in sources_str:
            sources = [ContentSource.ALL]
        else:
            for source in sources_str:
                sources.append(ContentSource(source))
        
        # Perform analysis based on type
        if analysis_type == "text" and text:
            # Direct text analysis
            result = await self.analyzer.analyze_text(text)
            return self._format_text_result(result)
        
        elif analysis_type == "entity":
            # Entity-specific sentiment
            result = await self.analyzer.get_entity_sentiment(query, timeframe, sources)
            return self._format_aggregated_result(result, include_trend, include_sources_breakdown)
        
        else:  # topic
            # General topic sentiment
            result = await self.analyzer.query_sentiment(query, timeframe, sources)
            return self._format_aggregated_result(result, include_trend, include_sources_breakdown)
    
    def _format_text_result(self, result: SentimentResult) -> Dict[str, Any]:
        """Format a single text sentiment result for API response.
        
        Args:
            result: Sentiment result to format
            
        Returns:
            Formatted result
        """
        return {
            "sentiment": {
                "score": result.score,
                "confidence": result.confidence,
                "label": self._score_to_label(result.score),
                "source": result.source.value,
                "entity": result.entity,
                "timestamp": result.timestamp.isoformat(),
                "metadata": result.metadata
            }
        }
    
    def _format_aggregated_result(self, result: AggregatedSentiment, 
                                include_trend: bool = True,
                                include_sources_breakdown: bool = True) -> Dict[str, Any]:
        """Format an aggregated sentiment result for API response.
        
        Args:
            result: Aggregated sentiment result to format
            include_trend: Whether to include trend data
            include_sources_breakdown: Whether to include source breakdown
            
        Returns:
            Formatted result
        """
        response = {
            "sentiment": {
                "query": result.query,
                "entity": result.entity,
                "overall_score": result.overall_score,
                "label": self._score_to_label(result.overall_score),
                "counts": {
                    "positive": result.positive_count,
                    "negative": result.negative_count,
                    "neutral": result.neutral_count,
                    "total": result.positive_count + result.negative_count + result.neutral_count
                },
                "timeframe": result.timeframe.value,
                "timestamp": result.timestamp.isoformat()
            }
        }
        
        # Add sources breakdown if requested
        if include_sources_breakdown:
            response["sentiment"]["sources"] = {}
            for source, count in result.sources.items():
                response["sentiment"]["sources"][source.value] = count
        
        # Add trend data if requested
        if include_trend and result.sentiment_trend:
            response["sentiment"]["trend"] = [
                {"timestamp": dt.isoformat(), "score": score}
                for dt, score in result.sentiment_trend
            ]
        
        return response
    
    def _score_to_label(self, score: float) -> str:
        """Convert a sentiment score to a human-readable label.
        
        Args:
            score: Sentiment score (-1.0 to 1.0)
            
        Returns:
            Sentiment label
        """
        if score >= 0.5:
            return "very positive"
        elif score >= 0.1:
            return "positive"
        elif score > -0.1:
            return "neutral"
        elif score > -0.5:
            return "negative"
        else:
            return "very negative"