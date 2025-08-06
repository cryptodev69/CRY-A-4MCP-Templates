#!/usr/bin/env python3
"""
Metrics Exporter for CRY-A-4MCP Extraction Service

This module provides a Prometheus metrics exporter for the extraction service,
tracking extraction attempts, successes, failures, time, token usage, cost,
quality, content size, and validation errors.

It exposes metrics via an HTTP endpoint that can be scraped by Prometheus.

Usage:
    Import this module and initialize the metrics in your application:
    ```python
    from cry_a_4mcp.monitoring.metrics_exporter import extraction_metrics
    
    # Record an extraction attempt
    extraction_metrics.record_extraction_attempt(content_type="CRYPTO", content_size_bytes=1024)
    
    # Record a successful extraction
    extraction_metrics.record_extraction_success(
        content_type="CRYPTO",
        extraction_time_seconds=1.5,
        token_usage=150,
        estimated_cost_dollars=0.002,
        quality_score=0.85
    )
    
    # Record a validation error
    extraction_metrics.record_validation_error(
        content_type="CRYPTO",
        error_type="missing_required_field"
    )
    ```

    Start the metrics server:
    ```python
    from cry_a_4mcp.monitoring.metrics_exporter import start_metrics_server
    
    # Start the metrics server on port 8000
    start_metrics_server(port=8000)
    ```
"""

import time
from typing import Dict, Optional, Union, List
from dataclasses import dataclass
import threading
import logging

# Conditional import for prometheus_client
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Summary
    from prometheus_client import start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("prometheus_client not available. Metrics will not be exported.")


