# AI Agent Guide: Data Quality Analysis

This guide outlines a systematic approach for an AI coding agent to analyze data quality within a project. Data quality is crucial for the reliability and accuracy of any data-driven application, especially in domains like cryptocurrency analysis where decisions are often based on real-time data.

## 1. Understand the Data Landscape

Before diving into specific data quality checks, the AI agent should first understand the project's data landscape. This involves:

*   **Identifying Data Sources:** List all internal and external data sources (e.g., PostgreSQL, Redis, Neo4j, Qdrant, CoinGecko API, Binance API, Twitter API, Reddit API).
*   **Mapping Data Flows:** Understand how data moves through the system, from ingestion to processing, storage, and consumption by different services.
*   **Understanding Data Models:** Familiarize with the schema and structure of data in each database and API response.
*   **Identifying Key Data Entities:** Determine the most critical data entities for the application's core functionality (e.g., cryptocurrency prices, trading volumes, social sentiment scores).

## 2. Define Data Quality Dimensions

Data quality is multi-faceted. The AI agent should consider the following dimensions:

*   **Accuracy:** Does the data correctly reflect the real-world values? (e.g., Is the price of BTC accurate?)
*   **Completeness:** Is all necessary data present? Are there missing values in critical fields? (e.g., Are all required fields present for a cryptocurrency record?)
*   **Consistency:** Is the data consistent across different systems and over time? (e.g., Does the price of BTC match across different APIs at the same timestamp?)
*   **Timeliness:** Is the data available when needed and up-to-date? (e.g., How fresh is the market data?)
*   **Validity:** Does the data conform to defined formats, types, and ranges? (e.g., Is a price value always a positive number?)
*   **Uniqueness:** Are there duplicate records where there shouldn't be? (e.g., Are there duplicate cryptocurrency entries?)

## 3. Implement Data Quality Checks

Based on the identified data landscape and quality dimensions, the AI agent can propose and implement automated data quality checks. This might involve:

*   **Schema Validation:** Ensure incoming data conforms to expected schemas (e.g., Pydantic models for API responses).
*   **Missing Value Checks:** Identify and flag records with null or empty values in critical fields.
*   **Range and Format Validation:** Verify that numerical data falls within expected ranges and that data types are correct.
*   **Cross-System Consistency Checks:** Compare data points across different databases or APIs to ensure consistency.
*   **Duplicate Detection:** Implement logic to identify and handle duplicate records.
*   **Timeliness Monitoring:** Track the age of data and alert if it becomes stale.
*   **Referential Integrity Checks:** For relational databases, ensure foreign key relationships are maintained.

## 4. Establish Monitoring and Alerting

Data quality checks are most effective when integrated into a continuous monitoring system. The AI agent should:

*   **Integrate Checks into CI/CD:** Run data quality checks as part of the continuous integration and deployment pipeline.
*   **Set up Metrics and Dashboards:** Expose data quality metrics (e.g., percentage of complete records, number of invalid entries) via Prometheus and visualize them in Grafana.
*   **Configure Alerts:** Set up alerts for critical data quality issues (e.g., sudden drop in data completeness, high rate of invalid records).

## 5. Data Quality Remediation and Improvement

When data quality issues are detected, the AI agent should consider:

*   **Root Cause Analysis:** Investigate why the data quality issue occurred (e.g., upstream API change, bug in data ingestion script).
*   **Automated Remediation:** Where possible, implement automated processes to correct common data quality issues.
*   **Reporting and Documentation:** Document identified issues, their root causes, and the steps taken for remediation.
*   **Continuous Improvement:** Regularly review data quality metrics and refine checks as the data landscape evolves.

By following these steps, an AI coding agent can significantly contribute to maintaining high data quality within the project, leading to more reliable and trustworthy insights.