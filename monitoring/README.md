# Monitoring Setup for CRY-A-4MCP

This directory contains the monitoring configuration for the CRY-A-4MCP platform, including Prometheus rules and Grafana dashboards for tracking extraction metrics and schema validation.

## Directory Structure

```
monitoring/
├── prometheus/
│   ├── prometheus.yml        # Main Prometheus configuration
│   └── extraction_rules.yml  # Alert and recording rules for extraction metrics
├── grafana/
│   └── dashboards/
│       ├── extraction_metrics_dashboard.json    # Dashboard for extraction metrics
│       └── schema_validation_dashboard.json     # Dashboard for schema validation
└── README.md                 # This file
```

## Prometheus Configuration

The Prometheus configuration is set up to scrape metrics from the extraction service, node_exporter, and Prometheus itself. It also includes alert rules for monitoring extraction performance and schema validation.

### Alert Rules

The `extraction_rules.yml` file defines the following alert rules:

- **HighExtractionFailureRate**: Alerts when the extraction failure rate exceeds 20% for 5 minutes
- **SlowExtractionTime**: Alerts when the average extraction time exceeds 10 seconds for 5 minutes
- **HighTokenUsage**: Alerts when the token usage rate exceeds 100,000 tokens per hour for 15 minutes
- **HighEstimatedCost**: Alerts when the estimated cost exceeds $50 per day for 1 hour
- **LowExtractionQuality**: Alerts when the average extraction quality score falls below 0.7 for 30 minutes
- **HighValidationErrorRate**: Alerts when the validation error rate exceeds 10% for 5 minutes

### Recording Rules

The `extraction_rules.yml` file also defines recording rules to pre-compute commonly used metrics:

- **extraction:success_rate:5m**: Extraction success rate over 5 minutes
- **extraction:avg_time_seconds:5m**: Average extraction time in seconds over 5 minutes
- **extraction:avg_tokens_per_extraction:5m**: Average token usage per extraction over 5 minutes
- **extraction:avg_cost_per_extraction:5m**: Average cost per extraction over 5 minutes
- **extraction:avg_content_size_bytes:5m**: Average content size in bytes over 5 minutes
- **extraction:quality_by_content_type:5m**: Average extraction quality by content type over 5 minutes

## Grafana Dashboards

### Extraction Metrics Dashboard

The extraction metrics dashboard provides a comprehensive view of the extraction performance, including:

- Extraction success rate
- Average extraction time
- Token usage per extraction
- Cost per extraction
- Content size
- Extraction quality by content type
- Failure rate
- Validation error rate

### Schema Validation Dashboard

The schema validation dashboard focuses on monitoring schema validation errors, including:

- Validation error rate
- Validation errors by content type
- Validation errors by error type
- Current validation error rate gauge

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Prometheus and Grafana containers running

### Prometheus Setup

1. Ensure the `prometheus.yml` file is properly configured to point to your extraction service
2. Copy the `extraction_rules.yml` file to your Prometheus configuration directory
3. Update the `prometheus.yml` file to include the `extraction_rules.yml` file in the `rule_files` section
4. Restart Prometheus to apply the changes

### Grafana Setup

1. Import the dashboard JSON files into Grafana:
   - Go to Dashboards > Import
   - Upload the JSON file or paste its contents
   - Select the Prometheus data source
   - Click Import
2. Repeat for each dashboard file

## Metrics Tracked

The monitoring setup tracks the following metrics:

### Extraction Metrics

- **extraction_attempts_total**: Total number of extraction attempts
- **extraction_successes_total**: Total number of successful extractions
- **extraction_failures_total**: Total number of failed extractions
- **extraction_time_seconds**: Time taken for extraction in seconds
- **token_usage_total**: Total token usage
- **estimated_cost_dollars_total**: Total estimated cost in dollars
- **extraction_quality_score**: Quality score of extractions
- **content_size_bytes**: Size of content in bytes

### Validation Metrics

- **validation_errors_total**: Total number of validation errors

## Troubleshooting

### Common Issues

- **No data in Grafana dashboards**: Ensure Prometheus is correctly scraping metrics from your extraction service
- **Missing metrics**: Check that the metrics are being exported by your application
- **Alert rules not working**: Verify that the `extraction_rules.yml` file is correctly loaded by Prometheus

### Logs

- Check Prometheus logs for any issues with scraping or rule evaluation
- Check Grafana logs for any issues with dashboard loading

## Extending the Monitoring

To add new metrics or dashboards:

1. Add new metrics to your application using the Prometheus client library
2. Update the `extraction_rules.yml` file to include new alert or recording rules
3. Create or modify Grafana dashboards to visualize the new metrics