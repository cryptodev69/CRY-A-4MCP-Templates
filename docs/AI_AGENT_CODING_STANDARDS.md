# AI Agent Coding Standards & Framework Documentation

## Overview
This document provides comprehensive guidelines for AI coding agents working on the CRY-A-4MCP cryptocurrency analysis platform. Follow these standards to ensure code quality, security, and maintainability.

## 1. Security & Secrets Management

### Input Validation
- **MANDATORY**: Sanitize ALL external or user-provided input using Pydantic-style validation
- Create validation models for every API endpoint and data structure
- Never trust user input - validate types, ranges, and formats

```python
from pydantic import BaseModel, validator

class CryptoDataRequest(BaseModel):
    symbol: str
    timeframe: str
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v.isalpha() or len(v) > 10:
            raise ValueError('Invalid symbol format')
        return v.upper()
```

### Secrets Management
- **NEVER** hard-code secrets, API keys, or passwords
- Load ALL secrets from environment variables or secrets manager
- Use `.env.example` to document required environment variables
- Validate secrets at startup using Pydantic settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    jwt_secret: str
    
    class Config:
        env_file = ".env"
```

### Dependency Security
- Pin ALL dependencies with exact versions in `requirements.txt`
- Run `pip-audit` before any deployment
- Use `bandit` for security linting
- Regular dependency updates with security patches

## 2. Code Quality & Style Standards

### Formatting & Linting
- **MANDATORY**: Use `black` for code formatting
- **MANDATORY**: Use `ruff` or `flake8` for linting
- Follow PEP 8 standards strictly
- Maximum line length: 88 characters (black default)

### Documentation Requirements
- Every public function/class MUST have Google-style docstrings
- Include full type hints for all parameters and return values
- Document exceptions that can be raised

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

### Function Complexity
- Keep functions ≤ 50 lines
- Extract complex logic into helper functions or classes
- Use single responsibility principle
- Prefer composition over inheritance

## 3. Error Handling & Observability

### Exception Handling
- Wrap ALL external calls in `try...except` blocks
- Create domain-specific exceptions
- Never use bare `except:` clauses
- Log errors with context and correlation IDs

```python
class CryptoAPIError(Exception):
    """Raised when cryptocurrency API calls fail."""
    pass

try:
    response = api_client.get_price_data(symbol)
except requests.RequestException as e:
    logger.error(f"API call failed for {symbol}", extra={
        "symbol": symbol,
        "error": str(e),
        "correlation_id": correlation_id
    })
    raise CryptoAPIError(f"Failed to fetch data for {symbol}") from e
```

### Metrics & Monitoring
- Expose Prometheus metrics at `/metrics` endpoint
- Track latency, throughput, and error rates
- Use structured JSON logging with timestamps
- Include correlation IDs for request tracing

```python
from prometheus_client import Counter, Histogram

api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration')
```

### Logging Standards
- Use structured JSON logs
- Include: timestamp, level, message, correlation-id, component
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Never log sensitive information (secrets, PII)

## 4. Testing Requirements

### Unit Testing
- **MANDATORY**: Every function ships with `pytest` unit tests
- Test happy path, edge cases, and failure scenarios
- Mock external services and dependencies
- Minimum 80% line coverage enforced in CI

```python
import pytest
from unittest.mock import Mock, patch

def test_process_crypto_data_success():
    """Test successful crypto data processing."""
    # Arrange
    mock_data = [{"price": 50000, "timestamp": "2024-01-01"}]
    
    # Act
    result = process_crypto_data("BTC", "1d")
    
    # Assert
    assert len(result) == 1
    assert result[0].price == 50000

def test_process_crypto_data_invalid_symbol():
    """Test handling of invalid symbol."""
    with pytest.raises(ValueError, match="Invalid symbol"):
        process_crypto_data("INVALID123", "1d")
```

### Integration Testing
- Test API endpoints end-to-end
- Use test databases and mock external services
- Test error scenarios and edge cases
- Validate data persistence and retrieval

### Test Organization
- Place tests in `tests/` directory
- Mirror source code structure
- Use descriptive test names
- Group related tests in classes

## 5. Architecture & Component Design

### Single-Component Lock
- Only modify files within the specific component folder
- Maintain clear component boundaries
- Document cross-component dependencies
- Use dependency injection for loose coupling

### Database Patterns

#### Qdrant (Vector Database)
```python
# qdrant_client.py
from qdrant_client import QdrantClient
from pydantic import BaseModel

COLLECTION_NAME = "crypto_embeddings"

class VectorPayload(BaseModel):
    symbol: str
    timestamp: str
    metadata: dict

class QdrantService:
    def __init__(self, client: QdrantClient):
        self.client = client
        
    def store_embedding(self, vector: List[float], payload: VectorPayload) -> str:
        """Store vector embedding with metadata."""
