# Testing Framework Guide for CRY-A-4MCP

## Overview

This guide provides comprehensive documentation for using the CRY-A-4MCP testing framework, designed specifically for coding agents and full-stack developers working with AI-driven cryptocurrency analysis platforms.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Framework Architecture](#framework-architecture)
3. [Testing for Coding Agents](#testing-for-coding-agents)
4. [Full-Stack Testing Approach](#full-stack-testing-approach)
5. [Test Categories](#test-categories)
6. [Running Tests](#running-tests)
7. [Writing Tests](#writing-tests)
8. [Performance Testing](#performance-testing)
9. [Security Testing](#security-testing)
10. [CI/CD Integration](#cicd-integration)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Validate framework setup
python validate_test_framework.py --verbose
```

### Run All Tests

```bash
# Run complete test suite
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests
pytest tests/performance/   # Performance tests
pytest tests/security/      # Security tests
```

## Framework Architecture

### Directory Structure

```
tests/
├── README.md                 # Testing overview
├── TEST_INDEX.md            # Test catalog
├── fixtures/                # Test data and utilities
│   ├── seed_test_data.py   # Database seeding
│   └── test_factories.py   # Data factories
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── e2e/                     # End-to-end tests
├── performance/             # Performance benchmarks
│   └── test_benchmark.py   # Performance testing suite
├── security/                # Security tests
│   └── test_security_basics.py
├── backend/                 # Backend-specific tests
├── ui/                      # Frontend tests
└── utils/                   # Testing utilities
```

### Key Components

- **pytest.ini**: Central configuration
- **validate_test_framework.py**: Framework validation
- **test_benchmark.py**: Performance testing suite
- **seed_test_data.py**: Test data management
- **conftest.py**: Shared fixtures and configuration

## Testing for Coding Agents

### Agent-Specific Testing Patterns

#### 1. AI Model Testing

```python
# tests/unit/test_ai_models.py
import pytest
from unittest.mock import Mock, patch

class TestAIModelIntegration:
    """Test AI model interactions and responses."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for testing."""
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
    
    @pytest.mark.asyncio
    async def test_async_model_calls(self, mock_llm_client):
        """Test asynchronous AI model calls."""
        # Test async patterns for AI agents
        pass
```

#### 2. Agent Decision Testing

```python
# tests/unit/test_agent_decisions.py
class TestAgentDecisionMaking:
    """Test agent decision-making logic."""
    
    def test_market_analysis_decision(self):
        """Test agent's market analysis decisions."""
        from src.agents.market_agent import MarketAgent
        
        agent = MarketAgent()
        market_data = {
            'price': 50000,
            'volume': 1000000,
            'trend': 'bullish'
        }
        
        decision = agent.analyze_market(market_data)
        
        assert decision['action'] in ['buy', 'sell', 'hold']
        assert 'confidence' in decision
        assert 'reasoning' in decision
    
    def test_risk_assessment(self):
        """Test agent's risk assessment capabilities."""
        # Test risk evaluation logic
        pass
```

#### 3. Agent Communication Testing

```python
# tests/integration/test_agent_communication.py
class TestAgentCommunication:
    """Test inter-agent communication."""
    
    @pytest.mark.asyncio
    async def test_agent_message_passing(self):
        """Test message passing between agents."""
        from src.agents.coordinator import AgentCoordinator
        
        coordinator = AgentCoordinator()
        
        # Test agent coordination
        result = await coordinator.coordinate_analysis({
            'market_data': {},
            'news_data': {},
            'social_data': {}
        })
        
        assert result['consensus'] is not None
        assert len(result['agent_responses']) > 0
```

### Agent Testing Best Practices

1. **Mock External AI Services**: Always mock LLM APIs and external AI services
2. **Test Decision Logic**: Focus on testing the decision-making algorithms
3. **Validate Outputs**: Ensure AI outputs meet expected formats and constraints
4. **Performance Testing**: Test response times and resource usage
5. **Error Handling**: Test how agents handle API failures and invalid inputs

## Full-Stack Testing Approach

### Testing Pyramid for Full-Stack Development

```
        /\     E2E Tests (Few)
       /  \    - User workflows
      /    \   - Browser automation
     /______\  - API integration
    /        \
   / Integration \ (Some)
  /   Tests      \ - API endpoints
 /________________\ - Database ops
/                  \
/    Unit Tests     \ (Many)
/    (Foundation)   \ - Pure functions
/__________________\ - Component logic
```

### 1. Frontend Testing

#### Component Testing

```javascript
// frontend/src/tests/components/StrategyCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import StrategyCard from '../components/StrategyCard';

describe('StrategyCard', () => {
  const mockStrategy = {
    id: '1',
    name: 'Test Strategy',
    performance: 15.5,
    risk: 'medium'
  };

  test('renders strategy information', () => {
    render(<StrategyCard strategy={mockStrategy} />);
    
    expect(screen.getByText('Test Strategy')).toBeInTheDocument();
    expect(screen.getByText('15.5%')).toBeInTheDocument();
    expect(screen.getByText('medium')).toBeInTheDocument();
  });

  test('handles strategy selection', () => {
    const onSelect = jest.fn();
    render(<StrategyCard strategy={mockStrategy} onSelect={onSelect} />);
    
    fireEvent.click(screen.getByRole('button'));
    expect(onSelect).toHaveBeenCalledWith(mockStrategy.id);
  });
});
```

#### Integration Testing

```javascript
// frontend/src/tests/integration/StrategyFlow.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import StrategyFlow from '../pages/StrategyFlow';

const server = setupServer(
  rest.get('/api/strategies', (req, res, ctx) => {
    return res(ctx.json([
      { id: '1', name: 'Strategy 1', performance: 10.5 }
    ]));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('loads and displays strategies', async () => {
  render(<StrategyFlow />);
  
  await waitFor(() => {
    expect(screen.getByText('Strategy 1')).toBeInTheDocument();
  });
});
```

### 2. Backend Testing

#### API Endpoint Testing

```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestStrategyAPI:
    """Test strategy API endpoints."""
    
    def test_get_strategies(self):
        """Test GET /api/strategies endpoint."""
        response = client.get("/api/strategies")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If strategies exist
            strategy = data[0]
            assert 'id' in strategy
            assert 'name' in strategy
            assert 'performance' in strategy
    
    def test_create_strategy(self):
        """Test POST /api/strategies endpoint."""
        strategy_data = {
            'name': 'Test Strategy',
            'description': 'A test strategy',
            'parameters': {'risk_level': 'medium'}
        }
        
        response = client.post("/api/strategies", json=strategy_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == strategy_data['name']
        assert 'id' in data
    
    def test_invalid_strategy_creation(self):
        """Test error handling for invalid strategy data."""
        invalid_data = {'name': ''}  # Missing required fields
        
        response = client.post("/api/strategies", json=invalid_data)
        
        assert response.status_code == 422
        assert 'detail' in response.json()
```

#### Database Testing

```python
# tests/integration/test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Strategy, Base
from src.database.crud import StrategyRepository

@pytest.fixture
def test_db():
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()

class TestStrategyRepository:
    """Test strategy database operations."""
    
    def test_create_strategy(self, test_db):
        """Test strategy creation in database."""
        repo = StrategyRepository(test_db)
        
        strategy_data = {
            'name': 'Test Strategy',
            'description': 'Test description',
            'parameters': {'risk': 'low'}
        }
        
        strategy = repo.create(strategy_data)
        
        assert strategy.id is not None
        assert strategy.name == strategy_data['name']
        assert strategy.created_at is not None
    
    def test_get_strategies(self, test_db):
        """Test retrieving strategies from database."""
        repo = StrategyRepository(test_db)
        
        # Create test data
        repo.create({'name': 'Strategy 1', 'description': 'Desc 1'})
        repo.create({'name': 'Strategy 2', 'description': 'Desc 2'})
        
        strategies = repo.get_all()
        
        assert len(strategies) == 2
        assert strategies[0].name == 'Strategy 1'
        assert strategies[1].name == 'Strategy 2'
```

### 3. End-to-End Testing

```python
# tests/e2e/test_strategy_workflow.py
import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
class TestStrategyWorkflow:
    """Test complete strategy workflow."""
    
    async def test_create_and_run_strategy(self):
        """Test creating and running a strategy end-to-end."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navigate to application
            await page.goto("http://localhost:3000")
            
            # Create new strategy
            await page.click("[data-testid='create-strategy-btn']")
            await page.fill("[data-testid='strategy-name']", "E2E Test Strategy")
            await page.select_option("[data-testid='risk-level']", "medium")
            await page.click("[data-testid='save-strategy-btn']")
            
            # Verify strategy was created
            await page.wait_for_selector("[data-testid='strategy-card']")
            strategy_name = await page.text_content("[data-testid='strategy-name']")
            assert strategy_name == "E2E Test Strategy"
            
            # Run strategy
            await page.click("[data-testid='run-strategy-btn']")
            await page.wait_for_selector("[data-testid='strategy-results']")
            
            # Verify results
            results = await page.text_content("[data-testid='strategy-results']")
            assert "Performance:" in results
            
            await browser.close()
```

### Full-Stack Testing Best Practices

1. **Test Isolation**: Each test should be independent and not rely on others
2. **Data Management**: Use factories and fixtures for consistent test data
3. **Mock External Services**: Mock third-party APIs and services
4. **Environment Consistency**: Use containerized test environments
5. **Parallel Execution**: Run tests in parallel for faster feedback
6. **Coverage Tracking**: Maintain high test coverage across all layers

## Test Categories

### Unit Tests
- **Purpose**: Test individual functions and classes in isolation
- **Location**: `tests/unit/`
- **Scope**: Single function/method
- **Speed**: Fast (< 1ms per test)

### Integration Tests
- **Purpose**: Test component interactions
- **Location**: `tests/integration/`
- **Scope**: Multiple components working together
- **Speed**: Medium (< 100ms per test)

### End-to-End Tests
- **Purpose**: Test complete user workflows
- **Location**: `tests/e2e/`
- **Scope**: Full application stack
- **Speed**: Slow (seconds per test)

### Performance Tests
- **Purpose**: Test system performance and scalability
- **Location**: `tests/performance/`
- **Scope**: Load, stress, and benchmark testing
- **Speed**: Variable (depends on test duration)

### Security Tests
- **Purpose**: Test security vulnerabilities
- **Location**: `tests/security/`
- **Scope**: Input validation, authentication, authorization
- **Speed**: Medium to slow

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_strategy.py

# Run specific test method
pytest tests/unit/test_strategy.py::TestStrategy::test_create_strategy

# Run tests matching pattern
pytest -k "test_strategy"

# Run tests with specific markers
pytest -m "unit"
pytest -m "integration"
pytest -m "slow"
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View coverage in terminal
pytest --cov=src --cov-report=term-missing

# Generate XML coverage for CI
pytest --cov=src --cov-report=xml
```

### Performance Testing

```bash
# Run performance benchmarks
pytest tests/performance/test_benchmark.py

# Run with performance profiling
pytest tests/performance/ --benchmark-only

# Generate performance report
python tests/performance/test_benchmark.py --generate-report
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto  # Auto-detect CPU cores
pytest -n 4     # Use 4 processes
```

## Writing Tests

### Test Structure

```python
# tests/unit/test_example.py
import pytest
from unittest.mock import Mock, patch
from src.example_module import ExampleClass

class TestExampleClass:
    """Test suite for ExampleClass."""
    
    @pytest.fixture
    def example_instance(self):
        """Create ExampleClass instance for testing."""
        return ExampleClass(config={'setting': 'value'})
    
    def test_basic_functionality(self, example_instance):
        """Test basic functionality."""
        # Arrange
        input_data = {'key': 'value'}
        expected_result = 'expected_output'
        
        # Act
        result = example_instance.process(input_data)
        
        # Assert
        assert result == expected_result
    
    def test_error_handling(self, example_instance):
        """Test error handling."""
        with pytest.raises(ValueError, match="Invalid input"):
            example_instance.process(None)
    
    @patch('src.example_module.external_service')
    def test_external_service_integration(self, mock_service, example_instance):
        """Test integration with external service."""
        # Mock external service
        mock_service.call.return_value = {'status': 'success'}
        
        result = example_instance.call_external_service()
        
        assert result['status'] == 'success'
        mock_service.call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_functionality(self, example_instance):
        """Test asynchronous functionality."""
        result = await example_instance.async_process()
        assert result is not None
    
    @pytest.mark.parametrize("input_value,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
    ])
    def test_parametrized(self, example_instance, input_value, expected):
        """Test with multiple parameter sets."""
        result = example_instance.double(input_value)
        assert result == expected
```

### Test Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.config import TestConfig

@pytest.fixture(scope="session")
def test_config():
    """Test configuration."""
    return TestConfig()

@pytest.fixture(scope="session")
def test_engine(test_config):
    """Create test database engine."""
    engine = create_engine(test_config.DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_db(test_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_strategy_data():
    """Sample strategy data for testing."""
    return {
        'name': 'Test Strategy',
        'description': 'A test strategy for unit testing',
        'parameters': {
            'risk_level': 'medium',
            'time_horizon': '1d',
            'max_positions': 5
        }
    }
```

### Test Markers

```python
# pytest.ini
[tool:pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    security: Security tests
    performance: Performance tests
    ai: AI/ML related tests
    database: Database tests
    api: API tests
    frontend: Frontend tests

# Usage in tests
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.slow
@pytest.mark.integration
def test_slow_integration():
    pass
```

## Performance Testing

### Using the Benchmark Suite

```python
# tests/performance/test_custom_benchmark.py
from tests.performance.test_benchmark import PerformanceBenchmark
import time

class TestCustomPerformance:
    """Custom performance tests."""
    
    def test_algorithm_performance(self):
        """Test algorithm performance."""
        benchmark = PerformanceBenchmark()
        
        def algorithm_to_test():
            # Your algorithm here
            time.sleep(0.1)  # Simulate work
            return "result"
        
        # Measure performance
        result = benchmark.measure_execution_time(
            algorithm_to_test,
            iterations=10
        )
        
        assert result['avg_time'] < 0.2  # Should complete in < 200ms
        assert result['memory_usage'] < 100  # Should use < 100MB
    
    def test_concurrent_performance(self):
        """Test concurrent operation performance."""
        from tests.performance.test_benchmark import APIPerformanceTester
        
        tester = APIPerformanceTester()
        
        # Test concurrent API calls
        results = tester.test_concurrent_requests(
            endpoint="/api/strategies",
            concurrent_users=10,
            requests_per_user=5
        )
        
        assert results['avg_response_time'] < 1.0  # < 1 second
        assert results['error_rate'] < 0.05  # < 5% errors
```

### Performance Monitoring

```python
# src/monitoring/performance.py
import time
import psutil
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            execution_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            # Log performance metrics
            print(f"Function {func.__name__}:")
            print(f"  Execution time: {execution_time:.4f}s")
            print(f"  Memory used: {memory_used / 1024 / 1024:.2f}MB")
    
    return wrapper

# Usage
@monitor_performance
def expensive_operation():
    # Your code here
    pass
```

## Security Testing

### Input Validation Tests

```python
# tests/security/test_input_validation.py
import pytest
from src.api.validators import validate_strategy_input

class TestInputValidation:
    """Test input validation security."""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        malicious_inputs = [
            "'; DROP TABLE strategies; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM users; --"
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(ValueError, match="Invalid input"):
                validate_strategy_input({'name': malicious_input})
    
    def test_xss_prevention(self):
        """Test XSS prevention."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            with pytest.raises(ValueError, match="Invalid input"):
                validate_strategy_input({'description': payload})
    
    def test_path_traversal_prevention(self):
        """Test path traversal prevention."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM"
        ]
        
        for path in malicious_paths:
            with pytest.raises(ValueError, match="Invalid path"):
                validate_strategy_input({'file_path': path})
```

### Authentication Tests

```python
# tests/security/test_authentication.py
import pytest
from src.auth.security import hash_password, verify_password, generate_token

class TestAuthentication:
    """Test authentication security."""
    
    def test_password_hashing(self):
        """Test password hashing security."""
        password = "secure_password_123"
        
        # Hash password
        hashed = hash_password(password)
        
        # Verify hash properties
        assert hashed != password  # Should not store plain text
        assert len(hashed) >= 60   # Bcrypt hash length
        assert hashed.startswith('$2b$')  # Bcrypt identifier
        
        # Verify password verification works
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
    
    def test_token_generation(self):
        """Test JWT token generation."""
        user_data = {'user_id': 123, 'email': 'test@example.com'}
        
        token = generate_token(user_data)
        
        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long
        assert '.' in token     # JWT has dots separating sections
    
    def test_weak_password_rejection(self):
        """Test weak password rejection."""
        weak_passwords = [
            "123456",
            "password",
            "qwerty",
            "abc123",
            "password123"
        ]
        
        for weak_password in weak_passwords:
            with pytest.raises(ValueError, match="Password too weak"):
                hash_password(weak_password)
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio pytest-mock
    
    - name: Validate test framework
      run: python validate_test_framework.py --verbose
    
    - name: Run unit tests
      run: pytest tests/unit/ -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: pytest tests/integration/ -v
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
    
    - name: Run security tests
      run: pytest tests/security/ -v
    
    - name: Run performance tests
      run: pytest tests/performance/ -v --benchmark-only
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Generate test report
      run: |
        pytest --html=report.html --self-contained-html
      if: always()
    
    - name: Upload test report
      uses: actions/upload-artifact@v3
      with:
        name: test-report-${{ matrix.python-version }}
        path: report.html
      if: always()
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
  
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit/ -x
        language: system
        pass_filenames: false
        always_run: true
```

## Best Practices

### 1. Test Organization

- **One test class per production class**
- **Descriptive test names** that explain what is being tested
- **Group related tests** using test classes
- **Use fixtures** for common setup and teardown

### 2. Test Data Management

```python
# Use factories for test data
from tests.fixtures.test_factories import StrategyFactory

def test_strategy_creation():
    strategy = StrategyFactory.create(
        name="Test Strategy",
        risk_level="medium"
    )
    assert strategy.name == "Test Strategy"

# Use fixtures for database setup
@pytest.fixture
def clean_database(test_db):
    """Ensure clean database state."""
    # Clean up before test
    test_db.query(Strategy).delete()
    test_db.commit()
    yield test_db
    # Clean up after test
    test_db.query(Strategy).delete()
    test_db.commit()
```

### 3. Mocking Best Practices

```python
# Mock external dependencies
@patch('src.services.external_api.requests.get')
def test_api_integration(mock_get):
    mock_get.return_value.json.return_value = {'status': 'success'}
    mock_get.return_value.status_code = 200
    
    result = call_external_api()
    
    assert result['status'] == 'success'
    mock_get.assert_called_once()

# Use dependency injection for easier testing
class StrategyService:
    def __init__(self, api_client=None):
        self.api_client = api_client or DefaultAPIClient()
    
    def get_market_data(self):
        return self.api_client.fetch_data()

# Test with mock client
def test_strategy_service():
    mock_client = Mock()
    mock_client.fetch_data.return_value = {'price': 50000}
    
    service = StrategyService(api_client=mock_client)
    data = service.get_market_data()
    
    assert data['price'] == 50000
```

### 4. Async Testing

```python
# Test async functions
@pytest.mark.asyncio
async def test_async_strategy_execution():
    strategy = AsyncStrategy()
    result = await strategy.execute()
    assert result is not None

# Test async context managers
@pytest.mark.asyncio
async def test_async_context_manager():
    async with AsyncDatabaseConnection() as conn:
        result = await conn.execute_query("SELECT 1")
        assert result == 1
```

### 5. Error Testing

```python
# Test expected exceptions
def test_invalid_input_raises_error():
    with pytest.raises(ValueError, match="Invalid strategy name"):
        create_strategy(name="")

# Test error handling
def test_api_error_handling():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.ConnectionError("Network error")
        
        result = fetch_market_data()
        
        assert result is None  # Should handle error gracefully
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Problem: ModuleNotFoundError
# Solution: Add src to Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Or use pytest.ini
[tool:pytest]
python_paths = [
    "src"
]
```

#### 2. Database Connection Issues

```python
# Problem: Database connection fails in tests
# Solution: Use test database configuration

# tests/conftest.py
@pytest.fixture(scope="session")
def test_database_url():
    return "sqlite:///:memory:"  # Use in-memory database

# Or use environment variables
import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
```

#### 3. Async Test Issues

```python
# Problem: RuntimeError: There is no current event loop
# Solution: Use pytest-asyncio

# Install pytest-asyncio
pip install pytest-asyncio

# Configure in pytest.ini
[tool:pytest]
asyncio_mode = auto
```

#### 4. Fixture Scope Issues

```python
# Problem: Fixture not cleaning up properly
# Solution: Use appropriate scope and cleanup

@pytest.fixture(scope="function")  # New instance per test
def clean_database():
    db = create_test_database()
    yield db
    db.cleanup()  # Always cleanup
```

### Debug Commands

```bash
# Run tests with debugging
pytest --pdb  # Drop into debugger on failure
pytest --pdbcls=IPython.terminal.debugger:Pdb  # Use IPython debugger

# Run specific test with verbose output
pytest tests/unit/test_strategy.py::test_create_strategy -v -s

# Show test discovery
pytest --collect-only

# Show fixtures
pytest --fixtures

# Run tests with coverage and show missing lines
pytest --cov=src --cov-report=term-missing
```

### Performance Debugging

```bash
# Profile test execution
pytest --profile

# Show slowest tests
pytest --durations=10

# Run tests with memory profiling
pytest --memray
```

## Conclusion

This testing framework provides comprehensive coverage for AI-driven cryptocurrency analysis platforms, supporting both coding agents and full-stack development workflows. The framework emphasizes:

- **Comprehensive Testing**: Unit, integration, E2E, performance, and security tests
- **AI-Specific Patterns**: Testing patterns for AI models and agent behaviors
- **Full-Stack Coverage**: Frontend, backend, and database testing
- **Performance Monitoring**: Built-in performance benchmarking and monitoring
- **Security Focus**: Security testing and validation
- **CI/CD Integration**: Automated testing in continuous integration pipelines

For additional support or questions, refer to the [main documentation](../README.md) or create an issue in the project repository.