#!/bin/bash

# CRY-A-4MCP Docker Stack Startup Script
# This script provides easy management of the entire CRY-A-4MCP stack

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

check_requirements() {
    log_info "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Requirements check passed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_warning "Please review and customize the .env file before running in production"
    fi
    
    # Create necessary directories
    mkdir -p config/{qdrant,neo4j,n8n,redis,prometheus,grafana,server}
    mkdir -p data/{qdrant,neo4j,n8n,redis,server}
    mkdir -p logs
    mkdir -p workflows
    mkdir -p backups
    
    log_success "Environment setup completed"
}

create_configs() {
    log_info "Creating default configuration files..."
    
    # Redis configuration
    if [ ! -f config/redis/redis.conf ]; then
        cat > config/redis/redis.conf << EOF
# Redis configuration for CRY-A-4MCP
bind 0.0.0.0
port 6379
timeout 0
tcp-keepalive 300
daemonize no
supervised no
pidfile /var/run/redis_6379.pid
loglevel notice
logfile ""
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF
    fi
    
    # Prometheus configuration
    if [ ! -f config/prometheus/prometheus.yml ]; then
        cat > config/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'cry-a-4mcp-server'
    static_configs:
      - targets: ['cry-a-4mcp-server:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'qdrant'
    static_configs:
      - targets: ['qdrant:6333']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'neo4j'
    static_configs:
      - targets: ['neo4j:2004']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF
    fi
    
    log_success "Configuration files created"
}

start_stack() {
    log_info "Starting CRY-A-4MCP stack..."
    
    # Pull latest images
    log_info "Pulling latest Docker images..."
    docker-compose pull
    
    # Build custom images
    log_info "Building custom images..."
    docker-compose build
    
    # Start services
    log_info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_services
    
    log_success "CRY-A-4MCP stack started successfully!"
    show_urls
}

stop_stack() {
    log_info "Stopping CRY-A-4MCP stack..."
    docker-compose down
    log_success "Stack stopped"
}

restart_stack() {
    log_info "Restarting CRY-A-4MCP stack..."
    docker-compose restart
    log_success "Stack restarted"
}

check_services() {
    log_info "Checking service health..."
    
    services=("qdrant:6333" "neo4j:7474" "n8n:5678" "redis:6379" "cry-a-4mcp-server:8000" "prometheus:9090" "grafana:3000")
    
    for service in "${services[@]}"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if docker-compose ps | grep -q "$name.*Up"; then
            log_success "$name is running"
        else
            log_error "$name is not running"
        fi
    done
}

show_urls() {
    echo ""
    log_info "Service URLs:"
    echo "  🔍 Qdrant (Vector DB):     http://localhost:6333"
    echo "  🕸️  Neo4j (Knowledge Graph): http://localhost:7474"
    echo "  🔄 n8n (Workflows):        http://localhost:5678"
    echo "  🚀 CRY-A-4MCP Server:      http://localhost:8000"
    echo "  📊 Prometheus (Metrics):   http://localhost:9090"
    echo "  📈 Grafana (Dashboards):   http://localhost:3000"
    echo ""
    log_info "Default credentials:"
    echo "  Neo4j:  neo4j / cry-a-4mcp-password"
    echo "  n8n:    admin / cry-a-4mcp-admin"
    echo "  Grafana: admin / cry-a-4mcp-admin"
    echo ""
}

show_logs() {
    if [ -z "$2" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$2"
    fi
}

show_status() {
    docker-compose ps
}

cleanup() {
    log_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

backup() {
    log_info "Creating backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backups/backup_$timestamp"
    mkdir -p "$backup_dir"
    
    # Backup Neo4j data
    docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/tmp/neo4j_backup.dump
    docker cp cry-a-4mcp-neo4j:/tmp/neo4j_backup.dump "$backup_dir/"
    
    # Backup Qdrant data
    docker-compose exec qdrant tar -czf /tmp/qdrant_backup.tar.gz /qdrant/storage
    docker cp cry-a-4mcp-qdrant:/tmp/qdrant_backup.tar.gz "$backup_dir/"
    
    # Backup n8n data
    docker-compose exec n8n tar -czf /tmp/n8n_backup.tar.gz /home/node/.n8n
    docker cp cry-a-4mcp-n8n:/tmp/n8n_backup.tar.gz "$backup_dir/"
    
    log_success "Backup created in $backup_dir"
}

show_help() {
    echo "CRY-A-4MCP Docker Stack Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the entire stack"
    echo "  stop      Stop the entire stack"
    echo "  restart   Restart the entire stack"
    echo "  status    Show service status"
    echo "  logs      Show logs (optionally for specific service)"
    echo "  backup    Create a backup of all data"
    echo "  cleanup   Remove all containers, networks, and volumes"
    echo "  urls      Show service URLs and credentials"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                 # Start all services"
    echo "  $0 logs                  # Show all logs"
    echo "  $0 logs neo4j           # Show Neo4j logs only"
    echo "  $0 status               # Show service status"
    echo ""
}

# Main script logic
case "${1:-help}" in
    start)
        check_requirements
        setup_environment
        create_configs
        start_stack
        ;;
    stop)
        stop_stack
        ;;
    restart)
        restart_stack
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$@"
        ;;
    backup)
        backup
        ;;
    cleanup)
        cleanup
        ;;
    urls)
        show_urls
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

