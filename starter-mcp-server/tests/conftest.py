"""Global test configuration and fixtures.

This module provides shared fixtures and configuration for all tests,
ensuring consistent test setup and teardown across the entire test suite.
"""

import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import application modules
try:
    from src.cry_a_4mcp.web_api import app
except ImportError:
    # Fallback for testing
    app = None

try:
    from src.database import get_db_session
except ImportError:
    # Mock for testing
    def get_db_session():
        return None

try:
    from src.url_mapping_service.models import Base
except ImportError:
    # Fallback for testing
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Create test settings with in-memory database."""
    return {
        "database_url": "sqlite:///:memory:",
        "environment": "test",
        "log_level": "ERROR",
        "enable_metrics": False,
        "openrouter_api_key": "test-key",
    }


@pytest.fixture(scope="session")
def test_engine(test_settings):
    """Create test database engine."""
    engine = create_engine(
        test_settings["database_url"],
        connect_args={"check_same_thread": False},
        echo=False,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Clean up
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def test_db_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session with automatic rollback."""
    TestSessionLocal = sessionmaker(bind=test_engine)
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_client(test_db_session, test_settings) -> Generator[TestClient, None, None]:
    """Create a test FastAPI client with dependency overrides."""
    if app is None:
        # Create a mock app for testing
        from fastapi import FastAPI
        test_app = FastAPI()
        
        @test_app.get("/health")
        def health_check():
            return {"status": "ok"}
            
        with TestClient(test_app) as client:
            yield client
        return
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def async_test_client(test_db_session, test_settings) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async test client for testing async endpoints."""
    if app is None:
        # Create a mock app for testing
        from fastapi import FastAPI
        test_app = FastAPI()
        
        @test_app.get("/health")
        def health_check():
            return {"status": "ok"}
            
        async with httpx.AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
        return
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_url_config():
    """Sample URL configuration data for testing."""
    return {
        "name": "Test Crypto News",
        "url": "https://test-crypto-news.com",
        "description": "Test cryptocurrency news source",
        "category": "news",
        "extraction_strategy": "news_article",
        "update_frequency": "hourly",
        "is_active": True,
        "tags": ["test", "crypto", "news"],
        "metadata": {
            "source_type": "rss",
            "language": "en"
        }
    }


@pytest.fixture
def sample_url_mapping():
    """Sample URL mapping data for testing."""
    return {
        "url_pattern": "https://test-exchange.com/api/v1/*",
        "name": "Test Exchange Mapping",
        "extractor_ids": ["crypto_price_extractor", "market_data_extractor"],
        "rate_limit": 60,
        "priority": 1,
        "crawler_settings": {
            "delay": 1.0,
            "timeout": 30,
            "user_agent": "TestBot/1.0"
        },
        "validation_rules": {
            "required_fields": ["price", "volume"],
            "min_content_length": 50
        },
        "is_active": True,
        "tags": ["test", "exchange", "api"],
        "notes": "Test mapping for API endpoints",
        "category": "exchange"
    }


@pytest.fixture
def sample_extractor():
    """Sample extractor data for testing."""
    return {
        "name": "Test Price Extractor",
        "description": "Extracts cryptocurrency prices",
        "extractor_type": "price",
        "config": {
            "selectors": {
                "price": ".price-value",
                "currency": ".currency-symbol"
            },
            "output_format": "json"
        },
        "is_active": True,
        "tags": ["test", "price", "crypto"]
    }


@pytest.fixture
def sample_crawler():
    """Sample crawler data for testing."""
    return {
        "name": "Test Crypto Crawler",
        "description": "Test crawler for cryptocurrency data",
        "url_mapping_ids": [],
        "extraction_strategies": ["crypto_price_extractor", "sentiment_analyzer"],
        "schedule": "0 */6 * * *",
        "is_active": True,
        "config": {
            "max_concurrent_requests": 5,
            "request_delay": 2.0,
            "timeout": 30
        },
        "tags": ["test", "crawler", "crypto"]
    }


@pytest.fixture
def mock_openrouter_response():
    """Mock OpenRouter API response for testing."""
    return {
        "data": [
            {
                "id": "openai/gpt-4",
                "name": "GPT-4",
                "description": "OpenAI's most capable model",
                "pricing": {
                    "prompt": "0.00003",
                    "completion": "0.00006"
                },
                "context_length": 8192,
                "architecture": {
                    "modality": "text",
                    "tokenizer": "cl100k_base"
                }
            }
        ]
    }


class TestDataFactory:
    """Factory class for creating test data with variations."""
    
    @staticmethod
    def create_url_config(name_suffix="", **overrides):
        """Create a URL configuration with optional overrides."""
        base_data = {
            "name": f"Test Config {name_suffix}",
            "url": f"https://test-{name_suffix.lower().replace(' ', '-')}.com",
            "description": f"Test configuration {name_suffix}",
            "category": "test",
            "extraction_strategy": "default",
            "update_frequency": "daily",
            "is_active": True
        }
        base_data.update(overrides)
        return base_data


@pytest.fixture
def test_data_factory():
    """Provide the test data factory."""
    return TestDataFactory


# Custom assertions
def assert_valid_response(response, expected_status=200):
    """Assert that a response is valid and has expected status."""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
    if expected_status == 200:
        assert response.headers.get("content-type", "").startswith("application/json")


def assert_valid_crud_response(response, operation="create"):
    """Assert that a CRUD operation response is valid."""
    if operation == "create":
        assert_valid_response(response, 201)
        data = response.json()
        assert "id" in data
        assert data["id"] is not None
    elif operation == "read":
        assert_valid_response(response, 200)
    elif operation == "update":
        assert_valid_response(response, 200)
    elif operation == "delete":
        assert_valid_response(response, 204)


# Markers for different test types
pytestmark = [
    pytest.mark.asyncio,
]