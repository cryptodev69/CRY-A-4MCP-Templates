# API Reference

Comprehensive API documentation for the CRY-A-4MCP Enhanced Templates package. This guide covers all REST API endpoints, request/response schemas, authentication, and integration examples.

## 📋 API Overview

### Base Information
- **Base URL**: `http://localhost:4000/api`
- **Protocol**: HTTP/HTTPS
- **Data Format**: JSON
- **Authentication**: API Key (optional)
- **Rate Limiting**: 1000 requests/hour per IP

### API Versioning
- **Current Version**: v1
- **Version Header**: `Accept: application/vnd.api+json;version=1`
- **Backward Compatibility**: Maintained for 2 major versions

### Response Format
All API responses follow a consistent structure:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "url",
      "reason": "Invalid URL format"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔐 Authentication

### API Key Authentication
```http
GET /api/crawlers
Authorization: Bearer your-api-key-here
Content-Type: application/json
```

### Environment Setup
```bash
# Set API key in environment
export CRY_A_4MCP_API_KEY="your-api-key"

# Or in .env file
CRY_A_4MCP_API_KEY=your-api-key
```

## 🏥 Health & Status

### Health Check
Check API and system health status.

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0.0",
    "services": {
      "database": "healthy",
      "redis": "healthy",
      "llm_providers": "healthy"
    },
    "uptime": 86400,
    "memory_usage": "45%",
    "cpu_usage": "12%"
  }
}
```

**Example**:
```bash
curl -X GET http://localhost:4000/api/health
```

```javascript
// JavaScript/TypeScript
const response = await fetch('http://localhost:4000/api/health');
const health = await response.json();
console.log('API Status:', health.data.status);
```

```python
# Python
import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.get('http://localhost:4000/api/health') as response:
        health = await response.json()
        print(f"API Status: {health['data']['status']}")
```

## 🗺️ URL Mappings API

Manage URL mapping configurations for web scraping.

### List URL Mappings
**Endpoint**: `GET /api/url-mappings`

**Query Parameters**:
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `search` (string): Search in URL patterns
- `profile` (string): Filter by profile type
- `priority` (integer): Filter by priority level

**Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid-123",
        "url_pattern": "https://example.com/*",
        "profile": "Degen Gambler",
        "priority": 1,
        "scraping_difficulty": "Medium",
        "api_available": false,
        "cost_analysis": "Low cost, high value",
        "extractor_id": "extractor-456",
        "match_type": "pattern",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

**Example**:
```bash
# Get all URL mappings
curl -X GET "http://localhost:4000/api/url-mappings"

# Get URL mappings with filters
curl -X GET "http://localhost:4000/api/url-mappings?profile=Degen%20Gambler&priority=1"
```

### Create URL Mapping
**Endpoint**: `POST /api/url-mappings`

**Request Body**:
```json
{
  "url_pattern": "https://example.com/*",
  "profile": "Degen Gambler",
  "priority": 1,
  "scraping_difficulty": "Medium",
  "api_available": false,
  "cost_analysis": "Low cost, high value",
  "extractor_id": "extractor-456",
  "match_type": "pattern",
  "metadata": {
    "tags": ["crypto", "defi"],
    "notes": "High-value target for price data"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-789",
    "url_pattern": "https://example.com/*",
    "profile": "Degen Gambler",
    "priority": 1,
    "scraping_difficulty": "Medium",
    "api_available": false,
    "cost_analysis": "Low cost, high value",
    "extractor_id": "extractor-456",
    "match_type": "pattern",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "URL mapping created successfully"
}
```

**Example**:
```javascript
// JavaScript/TypeScript
const urlMapping = {
  url_pattern: "https://coinmarketcap.com/*",
  profile: "Gem Hunter",
  priority: 2,
  scraping_difficulty: "Hard",
  api_available: true,
  cost_analysis: "API available, prefer API over scraping"
};

const response = await fetch('http://localhost:4000/api/url-mappings', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify(urlMapping)
});

