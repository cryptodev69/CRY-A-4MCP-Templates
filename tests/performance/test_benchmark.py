#!/usr/bin/env python3
"""
CRY-A-4MCP Test Performance Benchmarking

This module provides comprehensive performance benchmarking for the test suite,
including execution time tracking, memory usage monitoring, and performance
regression detection.

Usage:
    pytest tests/performance/test_benchmark.py -v
    pytest tests/performance/test_benchmark.py::test_api_performance -s

Features:
    - API endpoint performance testing
    - Database operation benchmarking
    - Memory usage profiling
    - Concurrent request testing
    - Performance regression detection
    - Detailed performance reporting
"""

import asyncio
import json
import time
import psutil
import pytest
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Callable
from unittest.mock import AsyncMock, MagicMock

import httpx
from fastapi.testclient import TestClient

# Test markers
pytestmark = [pytest.mark.performance, pytest.mark.slow]


class PerformanceBenchmark:
    """Performance benchmarking utility class."""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.memory_start = None
        self.memory_end = None
        self.results = []
    
    def __enter__(self):
        """Start performance measurement."""
        self.start_time = time.perf_counter()
        process = psutil.Process()
        self.memory_start = process.memory_info().rss / 1024 / 1024  # MB
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End performance measurement."""
        self.end_time = time.perf_counter()
        process = psutil.Process()
        self.memory_end = process.memory_info().rss / 1024 / 1024  # MB
    
    @property
    def duration(self) -> float:
        """Get execution duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    @property
    def memory_delta(self) -> float:
        """Get memory usage delta in MB."""
        if self.memory_start and self.memory_end:
            return self.memory_end - self.memory_start
        return 0.0
    
    def add_result(self, operation: str, duration: float, **kwargs):
        """Add a performance result."""
        result = {
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.results.append(result)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.results:
            return {}
        
        durations = [r["duration"] for r in self.results]
        return {
            "total_operations": len(self.results),
            "total_duration": sum(durations),
            "avg_duration": statistics.mean(durations),
            "median_duration": statistics.median(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "std_deviation": statistics.stdev(durations) if len(durations) > 1 else 0,
            "operations_per_second": len(durations) / sum(durations) if sum(durations) > 0 else 0
        }


class APIPerformanceTester:
    """API performance testing utility."""
    
    def __init__(self, client: TestClient):
        self.client = client
        self.benchmark = PerformanceBenchmark("API Performance")
    
    async def test_endpoint_performance(
        self,
        method: str,
        url: str,
        iterations: int = 100,
        **request_kwargs
    ) -> Dict[str, Any]:
        """Test API endpoint performance."""
        results = []
        
        for i in range(iterations):
            start_time = time.perf_counter()
            
            if method.upper() == "GET":
                response = self.client.get(url, **request_kwargs)
            elif method.upper() == "POST":
                response = self.client.post(url, **request_kwargs)
            elif method.upper() == "PUT":
                response = self.client.put(url, **request_kwargs)
            elif method.upper() == "DELETE":
                response = self.client.delete(url, **request_kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            results.append({
                "iteration": i + 1,
                "duration": duration,
                "status_code": response.status_code,
                "response_size": len(response.content) if response.content else 0
            })
            
            self.benchmark.add_result(
                operation=f"{method.upper()} {url}",
                duration=duration,
                status_code=response.status_code,
                response_size=len(response.content) if response.content else 0
            )
        
        return {
            "endpoint": f"{method.upper()} {url}",
            "iterations": iterations,
            "results": results,
            "statistics": self._calculate_stats(results)
        }
    
    async def test_concurrent_requests(
        self,
        method: str,
        url: str,
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        **request_kwargs
    ) -> Dict[str, Any]:
        """Test concurrent request performance."""
        async def make_requests(user_id: int):
            """Make requests for a single user."""
            user_results = []
            
            async with httpx.AsyncClient() as client:
                for i in range(requests_per_user):
                    start_time = time.perf_counter()
                    
                    try:
                        if method.upper() == "GET":
                            response = await client.get(url, **request_kwargs)
                        elif method.upper() == "POST":
                            response = await client.post(url, **request_kwargs)
                        else:
                            raise ValueError(f"Unsupported method: {method}")
                        
                        end_time = time.perf_counter()
                        duration = end_time - start_time
                        
                        user_results.append({
                            "user_id": user_id,
                            "request_id": i + 1,
                            "duration": duration,
                            "status_code": response.status_code,
                            "success": response.status_code < 400
                        })
                        
                    except Exception as e:
                        end_time = time.perf_counter()
                        duration = end_time - start_time
                        
                        user_results.append({
                            "user_id": user_id,
                            "request_id": i + 1,
                            "duration": duration,
                            "status_code": 0,
                            "success": False,
                            "error": str(e)
                        })
            
            return user_results
        
        # Run concurrent requests
        start_time = time.perf_counter()
        tasks = [make_requests(user_id) for user_id in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)
        end_time = time.perf_counter()
        
        # Flatten results
        flattened_results = []
        for user_results in all_results:
            flattened_results.extend(user_results)
        
        return {
            "endpoint": f"{method.upper()} {url}",
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_requests": len(flattened_results),
            "total_duration": end_time - start_time,
            "results": flattened_results,
            "statistics": self._calculate_stats(flattened_results)
        }
    
    def _calculate_stats(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate performance statistics."""
        if not results:
            return {}
        
        durations = [r["duration"] for r in results]
        successful_requests = [r for r in results if r.get("success", True)]
        
        return {
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "success_rate": len(successful_requests) / len(results) * 100,
            "avg_response_time": statistics.mean(durations),
            "median_response_time": statistics.median(durations),
            "min_response_time": min(durations),
            "max_response_time": max(durations),
            "p95_response_time": self._percentile(durations, 95),
            "p99_response_time": self._percentile(durations, 99),
            "requests_per_second": len(results) / sum(durations) if sum(durations) > 0 else 0,
            "std_deviation": statistics.stdev(durations) if len(durations) > 1 else 0
        }
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class DatabasePerformanceTester:
    """Database performance testing utility."""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.benchmark = PerformanceBenchmark("Database Performance")
    
    async def test_query_performance(
        self,
        query_func: Callable,
        iterations: int = 100,
        **query_kwargs
    ) -> Dict[str, Any]:
        """Test database query performance."""
        results = []
        
        for i in range(iterations):
            start_time = time.perf_counter()
            
            try:
                result = await query_func(**query_kwargs)
                end_time = time.perf_counter()
                duration = end_time - start_time
                
                results.append({
                    "iteration": i + 1,
                    "duration": duration,
                    "success": True,
                    "result_count": len(result) if hasattr(result, '__len__') else 1
                })
                
            except Exception as e:
                end_time = time.perf_counter()
                duration = end_time - start_time
                
                results.append({
                    "iteration": i + 1,
                    "duration": duration,
                    "success": False,
                    "error": str(e)
                })
            
            self.benchmark.add_result(
                operation=query_func.__name__,
                duration=duration,
                success=results[-1]["success"]
            )
        
        return {
            "query_function": query_func.__name__,
            "iterations": iterations,
            "results": results,
            "statistics": self._calculate_query_stats(results)
        }
    
    def _calculate_query_stats(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate database query statistics."""
        if not results:
            return {}
        
        durations = [r["duration"] for r in results]
        successful_queries = [r for r in results if r["success"]]
        
        return {
            "total_queries": len(results),
            "successful_queries": len(successful_queries),
            "success_rate": len(successful_queries) / len(results) * 100,
            "avg_query_time": statistics.mean(durations),
            "median_query_time": statistics.median(durations),
            "min_query_time": min(durations),
            "max_query_time": max(durations),
            "queries_per_second": len(results) / sum(durations) if sum(durations) > 0 else 0
        }


# Performance Test Fixtures
@pytest.fixture
def performance_benchmark():
    """Create a performance benchmark instance."""
    return PerformanceBenchmark("Test Suite")


@pytest.fixture
def mock_api_client():
    """Create a mock API client for testing."""
    client = MagicMock()
    
    # Mock successful responses
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"status": "success"}'
    mock_response.json.return_value = {"status": "success"}
    
    client.get.return_value = mock_response
    client.post.return_value = mock_response
    client.put.return_value = mock_response
    client.delete.return_value = mock_response
    
    return client


@pytest.fixture
def mock_database():
    """Create a mock database for testing."""
    db = AsyncMock()
    
    # Mock query results
    async def mock_query(*args, **kwargs):
        await asyncio.sleep(0.001)  # Simulate query time
        return [{"id": 1, "name": "test"}]
    
    db.execute = mock_query
    db.fetch_all = mock_query
    db.fetch_one = mock_query
    
    return db


# Performance Tests
@pytest.mark.asyncio
async def test_api_endpoint_performance(mock_api_client, performance_benchmark):
    """Test API endpoint performance under normal load."""
    tester = APIPerformanceTester(mock_api_client)
    
    with performance_benchmark:
        # Test GET endpoint
        get_results = await tester.test_endpoint_performance(
            method="GET",
            url="/api/v1/health",
            iterations=50
        )
        
        # Test POST endpoint
        post_results = await tester.test_endpoint_performance(
            method="POST",
            url="/api/v1/configurations",
            iterations=50,
            json={"url": "https://example.com", "strategy": "default"}
        )
    
    # Assertions
    assert get_results["statistics"]["success_rate"] >= 95.0
    assert get_results["statistics"]["avg_response_time"] < 1.0  # Less than 1 second
    assert get_results["statistics"]["p95_response_time"] < 2.0  # 95th percentile
    
    assert post_results["statistics"]["success_rate"] >= 95.0
    assert post_results["statistics"]["avg_response_time"] < 1.0
    
    # Performance regression check
    assert performance_benchmark.duration < 10.0  # Total test time
    assert performance_benchmark.memory_delta < 50.0  # Memory usage in MB


@pytest.mark.asyncio
async def test_concurrent_request_performance(mock_api_client):
    """Test API performance under concurrent load."""
    # Skip this test in CI to avoid resource constraints
    if os.getenv("CI"):
        pytest.skip("Skipping concurrent tests in CI environment")
    
    tester = APIPerformanceTester(mock_api_client)
    
    results = await tester.test_concurrent_requests(
        method="GET",
        url="http://localhost:8000/api/v1/health",
        concurrent_users=5,
        requests_per_user=10
    )
    
    # Assertions
    assert results["statistics"]["success_rate"] >= 90.0
    assert results["statistics"]["avg_response_time"] < 2.0
    assert results["statistics"]["requests_per_second"] > 10.0
    assert results["total_requests"] == 50  # 5 users * 10 requests


@pytest.mark.asyncio
async def test_database_query_performance(mock_database, performance_benchmark):
    """Test database query performance."""
    tester = DatabasePerformanceTester(mock_database)
    
    with performance_benchmark:
        # Test simple query
        simple_results = await tester.test_query_performance(
            query_func=mock_database.fetch_all,
            iterations=100
        )
        
        # Test complex query (simulated)
        complex_results = await tester.test_query_performance(
            query_func=mock_database.execute,
            iterations=50
        )
    
    # Assertions
    assert simple_results["statistics"]["success_rate"] >= 99.0
    assert simple_results["statistics"]["avg_query_time"] < 0.1  # 100ms
    assert simple_results["statistics"]["queries_per_second"] > 100.0
    
    assert complex_results["statistics"]["success_rate"] >= 99.0
    assert complex_results["statistics"]["avg_query_time"] < 0.1


@pytest.mark.asyncio
async def test_memory_usage_performance():
    """Test memory usage during operations."""
    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    # Simulate memory-intensive operations
    data_structures = []
    for i in range(1000):
        data_structures.append({"id": i, "data": "x" * 1000})
    
    peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
    memory_increase = peak_memory - initial_memory
    
    # Clean up
    del data_structures
    
    final_memory = psutil.Process().memory_info().rss / 1024 / 1024
    memory_cleanup = peak_memory - final_memory
    
    # Assertions
    assert memory_increase < 100.0  # Less than 100MB increase
    assert memory_cleanup > memory_increase * 0.8  # At least 80% cleanup


@pytest.mark.asyncio
async def test_response_time_distribution():
    """Test response time distribution patterns."""
    response_times = []
    
    # Simulate API calls with varying response times
    for i in range(100):
        start_time = time.perf_counter()
        
        # Simulate processing time
        await asyncio.sleep(0.001 + (i % 10) * 0.0001)
        
        end_time = time.perf_counter()
        response_times.append(end_time - start_time)
    
    # Calculate distribution metrics
    avg_time = statistics.mean(response_times)
    median_time = statistics.median(response_times)
    std_dev = statistics.stdev(response_times)
    
    # Assertions
    assert avg_time < 0.01  # Average less than 10ms
    assert median_time < 0.01  # Median less than 10ms
    assert std_dev < 0.005  # Low variance in response times
    
    # Check for outliers (values more than 2 standard deviations from mean)
    outliers = [t for t in response_times if abs(t - avg_time) > 2 * std_dev]
    outlier_percentage = len(outliers) / len(response_times) * 100
    
    assert outlier_percentage < 5.0  # Less than 5% outliers


@pytest.mark.asyncio
async def test_throughput_performance():
    """Test system throughput under sustained load."""
    start_time = time.perf_counter()
    operations_completed = 0
    target_duration = 5.0  # 5 seconds
    
    while time.perf_counter() - start_time < target_duration:
        # Simulate operation
        await asyncio.sleep(0.001)
        operations_completed += 1
    
    actual_duration = time.perf_counter() - start_time
    throughput = operations_completed / actual_duration
    
    # Assertions
    assert throughput > 500.0  # At least 500 operations per second
    assert operations_completed > 2500  # At least 2500 operations in 5 seconds


def test_performance_regression_detection(tmp_path):
    """Test performance regression detection."""
    # Create mock performance history
    history_file = tmp_path / "performance_history.json"
    
    historical_data = {
        "api_response_time": {
            "baseline": 0.1,
            "threshold": 0.15,
            "history": [0.09, 0.11, 0.10, 0.12, 0.08]
        },
        "database_query_time": {
            "baseline": 0.05,
            "threshold": 0.08,
            "history": [0.04, 0.06, 0.05, 0.05, 0.04]
        }
    }
    
    history_file.write_text(json.dumps(historical_data, indent=2))
    
    # Test current performance
    current_api_time = 0.12  # Within threshold
    current_db_time = 0.09   # Above threshold - regression!
    
    # Load historical data
    history = json.loads(history_file.read_text())
    
    # Check for regressions
    api_regression = current_api_time > history["api_response_time"]["threshold"]
    db_regression = current_db_time > history["database_query_time"]["threshold"]
    
    # Assertions
    assert not api_regression, "API response time regression detected"
    assert db_regression, "Database query time regression should be detected"
    
    # Update history
    history["api_response_time"]["history"].append(current_api_time)
    history["database_query_time"]["history"].append(current_db_time)
    
    # Keep only last 10 measurements
    for metric in history.values():
        metric["history"] = metric["history"][-10:]
    
    history_file.write_text(json.dumps(history, indent=2))


if __name__ == "__main__":
    # Run performance tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10"
    ])