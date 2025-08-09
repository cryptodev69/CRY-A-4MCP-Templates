# Development Guide

Welcome to the CRY-A-4MCP Enhanced Templates development guide. This section provides comprehensive information for developers contributing to the project, including testing frameworks, debugging procedures, coding standards, and contribution guidelines.

## 📚 Development Documentation

### 🧪 [Testing Framework](./testing.md)
- Unit testing with pytest
- Integration testing strategies
- End-to-end testing procedures
- Test coverage requirements
- Mock data and fixtures

### 🧪 [Testing Framework Guide](./testing-framework-guide.md) ⭐
- **Comprehensive testing guide for coding agents and full-stack developers**
- AI model testing patterns and agent decision testing
- Full-stack testing pyramid (unit, integration, E2E)
- Performance benchmarking and security testing
- CI/CD integration and best practices
- Complete examples and troubleshooting guide

### ⚡ [Testing Quick Reference](./testing-quick-reference.md) 📋
- **Essential commands and patterns cheat sheet**
- Quick test templates for common scenarios
- Debugging commands and troubleshooting
- Performance testing shortcuts
- Security testing patterns

### 🔄 [Testing-Based Development](./testing-based-development.md) 🎯
- **Comprehensive TDD and BDD guide for full-stack developers**
- Test-Driven Development (TDD) with Red-Green-Refactor cycle
- Behavior-Driven Development (BDD) with Gherkin scenarios
- AI-driven development and agent decision testing
- Continuous testing and CI/CD integration
- Quality gates and best practices

### 🐛 [Debugging Procedures](./debugging.md)
- Common issues and solutions
- Debug logging configuration
- Performance profiling
- Error tracking and resolution
- Development tools and utilities

### 📝 [Coding Standards](./coding-standards.md)
- Python code style (PEP 8, Black, Ruff)
- TypeScript/React conventions
- Documentation requirements
- Code review guidelines
- Quality assurance checklist

### 🤝 [Contributing Guidelines](./contributing.md)
- How to contribute to the project
- Pull request process
- Issue reporting guidelines
- Development workflow
- Community guidelines

### 🤖 [AI Agent Reference](./ai-agent-reference.md)
- AI agent development patterns
- MCP server integration
- LLM provider configuration
- Agent testing strategies
- Performance optimization

## 🚀 Quick Development Setup

### Prerequisites
- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher
- **Docker**: Latest version with Docker Compose
- **Git**: For version control

### Development Environment Setup

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd CRY-A-4MCP-Templates
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Backend Development**:
   ```bash
   cd starter-mcp-server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Frontend Development**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Start Development Services**:
   ```bash
   # Option 1: Unified development (recommended)
   npm run dev
   
   # Option 2: Docker stack
   cd docker-stack
   ./start.sh
   ```

## 🧪 Testing Overview

### Test Structure
```
tests/
├── unit/                 # Unit tests
│   ├── test_extractors.py
│   ├── test_crawlers.py
│   └── test_url_mappings.py
├── integration/          # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_crawler_integration.py
│   └── test_url_mapping_integration.py
├── e2e/                  # End-to-end tests
│   ├── test_full_workflow.py
│   └── test_ui_interactions.py
├── fixtures/             # Test data and fixtures
└── conftest.py          # Pytest configuration
```

### Running Tests

```bash
# Backend tests
cd starter-mcp-server
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Integration tests
python tests/integration/test_url_mapping_integration.py

# Coverage report
pytest --cov=src tests/
```

### Test Coverage Requirements
- **Minimum Coverage**: 80% line coverage
- **Critical Components**: 90%+ coverage required
- **New Features**: Must include comprehensive tests
- **Bug Fixes**: Must include regression tests

## 🐛 Common Development Issues

### Backend Issues

#### Port Conflicts
**Issue**: Port 4000 already in use
**Solution**:
```bash
# Find and kill process using port 4000
lsof -ti:4000 | xargs kill -9

# Or use different port
uvicorn src.main:app --host 0.0.0.0 --port 4001
```

#### API Key Issues
**Issue**: "Invalid API key" errors
**Solution**:
1. Verify API key is correct in `.env`
2. Restart backend server after updating `.env`
3. Check API key permissions and quotas

#### Database Issues
**Issue**: SQLite database locked or corrupted
**Solution**:
```bash
# Reset database
rm -f database.db
python -c "from src.database import init_db; init_db()"
```

### Frontend Issues

#### Node Modules Issues
**Issue**: Package installation or version conflicts
**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

#### TypeScript Errors
**Issue**: Type checking errors
**Solution**:
```bash
# Check types
npm run type-check

# Fix auto-fixable issues
npm run lint:fix
```

### Docker Issues

#### Container Startup Issues
**Issue**: Services won't start or crash
**Solution**:
```bash
# Reset Docker state
docker-compose down
docker system prune -f
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Memory Issues
**Issue**: Out of memory errors
**Solution**:
1. Increase Docker memory allocation to 8GB+
2. Use lightweight variant: `--variant minimal`
3. Close unnecessary applications

## 🔧 Development Tools

### Code Quality Tools

```bash
# Python code formatting
black src/ tests/
ruff check src/ tests/

# TypeScript/React formatting
npm run lint
npm run format

# Type checking
mypy src/
npm run type-check
```

### Development Utilities

```bash
# Health check script
./scripts/health_check.sh

# System monitoring
python scripts/system_monitor.py --watch

# Database management
python scripts/db_manager.py --reset
```

### Debugging Tools

```bash
# Backend debugging
python -m debugpy --listen 5678 --wait-for-client -m uvicorn src.main:app

# Frontend debugging
npm run dev:debug

# API testing
curl -X GET http://localhost:4000/health
```

## 📊 Performance Monitoring

### Metrics Collection
- **Response Times**: API endpoint performance
- **Success Rates**: Crawler and extraction success rates
- **Resource Usage**: CPU, memory, disk usage
- **Error Rates**: Application and system errors

### Monitoring Tools
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Health Checks**: Automated health monitoring
- **Log Analysis**: Structured log analysis

## 🔄 Development Workflow

### Feature Development
1. **Create Feature Branch**: `git checkout -b feature/your-feature-name`
2. **Implement Feature**: Follow coding standards and write tests
3. **Run Tests**: Ensure all tests pass
4. **Code Review**: Submit pull request for review
5. **Merge**: Merge after approval and CI passes

### Bug Fixes
1. **Reproduce Issue**: Create test case that reproduces the bug
2. **Fix Implementation**: Implement fix with minimal changes
3. **Regression Test**: Ensure fix doesn't break existing functionality
4. **Documentation**: Update documentation if needed

### Release Process
1. **Version Bump**: Update version numbers
2. **Changelog**: Update CHANGELOG.md
3. **Testing**: Run full test suite
4. **Documentation**: Update documentation
5. **Release**: Create release tag and deploy

## 🆘 Getting Help

### Documentation Resources
- **API Documentation**: http://localhost:4000/docs
- **Architecture Guide**: [../architecture/README.md](../architecture/README.md)
- **User Guides**: [../guides/README.md](../guides/README.md)

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Discord**: Real-time community support
- **Code Reviews**: Get feedback on your contributions
- **Pair Programming**: Collaborate with other developers

### Development Support
- **Debug Logs**: Check `logs/` directory for detailed information
- **Health Checks**: Run `scripts/health_check.sh` for diagnostics
- **System Monitor**: Use `scripts/system_monitor.py` for performance analysis
- **Test Suite**: Run comprehensive tests to identify issues

---

**Ready to start developing?** 👉 [Testing Framework](./testing.md)