# Adding New Data Sources to CRY-A-4MCP

This guide provides step-by-step instructions for extending the CRY-A-4MCP system with new data sources.

## 🎯 Overview

The CRY-A-4MCP system is designed to be extensible. You can add new data sources by:

1. **Creating a data source connector** - Interface with external APIs or services
2. **Implementing data processing** - Transform raw data into system format
3. **Integrating with storage** - Store processed data in vector and graph databases
4. **Adding MCP tools** - Expose new functionality via MCP protocol
5. **Testing and validation** - Ensure quality and performance

## 📋 Prerequisites

Before adding a new data source:

- [ ] CRY-A-4MCP system is running and healthy
- [ ] You have access to the target data source (API keys, documentation)
- [ ] Python development environment is set up
- [ ] Understanding of the data source's format and limitations

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Source   │───▶│   Connector     │───▶│   Processor     │
│   (External)    │    │   (Your Code)   │    │   (Transform)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Tools     │◀───│   Storage       │◀───│   Validation    │
│   (API Access)  │    │   (Qdrant+Neo4j)│    │   (Quality)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Step 1: Create Data Source Connector

### 1.1 Create Connector Module

Create a new file: `src/cry_a_4mcp/connectors/your_source.py`

```python
"""
Connector for [Your Data Source Name]
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from ..utils.logging import get_logger
from ..utils.rate_limiter import RateLimiter
from .base_connector import BaseConnector

logger = get_logger(__name__)

class YourSourceConfig(BaseModel):
    """Configuration for your data source"""
    api_key: str = Field(..., description="API key for authentication")
    base_url: str = Field(default="https://api.yoursource.com", description="Base API URL")
    rate_limit: int = Field(default=100, description="Requests per minute")
    timeout: int = Field(default=30, description="Request timeout in seconds")

class YourSourceData(BaseModel):
    """Data model for your source"""
    id: str
    title: str
    content: str
    timestamp: datetime
    source_url: str
    metadata: Dict = Field(default_factory=dict)

class YourSourceConnector(BaseConnector):
    """Connector for [Your Data Source Name]"""
    
    def __init__(self, config: YourSourceConfig):
        super().__init__()
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit, 60)  # per minute
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "User-Agent": "CRY-A-4MCP/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_data(
        self, 
        query: str, 
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> AsyncGenerator[YourSourceData, None]:
        """
        Fetch data from your source
        
        Args:
            query: Search query or filter
            limit: Maximum number of items to fetch
            since: Fetch items newer than this timestamp
        
        Yields:
            YourSourceData: Individual data items
        """
        if not self.session:
            raise RuntimeError("Connector not initialized. Use async context manager.")
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Build API request
        params = {
            "q": query,
            "limit": min(limit, 100),  # API limit
            "format": "json"
        }
        
        if since:
            params["since"] = since.isoformat()
        
        try:
            async with self.session.get(
                f"{self.config.base_url}/search",
                params=params
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Process each item
                for item in data.get("results", []):
                    yield YourSourceData(
                        id=item["id"],
                        title=item["title"],
                        content=item["content"],
                        timestamp=datetime.fromisoformat(item["created_at"]),
                        source_url=item["url"],
                        metadata={
                            "author": item.get("author"),
                            "tags": item.get("tags", []),
                            "score": item.get("relevance_score")
                        }
                    )
                    
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if the data source is accessible"""
        try:
            if not self.session:
                return False
                
            async with self.session.get(f"{self.config.base_url}/health") as response:
                return response.status == 200
        except:
            return False
```

### 1.2 Create Base Connector Interface

Create: `src/cry_a_4mcp/connectors/base_connector.py`

```python
"""
Base connector interface for data sources
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any, Dict, Optional
from datetime import datetime

class BaseConnector(ABC):
    """Base class for all data source connectors"""
    
    @abstractmethod
    async def fetch_data(
        self, 
        query: str, 
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> AsyncGenerator[Any, None]:
        """Fetch data from the source"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the data source is healthy"""
        pass
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass
```

## 🔄 Step 2: Implement Data Processing

### 2.1 Create Data Processor

Create: `src/cry_a_4mcp/processing/your_source_processor.py`

