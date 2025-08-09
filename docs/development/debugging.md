# Debugging Guide

This guide provides comprehensive debugging procedures for the CRY-A-4MCP Enhanced Templates package. It consolidates known issues, debugging techniques, and troubleshooting workflows.

## 🐛 Common Issues & Solutions

### Frontend Issues

#### Dropdown State Management Issues

**Problem**: URL Mapping dropdown not showing selected value when editing a crawler.

**Symptoms**:
- Dropdown appears empty when editing existing crawler
- Selected value not persisting in modal state
- State sharing issues between components

**Root Cause**: Improper modal state management and data transformation logic.

**Solution**:
```typescript
// Fix in Crawlers.tsx
const handleEditCrawler = (crawler: Crawler) => {
  // Ensure proper data transformation
  const editData = {
    ...crawler,
    urlMappingId: crawler.url_mapping_id, // Transform backend field to frontend field
    targetUrls: crawler.target_urls || [] // Ensure array exists
  };
  
  setEditingCrawler(editData);
  setIsEditModalOpen(true);
};

// Ensure modal receives proper initial values
<CrawlerModal
  isOpen={isEditModalOpen}
  onClose={() => setIsEditModalOpen(false)}
  onSubmit={handleUpdateCrawler}
  initialData={editingCrawler} // Pass transformed data
  urlMappings={urlMappings}
/>
```

**Prevention**:
- Always transform backend data to frontend format
- Use consistent field naming conventions
- Implement proper state initialization
- Add data validation before state updates

#### React State Updates

**Problem**: Component not re-rendering after state changes.

**Debug Steps**:
1. Check if state is being mutated directly
2. Verify useEffect dependencies
3. Ensure proper key props for list items
4. Check for stale closures

**Solution**:
```typescript
// Use functional state updates
setItems(prevItems => [...prevItems, newItem]);

// Proper useEffect dependencies
useEffect(() => {
  fetchData();
}, [dependency1, dependency2]); // Include all dependencies

// Unique keys for list items
{items.map(item => (
  <ItemComponent key={item.id} item={item} />
))}
```

### Backend Issues

#### URL Mapping Persistence Issues

**Problem**: `url_mapping_id` and `target_urls` are null in backend responses.

**Symptoms**:
- Crawler creation succeeds but URL mapping data is lost
- Database shows null values for URL mapping fields
- Frontend receives incomplete crawler data

**Debug Process**:
1. **Check API Request Data**:
   ```bash
   # Monitor API requests
   curl -X POST http://localhost:4000/api/crawlers \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Crawler",
       "urlMappingId": "123",
       "targetUrls": ["https://example.com"]
     }' -v
   ```

2. **Verify Database Schema**:
   ```sql
   -- Check crawler table structure
   DESCRIBE crawlers;
   
   -- Verify URL mapping foreign key
   SELECT * FROM crawlers WHERE url_mapping_id IS NOT NULL;
   ```

3. **Check Backend Validation**:
   ```python
   # Add logging to crawler creation endpoint
   @app.post("/api/crawlers/")
   async def create_crawler(crawler_data: CrawlerCreate):
       logger.info(f"Received crawler data: {crawler_data}")
       
       # Validate URL mapping exists
       if crawler_data.urlMappingId:
           url_mapping = await get_url_mapping(crawler_data.urlMappingId)
           if not url_mapping:
               raise HTTPException(404, "URL mapping not found")
       
       # Transform frontend fields to backend fields
       db_data = {
           "name": crawler_data.name,
           "description": crawler_data.description,
           "url_mapping_id": crawler_data.urlMappingId,  # Field transformation
           "target_urls": crawler_data.targetUrls
       }
       
       logger.info(f"Transformed data: {db_data}")
       return await create_crawler_in_db(db_data)
   ```

**Solution**:
- Implement proper field mapping between frontend and backend
- Add validation for required relationships
- Use database transactions for data consistency
- Add comprehensive logging for debugging

#### Database Connection Issues

**Problem**: Database connection failures or timeouts.

**Debug Steps**:
```python
# Test database connectivity
import asyncpg

async def test_db_connection():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="password",
            database="cry_a_4mcp"
        )
        result = await conn.fetchval("SELECT 1")
        print(f"Database connection successful: {result}")
        await conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")

# Run the test
import asyncio
asyncio.run(test_db_connection())
```

### API Issues

#### CORS Configuration

**Problem**: Frontend cannot connect to backend API.

**Debug Steps**:
1. Check browser console for CORS errors
2. Verify backend CORS configuration
3. Test API endpoints directly

