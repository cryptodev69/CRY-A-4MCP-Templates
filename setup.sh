#!/bin/bash

# CRY-A-4MCP Templates Setup Script
# Quick setup for the entire template package

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║           CRY-A-4MCP Executable Project Templates            ║"
    echo "║                                                              ║"
    echo "║    🚀 Ready-to-run cryptocurrency analysis scaffolding      ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    # Check available memory
    available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$available_memory" -lt 6144 ]; then
        log_warning "Available memory is ${available_memory}MB. Recommended: 8GB+"
        log_warning "The system may run slowly or fail to start all services."
    fi
    
    # Check available disk space
    available_space=$(df . | awk 'NR==2{printf "%.0f", $4/1024/1024}')
    if [ "$available_space" -lt 15 ]; then
        log_warning "Available disk space is ${available_space}GB. Recommended: 20GB+"
        log_warning "You may run out of space during setup."
    fi
    
    log_success "Requirements check completed"
}

setup_environment() {
    log_info "Setting up project environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f docker-stack/.env ]; then
        log_info "Creating environment configuration..."
        cp docker-stack/.env.example docker-stack/.env
        log_success "Created docker-stack/.env from template"
        log_warning "Please review and customize docker-stack/.env before production use"
    else
        log_info "Environment file already exists: docker-stack/.env"
    fi
    
    # Make scripts executable
    chmod +x docker-stack/start.sh
    chmod +x setup.sh
    
    log_success "Environment setup completed"
}

show_next_steps() {
    echo ""
    log_success "🎉 CRY-A-4MCP Templates setup completed!"
    echo ""
    log_info "Next steps:"
    echo ""
    echo "1. 🔧 Customize configuration (optional):"
    echo "   nano docker-stack/.env"
    echo ""
    echo "2. 🚀 Start the entire stack:"
    echo "   cd docker-stack && ./start.sh start"
    echo ""
    echo "3. 🌐 Access the services:"
    echo "   • Qdrant (Vector DB):     http://localhost:6333"
    echo "   • Neo4j (Knowledge Graph): http://localhost:7474"
    echo "   • MCP Server:             http://localhost:8000"
    echo "   • Grafana (Monitoring):   http://localhost:3000"
    echo ""
    echo "4. 📚 Follow development guides:"
    echo "   • Read: README.md"
    echo "   • Explore: prp-integration/features/"
    echo "   • Implement: Follow PRP templates"
    echo ""
    echo "5. 🧪 Run tests:"
    echo "   cd starter-mcp-server && pytest tests/"
    echo ""
    log_info "Default credentials:"
    echo "   • Neo4j:  neo4j / cry-a-4mcp-password"
    echo "   • Grafana: admin / cry-a-4mcp-admin"
    echo ""
    log_warning "⚠️  Change default passwords for production use!"
    echo ""
}

show_project_structure() {
    log_info "Project structure:"
    echo ""
    echo "CRY-A-4MCP-Templates/"
    echo "├── 📁 starter-mcp-server/     # Complete MCP server template"
    echo "│   ├── src/cry_a_4mcp/        # Source code"
    echo "│   ├── tests/                 # Test suites"
    echo "│   ├── Dockerfile             # Container configuration"
    echo "│   └── pyproject.toml         # Python dependencies"
    echo "├── 📁 docker-stack/           # One-command infrastructure"
    echo "│   ├── docker-compose.yml     # Service definitions"
    echo "│   ├── start.sh              # Management script"
    echo "│   └── config/               # Service configurations"
    echo "├── 📁 sample-data/           # Realistic test data"
    echo "│   ├── market_data/          # Price and volume data"
    echo "│   ├── news_articles/        # Cryptocurrency news"
    echo "│   └── entities/             # Tokens, exchanges, protocols"
    echo "├── 📁 prp-integration/       # Development guides"
    echo "│   ├── features/             # Feature implementation PRPs"
    echo "│   ├── core/                 # Infrastructure PRPs"
    echo "│   └── testing/              # Testing PRPs"
    echo "└── 📄 README.md              # Main documentation"
    echo ""
}

# Main execution
main() {
    show_banner
    
    case "${1:-setup}" in
        setup)
            check_requirements
            setup_environment
            show_project_structure
            show_next_steps
            ;;
        wizard)
            log_info "Starting interactive setup wizard..."
            python3 setup_wizard.py
            ;;
        check)
            check_requirements
            ;;
        structure)
            show_project_structure
            ;;
        health)
            log_info "Running health check..."
            ./scripts/health_check.sh
            ;;
        help|--help|-h)
            echo "CRY-A-4MCP Templates Setup Script"
            echo ""
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  setup      Basic setup (default)"
            echo "  wizard     Interactive setup wizard (recommended)"
            echo "  check      Check system requirements only"
            echo "  health     Run health check on services"
            echo "  structure  Show project structure"
            echo "  help       Show this help message"
            echo ""
            echo "For first-time setup, use: $0 wizard"
            echo ""
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

