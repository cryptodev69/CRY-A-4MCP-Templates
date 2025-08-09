# CRY-A-4MCP Architecture Overview

The CRY-A-4MCP Enhanced Templates Package implements a sophisticated, modular architecture for cryptocurrency data analysis and web crawling. This document provides a comprehensive overview of the system's design, components, and data flow.

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Backend API   │    │   Data Layer    │
│                 │    │                 │    │                 │
│ • React App     │◄──►│ • FastAPI       │◄──►│ • SQLite        │
│ • TypeScript    │    │ • Python 3.8+   │    │ • Qdrant        │
│ • Tailwind CSS  │    │ • Pydantic      │    │ • Neo4j         │
│ • Vite          │    │ • Uvicorn       │    │ • Redis         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  External APIs  │
                    │                 │
                    │ • OpenAI        │
                    │ • OpenRouter    │
                    │ • Groq          │
                    │ • Anthropic     │
                    └─────────────────┘
```

## 🔧 Core Components

### 1. Frontend Layer (React + TypeScript)

#### Main Pages
- **Dashboard**: System overview and quick actions
- **Extractors**: Data extraction strategy management
- **URL Mappings**: URL-to-extractor association configuration
- **Crawlers**: Crawler configuration and management
- **Crawl Jobs**: Job execution and monitoring

#### Key Features
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Real-time Updates**: WebSocket integration for live job monitoring
- **Type Safety**: Full TypeScript implementation
- **Component Reusability**: Modular component architecture

### 2. Backend Layer (FastAPI + Python)

#### API Endpoints
- **URL Configurations**: `/api/url-configs/`
- **URL Mappings**: `/api/url-mappings/`
- **Extractors**: `/api/extractors/`
- **Crawlers**: `/api/crawlers/`
- **Crawl Jobs**: `/api/crawl-jobs/`
- **Test URL**: `/api/test-url/`

#### Core Services
- **GenericAsyncCrawler**: Asynchronous web crawling engine
- **LLM Integration**: Multi-provider LLM support
- **Data Validation**: Pydantic models for request/response validation
- **Error Handling**: Comprehensive error management

### 3. Data Layer

#### Primary Database (SQLite)
- **URL Configurations**: Business-focused URL metadata
- **URL Mappings**: Technical URL-to-extractor associations
- **Extractors**: Data extraction strategies and schemas
- **Crawlers**: Crawler configurations and settings
- **Crawl Jobs**: Job execution history and results

#### Vector Database (Qdrant)
- **Semantic Search**: Content similarity and clustering
- **Embedding Storage**: Vector representations of crawled content
- **Hybrid Search**: Combining keyword and semantic search

#### Graph Database (Neo4j)
- **Relationship Mapping**: URL and content relationships
- **Network Analysis**: Link analysis and graph traversal
- **Knowledge Graphs**: Structured knowledge representation

#### Cache Layer (Redis)
- **Session Management**: User session storage
- **Job Queues**: Background task management
- **Rate Limiting**: API rate limiting and throttling
- **Caching**: Frequently accessed data caching

## 🔄 Data Flow Architecture

### Component Relationships

```
Extractors → URL Mappings → Crawlers → Crawl Jobs
    ↓            ↓           ↓          ↓
  Schema    URL+Extractor  Execution  Real-time
  Rules     Associations   Config     Monitoring