**Solution**:
```python
# Backend CORS configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### API Response Validation

**Problem**: API responses don't match expected schema.

**Debug Process**:
```python
# Add response validation middleware
from fastapi import Request, Response
import json

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log request
    body = await request.body()
    logger.info(f"Request: {request.method} {request.url} - Body: {body}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    
    logger.info(f"Response: {response.status_code} - Body: {response_body}")
    
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )
```

## 🔍 Debugging Techniques

### Frontend Debugging

#### React DevTools
```javascript
// Add debugging hooks
const DebugComponent = ({ data }) => {
  useEffect(() => {
    console.log('Component mounted with data:', data);
  }, []);
  
  useEffect(() => {
    console.log('Data changed:', data);
  }, [data]);
  
  return <div>{/* component content */}</div>;
};
```

#### Network Debugging
```javascript
// Add request/response interceptors
const api = axios.create({
  baseURL: 'http://localhost:4000/api'
});

// Request interceptor
api.interceptors.request.use(
  config => {
    console.log('API Request:', config);
    return config;
  },
  error => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  response => {
    console.log('API Response:', response);
    return response;
  },
  error => {
    console.error('API Response Error:', error);
    return Promise.reject(error);
  }
);
```

### Backend Debugging

#### Structured Logging
```python
import structlog
import sys

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage in code
logger.info(
    "Crawler created",
    crawler_id=crawler.id,
    url_mapping_id=crawler.url_mapping_id,
    target_urls_count=len(crawler.target_urls)
)
```

#### Database Query Debugging
```python
# Add query logging
import logging

# Enable SQLAlchemy query logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Custom query wrapper with timing
import time
from functools import wraps

def log_query_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                "Query executed",
                function=func.__name__,
                execution_time=execution_time,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Query failed",
                function=func.__name__,
                execution_time=execution_time,
                error=str(e)
            )
            raise
    return wrapper

# Apply to database functions
@log_query_time
async def get_crawler_by_id(crawler_id: int):
    # Database query implementation
    pass
```

### Performance Debugging

#### Frontend Performance
```javascript
// React performance profiling
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration, baseDuration, startTime, commitTime) {
  console.log('Profiler:', {
    id,
    phase,
    actualDuration,
    baseDuration,
    startTime,
    commitTime
  });
}

<Profiler id="CrawlerList" onRender={onRenderCallback}>
  <CrawlerList />
</Profiler>
```

#### Backend Performance
```python
# Add performance monitoring
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 1.0:  # Log requests taking more than 1 second
        logger.warning(
            "Slow request detected",
            path=request.url.path,
            method=request.method,
            process_time=process_time
        )
    
    return response
```

## 🛠️ Debugging Tools

### Development Tools

#### Browser DevTools
- **Console**: JavaScript errors and logs
- **Network**: API request/response inspection
- **Sources**: Breakpoint debugging
- **Performance**: React component profiling
- **Application**: Local storage and state inspection

#### Backend Tools

```bash
# Database debugging
psql -h localhost -U postgres -d cry_a_4mcp

# API testing
curl -X GET http://localhost:4000/api/health -v

# Log monitoring
tail -f logs/application.log | jq .

# Process monitoring
htop
ps aux | grep python
```

### Debugging Scripts

#### Health Check Script
```python
#!/usr/bin/env python3
# scripts/health_check.py

import asyncio
import aiohttp
import sys

