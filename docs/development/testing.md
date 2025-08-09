# Testing Framework

The CRY-A-4MCP Enhanced Templates package includes a comprehensive testing framework designed to ensure reliability, performance, and maintainability. This guide covers all aspects of testing from unit tests to end-to-end validation.

## 📋 Testing Overview

### Testing Philosophy
- **Test-Driven Development**: Write tests before implementation
- **Comprehensive Coverage**: Minimum 80% code coverage
- **Real-World Scenarios**: Tests reflect actual usage patterns
- **Performance Validation**: Tests include performance benchmarks
- **Regression Prevention**: All bugs must have corresponding tests

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **End-to-End Tests**: Full workflow validation
4. **Performance Tests**: Load and stress testing
5. **API Tests**: REST API endpoint validation

## 🏗️ Test Structure

### Directory Organization
```
tests/
├── unit/                     # Unit tests
│   ├── test_extractors.py    # Extractor logic tests
│   ├── test_crawlers.py      # Crawler functionality tests
│   ├── test_url_mappings.py  # URL mapping tests
│   ├── test_database.py      # Database operations tests
│   └── test_api_models.py    # Pydantic model tests
├── integration/              # Integration tests
│   ├── test_api_endpoints.py # API endpoint integration
│   ├── test_crawler_integration.py # Crawler workflow tests
│   ├── test_url_mapping_integration.py # URL mapping persistence
│   └── test_llm_integration.py # LLM provider integration
├── e2e/                      # End-to-end tests
│   ├── test_full_workflow.py # Complete user workflows
│   ├── test_ui_interactions.py # Frontend UI tests
│   └── test_data_pipeline.py # Data processing pipeline
├── performance/              # Performance tests
│   ├── test_crawler_performance.py # Crawler speed tests
│   ├── test_api_performance.py # API response time tests
│   └── test_load_testing.py # Load testing scenarios
├── fixtures/                 # Test data and fixtures
│   ├── sample_urls.json     # Sample URL configurations
│   ├── mock_responses.json  # Mock API responses
│   └── test_data.sql        # Test database data
├── mocks/                    # Mock implementations
│   ├── mock_llm_providers.py # Mock LLM responses
│   ├── mock_web_responses.py # Mock web page responses
│   └── mock_databases.py    # Mock database implementations
└── conftest.py              # Pytest configuration and fixtures
```

## 🧪 Unit Testing

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_extractors.py -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html

# Run tests matching pattern
pytest tests/unit/ -k "test_extractor" -v
```

### Unit Test Examples

#### Extractor Testing
```python
# tests/unit/test_extractors.py
import pytest
from src.extractors import LLMExtractor, CSSExtractor

class TestLLMExtractor:
    def test_extract_structured_data(self):
        """Test LLM extractor with structured data."""
        extractor = LLMExtractor(
            model="gpt-3.5-turbo",
            schema={"title": "string", "price": "number"}
        )
        
        html_content = "<h1>Bitcoin Price</h1><p>$45,000</p>"
        result = extractor.extract(html_content)
        
        assert "title" in result
        assert "price" in result
        assert result["title"] == "Bitcoin Price"
        assert result["price"] == 45000
    
    def test_extract_with_invalid_schema(self):
        """Test LLM extractor with invalid schema."""
        with pytest.raises(ValueError):
            LLMExtractor(schema="invalid_schema")

class TestCSSExtractor:
    def test_extract_with_css_selectors(self):
        """Test CSS extractor with valid selectors."""
        extractor = CSSExtractor({
            "title": "h1",
            "price": ".price"
        })
        
        html_content = '<h1>Bitcoin</h1><span class="price">$45,000</span>'
        result = extractor.extract(html_content)
        
        assert result["title"] == "Bitcoin"
        assert result["price"] == "$45,000"
```

#### Database Testing
```python
# tests/unit/test_database.py
import pytest
from src.database.url_configuration_db import URLConfigurationDatabase

@pytest.fixture
def db():
    """Create test database instance."""
    db = URLConfigurationDatabase(":memory:")  # In-memory SQLite
    db.init_db()
    yield db
    db.close()

class TestURLConfigurationDatabase:
    def test_create_url_config(self, db):
        """Test creating URL configuration."""
        config = {
            "url": "https://example.com",
            "profile": "Degen Gambler",
            "priority": 1,
            "scraping_difficulty": "Medium"
        }
        
        result = db.create_url_config(config)
        assert result["id"] is not None
        assert result["url"] == config["url"]
    
    def test_get_url_config(self, db):
        """Test retrieving URL configuration."""
        # Create test config
        config = db.create_url_config({
            "url": "https://test.com",
            "profile": "Gem Hunter"
        })
        
        # Retrieve config
        retrieved = db.get_url_config(config["id"])
        assert retrieved["url"] == "https://test.com"
        assert retrieved["profile"] == "Gem Hunter"
