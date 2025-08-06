#!/bin/bash

# CRY-A-4MCP Health Check Script
# Validates all services are running correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
QDRANT_URL="http://localhost:6333"
NEO4J_URL="http://localhost:7474"
N8N_URL="http://localhost:5678"
GRAFANA_URL="http://localhost:3000"
PROMETHEUS_URL="http://localhost:9090"
MCP_SERVER_URL="http://localhost:8000"

# Health check functions
check_service_basic() {
    local service=$1
    local url=$2
    local timeout=${3:-10}
    
    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

check_qdrant() {
    echo -n "Checking Qdrant vector database... "
    
    # Basic connectivity
    if ! check_service_basic "qdrant" "$QDRANT_URL"; then
        echo -e "${RED}FAILED${NC} - Service not responding"
        return 1
    fi
    
    # Check collections endpoint
    if ! curl -s "$QDRANT_URL/collections" | grep -q "crypto_embeddings" 2>/dev/null; then
        echo -e "${YELLOW}WARNING${NC} - Collections not found or not loaded"
        return 2
    fi
    
    echo -e "${GREEN}OK${NC}"
    return 0
}

check_neo4j() {
    echo -n "Checking Neo4j knowledge graph... "
    
    # Basic connectivity
    if ! check_service_basic "neo4j" "$NEO4J_URL"; then
        echo -e "${RED}FAILED${NC} - Service not responding"
        return 1
    fi
    
    echo -e "${GREEN}OK${NC} - Service responding"
    return 0
}

check_n8n() {
    echo -n "Checking n8n workflow automation... "
    
    if check_service_basic "n8n" "$N8N_URL"; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC} - Service not responding"
        return 1
    fi
}

check_grafana() {
    echo -n "Checking Grafana monitoring... "
    
    if check_service_basic "grafana" "$GRAFANA_URL"; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC} - Service not responding"
        return 1
    fi
}

check_prometheus() {
    echo -n "Checking Prometheus metrics... "
    
    # Basic connectivity
    if ! check_service_basic "prometheus" "$PROMETHEUS_URL"; then
        echo -e "${RED}FAILED${NC} - Service not responding"
        return 1
    fi
    
    # Check targets endpoint
    if curl -s "$PROMETHEUS_URL/api/v1/targets" | grep -q "\"health\":\"up\"" 2>/dev/null; then
        echo -e "${GREEN}OK${NC} - Targets healthy"
        return 0
    else
        echo -e "${YELLOW}WARNING${NC} - Some targets may be down"
        return 2
    fi
}

check_mcp_server() {
    echo -n "Checking MCP Server API... "
    
    # Check health endpoint
    if curl -s "$MCP_SERVER_URL/health" | grep -q "ok\|healthy" 2>/dev/null; then
        echo -e "${GREEN}OK${NC}"
        return 0
    elif check_service_basic "mcp-server" "$MCP_SERVER_URL"; then
        echo -e "${YELLOW}WARNING${NC} - Service responding but health check unclear"
        return 2
    else
        echo -e "${RED}FAILED${NC} - Service not responding"
        return 1
    fi
}

# Main health check function
run_health_check() {
    local service=$1
    local exit_code=0
    
    echo -e "${BLUE}CRY-A-4MCP Health Check${NC}"
    echo "=========================="
    
    if [ -n "$service" ]; then
        # Check specific service
        case $service in
            "qdrant") check_qdrant || exit_code=$? ;;
            "neo4j") check_neo4j || exit_code=$? ;;
            "n8n") check_n8n || exit_code=$? ;;
            "grafana") check_grafana || exit_code=$? ;;
            "prometheus") check_prometheus || exit_code=$? ;;
            "mcp-server") check_mcp_server || exit_code=$? ;;
            *)
                echo -e "${RED}Unknown service: $service${NC}"
                exit_code=1
                ;;
        esac
    else
        # Check all services
        check_qdrant || exit_code=$?
        check_neo4j || exit_code=$?
        check_n8n || exit_code=$?
        check_grafana || exit_code=$?
        check_prometheus || exit_code=$?
        check_mcp_server || exit_code=$?
    fi
    
    echo "=========================="
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}All checks passed!${NC}"
        echo "Your CRY-A-4MCP system is ready for use."
    elif [ $exit_code -eq 2 ]; then
        echo -e "${YELLOW}Some warnings detected.${NC}"
        echo "System is functional but may need attention."
    else
        echo -e "${RED}Health check failed!${NC}"
        echo "Please check the services and try again."
    fi
    
    return $exit_code
}

# Usage function
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -s, --service SERVICE    Check specific service (qdrant, neo4j, n8n, grafana, prometheus, mcp-server)"
    echo "  -w, --watch [INTERVAL]   Watch mode - continuous monitoring (default: 30s)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                      # Check all services"
    echo "  $0 --service qdrant     # Check only Qdrant"
    echo "  $0 --watch 60           # Monitor every 60 seconds"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
        -w|--watch)
            WATCH_MODE=true
            WATCH_INTERVAL=${2:-30}
            shift
            if [[ $1 =~ ^[0-9]+$ ]]; then
                shift
            fi
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
if [ "$WATCH_MODE" = true ]; then
    echo -e "${BLUE}Starting health check monitoring (every ${WATCH_INTERVAL}s)${NC}"
    echo "Press Ctrl+C to stop"
    while true; do
        clear
        run_health_check
        sleep $WATCH_INTERVAL
    done
else
    run_health_check $SERVICE
fi
