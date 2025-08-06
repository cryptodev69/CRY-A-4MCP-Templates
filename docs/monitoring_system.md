# Monitoring System for CRY-A-4MCP

This document provides a comprehensive guide to the monitoring system implemented for the CRY-A-4MCP platform. The monitoring system tracks extraction metrics, validates schema compliance, and provides real-time dashboards for system health and performance.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Metrics Tracked](#metrics-tracked)
- [Setup Instructions](#setup-instructions)
- [Integration Guide](#integration-guide)
- [Dashboards](#dashboards)
- [Alerting](#alerting)
- [Troubleshooting](#troubleshooting)
- [Extending the System](#extending-the-system)

## Overview

The CRY-A-4MCP monitoring system provides comprehensive visibility into the extraction service's performance, quality, and reliability. It tracks key metrics such as extraction success rates, processing times, token usage, and validation errors, enabling proactive identification of issues and optimization opportunities.

## Architecture

The monitoring system consists of the following components:

1. **Metrics Exporter**: A Python module that collects and exposes metrics from the extraction service.
2. **Prometheus**: A time-series database that scrapes and stores metrics.
3. **Grafana**: A visualization platform that provides dashboards for the metrics.
4. **Alertmanager**: A component that handles alerts from Prometheus and routes them to the appropriate channels.

![Monitoring Architecture](../docs/images/monitoring_architecture.png)

## Metrics Tracked

The monitoring system tracks the following metrics:

### Extraction Metrics

| Metric | Description | Type |
|--------|-------------|------|
| `extraction_attempts_total` | Total number of extraction attempts | Counter |
| `extraction_successes_total` | Total number of successful extractions | Counter |
| `extraction_failures_total` | Total number of failed extractions | Counter |
| `extraction_time_seconds` | Time taken for extraction in seconds | Histogram |
| `extraction_tokens_total` | Total number of tokens used in extractions | Counter |
| `extraction_cost_dollars_total` | Total cost of extractions in dollars | Counter |
| `extraction_quality_score` | Quality score of extractions (0-1) | Gauge |
| `extraction_content_size_bytes` | Size of extracted content in bytes | Histogram |

### Validation Metrics

| Metric | Description | Type |
|--------|-------------|------|
| `validation_errors_total` | Total number of validation errors | Counter |

### Recording Rules

The system also includes recording rules that calculate derived metrics:

| Metric | Description | Formula |
|--------|-------------|--------|
| `extraction:success_rate:5m` | Success rate over 5 minutes | `rate(extraction_successes_total[5m]) / rate(extraction_attempts_total[5m])` |
| `extraction:avg_time_seconds:5m` | Average extraction time over 5 minutes | `rate(extraction_time_seconds_sum[5m]) / rate(extraction_time_seconds_count[5m])` |
| `extraction:avg_tokens_per_extraction:5m` | Average tokens per extraction over 5 minutes | `rate(extraction_tokens_total[5m]) / rate(extraction_successes_total[5m])` |
| `extraction:avg_cost_per_extraction:5m` | Average cost per extraction over 5 minutes | `rate(extraction_cost_dollars_total[5m]) / rate(extraction_successes_total[5m])` |
| `extraction:avg_content_size_bytes:5m` | Average content size over 5 minutes | `rate(extraction_content_size_bytes_sum[5m]) / rate(extraction_content_size_bytes_count[5m])` |
| `extraction:quality_by_content_type:5m` | Average quality score by content type over 5 minutes | `avg by (content_type) (extraction_quality_score)` |

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ for the extraction service

### Installation

1. **Start the monitoring stack**:

   ```bash
   cd monitoring
   docker-compose up -d
   ```

2. **Verify the services are running**:

   ```bash
   docker-compose ps
   ```

3. **Access the dashboards**:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (default credentials: admin/admin)

## Integration Guide

### Basic Integration

To integrate the monitoring system with your extraction service, follow these steps:

1. **Import the metrics integration module**:

   ```python
   from cry_a_4mcp.monitoring.extraction_metrics_integration import track_extraction
   ```

2. **Use the decorator on your extraction functions**:

   ```python
   @track_extraction
   async def extract_content(content, content_type="CRYPTO"):
       # Your extraction logic here
       return result
   ```

3. **Start the metrics server**:

   ```python
   from cry_a_4mcp.monitoring.metrics_exporter import start_metrics_server
   
   # Start the server on port 8000
   start_metrics_server(port=8000)
   ```

### Advanced Integration

For more control over the metrics, you can use the `ExtractionMetricsTracker` context manager directly:

```python
from cry_a_4mcp.monitoring.extraction_metrics_integration import ExtractionMetricsTracker

async def extract_content(content, content_type="CRYPTO"):
    with ExtractionMetricsTracker(content, content_type) as tracker:
        # Your extraction logic here
        result = await perform_extraction(content)
        
        # Set the result to record metrics
        tracker.set_result(result)
        
        return result
```

### Example Implementation

A complete example implementation is available in the `examples/monitoring_demo.py` file. This script demonstrates how to use the monitoring system with a sample extraction service.

```bash
# Run the demo
python examples/monitoring_demo.py --port 8000 --duration 120
```

## Dashboards

The monitoring system includes two pre-configured Grafana dashboards:

### Extraction Metrics Dashboard

This dashboard provides an overview of the extraction service's performance, including:

- Extraction success rate
- Average extraction time
- Average token usage per extraction
- Average cost per extraction
- Average content size
- Extraction quality by content type
- Extraction failure rate
- Validation error rate
- Average extraction quality

### Schema Validation Dashboard

This dashboard focuses on schema validation metrics, including:

- Validation error rate
- Validation errors by content type
- Validation errors by error type
- Validation error rate by content type

## Alerting

The monitoring system includes pre-configured alerts for critical issues:

| Alert | Description | Threshold |
|-------|-------------|----------|
| `HighExtractionFailureRate` | High rate of extraction failures | >10% over 5m |
| `SlowExtractionTime` | Extractions taking too long | >5s avg over 5m |
| `HighTokenUsage` | Excessive token usage | >500 tokens/extraction over 5m |
| `HighEstimatedCost` | High extraction costs | >$0.01/extraction over 5m |
| `LowExtractionQuality` | Poor extraction quality | <0.7 avg over 5m |
| `HighValidationErrorRate` | High rate of validation errors | >5% over 5m |

Alerts are configured to be sent via email and webhook (for integration with services like PagerDuty or Slack).

### Configuring Alert Destinations

To configure where alerts are sent, edit the `monitoring/alertmanager/alertmanager.yml` file:

```yaml
receivers:
- name: 'team-email'
  email_configs:
  - to: 'your-team@example.com'  # Change this to your email
    send_resolved: true

- name: 'team-pager'
  webhook_configs:
  - url: 'http://your-webhook-url'  # Change this to your webhook URL
    send_resolved: true
```

## Troubleshooting

### Common Issues

#### Metrics Not Showing in Prometheus

1. Check if the metrics server is running:
   ```bash
   curl http://localhost:8000/metrics
   ```

2. Verify Prometheus configuration:
   ```bash
   curl http://localhost:9090/api/v1/status/config
   ```

3. Check Prometheus targets:
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```

#### Grafana Dashboards Not Loading

1. Check if Grafana is running:
   ```bash
   curl http://localhost:3000/api/health
   ```

2. Verify Prometheus data source in Grafana:
   - Go to Configuration > Data Sources
   - Check if Prometheus is configured correctly

#### Alerts Not Being Sent

1. Check Alertmanager status:
   ```bash
   curl http://localhost:9093/api/v1/status
   ```

2. Verify alert rules in Prometheus:
   ```bash
   curl http://localhost:9090/api/v1/rules
   ```

### Logs

To check logs for troubleshooting:

```bash
# Prometheus logs
docker-compose logs prometheus

# Grafana logs
docker-compose logs grafana

# Alertmanager logs
docker-compose logs alertmanager
```

## Extending the System

### Adding New Metrics

To add new metrics to the system, follow these steps:

1. **Update the metrics exporter**:

   Edit the `src/cry_a_4mcp/monitoring/metrics_exporter.py` file to add new metrics:

   ```python
   # Add a new counter metric
   my_new_metric = Counter(
       'my_new_metric_total',
       'Description of my new metric',
       ['label1', 'label2']
   )
   ```

2. **Update the integration module**:

   Edit the `src/cry_a_4mcp/monitoring/extraction_metrics_integration.py` file to track the new metric:

   ```python
   # Record the new metric
   my_new_metric.labels(label1='value1', label2='value2').inc()
   ```

3. **Add recording rules** (optional):

   Edit the `monitoring/prometheus/extraction_rules.yml` file to add new recording rules:

   ```yaml
   - record: extraction:my_new_metric:5m
     expr: rate(my_new_metric_total[5m])
   ```

4. **Create or update dashboards**:

   Edit the Grafana dashboard JSON files to add new panels for the new metrics.

### Adding New Alerts

To add new alerts, edit the `monitoring/prometheus/extraction_rules.yml` file:

```yaml
- alert: MyNewAlert
  expr: my_expression > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "My new alert summary"
    description: "Detailed description of the alert"
```

### Customizing Dashboards

To customize the dashboards:

1. Log in to Grafana (http://localhost:3000)
2. Navigate to the dashboard you want to customize
3. Click the gear icon in the top right to edit the dashboard
4. Make your changes and save the dashboard
5. Export the dashboard JSON and save it to the appropriate file in `monitoring/grafana/dashboards/`

## Conclusion

The monitoring system provides comprehensive visibility into the extraction service's performance and health. By tracking key metrics and setting up alerts, you can proactively identify and address issues before they impact users.

For any questions or issues, please refer to the troubleshooting section or contact the development team.