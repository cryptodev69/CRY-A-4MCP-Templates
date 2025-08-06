"""Sentiment analyzer for CRY-A-4MCP.

This module provides sentiment analysis capabilities for cryptocurrency
news and social media content using FinBERT model.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import structlog

from ..config import Settings


class ContentSource(str, Enum):
    """Source of content for sentiment analysis."""
    NEWS = "news"
    TWITTER = "twitter"
    REDDIT = "reddit"
    DISCORD = "discord"
    ALL = "all"


class TimeFrame(str, Enum):
    """Time frame for sentiment analysis."""
    HOUR_1 = "1h"
    HOUR_6 = "6h"
    HOUR_12 = "12h"
    DAY_1 = "24h"
    DAY_3 = "3d"
    WEEK_1 = "7d"
    MONTH_1 = "30d"


@dataclass
class SentimentResult:
    """Result of sentiment analysis for a single piece of content."""
    text: str
    score: float  # -1.0 to 1.0 (negative to positive)
    confidence: float  # 0.0 to 1.0
    source: ContentSource
    entity: Optional[str] = None  # Cryptocurrency entity (e.g., "Bitcoin", "ETH")
    timestamp: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AggregatedSentiment:
    """Aggregated sentiment for a specific entity or query."""
    query: str
    overall_score: float  # -1.0 to 1.0
    positive_count: int
    negative_count: int
    neutral_count: int
    sources: Dict[ContentSource, int]  # Count by source
    timeframe: TimeFrame
    entity: Optional[str] = None
    sentiment_trend: Optional[List[Tuple[datetime, float]]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.sentiment_trend is None:
            self.sentiment_trend = []


class SentimentAnalyzer:
    """Sentiment analyzer for cryptocurrency content."""
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the sentiment analyzer."""
        self.settings = settings
        self.logger = structlog.get_logger(self.__class__.__name__)
        
        # Common cryptocurrency mapping for entity normalization
        self.crypto_entities = {
            "BTC": "Bitcoin",
            "bitcoin": "Bitcoin",
            "btc": "Bitcoin",
            "ETH": "Ethereum",
            "ethereum": "Ethereum",
            "eth": "Ethereum",
            "BNB": "Binance Coin",
            "binance coin": "Binance Coin",
            "bnb": "Binance Coin",
            "ADA": "Cardano",
            "cardano": "Cardano",
            "ada": "Cardano",
            "SOL": "Solana",
            "solana": "Solana",
            "sol": "Solana",
            "XRP": "Ripple",
            "ripple": "Ripple",
            "xrp": "Ripple",
            "DOGE": "Dogecoin",
            "dogecoin": "Dogecoin",
            "doge": "Dogecoin",
        }
        
        # FinBERT model will be loaded during initialization
        self.model = None
    
    async def initialize(self) -> None:
        """Initialize the sentiment analyzer."""
        self.logger.info("Initializing sentiment analyzer")
        # In a real implementation, this would load the FinBERT model
        # For now, we'll simulate model loading
        await asyncio.sleep(0.5)  # Simulate model loading time
        self.logger.info("Sentiment analyzer initialized")
    
    async def analyze_text(self, text: str, source: ContentSource = ContentSource.NEWS) -> SentimentResult:
        """Analyze sentiment of a single text.
        
        Args:
            text: Text to analyze
            source: Source of the content
            
        Returns:
            Sentiment analysis result
        """
        self.logger.debug("Analyzing text sentiment", text_length=len(text), source=source)
        
        # In a real implementation, this would use the FinBERT model
        # For now, generate mock sentiment based on simple heuristics
        
        # Extract potential entity
        entity = self._extract_entity(text)
        
        # Simple sentiment heuristics
        positive_words = ["bullish", "surge", "gain", "rise", "up", "high", "growth", "profit", "success"]
        negative_words = ["bearish", "crash", "drop", "fall", "down", "low", "loss", "fail", "risk"]
        
        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())
        
        # Calculate mock sentiment score (-1.0 to 1.0)
        if positive_count > negative_count:
            score = min(0.5 + (positive_count - negative_count) * 0.1, 1.0)
            confidence = 0.5 + (positive_count / (len(text.split()) + 1)) * 0.5
        elif negative_count > positive_count:
            score = max(-0.5 - (negative_count - positive_count) * 0.1, -1.0)
            confidence = 0.5 + (negative_count / (len(text.split()) + 1)) * 0.5
        else:
            score = 0.0
            confidence = 0.5
        
        return SentimentResult(
            text=text,
            score=score,
            confidence=confidence,
            source=source,
            entity=entity,
            timestamp=datetime.now(),
            metadata={"word_count": len(text.split())}
        )
    
    async def analyze_batch(self, texts: List[str], source: ContentSource = ContentSource.NEWS) -> List[SentimentResult]:
        """Analyze sentiment of multiple texts in batch.
        
        Args:
            texts: List of texts to analyze
            source: Source of the content
            
        Returns:
            List of sentiment analysis results
        """
        self.logger.info("Analyzing batch sentiment", count=len(texts), source=source)
        
        # In a real implementation, this would batch process through the model
        # For now, process each text individually
        tasks = [self.analyze_text(text, source) for text in texts]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def get_entity_sentiment(self, entity: str, timeframe: TimeFrame = TimeFrame.DAY_1, 
                                 sources: List[ContentSource] = None) -> AggregatedSentiment:
        """Get aggregated sentiment for a specific cryptocurrency entity.
        
        Args:
            entity: Cryptocurrency entity (e.g., "Bitcoin", "ETH")
            timeframe: Time frame for analysis
            sources: List of content sources to include
            
        Returns:
            Aggregated sentiment for the entity
        """
        self.logger.info("Getting entity sentiment", entity=entity, timeframe=timeframe)
        
        # Normalize entity name
        normalized_entity = self._normalize_entity(entity)
        
        # In a real implementation, this would query a database of analyzed content
        # For now, generate mock aggregated sentiment
        
        # Default sources if not specified
        if sources is None:
            sources = [ContentSource.NEWS, ContentSource.TWITTER, ContentSource.REDDIT]
        
        # Generate mock sentiment data
        if normalized_entity == "Bitcoin":
            overall_score = 0.65
            positive_count = 120
            negative_count = 30
            neutral_count = 50
        elif normalized_entity == "Ethereum":
            overall_score = 0.45
            positive_count = 80
            negative_count = 40
            neutral_count = 60
        else:
            overall_score = 0.2
            positive_count = 30
            negative_count = 20
            neutral_count = 40
        
        # Mock source distribution
        source_counts = {}
        for source in sources:
            if source == ContentSource.NEWS:
                source_counts[source] = int(positive_count * 0.4) + int(negative_count * 0.4) + int(neutral_count * 0.4)
            elif source == ContentSource.TWITTER:
                source_counts[source] = int(positive_count * 0.4) + int(negative_count * 0.4) + int(neutral_count * 0.4)
            elif source == ContentSource.REDDIT:
                source_counts[source] = int(positive_count * 0.2) + int(negative_count * 0.2) + int(neutral_count * 0.2)
            elif source == ContentSource.DISCORD:
                source_counts[source] = int(positive_count * 0.1) + int(negative_count * 0.1) + int(neutral_count * 0.1)
        
        # Generate mock sentiment trend
        now = datetime.now()
        trend = []
        
        # Convert timeframe to hours for trend generation
        if timeframe == TimeFrame.HOUR_1:
            hours = 1
            points = 12  # 5-minute intervals
        elif timeframe == TimeFrame.HOUR_6:
            hours = 6
            points = 12  # 30-minute intervals
        elif timeframe == TimeFrame.HOUR_12:
            hours = 12
            points = 12  # 1-hour intervals
        elif timeframe == TimeFrame.DAY_1:
            hours = 24
            points = 24  # 1-hour intervals
        elif timeframe == TimeFrame.DAY_3:
            hours = 72
            points = 24  # 3-hour intervals
        elif timeframe == TimeFrame.WEEK_1:
            hours = 168
            points = 28  # 6-hour intervals
        else:  # MONTH_1
            hours = 720
            points = 30  # 1-day intervals
        
        # Generate trend points with some randomness
        import random
        for i in range(points):
            point_time = now - timedelta(hours=hours * (1 - i/points))
            # Add some random variation around the overall score
            point_score = max(-1.0, min(1.0, overall_score + random.uniform(-0.2, 0.2)))
            trend.append((point_time, point_score))
        
        return AggregatedSentiment(
            query=entity,
            overall_score=overall_score,
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            sources=source_counts,
            timeframe=timeframe,
            entity=normalized_entity,
            sentiment_trend=trend,
            timestamp=now
        )
    
    async def query_sentiment(self, query: str, timeframe: TimeFrame = TimeFrame.DAY_1,
                            sources: List[ContentSource] = None) -> AggregatedSentiment:
        """Query sentiment for a specific topic or keyword.
        
        Args:
            query: Search query
            timeframe: Time frame for analysis
            sources: List of content sources to include
            
        Returns:
            Aggregated sentiment for the query
        """
        self.logger.info("Querying sentiment", query=query, timeframe=timeframe)
        
        # Check if query is an entity
        entity = self._normalize_entity(query)
        
        # If it's a recognized entity, use entity-specific method
        if entity:
            return await self.get_entity_sentiment(entity, timeframe, sources)
        
        # Otherwise, treat as a general query
        # In a real implementation, this would search a database of analyzed content
        # For now, generate mock aggregated sentiment
        
        # Default sources if not specified
        if sources is None:
            sources = [ContentSource.NEWS, ContentSource.TWITTER, ContentSource.REDDIT]
        
        # Generate mock sentiment data based on query keywords
        if "bull" in query.lower() or "rally" in query.lower():
            overall_score = 0.7
            positive_count = 100
            negative_count = 20
            neutral_count = 30
        elif "bear" in query.lower() or "crash" in query.lower():
            overall_score = -0.6
            positive_count = 20
            negative_count = 90
            neutral_count = 30
        elif "regulation" in query.lower() or "sec" in query.lower():
            overall_score = -0.3
            positive_count = 40
            negative_count = 60
            neutral_count = 80
        elif "adoption" in query.lower() or "institutional" in query.lower():
            overall_score = 0.5
            positive_count = 80
            negative_count = 30
            neutral_count = 40
        else:
            overall_score = 0.1
            positive_count = 50
            negative_count = 40
            neutral_count = 60
        
        # Mock source distribution
        source_counts = {}
        for source in sources:
            if source == ContentSource.NEWS:
                source_counts[source] = int(positive_count * 0.5) + int(negative_count * 0.5) + int(neutral_count * 0.5)
            elif source == ContentSource.TWITTER:
                source_counts[source] = int(positive_count * 0.3) + int(negative_count * 0.3) + int(neutral_count * 0.3)
            elif source == ContentSource.REDDIT:
                source_counts[source] = int(positive_count * 0.2) + int(negative_count * 0.2) + int(neutral_count * 0.2)
            elif source == ContentSource.DISCORD:
                source_counts[source] = int(positive_count * 0.1) + int(negative_count * 0.1) + int(neutral_count * 0.1)
        
        # Generate mock sentiment trend
        now = datetime.now()
        trend = []
        
        # Convert timeframe to hours for trend generation
        if timeframe == TimeFrame.HOUR_1:
            hours = 1
            points = 12  # 5-minute intervals
        elif timeframe == TimeFrame.HOUR_6:
            hours = 6
            points = 12  # 30-minute intervals
        elif timeframe == TimeFrame.HOUR_12:
            hours = 12
            points = 12  # 1-hour intervals
        elif timeframe == TimeFrame.DAY_1:
            hours = 24
            points = 24  # 1-hour intervals
        elif timeframe == TimeFrame.DAY_3:
            hours = 72
            points = 24  # 3-hour intervals
        elif timeframe == TimeFrame.WEEK_1:
            hours = 168
            points = 28  # 6-hour intervals
        else:  # MONTH_1
            hours = 720
            points = 30  # 1-day intervals
        
        # Generate trend points with some randomness
        import random
        for i in range(points):
            point_time = now - timedelta(hours=hours * (1 - i/points))
            # Add some random variation around the overall score
            point_score = max(-1.0, min(1.0, overall_score + random.uniform(-0.2, 0.2)))
            trend.append((point_time, point_score))
        
        return AggregatedSentiment(
            query=query,
            overall_score=overall_score,
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            sources=source_counts,
            timeframe=timeframe,
            entity=entity,
            sentiment_trend=trend,
            timestamp=now
        )
    
    def _normalize_entity(self, text: str) -> Optional[str]:
        """Normalize cryptocurrency entity names.
        
        Args:
            text: Text containing potential entity
            
        Returns:
            Normalized entity name or None if not found
        """
        if not text:
            return None
        
        # Check if text is directly a known entity
        text_lower = text.lower()
        if text in self.crypto_entities:
            return self.crypto_entities[text]
        if text_lower in self.crypto_entities:
            return self.crypto_entities[text_lower]
        
        # No match found
        return None
    
    def _extract_entity(self, text: str) -> Optional[str]:
        """Extract cryptocurrency entity from text.
        
        Args:
            text: Text to extract entity from
            
        Returns:
            Extracted entity or None if not found
        """
        if not text:
            return None
        
        # In a real implementation, this would use NER or a more sophisticated approach
        # For now, use simple keyword matching
        text_lower = text.lower()
        
        for key, value in self.crypto_entities.items():
            if key.lower() in text_lower:
                return value
        
        return None
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis.
        
        Args:
            text: Text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # In a real implementation, this would handle emojis, hashtags, mentions, etc.
        # For now, do minimal preprocessing
        
        # Replace common crypto symbols
        for key, value in self.crypto_entities.items():
            text = text.replace(f"${key}", value)
        
        # Simple emoji mapping
        emoji_map = {
            "🚀": " positive ",
            "💎": " positive ",
            "🙌": " positive ",
            "📈": " positive ",
            "🔥": " positive ",
            "📉": " negative ",
            "😱": " negative ",
            "😢": " negative ",
            "🤔": " neutral ",
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
        
        return text