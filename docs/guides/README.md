# Implementation Guides

Practical guides for implementing and using the CRY-A-4MCP Enhanced Templates package. These guides provide step-by-step instructions, best practices, and real-world examples.

## 📚 Available Guides

### Getting Started
- [Quick Start Guide](./quick-start.md) - Get up and running in 5 minutes
- [Installation Guide](./installation.md) - Detailed installation instructions
- [Configuration Guide](./configuration.md) - System configuration and setup

### Core Features
- [URL Mapping Guide](./url-mapping.md) - Configure URL patterns and extractors
- [Crawler Setup Guide](./crawler-setup.md) - Create and manage crawlers
- [Data Extraction Guide](./data-extraction.md) - Configure LLM and CSS extractors
- [Scheduling Guide](./scheduling.md) - Set up automated crawling schedules

### Advanced Topics
- [Performance Optimization](./performance.md) - Optimize crawling performance
- [Custom Extractors](./custom-extractors.md) - Build custom data extractors
- [API Integration](./api-integration.md) - Integrate with external APIs
- [Monitoring & Alerts](./monitoring.md) - Set up monitoring and notifications

### Deployment
- [Docker Deployment](./docker-deployment.md) - Deploy using Docker containers
- [Production Setup](./production-setup.md) - Production deployment best practices
- [Scaling Guide](./scaling.md) - Scale your crawling infrastructure

### Troubleshooting
- [Common Issues](./troubleshooting.md) - Solutions to common problems
- [Debug Guide](./debugging.md) - Debug crawling issues
- [Performance Tuning](./performance-tuning.md) - Optimize system performance

## 🚀 Quick Start Example

Here's a complete example to get you started with the CRY-A-4MCP Enhanced Templates package:

### 1. Create a URL Mapping

```bash
# Create URL mapping for CoinMarketCap
curl -X POST http://localhost:4000/api/url-mappings \
  -H "Content-Type: application/json" \
  -d '{
    "url_pattern": "https://coinmarketcap.com/currencies/*",
    "profile": "Gem Hunter",
    "priority": 1,
    "scraping_difficulty": "Medium",
    "api_available": false,
    "cost_analysis": "High value crypto data"
  }'
```

### 2. Create an Extractor

```bash
# Create LLM extractor for crypto data
curl -X POST http://localhost:4000/api/extractors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Crypto Price Extractor",
    "type": "llm",
    "model": "gpt-3.5-turbo",
    "schema": {
      "name": "string",
      "symbol": "string",
      "price": "number",
      "market_cap": "number",
      "volume_24h": "number",
      "price_change_24h": "number"
    },
    "instructions": "Extract cryptocurrency data including name, symbol, current price, market cap, 24h volume, and 24h price change from the webpage."
  }'
```

### 3. Create a Crawler

```bash
# Create crawler using the URL mapping
curl -X POST http://localhost:4000/api/crawlers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bitcoin Price Monitor",
    "description": "Monitor Bitcoin price on CoinMarketCap",
    "urlMappingId": "your-url-mapping-id",
    "targetUrls": [
      "https://coinmarketcap.com/currencies/bitcoin/"
    ],
    "schedule": "0 */5 * * *"
  }'
```

### 4. Run the Crawler

```bash
# Start crawling
curl -X POST http://localhost:4000/api/crawlers/your-crawler-id/run
```

### 5. Get Results

```bash
# Check job status
curl http://localhost:4000/api/jobs/your-job-id

# Get extracted data
curl http://localhost:4000/api/jobs/your-job-id/results
```

## 🎯 Use Case Examples

### Cryptocurrency Price Monitoring

**Scenario**: Monitor cryptocurrency prices across multiple exchanges.

**Implementation**:
1. Create URL mappings for major exchanges (CoinMarketCap, CoinGecko, Binance)
2. Set up LLM extractors for price data
3. Create scheduled crawlers for each exchange
4. Set up alerts for significant price changes

**Benefits**:
- Real-time price monitoring
- Cross-exchange price comparison
- Automated alerts for trading opportunities

### DeFi Protocol Analysis

**Scenario**: Track DeFi protocol metrics and governance proposals.