```

#### Neo4j (Graph Database)
```python
# neo4j_client.py
from neo4j import GraphDatabase

# Node labels
CRYPTO_NODE = "Cryptocurrency"
EXCHANGE_NODE = "Exchange"
TRANSACTION_NODE = "Transaction"

# Relationship types
TRADED_ON = "TRADED_ON"
TRANSFERRED_TO = "TRANSFERRED_TO"

def execute_cypher(tx, query: str, parameters: dict = None) -> List[dict]:
    """Execute parameterized Cypher query safely."""
    result = tx.run(query, parameters or {})
    return [record.data() for record in result]
```

### Configuration Management
- Use `pydantic-settings` for environment configuration
- Validate all settings at startup
- Provide sensible defaults where appropriate
- Document all configuration options

```python
from pydantic_settings import BaseSettings

class CryptoSettings(BaseSettings):
    # Database settings
    neo4j_uri: str = "bolt://localhost:7687"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    
    # API settings
    binance_api_key: str
    coinbase_api_key: str
    
    # Application settings
    log_level: str = "INFO"
    max_workers: int = 4
    
    class Config:
        env_file = ".env"
        env_prefix = "CRYPTO_"
```

## 6. Development Workflow

### Pre-commit Hooks
- Install and configure pre-commit hooks
- Run black, ruff, pytest, and pip-audit
- Ensure all checks pass before committing

### CI/CD Pipeline
- All code goes through GitHub Actions
- Pipeline: lint → test → security scan → build → deploy
- No direct pushes to main branch
- Require PR reviews and passing tests

### Branch Strategy
- Use feature branches for development
- Follow conventional commit messages
- Squash commits when merging
- Tag releases with semantic versioning

## 7. File Structure Standards

```
my-component/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── models.py            # Pydantic models
│   ├── services.py          # Business logic
│   ├── database/
│   │   ├── __init__.py
│   │   ├── neo4j_client.py
│   │   └── qdrant_client.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_services.py
│   └── conftest.py          # Pytest fixtures
├── requirements.txt         # Pinned dependencies
├── pyproject.toml          # Tool configuration
├── Dockerfile
├── .env.example            # Environment template
└── README.md               # Component documentation
```

## 8. Performance Guidelines

### Async Programming
- Use `asyncio` for I/O-bound operations
- Implement proper connection pooling
- Handle timeouts and retries gracefully
- Monitor async task performance

### Caching Strategy
- Implement Redis caching for frequently accessed data
- Use appropriate cache TTLs
- Handle cache misses gracefully
- Monitor cache hit rates

### Database Optimization
- Use connection pooling
- Implement proper indexing
- Avoid N+1 query problems
- Monitor query performance

## 9. Security Checklist

- [ ] All inputs validated with Pydantic
- [ ] No hardcoded secrets or credentials
- [ ] Dependencies pinned and audited
- [ ] SQL injection prevention (parameterized queries)
- [ ] Rate limiting implemented
- [ ] CORS properly configured
- [ ] Authentication and authorization in place
- [ ] Sensitive data encrypted at rest
- [ ] Security headers configured
- [ ] Regular security scans in CI/CD

## 10. Documentation Requirements

### README.md Template
```markdown
# Component Name

## Purpose
Brief description of component functionality

## Quick Start
```bash
# Installation
pip install -r requirements.txt

# Setup
cp .env.example .env
# Edit .env with your configuration

# Development
make dev

# Testing
make test
```

## API Documentation
Link to OpenAPI/Swagger documentation

## Environment Variables
List all required environment variables

## Architecture Decisions
Link to ADR documents for major decisions
```

### Code Comments
- Comment complex business logic
- Explain non-obvious algorithms
- Document performance considerations
- Include links to external documentation

## 11. Monitoring & Alerting

### Metrics to Track
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Database connection pool usage
- Memory and CPU utilization
- Cache hit/miss rates

### Health Checks
- Implement `/health` endpoint
- Check database connectivity
- Verify external service availability
- Monitor disk space and memory

## 12. Deployment Standards

### Docker Requirements
- Use multi-stage builds
- Run as non-root user
- Minimize image size
- Include health checks
- Use specific base image tags

### Environment Management
- Separate configs for dev/staging/prod
- Use secrets management in production
- Implement blue-green deployments
- Monitor deployment success

## Conclusion

Following these standards ensures:
- **Security**: Proper input validation and secrets management
- **Quality**: Consistent code style and comprehensive testing
- **Reliability**: Robust error handling and monitoring
- **Maintainability**: Clear documentation and modular design
- **Performance**: Optimized database access and caching

Always refer to this document when implementing new features or refactoring existing code. When in doubt, prioritize security and code quality over speed of delivery.