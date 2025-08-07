# Backend Configuration Guide

## Critical Backend Information

⚠️ **IMPORTANT**: This document contains critical configuration information that must be followed to avoid errors.

### Backend API File

* **Correct File**: `web_api.py`

* **Incorrect File**: ~~`simple_web_api.py`~~ (DO NOT USE)

* **Location**: `starter-mcp-server/src/cry_a_4mcp/web_api.py`

### Backend Port Configuration

* **Correct Port**: `4000`

* **Incorrect Port**: ~~`8000`~~ (DO NOT USE)

* **Full URL**: `http://localhost:4000`

### Starting the Backend Server

```bash
cd starter-mcp-server/src/cry_a_4mcp
source ../../venv311/bin/activate
python web_api.py
```

### API Endpoints

The backend provides the following endpoints:

* `GET /docs` - API documentation (Swagger UI)

* `GET /openapi.json` - OpenAPI specification

* `POST /api/crawl` - Execute crawl with regular extraction

* `POST /api/crawl-llm` - Execute crawl with LLM-based extraction

* `GET /api/health` - Health check endpoint

### Frontend Integration

The `TestURL.tsx` component should connect to:

```typescript
const API_BASE_URL = 'http://localhost:4000';
```

### Common Mistakes to Avoid

1. ❌ Using `simple_web_api.py` instead of `web_api.py`
2. ❌ Connecting to port 8000 instead of 4000
3. ❌ Using wrong virtual environment (use `venv311` with crawl4ai 0.7.0)

### Verification Steps

1. Ensure the backend is running on port 4000:

   ```bash
   curl http://localhost:4000/docs
   ```

2. Check API health:

   ```bash
   curl http://localhost:4000/api/health
   ```

3. Verify crawl4ai version in virtual environment:

   ```bash
   source venv311/bin/activate
   pip show crawl4ai
   ```

### Dependencies

* Python 3.11+ (use `venv311` virtual environment)

* crawl4ai 0.7.0

* FastAPI

* Uvicorn