```

## 🔗 Integration Testing

### API Integration Tests

```bash
# Run integration tests
pytest tests/integration/ -v

# Run specific integration test
pytest tests/integration/test_url_mapping_integration.py -v

# Run with real backend (requires running server)
pytest tests/integration/ --backend-url http://localhost:4000
```

### Critical Integration Test: URL Mapping Persistence

```python
# tests/integration/test_url_mapping_integration.py
import asyncio
import aiohttp
import pytest

class TestURLMappingIntegration:
    """Test URL mapping persistence functionality."""
    
    @pytest.fixture
    async def client_session(self):
        """Create HTTP client session."""
        async with aiohttp.ClientSession() as session:
            yield session
    
    async def test_url_mapping_persistence(self, client_session):
        """Test critical URL mapping persistence issue."""
        base_url = "http://localhost:4000"
        
        # 1. Create URL mapping
        url_mapping_data = {
            "url_pattern": "https://example.com/*",
            "extractor_id": "test-extractor",
            "match_type": "pattern",
            "priority": 1
        }
        
        async with client_session.post(
            f"{base_url}/api/url-mappings/",
            json=url_mapping_data
        ) as response:
            assert response.status == 201
            url_mapping = await response.json()
            url_mapping_id = url_mapping["id"]
        
        # 2. Create crawler with URL mapping
        crawler_data = {
            "name": "Test Crawler",
            "description": "Integration test crawler",
            "urlMappingId": url_mapping_id,  # Frontend field
            "targetUrls": ["https://example.com/page1", "https://example.com/page2"]
        }
        
        async with client_session.post(
            f"{base_url}/api/crawlers/",
            json=crawler_data
        ) as response:
            assert response.status == 201
            crawler = await response.json()
            crawler_id = crawler["id"]
            
            # CRITICAL: Verify URL mapping data is not null
            assert crawler["url_mapping_id"] is not None
            assert crawler["target_urls"] is not None
            assert len(crawler["target_urls"]) == 2
        
        # 3. Verify persistence by retrieving crawler
        async with client_session.get(
            f"{base_url}/api/crawlers/{crawler_id}"
        ) as response:
            assert response.status == 200
            retrieved_crawler = await response.json()
            
            # CRITICAL: Verify data persisted correctly
            assert retrieved_crawler["url_mapping_id"] == url_mapping_id
            assert retrieved_crawler["target_urls"] == crawler_data["targetUrls"]
        
        # 4. Cleanup
        await client_session.delete(f"{base_url}/api/crawlers/{crawler_id}")
        await client_session.delete(f"{base_url}/api/url-mappings/{url_mapping_id}")
```

### LLM Integration Tests

```python
# tests/integration/test_llm_integration.py
import pytest
from src.llm.providers import OpenAIProvider, OpenRouterProvider

class TestLLMIntegration:
    """Test LLM provider integration."""
    
    @pytest.mark.asyncio
    async def test_openai_extraction(self):
        """Test OpenAI content extraction."""
        provider = OpenAIProvider(api_key="test-key")
        
        content = "Bitcoin price is $45,000 today."
        schema = {"cryptocurrency": "string", "price": "number"}
        
        # Mock the API response
        with patch.object(provider, '_make_request') as mock_request:
            mock_request.return_value = {
                "cryptocurrency": "Bitcoin",
                "price": 45000
            }
            
            result = await provider.extract_structured_data(content, schema)
            assert result["cryptocurrency"] == "Bitcoin"
            assert result["price"] == 45000
```

## 🎭 End-to-End Testing

### Full Workflow Tests

```python
# tests/e2e/test_full_workflow.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestFullWorkflow:
    """Test complete user workflows."""
    
    @pytest.fixture
    def driver(self):
        """Create web driver instance."""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_create_crawler_workflow(self, driver):
        """Test complete crawler creation workflow."""
        # 1. Navigate to application
        driver.get("http://localhost:5000")
        
        # 2. Navigate to crawlers page
        crawlers_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Crawlers"))
        )
        crawlers_link.click()
        
        # 3. Create new crawler
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.BUTTON, "Create Crawler"))
        )
        create_button.click()
        
        # 4. Fill crawler form
        name_input = driver.find_element(By.NAME, "name")
        name_input.send_keys("E2E Test Crawler")
        
        description_input = driver.find_element(By.NAME, "description")
        description_input.send_keys("End-to-end test crawler")
        
        # 5. Submit form
        submit_button = driver.find_element(By.TYPE, "submit")
        submit_button.click()
        
        # 6. Verify crawler was created
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        assert "Crawler created successfully" in success_message.text
```

## ⚡ Performance Testing

### Load Testing

```python
# tests/performance/test_load_testing.py
import asyncio
import aiohttp
import time
import pytest

