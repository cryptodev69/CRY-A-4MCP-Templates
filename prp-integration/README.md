# PRP Integration for CRY-A-4MCP Templates

This directory contains enhanced Product Requirements Prompt (PRP) templates that integrate with the executable CRY-A-4MCP project templates. These PRPs provide structured guidance for coding agents to build cryptocurrency analysis features using the provided scaffolding.

## Overview

The PRP system bridges the gap between high-level requirements and executable code by providing:

1. **Template-Aware PRPs**: Requirements that reference specific template components
2. **Automated Scaffolding**: PRPs that can generate project structure automatically
3. **Integration Guidance**: Step-by-step instructions for connecting components
4. **Testing Frameworks**: Built-in testing approaches for each feature type

## PRP Categories

### 1. Core Infrastructure PRPs (`core/`)
- **MCP Server Setup**: Initialize and configure the MCP server
- **Database Integration**: Connect Qdrant, Neo4j, and Redis
- **Crawl4AI Configuration**: Set up web crawling capabilities
- **Monitoring Setup**: Configure Prometheus and Grafana

### 2. Feature Development PRPs (`features/`)
- **Hybrid Search Implementation**: Build RAG + Knowledge Graph search
- **Real-time Data Processing**: Implement cryptocurrency data pipelines
- **Entity Extraction**: Create domain-specific entity recognition
- **Market Analysis Tools**: Build technical and fundamental analysis

### 3. Integration PRPs (`integrations/`)
- **Exchange API Integration**: Connect to cryptocurrency exchanges
- **Social Media Monitoring**: Implement Twitter/Discord/Telegram monitoring
- **News Feed Processing**: Build news aggregation and analysis
- **Workflow Automation**: Create n8n workflow templates

### 4. Testing and Validation PRPs (`testing/`)
- **Unit Testing Setup**: Implement comprehensive unit tests
- **Integration Testing**: Test component interactions
- **Performance Testing**: Validate system performance
- **Security Testing**: Ensure security best practices

## Using Template-Aware PRPs

### Quick Start

1. **Choose a PRP**: Select from available templates based on your requirements
2. **Run Scaffolding**: Use the PRP to generate initial project structure
3. **Follow Implementation**: Step through the guided implementation process
4. **Validate Results**: Use built-in testing to verify functionality

### Example Usage

```bash
# Generate a new feature using PRP
./prp-generate.sh features/hybrid-search-implementation.md

# This will:
# 1. Create the necessary directory structure
# 2. Generate boilerplate code from templates
# 3. Set up testing framework
# 4. Provide implementation guidance
```

## PRP Structure

Each PRP follows a standardized structure:

```markdown
# Feature Name

## Context
- Background information
- Integration points with existing templates
- Dependencies and prerequisites

## Requirements
- Functional requirements
- Non-functional requirements
- Integration requirements

## Implementation Plan
- Step-by-step implementation guide
- Code generation instructions
- Testing approach

## Validation Criteria
- Acceptance criteria
- Performance benchmarks
- Integration tests

## Template Integration
- Which template components to use
- How to extend existing code
- Configuration requirements
```

## Automated Code Generation

PRPs include automated code generation capabilities:

### Template Variables
- `{{PROJECT_NAME}}`: Name of the project
- `{{FEATURE_NAME}}`: Name of the feature being implemented
- `{{NETWORK}}`: Target blockchain network
- `{{API_ENDPOINTS}}`: Required API endpoints

### Code Templates
- **Python Classes**: Generate service classes with proper structure
- **Configuration Files**: Create environment-specific configs
- **Test Files**: Generate comprehensive test suites
- **Documentation**: Create API documentation and usage guides

### Integration Points
- **MCP Tools**: Automatically register new tools with the MCP server
- **Database Schemas**: Generate Qdrant collections and Neo4j schemas
- **API Routes**: Create FastAPI routes with proper validation
- **Monitoring**: Add Prometheus metrics and Grafana dashboards

## Best Practices

### PRP Development
1. **Start with Templates**: Always reference existing template components
2. **Include Testing**: Every PRP should include testing guidance
3. **Document Integration**: Clearly explain how components connect
4. **Provide Examples**: Include working code examples

### Implementation Process
1. **Read Completely**: Review the entire PRP before starting
2. **Check Dependencies**: Ensure all prerequisites are met
3. **Follow Order**: Implement steps in the specified sequence
4. **Test Incrementally**: Validate each step before proceeding

### Quality Assurance
1. **Code Review**: All generated code should be reviewed
2. **Integration Testing**: Test component interactions thoroughly
3. **Performance Validation**: Ensure performance requirements are met
4. **Documentation Updates**: Keep documentation current with implementation

## Advanced Features

### Dynamic PRP Generation
- **Requirement Analysis**: Analyze natural language requirements
- **Template Selection**: Automatically choose appropriate templates
- **Code Generation**: Generate implementation code from requirements
- **Validation Planning**: Create comprehensive test plans

### Integration with CI/CD
- **Automated Testing**: Run tests on every PRP implementation
- **Code Quality Checks**: Validate code quality and standards
- **Deployment Automation**: Automatically deploy validated features
- **Monitoring Integration**: Set up monitoring for new features

### Collaborative Development
- **Team Coordination**: Coordinate multiple developers using PRPs
- **Progress Tracking**: Track implementation progress across features
- **Knowledge Sharing**: Share implementation patterns and best practices
- **Code Reuse**: Identify and promote reusable components

## Troubleshooting

### Common Issues
1. **Template Conflicts**: Resolve conflicts between template versions
2. **Dependency Issues**: Handle missing or incompatible dependencies
3. **Integration Failures**: Debug component integration problems
4. **Performance Issues**: Optimize generated code for performance

### Support Resources
- **Documentation**: Comprehensive guides and API references
- **Examples**: Working examples for common use cases
- **Community**: Developer community for questions and support
- **Issue Tracking**: Bug reports and feature requests

