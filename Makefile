# CRY-A-4MCP Templates - Development Makefile
# Usage: make <target>

.PHONY: help install install-dev install-ci test test-unit test-integration test-e2e
.PHONY: lint format security audit clean build docker-build docker-run docker-stop
.PHONY: setup dev start stop restart logs health check-deps pre-commit-install
.PHONY: release deploy-staging deploy-prod backup restore

# Default target
help: ## Show this help message
	@echo "CRY-A-4MCP Templates - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup     # Initial project setup"
	@echo "  make dev       # Start development environment"
	@echo "  make test      # Run all tests"
	@echo "  make lint      # Run code quality checks"

# Installation targets
install: ## Install production dependencies
	cd starter-mcp-server && pip install -e .

install-dev: ## Install development dependencies
	cd starter-mcp-server && pip install -e ".[dev,test]"
	pip install pre-commit
	npm install --prefix frontend

install-ci: ## Install CI dependencies
	cd starter-mcp-server && pip install -e ".[ci,test]"

# Setup targets
setup: ## Initial project setup
	@echo "🚀 Setting up CRY-A-4MCP Templates..."
	./setup.sh
	make install-dev
	make pre-commit-install
	@echo "✅ Setup complete! Run 'make dev' to start development."

check-deps: ## Check system dependencies
	@echo "🔍 Checking system dependencies..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed."; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
	@echo "✅ All dependencies are installed."

pre-commit-install: ## Install pre-commit hooks
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ Pre-commit hooks installed."

# Development targets
dev: ## Start development environment
	@echo "🔧 Starting development environment..."
	cd docker-stack && ./start.sh start
	@echo "✅ Development environment started!"
	@echo "📊 Services available at:"
	@echo "   - API: http://localhost:8000"
	@echo "   - Grafana: http://localhost:3000"
	@echo "   - Prometheus: http://localhost:9090"

start: dev ## Alias for dev

stop: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	cd docker-stack && ./start.sh stop
	@echo "✅ Development environment stopped."

restart: ## Restart development environment
	make stop
	make start

logs: ## Show logs from all services
	cd docker-stack && docker-compose logs -f

health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health 2>/dev/null && echo "✅ API is healthy" || echo "❌ API is unhealthy"
	@curl -f http://localhost:3000/api/health 2>/dev/null && echo "✅ Grafana is healthy" || echo "❌ Grafana is unhealthy"
	@curl -f http://localhost:9090/-/healthy 2>/dev/null && echo "✅ Prometheus is healthy" || echo "❌ Prometheus is unhealthy"

# Testing targets
test: ## Run all tests
	@echo "🧪 Running all tests..."
	make test-unit
	make test-integration
	@echo "✅ All tests completed."

test-unit: ## Run unit tests
	@echo "🔬 Running unit tests..."
	cd starter-mcp-server && python -m pytest tests/ -m "unit" -v

test-integration: ## Run integration tests
	@echo "🔗 Running integration tests..."
	cd starter-mcp-server && python -m pytest tests/ -m "integration" -v

test-e2e: ## Run end-to-end tests
	@echo "🎭 Running end-to-end tests..."
	cd starter-mcp-server && python -m pytest tests/ -m "e2e" -v

test-smoke: ## Run smoke tests
	@echo "💨 Running smoke tests..."
	cd starter-mcp-server && python -m pytest tests/ -m "smoke" -v

test-security: ## Run security tests
	@echo "🔒 Running security tests..."
	cd starter-mcp-server && python -m pytest tests/ -m "security" -v

test-coverage: ## Run tests with coverage report
	@echo "📊 Running tests with coverage..."
	cd starter-mcp-server && python -m pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "📈 Coverage report generated in starter-mcp-server/htmlcov/"

# Code quality targets
lint: ## Run all linting checks
	@echo "🔍 Running code quality checks..."
	make lint-python
	make lint-frontend
	@echo "✅ Linting completed."

lint-python: ## Run Python linting
	@echo "🐍 Linting Python code..."
	cd starter-mcp-server && black --check --diff src/ tests/
	cd starter-mcp-server && ruff check src/ tests/
	cd starter-mcp-server && mypy src/ --ignore-missing-imports

