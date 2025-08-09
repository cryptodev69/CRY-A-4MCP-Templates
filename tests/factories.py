"""Test data factories for CRY-A-4MCP test suite.

This module provides factory classes for generating test data consistently
across all test modules. Uses factory_boy pattern for creating test objects.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4


class BaseFactory:
    """Base factory class with common utilities."""
    
    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate a random string of specified length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def random_email() -> str:
        """Generate a random email address."""
        username = BaseFactory.random_string(8)
        domain = random.choice(['example.com', 'test.org', 'demo.net'])
        return f"{username}@{domain}"
    
    @staticmethod
    def random_url() -> str:
        """Generate a random URL."""
        domain = BaseFactory.random_string(8)
        path = BaseFactory.random_string(6)
        return f"https://{domain}.com/{path}"
    
    @staticmethod
    def random_uuid() -> str:
        """Generate a random UUID string."""
        return str(uuid4())
    
    @staticmethod
    def random_timestamp() -> str:
        """Generate a random ISO timestamp."""
        base_time = datetime.now()
        random_delta = timedelta(days=random.randint(-30, 30))
        return (base_time + random_delta).isoformat()


class UserFactory(BaseFactory):
    """Factory for creating test user data."""
    
    @classmethod
    def create(cls, **kwargs) -> Dict[str, Any]:
        """Create a test user with optional overrides."""
        defaults = {
            "id": cls.random_uuid(),
            "username": cls.random_string(8),
            "email": cls.random_email(),
            "first_name": random.choice(["John", "Jane", "Alice", "Bob"]),
            "last_name": random.choice(["Doe", "Smith", "Johnson", "Brown"]),
            "is_active": True,
            "is_admin": False,
            "created_at": cls.random_timestamp(),
            "updated_at": cls.random_timestamp()
        }
        defaults.update(kwargs)
        return defaults
    
    @classmethod
    def create_admin(cls, **kwargs) -> Dict[str, Any]:
        """Create a test admin user."""
        kwargs.update({"is_admin": True})
        return cls.create(**kwargs)
    
    @classmethod
    def create_batch(cls, count: int, **kwargs) -> List[Dict[str, Any]]:
        """Create multiple test users."""
        return [cls.create(**kwargs) for _ in range(count)]


class StrategyFactory(BaseFactory):
    """Factory for creating test strategy data."""
    
    @classmethod
    def create(cls, **kwargs) -> Dict[str, Any]:
        """Create a test strategy with optional overrides."""
        defaults = {
            "id": cls.random_uuid(),
            "name": f"strategy_{cls.random_string(6)}",
            "type": random.choice(["extraction", "crawling", "analysis"]),
            "description": f"Test strategy for {cls.random_string(10)}",
            "config": {
                "selectors": {
                    "title": "h1, .title",
                    "content": ".content, .main",
                    "links": "a[href]"
                },
                "options": {
                    "wait_for": "networkidle",
                    "timeout": random.randint(10000, 60000),
                    "retries": random.randint(1, 5)
                }
            },
            "is_active": True,
            "created_by": cls.random_uuid(),
            "created_at": cls.random_timestamp(),
            "updated_at": cls.random_timestamp()
        }
        defaults.update(kwargs)
        return defaults
    
    @classmethod
    def create_extraction_strategy(cls, **kwargs) -> Dict[str, Any]:
        """Create a test extraction strategy."""
        kwargs.update({"type": "extraction"})
        return cls.create(**kwargs)
    
    @classmethod
    def create_crawling_strategy(cls, **kwargs) -> Dict[str, Any]:
        """Create a test crawling strategy."""
        kwargs.update({"type": "crawling"})
        return cls.create(**kwargs)


class CrawlerFactory(BaseFactory):
    """Factory for creating test crawler data."""
    
    @classmethod
    def create(cls, **kwargs) -> Dict[str, Any]:
        """Create a test crawler with optional overrides."""
        defaults = {
            "id": cls.random_uuid(),
            "name": f"crawler_{cls.random_string(6)}",
            "base_url": cls.random_url(),
            "strategy_id": cls.random_uuid(),
            "settings": {
                "concurrent_requests": random.randint(1, 10),
                "delay": random.uniform(0.5, 3.0),
                "respect_robots_txt": random.choice([True, False]),
                "user_agent": "CRY-A-4MCP-Test-Bot/1.0",
                "max_depth": random.randint(1, 5)
            },
            "status": random.choice(["active", "inactive", "paused"]),
            "created_by": cls.random_uuid(),
            "created_at": cls.random_timestamp(),
            "updated_at": cls.random_timestamp()
        }
        defaults.update(kwargs)
        return defaults
    
    @classmethod
    def create_active_crawler(cls, **kwargs) -> Dict[str, Any]:
        """Create an active test crawler."""
        kwargs.update({"status": "active"})
        return cls.create(**kwargs)


class URLConfigurationFactory(BaseFactory):
    """Factory for creating test URL configuration data."""
    
    @classmethod
    def create(cls, **kwargs) -> Dict[str, Any]:
        """Create a test URL configuration with optional overrides."""
        defaults = {
            "id": cls.random_uuid(),
            "url": cls.random_url(),
            "strategy_id": cls.random_uuid(),
            "extractor_id": cls.random_uuid(),
            "priority": random.randint(1, 10),
            "is_active": True,
            "metadata": {
                "tags": [cls.random_string(5) for _ in range(3)],
                "category": random.choice(["news", "blog", "ecommerce", "social"]),
                "language": random.choice(["en", "es", "fr", "de"])
            },
            "created_at": cls.random_timestamp(),
            "updated_at": cls.random_timestamp()
        }
        defaults.update(kwargs)
        return defaults


class ExtractorFactory(BaseFactory):
    """Factory for creating test extractor data."""
    
    @classmethod
    def create(cls, **kwargs) -> Dict[str, Any]:
        """Create a test extractor with optional overrides."""
        defaults = {
            "id": cls.random_uuid(),
            "name": f"extractor_{cls.random_string(6)}",
            "type": random.choice(["css", "xpath", "regex", "ai"]),
            "config": {
                "selectors": {
                    "title": "h1, .title, .headline",
                    "content": ".content, .article-body, main",
                    "author": ".author, .byline",
                    "date": ".date, .published, time"
                },
                "options": {
                    "clean_html": True,
                    "extract_links": True,
                    "extract_images": False
                }
            },
            "is_active": True,
            "created_by": cls.random_uuid(),
            "created_at": cls.random_timestamp(),
            "updated_at": cls.random_timestamp()
        }
        defaults.update(kwargs)
        return defaults


class APIResponseFactory(BaseFactory):
    """Factory for creating test API response data."""
    
    @classmethod
    def create_success_response(cls, data: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        """Create a successful API response."""
        defaults = {
            "status": "success",
            "message": "Operation completed successfully",
            "data": data or {"id": cls.random_uuid(), "result": "test_data"},
            "timestamp": cls.random_timestamp(),
            "request_id": cls.random_uuid()
        }
        defaults.update(kwargs)
        return defaults
    
    @classmethod
    def create_error_response(cls, error_code: str = "GENERIC_ERROR", **kwargs) -> Dict[str, Any]:
        """Create an error API response."""
        defaults = {
            "status": "error",
            "error": {
                "code": error_code,
                "message": f"Test error: {cls.random_string(20)}",
                "details": {"field": "test_field", "reason": "validation_failed"}
            },
            "timestamp": cls.random_timestamp(),
            "request_id": cls.random_uuid()
        }
        defaults.update(kwargs)
        return defaults


class CrawlResultFactory(BaseFactory):
    """Factory for creating test crawl result data."""
    
    @classmethod
    def create(cls, **kwargs) -> Dict[str, Any]:
        """Create a test crawl result with optional overrides."""
        defaults = {
            "id": cls.random_uuid(),
            "url": cls.random_url(),
            "crawler_id": cls.random_uuid(),
            "status": random.choice(["success", "failed", "pending"]),
            "content": {
                "title": f"Test Title {cls.random_string(10)}",
                "text": f"Test content {cls.random_string(100)}",
                "html": f"<html><body>{cls.random_string(50)}</body></html>",
                "links": [cls.random_url() for _ in range(5)],
                "images": [f"{cls.random_url()}/image.jpg" for _ in range(3)]
            },
            "metadata": {
                "response_time": random.uniform(0.1, 5.0),
                "status_code": random.choice([200, 404, 500]),
                "content_type": "text/html",
                "size_bytes": random.randint(1000, 100000)
            },
            "extracted_at": cls.random_timestamp(),
            "processed_at": cls.random_timestamp()
        }
        defaults.update(kwargs)
        return defaults
    
    @classmethod
    def create_successful_result(cls, **kwargs) -> Dict[str, Any]:
        """Create a successful crawl result."""
        kwargs.update({"status": "success"})
        kwargs.setdefault("metadata", {}).update({"status_code": 200})
        return cls.create(**kwargs)
    
    @classmethod
    def create_failed_result(cls, **kwargs) -> Dict[str, Any]:
        """Create a failed crawl result."""
        kwargs.update({"status": "failed"})
        kwargs.setdefault("metadata", {}).update({"status_code": 404})
        return cls.create(**kwargs)


# Convenience functions for quick test data generation
def create_test_user(**kwargs) -> Dict[str, Any]:
    """Quick function to create a test user."""
    return UserFactory.create(**kwargs)


def create_test_strategy(**kwargs) -> Dict[str, Any]:
    """Quick function to create a test strategy."""
    return StrategyFactory.create(**kwargs)


def create_test_crawler(**kwargs) -> Dict[str, Any]:
    """Quick function to create a test crawler."""
    return CrawlerFactory.create(**kwargs)


def create_test_url_config(**kwargs) -> Dict[str, Any]:
    """Quick function to create a test URL configuration."""
    return URLConfigurationFactory.create(**kwargs)


def create_test_extractor(**kwargs) -> Dict[str, Any]:
    """Quick function to create a test extractor."""
    return ExtractorFactory.create(**kwargs)


def create_test_crawl_result(**kwargs) -> Dict[str, Any]:
    """Quick function to create a test crawl result."""
    return CrawlResultFactory.create(**kwargs)