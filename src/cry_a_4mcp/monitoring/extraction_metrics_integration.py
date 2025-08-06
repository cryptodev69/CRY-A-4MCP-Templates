#!/usr/bin/env python3
"""
Extraction Metrics Integration for CRY-A-4MCP

This module demonstrates how to integrate the metrics exporter with the extraction service.
It provides utility functions and decorators to automatically track extraction metrics.

Usage:
    Import this module and use the decorators to track extraction metrics:
    ```python
    from cry_a_4mcp.monitoring.extraction_metrics_integration import track_extraction
    
    @track_extraction
    async def extract_content(content, content_type="CRYPTO"):
        # Extraction logic here
        return extracted_data
    ```

    Or use the context manager directly:
    ```python
    from cry_a_4mcp.monitoring.extraction_metrics_integration import ExtractionMetricsTracker
    
    async def extract_content(content, content_type="CRYPTO"):
        with ExtractionMetricsTracker(content, content_type) as tracker:
            # Extraction logic here
            result = await perform_extraction(content)
            tracker.set_result(result)
            return result
    ```
"""

import functools
import time
import logging
from typing import Any, Callable, Dict, Optional, Union, TypeVar, cast
from functools import wraps
import inspect

# Import the metrics exporter
try:
    from cry_a_4mcp.monitoring.metrics_exporter import extraction_metrics, ExtractionTimer
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    logging.warning("Metrics exporter not available. Metrics will not be tracked.")

# Import schema validation if available
try:
    from cry_a_4mcp.extraction.schema_validation import SchemaValidator
    SCHEMA_VALIDATION_AVAILABLE = True
except ImportError:
    SCHEMA_VALIDATION_AVAILABLE = False
    logging.warning("Schema validation not available. Validation errors will not be tracked.")