const result = await response.json();
console.log('Created URL mapping:', result.data.id);
```

### Get URL Mapping
**Endpoint**: `GET /api/url-mappings/{id}`

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-123",
    "url_pattern": "https://example.com/*",
    "profile": "Degen Gambler",
    "priority": 1,
    "scraping_difficulty": "Medium",
    "api_available": false,
    "cost_analysis": "Low cost, high value",
    "extractor_id": "extractor-456",
    "match_type": "pattern",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "usage_stats": {
      "total_crawls": 150,
      "success_rate": 0.95,
      "avg_response_time": 1.2
    }
  }
}
```

### Update URL Mapping
**Endpoint**: `PUT /api/url-mappings/{id}`

**Request Body**: Same as create, all fields optional

### Delete URL Mapping
**Endpoint**: `DELETE /api/url-mappings/{id}`

**Response**:
```json
{
  "success": true,
  "message": "URL mapping deleted successfully"
}
```

## 🕷️ Crawlers API

Manage web crawlers and crawling jobs.

### List Crawlers
**Endpoint**: `GET /api/crawlers`

**Query Parameters**:
- `page` (integer): Page number
- `limit` (integer): Items per page
- `status` (string): Filter by status (active, inactive, error)
- `url_mapping_id` (string): Filter by URL mapping

**Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "crawler-123",
        "name": "Bitcoin Price Crawler",
        "description": "Crawls Bitcoin price from multiple sources",
        "status": "active",
        "url_mapping_id": "uuid-456",
        "target_urls": [
          "https://coinmarketcap.com/currencies/bitcoin/",
          "https://coingecko.com/en/coins/bitcoin"
        ],
        "schedule": "0 */5 * * *",
        "last_run": "2024-01-15T10:25:00Z",
        "next_run": "2024-01-15T10:30:00Z",
        "success_rate": 0.98,
        "created_at": "2024-01-15T09:00:00Z",
        "updated_at": "2024-01-15T10:25:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "pages": 3
    }
  }
}
```

### Create Crawler
**Endpoint**: `POST /api/crawlers`

**Request Body**:
```json
{
  "name": "Ethereum Price Crawler",
  "description": "Monitors Ethereum price across exchanges",
  "urlMappingId": "uuid-456",
  "targetUrls": [
    "https://coinmarketcap.com/currencies/ethereum/",
    "https://coingecko.com/en/coins/ethereum"
  ],
  "schedule": "0 */10 * * *",
  "config": {
    "timeout": 30,
    "retries": 3,
    "concurrent_requests": 5,
    "delay_between_requests": 1.0
  },
  "notifications": {
    "on_success": false,
    "on_error": true,
    "webhook_url": "https://hooks.slack.com/..."
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "crawler-789",
    "name": "Ethereum Price Crawler",
    "description": "Monitors Ethereum price across exchanges",
    "status": "active",
    "url_mapping_id": "uuid-456",
    "target_urls": [
      "https://coinmarketcap.com/currencies/ethereum/",
      "https://coingecko.com/en/coins/ethereum"
    ],
    "schedule": "0 */10 * * *",
    "next_run": "2024-01-15T10:40:00Z",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "Crawler created successfully"
}
```

### Run Crawler
**Endpoint**: `POST /api/crawlers/{id}/run`

**Request Body** (optional):
```json
{
  "urls": ["https://specific-url.com"],
  "priority": "high",
  "metadata": {
    "run_type": "manual",
    "user_id": "user-123"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "job_id": "job-456",
    "crawler_id": "crawler-123",
    "status": "queued",
    "estimated_completion": "2024-01-15T10:35:00Z",
    "urls_count": 2
  },
  "message": "Crawler job started successfully"
}
```

### Get Crawler Status
**Endpoint**: `GET /api/crawlers/{id}/status`

**Response**:
```json
{
  "success": true,
  "data": {
    "crawler_id": "crawler-123",
    "status": "running",
    "current_job": {
      "job_id": "job-456",
      "started_at": "2024-01-15T10:30:00Z",
      "progress": {
        "completed": 1,
        "total": 2,
        "percentage": 50
      },
      "current_url": "https://coingecko.com/en/coins/bitcoin"
    },
    "last_results": {
      "success_count": 1,
      "error_count": 0,
      "data_points_extracted": 15
    }
  }
}
```

## 🔧 Extractors API

Manage data extraction configurations.

### List Extractors
**Endpoint**: `GET /api/extractors`

**Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "extractor-123",
        "name": "Crypto Price Extractor",
        "type": "llm",
        "model": "gpt-3.5-turbo",
        "schema": {
          "price": "number",
          "currency": "string",
          "timestamp": "datetime",
          "volume_24h": "number"
        },
        "instructions": "Extract cryptocurrency price and volume data",
        "success_rate": 0.95,
        "avg_extraction_time": 2.1,
        "created_at": "2024-01-15T09:00:00Z"
      }
    ]
  }
}
```

### Create Extractor
**Endpoint**: `POST /api/extractors`

**Request Body**:
```json
{
  "name": "NFT Metadata Extractor",
  "type": "llm",
  "model": "gpt-4",
  "schema": {
    "name": "string",
    "description": "string",
    "price": "number",
    "currency": "string",
    "collection": "string",
    "traits": "array"
  },
  "instructions": "Extract NFT metadata including name, description, price, and traits",
  "config": {
    "temperature": 0.1,
    "max_tokens": 1000,
    "timeout": 30
  }
}
```

### Test Extractor
**Endpoint**: `POST /api/extractors/{id}/test`

**Request Body**:
```json
{
  "content": "<html><h1>Bitcoin</h1><p>Price: $45,000</p></html>",
  "content_type": "html"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "extracted_data": {
      "price": 45000,
      "currency": "USD",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    "extraction_time": 1.8,
    "confidence_score": 0.92
  }
}
```

## 📊 Jobs & Results API

Monitor crawling jobs and retrieve results.

### List Jobs
**Endpoint**: `GET /api/jobs`

**Query Parameters**:
- `status` (string): Filter by status (queued, running, completed, failed)
- `crawler_id` (string): Filter by crawler
- `from_date` (string): Filter jobs from date (ISO format)
- `to_date` (string): Filter jobs to date (ISO format)

**Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "job-123",
        "crawler_id": "crawler-456",
        "status": "completed",
        "started_at": "2024-01-15T10:30:00Z",
        "completed_at": "2024-01-15T10:32:15Z",
        "duration": 135,
        "urls_processed": 5,
        "data_points_extracted": 25,
        "success_rate": 1.0,
        "results_url": "/api/jobs/job-123/results"
      }
    ]
  }
}
```

### Get Job Details
**Endpoint**: `GET /api/jobs/{id}`

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "job-123",
    "crawler_id": "crawler-456",
    "status": "completed",
    "started_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:32:15Z",
    "duration": 135,
    "config": {
      "timeout": 30,
      "retries": 3,
      "concurrent_requests": 5
    },
    "progress": {
      "total_urls": 5,
      "completed_urls": 5,
      "failed_urls": 0,
      "percentage": 100
    },
    "statistics": {
      "avg_response_time": 1.2,
      "total_data_size": 1048576,
      "data_points_extracted": 25
    },
    "errors": []
  }
}
```

### Get Job Results
**Endpoint**: `GET /api/jobs/{id}/results`

**Query Parameters**:
- `format` (string): Response format (json, csv, xlsx)
- `page` (integer): Page number for pagination
- `limit` (integer): Items per page

**Response**:
```json
{
  "success": true,
  "data": {
    "job_id": "job-123",
    "results": [
      {
        "url": "https://coinmarketcap.com/currencies/bitcoin/",
        "extracted_at": "2024-01-15T10:30:30Z",
        "data": {
          "price": 45000,
          "currency": "USD",
          "volume_24h": 25000000000,
          "market_cap": 880000000000
        },
        "metadata": {
          "response_time": 1.1,
          "content_size": 245760,
          "extraction_confidence": 0.95
        }
      }
    ],
    "summary": {
      "total_results": 25,
      "unique_data_points": 20,
      "avg_confidence": 0.93
    }
  }
}
```