**Implementation**:
1. Map DeFi protocol websites and documentation
2. Extract TVL, APY, and governance data
3. Monitor proposal voting and outcomes
4. Generate analytics reports

**Benefits**:
- Comprehensive DeFi ecosystem monitoring
- Investment decision support
- Risk assessment data

### NFT Market Intelligence

**Scenario**: Monitor NFT collections and marketplace trends.

**Implementation**:
1. Create mappings for NFT marketplaces (OpenSea, Blur, LooksRare)
2. Extract collection metrics, floor prices, and sales data
3. Track trending collections and whale activities
4. Generate market intelligence reports

**Benefits**:
- Market trend identification
- Investment opportunity discovery
- Portfolio performance tracking

### News and Social Sentiment

**Scenario**: Aggregate crypto news and social media sentiment.

**Implementation**:
1. Map crypto news websites and social platforms
2. Extract headlines, sentiment, and engagement metrics
3. Correlate news sentiment with price movements
4. Generate sentiment analysis reports

**Benefits**:
- Market sentiment tracking
- News-driven trading signals
- Social media influence analysis

## 🛠️ Integration Patterns

### Webhook Integration

```python
# Flask webhook receiver
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/crawler-results', methods=['POST'])
def handle_crawler_results():
    data = request.json
    
    # Process crawler results
    job_id = data['job_id']
    results = data['results']
    
    # Your business logic here
    process_crypto_data(results)
    
    return jsonify({'status': 'success'})

def process_crypto_data(results):
    for result in results:
        price_data = result['data']
        
        # Store in database
        save_price_data(price_data)
        
        # Check for alerts
        check_price_alerts(price_data)
        
        # Update dashboard
        update_dashboard(price_data)
```

### Database Integration

```python
# SQLAlchemy models for storing crawler data
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CryptoPriceData(Base):
    __tablename__ = 'crypto_prices'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    market_cap = Column(Float)
    volume_24h = Column(Float)
    price_change_24h = Column(Float)
    source_url = Column(String(500))
    extracted_at = Column(DateTime, nullable=False)
    raw_data = Column(JSON)
    
    def __repr__(self):
        return f'<CryptoPriceData {self.symbol}: ${self.price}>'

# Data processing function
def store_crawler_results(job_results):
    session = get_db_session()
    
    for result in job_results['results']:
        price_data = CryptoPriceData(
            symbol=result['data']['symbol'],
            name=result['data']['name'],
            price=result['data']['price'],
            market_cap=result['data'].get('market_cap'),
            volume_24h=result['data'].get('volume_24h'),
            price_change_24h=result['data'].get('price_change_24h'),
            source_url=result['url'],
            extracted_at=datetime.fromisoformat(result['extracted_at']),
            raw_data=result['data']
        )
        
        session.add(price_data)
    
    session.commit()
    session.close()
```

### Real-time Dashboard Integration

```javascript
// React component for real-time price dashboard
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const CryptoDashboard = () => {
  const [priceData, setPriceData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch initial data
    fetchPriceData();
    
    // Set up WebSocket for real-time updates
    const ws = new WebSocket('ws://localhost:4000/ws/price-updates');
    
    ws.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setPriceData(prev => [...prev.slice(-99), newData]); // Keep last 100 points
    };
    
    return () => ws.close();
  }, []);

  const fetchPriceData = async () => {
    try {
      const response = await fetch('/api/crypto-prices?limit=100');
      const data = await response.json();
      setPriceData(data.results);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch price data:', error);
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div>Loading price data...</div>;
  }

  return (
    <div className="crypto-dashboard">
      <h2>Real-time Crypto Prices</h2>
      
      <div className="price-grid">
        {priceData.slice(-10).map(item => (
          <div key={item.id} className="price-card">
            <h3>{item.symbol}</h3>
            <p className="price">${item.price.toLocaleString()}</p>
            <p className={`change ${item.price_change_24h >= 0 ? 'positive' : 'negative'}`}>
              {item.price_change_24h >= 0 ? '+' : ''}{item.price_change_24h.toFixed(2)}%
            </p>
          </div>
        ))}
      </div>
      
      <div className="price-chart">
        <LineChart width={800} height={400} data={priceData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="extracted_at" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="price" stroke="#8884d8" strokeWidth={2} />
        </LineChart>
      </div>
    </div>
  );
};

export default CryptoDashboard;
```