class ExtractionMetricsTracker:
    """
    Context manager for tracking extraction metrics.
    
    This class provides a context manager that automatically tracks extraction metrics,
    including extraction time, token usage, cost, and quality.
    """
    
    def __init__(self, content: str, content_type: str = "CRYPTO"):
        """
        Initialize the extraction metrics tracker.
        
        Args:
            content: The content to extract from
            content_type: Type of content being extracted (e.g., CRYPTO, NEWS, SOCIAL_MEDIA)
        """
        self.content = content
        self.content_type = content_type
        self.content_size_bytes = len(content.encode('utf-8'))
        self.result = None
        self.extraction_timer = None
        
        if METRICS_AVAILABLE:
            self.extraction_timer = ExtractionTimer(
                content_type=content_type,
                content_size_bytes=self.content_size_bytes
            )
    
    def __enter__(self):
        """
        Enter the context manager and start tracking metrics.
        """
        if self.extraction_timer:
            self.extraction_timer.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and record metrics.
        """
        if self.extraction_timer:
            self.extraction_timer.__exit__(exc_type, exc_val, exc_tb)
    
    def set_result(self, result: Dict[str, Any]) -> None:
        """
        Set the extraction result and record metrics.
        
        Args:
            result: The extraction result
        """
        self.result = result
        
        if not self.extraction_timer or not METRICS_AVAILABLE:
            return
        
        # Extract metrics from the result
        token_usage = result.get('_metadata', {}).get('token_usage', 0)
        estimated_cost = result.get('_metadata', {}).get('estimated_cost_dollars', 0.0)
        quality_score = result.get('_metadata', {}).get('extraction_quality', 0.8)
        
        # Set success metrics
        self.extraction_timer.set_success(
            token_usage=token_usage,
            estimated_cost_dollars=estimated_cost,
            quality_score=quality_score
        )
        
        # Track validation errors if schema validation is available
        if SCHEMA_VALIDATION_AVAILABLE and METRICS_AVAILABLE:
            self._track_validation_errors(result)
    
    def _track_validation_errors(self, result: Dict[str, Any]) -> None:
        """
        Track validation errors in the extraction result.
        
        Args:
            result: The extraction result
        """
        if not SCHEMA_VALIDATION_AVAILABLE or not METRICS_AVAILABLE:
            return
        
        # Check for validation errors in the result metadata
        validation_errors = result.get('_metadata', {}).get('validation_errors', [])
        
        for error in validation_errors:
            error_type = error.get('error_type', 'other')
            extraction_metrics.record_validation_error(
                content_type=self.content_type,
                error_type=error_type
            )


# Type variable for function return type
T = TypeVar('T')


def track_extraction(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to track extraction metrics.
    
    This decorator wraps an extraction function and automatically tracks metrics
    for the extraction, including time, token usage, cost, and quality.
    
    Args:
        func: The extraction function to wrap
    
    Returns:
        The wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract content and content_type from arguments
        content = None
        content_type = "CRYPTO"  # Default content type
        
        # Try to find content in positional arguments
        if len(args) > 0:
            content = args[0]
        
        # Try to find content_type in keyword arguments
        if 'content_type' in kwargs:
            content_type = kwargs['content_type']
        
        # If content is not found, try to find it in keyword arguments
        if content is None and 'content' in kwargs:
            content = kwargs['content']
        
        # If content is still None, we can't track metrics
        if content is None:
            return func(*args, **kwargs)
        
        # Create a tracker
        with ExtractionMetricsTracker(content, content_type) as tracker:
            # Call the function
            result = func(*args, **kwargs)
            
            # If the result is a dictionary, set it in the tracker
            if isinstance(result, dict):
                tracker.set_result(result)
            
            return result
    
    # If the function is async, we need to handle it differently
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract content and content_type from arguments
            content = None
            content_type = "CRYPTO"  # Default content type
            
            # Try to find content in positional arguments
            if len(args) > 0:
                content = args[0]
            
            # Try to find content_type in keyword arguments
            if 'content_type' in kwargs:
                content_type = kwargs['content_type']
            
            # If content is not found, try to find it in keyword arguments
            if content is None and 'content' in kwargs:
                content = kwargs['content']
            
            # If content is still None, we can't track metrics
            if content is None:
                return await func(*args, **kwargs)
            
            # Create a tracker
            with ExtractionMetricsTracker(content, content_type) as tracker:
                # Call the function
                result = await func(*args, **kwargs)
                
                # If the result is a dictionary, set it in the tracker
                if isinstance(result, dict):
                    tracker.set_result(result)
                
                return result
        
        return cast(Callable[..., T], async_wrapper)
    
    return cast(Callable[..., T], wrapper)


# Example usage
if __name__ == "__main__":
    import asyncio
    import random
    import json
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Sample content
    SAMPLE_CONTENT = """
    Bitcoin ETFs Finally Approved by SEC After Decade-Long Battle
    
    The U.S. Securities and Exchange Commission has approved spot Bitcoin exchange-traded funds,
    marking a historic moment for the cryptocurrency industry after a decade-long battle for acceptance.
    
    The approval allows financial giants like BlackRock, Fidelity, and Grayscale to offer investment
    products that directly track Bitcoin's price, potentially opening the cryptocurrency to millions
    of traditional investors.
    
    "This is a watershed moment for the crypto industry," said Michael Sonnenshein, CEO of Grayscale
    Investments. "It legitimizes Bitcoin as an asset class and makes it accessible through traditional
    investment accounts."
    
    The decision comes after SEC Chair Gary Gensler, who has been skeptical of cryptocurrencies,
    faced pressure from courts and the financial industry to approve the products.
    
    Bitcoin's price surged on the news, reaching $47,500, its highest level in nearly two years.
    
    Analysts expect the ETFs to attract billions in inflows in their first year, with some projecting
    up to $100 billion over time.
    """
    
    # Define a sample extraction function
    @track_extraction
    async def extract_content(content, content_type="CRYPTO"):
        # Simulate extraction time
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Simulate extraction result
        result = {
            "headline": "Bitcoin ETFs Finally Approved by SEC After Decade-Long Battle",
            "summary": "The SEC has approved spot Bitcoin ETFs after a decade-long battle, allowing financial giants to offer products tracking Bitcoin's price.",
            "entities": ["Bitcoin", "SEC", "BlackRock", "Fidelity", "Grayscale"],
            "sentiment": "positive",
            "_metadata": {
                "token_usage": random.randint(100, 500),
                "estimated_cost_dollars": random.uniform(0.001, 0.01),
                "extraction_quality": random.uniform(0.7, 1.0),
                "validation_errors": []
            }
        }
        
        # Randomly add validation errors
        if random.random() < 0.2:
            result["_metadata"]["validation_errors"].append({
                "error_type": "missing_required_field",
                "field": "source",
                "message": "Required field 'source' is missing"
            })
        
        return result
    
    # Run the example
    async def main():
        # Start the metrics server if available
        if METRICS_AVAILABLE:
            from cry_a_4mcp.monitoring.metrics_exporter import start_metrics_server
            start_metrics_server(port=8000)
            logging.info("Metrics server started on port 8000")
        
        # Perform extractions
        content_types = ["CRYPTO", "NEWS", "SOCIAL_MEDIA"]
        
        for _ in range(10):
            for content_type in content_types:
                try:
                    result = await extract_content(SAMPLE_CONTENT, content_type=content_type)
                    logging.info(f"Extracted {content_type} content: {json.dumps(result, indent=2)}")
                except Exception as e:
                    logging.error(f"Error extracting {content_type} content: {e}")
            
            # Wait before next batch
            await asyncio.sleep(1)
        
        logging.info("Example completed. Metrics are available at http://localhost:8000/metrics")
    
    # Run the main function
    asyncio.run(main())