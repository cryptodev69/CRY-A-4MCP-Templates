# CRY-A-4MCP Starter MCP Server

## Overview

This is a starter MCP (Multi-Context Protocol) server for the CRY-A-4MCP platform, a comprehensive cryptocurrency analysis and information retrieval system. The server provides tools for cryptocurrency data retrieval, analysis, and knowledge graph exploration.

## Features

### Hybrid Search Engine

The hybrid search engine combines vector similarity search and knowledge graph traversal to provide comprehensive and contextually relevant search results for cryptocurrency queries.

- **Vector Search**: Utilizes Qdrant for semantic similarity search based on embeddings
- **Knowledge Graph**: Leverages Neo4j for entity relationship exploration
- **Hybrid Mode**: Intelligently combines results from both approaches
- **Auto Mode**: Automatically selects the best search strategy based on query characteristics

### Cryptocurrency Analysis

Provides comprehensive cryptocurrency analysis capabilities:

- **Market Data**: Price, volume, market cap, and price changes
- **Technical Analysis**: RSI, moving averages, MACD, and Bollinger Bands
- **Sentiment Analysis**: Social media and news sentiment scoring
- **Risk Assessment**: Volatility, liquidity, and overall risk evaluation

### Knowledge Graph Management

Manages a comprehensive knowledge graph of cryptocurrency entities and their relationships:

- **Entity Types**: Cryptocurrencies, exchanges, people, organizations, technologies, events, and concepts
- **Relationship Types**: Trading relationships, founding relationships, development relationships, and more
- **Path Finding**: Discover connections between entities
- **Entity Search**: Find entities by name or properties

## Architecture

The server is organized into several modules:

- **retrieval**: Hybrid search engine implementation
- **processing**: Cryptocurrency analysis tools
- **storage**: Vector store and knowledge graph management
- **mcp_server**: MCP server implementation
- **tools**: MCP tools implementation

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Neo4j database
- Qdrant vector database

### Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables (see `.env.example`)
4. Start the required services using Docker Compose:

```bash
cd ../docker-stack
./start.sh
```

5. Run the server:

```bash
python -m cry_a_4mcp.server
```

## MCP Tools

### HybridSearchTool

Performs hybrid search combining vector similarity and knowledge graph traversal.

**Input Schema:**
- `query`: Search query string
- `search_mode`: Search mode (hybrid, vector_only, graph_only, auto)
- `max_results`: Maximum number of results to return
- `include_sources`: Whether to include source information
- `confidence_threshold`: Minimum confidence score for results

### AnalyzeCryptoTool

Performs cryptocurrency analysis.

**Input Schema:**
- `symbol`: Cryptocurrency symbol (e.g., BTC, ETH)
- `analysis_type`: Type of analysis (comprehensive, technical, fundamental, sentiment)
- `days_back`: Number of days of historical data to analyze

### CrawlWebsiteTool

Crawls cryptocurrency websites for information.

**Input Schema:**
- `url`: URL to crawl
- `content_type`: Type of content to extract
- `extract_entities`: Whether to extract entities
- `generate_triples`: Whether to generate knowledge graph triples

## Development

### Adding New Tools

To add a new tool:

1. Create a new class in `tools.py` that inherits from `BaseTool`
2. Implement the required methods: `_initialize_impl` and `_execute_impl`
3. Define the tool's name, description, and input schema

### Testing

Run tests using pytest:

```bash
python -m pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.