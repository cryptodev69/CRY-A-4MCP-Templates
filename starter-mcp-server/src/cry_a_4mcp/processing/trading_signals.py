"""Trading signals module for CRY-A-4MCP.

This module provides trading signal generation and management capabilities
for cryptocurrency markets using technical and sentiment analysis.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import structlog

from ..config import Settings


class SignalType(str, Enum):
    """Type of trading signal."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"


class TimeFrame(str, Enum):
    """Time frame for trading signals."""
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    HOUR_12 = "12h"
    DAY_1 = "1d"
    WEEK_1 = "1w"


class SignalSource(str, Enum):
    """Source of trading signal."""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    HYBRID = "hybrid"


class SignalStrength(str, Enum):
    """Strength of trading signal."""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


@dataclass
class TechnicalIndicator:
    """Technical indicator data."""
    name: str
    value: float
    signal: SignalType
    timeframe: TimeFrame
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class RiskAssessment:
    """Risk assessment for a trading signal."""
    volatility: float  # 0.0 to 1.0
    market_risk: float  # 0.0 to 1.0
    recommended_position_size: float  # Percentage of portfolio
    stop_loss_percentage: float
    take_profit_percentage: float
    risk_reward_ratio: float
    max_drawdown: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TradingSignal:
    """Trading signal for a cryptocurrency."""
    symbol: str
    signal_type: SignalType
    source: SignalSource
    strength: SignalStrength
    timeframe: TimeFrame
    price: float
    confidence: float  # 0.0 to 1.0
    timestamp: datetime = None
    expiration: datetime = None
    indicators: List[TechnicalIndicator] = field(default_factory=list)
    risk_assessment: Optional[RiskAssessment] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.expiration is None:
            # Default expiration based on timeframe
            if self.timeframe == TimeFrame.MINUTE_1:
                self.expiration = self.timestamp + timedelta(minutes=5)
            elif self.timeframe == TimeFrame.MINUTE_5:
                self.expiration = self.timestamp + timedelta(minutes=15)
            elif self.timeframe == TimeFrame.MINUTE_15:
                self.expiration = self.timestamp + timedelta(minutes=45)
            elif self.timeframe == TimeFrame.MINUTE_30:
                self.expiration = self.timestamp + timedelta(hours=1, minutes=30)
            elif self.timeframe == TimeFrame.HOUR_1:
                self.expiration = self.timestamp + timedelta(hours=4)
            elif self.timeframe == TimeFrame.HOUR_4:
                self.expiration = self.timestamp + timedelta(hours=12)
            elif self.timeframe == TimeFrame.HOUR_12:
                self.expiration = self.timestamp + timedelta(days=1, hours=12)
            elif self.timeframe == TimeFrame.DAY_1:
                self.expiration = self.timestamp + timedelta(days=3)
            else:  # WEEK_1
                self.expiration = self.timestamp + timedelta(weeks=2)