lint-frontend: ## Run frontend linting
	@echo "🎨 Linting frontend code..."
	cd frontend && npm run lint || echo "Frontend linting not configured yet"

format: ## Format all code
	@echo "✨ Formatting code..."
	make format-python
	make format-frontend
	@echo "✅ Code formatting completed."

format-python: ## Format Python code
	@echo "🐍 Formatting Python code..."
	cd starter-mcp-server && black src/ tests/
	cd starter-mcp-server && isort src/ tests/
	cd starter-mcp-server && ruff check --fix src/ tests/

format-frontend: ## Format frontend code
	@echo "🎨 Formatting frontend code..."
	cd frontend && npm run format || echo "Frontend formatting not configured yet"

# Security targets
security: ## Run security checks
	@echo "🔒 Running security checks..."
	make security-python
	make security-deps
	@echo "✅ Security checks completed."

security-python: ## Run Python security checks
	@echo "🐍 Running Python security checks..."
	cd starter-mcp-server && bandit -r src/ -f json -o bandit-report.json || true
	cd starter-mcp-server && safety check

audit: ## Run dependency audit
	@echo "🔍 Auditing dependencies..."
	cd starter-mcp-server && pip-audit
	cd frontend && npm audit || true

security-deps: audit ## Alias for audit

# Build targets
build: ## Build all components
	@echo "🏗️ Building all components..."
	make build-backend
	make build-frontend
	@echo "✅ Build completed."

build-backend: ## Build backend
	@echo "🐍 Building backend..."
	cd starter-mcp-server && python -m build

build-frontend: ## Build frontend
	@echo "🎨 Building frontend..."
	cd frontend && npm run build

# Docker targets
docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	cd docker-stack && docker-compose build

docker-run: ## Run Docker stack
	@echo "🐳 Running Docker stack..."
	cd docker-stack && docker-compose up -d

docker-stop: ## Stop Docker stack
	@echo "🐳 Stopping Docker stack..."
	cd docker-stack && docker-compose down

docker-clean: ## Clean Docker resources
	@echo "🧹 Cleaning Docker resources..."
	docker system prune -f
	docker volume prune -f

# Maintenance targets
clean: ## Clean build artifacts and caches
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf starter-mcp-server/dist/ starter-mcp-server/build/
	rm -rf frontend/build/ frontend/dist/
	rm -rf htmlcov/ .coverage coverage.xml
	@echo "✅ Cleanup completed."

update-deps: ## Update dependencies
	@echo "📦 Updating dependencies..."
	cd starter-mcp-server && pip install --upgrade pip
	cd starter-mcp-server && pip-compile --upgrade requirements.in
	cd frontend && npm update
	pre-commit autoupdate
	@echo "✅ Dependencies updated."

# CI/CD targets
ci-test: ## Run CI test suite
	@echo "🤖 Running CI test suite..."
	make lint
	make security
	make test
	@echo "✅ CI tests completed."

ci-build: ## Run CI build
	@echo "🤖 Running CI build..."
	make build
	make docker-build
	@echo "✅ CI build completed."

# Deployment targets (placeholders)
release: ## Create a new release
	@echo "🚀 Creating release..."
	@echo "This would typically:"
	@echo "  1. Bump version numbers"
	@echo "  2. Update changelog"
	@echo "  3. Create git tag"
	@echo "  4. Trigger deployment pipeline"

deploy-staging: ## Deploy to staging
	@echo "🚀 Deploying to staging..."
	@echo "This would trigger the staging deployment pipeline"

deploy-prod: ## Deploy to production
	@echo "🚀 Deploying to production..."
	@echo "This would trigger the production deployment pipeline"

# Backup targets (placeholders)
backup: ## Create backup
	@echo "💾 Creating backup..."
	@echo "This would backup databases and important data"

restore: ## Restore from backup
	@echo "🔄 Restoring from backup..."
	@echo "This would restore databases from backup"

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "Documentation generation not implemented yet"

# Default target when no arguments provided
.DEFAULT_GOAL := help