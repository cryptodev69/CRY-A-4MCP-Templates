"""
Cryptocurrency analyzer for CRY-A-4MCP.

This module provides cryptocurrency analysis capabilities including
market data, sentiment analysis, and technical indicators.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog

from ..config import Settings


class AnalysisType(str, Enum):
    """Type of cryptocurrency analysis."""
    COMPREHENSIVE = "comprehensive"
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"


@dataclass
class MarketData:
    """Cryptocurrency market data."""
    price: float
    market_cap: float
    volume_24h: float
    price_change_24h: float
    price_change_7d: float
    price_change_30d: float
    timestamp: datetime


@dataclass
class SentimentData:
    """Cryptocurrency sentiment data."""
    score: float  # -1.0 to 1.0
    positive_mentions: int
    negative_mentions: int
    neutral_mentions: int
    sources_count: int
    timestamp: datetime


@dataclass
class TechnicalData:
    """Cryptocurrency technical indicators."""
    rsi_14: float
    ma_50: float
    ma_200: float
    bollinger_upper: float
    bollinger_lower: float
    macd: float
    macd_signal: float
    timestamp: datetime


@dataclass
class RiskAssessment:
    """Cryptocurrency risk assessment."""
    volatility_score: float  # 0.0 to 1.0
    liquidity_score: float  # 0.0 to 1.0
    market_cap_category: str  # Large, Medium, Small, Micro
    overall_risk: float  # 0.0 to 1.0
    timestamp: datetime


@dataclass
class AnalysisResult:
    """Comprehensive cryptocurrency analysis result."""
    symbol: str
    name: str
    analysis_type: AnalysisType
    market_data: Optional[MarketData] = None
    sentiment_data: Optional[SentimentData] = None
    technical_data: Optional[TechnicalData] = None
    risk_assessment: Optional[RiskAssessment] = None
    summary: str = ""
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CryptoAnalyzer:
    """Cryptocurrency analyzer for market data, sentiment, and technical analysis."""
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the cryptocurrency analyzer."""
        self.settings = settings
        self.logger = structlog.get_logger(self.__class__.__name__)
        
        # Common cryptocurrency mapping
        self.crypto_names = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "BNB": "Binance Coin",
            "ADA": "Cardano",
            "SOL": "Solana",
            "XRP": "Ripple",
            "DOGE": "Dogecoin",
            "DOT": "Polkadot",
            "LTC": "Litecoin",
            "LINK": "Chainlink",
        }
    
    async def initialize(self) -> None:
        """Initialize the analyzer."""
        self.logger.info("Initializing cryptocurrency analyzer")
        # No specific initialization needed for now
        self.logger.info("Cryptocurrency analyzer initialized")
    
    async def analyze(self, symbol: str, analysis_type: str = "comprehensive", 
                     days_back: int = 30) -> AnalysisResult:
        """Perform cryptocurrency analysis.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., BTC, ETH)
            analysis_type: Type of analysis to perform
            days_back: Number of days of historical data to analyze
            
        Returns:
            Analysis result
        """
        self.logger.info("Analyzing cryptocurrency", symbol=symbol, analysis_type=analysis_type)
        
        # Validate symbol
        symbol = symbol.upper()
        if symbol not in self.crypto_names:
            self.logger.warning("Unknown cryptocurrency symbol", symbol=symbol)
            name = symbol  # Use symbol as name for unknown cryptocurrencies
        else:
            name = self.crypto_names[symbol]
        
        # Validate analysis type
        try:
            analysis_type_enum = AnalysisType(analysis_type)
        except ValueError:
            self.logger.warning("Invalid analysis type, using comprehensive", 
                              provided=analysis_type)
            analysis_type_enum = AnalysisType.COMPREHENSIVE
        
        # Create result object
        result = AnalysisResult(
            symbol=symbol,
            name=name,
            analysis_type=analysis_type_enum,
        )
        
        # Perform requested analysis
        tasks = []
        
        if analysis_type_enum in [AnalysisType.COMPREHENSIVE, AnalysisType.TECHNICAL]:
            tasks.append(self._get_technical_data(symbol, days_back))
        else:
            result.technical_data = None
        
        if analysis_type_enum in [AnalysisType.COMPREHENSIVE, AnalysisType.FUNDAMENTAL]:
            tasks.append(self._get_market_data(symbol))
        else:
            result.market_data = None
        
        if analysis_type_enum in [AnalysisType.COMPREHENSIVE, AnalysisType.SENTIMENT]:
            tasks.append(self._get_sentiment_data(symbol, days_back))
        else:
            result.sentiment_data = None
        
        if analysis_type_enum == AnalysisType.COMPREHENSIVE:
            tasks.append(self._get_risk_assessment(symbol))
        else:
            result.risk_assessment = None
        
        # Wait for all tasks to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, res in enumerate(results):
                if isinstance(res, Exception):
                    self.logger.error("Analysis task failed", error=str(res))
                    continue
                
                if i == 0 and analysis_type_enum in [AnalysisType.COMPREHENSIVE, AnalysisType.TECHNICAL]:
                    result.technical_data = res
                elif i == 1 and analysis_type_enum in [AnalysisType.COMPREHENSIVE, AnalysisType.FUNDAMENTAL]:
                    result.market_data = res
                elif i == 2 and analysis_type_enum in [AnalysisType.COMPREHENSIVE, AnalysisType.SENTIMENT]:
                    result.sentiment_data = res
                elif i == 3 and analysis_type_enum == AnalysisType.COMPREHENSIVE:
                    result.risk_assessment = res
        
        # Generate summary
        result.summary = self._generate_summary(result)
        
        self.logger.info("Cryptocurrency analysis completed", symbol=symbol)
        
        return result
    
    async def _get_market_data(self, symbol: str) -> MarketData:
        """Get cryptocurrency market data.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Market data
        """
        # In a real implementation, this would call an external API
        # For now, generate mock data
        return MarketData(
            price=50000.0 if symbol == "BTC" else 3000.0 if symbol == "ETH" else 100.0,
            market_cap=1000000000.0 if symbol == "BTC" else 500000000.0 if symbol == "ETH" else 10000000.0,
            volume_24h=50000000.0 if symbol == "BTC" else 20000000.0 if symbol == "ETH" else 1000000.0,
            price_change_24h=2.5 if symbol == "BTC" else 1.5 if symbol == "ETH" else 0.5,
            price_change_7d=5.0 if symbol == "BTC" else 3.0 if symbol == "ETH" else 1.0,
            price_change_30d=10.0 if symbol == "BTC" else 7.0 if symbol == "ETH" else 2.0,
            timestamp=datetime.now(),
        )
    
    async def _get_sentiment_data(self, symbol: str, days_back: int) -> SentimentData:
        """Get cryptocurrency sentiment data.
        
        Args:
            symbol: Cryptocurrency symbol
            days_back: Number of days of historical data
            
        Returns:
            Sentiment data
        """
        # In a real implementation, this would analyze news and social media
        # For now, generate mock data
        return SentimentData(
            score=0.7 if symbol == "BTC" else 0.6 if symbol == "ETH" else 0.5,
            positive_mentions=1000 if symbol == "BTC" else 500 if symbol == "ETH" else 100,
            negative_mentions=200 if symbol == "BTC" else 100 if symbol == "ETH" else 50,
            neutral_mentions=500 if symbol == "BTC" else 300 if symbol == "ETH" else 100,
            sources_count=50 if symbol == "BTC" else 30 if symbol == "ETH" else 10,
            timestamp=datetime.now(),
        )
    
    async def _get_technical_data(self, symbol: str, days_back: int) -> TechnicalData:
        """Get cryptocurrency technical indicators.
        
        Args:
            symbol: Cryptocurrency symbol
            days_back: Number of days of historical data
            
        Returns:
            Technical data
        """
        # In a real implementation, this would calculate technical indicators
        # For now, generate mock data
        return TechnicalData(
            rsi_14=65.0 if symbol == "BTC" else 60.0 if symbol == "ETH" else 55.0,
            ma_50=48000.0 if symbol == "BTC" else 2900.0 if symbol == "ETH" else 95.0,
            ma_200=45000.0 if symbol == "BTC" else 2800.0 if symbol == "ETH" else 90.0,
            bollinger_upper=52000.0 if symbol == "BTC" else 3100.0 if symbol == "ETH" else 105.0,
            bollinger_lower=48000.0 if symbol == "BTC" else 2900.0 if symbol == "ETH" else 95.0,
            macd=200.0 if symbol == "BTC" else 100.0 if symbol == "ETH" else 5.0,
            macd_signal=180.0 if symbol == "BTC" else 90.0 if symbol == "ETH" else 4.5,
            timestamp=datetime.now(),
        )
    
    async def _get_risk_assessment(self, symbol: str) -> RiskAssessment:
        """Get cryptocurrency risk assessment.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Risk assessment
        """
        # In a real implementation, this would perform risk analysis
        # For now, generate mock data
        if symbol == "BTC":
            category = "Large"
            volatility = 0.3
            liquidity = 0.9
            overall = 0.2
        elif symbol == "ETH":
            category = "Large"
            volatility = 0.4
            liquidity = 0.8
            overall = 0.3
        else:
            category = "Medium"
            volatility = 0.6
            liquidity = 0.5
            overall = 0.5
        
        return RiskAssessment(
            volatility_score=volatility,
            liquidity_score=liquidity,
            market_cap_category=category,
            overall_risk=overall,
            timestamp=datetime.now(),
        )
    
    def _generate_summary(self, result: AnalysisResult) -> str:
        """Generate a summary of the analysis result.
        
        Args:
            result: Analysis result
            
        Returns:
            Summary text
        """
        summary_parts = [f"{result.name} ({result.symbol}) Analysis:"]
        
        # Add market data summary
        if result.market_data:
            md = result.market_data
            summary_parts.append(
                f"Market Data: Price ${md.price:,.2f}, Market Cap ${md.market_cap:,.0f}, "
                f"24h Volume ${md.volume_24h:,.0f}, 24h Change {md.price_change_24h:+.2f}%"
            )
        
        # Add sentiment data summary
        if result.sentiment_data:
            sd = result.sentiment_data
            sentiment_text = "Positive" if sd.score > 0.6 else "Neutral" if sd.score > 0.4 else "Negative"
            summary_parts.append(
                f"Sentiment: {sentiment_text} (Score: {sd.score:.2f}), "
                f"Mentions: {sd.positive_mentions} positive, {sd.negative_mentions} negative, "
                f"{sd.neutral_mentions} neutral from {sd.sources_count} sources"
            )
        
        # Add technical data summary
        if result.technical_data:
            td = result.technical_data
            trend = "Bullish" if td.ma_50 > td.ma_200 else "Bearish"
            rsi_status = "Overbought" if td.rsi_14 > 70 else "Oversold" if td.rsi_14 < 30 else "Neutral"
            summary_parts.append(
                f"Technical: {trend} trend, RSI {td.rsi_14:.1f} ({rsi_status}), "
                f"MACD {td.macd:.1f} vs Signal {td.macd_signal:.1f}"
            )
        
        # Add risk assessment summary
        if result.risk_assessment:
            ra = result.risk_assessment
            risk_text = "Low" if ra.overall_risk < 0.3 else "Medium" if ra.overall_risk < 0.6 else "High"
            summary_parts.append(
                f"Risk Assessment: {risk_text} risk ({ra.overall_risk:.2f}), "
                f"{ra.market_cap_category} market cap, Volatility {ra.volatility_score:.2f}, "
                f"Liquidity {ra.liquidity_score:.2f}"
            )
        
        # Join all parts
        return "\n".join(summary_parts)