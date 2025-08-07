# API Documentation
## CRY-A-4MCP: Cryptocurrency AI Analysis Platform

**Base URL**: `http://localhost:4000`  
**API Version**: v1  
**Backend File**: `web_api.py`  
**Port**: 4000

## Authentication

### Overview
The API uses Supabase-based authentication with JWT tokens. All protected endpoints require a valid Bearer token in the Authorization header.

```http
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "analyst"
  }
}
```

## Core Crawling API

### Regular Crawl
Execute web crawling with standard extraction methods.

```http
POST /api/crawl
Content-Type: application/json
Authorization: Bearer <token>

{
  "url": "https://example.com",
  "css_selector": ".content",
  "wait_for": "#main-content",
  "extraction_strategy": "regular",
  "options": {
    "timeout": 30,
    "user_agent": "CRY-A-4MCP/1.0"
  }
}
```

**Response**:
```json
{
  "success": true,
  "job_id": "uuid",
  "data": {
    "url": "https://example.com",
    "title": "Page Title",
    "content": "Extracted content...",
    "metadata": {
      "word_count": 1250,
      "extraction_time": "2025-01-20T10:30:00Z",
      "content_type": "text/html"
    }
  },
  "metrics": {
    "response_time_ms": 1500,
    "content_size_bytes": 45000,
    "quality_score": 0.95
  }
}
```

### LLM-Enhanced Crawl
Execute web crawling with AI-powered content extraction and analysis.

```http
POST /api/crawl-llm
Content-Type: application/json
Authorization: Bearer <token>

{
  "url": "https://coindesk.com/markets/",
  "extraction_prompt": "Extract cryptocurrency news headlines, prices, and market sentiment. Focus on Bitcoin, Ethereum, and major altcoins.",
  "model": "gpt-4",
  "schema": {
    "type": "object",
    "properties": {
      "headlines": {"type": "array", "items": {"type": "string"}},
      "prices": {"type": "object"},
      "sentiment": {"type": "string", "enum": ["bullish", "bearish", "neutral"]}
    }
  },
  "options": {
    "temperature": 0.1,
    "max_tokens": 2000
  }
}
```

**Response**:
```json
{
  "success": true,
  "job_id": "uuid",
  "extracted_data": {
    "headlines": [
      "Bitcoin Surges Past $45,000 Amid Institutional Interest",
      "Ethereum 2.0 Staking Rewards Reach New Highs"
    ],
    "prices": {
      "BTC": 45250.00,
      "ETH": 2850.00
    },
    "sentiment": "bullish"
  },
  "entities": [
    {
      "type": "cryptocurrency",
      "name": "Bitcoin",
      "symbol": "BTC",
      "confidence": 0.98,
      "context": "price movement"
    }
  ],
  "sentiment_analysis": {
    "overall_sentiment": "bullish",
    "confidence": 0.87,
    "key_indicators": ["institutional interest", "price surge"]
  },
  "metrics": {
    "llm_tokens_used": 1250,
    "llm_cost_usd": 0.025,
    "processing_time_ms": 3500,
    "quality_score": 0.92
  }
}
```

## URL Configuration Management

### List Configurations
```http
GET /api/configurations
Authorization: Bearer <token>
```

