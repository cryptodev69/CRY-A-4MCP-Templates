#!/usr/bin/env python3
"""
Test script for the metrics exporter module.

This script tests the functionality of the metrics exporter module by simulating
extraction operations and verifying that metrics are correctly recorded and exposed.

Usage:
    python test_metrics_exporter.py
"""

import unittest
import asyncio
import time
import requests
import threading
import json
from unittest.mock import patch
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the metrics exporter module
try:
    from src.cry_a_4mcp.monitoring.metrics_exporter import (
        ExtractionMetrics, ExtractionTimer, start_metrics_server
    )
except ImportError:
    print("Error: Could not import metrics_exporter module. Make sure the module exists.")
    sys.exit(1)


class TestMetricsExporter(unittest.TestCase):
    """Test cases for the metrics exporter module."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a new ExtractionMetrics instance for each test
        self.metrics = ExtractionMetrics()
        
        # Start a metrics server in a separate thread
        self.server_port = 8001
        self.server_thread = threading.Thread(
            target=start_metrics_server,
            args=(self.server_port,),
            daemon=True
        )
        self.server_thread.start()
        
        # Wait for the server to start
        time.sleep(1)
    
    def test_record_attempt(self):
        """Test recording an extraction attempt."""
        # Record an attempt
        self.metrics.record_attempt(content_type="CRYPTO")
        
        # Get the metrics
        response = requests.get(f"http://localhost:{self.server_port}/metrics")
        self.assertEqual(response.status_code, 200)
        
        # Check if the attempt was recorded
        self.assertIn("extraction_attempts_total{content_type=\"CRYPTO\"} 1.0", response.text)
    
    def test_record_success(self):
        """Test recording a successful extraction."""
        # Record a success
        self.metrics.record_success(
            content_type="NEWS",
            token_usage=100,
            estimated_cost_dollars=0.002,
            quality_score=0.8,
            content_size_bytes=1000
        )
        
        # Get the metrics
        response = requests.get(f"http://localhost:{self.server_port}/metrics")
        self.assertEqual(response.status_code, 200)
        
        # Check if the success was recorded
        self.assertIn("extraction_successes_total{content_type=\"NEWS\"} 1.0", response.text)
        self.assertIn("extraction_tokens_total{content_type=\"NEWS\"} 100.0", response.text)
        self.assertIn("extraction_cost_dollars_total{content_type=\"NEWS\"} 0.002", response.text)
        self.assertIn("extraction_quality_score{content_type=\"NEWS\"} 0.8", response.text)
    
    def test_record_failure(self):
        """Test recording a failed extraction."""
        # Record a failure
        self.metrics.record_failure(content_type="SOCIAL_MEDIA", error="API error")
        
        # Get the metrics
        response = requests.get(f"http://localhost:{self.server_port}/metrics")
        self.assertEqual(response.status_code, 200)
        
        # Check if the failure was recorded
        self.assertIn("extraction_failures_total{content_type=\"SOCIAL_MEDIA\",error=\"API error\"} 1.0", response.text)
    
    def test_record_validation_error(self):
        """Test recording a validation error."""
        # Record a validation error
        self.metrics.record_validation_error(
            content_type="CRYPTO",
            error_type="missing_required_field"
        )
        
        # Get the metrics
        response = requests.get(f"http://localhost:{self.server_port}/metrics")
        self.assertEqual(response.status_code, 200)
        
        # Check if the validation error was recorded
        self.assertIn(
            "validation_errors_total{content_type=\"CRYPTO\",error_type=\"missing_required_field\"} 1.0",
            response.text
        )
    
    def test_extraction_timer(self):
        """Test the ExtractionTimer context manager."""
        # Use the ExtractionTimer context manager
        with ExtractionTimer(content_type="NEWS", content_size_bytes=2000) as timer:
            # Simulate some work
            time.sleep(0.1)
            
            # Set success metrics
            timer.set_success(
                token_usage=200,
                estimated_cost_dollars=0.004,
                quality_score=0.9
            )
        
        # Get the metrics
        response = requests.get(f"http://localhost:{self.server_port}/metrics")
        self.assertEqual(response.status_code, 200)
        
        # Check if the timer metrics were recorded
        self.assertIn("extraction_attempts_total{content_type=\"NEWS\"} 1.0", response.text)
        self.assertIn("extraction_successes_total{content_type=\"NEWS\"} 1.0", response.text)
        self.assertIn("extraction_tokens_total{content_type=\"NEWS\"} 200.0", response.text)
        self.assertIn("extraction_cost_dollars_total{content_type=\"NEWS\"} 0.004", response.text)
        self.assertIn("extraction_quality_score{content_type=\"NEWS\"} 0.9", response.text)
        self.assertIn("extraction_content_size_bytes_bucket", response.text)
    
    def test_extraction_timer_failure(self):
        """Test the ExtractionTimer context manager with a failure."""
        try:
            with ExtractionTimer(content_type="CRYPTO", content_size_bytes=3000):
                # Simulate an error
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Get the metrics
        response = requests.get(f"http://localhost:{self.server_port}/metrics")
        self.assertEqual(response.status_code, 200)
        
        # Check if the failure was recorded
        self.assertIn("extraction_attempts_total{content_type=\"CRYPTO\"} 1.0", response.text)
        self.assertIn("extraction_failures_total{content_type=\"CRYPTO\",error=\"ValueError\"} 1.0", response.text)


class TestAsyncExtractionTimer(unittest.IsolatedAsyncioTestCase):
    """Test cases for the ExtractionTimer with async functions."""
    
    async def asyncSetUp(self):
        """Set up the test environment."""
        # Create a new ExtractionMetrics instance for each test
        self.metrics = ExtractionMetrics()
        
        # Start a metrics server in a separate thread
        self.server_port = 8002
        self.server_thread = threading.Thread(
            target=start_metrics_server,
            args=(self.server_port,),
            daemon=True
        )
        self.server_thread.start()
        
        # Wait for the server to start
        await asyncio.sleep(1)
    
    async def test_async_extraction_timer(self):
        """Test the ExtractionTimer context manager with async functions."""
        # Use the ExtractionTimer context manager
        with ExtractionTimer(content_type="SOCIAL_MEDIA", content_size_bytes=4000) as timer:
            # Simulate some async work
            await asyncio.sleep(0.1)
            
            # Set success metrics
            timer.set_success(
                token_usage=300,
                estimated_cost_dollars=0.006,
                quality_score=0.95
            )
        
        # Get the metrics
        response = requests.get(f"http://localhost:{self.server_port}/metrics")
        self.assertEqual(response.status_code, 200)
        
        # Check if the timer metrics were recorded
        self.assertIn("extraction_attempts_total{content_type=\"SOCIAL_MEDIA\"} 1.0", response.text)
        self.assertIn("extraction_successes_total{content_type=\"SOCIAL_MEDIA\"} 1.0", response.text)
        self.assertIn("extraction_tokens_total{content_type=\"SOCIAL_MEDIA\"} 300.0", response.text)
        self.assertIn("extraction_cost_dollars_total{content_type=\"SOCIAL_MEDIA\"} 0.006", response.text)
        self.assertIn("extraction_quality_score{content_type=\"SOCIAL_MEDIA\"} 0.95", response.text)
        self.assertIn("extraction_content_size_bytes_bucket", response.text)


if __name__ == "__main__":
    unittest.main()