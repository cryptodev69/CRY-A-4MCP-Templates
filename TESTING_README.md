# CRY-A-4MCP Testing Framework

A comprehensive testing framework for the CRY-A-4MCP (Crypto AI 4 Model Context Protocol) platform, providing robust test coverage across unit, integration, end-to-end, performance, and security testing.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Configuration](#configuration)
- [CI/CD Integration](#cicd-integration)
- [Coverage Reports](#coverage-reports)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This testing framework implements a comprehensive test pyramid approach:

- **60% Unit Tests**: Fast, isolated component testing
- **30% Integration Tests**: API and service integration testing
- **10% End-to-End Tests**: Complete user workflow testing
- **Performance Tests**: Load, stress, and benchmark testing
- **Security Tests**: Vulnerability and penetration testing

### Current Test Coverage

- **41 test files** across different test types
- **Target coverage**: 85%+ for critical paths
- **Performance benchmarks**: Response time < 200ms
- **Security validation**: OWASP Top 10 compliance

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.9+ required
python --version

# Install dependencies
make install-dev

# Or manually
pip install -e ".[dev,test]"
```

### Run All Tests

```bash
# Using Makefile (recommended)
make test

# Using test runner directly
python run_tests.py --suite all --verbose

# Using pytest directly
pytest tests/ -v
```

### Quick Health Check

```bash
# Run fast tests only
make test-fast

# Run critical functionality tests
make test-critical

# Quick development check
make quick-check
python run_tests.py --backend-url http://localhost:4001
```

## 📁 Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── factories.py                # Test data factories
├── unit/                       # Unit tests (60%)
│   ├── test_url_configuration.py
│   ├── test_strategy_manager.py
│   ├── test_crawler_service.py
│   └── ...
├── integration/                # Integration tests (30%)
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   ├── test_external_services.py
│   └── ...
├── e2e/                       # End-to-end tests (10%)
│   ├── test_user_workflows.py
│   ├── test_complete_scenarios.py
│   └── ...
├── performance/               # Performance tests
│   ├── test_load_testing.py
│   ├── test_stress_testing.py
│   └── test_benchmarks.py
├── security/                  # Security tests
│   ├── test_security_validation.py
│   ├── test_authentication.py
│   └── test_authorization.py
└── fixtures/                  # Test data and fixtures
    ├── sample_data.json
    ├── mock_responses/
    └── test_configs/
```

## 🏃‍♂️ Running Tests

### By Test Suite

```bash
# Unit tests
make test-unit
python run_tests.py --suite unit

# Integration tests
make test-integration
python run_tests.py --suite integration

# End-to-end tests
make test-e2e
python run_tests.py --suite e2e

# Performance tests
make test-performance
python run_tests.py --suite performance

# Security tests
make test-security
python run_tests.py --suite security
```

### By Test Markers

```bash
# Fast tests (< 1 second)
pytest -m "fast"

# Slow tests (> 5 seconds)
pytest -m "slow"

# Smoke tests
pytest -m "smoke"

# Regression tests
pytest -m "regression"

# Critical functionality
pytest -m "critical"
```

### Parallel Execution

```bash
# Run tests in parallel
make test-parallel
python run_tests.py --suite all --parallel

# Specify number of workers
pytest -n 4 tests/
```

### Debugging Tests

```bash
# Run with debugging
make test-debug

# Run specific test with pdb
pytest tests/unit/test_url_configuration.py::test_create_url_config --pdb

# Verbose output
pytest -vvv -s tests/
```

## 🧪 Test Types

### Unit Tests

**Location**: `tests/unit/`
**Purpose**: Test individual components in isolation
**Speed**: Fast (< 1 second per test)
**Coverage**: 60% of total tests

```python
# Example unit test
def test_url_configuration_validation():
    config = URLConfigurationFactory()
    assert config.is_valid()
    assert config.url.startswith('http')
```

**Key Features**:
- Mocked external dependencies
- Fast execution
- High code coverage
- Isolated component testing

### Integration Tests

**Location**: `tests/integration/`
**Purpose**: Test component interactions and API endpoints
**Speed**: Medium (1-5 seconds per test)
**Coverage**: 30% of total tests

```python
# Example integration test
def test_api_create_url_configuration(test_client):
    response = test_client.post('/api/v1/urls', json={
        'url': 'https://example.com',
        'strategy': 'default'
    })
    assert response.status_code == 201
```

**Key Features**:
- Real database connections
- API endpoint testing
- Service integration
- External service mocking

### End-to-End Tests

**Location**: `tests/e2e/`
**Purpose**: Test complete user workflows
**Speed**: Slow (5+ seconds per test)
**Coverage**: 10% of total tests

```python
# Example E2E test
def test_complete_crawling_workflow(test_client):
    # Create user
    user = create_test_user()
    
    # Configure URL
    url_config = create_url_configuration(user)
    
    # Trigger crawl
    crawl_result = trigger_crawl(url_config)
    
    # Verify results
    assert crawl_result.status == 'completed'
```

**Key Features**:
- Complete user journeys
- Real browser automation (when applicable)
- Full system integration
- Production-like scenarios

### Performance Tests

**Location**: `tests/performance/`
**Purpose**: Validate system performance and scalability
**Metrics**: Response time, throughput, resource usage

```python
# Example performance test
def test_api_response_time(test_client):
    start_time = time.time()
    response = test_client.get('/api/v1/health')
    duration = time.time() - start_time
    
    assert response.status_code == 200
    assert duration < 0.2  # 200ms threshold
```

**Key Features**:
- Load testing
- Stress testing
- Memory profiling
- Benchmark comparisons

### Security Tests

**Location**: `tests/security/`
**Purpose**: Validate security controls and identify vulnerabilities
**Scope**: Authentication, authorization, input validation

```python
# Example security test
def test_sql_injection_protection(test_client):
    malicious_input = "'; DROP TABLE users; --"
    response = test_client.get(f'/api/v1/search?q={malicious_input}')
    
    # Should not cause server error
    assert response.status_code in [200, 400]
```

**Key Features**:
- Input validation testing
- Authentication bypass attempts
- Authorization checks
- OWASP Top 10 coverage

## ⚙️ Configuration

### pytest.ini

Main pytest configuration file:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

### Test Markers

Custom markers for test categorization:

```python
# pytest.ini markers
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    security: Security tests
    fast: Fast tests (< 1 second)
    slow: Slow tests (> 5 seconds)
    smoke: Smoke tests
    regression: Regression tests
    critical: Critical functionality tests
```

### Environment Variables

```bash
# Test environment configuration
TEST_ENV=true
DATABASE_URL=postgresql://testuser:testpass@localhost:5432/testdb
REDIS_URL=redis://localhost:6379
LOG_LEVEL=DEBUG
HEADLESS=true  # For browser tests
```

## 🔄 CI/CD Integration

### GitHub Actions

The framework integrates with GitHub Actions for automated testing:

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

### Test Execution Matrix

- **Python versions**: 3.9, 3.10, 3.11, 3.12
- **Test suites**: Unit, Integration, E2E, Performance, Security
- **Services**: Redis, PostgreSQL
- **Environments**: Development, Staging, Production

### Workflow Triggers

1. **Push to main/develop**: Full test suite
2. **Pull requests**: Core tests + security
3. **Scheduled**: Performance + regression tests
4. **Manual**: Configurable test suite selection

## 📊 Coverage Reports

### Generating Reports

```bash
# Generate all coverage reports
make coverage

# HTML report (recommended)
coverage html
open coverage/html/index.html

# Terminal report
coverage report --show-missing

# JSON report (for CI)
coverage json

# XML report (for external tools)
coverage xml
```

### Coverage Targets

- **Overall**: 85%+
- **Critical paths**: 95%+
- **New code**: 90%+
- **Security modules**: 100%

### Coverage Analysis

```bash
# View coverage by file
coverage report --sort=cover

# Find uncovered lines
coverage report --show-missing

# Coverage diff (for PRs)
coverage-diff coverage.xml main-coverage.xml
```

## 📈 Performance Monitoring

### Benchmarks

```bash
# Run performance benchmarks
make benchmark

# Profile memory usage
make profile

# Load testing
make load-test
```

### Performance Thresholds

- **API Response Time**: < 200ms (95th percentile)
- **Database Queries**: < 50ms average
- **Memory Usage**: < 512MB peak
- **Concurrent Users**: 100+ simultaneous

### Monitoring Integration

- **Prometheus metrics**: `/metrics` endpoint
- **Grafana dashboards**: Performance visualization
- **Alerting**: Performance degradation alerts

## 🛡️ Security Testing

### Security Test Categories

1. **Authentication Tests**
   - Password security
   - JWT token validation
   - Session management

2. **Authorization Tests**
   - Role-based access control
   - Resource ownership
   - API scope validation

3. **Input Validation Tests**
   - SQL injection
   - XSS prevention
   - Command injection
   - Path traversal

4. **Data Protection Tests**
   - Sensitive data masking
   - Encryption at rest
   - PII handling

### Security Tools Integration

```bash
# Security vulnerability scan
make security

# Bandit security linter
bandit -r src/

# Safety dependency check
safety check

# Pip audit
pip-audit
```

## 🎯 Best Practices

### Test Writing Guidelines

1. **Follow AAA Pattern**:
   ```python
   def test_example():
       # Arrange
       user = UserFactory()
       
       # Act
       result = user.perform_action()
       
       # Assert
       assert result.is_successful
   ```

2. **Use Descriptive Names**:
   ```python
   # Good
   def test_user_cannot_access_other_users_data():
       pass
   
   # Bad
   def test_user_access():
       pass
   ```

3. **Test One Thing**:
   ```python
   # Good - focused test
   def test_password_validation_requires_minimum_length():
       pass
   
   def test_password_validation_requires_special_characters():
       pass
   
   # Bad - testing multiple things
   def test_password_validation():
       pass
   ```

### Test Data Management

1. **Use Factories**: Leverage `factory-boy` for test data generation
2. **Isolate Tests**: Each test should be independent
3. **Clean Up**: Use fixtures for setup/teardown
4. **Realistic Data**: Use `Faker` for realistic test data

### Performance Considerations

1. **Fast Feedback**: Keep unit tests under 1 second
2. **Parallel Execution**: Use `pytest-xdist` for parallel runs
3. **Test Isolation**: Avoid shared state between tests
4. **Resource Management**: Clean up resources after tests

## 🔧 Troubleshooting

### Common Issues

#### Test Discovery Problems

```bash
# Check test discovery
pytest --collect-only

# Verify test paths
pytest --verbose tests/
```

#### Database Connection Issues

```bash
# Check database connectivity
psql -h localhost -U testuser -d testdb

# Reset test database
make clean-db
make setup-test-db
```

#### Redis Connection Issues

```bash
# Check Redis connectivity
redis-cli ping

# Start Redis (macOS)
brew services start redis

# Start Redis (Docker)
docker run -d -p 6379:6379 redis:7-alpine
```

#### Coverage Issues

```bash
# Clear coverage data
coverage erase

# Regenerate coverage
coverage run -m pytest
coverage report
```

### Debug Mode

```bash
# Run tests with debugging
pytest --pdb tests/unit/test_example.py

# Add breakpoint in code
import pdb; pdb.set_trace()

# Use pytest debugging
pytest --pdbcls=IPython.terminal.debugger:Pdb
```

### Logging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
pytest -s tests/

# View test logs
tail -f test_reports/test.log
```

## 📚 Additional Resources

### Documentation

- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Faker Documentation](https://faker.readthedocs.io/)

### Related Files

- [`TESTING_STRATEGY_IMPLEMENTATION.md`](./TESTING_STRATEGY_IMPLEMENTATION.md) - Detailed implementation strategy
- [`CODEBASE_AUDIT_REPORT.md`](./CODEBASE_AUDIT_REPORT.md) - Code quality analysis
- [`CODE_DUPLICATION_ANALYSIS.md`](./CODE_DUPLICATION_ANALYSIS.md) - Duplication analysis
- [`pytest.ini`](./pytest.ini) - Pytest configuration
- [`run_tests.py`](./run_tests.py) - Test runner script
- [`Makefile`](./Makefile) - Build and test commands

### Support

For questions or issues with the testing framework:

1. Check the troubleshooting section above
2. Review the test logs in `test_reports/`
3. Check the CI/CD pipeline status
4. Consult the team documentation

---

**Happy Testing! 🧪✨**

*This testing framework is designed to ensure the highest quality and reliability of the CRY-A-4MCP platform. Regular updates and improvements are made based on testing feedback and evolving best practices.*

## 🧪 Test Coverage

The integration tests cover the following scenarios:

### 1. Backend Health Check
- Verifies backend server is running and responsive
- Tests basic connectivity

### 2. URL Mapping Creation
- Creates a test URL mapping via API
- Validates response structure and ID generation
- Tests data persistence

### 3. Crawler Creation with URL Mapping
- Creates a crawler with URL mapping reference
- **CRITICAL**: Tests if `urlMappingId` and `targetUrls` from frontend are properly stored
- Validates that `url_mapping_id` and `target_urls` are not null in response

### 4. URL Mapping Persistence Verification
- Retrieves created crawler and verifies URL mapping data persists
- **CRITICAL**: Checks if `url_mapping_id` and `target_urls` fields contain expected values
- Tests JSON serialization/deserialization of URL arrays

### 5. Crawler List Validation
- Verifies crawler list endpoint includes URL mapping data
- Tests data consistency across different API endpoints

### 6. Update Operations
- Tests updating crawler URL mapping configuration
- Validates that updates persist correctly

### 7. Cleanup
- Removes test data to avoid pollution
- Tests delete operations

## 📊 Expected Test Results

### ✅ If URL Mapping Persistence is Working
```
✅ Backend Health Check: PASS
✅ Create URL Mapping: PASS
✅ Create Crawler with URL Mapping: PASS
✅ Retrieve Crawler - URL Mapping Persistence: PASS
✅ Crawler List - URL Mapping Data: PASS
✅ Update Crawler URL Mapping: PASS
✅ Cleanup Test Data: PASS

📊 TEST SUMMARY
============================================================
Total Tests: 7
✅ Passed: 7
❌ Failed: 0
⏭️ Skipped: 0
Success Rate: 100.0%

✅ ALL INTEGRATION TESTS PASSED - URL mapping persistence is working correctly!
```

### ❌ If URL Mapping Persistence is Broken
```
✅ Backend Health Check: PASS
✅ Create URL Mapping: PASS
❌ Create Crawler with URL Mapping: FAIL
   Error: URL mapping data not properly stored. Got: url_mapping_id=None, target_urls=None
⏭️ Retrieve Crawler - URL Mapping Persistence: SKIP
⏭️ Crawler List - URL Mapping Data: SKIP
⏭️ Update Crawler URL Mapping: SKIP
✅ Cleanup Test Data: PASS

📊 TEST SUMMARY
============================================================
Total Tests: 7
✅ Passed: 3
❌ Failed: 1
⏭️ Skipped: 3
Success Rate: 42.9%

🔍 FAILED TESTS:
  • Create Crawler with URL Mapping: URL mapping data not properly stored. Got: url_mapping_id=None, target_urls=None

❌ INTEGRATION TESTS FAILED - URL mapping persistence is not working correctly!
```

## 🔧 Debugging Failed Tests

### Common Issues and Solutions

#### 1. Backend Not Running
```
❌ Backend Health Check: FAIL
   Error: Cannot connect to backend: Connection refused
```
**Solution**: Start the backend server on `localhost:4001`

#### 2. URL Mapping Data Not Persisting
```
❌ Create Crawler with URL Mapping: FAIL
   Error: URL mapping data not properly stored. Got: url_mapping_id=None, target_urls=None
```
**This is the critical issue!** Check:
- `web_api.py` - ensure `urlMappingId` and `targetUrls` are correctly mapped
- `crawler_db.py` - verify `url_mapping_id` and `target_urls` are in SQL statements
- Database schema - ensure columns exist and accept the data types

#### 3. JSON Serialization Issues
```
❌ Retrieve Crawler - URL Mapping Persistence: FAIL
   Error: target_urls is not valid JSON: ["url1", "url2"]
```
**Solution**: Check JSON encoding/decoding in database operations

## 🛠️ Manual Testing

If automated tests fail, you can manually test using curl:

### 1. Create URL Mapping
```bash
curl -X POST http://localhost:4001/api/url-mappings \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Manual Test Mapping",
    "urls": ["https://test.com"],
    "extractor_ids": ["cryptoinvestorllmextractionstrategy"]
  }'
```

### 2. Create Crawler with URL Mapping
```bash
curl -X POST http://localhost:4001/api/crawlers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Manual Test Crawler",
    "crawler_type": "llm",
    "urlMappingId": "<mapping_id_from_step_1>",
    "targetUrls": ["https://test.com/page1"]
  }'
```

### 3. Verify Persistence
```bash
curl http://localhost:4001/api/crawlers/<crawler_id_from_step_2>
```

Check if the response contains non-null values for `url_mapping_id` and `target_urls`.

## 📝 Test Data Structure

The tests use the following data structures:

### URL Mapping
```json
{
  "name": "Test Integration Mapping",
  "description": "Test mapping for integration testing",
  "urls": ["https://test-crypto-news.com", "https://test-market-data.com"],
  "extractor_ids": ["cryptoinvestorllmextractionstrategy", "xcryptohunterllmextractionstrategy"],
  "priority": 1,
  "rate_limit": 2,
  "crawler_settings": {
    "timeout": 30,
    "retry_attempts": 3,
    "user_agent": "CRY-A-4MCP-Test/1.0"
  }
}
```

### Crawler with URL Mapping
```json
{
  "name": "Test Integration Crawler",
  "description": "Test crawler with URL mapping integration",
  "crawler_type": "llm",
  "is_active": true,
  "urlMappingId": "<generated_mapping_id>",
  "targetUrls": ["https://test-crypto-news.com/latest", "https://test-market-data.com/prices"],
  "config": {
    "timeout": 30,
    "retry_attempts": 3,
    "concurrent_requests": 5
  }
}
```

## 🎯 Success Criteria

The URL mapping persistence is considered **WORKING** when:

1. ✅ All 7 integration tests pass
2. ✅ `url_mapping_id` field contains the correct mapping ID (not null)
3. ✅ `target_urls` field contains the correct URL array (not null/empty)
4. ✅ Data persists across API calls (create → retrieve → list)
5. ✅ Updates to URL mapping data work correctly
6. ✅ No data loss during frontend-backend communication

## 🚨 Current Status

As documented in `CRY-A-4MCP_Crawler_Architecture_README.md`, the URL mapping persistence is currently **BROKEN**. These tests will help identify exactly where the data flow is failing and validate when the issue is resolved.

---

**Run these tests after any changes to URL mapping functionality to ensure the critical persistence issue is resolved!**