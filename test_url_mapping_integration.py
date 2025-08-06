#!/usr/bin/env python3
"""
Comprehensive test script for URL mapping persistence and crawler integration.

This script tests the complete flow:
1. Backend API endpoints for URL mappings and crawlers
2. Data transformation between frontend and backend
3. Persistence of URL mapping data in crawler configurations
4. Error handling and edge cases

Usage:
    python test_url_mapping_integration.py
    
Requirements:
    - Backend server running on localhost:4001
    - Frontend server running on localhost:3000 (optional for API-only tests)
"""

import asyncio
import aiohttp
import json
import sys
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class TestResult(Enum):
    """Test result enumeration."""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class TestCase:
    """Test case data structure."""
    name: str
    description: str
    result: TestResult
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class URLMappingIntegrationTester:
    """Comprehensive tester for URL mapping integration."""
    
    def __init__(self, backend_url: str = "http://localhost:4001"):
        """Initialize the tester with backend URL."""
        self.backend_url = backend_url
        self.test_results: List[TestCase] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Test data
        self.test_mapping_id: Optional[str] = None
        self.test_crawler_id: Optional[str] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_case: TestCase):
        """Log and store test result."""
        self.test_results.append(test_case)
        status_icon = "✅" if test_case.result == TestResult.PASS else "❌" if test_case.result == TestResult.FAIL else "⏭️"
        print(f"{status_icon} {test_case.name}: {test_case.result.value}")
        if test_case.error_message:
            print(f"   Error: {test_case.error_message}")
        if test_case.execution_time:
            print(f"   Time: {test_case.execution_time:.2f}s")
    
    async def test_backend_health(self) -> TestCase:
        """Test if backend server is running and responsive."""
        test_name = "Backend Health Check"
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with self.session.get(f"{self.backend_url}/health") as response:
                if response.status == 200:
                    execution_time = asyncio.get_event_loop().time() - start_time
                    return TestCase(
                        name=test_name,
                        description="Check if backend server is running",
                        result=TestResult.PASS,
                        execution_time=execution_time
                    )
                else:
                    return TestCase(
                        name=test_name,
                        description="Check if backend server is running",
                        result=TestResult.FAIL,
                        error_message=f"Backend returned status {response.status}"
                    )
        except Exception as e:
            return TestCase(
                name=test_name,
                description="Check if backend server is running",
                result=TestResult.FAIL,
                error_message=f"Cannot connect to backend: {str(e)}"
            )
    
    async def test_create_url_mapping(self) -> TestCase:
        """Test creating a URL mapping via API."""
        test_name = "Create URL Mapping"
        start_time = asyncio.get_event_loop().time()
        
        mapping_data = {
            "name": "Test Integration Mapping",
            "description": "Test mapping for integration testing",
            "urls": ["https://test-crypto-news.com", "https://test-market-data.com"],
            "extractor_ids": ["test_news_extractor", "test_price_extractor"],
            "priority": 1,
            "rate_limit": 2,
            "crawler_settings": {
                "timeout": 30,
                "retry_attempts": 3,
                "user_agent": "CRY-A-4MCP-Test/1.0"
            },
            "validation_rules": {
                "required_elements": ["title", "content"],
                "min_content_length": 100
            }
        }
        
        try:
            async with self.session.post(
                f"{self.backend_url}/api/url-mappings",
                json=mapping_data
            ) as response:
                execution_time = asyncio.get_event_loop().time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    if "id" in data:
                        self.test_mapping_id = data["id"]
                        return TestCase(
                            name=test_name,
                            description="Create URL mapping via API",
                            result=TestResult.PASS,
                            execution_time=execution_time
                        )
                    else:
                        return TestCase(
                            name=test_name,
                            description="Create URL mapping via API",
                            result=TestResult.FAIL,
                            error_message="Response missing 'id' field"
                        )
                else:
                    error_text = await response.text()
                    return TestCase(
                        name=test_name,
                        description="Create URL mapping via API",
                        result=TestResult.FAIL,
                        error_message=f"HTTP {response.status}: {error_text}"
                    )
        except Exception as e:
            return TestCase(
                name=test_name,
                description="Create URL mapping via API",
                result=TestResult.FAIL,
                error_message=f"Exception: {str(e)}"
            )
    
    async def test_create_crawler_with_url_mapping(self) -> TestCase:
        """Test creating a crawler with URL mapping reference."""
        test_name = "Create Crawler with URL Mapping"
        start_time = asyncio.get_event_loop().time()
        
        if not self.test_mapping_id:
            return TestCase(
                name=test_name,
                description="Create crawler with URL mapping reference",
                result=TestResult.SKIP,
                error_message="No URL mapping ID available from previous test"
            )
        
        crawler_data = {
            "name": "Test Integration Crawler",
            "description": "Test crawler with URL mapping integration",
            "crawler_type": "llm",
            "is_active": True,
            "urlMappingId": self.test_mapping_id,
            "targetUrls": ["https://test-crypto-news.com/latest", "https://test-market-data.com/prices"],
            "config": {
                "timeout": 30,
                "retry_attempts": 3,
                "concurrent_requests": 5
            },
            "llm_config": {
                "model": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 2000
            },
            "extraction_strategies": ["test_news_extractor"]
        }
        
        try:
            async with self.session.post(
                f"{self.backend_url}/api/crawlers",
                json=crawler_data
            ) as response:
                execution_time = asyncio.get_event_loop().time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Handle nested response structure
                    crawler_data_response = data.get("crawler", data)
                    
                    if "id" in crawler_data_response:
                        self.test_crawler_id = crawler_data_response["id"]
                        
                        # Verify URL mapping data is present
                        url_mapping_id = crawler_data_response.get("url_mapping_id")
                        target_urls = crawler_data_response.get("target_urls")
                        
                        # Check if URL mapping data is properly stored
                        issues = []
                        
                        if url_mapping_id != self.test_mapping_id:
                            issues.append(f"url_mapping_id mismatch: expected {self.test_mapping_id}, got {url_mapping_id}")
                        
                        if target_urls != crawler_data["targetUrls"]:
                            issues.append(f"target_urls mismatch: expected {crawler_data['targetUrls']}, got {target_urls}")
                        
                        if not issues:
                            return TestCase(
                                name=test_name,
                                description="Create crawler with URL mapping reference",
                                result=TestResult.PASS,
                                execution_time=execution_time
                            )
                        else:
                            return TestCase(
                                name=test_name,
                                description="Create crawler with URL mapping reference",
                                result=TestResult.FAIL,
                                error_message="CRITICAL URL MAPPING PERSISTENCE ISSUE: " + "; ".join(issues)
                            )
                    else:
                        return TestCase(
                            name=test_name,
                            description="Create crawler with URL mapping reference",
                            result=TestResult.FAIL,
                            error_message=f"Response missing 'id' field. Full response: {json.dumps(data, indent=2)}"
                        )
                else:
                    error_text = await response.text()
                    return TestCase(
                        name=test_name,
                        description="Create crawler with URL mapping reference",
                        result=TestResult.FAIL,
                        error_message=f"HTTP {response.status}: {error_text}"
                    )
        except Exception as e:
            return TestCase(
                name=test_name,
                description="Create crawler with URL mapping reference",
                result=TestResult.FAIL,
                error_message=f"Exception: {str(e)}"
            )
    
    async def test_retrieve_crawler_persistence(self) -> TestCase:
        """Test retrieving crawler and verifying URL mapping persistence."""
        test_name = "Retrieve Crawler - URL Mapping Persistence"
        start_time = asyncio.get_event_loop().time()
        
        if not self.test_crawler_id:
            return TestCase(
                name=test_name,
                description="Verify URL mapping data persists in crawler",
                result=TestResult.SKIP,
                error_message="No crawler ID available from previous test"
            )
        
        try:
            async with self.session.get(
                f"{self.backend_url}/api/crawlers/{self.test_crawler_id}"
            ) as response:
                execution_time = asyncio.get_event_loop().time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if URL mapping data is persisted
                    issues = []
                    
                    if data.get("url_mapping_id") != self.test_mapping_id:
                        issues.append(f"url_mapping_id mismatch: expected {self.test_mapping_id}, got {data.get('url_mapping_id')}")
                    
                    expected_urls = ["https://test-crypto-news.com/latest", "https://test-market-data.com/prices"]
                    actual_urls = data.get("target_urls")
                    
                    # Handle JSON string case
                    if isinstance(actual_urls, str):
                        try:
                            actual_urls = json.loads(actual_urls)
                        except json.JSONDecodeError:
                            issues.append(f"target_urls is not valid JSON: {actual_urls}")
                    
                    if actual_urls != expected_urls:
                        issues.append(f"target_urls mismatch: expected {expected_urls}, got {actual_urls}")
                    
                    # Check url_mapping_ids field
                    url_mapping_ids = data.get("url_mapping_ids")
                    if url_mapping_ids:
                        if isinstance(url_mapping_ids, str):
                            try:
                                url_mapping_ids = json.loads(url_mapping_ids)
                            except json.JSONDecodeError:
                                issues.append(f"url_mapping_ids is not valid JSON: {url_mapping_ids}")
                        
                        if isinstance(url_mapping_ids, list) and self.test_mapping_id not in url_mapping_ids:
                            issues.append(f"test_mapping_id {self.test_mapping_id} not found in url_mapping_ids {url_mapping_ids}")
                    
                    if not issues:
                        return TestCase(
                            name=test_name,
                            description="Verify URL mapping data persists in crawler",
                            result=TestResult.PASS,
                            execution_time=execution_time
                        )
                    else:
                        return TestCase(
                            name=test_name,
                            description="Verify URL mapping data persists in crawler",
                            result=TestResult.FAIL,
                            error_message="; ".join(issues)
                        )
                else:
                    error_text = await response.text()
                    return TestCase(
                        name=test_name,
                        description="Verify URL mapping data persists in crawler",
                        result=TestResult.FAIL,
                        error_message=f"HTTP {response.status}: {error_text}"
                    )
        except Exception as e:
            return TestCase(
                name=test_name,
                description="Verify URL mapping data persists in crawler",
                result=TestResult.FAIL,
                error_message=f"Exception: {str(e)}"
            )
    
    async def test_crawler_list_includes_url_mapping(self) -> TestCase:
        """Test that crawler list includes URL mapping data."""
        test_name = "Crawler List - URL Mapping Data"
        start_time = asyncio.get_event_loop().time()
        
        if not self.test_crawler_id:
            return TestCase(
                name=test_name,
                description="Verify crawler list includes URL mapping data",
                result=TestResult.SKIP,
                error_message="No crawler ID available from previous test"
            )
        
        try:
            async with self.session.get(
                f"{self.backend_url}/api/crawlers"
            ) as response:
                execution_time = asyncio.get_event_loop().time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Find our test crawler
                    test_crawler = None
                    crawlers = data.get('items', []) if isinstance(data, dict) else data
                    for crawler in crawlers:
                        if crawler.get("id") == self.test_crawler_id:
                            test_crawler = crawler
                            break
                    
                    if test_crawler:
                        if (test_crawler.get("url_mapping_id") == self.test_mapping_id and
                            test_crawler.get("target_urls") is not None):
                            return TestCase(
                                name=test_name,
                                description="Verify crawler list includes URL mapping data",
                                result=TestResult.PASS,
                                execution_time=execution_time
                            )
                        else:
                            return TestCase(
                                name=test_name,
                                description="Verify crawler list includes URL mapping data",
                                result=TestResult.FAIL,
                                error_message=f"URL mapping data missing in list: url_mapping_id={test_crawler.get('url_mapping_id')}, target_urls={test_crawler.get('target_urls')}"
                            )
                    else:
                        return TestCase(
                            name=test_name,
                            description="Verify crawler list includes URL mapping data",
                            result=TestResult.FAIL,
                            error_message=f"Test crawler {self.test_crawler_id} not found in list"
                        )
                else:
                    error_text = await response.text()
                    return TestCase(
                        name=test_name,
                        description="Verify crawler list includes URL mapping data",
                        result=TestResult.FAIL,
                        error_message=f"HTTP {response.status}: {error_text}"
                    )
        except Exception as e:
            return TestCase(
                name=test_name,
                description="Verify crawler list includes URL mapping data",
                result=TestResult.FAIL,
                error_message=f"Exception: {str(e)}"
            )
    
    async def test_update_crawler_url_mapping(self) -> TestCase:
        """Test updating crawler URL mapping configuration."""
        test_name = "Update Crawler URL Mapping"
        start_time = asyncio.get_event_loop().time()
        
        if not self.test_crawler_id:
            return TestCase(
                name=test_name,
                description="Test updating crawler URL mapping",
                result=TestResult.SKIP,
                error_message="No crawler ID available from previous test"
            )
        
        update_data = {
            "targetUrls": ["https://updated-crypto-news.com", "https://updated-market-data.com"],
            "config": {
                "timeout": 45,
                "retry_attempts": 5
            }
        }
        
        try:
            async with self.session.put(
                f"{self.backend_url}/api/crawlers/{self.test_crawler_id}",
                json=update_data
            ) as response:
                execution_time = asyncio.get_event_loop().time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify update was successful
                    crawler_data = data.get("crawler", {})
                    actual_urls = crawler_data.get("target_urls")
                    if isinstance(actual_urls, str):
                        try:
                            actual_urls = json.loads(actual_urls)
                        except json.JSONDecodeError:
                            pass
                    
                    if actual_urls == update_data["targetUrls"]:
                        return TestCase(
                            name=test_name,
                            description="Test updating crawler URL mapping",
                            result=TestResult.PASS,
                            execution_time=execution_time
                        )
                    else:
                        return TestCase(
                            name=test_name,
                            description="Test updating crawler URL mapping",
                            result=TestResult.FAIL,
                            error_message=f"Update failed: expected {update_data['targetUrls']}, got {actual_urls}"
                        )
                else:
                    error_text = await response.text()
                    return TestCase(
                        name=test_name,
                        description="Test updating crawler URL mapping",
                        result=TestResult.FAIL,
                        error_message=f"HTTP {response.status}: {error_text}"
                    )
        except Exception as e:
            return TestCase(
                name=test_name,
                description="Test updating crawler URL mapping",
                result=TestResult.FAIL,
                error_message=f"Exception: {str(e)}"
            )
    
    async def cleanup_test_data(self) -> TestCase:
        """Clean up test data created during testing."""
        test_name = "Cleanup Test Data"
        start_time = asyncio.get_event_loop().time()
        
        cleanup_errors = []
        
        # Delete test crawler
        if self.test_crawler_id:
            try:
                async with self.session.delete(
                    f"{self.backend_url}/api/crawlers/{self.test_crawler_id}"
                ) as response:
                    if response.status not in [200, 204, 404]:
                        cleanup_errors.append(f"Failed to delete crawler: HTTP {response.status}")
            except Exception as e:
                cleanup_errors.append(f"Error deleting crawler: {str(e)}")
        
        # Delete test URL mapping
        if self.test_mapping_id:
            try:
                async with self.session.delete(
                    f"{self.backend_url}/api/url-mappings/{self.test_mapping_id}"
                ) as response:
                    if response.status not in [200, 204, 404]:
                        cleanup_errors.append(f"Failed to delete URL mapping: HTTP {response.status}")
            except Exception as e:
                cleanup_errors.append(f"Error deleting URL mapping: {str(e)}")
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        if not cleanup_errors:
            return TestCase(
                name=test_name,
                description="Clean up test data",
                result=TestResult.PASS,
                execution_time=execution_time
            )
        else:
            return TestCase(
                name=test_name,
                description="Clean up test data",
                result=TestResult.FAIL,
                error_message="; ".join(cleanup_errors)
            )
    
    async def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting URL Mapping Integration Tests\n")
        
        # Test sequence
        tests = [
            self.test_backend_health,
            self.test_create_url_mapping,
            self.test_create_crawler_with_url_mapping,
            self.test_retrieve_crawler_persistence,
            self.test_crawler_list_includes_url_mapping,
            self.test_update_crawler_url_mapping,
            self.cleanup_test_data
        ]
        
        for test_func in tests:
            try:
                result = await test_func()
                self.log_test_result(result)
            except Exception as e:
                error_result = TestCase(
                    name=test_func.__name__,
                    description=f"Test function {test_func.__name__}",
                    result=TestResult.FAIL,
                    error_message=f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
                )
                self.log_test_result(error_result)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t.result == TestResult.PASS])
        failed_tests = len([t for t in self.test_results if t.result == TestResult.FAIL])
        skipped_tests = len([t for t in self.test_results if t.result == TestResult.SKIP])
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️ Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for test in self.test_results:
                if test.result == TestResult.FAIL:
                    print(f"  • {test.name}: {test.error_message}")
        
        print("\n" + "="*60)
        
        # Exit with appropriate code
        if failed_tests > 0:
            print("❌ INTEGRATION TESTS FAILED - URL mapping persistence is not working correctly!")
            sys.exit(1)
        else:
            print("✅ ALL INTEGRATION TESTS PASSED - URL mapping persistence is working correctly!")
            sys.exit(0)


async def main():
    """Main entry point for the integration test script."""
    print("URL Mapping Integration Test Suite")
    print("==================================\n")
    
    async with URLMappingIntegrationTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)