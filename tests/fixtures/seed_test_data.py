#!/usr/bin/env python3
"""
CRY-A-4MCP Test Data Seeding Script

This script provides comprehensive test data seeding capabilities for the
CRY-A-4MCP testing framework, including database population, file generation,
and test environment setup.

Usage:
    python tests/fixtures/seed_test_data.py --environment test
    python tests/fixtures/seed_test_data.py --seed-type minimal
    python tests/fixtures/seed_test_data.py --clean --seed-type full

Features:
    - Multiple seeding strategies (minimal, standard, full, performance)
    - Database population with realistic data
    - File-based test data generation
    - Environment-specific configurations
    - Data cleanup and reset capabilities
    - Seed data validation
"""

import argparse
import asyncio
import json
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import uuid4

import asyncpg
from faker import Faker

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tests.factories import (
        URLConfigurationFactory,
        StrategyFactory,
        CrawlerDataFactory,
        UserFactory,
        APIKeyFactory,
        WebhookFactory,
        AlertFactory,
        PerformanceMetricFactory
    )
except ImportError:
    print("Warning: Could not import factories. Some features may not work.")
    URLConfigurationFactory = None


class TestDataSeeder:
    """Main test data seeding class."""
    
    def __init__(self, environment: str = "test", verbose: bool = False):
        self.environment = environment
        self.verbose = verbose
        self.fake = Faker()
        self.db_connection = None
        self.seeded_data = {
            "users": [],
            "configurations": [],
            "strategies": [],
            "crawler_data": [],
            "api_keys": [],
            "webhooks": [],
            "alerts": [],
            "performance_metrics": []
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with appropriate formatting."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            prefix = {
                "INFO": "ℹ️",
                "SUCCESS": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "DEBUG": "🔍"
            }.get(level, "📝")
            print(f"[{timestamp}] {prefix} {message}")
    
    async def connect_database(self) -> bool:
        """Connect to the test database."""
        try:
            # Database connection parameters for test environment
            db_config = {
                "host": os.getenv("TEST_DB_HOST", "localhost"),
                "port": int(os.getenv("TEST_DB_PORT", "5432")),
                "database": os.getenv("TEST_DB_NAME", "cry_a_4mcp_test"),
                "user": os.getenv("TEST_DB_USER", "test_user"),
                "password": os.getenv("TEST_DB_PASSWORD", "test_password")
            }
            
            self.db_connection = await asyncpg.connect(**db_config)
            self.log(f"Connected to test database: {db_config['database']}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to connect to database: {e}", "ERROR")
            return False
    
    async def disconnect_database(self):
        """Disconnect from the database."""
        if self.db_connection:
            await self.db_connection.close()
            self.log("Disconnected from database", "INFO")
    
    async def clean_database(self) -> bool:
        """Clean all test data from the database."""
        if not self.db_connection:
            self.log("No database connection available", "ERROR")
            return False
        
        try:
            # List of tables to clean (in dependency order)
            tables_to_clean = [
                "performance_metrics",
                "alerts",
                "webhook_logs",
                "webhooks",
                "crawler_data",
                "api_keys",
                "url_configurations",
                "strategies",
                "users"
            ]
            
            for table in tables_to_clean:
                try:
                    await self.db_connection.execute(f"DELETE FROM {table}")
                    self.log(f"Cleaned table: {table}", "DEBUG")
                except Exception as e:
                    self.log(f"Warning: Could not clean table {table}: {e}", "WARNING")
            
            # Reset sequences
            sequences = [
                "users_id_seq",
                "strategies_id_seq",
                "url_configurations_id_seq",
                "api_keys_id_seq",
                "webhooks_id_seq",
                "alerts_id_seq"
            ]
            
            for sequence in sequences:
                try:
                    await self.db_connection.execute(f"ALTER SEQUENCE {sequence} RESTART WITH 1")
                    self.log(f"Reset sequence: {sequence}", "DEBUG")
                except Exception as e:
                    self.log(f"Warning: Could not reset sequence {sequence}: {e}", "WARNING")
            
            self.log("Database cleaned successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error cleaning database: {e}", "ERROR")
            return False
    
    async def seed_users(self, count: int = 10) -> List[Dict[str, Any]]:
        """Seed user data."""
        self.log(f"Seeding {count} users...", "INFO")
        users = []
        
        for i in range(count):
            user_data = {
                "id": i + 1,
                "username": self.fake.user_name(),
                "email": self.fake.email(),
                "full_name": self.fake.name(),
                "is_active": random.choice([True, True, True, False]),  # 75% active
                "is_verified": random.choice([True, True, False]),  # 66% verified
                "created_at": self.fake.date_time_between(start_date="-1y", end_date="now"),
                "last_login": self.fake.date_time_between(start_date="-30d", end_date="now") if random.random() > 0.2 else None,
                "subscription_tier": random.choice(["free", "pro", "enterprise"]),
                "api_quota_used": random.randint(0, 1000),
                "api_quota_limit": random.choice([1000, 5000, 10000, 50000])
            }
            
            if self.db_connection:
                try:
                    await self.db_connection.execute(
                        """
                        INSERT INTO users (id, username, email, full_name, is_active, is_verified, 
                                         created_at, last_login, subscription_tier, api_quota_used, api_quota_limit)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        """,
                        user_data["id"], user_data["username"], user_data["email"],
                        user_data["full_name"], user_data["is_active"], user_data["is_verified"],
                        user_data["created_at"], user_data["last_login"], user_data["subscription_tier"],
                        user_data["api_quota_used"], user_data["api_quota_limit"]
                    )
                except Exception as e:
                    self.log(f"Error inserting user {i+1}: {e}", "WARNING")
                    continue
            
            users.append(user_data)
        
        self.seeded_data["users"] = users
        self.log(f"Seeded {len(users)} users", "SUCCESS")
        return users
    
    async def seed_strategies(self, count: int = 15) -> List[Dict[str, Any]]:
        """Seed strategy data."""
        self.log(f"Seeding {count} strategies...", "INFO")
        strategies = []
        
        strategy_types = ["basic", "advanced", "ai_powered", "custom"]
        strategy_names = [
            "Default Crawler", "E-commerce Scraper", "News Aggregator",
            "Social Media Monitor", "Price Tracker", "Content Analyzer",
            "SEO Auditor", "Competitor Monitor", "Lead Generator",
            "Market Research", "Brand Monitor", "Review Tracker",
            "Job Listings", "Real Estate", "Academic Papers"
        ]
        
        for i in range(count):
            strategy_data = {
                "id": i + 1,
                "name": strategy_names[i] if i < len(strategy_names) else f"Strategy {i+1}",
                "description": self.fake.text(max_nb_chars=200),
                "strategy_type": random.choice(strategy_types),
                "configuration": {
                    "selectors": {
                        "title": random.choice(["h1", "h2", ".title", "#main-title"]),
                        "content": random.choice([".content", "#main", ".article-body"]),
                        "links": "a[href]"
                    },
                    "options": {
                        "wait_time": random.randint(1, 5),
                        "max_depth": random.randint(1, 3),
                        "follow_links": random.choice([True, False]),
                        "javascript_enabled": random.choice([True, False])
                    }
                },
                "is_active": random.choice([True, True, True, False]),  # 75% active
                "created_by": random.randint(1, min(10, len(self.seeded_data.get("users", [])))),
                "created_at": self.fake.date_time_between(start_date="-6m", end_date="now"),
                "updated_at": self.fake.date_time_between(start_date="-1m", end_date="now"),
                "usage_count": random.randint(0, 1000),
                "success_rate": round(random.uniform(0.7, 0.99), 3)
            }
            
            if self.db_connection:
                try:
                    await self.db_connection.execute(
                        """
                        INSERT INTO strategies (id, name, description, strategy_type, configuration,
                                              is_active, created_by, created_at, updated_at, usage_count, success_rate)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        """,
                        strategy_data["id"], strategy_data["name"], strategy_data["description"],
                        strategy_data["strategy_type"], json.dumps(strategy_data["configuration"]),
                        strategy_data["is_active"], strategy_data["created_by"],
                        strategy_data["created_at"], strategy_data["updated_at"],
                        strategy_data["usage_count"], strategy_data["success_rate"]
                    )
                except Exception as e:
                    self.log(f"Error inserting strategy {i+1}: {e}", "WARNING")
                    continue
            
            strategies.append(strategy_data)
        
        self.seeded_data["strategies"] = strategies
        self.log(f"Seeded {len(strategies)} strategies", "SUCCESS")
        return strategies
    
    async def seed_url_configurations(self, count: int = 50) -> List[Dict[str, Any]]:
        """Seed URL configuration data."""
        self.log(f"Seeding {count} URL configurations...", "INFO")
        configurations = []
        
        domains = [
            "example.com", "test-site.org", "demo.net", "sample-data.io",
            "news-source.com", "ecommerce-store.com", "blog-platform.org",
            "social-network.net", "job-board.com", "real-estate.org"
        ]
        
        for i in range(count):
            domain = random.choice(domains)
            path = random.choice(["/", "/products", "/articles", "/news", "/jobs", "/listings"])
            
            config_data = {
                "id": i + 1,
                "url": f"https://{domain}{path}",
                "name": f"Config for {domain}",
                "description": self.fake.text(max_nb_chars=150),
                "strategy_id": random.randint(1, min(15, len(self.seeded_data.get("strategies", [])))),
                "user_id": random.randint(1, min(10, len(self.seeded_data.get("users", [])))),
                "is_active": random.choice([True, True, True, False]),  # 75% active
                "schedule": random.choice(["hourly", "daily", "weekly", "monthly", None]),
                "last_crawled": self.fake.date_time_between(start_date="-7d", end_date="now") if random.random() > 0.3 else None,
                "next_crawl": self.fake.date_time_between(start_date="now", end_date="+7d") if random.random() > 0.2 else None,
                "crawl_count": random.randint(0, 100),
                "success_count": random.randint(0, 80),
                "error_count": random.randint(0, 20),
                "created_at": self.fake.date_time_between(start_date="-3m", end_date="now"),
                "updated_at": self.fake.date_time_between(start_date="-1w", end_date="now")
            }
            
            if self.db_connection:
                try:
                    await self.db_connection.execute(
                        """
                        INSERT INTO url_configurations (id, url, name, description, strategy_id, user_id,
                                                       is_active, schedule, last_crawled, next_crawl,
                                                       crawl_count, success_count, error_count, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                        """,
                        config_data["id"], config_data["url"], config_data["name"],
                        config_data["description"], config_data["strategy_id"], config_data["user_id"],
                        config_data["is_active"], config_data["schedule"], config_data["last_crawled"],
                        config_data["next_crawl"], config_data["crawl_count"], config_data["success_count"],
                        config_data["error_count"], config_data["created_at"], config_data["updated_at"]
                    )
                except Exception as e:
                    self.log(f"Error inserting URL configuration {i+1}: {e}", "WARNING")
                    continue
            
            configurations.append(config_data)
        
        self.seeded_data["configurations"] = configurations
        self.log(f"Seeded {len(configurations)} URL configurations", "SUCCESS")
        return configurations
    
    async def seed_crawler_data(self, count: int = 200) -> List[Dict[str, Any]]:
        """Seed crawler data."""
        self.log(f"Seeding {count} crawler data records...", "INFO")
        crawler_data = []
        
        for i in range(count):
            config_id = random.randint(1, min(50, len(self.seeded_data.get("configurations", []))))
            
            data_record = {
                "id": i + 1,
                "configuration_id": config_id,
                "crawl_timestamp": self.fake.date_time_between(start_date="-30d", end_date="now"),
                "status": random.choice(["success", "success", "success", "error", "timeout"]),  # 60% success
                "data_extracted": {
                    "title": self.fake.sentence(nb_words=6),
                    "content": self.fake.text(max_nb_chars=500),
                    "links": [self.fake.url() for _ in range(random.randint(0, 5))],
                    "metadata": {
                        "word_count": random.randint(50, 1000),
                        "image_count": random.randint(0, 10),
                        "link_count": random.randint(0, 20)
                    }
                },
                "response_time": round(random.uniform(0.5, 5.0), 3),
                "response_size": random.randint(1000, 100000),
                "error_message": self.fake.sentence() if random.random() < 0.2 else None,
                "retry_count": random.randint(0, 3),
                "processing_time": round(random.uniform(0.1, 2.0), 3)
            }
            
            if self.db_connection:
                try:
                    await self.db_connection.execute(
                        """
                        INSERT INTO crawler_data (id, configuration_id, crawl_timestamp, status,
                                                 data_extracted, response_time, response_size,
                                                 error_message, retry_count, processing_time)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        """,
                        data_record["id"], data_record["configuration_id"], data_record["crawl_timestamp"],
                        data_record["status"], json.dumps(data_record["data_extracted"]),
                        data_record["response_time"], data_record["response_size"],
                        data_record["error_message"], data_record["retry_count"], data_record["processing_time"]
                    )
                except Exception as e:
                    self.log(f"Error inserting crawler data {i+1}: {e}", "WARNING")
                    continue
            
            crawler_data.append(data_record)
        
        self.seeded_data["crawler_data"] = crawler_data
        self.log(f"Seeded {len(crawler_data)} crawler data records", "SUCCESS")
        return crawler_data
    
    async def seed_api_keys(self, count: int = 25) -> List[Dict[str, Any]]:
        """Seed API key data."""
        self.log(f"Seeding {count} API keys...", "INFO")
        api_keys = []
        
        for i in range(count):
            key_data = {
                "id": i + 1,
                "user_id": random.randint(1, min(10, len(self.seeded_data.get("users", [])))),
                "key_name": f"API Key {i+1}",
                "key_hash": f"ak_{uuid4().hex[:32]}",
                "permissions": random.choice([
                    ["read"],
                    ["read", "write"],
                    ["read", "write", "admin"],
                    ["read", "crawl"]
                ]),
                "is_active": random.choice([True, True, True, False]),  # 75% active
                "expires_at": self.fake.date_time_between(start_date="+30d", end_date="+1y") if random.random() > 0.3 else None,
                "last_used": self.fake.date_time_between(start_date="-7d", end_date="now") if random.random() > 0.4 else None,
                "usage_count": random.randint(0, 1000),
                "rate_limit": random.choice([100, 500, 1000, 5000]),
                "created_at": self.fake.date_time_between(start_date="-6m", end_date="now")
            }
            
            if self.db_connection:
                try:
                    await self.db_connection.execute(
                        """
                        INSERT INTO api_keys (id, user_id, key_name, key_hash, permissions,
                                            is_active, expires_at, last_used, usage_count, rate_limit, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        """,
                        key_data["id"], key_data["user_id"], key_data["key_name"],
                        key_data["key_hash"], json.dumps(key_data["permissions"]),
                        key_data["is_active"], key_data["expires_at"], key_data["last_used"],
                        key_data["usage_count"], key_data["rate_limit"], key_data["created_at"]
                    )
                except Exception as e:
                    self.log(f"Error inserting API key {i+1}: {e}", "WARNING")
                    continue
            
            api_keys.append(key_data)
        
        self.seeded_data["api_keys"] = api_keys
        self.log(f"Seeded {len(api_keys)} API keys", "SUCCESS")
        return api_keys
    
    async def seed_webhooks(self, count: int = 15) -> List[Dict[str, Any]]:
        """Seed webhook data."""
        self.log(f"Seeding {count} webhooks...", "INFO")
        webhooks = []
        
        for i in range(count):
            webhook_data = {
                "id": i + 1,
                "user_id": random.randint(1, min(10, len(self.seeded_data.get("users", [])))),
                "name": f"Webhook {i+1}",
                "url": f"https://webhook-{i+1}.example.com/callback",
                "events": random.choice([
                    ["crawl.completed"],
                    ["crawl.failed"],
                    ["crawl.completed", "crawl.failed"],
                    ["crawl.completed", "crawl.failed", "user.quota_exceeded"]
                ]),
                "is_active": random.choice([True, True, False]),  # 66% active
                "secret": f"whsec_{uuid4().hex[:24]}",
                "retry_count": random.randint(0, 5),
                "timeout": random.choice([30, 60, 120]),
                "last_triggered": self.fake.date_time_between(start_date="-7d", end_date="now") if random.random() > 0.3 else None,
                "success_count": random.randint(0, 100),
                "failure_count": random.randint(0, 20),
                "created_at": self.fake.date_time_between(start_date="-3m", end_date="now")
            }
            
            if self.db_connection:
                try:
                    await self.db_connection.execute(
                        """
                        INSERT INTO webhooks (id, user_id, name, url, events, is_active,
                                            secret, retry_count, timeout, last_triggered,
                                            success_count, failure_count, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                        """,
                        webhook_data["id"], webhook_data["user_id"], webhook_data["name"],
                        webhook_data["url"], json.dumps(webhook_data["events"]),
                        webhook_data["is_active"], webhook_data["secret"],
                        webhook_data["retry_count"], webhook_data["timeout"],
                        webhook_data["last_triggered"], webhook_data["success_count"],
                        webhook_data["failure_count"], webhook_data["created_at"]
                    )
                except Exception as e:
                    self.log(f"Error inserting webhook {i+1}: {e}", "WARNING")
                    continue
            
            webhooks.append(webhook_data)
        
        self.seeded_data["webhooks"] = webhooks
        self.log(f"Seeded {len(webhooks)} webhooks", "SUCCESS")
        return webhooks
    
    def create_test_files(self, output_dir: Path):
        """Create test files for file-based testing."""
        self.log(f"Creating test files in {output_dir}...", "INFO")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sample JSON files
        json_files = {
            "sample_config.json": {
                "name": "Sample Configuration",
                "url": "https://example.com",
                "strategy": "default",
                "options": {
                    "wait_time": 2,
                    "max_depth": 3
                }
            },
            "sample_data.json": {
                "results": [
                    {
                        "title": "Sample Article",
                        "content": "This is sample content for testing.",
                        "url": "https://example.com/article1",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            },
            "error_responses.json": {
                "errors": [
                    {"code": 404, "message": "Page not found"},
                    {"code": 500, "message": "Internal server error"},
                    {"code": 403, "message": "Access forbidden"}
                ]
            }
        }
        
        for filename, content in json_files.items():
            file_path = output_dir / filename
            file_path.write_text(json.dumps(content, indent=2, default=str))
            self.log(f"Created: {filename}", "DEBUG")
        
        # Create sample CSV files
        csv_content = "id,name,url,status\n"
        for i in range(10):
            csv_content += f"{i+1},Config {i+1},https://example{i+1}.com,active\n"
        
        csv_file = output_dir / "sample_configurations.csv"
        csv_file.write_text(csv_content)
        self.log("Created: sample_configurations.csv", "DEBUG")
        
        # Create sample HTML files
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample Page</title>
</head>
<body>
    <h1>Sample Article Title</h1>
    <div class="content">
        <p>This is sample content for testing web scraping.</p>
        <a href="https://example.com/link1">Link 1</a>
        <a href="https://example.com/link2">Link 2</a>
    </div>
</body>
</html>
        """
        
        html_file = output_dir / "sample_page.html"
        html_file.write_text(html_content)
        self.log("Created: sample_page.html", "DEBUG")
        
        self.log(f"Created test files in {output_dir}", "SUCCESS")
    
    def generate_performance_data(self, output_dir: Path, count: int = 1000):
        """Generate performance test data."""
        self.log(f"Generating performance test data ({count} records)...", "INFO")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate large dataset for performance testing
        performance_data = []
        for i in range(count):
            record = {
                "id": i + 1,
                "timestamp": (datetime.now() - timedelta(seconds=i)).isoformat(),
                "url": f"https://performance-test-{i % 100}.com/page/{i}",
                "response_time": round(random.uniform(0.1, 5.0), 3),
                "status_code": random.choice([200, 200, 200, 404, 500]),
                "data_size": random.randint(1000, 100000),
                "processing_time": round(random.uniform(0.05, 2.0), 3)
            }
            performance_data.append(record)
        
        # Save as JSON
        json_file = output_dir / "performance_data.json"
        json_file.write_text(json.dumps(performance_data, indent=2))
        
        # Save as CSV
        csv_file = output_dir / "performance_data.csv"
        csv_content = "id,timestamp,url,response_time,status_code,data_size,processing_time\n"
        for record in performance_data:
            csv_content += f"{record['id']},{record['timestamp']},{record['url']},{record['response_time']},{record['status_code']},{record['data_size']},{record['processing_time']}\n"
        csv_file.write_text(csv_content)
        
        self.log(f"Generated performance data: {count} records", "SUCCESS")
    
    async def seed_by_type(self, seed_type: str) -> bool:
        """Seed data based on the specified type."""
        self.log(f"Starting {seed_type} data seeding...", "INFO")
        
        try:
            if seed_type == "minimal":
                await self.seed_users(5)
                await self.seed_strategies(5)
                await self.seed_url_configurations(10)
                await self.seed_api_keys(5)
                
            elif seed_type == "standard":
                await self.seed_users(10)
                await self.seed_strategies(15)
                await self.seed_url_configurations(50)
                await self.seed_crawler_data(100)
                await self.seed_api_keys(25)
                await self.seed_webhooks(10)
                
            elif seed_type == "full":
                await self.seed_users(25)
                await self.seed_strategies(30)
                await self.seed_url_configurations(100)
                await self.seed_crawler_data(500)
                await self.seed_api_keys(50)
                await self.seed_webhooks(25)
                
            elif seed_type == "performance":
                await self.seed_users(100)
                await self.seed_strategies(50)
                await self.seed_url_configurations(500)
                await self.seed_crawler_data(5000)
                await self.seed_api_keys(200)
                await self.seed_webhooks(100)
                
            else:
                self.log(f"Unknown seed type: {seed_type}", "ERROR")
                return False
            
            self.log(f"Completed {seed_type} data seeding", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error during {seed_type} seeding: {e}", "ERROR")
            return False
    
    def save_seed_report(self, output_file: Path):
        """Save a report of seeded data."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment,
            "summary": {
                "users": len(self.seeded_data["users"]),
                "strategies": len(self.seeded_data["strategies"]),
                "configurations": len(self.seeded_data["configurations"]),
                "crawler_data": len(self.seeded_data["crawler_data"]),
                "api_keys": len(self.seeded_data["api_keys"]),
                "webhooks": len(self.seeded_data["webhooks"])
            },
            "data": self.seeded_data
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(report, indent=2, default=str))
        self.log(f"Seed report saved to: {output_file}", "SUCCESS")


async def main():
    """Main entry point for the seeding script."""
    parser = argparse.ArgumentParser(
        description="CRY-A-4MCP Test Data Seeding Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--environment", "-e",
        default="test",
        choices=["test", "dev", "staging"],
        help="Target environment"
    )
    
    parser.add_argument(
        "--seed-type", "-t",
        default="standard",
        choices=["minimal", "standard", "full", "performance"],
        help="Type of data seeding to perform"
    )
    
    parser.add_argument(
        "--clean", "-c",
        action="store_true",
        help="Clean existing data before seeding"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=Path("tests/fixtures/generated"),
        help="Output directory for generated files"
    )
    
    parser.add_argument(
        "--report", "-r",
        type=Path,
        help="Save seeding report to file"
    )
    
    parser.add_argument(
        "--files-only",
        action="store_true",
        help="Only generate test files, skip database seeding"
    )
    
    args = parser.parse_args()
    
    # Create seeder instance
    seeder = TestDataSeeder(environment=args.environment, verbose=args.verbose)
    
    try:
        if not args.files_only:
            # Connect to database
            if not await seeder.connect_database():
                sys.exit(1)
            
            # Clean database if requested
            if args.clean:
                if not await seeder.clean_database():
                    sys.exit(1)
            
            # Seed database
            if not await seeder.seed_by_type(args.seed_type):
                sys.exit(1)
        
        # Create test files
        seeder.create_test_files(args.output_dir)
        
        # Generate performance data for performance tests
        if args.seed_type == "performance":
            seeder.generate_performance_data(args.output_dir / "performance", 10000)
        
        # Save report if requested
        if args.report:
            seeder.save_seed_report(args.report)
        
        seeder.log("🎉 Test data seeding completed successfully!", "SUCCESS")
        
    except KeyboardInterrupt:
        seeder.log("Seeding interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        seeder.log(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)
    finally:
        await seeder.disconnect_database()


if __name__ == "__main__":
    asyncio.run(main())