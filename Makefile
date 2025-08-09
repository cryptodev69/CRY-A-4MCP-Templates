# CRY-A-4MCP Templates - Development Makefile
# Usage: make <target>

.PHONY: help install install-dev install-ci test test-unit test-integration test-e2e
.PHONY: test-performance test-security test-all test-fast test-slow test-parallel
.PHONY: test-verbose test-debug test-watch test-smoke test-regression test-critical
.PHONY: coverage coverage-open coverage-json coverage-xml
.PHONY: lint format security audit clean build docker-build docker-run docker-stop
.PHONY: format-check mypy ruff ruff-fix black black-check isort isort-check
.PHONY: security-scan benchmark profile load-test deps-check deps-update
.PHONY: setup dev start stop restart logs health check-deps pre-commit-install
.PHONY: reports reports-open ci-setup ci-test ci-lint ci-security ci-coverage
.PHONY: release deploy-staging deploy-prod backup restore clean-all status info

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
	python run_tests.py --install-deps

install-ci: ## Install CI dependencies
	cd starter-mcp-server && pip install -e ".[ci,test]"
	python run_tests.py --install-deps

deps-check: ## Check for dependency vulnerabilities
	pip-audit
	safety check

deps-update: ## Update all dependencies
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt || echo "No requirements.txt found"
	cd starter-mcp-server && pip install --upgrade -e ".[dev,test]"

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

# Enhanced Testing Commands
test: ## Run all tests with coverage
	python run_tests.py --suite all --verbose

test-unit: ## Run unit tests only
	python run_tests.py --suite unit --verbose

test-integration: ## Run integration tests only
	python run_tests.py --suite integration --verbose

test-e2e: ## Run end-to-end tests only
	python run_tests.py --suite e2e --verbose

test-performance: ## Run performance tests only
	python run_tests.py --suite performance --verbose

test-security: ## Run security tests only
	python run_tests.py --suite security --verbose

test-all: ## Run all test suites sequentially
	python run_tests.py --suite all --verbose

test-parallel: ## Run tests in parallel
	python run_tests.py --suite all --parallel --verbose

test-fast: ## Run only fast tests
	pytest -m "fast" --verbose

test-slow: ## Run only slow tests
	pytest -m "slow" --verbose

test-smoke: ## Run smoke tests
	pytest -m "smoke" --verbose

test-regression: ## Run regression tests
	pytest -m "regression" --verbose

test-critical: ## Run critical functionality tests
	pytest -m "critical" --verbose

test-verbose: ## Run tests with maximum verbosity
	python run_tests.py --suite all --verbose

test-debug: ## Run tests with debugging enabled
	pytest --pdb --pdbcls=IPython.terminal.debugger:Pdb -s --verbose

test-watch: ## Run tests in watch mode (requires pytest-watch)
	ptw --runner "python run_tests.py --suite unit"

# Coverage Commands
coverage: ## Generate coverage report
	python run_tests.py --suite all
	coverage report --show-missing
	coverage html
	@echo "Coverage report generated in coverage/html/index.html"

coverage-open: coverage ## Open coverage report in browser
	open coverage/html/index.html

coverage-json: ## Generate JSON coverage report
	coverage json
	@echo "JSON coverage report generated in coverage.json"

coverage-xml: ## Generate XML coverage report
	coverage xml
	@echo "XML coverage report generated in coverage.xml"

# Enhanced Code Quality Commands
lint: ## Run all linting checks
	python run_tests.py --lint

format: ## Format code with black and isort
	black src tests || echo "No src/tests directories found"
	isort src tests || echo "No src/tests directories found"
	ruff check --fix src tests || echo "No src/tests directories found"

format-check: ## Check code formatting without making changes
	black --check --diff src tests || echo "No src/tests directories found"
	isort --check-only --diff src tests || echo "No src/tests directories found"
	ruff check src tests || echo "No src/tests directories found"

mypy: ## Run type checking
	mypy src --ignore-missing-imports || echo "No src directory found"