async def check_backend_health():
    """Check backend API health."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:4000/api/health') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Backend healthy: {data}")
                    return True
                else:
                    print(f"❌ Backend unhealthy: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

async def check_database_health():
    """Check database connectivity."""
    try:
        import asyncpg
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="password",
            database="cry_a_4mcp"
        )
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        print("✅ Database healthy")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def main():
    """Run all health checks."""
    print("🔍 Running health checks...")
    
    backend_ok = await check_backend_health()
    db_ok = await check_database_health()
    
    if backend_ok and db_ok:
        print("\n✅ All systems healthy")
        sys.exit(0)
    else:
        print("\n❌ Some systems unhealthy")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

#### Debug Data Script
```python
#!/usr/bin/env python3
# scripts/debug_data.py

import asyncio
import asyncpg
import json

async def inspect_crawler_data():
    """Inspect crawler data for debugging."""
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="password",
        database="cry_a_4mcp"
    )
    
    # Check crawlers with null URL mapping
    null_mapping_crawlers = await conn.fetch("""
        SELECT id, name, url_mapping_id, target_urls 
        FROM crawlers 
        WHERE url_mapping_id IS NULL
    """)
    
    print(f"Crawlers with null URL mapping: {len(null_mapping_crawlers)}")
    for crawler in null_mapping_crawlers:
        print(f"  - ID: {crawler['id']}, Name: {crawler['name']}")
    
    # Check URL mappings
    url_mappings = await conn.fetch("SELECT id, url_pattern FROM url_mappings")
    print(f"\nTotal URL mappings: {len(url_mappings)}")
    
    # Check orphaned crawlers
    orphaned_crawlers = await conn.fetch("""
        SELECT c.id, c.name 
        FROM crawlers c 
        LEFT JOIN url_mappings um ON c.url_mapping_id = um.id 
        WHERE c.url_mapping_id IS NOT NULL AND um.id IS NULL
    """)
    
    print(f"\nOrphaned crawlers: {len(orphaned_crawlers)}")
    for crawler in orphaned_crawlers:
        print(f"  - ID: {crawler['id']}, Name: {crawler['name']}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(inspect_crawler_data())
```

## 🚨 Emergency Debugging

### System Down Checklist

1. **Check Service Status**:
   ```bash
   # Check if services are running
   ps aux | grep -E "(python|node|postgres|redis)"
   
   # Check port availability
   netstat -tulpn | grep -E "(3000|4000|5432|6379)"
   ```

2. **Check Logs**:
   ```bash
   # Backend logs
   tail -f logs/backend.log
   
   # Frontend logs (if using PM2)
   pm2 logs frontend
   
   # System logs
   journalctl -u postgresql -f
   ```

3. **Quick Restart**:
   ```bash
   # Restart backend
   pkill -f "python.*main.py"
   cd backend && python main.py &
   
   # Restart frontend
   pkill -f "node.*react"
   cd frontend && npm start &
   ```

### Data Recovery

```sql
-- Backup critical data
COPY crawlers TO '/tmp/crawlers_backup.csv' DELIMITER ',' CSV HEADER;
COPY url_mappings TO '/tmp/url_mappings_backup.csv' DELIMITER ',' CSV HEADER;

-- Check data integrity
SELECT 
    COUNT(*) as total_crawlers,
    COUNT(url_mapping_id) as crawlers_with_mapping,
    COUNT(*) - COUNT(url_mapping_id) as crawlers_without_mapping
FROM crawlers;
```

## 📝 Debug Log Analysis

### Log Patterns to Watch

```bash
# Find error patterns
grep -E "ERROR|CRITICAL|Exception" logs/application.log | tail -20

# Find slow queries
grep "execution_time" logs/application.log | awk '$NF > 1.0' | tail -10

# Find failed API requests
grep "Response: [45][0-9][0-9]" logs/application.log | tail -10

# Monitor memory usage
grep "memory" logs/application.log | tail -10
```

### Automated Log Analysis

```python
#!/usr/bin/env python3
# scripts/analyze_logs.py

import re
import json
from collections import defaultdict, Counter
from datetime import datetime

def analyze_log_file(log_file_path):
    """Analyze application logs for patterns."""
    error_counts = Counter()
    slow_requests = []
    api_errors = []
    
    with open(log_file_path, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line)
                
                # Count errors by type
                if log_entry.get('level') in ['ERROR', 'CRITICAL']:
                    error_type = log_entry.get('event', 'Unknown')
                    error_counts[error_type] += 1
                
                # Find slow requests
                if 'process_time' in log_entry and log_entry['process_time'] > 1.0:
                    slow_requests.append({
                        'timestamp': log_entry.get('timestamp'),
                        'path': log_entry.get('path'),
                        'process_time': log_entry.get('process_time')
                    })
                
                # Find API errors
                if 'status_code' in log_entry and log_entry['status_code'] >= 400:
                    api_errors.append({
                        'timestamp': log_entry.get('timestamp'),
                        'path': log_entry.get('path'),
                        'status_code': log_entry.get('status_code')
                    })
                    
            except json.JSONDecodeError:
                continue
    
    # Generate report
    print("📊 Log Analysis Report")
    print("=" * 50)
    
    print(f"\n🚨 Error Summary:")
    for error_type, count in error_counts.most_common(10):
        print(f"  {error_type}: {count}")
    
    print(f"\n🐌 Slow Requests ({len(slow_requests)}):")
    for req in sorted(slow_requests, key=lambda x: x['process_time'], reverse=True)[:5]:
        print(f"  {req['path']}: {req['process_time']:.2f}s at {req['timestamp']}")
    
    print(f"\n❌ API Errors ({len(api_errors)}):")
    for error in api_errors[-5:]:
        print(f"  {error['status_code']} {error['path']} at {error['timestamp']}")

if __name__ == "__main__":
    analyze_log_file("logs/application.log")
```

---

**Next Steps**: Learn about [Contributing Guidelines](./contributing.md) for development best practices.