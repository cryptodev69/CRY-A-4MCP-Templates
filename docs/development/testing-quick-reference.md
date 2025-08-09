# Testing Framework Quick Reference

## 🚀 Quick Commands

### Framework Validation
```bash
# Validate entire test framework setup
python validate_test_framework.py --verbose

# Quick syntax check
pytest --collect-only --quiet
```

### Running Tests
```bash
# Run all tests
pytest

# Run by category
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests
pytest tests/performance/   # Performance tests
pytest tests/security/      # Security tests

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_strategy.py::TestStrategy::test_create_strategy

# Run tests matching pattern
pytest -k "test_strategy"

# Run with markers
pytest -m "unit"           # Unit tests only
pytest -m "slow"           # Slow tests only
pytest -m "not slow"       # Exclude slow tests
```

### Performance Testing
```bash
# Run performance benchmarks
pytest tests/performance/test_benchmark.py

# Generate performance report
python tests/performance/test_benchmark.py --generate-report

# Profile test execution
pytest --durations=10
```

### Debugging
```bash
# Run with debugger
pytest --pdb

# Verbose output
pytest -v -s

# Show test discovery
pytest --collect-only

# Show available fixtures
pytest --fixtures
```

## 🧪 Test Structure Templates

### Basic Unit Test
```python
import pytest
from unittest.mock import Mock, patch
from src.module import ClassToTest

class TestClassToTest:
    """Test suite for ClassToTest."""
    
    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return ClassToTest(config={'setting': 'value'})
    
    def test_basic_functionality(self, instance):
        """Test basic functionality."""
        # Arrange
        input_data = {'key': 'value'}
        expected = 'expected_result'
        
        # Act
        result = instance.process(input_data)
        
        # Assert
        assert result == expected
    
    def test_error_handling(self, instance):
        """Test error handling."""
        with pytest.raises(ValueError, match="Invalid input"):
            instance.process(None)
    
    @patch('src.module.external_service')
    def test_external_service(self, mock_service, instance):
        """Test external service integration."""
        mock_service.call.return_value = {'status': 'success'}
        
        result = instance.call_external()
        
        assert result['status'] == 'success'
        mock_service.call.assert_called_once()
```

### AI Agent Test
```python
class TestAIAgent:
    """Test AI agent functionality."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        client = Mock()
        client.generate.return_value = {
            'content': 'Test response',
            'tokens_used': 150,
            'confidence': 0.95
        }
        return client
    
    def test_strategy_generation(self, mock_llm_client):
        """Test AI strategy generation."""
        from src.ai.strategy_generator import StrategyGenerator
        
        generator = StrategyGenerator(client=mock_llm_client)
        result = generator.generate_strategy({
            'market': 'crypto',
            'risk_level': 'medium'
        })
        
        assert result['strategy'] is not None
        assert result['confidence'] >= 0.8
        mock_llm_client.generate.assert_called_once()
```

### API Integration Test
```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestAPI:
    """Test API endpoints."""
    
    def test_get_strategies(self):
        """Test GET /api/strategies."""
        response = client.get("/api/strategies")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_strategy(self):
        """Test POST /api/strategies."""
        strategy_data = {
            'name': 'Test Strategy',
            'description': 'Test description'
        }
        
        response = client.post("/api/strategies", json=strategy_data)
        
        assert response.status_code == 201
        assert response.json()['name'] == strategy_data['name']
```

### Async Test
```python
@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Test async functionality."""
    
    async def test_async_operation(self):
        """Test async operation."""
        from src.async_module import async_function
        
        result = await async_function()
        assert result is not None
    
    async def test_async_context_manager(self):
        """Test async context manager."""
        async with AsyncResource() as resource:
            result = await resource.process()
            assert result['status'] == 'success'
```

### Performance Test
```python
from tests.performance.test_benchmark import PerformanceBenchmark

class TestPerformance:
    """Test performance requirements."""
    
    def test_algorithm_performance(self):
        """Test algorithm performance."""
        benchmark = PerformanceBenchmark()
        
        def algorithm_to_test():
            # Your algorithm here
            return "result"
        
        result = benchmark.measure_execution_time(
            algorithm_to_test,
            iterations=10
        )
        
        assert result['avg_time'] < 0.1  # < 100ms
        assert result['memory_usage'] < 50  # < 50MB
```

## 🔧 Common Fixtures

### Database Fixture
```python
@pytest.fixture
def test_db():
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()
```

### Mock API Client
```python
@pytest.fixture
def mock_api_client():
    """Mock API client."""
    client = Mock()
    client.get.return_value = {'status': 'success', 'data': []}
    client.post.return_value = {'status': 'created', 'id': 123}
    return client
```

### Test Data Factory
```python
@pytest.fixture
def sample_strategy_data():
    """Sample strategy data."""
    return {
        'name': 'Test Strategy',
        'description': 'Test description',
        'parameters': {
            'risk_level': 'medium',
            'time_horizon': '1d'
        }
    }
```

## 🏷️ Test Markers

```python
# Mark test categories
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.e2e
def test_end_to_end():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.security
def test_security_feature():
    pass

@pytest.mark.performance
def test_performance():
    pass

@pytest.mark.ai
def test_ai_functionality():
    pass

# Parametrized tests
@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_parametrized(input_value, expected):
    result = double(input_value)
    assert result == expected
```

## 🛡️ Security Testing Patterns

### Input Validation
```python
def test_sql_injection_prevention():
    """Test SQL injection prevention."""
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--"
    ]
    
    for malicious_input in malicious_inputs:
        with pytest.raises(ValueError):
            validate_input(malicious_input)
```

### XSS Prevention
```python
def test_xss_prevention():
    """Test XSS prevention."""
    xss_payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>"
    ]
    
    for payload in xss_payloads:
        with pytest.raises(ValueError):
            sanitize_input(payload)
```

## 📊 Coverage Commands

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Show missing lines in terminal
pytest --cov=src --cov-report=term-missing

# Generate XML for CI
pytest --cov=src --cov-report=xml

# Set minimum coverage threshold
pytest --cov=src --cov-fail-under=80
```

## 🚨 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Or use pytest.ini
[tool:pytest]
python_paths = ["src"]
```

#### Async Test Issues
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Configure in pytest.ini
[tool:pytest]
asyncio_mode = auto
```

#### Database Connection Issues
```python
# Use in-memory database for tests
@pytest.fixture
def test_db_url():
    return "sqlite:///:memory:"
```

### Debug Commands
```bash
# Drop into debugger on failure
pytest --pdb

# Use IPython debugger
pytest --pdbcls=IPython.terminal.debugger:Pdb

# Show test collection
pytest --collect-only

# Show slowest tests
pytest --durations=10
```

## 📚 Related Documentation

- [Complete Testing Framework Guide](./testing-framework-guide.md)
- [Testing Framework Overview](./testing.md)
- [Debugging Procedures](./debugging.md)
- [Contributing Guidelines](./contributing.md)

---

**💡 Pro Tip**: Use `pytest -k "not slow"` during development to skip slow tests and get faster feedback!