## 📊 Analytics and Reporting

### Custom Analytics Pipeline

```python
# Analytics pipeline for crawler data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CryptoAnalytics:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def generate_daily_report(self, date=None):
        """Generate daily analytics report."""
        if date is None:
            date = datetime.now().date()
        
        # Fetch data for the day
        query = """
        SELECT symbol, name, price, market_cap, volume_24h, price_change_24h, extracted_at
        FROM crypto_prices 
        WHERE DATE(extracted_at) = %s
        ORDER BY extracted_at
        """
        
        df = pd.read_sql(query, self.db, params=[date])
        
        if df.empty:
            return {"error": "No data available for the specified date"}
        
        # Calculate analytics
        analytics = {
            "date": date.isoformat(),
            "total_data_points": len(df),
            "unique_symbols": df['symbol'].nunique(),
            "price_summary": {
                "highest_price": {
                    "symbol": df.loc[df['price'].idxmax(), 'symbol'],
                    "price": df['price'].max()
                },
                "lowest_price": {
                    "symbol": df.loc[df['price'].idxmin(), 'symbol'],
                    "price": df['price'].min()
                },
                "avg_price": df['price'].mean()
            },
            "market_cap_summary": {
                "total_market_cap": df['market_cap'].sum(),
                "avg_market_cap": df['market_cap'].mean()
            },
            "volume_summary": {
                "total_volume": df['volume_24h'].sum(),
                "avg_volume": df['volume_24h'].mean()
            },
            "price_changes": {
                "biggest_gainer": {
                    "symbol": df.loc[df['price_change_24h'].idxmax(), 'symbol'],
                    "change": df['price_change_24h'].max()
                },
                "biggest_loser": {
                    "symbol": df.loc[df['price_change_24h'].idxmin(), 'symbol'],
                    "change": df['price_change_24h'].min()
                },
                "avg_change": df['price_change_24h'].mean()
            }
        }
        
        return analytics
    
    def detect_anomalies(self, symbol, lookback_days=7):
        """Detect price anomalies for a specific symbol."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        query = """
        SELECT price, extracted_at
        FROM crypto_prices 
        WHERE symbol = %s AND extracted_at BETWEEN %s AND %s
        ORDER BY extracted_at
        """
        
        df = pd.read_sql(query, self.db, params=[symbol, start_date, end_date])
        
        if len(df) < 10:
            return {"error": "Insufficient data for anomaly detection"}
        
        # Calculate rolling statistics
        df['rolling_mean'] = df['price'].rolling(window=24).mean()
        df['rolling_std'] = df['price'].rolling(window=24).std()
        
        # Detect anomalies (price > 2 standard deviations from mean)
        df['is_anomaly'] = abs(df['price'] - df['rolling_mean']) > (2 * df['rolling_std'])
        
        anomalies = df[df['is_anomaly']].to_dict('records')
        
        return {
            "symbol": symbol,
            "anomalies_count": len(anomalies),
            "anomalies": anomalies,
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": lookback_days
            }
        }
    
    def correlation_analysis(self, symbols, days=30):
        """Analyze price correlations between symbols."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch price data for all symbols
        query = """
        SELECT symbol, price, DATE(extracted_at) as date
        FROM crypto_prices 
        WHERE symbol IN %s AND extracted_at BETWEEN %s AND %s
        """
        
        df = pd.read_sql(query, self.db, params=[tuple(symbols), start_date, end_date])
        
        # Pivot to get symbols as columns
        pivot_df = df.pivot_table(index='date', columns='symbol', values='price', aggfunc='mean')
        
        # Calculate correlation matrix
        correlation_matrix = pivot_df.corr()
        
        return {
            "symbols": symbols,
            "correlation_matrix": correlation_matrix.to_dict(),
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "strongest_correlations": self._find_strongest_correlations(correlation_matrix)
        }
    
    def _find_strongest_correlations(self, corr_matrix):
        """Find the strongest positive and negative correlations."""
        # Remove self-correlations
        corr_matrix = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # Find strongest positive correlation
        max_corr = corr_matrix.max().max()
        max_pair = corr_matrix.stack().idxmax()
        
        # Find strongest negative correlation
        min_corr = corr_matrix.min().min()
        min_pair = corr_matrix.stack().idxmin()
        
        return {
            "strongest_positive": {
                "symbols": list(max_pair),
                "correlation": max_corr
            },
            "strongest_negative": {
                "symbols": list(min_pair),
                "correlation": min_corr
            }
        }

# Usage example
analytics = CryptoAnalytics(db_connection)

# Generate daily report
daily_report = analytics.generate_daily_report()
print(f"Daily Report: {daily_report}")

# Detect anomalies for Bitcoin
btc_anomalies = analytics.detect_anomalies('BTC')
print(f"Bitcoin Anomalies: {btc_anomalies}")

# Analyze correlations between major cryptocurrencies
correlations = analytics.correlation_analysis(['BTC', 'ETH', 'ADA', 'SOL'])
print(f"Correlations: {correlations}")
```