```python
"""
Data processor for [Your Data Source Name]
"""

import asyncio
from typing import List, Dict, Tuple
from datetime import datetime

from ..connectors.your_source import YourSourceData
from ..utils.text_processing import clean_text, extract_entities
from ..utils.crypto_entities import CryptoEntityExtractor
from .base_processor import BaseProcessor

class YourSourceProcessor(BaseProcessor):
    """Process data from your source for CRY-A-4MCP system"""
    
    def __init__(self):
        super().__init__()
        self.entity_extractor = CryptoEntityExtractor()
    
    async def process_item(self, item: YourSourceData) -> Dict:
        """
        Process a single data item
        
        Args:
            item: Raw data from your source
            
        Returns:
            Dict: Processed data ready for storage
        """
        # Clean and normalize text
        cleaned_content = clean_text(item.content)
        cleaned_title = clean_text(item.title)
        
        # Extract cryptocurrency entities
        entities = await self.entity_extractor.extract(
            text=f"{cleaned_title} {cleaned_content}",
            source="your_source"
        )
        
        # Generate embeddings for vector search
        embedding = await self.generate_embedding(
            text=f"{cleaned_title} {cleaned_content}"
        )
        
        # Extract relationships for knowledge graph
        relationships = await self.extract_relationships(
            text=cleaned_content,
            entities=entities
        )
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(item, entities)
        
        return {
            # Original data
            "id": f"your_source_{item.id}",
            "title": cleaned_title,
            "content": cleaned_content,
            "timestamp": item.timestamp,
            "source_url": item.source_url,
            "source_type": "your_source",
            
            # Processed data
            "entities": entities,
            "relationships": relationships,
            "embedding": embedding,
            "quality_score": quality_score,
            
            # Metadata
            "metadata": {
                **item.metadata,
                "processed_at": datetime.utcnow(),
                "processor_version": "1.0"
            }
        }
    
    def calculate_quality_score(
        self, 
        item: YourSourceData, 
        entities: List[Dict]
    ) -> float:
        """Calculate quality score for the item"""
        score = 0.5  # Base score
        
        # Content length bonus
        if len(item.content) > 100:
            score += 0.1
        if len(item.content) > 500:
            score += 0.1
        
        # Entity detection bonus
        crypto_entities = [e for e in entities if e.get("type") == "cryptocurrency"]
        if crypto_entities:
            score += min(0.3, len(crypto_entities) * 0.1)
        
        # Recency bonus
        age_hours = (datetime.utcnow() - item.timestamp).total_seconds() / 3600
        if age_hours < 24:
            score += 0.1
        
        # Source-specific scoring
        if item.metadata.get("score"):
            score += min(0.2, item.metadata["score"] / 10)
        
        return min(1.0, score)
    
    async def extract_relationships(
        self, 
        text: str, 
        entities: List[Dict]
    ) -> List[Dict]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple relationship extraction
        # You can implement more sophisticated NLP here
        
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Check if entities appear close together in text
                pos1 = text.lower().find(entity1["text"].lower())
                pos2 = text.lower().find(entity2["text"].lower())
                
                if pos1 != -1 and pos2 != -1 and abs(pos1 - pos2) < 100:
                    relationships.append({
                        "source": entity1["text"],
                        "target": entity2["text"],
                        "type": "mentioned_together",
                        "confidence": 0.7,
                        "context": text[min(pos1, pos2):max(pos1, pos2) + 50]
                    })
        
        return relationships
```

## 💾 Step 3: Integrate with Storage

### 3.1 Update Storage Manager

Add to: `src/cry_a_4mcp/storage/storage_manager.py`

