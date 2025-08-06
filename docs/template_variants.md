# CRY-A-4MCP Template Variants

Choose the pre-configured template that best matches your cryptocurrency analysis needs.

## 🎯 Available Variants

### 1. Market Sentiment Analysis (`variants/market-sentiment/`)
**Best for**: News analysis, social media monitoring, sentiment tracking

**Pre-configured Features**:
- Enhanced news crawling with sentiment analysis
- Social media data integration (Twitter, Reddit, Discord)
- Sentiment scoring algorithms optimized for crypto
- Real-time sentiment dashboards
- Alert system for sentiment shifts

**Sample Data Includes**:
- 1000+ crypto news articles with sentiment scores
- Social media posts from major crypto communities
- Historical sentiment data for major cryptocurrencies
- Correlation data between sentiment and price movements

**Optimized For**:
- News sentiment analysis queries
- Social media trend detection
- Market mood assessment
- Sentiment-based trading signals

**Quick Start**:
```bash
cd variants/market-sentiment
./setup.sh
./docker-stack/start.sh start
```

### 2. Trading Signals (`variants/trading-signals/`)
**Best for**: Technical analysis, trading automation, signal generation

**Pre-configured Features**:
- Technical indicator calculations (RSI, MACD, Bollinger Bands)
- Price pattern recognition algorithms
- Multi-timeframe analysis capabilities
- Backtesting framework for strategies
- Real-time signal generation and alerts

**Sample Data Includes**:
- OHLCV data for 50+ cryptocurrencies (1 year history)
- Technical indicators pre-calculated
- Historical trading signals with performance metrics
- Market microstructure data for major pairs

**Optimized For**:
- Technical analysis queries
- Trading signal generation
- Strategy backtesting
- Risk assessment calculations

**Quick Start**:
```bash
cd variants/trading-signals
./setup.sh
./docker-stack/start.sh start
```

### 3. Compliance Monitoring (`variants/compliance-monitoring/`)
**Best for**: Regulatory compliance, risk assessment, AML monitoring

**Pre-configured Features**:
- Regulatory news tracking and analysis
- AML/KYC data integration capabilities
- Compliance risk scoring algorithms
- Regulatory change impact assessment
- Audit trail and reporting features

**Sample Data Includes**:
- Regulatory announcements from major jurisdictions
- Compliance risk indicators for exchanges and tokens
- Historical regulatory impact data
- Jurisdiction-specific compliance requirements

**Optimized For**:
- Regulatory compliance queries
- Risk assessment calculations
- Compliance monitoring alerts
- Regulatory impact analysis

**Quick Start**:
```bash
cd variants/compliance-monitoring
./setup.sh
./docker-stack/start.sh start
```

## 🔧 Variant Configuration Details

### Market Sentiment Analysis Configuration

**Environment Variables** (`.env`):
```bash
# Sentiment Analysis Specific
CRYA4MCP_SENTIMENT_MODEL=finbert-crypto
CRYA4MCP_NEWS_SOURCES=coindesk,cointelegraph,decrypt,theblock
CRYA4MCP_SOCIAL_PLATFORMS=twitter,reddit,discord
CRYA4MCP_SENTIMENT_UPDATE_INTERVAL=300  # 5 minutes

# Enhanced crawling for news
CRYA4MCP_CRAWL_FREQUENCY=high
CRYA4MCP_CONTENT_TYPES=news,social,analysis
```

**Docker Compose Additions**:
- Sentiment analysis service container
- Social media API connectors
- Real-time news processing pipeline
- Enhanced monitoring for sentiment metrics

**MCP Tools**:
- `analyze_sentiment` - Analyze sentiment of crypto content
- `track_sentiment_trends` - Monitor sentiment changes over time
- `sentiment_alerts` - Set up sentiment-based alerts
- `social_media_scan` - Scan social platforms for mentions

### Trading Signals Configuration

**Environment Variables** (`.env`):
```bash
# Trading Signals Specific
CRYA4MCP_TRADING_PAIRS=BTC/USD,ETH/USD,SOL/USD,ADA/USD
CRYA4MCP_TIMEFRAMES=1m,5m,15m,1h,4h,1d
CRYA4MCP_INDICATORS=RSI,MACD,BB,EMA,SMA
CRYA4MCP_SIGNAL_THRESHOLD=0.7

# Market data configuration
CRYA4MCP_MARKET_DATA_PROVIDER=binance,coinbase,kraken
CRYA4MCP_REAL_TIME_UPDATES=true
```

**Docker Compose Additions**:
- Technical analysis service container
- Market data streaming service
- Backtesting engine container
- Signal generation and alert system

**MCP Tools**:
- `generate_signals` - Generate trading signals for specified pairs
- `backtest_strategy` - Backtest trading strategies
- `calculate_indicators` - Calculate technical indicators
- `risk_assessment` - Assess trading risk metrics