ruff: ## Run ruff linter
	ruff check src tests || echo "No src/tests directories found"

ruff-fix: ## Run ruff with auto-fix
	ruff check --fix src tests || echo "No src/tests directories found"

black: ## Run black formatter
	black src tests || echo "No src/tests directories found"

black-check: ## Check black formatting
	black --check --diff src tests || echo "No src/tests directories found"

isort: ## Run import sorting
	isort src tests || echo "No src/tests directories found"

isort-check: ## Check import sorting
	isort --check-only --diff src tests || echo "No src/tests directories found"

# Security Commands
security: ## Run security vulnerability scans
	bandit -r src/ || echo "No src directory found"
	safety check
	pip-audit

security-scan: security ## Alias for security

# Performance Commands
benchmark: ## Run performance benchmarks
	pytest tests/performance/ --benchmark-only --benchmark-sort=mean || echo "No performance tests found"

profile: ## Run performance profiling
	pytest tests/performance/ --profile --profile-svg || echo "No performance tests found"

load-test: ## Run load tests
	pytest tests/performance/test_load_testing.py -v || echo "No load tests found"

# Reporting Commands
reports: ## Generate all test reports
	python run_tests.py --suite all
	@echo "Test reports generated in test_reports/"
	@echo "Coverage reports generated in coverage/"

reports-open: reports ## Open test reports in browser
	open test_reports/all_tests.html || echo "No test reports found"
	open coverage/html/index.html || echo "No coverage reports found"

# CI/CD Commands
ci-setup: ## Setup CI environment
	pip install --upgrade pip
	make install-ci

ci-test: ## Run tests in CI environment
	python run_tests.py --suite all --parallel

ci-lint: ## Run linting in CI environment
	python run_tests.py --lint

ci-security: ## Run security checks in CI environment
	bandit -r src/ -f json -o security-report.json || echo "No src directory found"
	safety check --json --output safety-report.json || echo "Safety check failed"
	pip-audit --format=json --output=audit-report.json || echo "Pip audit failed"

ci-coverage: ## Generate coverage for CI
	python run_tests.py --suite all
	coverage xml
	coverage json

ci-all: ci-setup ci-lint ci-security ci-test ci-coverage ## Run complete CI pipeline

# Utility Commands
clean: ## Clean up generated files
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage/
	rm -rf test_reports/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

clean-all: clean ## Clean everything including dependencies
	rm -rf venv/
	rm -rf .venv/
	rm -rf node_modules/

status: ## Show project status
	@echo "Project Status:"
	@echo "=============="
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version)"
	@echo "Test files: $$(find . -name 'test_*.py' -o -name '*_test.py' 2>/dev/null | wc -l)"
	@echo "Source files: $$(find . -name '*.py' -not -path './.*' -not -path './venv/*' -not -path './.venv/*' 2>/dev/null | wc -l)"
	@echo "Last test run: $$(ls -la test_reports/ 2>/dev/null | head -2 | tail -1 || echo 'No reports found')"

info: ## Show detailed project information
	@echo "CRY-A-4MCP Testing Framework Information"
	@echo "======================================"
	@echo "Test suites available:"
	@echo "  - unit: Unit tests"
	@echo "  - integration: Integration tests"
	@echo "  - e2e: End-to-end tests"
	@echo "  - performance: Performance tests"
	@echo "  - security: Security tests"
	@echo ""
	@echo "Test markers available:"
	@echo "  - fast/slow: Test execution speed"
	@echo "  - smoke: Smoke tests"
	@echo "  - regression: Regression tests"
	@echo "  - critical: Critical functionality"
	@echo ""
	@echo "Reports generated in:"
	@echo "  - test_reports/: Test execution reports"
	@echo "  - coverage/: Coverage reports"
	@echo ""
	@echo "For more information, run: make help"

check: lint test ## Run all checks (lint + test)

quick-check: format-check test-fast ## Quick development check

full-check: clean deps-check lint test security ## Comprehensive check
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