## 🔔 Alert System

### Price Alert Implementation

```python
# Alert system for price monitoring
from dataclasses import dataclass
from typing import List, Callable
from enum import Enum

class AlertType(Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_CHANGE = "price_change"
    VOLUME_SPIKE = "volume_spike"
    ANOMALY_DETECTED = "anomaly_detected"

@dataclass
class Alert:
    id: str
    symbol: str
    alert_type: AlertType
    threshold: float
    is_active: bool = True
    notification_channels: List[str] = None

class AlertManager:
    def __init__(self):
        self.alerts = {}
        self.notification_handlers = {}
    
    def register_notification_handler(self, channel: str, handler: Callable):
        """Register a notification handler for a specific channel."""
        self.notification_handlers[channel] = handler
    
    def create_alert(self, alert: Alert):
        """Create a new price alert."""
        self.alerts[alert.id] = alert
        return alert.id
    
    def check_alerts(self, price_data):
        """Check all active alerts against new price data."""
        triggered_alerts = []
        
        for alert in self.alerts.values():
            if not alert.is_active:
                continue
            
            if self._should_trigger_alert(alert, price_data):
                triggered_alerts.append(alert)
                self._send_notifications(alert, price_data)
        
        return triggered_alerts
    
    def _should_trigger_alert(self, alert: Alert, price_data) -> bool:
        """Check if an alert should be triggered."""
        symbol_data = next((item for item in price_data if item['symbol'] == alert.symbol), None)
        
        if not symbol_data:
            return False
        
        if alert.alert_type == AlertType.PRICE_ABOVE:
            return symbol_data['price'] > alert.threshold
        elif alert.alert_type == AlertType.PRICE_BELOW:
            return symbol_data['price'] < alert.threshold
        elif alert.alert_type == AlertType.PRICE_CHANGE:
            return abs(symbol_data.get('price_change_24h', 0)) > alert.threshold
        elif alert.alert_type == AlertType.VOLUME_SPIKE:
            # Implement volume spike detection logic
            return self._detect_volume_spike(symbol_data, alert.threshold)
        
        return False
    
    def _detect_volume_spike(self, symbol_data, threshold) -> bool:
        """Detect if there's a volume spike."""
        # This would typically compare current volume to historical average
        # For simplicity, we'll use a basic threshold check
        current_volume = symbol_data.get('volume_24h', 0)
        return current_volume > threshold
    
    def _send_notifications(self, alert: Alert, price_data):
        """Send notifications for triggered alert."""
        symbol_data = next((item for item in price_data if item['symbol'] == alert.symbol), None)
        
        message = self._format_alert_message(alert, symbol_data)
        
        channels = alert.notification_channels or ['console']
        
        for channel in channels:
            if channel in self.notification_handlers:
                self.notification_handlers[channel](message, alert, symbol_data)
    
    def _format_alert_message(self, alert: Alert, symbol_data) -> str:
        """Format alert message."""
        if alert.alert_type == AlertType.PRICE_ABOVE:
            return f"🚨 {alert.symbol} price is above ${alert.threshold:,.2f}! Current price: ${symbol_data['price']:,.2f}"
        elif alert.alert_type == AlertType.PRICE_BELOW:
            return f"📉 {alert.symbol} price is below ${alert.threshold:,.2f}! Current price: ${symbol_data['price']:,.2f}"
        elif alert.alert_type == AlertType.PRICE_CHANGE:
            change = symbol_data.get('price_change_24h', 0)
            return f"📊 {alert.symbol} price changed by {change:+.2f}% (threshold: {alert.threshold}%)"
        elif alert.alert_type == AlertType.VOLUME_SPIKE:
            volume = symbol_data.get('volume_24h', 0)
            return f"📈 {alert.symbol} volume spike detected! Current volume: ${volume:,.0f}"
        
        return f"Alert triggered for {alert.symbol}"

# Notification handlers
def console_notification_handler(message: str, alert: Alert, data: dict):
    """Print notification to console."""
    print(f"[{datetime.now()}] {message}")

def slack_notification_handler(message: str, alert: Alert, data: dict):
    """Send notification to Slack."""
    import requests
    
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        return
    
    payload = {
        "text": message,
        "attachments": [{
            "color": "warning" if alert.alert_type in [AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW] else "good",
            "fields": [
                {"title": "Symbol", "value": alert.symbol, "short": True},
                {"title": "Price", "value": f"${data['price']:,.2f}", "short": True},
                {"title": "24h Change", "value": f"{data.get('price_change_24h', 0):+.2f}%", "short": True},
                {"title": "Market Cap", "value": f"${data.get('market_cap', 0):,.0f}", "short": True}
            ]
        }]
    }
    
    requests.post(webhook_url, json=payload)

def email_notification_handler(message: str, alert: Alert, data: dict):
    """Send email notification."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Email configuration (use environment variables)
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    recipient_email = os.getenv('ALERT_EMAIL')
    
    if not all([smtp_server, smtp_username, smtp_password, recipient_email]):
        return
    
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = recipient_email
    msg['Subject'] = f"CRY-A-4MCP Alert: {alert.symbol}"
    
    body = f"""
    {message}
    
    Alert Details:
    - Symbol: {alert.symbol}
    - Alert Type: {alert.alert_type.value}
    - Threshold: {alert.threshold}
    - Current Price: ${data['price']:,.2f}
    - 24h Change: {data.get('price_change_24h', 0):+.2f}%
    - Market Cap: ${data.get('market_cap', 0):,.0f}
    - Volume 24h: ${data.get('volume_24h', 0):,.0f}
    
    Timestamp: {datetime.now()}
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email notification: {e}")

# Usage example
alert_manager = AlertManager()

# Register notification handlers
alert_manager.register_notification_handler('console', console_notification_handler)
alert_manager.register_notification_handler('slack', slack_notification_handler)
alert_manager.register_notification_handler('email', email_notification_handler)

# Create alerts
btc_high_alert = Alert(
    id="btc_high_50k",
    symbol="BTC",
    alert_type=AlertType.PRICE_ABOVE,
    threshold=50000,
    notification_channels=['console', 'slack', 'email']
)

eth_change_alert = Alert(
    id="eth_change_10pct",
    symbol="ETH",
    alert_type=AlertType.PRICE_CHANGE,
    threshold=10,  # 10% change
    notification_channels=['slack']
)

alert_manager.create_alert(btc_high_alert)
alert_manager.create_alert(eth_change_alert)

# Check alerts when new price data arrives
def process_new_price_data(price_data):
    # Store data in database
    store_crawler_results({'results': price_data})
    
    # Check alerts
    triggered_alerts = alert_manager.check_alerts(price_data)
    
    if triggered_alerts:
        print(f"Triggered {len(triggered_alerts)} alerts")
    
    return triggered_alerts
```

---

**Next Steps**: Explore specific guides for detailed implementation instructions:
- [Quick Start Guide](./quick-start.md) for immediate setup
- [URL Mapping Guide](./url-mapping.md) for configuration details
- [API Integration Guide](./api-integration.md) for programmatic access