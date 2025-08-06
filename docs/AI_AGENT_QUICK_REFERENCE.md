# AI Agent Quick Reference Guide

## 🚨 Critical Security Rules

```python
# ✅ ALWAYS validate inputs
from pydantic import BaseModel, validator

class APIRequest(BaseModel):
    symbol: str
    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper() if v.isalpha() else ValueError("Invalid")

# ✅ NEVER hardcode secrets
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    api_key: str
    class Config:
        env_file = ".env"

# ✅ ALWAYS use parameterized queries
def get_user(tx, user_id: str):
    return tx.run("MATCH (u:User {id: $id}) RETURN u", {"id": user_id})
```

## 📝 Code Quality Checklist

- [ ] **Black formatting**: `black src/`
- [ ] **Ruff linting**: `ruff check src/`
- [ ] **Type hints**: All functions have complete type annotations
- [ ] **Docstrings**: Google-style for all public functions
- [ ] **Function size**: ≤ 50 lines per function
- [ ] **Error handling**: All external calls wrapped in try/except

## 🧪 Testing Requirements

```python
# Test structure
def test_function_name_scenario():
    """Test description."""
    # Arrange
    input_data = {...}
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result.status == "success"
    
# Mock external services
@patch('module.external_api')
def test_with_mock(mock_api):
    mock_api.return_value = {"data": "test"}
    # Test logic here
```

**Coverage requirement**: Minimum 80%

## 🏗️ Architecture Patterns

### Database Clients

```python
# Qdrant
COLLECTION_NAME = "crypto_embeddings"
class VectorPayload(BaseModel):
    symbol: str
    metadata: dict

# Neo4j
CRYPTO_NODE = "Cryptocurrency"
TRADED_ON = "TRADED_ON"

def execute_cypher(tx, query: str, params: dict = None):
    return tx.run(query, params or {})
```

### Error Handling

```python
class CryptoAPIError(Exception):
    """Domain-specific exception."""
    pass

try:
    result = external_api_call()
except requests.RequestException as e:
    logger.error("API failed", extra={"error": str(e)})
    raise CryptoAPIError("Service unavailable") from e
```

## 📊 Monitoring & Logging

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

api_requests = Counter('api_requests_total', 'Total requests', ['endpoint'])
api_duration = Histogram('api_duration_seconds', 'Request duration')

# Structured logging
import structlog
logger = structlog.get_logger()

logger.info("Processing request", 
           symbol="BTC", 
           correlation_id=correlation_id)
```

## 🐳 Docker Standards

```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "src/main.py"]
```

## 📁 File Structure Template

```
component/
├── src/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   ├── services.py          # Business logic
│   ├── database/
│   │   ├── neo4j_client.py
│   │   └── qdrant_client.py
│   └── utils/helpers.py
├── tests/
│   ├── test_main.py
│   ├── test_services.py
│   └── conftest.py
├── requirements.txt         # Pinned versions
├── pyproject.toml          # Tool configs
├── Dockerfile
├── .env.example
└── README.md
```

## ⚡ Performance Guidelines

```python
# Async patterns
import asyncio
from aiohttp import ClientSession

async def fetch_crypto_data(session: ClientSession, symbol: str):
    async with session.get(f"/api/crypto/{symbol}") as response:
        return await response.json()

# Connection pooling
from sqlalchemy.pool import QueuePool
engine = create_engine(url, poolclass=QueuePool, pool_size=20)

# Caching
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param: str) -> str:
    return complex_operation(param)
```

## 🔧 Development Commands

```bash
# Setup
cp .env.example .env
pip install -r requirements.txt
pre-commit install

# Development
make dev          # Start development server
make test         # Run tests
make lint         # Run linting
make format       # Format code
make security     # Security checks

# Docker
docker-compose up -d    # Start services
docker-compose logs -f  # View logs
```

## 🚦 CI/CD Pipeline

1. **Lint**: black, ruff, mypy
2. **Test**: pytest with coverage
3. **Security**: bandit, pip-audit, trivy
4. **Build**: Docker image
5. **Deploy**: Staging → Production

## 📋 Pre-commit Checklist

- [ ] Code formatted with black
- [ ] Linting passes (ruff)
- [ ] Type checking passes (mypy)
- [ ] Tests pass with >80% coverage
- [ ] Security scan clean (bandit)
- [ ] Dependencies audited (pip-audit)
- [ ] Secrets not committed
- [ ] Documentation updated

## 🔍 Debugging Circuit Breaker

**Single-Fix Budget**: Max 3 file edits + 1 test per bug
**If stuck**: Write `scratchpad/debug-blocked.md` and escalate
**Loop detection**: Hash stack trace; if repeated, halt

## 📚 Documentation Requirements

### Function Documentation
```python
def process_crypto_data(
    symbol: str, 
    timeframe: str, 
    limit: int = 100
) -> List[CryptoDataPoint]:
    """Process cryptocurrency data for analysis.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        timeframe: Data timeframe ('1h', '1d', '1w')
        limit: Maximum number of data points to return
        
    Returns:
        List of processed cryptocurrency data points
        
    Raises:
        ValueError: If symbol or timeframe is invalid
        APIError: If external API call fails
    """
```

### README Template
```markdown
# Component Name

## Purpose
Brief description

## Quick Start
```bash
make dev
```

## API Documentation
`/docs` - Swagger UI

## Environment Variables
See `.env.example`
```

---

## 🎯 Remember: Security First, Quality Always

1. **Validate everything** - Never trust input
2. **Test everything** - 80% coverage minimum  
3. **Monitor everything** - Metrics + logs
4. **Document everything** - Code + architecture
5. **Secure everything** - Secrets + dependencies