### Compliance Monitoring Configuration

**Environment Variables** (`.env`):
```bash
# Compliance Specific
CRYA4MCP_JURISDICTIONS=US,EU,UK,JP,SG
CRYA4MCP_REGULATORY_SOURCES=sec,cftc,fca,jfsa,mas
CRYA4MCP_COMPLIANCE_LEVEL=strict
CRYA4MCP_AUDIT_RETENTION=7years

# Risk assessment
CRYA4MCP_RISK_FACTORS=regulatory,operational,market,liquidity
CRYA4MCP_COMPLIANCE_ALERTS=true
```

**Docker Compose Additions**:
- Regulatory data service container
- Compliance scoring engine
- Audit logging service
- Risk assessment dashboard

**MCP Tools**:
- `compliance_check` - Check compliance status of entities
- `regulatory_scan` - Scan for regulatory changes
- `risk_score` - Calculate compliance risk scores
- `audit_trail` - Generate audit reports

## 🚀 Choosing the Right Variant

### Decision Matrix

| Use Case | Market Sentiment | Trading Signals | Compliance |
|----------|------------------|-----------------|------------|
| **News Analysis** | ✅ Primary | ⚠️ Secondary | ⚠️ Secondary |
| **Social Media** | ✅ Primary | ❌ Not included | ❌ Not included |
| **Technical Analysis** | ❌ Not included | ✅ Primary | ❌ Not included |
| **Trading Automation** | ⚠️ Secondary | ✅ Primary | ❌ Not included |
| **Risk Assessment** | ⚠️ Secondary | ⚠️ Secondary | ✅ Primary |
| **Regulatory Monitoring** | ❌ Not included | ❌ Not included | ✅ Primary |

### Hybrid Approach

You can also combine variants by:

1. **Starting with one variant** as your base
2. **Adding components** from other variants
3. **Customizing configuration** to meet specific needs

Example hybrid setup:
```bash
# Start with trading signals base
cd variants/trading-signals
./setup.sh

# Add sentiment analysis components
cp -r ../market-sentiment/src/sentiment_analysis src/
# Update configuration to include sentiment features
```

## 📊 Performance Characteristics

### Resource Requirements by Variant

| Variant | RAM | CPU | Storage | Network |
|---------|-----|-----|---------|---------|
| **Market Sentiment** | 6GB | 4 cores | 50GB | High |
| **Trading Signals** | 8GB | 6 cores | 100GB | Medium |
| **Compliance** | 4GB | 2 cores | 30GB | Low |

### Expected Query Performance

| Variant | Avg Response | 95th Percentile | Concurrent Users |
|---------|--------------|-----------------|------------------|
| **Market Sentiment** | 800ms | 1.5s | 50+ |
| **Trading Signals** | 600ms | 1.2s | 100+ |
| **Compliance** | 400ms | 800ms | 25+ |

## 🔄 Migration Between Variants

### From Base Template to Variant
```bash
# Backup current setup
./scripts/backup_data.sh

# Choose and setup variant
cd variants/[variant-name]
./setup.sh

# Migrate existing data (if compatible)
./scripts/migrate_data.sh /path/to/backup
```

### Between Variants
```bash
# Export data from current variant
./scripts/export_data.sh

# Setup new variant
cd ../[new-variant]
./setup.sh

# Import compatible data
./scripts/import_data.sh /path/to/export
```

## 🛠️ Customization Guide

### Adding Custom Features

1. **Identify base variant** closest to your needs
2. **Review variant structure** and configuration
3. **Add custom components** following established patterns
4. **Update configuration** files and environment variables
5. **Test thoroughly** with your specific use cases

### Configuration Templates

Each variant includes:
- `config/custom.yml` - Custom configuration options
- `scripts/customize.sh` - Customization helper script
- `docs/customization.md` - Detailed customization guide

## 📋 Variant Comparison Summary

| Feature | Market Sentiment | Trading Signals | Compliance |
|---------|------------------|-----------------|------------|
| **News Analysis** | ✅ Advanced | ⚠️ Basic | ⚠️ Regulatory only |
| **Social Media** | ✅ Full integration | ❌ None | ❌ None |
| **Technical Analysis** | ❌ None | ✅ Comprehensive | ❌ None |
| **Price Data** | ⚠️ Basic | ✅ Real-time | ⚠️ Basic |
| **Risk Assessment** | ⚠️ Sentiment risk | ✅ Trading risk | ✅ Compliance risk |
| **Alerts** | ✅ Sentiment alerts | ✅ Signal alerts | ✅ Compliance alerts |
| **Backtesting** | ❌ None | ✅ Full framework | ❌ None |
| **Regulatory Data** | ❌ None | ❌ None | ✅ Comprehensive |

Choose the variant that best matches your primary use case, then customize as needed for your specific requirements.