class TestLoadTesting:
    """Test system performance under load."""
    
    @pytest.mark.asyncio
    async def test_api_load_performance(self):
        """Test API performance under concurrent load."""
        base_url = "http://localhost:4000"
        concurrent_requests = 50
        
        async def make_request(session):
            """Make single API request."""
            start_time = time.time()
            async with session.get(f"{base_url}/api/health") as response:
                await response.json()
                return time.time() - start_time
        
        async with aiohttp.ClientSession() as session:
            # Make concurrent requests
            tasks = [make_request(session) for _ in range(concurrent_requests)]
            response_times = await asyncio.gather(*tasks)
        
        # Verify performance metrics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 0.5  # Average response time < 500ms
        assert max_response_time < 2.0  # Max response time < 2s
        assert len(response_times) == concurrent_requests
    
    @pytest.mark.asyncio
    async def test_crawler_performance(self):
        """Test crawler performance with multiple URLs."""
        from src.crawlers import GenericAsyncCrawler
        
        urls = [
            "https://httpbin.org/json",
            "https://httpbin.org/html",
            "https://httpbin.org/xml"
        ] * 10  # 30 URLs total
        
        crawler = GenericAsyncCrawler(concurrency=5)
        
        start_time = time.time()
        results = await crawler.crawl_urls(urls)
        total_time = time.time() - start_time
        
        # Performance assertions
        assert len(results) == len(urls)
        assert total_time < 30  # Should complete within 30 seconds
        
        # Calculate throughput
        throughput = len(urls) / total_time
        assert throughput > 1  # At least 1 URL per second
```

## 🔧 Test Configuration

### Pytest Configuration

```python
# tests/conftest.py
import pytest
import asyncio
import os
from unittest.mock import Mock

# Test environment setup
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""
    mock = Mock()
    mock.extract_structured_data.return_value = {
        "title": "Test Title",
        "content": "Test Content"
    }
    return mock

@pytest.fixture
def sample_url_config():
    """Sample URL configuration for testing."""
    return {
        "url": "https://example.com",
        "profile": "Degen Gambler",
        "priority": 1,
        "scraping_difficulty": "Medium",
        "api_available": False,
        "cost_analysis": "Low cost, high value"
    }

@pytest.fixture
def sample_extractor_config():
    """Sample extractor configuration for testing."""
    return {
        "name": "Test Extractor",
        "type": "llm",
        "model": "gpt-3.5-turbo",
        "schema": {
            "title": "string",
            "price": "number",
            "description": "string"
        },
        "instructions": "Extract cryptocurrency information"
    }
```

### Test Environment Variables

```bash
# .env.test
TESTING=true
DATABASE_URL=sqlite:///:memory:
OPENAI_API_KEY=test-key
OPENROUTER_API_KEY=test-key
GROQ_API_KEY=test-key
LOG_LEVEL=DEBUG
DISABLE_AUTH=true
```

## 📊 Test Coverage

### Coverage Requirements
- **Overall Coverage**: Minimum 80%
- **Critical Components**: 90%+ coverage
- **New Features**: 100% coverage required
- **Bug Fixes**: Must include regression tests

### Generating Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/

# Generate terminal coverage report
pytest --cov=src --cov-report=term-missing tests/

# Generate XML coverage report (for CI)
pytest --cov=src --cov-report=xml tests/

# Coverage with branch analysis
pytest --cov=src --cov-branch --cov-report=html tests/
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = src/
omit = 
    */tests/*
    */venv/*
    */migrations/*
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

## 🚀 Running Tests in CI/CD

### GitHub Actions Configuration

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:alpine
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: pytest tests/unit/ --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: pytest tests/integration/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## 🆘 Troubleshooting Tests

### Common Test Issues

#### Test Database Issues
```bash
# Reset test database
rm -f test_database.db
python -c "from tests.conftest import init_test_db; init_test_db()"
```

#### Async Test Issues
```python
# Ensure proper async test setup
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

#### Mock Issues
```python
# Proper mock setup
with patch('src.module.function') as mock_func:
    mock_func.return_value = expected_value
    result = function_under_test()
    assert result == expected_result
```

### Test Debugging

```bash
# Run tests with verbose output
pytest -v -s tests/

# Run specific test with debugging
pytest -v -s tests/unit/test_extractors.py::TestLLMExtractor::test_extract_structured_data

# Run tests with pdb debugging
pytest --pdb tests/

# Run tests with custom markers
pytest -m "slow" tests/  # Run only slow tests
pytest -m "not slow" tests/  # Skip slow tests
```

---

**Next Steps**: Learn about [Debugging Procedures](./debugging.md) for troubleshooting development issues.