```python
async def store_your_source_data(self, processed_data: Dict) -> bool:
    """Store processed data from your source"""
    try:
        # Store in vector database (Qdrant)
        await self.vector_store.upsert(
            collection_name="your_source_embeddings",
            points=[{
                "id": processed_data["id"],
                "vector": processed_data["embedding"],
                "payload": {
                    "title": processed_data["title"],
                    "content": processed_data["content"][:1000],  # Truncate for payload
                    "timestamp": processed_data["timestamp"].isoformat(),
                    "source_url": processed_data["source_url"],
                    "quality_score": processed_data["quality_score"],
                    "entities": [e["text"] for e in processed_data["entities"]]
                }
            }]
        )
        
        # Store in knowledge graph (Neo4j)
        await self.graph_store.create_nodes_and_relationships(
            nodes=[
                {
                    "id": processed_data["id"],
                    "type": "YourSourceItem",
                    "properties": {
                        "title": processed_data["title"],
                        "timestamp": processed_data["timestamp"].isoformat(),
                        "source_url": processed_data["source_url"],
                        "quality_score": processed_data["quality_score"]
                    }
                }
            ] + [
                {
                    "id": f"entity_{entity['text']}",
                    "type": entity["type"],
                    "properties": {
                        "name": entity["text"],
                        "confidence": entity.get("confidence", 0.8)
                    }
                }
                for entity in processed_data["entities"]
            ],
            relationships=[
                {
                    "source": processed_data["id"],
                    "target": f"entity_{entity['text']}",
                    "type": "MENTIONS",
                    "properties": {
                        "confidence": entity.get("confidence", 0.8)
                    }
                }
                for entity in processed_data["entities"]
            ] + processed_data["relationships"]
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to store data: {e}")
        return False
```

## 🛠️ Step 4: Add MCP Tools

### 4.1 Create MCP Tool

Create: `src/cry_a_4mcp/mcp_server/tools/your_source_tool.py`

```python
"""
MCP tool for accessing your data source
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..base_tool import BaseTool
from ...connectors.your_source import YourSourceConnector, YourSourceConfig
from ...processing.your_source_processor import YourSourceProcessor
from ...storage.storage_manager import StorageManager

class YourSourceTool(BaseTool):
    """MCP tool for your data source"""
    
    name = "your_source_search"
    description = "Search and analyze data from [Your Data Source Name]"
    
    def __init__(self, config: YourSourceConfig):
        super().__init__()
        self.config = config
        self.processor = YourSourceProcessor()
        self.storage = StorageManager()
    
    async def execute(
        self,
        query: str,
        limit: int = 10,
        days_back: int = 7,
        include_analysis: bool = True
    ) -> Dict:
        """
        Execute search on your data source
        
        Args:
            query: Search query
            limit: Maximum results to return
            days_back: How many days back to search
            include_analysis: Whether to include entity analysis
            
        Returns:
            Dict: Search results with analysis
        """
        try:
            since = datetime.utcnow() - timedelta(days=days_back)
            results = []
            
            # Fetch data from source
            async with YourSourceConnector(self.config) as connector:
                async for item in connector.fetch_data(
                    query=query,
                    limit=limit,
                    since=since
                ):
                    # Process the item
                    processed = await self.processor.process_item(item)
                    
                    # Store in databases
                    await self.storage.store_your_source_data(processed)
                    
                    # Prepare result
                    result = {
                        "id": processed["id"],
                        "title": processed["title"],
                        "content": processed["content"][:500] + "..." if len(processed["content"]) > 500 else processed["content"],
                        "timestamp": processed["timestamp"].isoformat(),
                        "source_url": processed["source_url"],
                        "quality_score": processed["quality_score"]
                    }
                    
                    if include_analysis:
                        result["entities"] = processed["entities"]
                        result["relationships"] = processed["relationships"]
                    
                    results.append(result)
            
            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": results,
                "metadata": {
                    "search_timestamp": datetime.utcnow().isoformat(),
                    "days_searched": days_back,
                    "source": "your_source"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
```

### 4.2 Register Tool in MCP Server

Add to: `src/cry_a_4mcp/mcp_server/server.py`

```python
from .tools.your_source_tool import YourSourceTool
from ..connectors.your_source import YourSourceConfig

# In the server initialization
your_source_config = YourSourceConfig(
    api_key=os.getenv("YOUR_SOURCE_API_KEY"),
    rate_limit=int(os.getenv("YOUR_SOURCE_RATE_LIMIT", "100"))
)

your_source_tool = YourSourceTool(your_source_config)
server.register_tool(your_source_tool)
```

## 🧪 Step 5: Testing and Validation

### 5.1 Create Unit Tests

Create: `tests/unit/test_your_source_connector.py`

