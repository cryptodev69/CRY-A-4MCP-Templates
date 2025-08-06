#!/usr/bin/env python3
"""
Metrics module for the cry_a_4mcp.crawl4ai package.

This module provides utilities for tracking and reporting metrics related to
extraction performance, success rates, and token usage across different providers.
"""

import time
import logging
from typing import Dict, Any, Optional, List, Callable, Union
from functools import wraps
import json
import os
from datetime import datetime

# Conditionally import prometheus_client if available
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("prometheus_client not installed. Prometheus metrics will not be available.")

logger = logging.getLogger(__name__)


class MetricsRegistry:
    """Registry for tracking metrics related to extraction operations."""

    def __init__(self, enable_prometheus: bool = True, metrics_dir: Optional[str] = None):
        """Initialize the metrics registry.
        
        Args:
            enable_prometheus: Whether to enable Prometheus metrics
            metrics_dir: Optional directory to store metrics data
        """
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.metrics_dir = metrics_dir
        
        # Create metrics directory if it doesn't exist
        if self.metrics_dir and not os.path.exists(self.metrics_dir):
            os.makedirs(self.metrics_dir)
        
        # Initialize metrics
        self._init_prometheus_metrics() if self.enable_prometheus else None
        
        # In-memory metrics for when Prometheus is not available
        self.extraction_count = 0
        self.extraction_success_count = 0
        self.extraction_failure_count = 0
        self.extraction_times = []
        self.token_usage = {}
        self.provider_usage = {}
        self.model_usage = {}
        self.content_type_counts = {}
        self.validation_error_counts = {}
        
        logger.info(f"Metrics registry initialized with Prometheus {'enabled' if self.enable_prometheus else 'disabled'}")

    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        # Extraction counters
        self.prom_extraction_count = Counter(
            'crawl4ai_extraction_total',
            'Total number of extraction attempts',
            ['provider', 'model', 'content_type']
        )
        
        self.prom_extraction_success = Counter(
            'crawl4ai_extraction_success_total',
            'Total number of successful extractions',
            ['provider', 'model', 'content_type']
        )
        
        self.prom_extraction_failure = Counter(
            'crawl4ai_extraction_failure_total',
            'Total number of failed extractions',
            ['provider', 'model', 'content_type', 'error_type']
        )
        
        # Extraction time histogram
        self.prom_extraction_time = Histogram(
            'crawl4ai_extraction_duration_seconds',
            'Time taken for extraction operations',
            ['provider', 'model', 'content_type'],
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 15.0, 30.0, 60.0, 120.0)
        )
        
        # Token usage counters
        self.prom_token_usage = Counter(
            'crawl4ai_token_usage_total',
            'Total number of tokens used',
            ['provider', 'model', 'token_type']
        )
        
        # Cost tracking (estimated)
        self.prom_estimated_cost = Counter(
            'crawl4ai_estimated_cost_total',
            'Estimated cost of API usage in USD',
            ['provider', 'model']
        )
        
        # Quality metrics
        self.prom_extraction_quality = Gauge(
            'crawl4ai_extraction_quality',
            'Quality score of extraction results',
            ['provider', 'model', 'content_type']
        )
        
        # Validation errors
        self.prom_validation_errors = Counter(
            'crawl4ai_validation_errors_total',
            'Total number of validation errors',
            ['error_type', 'content_type']
        )
        
        # Content size metrics
        self.prom_content_size = Summary(
            'crawl4ai_content_size_bytes',
            'Size of content being processed',
            ['content_type']
        )

    def track_extraction_attempt(self, provider: str, model: str, content_type: str):
        """Track an extraction attempt.
        
        Args:
            provider: The provider used for extraction
            model: The model used for extraction
            content_type: The type of content being extracted
        """
        self.extraction_count += 1
        
        # Update provider and model usage
        self.provider_usage[provider] = self.provider_usage.get(provider, 0) + 1
        self.model_usage[model] = self.model_usage.get(model, 0) + 1
        self.content_type_counts[content_type] = self.content_type_counts.get(content_type, 0) + 1
        
        # Update Prometheus metrics if enabled
        if self.enable_prometheus:
            self.prom_extraction_count.labels(provider=provider, model=model, content_type=content_type).inc()

    def track_extraction_success(self, provider: str, model: str, content_type: str, duration: float):
        """Track a successful extraction.
        
        Args:
            provider: The provider used for extraction
            model: The model used for extraction
            content_type: The type of content being extracted
            duration: The time taken for extraction in seconds
        """
        self.extraction_success_count += 1
        self.extraction_times.append(duration)
        
        # Update Prometheus metrics if enabled
        if self.enable_prometheus:
            self.prom_extraction_success.labels(provider=provider, model=model, content_type=content_type).inc()
            self.prom_extraction_time.labels(provider=provider, model=model, content_type=content_type).observe(duration)

    def track_extraction_failure(self, provider: str, model: str, content_type: str, error_type: str):
        """Track a failed extraction.
        
        Args:
            provider: The provider used for extraction
            model: The model used for extraction
            content_type: The type of content being extracted
            error_type: The type of error that occurred
        """
        self.extraction_failure_count += 1
        
        # Update Prometheus metrics if enabled
        if self.enable_prometheus:
            self.prom_extraction_failure.labels(
                provider=provider, model=model, content_type=content_type, error_type=error_type
            ).inc()

    def track_token_usage(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int):
        """Track token usage for an extraction.
        
        Args:
            provider: The provider used for extraction
            model: The model used for extraction
            prompt_tokens: The number of prompt tokens used
            completion_tokens: The number of completion tokens used
        """
        total_tokens = prompt_tokens + completion_tokens
        
        # Update token usage tracking
        provider_key = f"{provider}:{model}"
        if provider_key not in self.token_usage:
            self.token_usage[provider_key] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        
        self.token_usage[provider_key]["prompt_tokens"] += prompt_tokens
        self.token_usage[provider_key]["completion_tokens"] += completion_tokens
        self.token_usage[provider_key]["total_tokens"] += total_tokens
        
        # Update Prometheus metrics if enabled
        if self.enable_prometheus:
            self.prom_token_usage.labels(provider=provider, model=model, token_type="prompt").inc(prompt_tokens)
            self.prom_token_usage.labels(provider=provider, model=model, token_type="completion").inc(completion_tokens)
            self.prom_token_usage.labels(provider=provider, model=model, token_type="total").inc(total_tokens)

    def track_estimated_cost(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int):
        """Track estimated cost for an extraction.
        
        Args:
            provider: The provider used for extraction
            model: The model used for extraction
            prompt_tokens: The number of prompt tokens used
            completion_tokens: The number of completion tokens used
        """
        # Simplified cost estimation based on common pricing models
        # These are approximate and should be updated based on actual pricing
        cost_per_1k_tokens = {
            "openai": {
                "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
                "gpt-4": {"prompt": 0.03, "completion": 0.06},
                "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03}
            },
            "openrouter": {
                # Simplified - actual costs vary by model
                "default": {"prompt": 0.005, "completion": 0.01}
            },
            "groq": {
                "llama2-70b": {"prompt": 0.0007, "completion": 0.0007},
                "mixtral-8x7b": {"prompt": 0.0007, "completion": 0.0007}
            }
        }
        
        # Get cost rates for the provider and model
        provider_costs = cost_per_1k_tokens.get(provider.lower(), {})
        model_costs = provider_costs.get(model, provider_costs.get("default", {"prompt": 0.001, "completion": 0.002}))
        
        # Calculate cost
        prompt_cost = (prompt_tokens / 1000) * model_costs.get("prompt", 0.001)
        completion_cost = (completion_tokens / 1000) * model_costs.get("completion", 0.002)
        total_cost = prompt_cost + completion_cost
        
        # Update Prometheus metrics if enabled
        if self.enable_prometheus:
            self.prom_estimated_cost.labels(provider=provider, model=model).inc(total_cost)
        
        return total_cost

    def track_extraction_quality(self, provider: str, model: str, content_type: str, quality_score: float):
        """Track the quality of an extraction result.
        
        Args:
            provider: The provider used for extraction
            model: The model used for extraction
            content_type: The type of content being extracted
            quality_score: The quality score (0.0 to 1.0)
        """
        # Update Prometheus metrics if enabled
        if self.enable_prometheus:
            self.prom_extraction_quality.labels(provider=provider, model=model, content_type=content_type).set(quality_score)

    def track_validation_error(self, error_type: str, content_type: str):
        """Track a validation error.
        
        Args:
            error_type: The type of validation error
            content_type: The type of content being validated
        """
        error_key = f"{content_type}:{error_type}"
        self.validation_error_counts[error_key] = self.validation_error_counts.get(error_key, 0) + 1
        
        # Update Prometheus metrics if enabled
        if self.enable_prometheus:
            self.prom_validation_errors.labels(error_type=error_type, content_type=content_type).inc()

    def track_content_size(self, content_type: str, size_bytes: int):
        """Track the size of content being processed.
        
        Args:
            content_type: The type of content being processed
            size_bytes: The size of the content in bytes
        """
        # Update Prometheus metrics if enabled
        if self.enable_prometheus:
            self.prom_content_size.labels(content_type=content_type).observe(size_bytes)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of tracked metrics.
        
        Returns:
            Dictionary containing metrics summary
        """
        avg_extraction_time = sum(self.extraction_times) / len(self.extraction_times) if self.extraction_times else 0
        success_rate = (self.extraction_success_count / self.extraction_count) * 100 if self.extraction_count > 0 else 0
        
        return {
            "extraction": {
                "total": self.extraction_count,
                "success": self.extraction_success_count,
                "failure": self.extraction_failure_count,
                "success_rate": success_rate,
                "avg_time": avg_extraction_time
            },
            "token_usage": self.token_usage,
            "provider_usage": self.provider_usage,
            "model_usage": self.model_usage,
            "content_types": self.content_type_counts,
            "validation_errors": self.validation_error_counts
        }

    def save_metrics_to_file(self, filename: Optional[str] = None) -> None:
        """Save metrics to a JSON file.
        
        Args:
            filename: Optional filename to save metrics to
        """
        if not self.metrics_dir:
            logger.warning("Metrics directory not set, cannot save metrics to file")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.json"
        
        filepath = os.path.join(self.metrics_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.get_metrics_summary(), f, indent=2)
            logger.info(f"Metrics saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save metrics to {filepath}: {str(e)}")


# Global metrics registry instance
default_metrics_registry = MetricsRegistry(
    enable_prometheus=True,
    metrics_dir=os.environ.get("CRAWL4AI_METRICS_DIR")
)


def calculate_extraction_quality(extraction: Dict[str, Any], content_type: str) -> float:
    """Calculate a quality score for an extraction result.
    
    Args:
        extraction: The extraction result to score
        content_type: The type of content that was extracted
        
    Returns:
        Quality score between 0.0 and 1.0
    """
    # Base score starts at 0.5
    score = 0.5
    
    # Check for presence of key fields based on content type
    if content_type == "crypto":
        required_fields = ["headline", "summary", "sentiment", "market_impact"]
        optional_fields = ["category", "key_entities", "persona_relevance", "urgency_score", "price_mentions"]
    elif content_type == "news":
        required_fields = ["headline", "summary"]
        optional_fields = ["author", "publication_date", "category", "sentiment", "key_points", "entities"]
    elif content_type == "social_media":
        required_fields = ["content", "sentiment"]
        optional_fields = ["username", "platform", "post_date", "engagement", "hashtags", "mentions"]
    else:
        # Generic scoring for unknown content types
        required_fields = []
        optional_fields = list(extraction.keys())
    
    # Score based on required fields (up to +0.5)
    if required_fields:
        present_required = sum(1 for field in required_fields if field in extraction)
        score += 0.5 * (present_required / len(required_fields))
    
    # Score based on optional fields (up to +0.3)
    if optional_fields:
        present_optional = sum(1 for field in optional_fields if field in extraction)
        score += 0.3 * (present_optional / len(optional_fields))
    
    # Check for non-empty values in required fields (up to -0.3)
    empty_penalties = 0
    for field in required_fields:
        if field in extraction:
            value = extraction[field]
            if value is None or (isinstance(value, str) and not value.strip()):
                empty_penalties += 1
    
    if required_fields:
        score -= 0.3 * (empty_penalties / len(required_fields))
    
    # Check for metadata completeness (up to +0.2)
    if "_metadata" in extraction:
        metadata = extraction["_metadata"]
        metadata_fields = ["model", "timestamp", "usage", "performance"]
        present_metadata = sum(1 for field in metadata_fields if field in metadata)
        score += 0.2 * (present_metadata / len(metadata_fields))
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))


def track_extraction_metrics(func):
    """Decorator to track metrics for extraction operations.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # Get content type if available
        content_type = kwargs.get("content_type", "unknown")
        
        # Track content size if html is provided
        html = kwargs.get("html", "")
        if html:
            default_metrics_registry.track_content_size(content_type, len(html.encode('utf-8')))
        
        # Track extraction attempt
        provider = getattr(self, "provider", "unknown")
        model = getattr(self, "model", "unknown")
        default_metrics_registry.track_extraction_attempt(provider, model, content_type)
        
        start_time = time.time()
        try:
            # Call the original function
            result = await func(self, *args, **kwargs)
            
            # Track successful extraction
            duration = time.time() - start_time
            default_metrics_registry.track_extraction_success(provider, model, content_type, duration)
            
            # Track token usage if available in result
            if result and "_metadata" in result and "usage" in result["_metadata"]:
                usage = result["_metadata"]["usage"]
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                
                default_metrics_registry.track_token_usage(
                    provider, model, prompt_tokens, completion_tokens
                )
                
                default_metrics_registry.track_estimated_cost(
                    provider, model, prompt_tokens, completion_tokens
                )
            
            # Calculate and track extraction quality
            if result:
                quality_score = calculate_extraction_quality(
                    result, result.get("_metadata", {}).get("content_type", content_type)
                )
                default_metrics_registry.track_extraction_quality(provider, model, content_type, quality_score)
            
            return result
        except Exception as e:
            # Track failed extraction
            error_type = type(e).__name__
            default_metrics_registry.track_extraction_failure(provider, model, content_type, error_type)
            raise
    
    return wrapper


def get_metrics_summary() -> Dict[str, Any]:
    """Get a summary of tracked metrics.
    
    Returns:
        Dictionary containing metrics summary
    """
    return default_metrics_registry.get_metrics_summary()


def save_metrics_to_file(filename: Optional[str] = None) -> None:
    """Save metrics to a JSON file.
    
    Args:
        filename: Optional filename to save metrics to
    """
    default_metrics_registry.save_metrics_to_file(filename)