"""Trading Signals Tool for CRY-A-4MCP.

This module provides an MCP tool for generating, querying, and backtesting
trading signals for cryptocurrency markets.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import structlog

from ...config import Settings
from ...processing.trading_signals import (
    BacktestResult,
    SignalSource,
    SignalStrength,
    SignalType,
    TimeFrame,
    TradingSignal,
    TradingSignalsGenerator,
)
from ..base_tool import BaseTool


class TradingSignalsTool(BaseTool):
    """MCP tool for cryptocurrency trading signals.
    
    This tool provides trading signal generation, querying, and backtesting
    capabilities for cryptocurrency markets using technical and sentiment analysis.
    """
    
    name = "trading_signals"
    description = "Generate, query, and backtest trading signals for cryptocurrency markets"
    
    input_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["generate", "query", "backtest"],
                "description": "Action to perform: 'generate' for a single signal, 'query' for multiple signals, 'backtest' for strategy testing"
            },
            "symbol": {
                "type": "string",
                "description": "Cryptocurrency symbol (e.g., 'BTC', 'ETH')"
            },
            "symbols": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of cryptocurrency symbols for query or backtest"
            },
            "timeframe": {
                "type": "string",
                "enum": ["1m", "5m", "15m", "30m", "1h", "4h", "12h", "1d", "1w"],
                "description": "Time frame for the trading signal",
                "default": "1h"
            },
            "source": {
                "type": "string",
                "enum": ["technical", "fundamental", "sentiment", "hybrid"],
                "description": "Source of the trading signal",
                "default": "hybrid"
            },
            "signal_types": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["buy", "sell", "hold", "strong_buy", "strong_sell"]
                },
                "description": "Types of signals to include in query results"
            },
            "min_confidence": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Minimum confidence threshold for query results",
                "default": 0.5
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Maximum number of signals to return in query results",
                "default": 10
            },
            "strategy_name": {
                "type": "string",
                "description": "Name of the strategy for backtesting"
            },
            "start_date": {
                "type": "string",
                "format": "date-time",
                "description": "Start date for backtesting (ISO format)"
            },
            "end_date": {
                "type": "string",
                "format": "date-time",
                "description": "End date for backtesting (ISO format)"
            },
            "initial_capital": {
                "type": "number",
                "minimum": 100.0,
                "description": "Initial capital for backtesting",
                "default": 10000.0
            },
            "include_indicators": {
                "type": "boolean",
                "description": "Whether to include technical indicators in the response",
                "default": True
            },
            "include_risk_assessment": {
                "type": "boolean",
                "description": "Whether to include risk assessment in the response",
                "default": True
            }
        },
        "required": ["action"]
    }
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the trading signals tool."""
        super().__init__(settings)
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.generator = TradingSignalsGenerator(settings)
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize the trading signals generator."""
        if not self.initialized:
            await self.generator.initialize()
            self.initialized = True
    
    async def _run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run the trading signals tool.
        
        Args:
            params: Tool parameters
            
        Returns:
            Trading signals results
        """
        await self.initialize()
        
        # Extract action parameter
        action = params.get("action")
        
        if action == "generate":
            return await self._generate_signal(params)
        elif action == "query":
            return await self._query_signals(params)
        elif action == "backtest":
            return await self._backtest_strategy(params)
        else:
            return {"error": f"Invalid action: {action}"}
    
    async def _generate_signal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single trading signal.
        
        Args:
            params: Tool parameters
            
        Returns:
            Generated trading signal
        """
        # Extract parameters
        symbol = params.get("symbol")
        if not symbol:
            return {"error": "Symbol is required for generate action"}
        
        timeframe_str = params.get("timeframe", "1h")
        source_str = params.get("source", "hybrid")
        include_indicators = params.get("include_indicators", True)
        include_risk_assessment = params.get("include_risk_assessment", True)
        
        # Convert string parameters to enums
        timeframe = TimeFrame(timeframe_str)
        source = SignalSource(source_str)
        
        # Generate signal
        signal = await self.generator.generate_signal(symbol, timeframe, source)
        
        # Format response
        return self._format_signal(signal, include_indicators, include_risk_assessment)
    
    async def _query_signals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query multiple trading signals based on filters.
        
        Args:
            params: Tool parameters
            
        Returns:
            Query results
        """
        # Extract parameters
        symbols = params.get("symbols")
        symbol = params.get("symbol")
        
        # If symbol is provided but not symbols, convert to list
        if symbol and not symbols:
            symbols = [symbol]
        
        timeframe_str = params.get("timeframe")
        timeframes = [TimeFrame(timeframe_str)] if timeframe_str else None
        
        source_str = params.get("source")
        sources = [SignalSource(source_str)] if source_str else None
        
        signal_types_str = params.get("signal_types")
        signal_types = [SignalType(st) for st in signal_types_str] if signal_types_str else None
        
        min_confidence = params.get("min_confidence", 0.5)
        limit = params.get("limit", 10)
        
        include_indicators = params.get("include_indicators", True)
        include_risk_assessment = params.get("include_risk_assessment", True)
        
        # Query signals
        signals = await self.generator.get_signals(
            symbols=symbols,
            timeframes=timeframes,
            signal_types=signal_types,
            sources=sources,
            min_confidence=min_confidence,
            limit=limit
        )
        
        # Format response
        return {
            "signals": [
                self._format_signal(signal, include_indicators, include_risk_assessment)
                for signal in signals
            ],
            "count": len(signals),
            "filters": {
                "symbols": symbols,
                "timeframes": [tf.value for tf in timeframes] if timeframes else None,
                "signal_types": [st.value for st in signal_types] if signal_types else None,
                "sources": [s.value for s in sources] if sources else None,
                "min_confidence": min_confidence,
                "limit": limit
            }
        }
    
    async def _backtest_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Backtest a trading strategy.
        
        Args:
            params: Tool parameters
            
        Returns:
            Backtest results
        """
        # Extract parameters
        strategy_name = params.get("strategy_name")
        if not strategy_name:
            return {"error": "Strategy name is required for backtest action"}
        
        symbols = params.get("symbols")
        symbol = params.get("symbol")
        
        # If symbol is provided but not symbols, convert to list
        if symbol and not symbols:
            symbols = [symbol]
        
        if not symbols:
            return {"error": "Symbols are required for backtest action"}
        
        timeframe_str = params.get("timeframe", "1h")
        timeframe = TimeFrame(timeframe_str)
        
        # Parse dates
        start_date_str = params.get("start_date")
        end_date_str = params.get("end_date")
        
        if not start_date_str or not end_date_str:
            # Default to last 30 days if dates not provided
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        else:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            except ValueError:
                return {"error": "Invalid date format. Use ISO format (e.g., '2023-01-01T00:00:00Z')"}
        
        initial_capital = params.get("initial_capital", 10000.0)
        include_signals = params.get("include_indicators", True)  # Reuse parameter
        
        # Run backtest
        result = await self.generator.backtest(
            strategy_name=strategy_name,
            symbols=symbols,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
        
        # Format response
        return self._format_backtest_result(result, include_signals)
    
    def _format_signal(self, signal: TradingSignal, include_indicators: bool = True,
                      include_risk_assessment: bool = True) -> Dict[str, Any]:
        """Format a trading signal for API response.
        
        Args:
            signal: Trading signal to format
            include_indicators: Whether to include technical indicators
            include_risk_assessment: Whether to include risk assessment
            
        Returns:
            Formatted signal
        """
        formatted = {
            "symbol": signal.symbol,
            "signal_type": signal.signal_type.value,
            "source": signal.source.value,
            "strength": signal.strength.value,
            "timeframe": signal.timeframe.value,
            "price": signal.price,
            "confidence": signal.confidence,
            "timestamp": signal.timestamp.isoformat(),
            "expiration": signal.expiration.isoformat() if signal.expiration else None,
        }
        
        # Include indicators if requested
        if include_indicators and signal.indicators:
            formatted["indicators"] = [
                {
                    "name": indicator.name,
                    "value": indicator.value,
                    "signal": indicator.signal.value,
                    "timeframe": indicator.timeframe.value,
                    "timestamp": indicator.timestamp.isoformat() if indicator.timestamp else None
                }
                for indicator in signal.indicators
            ]
        
        # Include risk assessment if requested
        if include_risk_assessment and signal.risk_assessment:
            formatted["risk_assessment"] = {
                "volatility": signal.risk_assessment.volatility,
                "market_risk": signal.risk_assessment.market_risk,
                "recommended_position_size": signal.risk_assessment.recommended_position_size,
                "stop_loss_percentage": signal.risk_assessment.stop_loss_percentage,
                "take_profit_percentage": signal.risk_assessment.take_profit_percentage,
                "risk_reward_ratio": signal.risk_assessment.risk_reward_ratio,
                "max_drawdown": signal.risk_assessment.max_drawdown,
                "timestamp": signal.risk_assessment.timestamp.isoformat() if signal.risk_assessment.timestamp else None
            }
        
        # Include metadata
        if signal.metadata:
            formatted["metadata"] = signal.metadata
        
        return formatted
    
    def _format_backtest_result(self, result: BacktestResult, include_signals: bool = True) -> Dict[str, Any]:
        """Format a backtest result for API response.
        
        Args:
            result: Backtest result to format
            include_signals: Whether to include signals
            
        Returns:
            Formatted backtest result
        """
        formatted = {
            "strategy": {
                "name": result.strategy_name,
                "symbols": result.symbol.split(","),
                "timeframe": result.timeframe.value,
                "start_date": result.start_date.isoformat(),
                "end_date": result.end_date.isoformat(),
                "initial_capital": result.initial_capital
            },
            "performance": {
                "final_capital": result.final_capital,
                "total_return": result.total_return,
                "annualized_return": result.annualized_return,
                "max_drawdown": result.max_drawdown,
                "sharpe_ratio": result.sharpe_ratio,
                "win_rate": result.win_rate,
                "profit_factor": result.profit_factor
            },
            "trades": {
                "total": result.total_trades,
                "winning": result.winning_trades,
                "losing": result.losing_trades,
                "avg_profit": result.avg_profit_per_trade,
                "avg_loss": result.avg_loss_per_trade,
                "avg_holding_period": str(result.avg_holding_period)
            }
        }
        
        # Include equity curve
        if result.equity_curve:
            formatted["equity_curve"] = [
                {"timestamp": dt.isoformat(), "value": value}
                for dt, value in result.equity_curve
            ]
        
        # Include signals if requested
        if include_signals and result.signals:
            formatted["signals"] = [
                self._format_signal(signal, include_indicators=False, include_risk_assessment=False)
                for signal in result.signals[:10]  # Limit to 10 signals
            ]
            
            if len(result.signals) > 10:
                formatted["signals_truncated"] = True
                formatted["total_signals"] = len(result.signals)
        
        # Include metadata
        if result.metadata:
            formatted["metadata"] = result.metadata
        
        return formatted