```python
"""
Unit tests for your source connector
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.cry_a_4mcp.connectors.your_source import (
    YourSourceConnector,
    YourSourceConfig,
    YourSourceData
)

@pytest.fixture
def config():
    return YourSourceConfig(
        api_key="test_key",
        base_url="https://api.test.com"
    )

@pytest.fixture
def connector(config):
    return YourSourceConnector(config)

@pytest.mark.asyncio
async def test_fetch_data(connector):
    """Test data fetching"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        # Mock API response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "test_1",
                    "title": "Test Bitcoin News",
                    "content": "Bitcoin price analysis...",
                    "created_at": "2024-01-01T00:00:00Z",
                    "url": "https://test.com/news/1",
                    "author": "Test Author",
                    "tags": ["bitcoin", "analysis"]
                }
            ]
        }
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with connector:
            results = []
            async for item in connector.fetch_data("bitcoin", limit=10):
                results.append(item)
        
        assert len(results) == 1
        assert results[0].title == "Test Bitcoin News"
        assert "bitcoin" in results[0].metadata["tags"]

@pytest.mark.asyncio
async def test_health_check(connector):
    """Test health check"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with connector:
            health = await connector.health_check()
        
        assert health is True
```

### 5.2 Create Integration Tests

Create: `tests/integration/test_your_source_integration.py`

```python
"""
Integration tests for your source
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from src.cry_a_4mcp.connectors.your_source import YourSourceConnector, YourSourceConfig
from src.cry_a_4mcp.processing.your_source_processor import YourSourceProcessor
from src.cry_a_4mcp.mcp_server.tools.your_source_tool import YourSourceTool

@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_flow():
    """Test complete flow from connector to storage"""
    # This test requires actual API credentials
    # Skip if not available
    api_key = os.getenv("YOUR_SOURCE_API_KEY")
    if not api_key:
        pytest.skip("API key not available")
    
    config = YourSourceConfig(api_key=api_key)
    tool = YourSourceTool(config)
    
    # Execute search
    result = await tool.execute(
        query="bitcoin",
        limit=5,
        days_back=1
    )
    
    assert result["success"] is True
    assert result["results_count"] > 0
    assert all("entities" in r for r in result["results"])
```

### 5.3 Performance Testing

Create: `tests/performance/test_your_source_performance.py`

```python
"""
Performance tests for your source
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from src.cry_a_4mcp.mcp_server.tools.your_source_tool import YourSourceTool

@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test concurrent request handling"""
    tool = YourSourceTool(config)
    
    async def make_request():
        start_time = time.time()
        result = await tool.execute("bitcoin", limit=5)
        end_time = time.time()
        return end_time - start_time, result["success"]
    
    # Run 10 concurrent requests
    tasks = [make_request() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    # Check all succeeded
    assert all(success for _, success in results)
    
    # Check average response time
    avg_time = sum(duration for duration, _ in results) / len(results)
    assert avg_time < 2.0  # Should be under 2 seconds
```

## 📚 Step 6: Documentation

### 6.1 Update API Documentation

Add to your MCP tool docstring:

```python
class YourSourceTool(BaseTool):
    """
    MCP tool for accessing [Your Data Source Name]
    
    This tool provides access to [description of your data source] with the following capabilities:
    - Real-time data fetching
    - Cryptocurrency entity extraction
    - Quality scoring and filtering
    - Integration with vector and graph databases
    
    Usage Examples:
    
    Basic search:
    ```
    {
        "tool": "your_source_search",
        "arguments": {
            "query": "bitcoin price analysis",
            "limit": 10
        }
    }
    ```
    
    Advanced search with analysis:
    ```
    {
        "tool": "your_source_search", 
        "arguments": {
            "query": "ethereum defi",
            "limit": 20,
            "days_back": 3,
            "include_analysis": true
        }
    }
    ```
    
    Response Format:
    ```json
    {
        "success": true,
        "query": "bitcoin",
        "results_count": 5,
        "results": [
            {
                "id": "your_source_123",
                "title": "Bitcoin Analysis",
                "content": "Content preview...",
                "timestamp": "2024-01-01T00:00:00Z",
                "source_url": "https://source.com/article",
                "quality_score": 0.85,
                "entities": [...],
                "relationships": [...]
            }
        ]
    }
    ```
    """
```

### 6.2 Create Usage Guide

Create: `docs/data_sources/your_source.md`