@dataclass
class ExtractionMetrics:
    """
    Class for tracking extraction metrics using Prometheus.
    
    This class provides methods to record extraction attempts, successes, failures,
    and validation errors, along with associated metrics like extraction time,
    token usage, cost, quality, and content size.
    """
    
    def __init__(self):
        """
        Initialize Prometheus metrics for extraction monitoring.
        
        Creates counters, histograms, and summaries for tracking extraction metrics.
        If prometheus_client is not available, dummy metrics will be used.
        """
        self.enabled = PROMETHEUS_AVAILABLE
        
        if not self.enabled:
            return
        
        # Counters for tracking extraction attempts, successes, and failures
        self.extraction_attempts = Counter(
            'extraction_attempts_total',
            'Total number of extraction attempts',
            ['content_type']
        )
        
        self.extraction_successes = Counter(
            'extraction_successes_total',
            'Total number of successful extractions',
            ['content_type']
        )
        
        self.extraction_failures = Counter(
            'extraction_failures_total',
            'Total number of failed extractions',
            ['content_type']
        )
        
        # Histogram for extraction time
        self.extraction_time = Histogram(
            'extraction_time_seconds',
            'Time taken for extraction in seconds',
            ['content_type'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
        )
        
        # Counter for token usage
        self.token_usage = Counter(
            'token_usage_total',
            'Total token usage',
            ['content_type']
        )
        
        # Counter for estimated cost
        self.estimated_cost = Counter(
            'estimated_cost_dollars_total',
            'Total estimated cost in dollars',
            ['content_type']
        )
        
        # Gauge for extraction quality
        self.extraction_quality = Gauge(
            'extraction_quality_score',
            'Quality score of extractions',
            ['content_type']
        )
        
        # Summary for content size
        self.content_size = Summary(
            'content_size_bytes',
            'Size of content in bytes',
            ['content_type']
        )
        
        # Counter for validation errors
        self.validation_errors = Counter(
            'validation_errors_total',
            'Total number of validation errors',
            ['content_type', 'error_type']
        )
    
    def record_extraction_attempt(self, content_type: str, content_size_bytes: int) -> None:
        """
        Record an extraction attempt.
        
        Args:
            content_type: Type of content being extracted (e.g., CRYPTO, NEWS, SOCIAL_MEDIA)
            content_size_bytes: Size of the content in bytes
        """
        if not self.enabled:
            return
        
        self.extraction_attempts.labels(content_type=content_type).inc()
        self.content_size.labels(content_type=content_type).observe(content_size_bytes)
    
    def record_extraction_success(
        self,
        content_type: str,
        extraction_time_seconds: float,
        token_usage: int,
        estimated_cost_dollars: float,
        quality_score: float
    ) -> None:
        """
        Record a successful extraction.
        
        Args:
            content_type: Type of content being extracted (e.g., CRYPTO, NEWS, SOCIAL_MEDIA)
            extraction_time_seconds: Time taken for extraction in seconds
            token_usage: Number of tokens used for extraction
            estimated_cost_dollars: Estimated cost of extraction in dollars
            quality_score: Quality score of extraction (0.0 to 1.0)
        """
        if not self.enabled:
            return
        
        self.extraction_successes.labels(content_type=content_type).inc()
        self.extraction_time.labels(content_type=content_type).observe(extraction_time_seconds)
        self.token_usage.labels(content_type=content_type).inc(token_usage)
        self.estimated_cost.labels(content_type=content_type).inc(estimated_cost_dollars)
        self.extraction_quality.labels(content_type=content_type).set(quality_score)
    
    def record_extraction_failure(self, content_type: str) -> None:
        """
        Record an extraction failure.
        
        Args:
            content_type: Type of content being extracted (e.g., CRYPTO, NEWS, SOCIAL_MEDIA)
        """
        if not self.enabled:
            return
        
        self.extraction_failures.labels(content_type=content_type).inc()
    
    def record_validation_error(
        self,
        content_type: str,
        error_type: str
    ) -> None:
        """
        Record a validation error.
        
        Args:
            content_type: Type of content being extracted (e.g., CRYPTO, NEWS, SOCIAL_MEDIA)
            error_type: Type of validation error (e.g., missing_required_field, invalid_field_type)
        """
        if not self.enabled:
            return
        
        self.validation_errors.labels(
            content_type=content_type,
            error_type=error_type
        ).inc()


# Create a global instance of ExtractionMetrics
extraction_metrics = ExtractionMetrics()


def start_metrics_server(port: int = 8000) -> None:
    """
    Start a Prometheus metrics server on the specified port.
    
    Args:
        port: Port number to expose metrics on (default: 8000)
    """
    if not PROMETHEUS_AVAILABLE:
        logging.warning("Cannot start metrics server: prometheus_client not available")
        return
    
    try:
        start_http_server(port)
        logging.info(f"Metrics server started on port {port}")
    except Exception as e:
        logging.error(f"Failed to start metrics server: {e}")


class ExtractionTimer:
    """
    Context manager for timing extractions and recording metrics.
    
    Usage:
        ```python
        with ExtractionTimer(content_type="CRYPTO", content_size_bytes=1024) as timer:
            # Perform extraction
            result = extract_content(content)
            
            # Set extraction results
            timer.set_success(
                token_usage=150,
                estimated_cost_dollars=0.002,
                quality_score=0.85
            )
        ```
    """
    
    def __init__(self, content_type: str, content_size_bytes: int):
        """
        Initialize the extraction timer.
        
        Args:
            content_type: Type of content being extracted (e.g., CRYPTO, NEWS, SOCIAL_MEDIA)
            content_size_bytes: Size of the content in bytes
        """
        self.content_type = content_type
        self.content_size_bytes = content_size_bytes
        self.start_time = None
        self.success = False
        self.token_usage = 0
        self.estimated_cost_dollars = 0.0
        self.quality_score = 0.0
    
    def __enter__(self):
        """
        Start timing the extraction and record the attempt.
        """
        extraction_metrics.record_extraction_attempt(
            content_type=self.content_type,
            content_size_bytes=self.content_size_bytes
        )
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Stop timing the extraction and record the result.
        """
        if self.start_time is None:
            return
        
        extraction_time_seconds = time.time() - self.start_time
        
        if self.success:
            extraction_metrics.record_extraction_success(
                content_type=self.content_type,
                extraction_time_seconds=extraction_time_seconds,
                token_usage=self.token_usage,
                estimated_cost_dollars=self.estimated_cost_dollars,
                quality_score=self.quality_score
            )
        else:
            extraction_metrics.record_extraction_failure(
                content_type=self.content_type
            )
    
    def set_success(
        self,
        token_usage: int,
        estimated_cost_dollars: float,
        quality_score: float
    ) -> None:
        """
        Set the extraction as successful and record metrics.
        
        Args:
            token_usage: Number of tokens used for extraction
            estimated_cost_dollars: Estimated cost of extraction in dollars
            quality_score: Quality score of extraction (0.0 to 1.0)
        """
        self.success = True
        self.token_usage = token_usage
        self.estimated_cost_dollars = estimated_cost_dollars
        self.quality_score = quality_score


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    if not PROMETHEUS_AVAILABLE:
        logging.error("prometheus_client not available. Please install it with 'pip install prometheus_client'")
        exit(1)
    
    # Start the metrics server
    start_metrics_server(port=8000)
    
    # Simulate some extractions
    def simulate_extractions():
        content_types = ["CRYPTO", "NEWS", "SOCIAL_MEDIA"]
        error_types = ["missing_required_field", "invalid_field_type", "invalid_field_value"]
        
        while True:
            for content_type in content_types:
                # Simulate an extraction
                with ExtractionTimer(content_type=content_type, content_size_bytes=1024) as timer:
                    # Simulate extraction time
                    time.sleep(0.1)
                    
                    # 80% success rate
                    if time.time() % 5 != 0:
                        timer.set_success(
                            token_usage=150,
                            estimated_cost_dollars=0.002,
                            quality_score=0.85
                        )
                        
                        # 10% validation error rate
                        if time.time() % 10 == 0:
                            import random
                            error_type = random.choice(error_types)
                            extraction_metrics.record_validation_error(
                                content_type=content_type,
                                error_type=error_type
                            )
            
            # Wait before next batch
            time.sleep(1)
    
    # Start simulation in a separate thread
    simulation_thread = threading.Thread(target=simulate_extractions)
    simulation_thread.daemon = True
    simulation_thread.start()
    
    logging.info("Metrics simulation started. Press Ctrl+C to exit.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Exiting...")