### Export Job Results
**Endpoint**: `GET /api/jobs/{id}/export`

**Query Parameters**:
- `format` (string): Export format (csv, xlsx, json)
- `fields` (string): Comma-separated list of fields to include

**Response**: File download with appropriate content-type header

## 📈 Analytics API

Retrieve system analytics and performance metrics.

### System Metrics
**Endpoint**: `GET /api/analytics/metrics`

**Query Parameters**:
- `period` (string): Time period (1h, 24h, 7d, 30d)
- `metrics` (string): Comma-separated list of metrics

**Response**:
```json
{
  "success": true,
  "data": {
    "period": "24h",
    "metrics": {
      "total_crawls": 1250,
      "successful_crawls": 1188,
      "failed_crawls": 62,
      "success_rate": 0.95,
      "avg_response_time": 1.8,
      "data_points_extracted": 15600,
      "unique_urls_crawled": 450,
      "total_data_size": 52428800
    },
    "trends": {
      "crawls_per_hour": [
        {"hour": "2024-01-15T00:00:00Z", "count": 45},
        {"hour": "2024-01-15T01:00:00Z", "count": 52}
      ]
    }
  }
}
```

### Crawler Performance
**Endpoint**: `GET /api/analytics/crawlers/{id}/performance`

**Response**:
```json
{
  "success": true,
  "data": {
    "crawler_id": "crawler-123",
    "performance": {
      "total_runs": 150,
      "success_rate": 0.97,
      "avg_duration": 125,
      "avg_data_points": 18,
      "reliability_score": 0.95
    },
    "recent_runs": [
      {
        "job_id": "job-456",
        "started_at": "2024-01-15T10:30:00Z",
        "duration": 135,
        "success_rate": 1.0,
        "data_points": 25
      }
    ]
  }
}
```

## 🚨 Error Handling

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Invalid input data | 400 |
| `AUTHENTICATION_ERROR` | Invalid or missing API key | 401 |
| `AUTHORIZATION_ERROR` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `CONFLICT` | Resource conflict | 409 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