```

### 1. Extractors - The Data Processing Engine
**Purpose**: Define HOW to extract data
- Data extraction strategies (LLM-based, CSS selectors, XPath, API)
- Processing schemas and instructions for different content types
- Reusable extraction logic applicable across multiple URLs
- Performance metrics (usage count, success rates)

### 2. URL Mappings - The Configuration Bridge
**Purpose**: Define WHICH extractor to use for WHICH URLs
- Associates specific URLs with appropriate extractors
- Defines URL-specific processing rules (rate limiting, retries, timeouts)
- Manages URL priorities and categories
- Provides advanced configuration (custom headers, validation rules)

### 3. Crawlers - The Execution Engine
**Purpose**: Combine configurations into executable units
- Combines URL mappings with extractors into executable configurations
- Defines crawler types (basic, LLM, composite) with different capabilities
- Manages execution parameters (concurrency, timeouts, retry logic)
- Tracks performance statistics (success rates, extraction times)

### 4. Crawl Jobs - The Orchestration Layer
**Purpose**: Execute and monitor crawling operations
- Executes specific crawler configurations against target URLs
- Provides real-time monitoring and progress tracking
- Manages job scheduling (one-time, recurring)
- Handles job lifecycle (pending, running, completed, failed)

## 🎯 Business Logic Flow

### URL Configuration Workflow

1. **URL Discovery**: Identify target URLs for cryptocurrency data
2. **Business Classification**: Categorize URLs by trading strategy:
   - Degen Gambler: High-risk, high-reward opportunities
   - Gem Hunter: Early-stage project discovery
   - Traditional Investor: Established market analysis
   - DeFi Yield Farmer: Yield farming opportunities
3. **Cost Analysis**: Evaluate scraping difficulty and API alternatives
4. **Priority Assignment**: Set crawling priorities based on business value

### Extraction Strategy Workflow

1. **Strategy Selection**: Choose appropriate extraction method:
   - **LLM-based**: For complex, unstructured content
   - **CSS Selectors**: For structured HTML content
   - **XPath**: For precise element targeting
   - **API Integration**: For structured data sources
2. **Schema Definition**: Define expected output structure
3. **Validation Rules**: Set data quality and validation criteria
4. **Performance Optimization**: Configure caching and rate limiting

### Crawling Execution Workflow

1. **Configuration Assembly**: Combine URL mappings with extractors
2. **Resource Allocation**: Determine concurrency and resource limits
3. **Job Scheduling**: Queue jobs based on priority and constraints
4. **Execution Monitoring**: Track progress and handle errors
5. **Data Processing**: Validate, transform, and store extracted data
6. **Performance Analysis**: Analyze success rates and optimization opportunities

## 🔌 Integration Points

### LLM Provider Integration

- **OpenAI**: GPT models for content analysis
- **OpenRouter**: Cost-effective model access
- **Groq**: High-speed inference
- **Anthropic**: Claude models for complex reasoning

### External Service Integration

- **Docker**: Containerized deployment
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **GitHub**: Version control and CI/CD

## 🛡️ Security Architecture

### Authentication & Authorization
- **API Key Management**: Secure storage and rotation
- **Rate Limiting**: Prevent abuse and ensure fair usage
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses without information leakage

### Data Protection
- **Environment Variables**: Secure configuration management
- **Database Encryption**: Encrypted data storage
- **Network Security**: HTTPS/TLS for all communications
- **Access Control**: Role-based access to sensitive operations

## 📊 Monitoring & Observability

### Metrics Collection
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Request rates, response times, error rates
- **Business Metrics**: Extraction success rates, data quality scores
- **Custom Metrics**: Domain-specific performance indicators

### Logging Strategy
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Levels**: Appropriate log levels for different environments
- **Centralized Logging**: Aggregated logs for analysis
- **Log Retention**: Configurable retention policies

### Health Monitoring
- **Health Checks**: Endpoint health monitoring
- **Service Discovery**: Automatic service registration
- **Alerting**: Proactive issue detection and notification
- **Performance Monitoring**: Real-time performance tracking

## 🚀 Scalability Considerations

### Horizontal Scaling
- **Microservices Architecture**: Independent service scaling
- **Load Balancing**: Distribute traffic across instances
- **Database Sharding**: Partition data for performance
- **Caching Strategy**: Multi-level caching for performance

### Performance Optimization
- **Asynchronous Processing**: Non-blocking operations
- **Connection Pooling**: Efficient database connections
- **Resource Management**: Optimal resource utilization
- **Batch Processing**: Efficient bulk operations

## 📚 Related Documentation

- **[Crawler System Details](./crawler-system.md)** - Deep dive into crawling architecture
- **[Data Flow Architecture](./data-flow.md)** - Detailed data flow patterns
- **[URL Mapping System](./url-mapping.md)** - URL mapping configuration
- **[Extraction Strategies](./extraction-strategies.md)** - Extraction strategy patterns

---

**Next Steps**: Explore the [Crawler System Overview](./crawler-system.md) for detailed implementation details.