@dataclass
class BacktestResult:
    """Result of backtesting a trading strategy."""
    symbol: str
    strategy_name: str
    timeframe: TimeFrame
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float  # Percentage
    annualized_return: float  # Percentage
    max_drawdown: float  # Percentage
    sharpe_ratio: float
    win_rate: float  # Percentage
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_profit_per_trade: float
    avg_loss_per_trade: float
    avg_holding_period: timedelta
    signals: List[TradingSignal] = field(default_factory=list)
    equity_curve: List[Tuple[datetime, float]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TradingSignalsGenerator:
    """Trading signals generator for cryptocurrency markets."""
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the trading signals generator."""
        self.settings = settings
        self.logger = structlog.get_logger(self.__class__.__name__)
        
        # Common cryptocurrency mapping
        self.crypto_mapping = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "BNB": "Binance Coin",
            "ADA": "Cardano",
            "SOL": "Solana",
            "XRP": "Ripple",
            "DOGE": "Dogecoin",
            "DOT": "Polkadot",
            "AVAX": "Avalanche",
            "MATIC": "Polygon",
        }
        
        # Initialize technical indicators
        self.technical_indicators = {
            "RSI": self._calculate_rsi,
            "MACD": self._calculate_macd,
            "Bollinger Bands": self._calculate_bollinger_bands,
            "Moving Average": self._calculate_moving_average,
            "Stochastic": self._calculate_stochastic,
        }
    
    async def initialize(self) -> None:
        """Initialize the trading signals generator."""
        self.logger.info("Initializing trading signals generator")
        # In a real implementation, this would initialize connections to market data providers
        await asyncio.sleep(0.5)  # Simulate initialization time
        self.logger.info("Trading signals generator initialized")
    
    async def generate_signal(self, symbol: str, timeframe: TimeFrame = TimeFrame.HOUR_1, 
                           source: SignalSource = SignalSource.HYBRID) -> TradingSignal:
        """Generate a trading signal for a specific cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
            timeframe: Time frame for the signal
            source: Source of the signal
            
        Returns:
            Trading signal
        """
        self.logger.info("Generating trading signal", symbol=symbol, timeframe=timeframe, source=source)
        
        # Normalize symbol
        symbol = symbol.upper()
        
        # In a real implementation, this would fetch market data and apply technical analysis
        # For now, generate mock trading signal
        
        # Get mock price
        price = await self._get_mock_price(symbol)
        
        # Generate technical indicators
        indicators = await self._generate_indicators(symbol, timeframe)
        
        # Determine signal type and strength based on indicators
        signal_type, strength, confidence = self._determine_signal(indicators, source)
        
        # Generate risk assessment
        risk_assessment = await self._generate_risk_assessment(symbol, signal_type, price)
        
        # Create trading signal
        signal = TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            source=source,
            strength=strength,
            timeframe=timeframe,
            price=price,
            confidence=confidence,
            indicators=indicators,
            risk_assessment=risk_assessment,
            metadata={
                "generated_by": "TradingSignalsGenerator",
                "version": "1.0.0",
            }
        )
        
        return signal
    
    async def get_signals(self, symbols: List[str] = None, timeframes: List[TimeFrame] = None,
                        signal_types: List[SignalType] = None, sources: List[SignalSource] = None,
                        min_confidence: float = 0.5, limit: int = 10) -> List[TradingSignal]:
        """Get trading signals based on filters.
        
        Args:
            symbols: List of cryptocurrency symbols to filter by
            timeframes: List of time frames to filter by
            signal_types: List of signal types to filter by
            sources: List of signal sources to filter by
            min_confidence: Minimum confidence threshold
            limit: Maximum number of signals to return
            
        Returns:
            List of trading signals
        """
        self.logger.info("Getting trading signals", symbols=symbols, timeframes=timeframes, 
                        signal_types=signal_types, sources=sources, min_confidence=min_confidence)
        
        # Default values
        if symbols is None:
            symbols = list(self.crypto_mapping.keys())[:5]  # Top 5 cryptocurrencies
        if timeframes is None:
            timeframes = [TimeFrame.HOUR_1, TimeFrame.DAY_1]  # Default timeframes
        if signal_types is None:
            signal_types = [SignalType.BUY, SignalType.SELL, SignalType.STRONG_BUY, SignalType.STRONG_SELL]
        if sources is None:
            sources = [SignalSource.HYBRID]
        
        # In a real implementation, this would query a database of signals
        # For now, generate mock signals
        
        signals = []
        tasks = []
        
        # Generate signals for each symbol and timeframe combination
        for symbol in symbols[:min(5, len(symbols))]:  # Limit to 5 symbols for mock data
            for timeframe in timeframes[:min(2, len(timeframes))]:  # Limit to 2 timeframes for mock data
                for source in sources[:min(1, len(sources))]:  # Limit to 1 source for mock data
                    tasks.append(self.generate_signal(symbol, timeframe, source))
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Filter signals
        for signal in results:
            if signal.confidence >= min_confidence and signal.signal_type in signal_types:
                signals.append(signal)
        
        # Sort by confidence (descending)
        signals.sort(key=lambda x: x.confidence, reverse=True)
        
        # Limit results
        return signals[:limit]
    
    async def backtest(self, strategy_name: str, symbols: List[str], timeframe: TimeFrame,
                     start_date: datetime, end_date: datetime, initial_capital: float = 10000.0) -> BacktestResult:
        """Backtest a trading strategy.
        
        Args:
            strategy_name: Name of the strategy to backtest
            symbols: List of cryptocurrency symbols to include
            timeframe: Time frame for the backtest
            start_date: Start date for the backtest
            end_date: End date for the backtest
            initial_capital: Initial capital for the backtest
            
        Returns:
            Backtest result
        """
        self.logger.info("Backtesting trading strategy", strategy_name=strategy_name, symbols=symbols,
                        timeframe=timeframe, start_date=start_date, end_date=end_date)
        
        # In a real implementation, this would run a full backtest with historical data
        # For now, generate mock backtest result
        
        # Generate mock signals for the backtest period
        signals = []
        current_date = start_date
        while current_date <= end_date:
            # Generate a signal every few days/hours depending on timeframe
            if timeframe in [TimeFrame.MINUTE_1, TimeFrame.MINUTE_5, TimeFrame.MINUTE_15, TimeFrame.MINUTE_30]:
                step = timedelta(hours=1)
            elif timeframe in [TimeFrame.HOUR_1, TimeFrame.HOUR_4, TimeFrame.HOUR_12]:
                step = timedelta(days=1)
            else:  # DAY_1, WEEK_1
                step = timedelta(days=7)
            
            # Only generate signals on some intervals (not every step)
            if current_date.day % 3 == 0 or current_date.day % 7 == 0:
                for symbol in symbols[:min(2, len(symbols))]:  # Limit to 2 symbols for mock data
                    # Create a mock signal with the historical date
                    mock_signal = await self.generate_signal(symbol, timeframe)
                    mock_signal.timestamp = current_date
                    mock_signal.expiration = current_date + step * 3
                    signals.append(mock_signal)
            
            current_date += step
        
        # Generate mock equity curve
        equity_curve = []
        current_capital = initial_capital
        current_date = start_date
        while current_date <= end_date:
            # Add some randomness to the equity curve
            import random
            change_percent = random.uniform(-0.02, 0.03)  # -2% to +3%
            current_capital *= (1 + change_percent)
            equity_curve.append((current_date, current_capital))
            
            # Step forward in time
            if timeframe in [TimeFrame.MINUTE_1, TimeFrame.MINUTE_5, TimeFrame.MINUTE_15, TimeFrame.MINUTE_30]:
                current_date += timedelta(hours=4)
            elif timeframe in [TimeFrame.HOUR_1, TimeFrame.HOUR_4, TimeFrame.HOUR_12]:
                current_date += timedelta(days=1)
            else:  # DAY_1, WEEK_1
                current_date += timedelta(days=3)
        
        # Calculate mock performance metrics
        final_capital = equity_curve[-1][1]
        total_return = (final_capital - initial_capital) / initial_capital * 100
        
        # Calculate annualized return
        days = (end_date - start_date).days
        if days > 0:
            annualized_return = ((final_capital / initial_capital) ** (365 / days) - 1) * 100
        else:
            annualized_return = 0.0
        
        # Calculate max drawdown
        max_drawdown = 0.0
        peak_value = initial_capital
        for _, value in equity_curve:
            if value > peak_value:
                peak_value = value
            drawdown = (peak_value - value) / peak_value * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        # Generate mock trade statistics
        total_trades = len(signals)
        winning_trades = int(total_trades * 0.6)  # 60% win rate
        losing_trades = total_trades - winning_trades
        
        avg_profit_per_trade = total_return / total_trades if total_trades > 0 else 0.0
        avg_loss_per_trade = -avg_profit_per_trade * 0.7  # Average loss is 70% of average profit
        
        # Calculate Sharpe ratio (simplified)
        sharpe_ratio = 1.5  # Mock value
        
        # Calculate profit factor
        profit_factor = abs(winning_trades * avg_profit_per_trade) / abs(losing_trades * avg_loss_per_trade) if losing_trades > 0 and avg_loss_per_trade != 0 else 0.0
        
        # Calculate average holding period
        avg_holding_period = timedelta(days=3) if timeframe in [TimeFrame.DAY_1, TimeFrame.WEEK_1] else timedelta(hours=8)
        
        return BacktestResult(
            symbol=",".join(symbols),
            strategy_name=strategy_name,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annualized_return=annualized_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=winning_trades / total_trades * 100 if total_trades > 0 else 0.0,
            profit_factor=profit_factor,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_profit_per_trade=avg_profit_per_trade,
            avg_loss_per_trade=avg_loss_per_trade,
            avg_holding_period=avg_holding_period,
            signals=signals,
            equity_curve=equity_curve,
            metadata={
                "backtest_engine": "TradingSignalsGenerator",
                "version": "1.0.0",
            }
        )
    
    async def _get_mock_price(self, symbol: str) -> float:
        """Get mock price for a cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol
            
        Returns:
            Mock price
        """
        # Mock prices for common cryptocurrencies
        prices = {
            "BTC": 50000.0,
            "ETH": 3000.0,
            "BNB": 400.0,
            "ADA": 1.2,
            "SOL": 150.0,
            "XRP": 0.8,
            "DOGE": 0.15,
            "DOT": 20.0,
            "AVAX": 80.0,
            "MATIC": 1.5,
        }
        
        # Add some randomness to the price
        import random
        base_price = prices.get(symbol, 100.0)  # Default to 100.0 if symbol not found
        return base_price * random.uniform(0.98, 1.02)  # +/- 2%
    
    async def _generate_indicators(self, symbol: str, timeframe: TimeFrame) -> List[TechnicalIndicator]:
        """Generate technical indicators for a cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol
            timeframe: Time frame for the indicators
            
        Returns:
            List of technical indicators
        """
        # In a real implementation, this would calculate actual technical indicators
        # For now, generate mock indicators
        
        indicators = []
        
        # Generate RSI
        rsi = await self._calculate_rsi(symbol, timeframe)
        indicators.append(rsi)
        
        # Generate MACD
        macd = await self._calculate_macd(symbol, timeframe)
        indicators.append(macd)
        
        # Generate Bollinger Bands
        bb = await self._calculate_bollinger_bands(symbol, timeframe)
        indicators.append(bb)
        
        # Generate Moving Average
        ma = await self._calculate_moving_average(symbol, timeframe)
        indicators.append(ma)
        
        # Generate Stochastic
        stoch = await self._calculate_stochastic(symbol, timeframe)
        indicators.append(stoch)
        
        return indicators
    
    async def _calculate_rsi(self, symbol: str, timeframe: TimeFrame) -> TechnicalIndicator:
        """Calculate RSI technical indicator.
        
        Args:
            symbol: Cryptocurrency symbol
            timeframe: Time frame for the indicator
            
        Returns:
            RSI technical indicator
        """
        # In a real implementation, this would calculate actual RSI
        # For now, generate mock RSI
        
        import random
        rsi_value = random.uniform(30.0, 70.0)
        
        # Determine signal based on RSI value
        if rsi_value < 30.0:
            signal = SignalType.BUY
        elif rsi_value > 70.0:
            signal = SignalType.SELL
        else:
            signal = SignalType.HOLD
        
        return TechnicalIndicator(
            name="RSI",
            value=rsi_value,
            signal=signal,
            timeframe=timeframe
        )
    
    async def _calculate_macd(self, symbol: str, timeframe: TimeFrame) -> TechnicalIndicator:
        """Calculate MACD technical indicator.
        
        Args:
            symbol: Cryptocurrency symbol
            timeframe: Time frame for the indicator
            
        Returns:
            MACD technical indicator
        """
        # In a real implementation, this would calculate actual MACD
        # For now, generate mock MACD
        
        import random
        macd_value = random.uniform(-10.0, 10.0)
        
        # Determine signal based on MACD value
        if macd_value > 2.0:
            signal = SignalType.BUY
        elif macd_value < -2.0:
            signal = SignalType.SELL
        else:
            signal = SignalType.HOLD
        
        return TechnicalIndicator(
            name="MACD",
            value=macd_value,
            signal=signal,
            timeframe=timeframe
        )
    
    async def _calculate_bollinger_bands(self, symbol: str, timeframe: TimeFrame) -> TechnicalIndicator:
        """Calculate Bollinger Bands technical indicator.
        
        Args:
            symbol: Cryptocurrency symbol
            timeframe: Time frame for the indicator
            
        Returns:
            Bollinger Bands technical indicator
        """
        # In a real implementation, this would calculate actual Bollinger Bands
        # For now, generate mock Bollinger Bands
        
        import random
        # Value represents the position within the bands (0 = lower band, 1 = upper band, 0.5 = middle band)
        bb_value = random.uniform(0.0, 1.0)
        
        # Determine signal based on Bollinger Bands value
        if bb_value < 0.2:
            signal = SignalType.BUY
        elif bb_value > 0.8:
            signal = SignalType.SELL
        else:
            signal = SignalType.HOLD
        
        return TechnicalIndicator(
            name="Bollinger Bands",
            value=bb_value,
            signal=signal,
            timeframe=timeframe
        )
    
    async def _calculate_moving_average(self, symbol: str, timeframe: TimeFrame) -> TechnicalIndicator:
        """Calculate Moving Average technical indicator.
        
        Args:
            symbol: Cryptocurrency symbol
            timeframe: Time frame for the indicator
            
        Returns:
            Moving Average technical indicator
        """
        # In a real implementation, this would calculate actual Moving Average
        # For now, generate mock Moving Average
        
        import random
        # Value represents the price relative to the moving average (< 1 = below MA, > 1 = above MA)
        ma_value = random.uniform(0.9, 1.1)
        
        # Determine signal based on Moving Average value
        if ma_value > 1.02:
            signal = SignalType.SELL
        elif ma_value < 0.98:
            signal = SignalType.BUY
        else:
            signal = SignalType.HOLD
        
        return TechnicalIndicator(
            name="Moving Average",
            value=ma_value,
            signal=signal,
            timeframe=timeframe
        )
    
    async def _calculate_stochastic(self, symbol: str, timeframe: TimeFrame) -> TechnicalIndicator:
        """Calculate Stochastic technical indicator.
        
        Args:
            symbol: Cryptocurrency symbol
            timeframe: Time frame for the indicator
            
        Returns:
            Stochastic technical indicator
        """
        # In a real implementation, this would calculate actual Stochastic
        # For now, generate mock Stochastic
        
        import random
        stoch_value = random.uniform(0.0, 100.0)
        
        # Determine signal based on Stochastic value
        if stoch_value < 20.0:
            signal = SignalType.BUY
        elif stoch_value > 80.0:
            signal = SignalType.SELL
        else:
            signal = SignalType.HOLD
        
        return TechnicalIndicator(
            name="Stochastic",
            value=stoch_value,
            signal=signal,
            timeframe=timeframe
        )
    
    def _determine_signal(self, indicators: List[TechnicalIndicator], source: SignalSource) -> Tuple[SignalType, SignalStrength, float]:
        """Determine overall signal type and strength based on indicators.
        
        Args:
            indicators: List of technical indicators
            source: Source of the signal
            
        Returns:
            Tuple of (signal_type, strength, confidence)
        """
        # Count signals by type
        signal_counts = {
            SignalType.BUY: 0,
            SignalType.SELL: 0,
            SignalType.HOLD: 0,
            SignalType.STRONG_BUY: 0,
            SignalType.STRONG_SELL: 0,
        }
        
        for indicator in indicators:
            signal_counts[indicator.signal] += 1
        
        # Determine overall signal type
        buy_signals = signal_counts[SignalType.BUY] + signal_counts[SignalType.STRONG_BUY]
        sell_signals = signal_counts[SignalType.SELL] + signal_counts[SignalType.STRONG_SELL]
        hold_signals = signal_counts[SignalType.HOLD]
        
        if buy_signals > sell_signals and buy_signals > hold_signals:
            if buy_signals >= len(indicators) * 0.7:
                signal_type = SignalType.STRONG_BUY
            else:
                signal_type = SignalType.BUY
        elif sell_signals > buy_signals and sell_signals > hold_signals:
            if sell_signals >= len(indicators) * 0.7:
                signal_type = SignalType.STRONG_SELL
            else:
                signal_type = SignalType.SELL
        else:
            signal_type = SignalType.HOLD
        
        # Determine signal strength
        if signal_type in [SignalType.STRONG_BUY, SignalType.STRONG_SELL]:
            strength = SignalStrength.STRONG
        elif signal_type in [SignalType.BUY, SignalType.SELL]:
            if abs(buy_signals - sell_signals) >= len(indicators) * 0.4:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK
        else:  # HOLD
            strength = SignalStrength.WEAK
        
        # Calculate confidence
        if signal_type in [SignalType.STRONG_BUY, SignalType.STRONG_SELL]:
            confidence = 0.8 + (max(buy_signals, sell_signals) / len(indicators)) * 0.2
        elif signal_type in [SignalType.BUY, SignalType.SELL]:
            confidence = 0.5 + (max(buy_signals, sell_signals) / len(indicators)) * 0.3
        else:  # HOLD
            confidence = 0.4 + (hold_signals / len(indicators)) * 0.2
        
        # Adjust confidence based on source
        if source == SignalSource.HYBRID:
            # Hybrid signals have higher confidence
            confidence = min(confidence * 1.2, 1.0)
        
        return signal_type, strength, confidence
    
    async def _generate_risk_assessment(self, symbol: str, signal_type: SignalType, price: float) -> RiskAssessment:
        """Generate risk assessment for a trading signal.
        
        Args:
            symbol: Cryptocurrency symbol
            signal_type: Type of trading signal
            price: Current price
            
        Returns:
            Risk assessment
        """
        # In a real implementation, this would calculate actual risk metrics
        # For now, generate mock risk assessment
        
        import random
        
        # Volatility based on symbol (some cryptocurrencies are more volatile)
        if symbol in ["BTC", "ETH"]:
            volatility = random.uniform(0.3, 0.5)
        else:
            volatility = random.uniform(0.5, 0.8)
        
        # Market risk (overall market conditions)
        market_risk = random.uniform(0.3, 0.7)
        
        # Position size based on volatility and market risk
        recommended_position_size = max(1.0, 10.0 - (volatility * 10.0) - (market_risk * 5.0))
        
        # Stop loss and take profit percentages
        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
            stop_loss_percentage = volatility * 100 * random.uniform(0.8, 1.2)
            take_profit_percentage = stop_loss_percentage * random.uniform(1.5, 2.5)
        else:  # SELL, STRONG_SELL
            stop_loss_percentage = volatility * 100 * random.uniform(0.8, 1.2)
            take_profit_percentage = stop_loss_percentage * random.uniform(1.5, 2.5)
        
        # Risk-reward ratio
        risk_reward_ratio = take_profit_percentage / stop_loss_percentage
        
        # Max drawdown
        max_drawdown = volatility * 100 * random.uniform(1.0, 1.5)
        
        return RiskAssessment(
            volatility=volatility,
            market_risk=market_risk,
            recommended_position_size=recommended_position_size,
            stop_loss_percentage=stop_loss_percentage,
            take_profit_percentage=take_profit_percentage,
            risk_reward_ratio=risk_reward_ratio,
            max_drawdown=max_drawdown
        )