### Error Response Examples

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid URL pattern",
    "details": {
      "field": "url_pattern",
      "value": "invalid-url",
      "reason": "URL must start with http:// or https://"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 1000,
      "window": "1h",
      "reset_at": "2024-01-15T11:00:00Z"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔌 Integration Examples

### Python Integration

```python
import aiohttp
import asyncio
from typing import Dict, List, Optional

class CryA4MCPClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
    
    async def __aenter__(self):
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_url_mapping(self, data: Dict) -> Dict:
        """Create a new URL mapping."""
        async with self.session.post(f'{self.base_url}/api/url-mappings', json=data) as response:
            result = await response.json()
            if not result['success']:
                raise Exception(f"API Error: {result['error']['message']}")
            return result['data']
    
    async def create_crawler(self, data: Dict) -> Dict:
        """Create a new crawler."""
        async with self.session.post(f'{self.base_url}/api/crawlers', json=data) as response:
            result = await response.json()
            if not result['success']:
                raise Exception(f"API Error: {result['error']['message']}")
            return result['data']
    
    async def run_crawler(self, crawler_id: str, urls: Optional[List[str]] = None) -> Dict:
        """Run a crawler."""
        data = {'urls': urls} if urls else {}
        async with self.session.post(f'{self.base_url}/api/crawlers/{crawler_id}/run', json=data) as response:
            result = await response.json()
            if not result['success']:
                raise Exception(f"API Error: {result['error']['message']}")
            return result['data']
    
    async def get_job_results(self, job_id: str) -> Dict:
        """Get job results."""
        async with self.session.get(f'{self.base_url}/api/jobs/{job_id}/results') as response:
            result = await response.json()
            if not result['success']:
                raise Exception(f"API Error: {result['error']['message']}")
            return result['data']

# Usage example
async def main():
    async with CryA4MCPClient('http://localhost:4000', 'your-api-key') as client:
        # Create URL mapping
        url_mapping = await client.create_url_mapping({
            'url_pattern': 'https://coinmarketcap.com/*',
            'profile': 'Gem Hunter',
            'priority': 1,
            'scraping_difficulty': 'Medium'
        })
        
        # Create crawler
        crawler = await client.create_crawler({
            'name': 'CMC Price Crawler',
            'description': 'Crawl CoinMarketCap for price data',
            'urlMappingId': url_mapping['id'],
            'targetUrls': ['https://coinmarketcap.com/currencies/bitcoin/']
        })
        
        # Run crawler
        job = await client.run_crawler(crawler['id'])
        
        # Wait for completion and get results
        await asyncio.sleep(30)  # Wait for job to complete
        results = await client.get_job_results(job['job_id'])
        
        print(f"Extracted {len(results['results'])} data points")

if __name__ == '__main__':
    asyncio.run(main())
```

### JavaScript/TypeScript Integration

```typescript
interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
}

class CryA4MCPClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    const result: APIResponse<T> = await response.json();

    if (!result.success) {
      throw new Error(`API Error: ${result.error?.message}`);
    }

    return result.data!;
  }

  async createUrlMapping(data: any) {
    return this.request('/api/url-mappings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async createCrawler(data: any) {
    return this.request('/api/crawlers', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async runCrawler(crawlerId: string, urls?: string[]) {
    return this.request(`/api/crawlers/${crawlerId}/run`, {
      method: 'POST',
      body: JSON.stringify({ urls }),
    });
  }

  async getJobResults(jobId: string) {
    return this.request(`/api/jobs/${jobId}/results`);
  }

  async getCrawlerStatus(crawlerId: string) {
    return this.request(`/api/crawlers/${crawlerId}/status`);
  }
}

// Usage example
const client = new CryA4MCPClient('http://localhost:4000', 'your-api-key');

async function example() {
  try {
    // Create URL mapping
    const urlMapping = await client.createUrlMapping({
      url_pattern: 'https://coingecko.com/*',
      profile: 'Degen Gambler',
      priority: 2,
      scraping_difficulty: 'Easy'
    });

    // Create crawler
    const crawler = await client.createCrawler({
      name: 'CoinGecko Price Crawler',
      description: 'Monitor prices on CoinGecko',
      urlMappingId: urlMapping.id,
      targetUrls: ['https://coingecko.com/en/coins/bitcoin']
    });

    // Run crawler
    const job = await client.runCrawler(crawler.id);
    console.log(`Job started: ${job.job_id}`);

    // Monitor status
    const checkStatus = async () => {
      const status = await client.getCrawlerStatus(crawler.id);
      console.log(`Status: ${status.status}`);
      
      if (status.status === 'completed') {
        const results = await client.getJobResults(job.job_id);
        console.log(`Results: ${results.results.length} items`);
      } else if (status.status === 'running') {
        setTimeout(checkStatus, 5000); // Check again in 5 seconds
      }
    };

    setTimeout(checkStatus, 2000); // Start checking after 2 seconds

  } catch (error) {
    console.error('Error:', error.message);
  }
}

example();
```

## 📚 SDK Libraries

### Official SDKs
- **Python**: `pip install cry-a-4mcp-python`
- **JavaScript/TypeScript**: `npm install cry-a-4mcp-js`
- **Go**: `go get github.com/cry-a-4mcp/go-sdk`

### Community SDKs
- **Ruby**: `gem install cry_a_4mcp`
- **PHP**: `composer require cry-a-4mcp/php-sdk`
- **Java**: Available on Maven Central

---

**Next Steps**: Explore [Guides](../guides/README.md) for detailed implementation examples and best practices.