```markdown
# [Your Data Source Name] Integration

## Overview

This integration provides access to [description] through the CRY-A-4MCP system.

## Setup

1. **Get API Key**: Obtain API key from [source website]
2. **Configure Environment**: Add to `.env` file:
   ```bash
   YOUR_SOURCE_API_KEY=your_api_key_here
   YOUR_SOURCE_RATE_LIMIT=100
   ```
3. **Restart Services**: Restart MCP server to load new configuration

## Usage

### Via MCP Tool

```python
# Search for recent Bitcoin news
result = await mcp_client.call_tool(
    "your_source_search",
    {
        "query": "bitcoin",
        "limit": 10,
        "days_back": 7
    }
)
```

### Direct Connector Usage

```python
from cry_a_4mcp.connectors.your_source import YourSourceConnector, YourSourceConfig

config = YourSourceConfig(api_key="your_key")

async with YourSourceConnector(config) as connector:
    async for item in connector.fetch_data("ethereum", limit=50):
        print(f"Found: {item.title}")
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `api_key` | Required | API authentication key |
| `base_url` | `https://api.yoursource.com` | API base URL |
| `rate_limit` | 100 | Requests per minute |
| `timeout` | 30 | Request timeout in seconds |

## Data Quality

The integration includes quality scoring based on:
- Content length and depth
- Cryptocurrency entity detection
- Recency of information
- Source-specific relevance scores

Quality scores range from 0.0 to 1.0, with higher scores indicating better quality.

## Troubleshooting

### Common Issues

1. **API Key Invalid**
   - Verify key is correct in `.env` file
   - Check key hasn't expired
   - Ensure proper permissions

2. **Rate Limiting**
   - Reduce `rate_limit` in configuration
   - Implement exponential backoff
   - Consider upgrading API plan

3. **No Results**
   - Check query formatting
   - Verify data source has recent content
   - Review search parameters

### Monitoring

Monitor your integration using:
- Health check endpoint: `/health`
- Grafana dashboards for performance metrics
- Log files for error tracking

## Performance

Expected performance characteristics:
- **Response Time**: < 2 seconds for typical queries
- **Throughput**: Up to 100 requests/minute (API dependent)
- **Concurrent Users**: 10+ simultaneous queries
- **Data Freshness**: Real-time to 5 minutes delay
```

## 🚀 Step 7: Deployment

### 7.1 Update Docker Configuration

Add to `docker-compose.yml`:

```yaml
services:
  mcp-server:
    environment:
      - YOUR_SOURCE_API_KEY=${YOUR_SOURCE_API_KEY}
      - YOUR_SOURCE_RATE_LIMIT=${YOUR_SOURCE_RATE_LIMIT:-100}
```

### 7.2 Update Health Checks

Add to `scripts/health_check.sh`:

```bash
check_your_source() {
    echo -n "Checking Your Source integration... "
    
    # Test API connectivity
    if curl -s "$MCP_SERVER_URL/tools/your_source_search/health" | grep -q "ok"; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC} - Integration not responding"
        return 1
    fi
}

# Add to main health check function
check_your_source || exit_code=$?
```

## 📋 Checklist

Before deploying your new data source integration:

### Development
- [ ] Connector implements `BaseConnector` interface
- [ ] Data processor handles entity extraction
- [ ] Storage integration works with both Qdrant and Neo4j
- [ ] MCP tool follows protocol specifications
- [ ] Error handling is comprehensive

### Testing
- [ ] Unit tests cover all components
- [ ] Integration tests validate end-to-end flow
- [ ] Performance tests meet requirements
- [ ] Health checks work correctly
- [ ] Rate limiting is properly implemented

### Documentation
- [ ] API documentation is complete
- [ ] Usage examples are provided
- [ ] Configuration options are documented
- [ ] Troubleshooting guide is available
- [ ] Performance characteristics are specified

### Deployment
- [ ] Environment variables are configured
- [ ] Docker configuration is updated
- [ ] Health checks include new integration
- [ ] Monitoring dashboards are updated
- [ ] Backup procedures include new data

## 🎉 Success!

Your new data source is now integrated into the CRY-A-4MCP system! Users can access it via:

- **MCP Tools**: Direct API access through MCP protocol
- **Hybrid Search**: Automatic inclusion in search results
- **Knowledge Graph**: Entity relationships in Neo4j
- **Vector Search**: Semantic search through Qdrant
- **Monitoring**: Health and performance tracking

For additional help or advanced customization, refer to the main CRY-A-4MCP documentation or create an issue in the project repository.