**Response**:
```json
{
  "configurations": [
    {
      "id": "uuid",
      "name": "CoinDesk News Monitor",
      "url": "https://coindesk.com",
      "extraction_strategy": "llm",
      "schedule": "0 */6 * * *",
      "is_active": true,
      "created_at": "2025-01-20T10:00:00Z",
      "last_run": "2025-01-20T16:00:00Z",
      "success_rate": 0.95
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### Create Configuration
```http
POST /api/configurations
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Binance Price Feed",
  "url": "https://api.binance.com/api/v3/ticker/24hr",
  "extraction_strategy": "regular",
  "extraction_config": {
    "css_selector": "body",
    "data_format": "json"
  },
  "schedule": "*/5 * * * *",
  "is_active": true
}
```

### Update Configuration
```http
PUT /api/configurations/{id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Updated Configuration Name",
  "is_active": false
}
```

### Delete Configuration
```http
DELETE /api/configurations/{id}
Authorization: Bearer <token>
```

## Job Management

### List Jobs
```http
GET /api/jobs?status=completed&limit=50&offset=0
Authorization: Bearer <token>
```

**Response**:
```json
{
  "jobs": [
    {
      "id": "uuid",
      "config_id": "uuid",
      "status": "completed",
      "started_at": "2025-01-20T16:00:00Z",
      "completed_at": "2025-01-20T16:00:05Z",
      "metrics": {
        "duration_ms": 5000,
        "success": true,
        "data_extracted": true
      }
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 50
}
```

### Get Job Details
```http
GET /api/jobs/{id}
Authorization: Bearer <token>
```

### Cancel Job
```http
POST /api/jobs/{id}/cancel
Authorization: Bearer <token>
```

## Analytics API

### Market Sentiment Analysis
```http
GET /api/analytics/sentiment?symbol=BTC&timeframe=24h
Authorization: Bearer <token>
```

**Response**:
```json
{
  "symbol": "BTC",
  "timeframe": "24h",
  "sentiment": {
    "overall": "bullish",
    "score": 0.75,
    "confidence": 0.88
  },
  "sources": {
    "news_articles": 45,
    "social_media": 120,
    "technical_analysis": 8
  },
  "trend": "increasing",
  "last_updated": "2025-01-20T16:30:00Z"
}
```

### Price Correlation Analysis
```http
GET /api/analytics/correlation?symbols=BTC,ETH,ADA&period=7d
Authorization: Bearer <token>
```

## System Monitoring

### Health Check
```http
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T16:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "crawl4ai": "healthy",
    "llm_service": "healthy",
    "vector_db": "healthy"
  },
  "metrics": {
    "uptime_seconds": 86400,
    "active_crawls": 3,
    "queue_size": 12
  }
}
```

### System Metrics
```http
GET /metrics
```

**Response** (Prometheus format):
```
# HELP crawl_requests_total Total number of crawl requests
# TYPE crawl_requests_total counter
crawl_requests_total{strategy="regular"} 1250
crawl_requests_total{strategy="llm"} 340

# HELP crawl_duration_seconds Time spent on crawling
# TYPE crawl_duration_seconds histogram
crawl_duration_seconds_bucket{le="1.0"} 450
crawl_duration_seconds_bucket{le="5.0"} 1200
crawl_duration_seconds_bucket{le="10.0"} 1580
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "INVALID_URL",
    "message": "The provided URL is not accessible or invalid",
    "details": {
      "url": "https://invalid-domain.com",
      "status_code": 404,
      "timestamp": "2025-01-20T16:30:00Z"
    }
  },
  "request_id": "uuid"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_URL` | 400 | URL format is invalid or unreachable |
| `EXTRACTION_FAILED` | 422 | Content extraction failed |
| `LLM_ERROR` | 503 | LLM service unavailable or failed |
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded |
| `UNAUTHORIZED` | 401 | Invalid or missing authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Rate Limiting

### Limits by User Role

| Role | Requests/Hour | LLM Requests/Day | Concurrent Crawls |
|------|---------------|------------------|-------------------|
| Analyst | 1,000 | 100 | 3 |
| Trader | 5,000 | 500 | 10 |
| Enterprise | 50,000 | 5,000 | 50 |

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642694400
X-RateLimit-Window: 3600
```

## WebSocket API (Real-time Updates)

### Connection
```javascript
const ws = new WebSocket('ws://localhost:4000/ws');
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['crawl_updates', 'market_alerts']
}));
```

### Message Format
```json
{
  "type": "crawl_update",
  "job_id": "uuid",
  "status": "completed",
  "data": {
    "progress": 100,
    "extracted_items": 25
  },
  "timestamp": "2025-01-20T16:30:00Z"
}
```

## SDK Examples

### Python SDK
```python
from cry_a_4mcp import CryptoAnalysisClient

client = CryptoAnalysisClient(
    base_url="http://localhost:4000",
    api_key="your_api_key"
)

# Regular crawl
result = await client.crawl(
    url="https://coindesk.com",
    strategy="regular"
)

# LLM crawl
result = await client.crawl_llm(
    url="https://coindesk.com",
    prompt="Extract crypto news and sentiment"
)
```

### JavaScript SDK
```javascript
import { CryptoAnalysisClient } from '@cry-a-4mcp/sdk';

const client = new CryptoAnalysisClient({
  baseUrl: 'http://localhost:4000',
  apiKey: 'your_api_key'
});

// Regular crawl
const result = await client.crawl({
  url: 'https://coindesk.com',
  strategy: 'regular'
});
```

---

**API Documentation Version**: 1.0  
**Last Updated**: January 2025  
**Support**: For API support, please refer to the project documentation or create an issue in the repository.
