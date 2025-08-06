# CRY-A-4MCP Sample Data Sets

This directory contains realistic sample data for testing and development of the CRY-A-4MCP cryptocurrency analysis system. The data is designed to be representative of real-world cryptocurrency information while being safe for development and testing purposes.

## Data Categories

### 1. Market Data (`market_data/`)
- **Price Data**: Historical and real-time price information for major cryptocurrencies
- **Volume Data**: Trading volume across different exchanges and time periods
- **Liquidity Data**: Order book depth and liquidity metrics
- **Technical Indicators**: Pre-calculated technical analysis indicators

### 2. News and Articles (`news_articles/`)
- **Cryptocurrency News**: Sample news articles from major crypto publications
- **Market Analysis**: Technical and fundamental analysis articles
- **Regulatory News**: Regulatory developments and compliance updates
- **Protocol Updates**: Information about blockchain protocol upgrades

### 3. Social Media Content (`social_media/`)
- **Twitter/X Posts**: Sample tweets about cryptocurrency topics
- **Reddit Posts**: Sample posts from cryptocurrency subreddits
- **Discord Messages**: Sample messages from crypto community channels
- **Telegram Messages**: Sample messages from crypto announcement channels

### 4. Entity Relationships (`entities/`)
- **Tokens**: Information about various cryptocurrencies and tokens
- **Exchanges**: Data about cryptocurrency exchanges
- **Protocols**: Information about DeFi protocols and blockchain networks
- **People**: Key figures in the cryptocurrency space
- **Organizations**: Companies and organizations in the crypto ecosystem

### 5. Knowledge Graph Triples (`knowledge_graph/`)
- **Entity Relationships**: Pre-defined relationships between crypto entities
- **Temporal Relationships**: Time-based relationships and events
- **Hierarchical Relationships**: Parent-child relationships in crypto ecosystems

### 6. Crawled Content (`crawled_content/`)
- **Website Snapshots**: Sample crawled content from crypto websites
- **API Responses**: Sample responses from cryptocurrency APIs
- **Structured Data**: Extracted structured data from various sources

## Data Format

All sample data follows consistent formatting:

- **JSON**: Structured data and API responses
- **CSV**: Tabular data like price histories and metrics
- **Markdown**: Text content and articles
- **JSONL**: Streaming data and logs

## Usage

### Loading Sample Data

```python
from cry_a_4mcp.utils.sample_data import SampleDataLoader

# Load all sample data
loader = SampleDataLoader()
data = loader.load_all()

# Load specific data types
market_data = loader.load_market_data()
news_articles = loader.load_news_articles()
entities = loader.load_entities()
```

### Testing with Sample Data

```python
# Use sample data in tests
from cry_a_4mcp.testing.fixtures import sample_market_data

def test_price_analysis():
    data = sample_market_data("BTC", "1d", 30)
    # Your test code here
```

### Development Environment

The Docker stack automatically loads sample data into the appropriate services:

- **Qdrant**: Pre-populated with embedded news articles and content
- **Neo4j**: Pre-loaded with entity relationships and knowledge graph
- **Redis**: Cached market data and API responses

## Data Sources

All sample data is either:
- **Synthetic**: Generated using realistic patterns and distributions
- **Historical**: Based on historical public data with anonymization
- **Simulated**: Created to represent realistic scenarios

**Note**: This data is for development and testing only. Do not use for actual trading or financial decisions.

## Updating Sample Data

To add new sample data:

1. Follow the existing format and structure
2. Update the data loader utilities
3. Add appropriate test fixtures
4. Update this documentation

## Data Privacy

All sample data has been anonymized and does not contain:
- Real user information
- Actual trading positions
- Proprietary trading strategies
- Sensitive financial data

