#!/bin/bash

# Monitoring Management Script for CRY-A-4MCP
# This script helps manage the monitoring stack (Prometheus, Grafana, Alertmanager)

# Set script to exit on error
set -e

# Define colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Define the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to display usage information
usage() {
    echo -e "${YELLOW}Usage:${NC} $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start the monitoring stack"
    echo "  stop        - Stop the monitoring stack"
    echo "  restart     - Restart the monitoring stack"
    echo "  status      - Check the status of the monitoring stack"
    echo "  logs        - View logs from the monitoring stack"
    echo "  reload      - Reload Prometheus configuration"
    echo "  demo        - Run the monitoring demo script"
    echo "  help        - Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    - Start the monitoring stack"
    echo "  $0 logs     - View logs from all services"
    echo "  $0 logs prometheus - View logs from Prometheus only"
    echo ""
}

# Function to check if Docker and Docker Compose are installed
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}All prerequisites are met.${NC}"
}

# Function to start the monitoring stack
start_monitoring() {
    echo -e "${YELLOW}Starting the monitoring stack...${NC}"
    cd "$SCRIPT_DIR"
    docker-compose up -d
    echo -e "${GREEN}Monitoring stack started successfully.${NC}"
    echo -e "${GREEN}Prometheus: http://localhost:9090${NC}"
    echo -e "${GREEN}Grafana: http://localhost:3000 (admin/admin)${NC}"
    echo -e "${GREEN}Alertmanager: http://localhost:9093${NC}"
}

# Function to stop the monitoring stack
stop_monitoring() {
    echo -e "${YELLOW}Stopping the monitoring stack...${NC}"
    cd "$SCRIPT_DIR"
    docker-compose down
    echo -e "${GREEN}Monitoring stack stopped successfully.${NC}"
}

# Function to restart the monitoring stack
restart_monitoring() {
    echo -e "${YELLOW}Restarting the monitoring stack...${NC}"
    cd "$SCRIPT_DIR"
    docker-compose restart
    echo -e "${GREEN}Monitoring stack restarted successfully.${NC}"
}

# Function to check the status of the monitoring stack
check_status() {
    echo -e "${YELLOW}Checking the status of the monitoring stack...${NC}"
    cd "$SCRIPT_DIR"
    docker-compose ps
}

# Function to view logs from the monitoring stack
view_logs() {
    cd "$SCRIPT_DIR"
    if [ -z "$1" ]; then
        echo -e "${YELLOW}Viewing logs from all services...${NC}"
        docker-compose logs --tail=100 -f
    else
        echo -e "${YELLOW}Viewing logs from $1...${NC}"
        docker-compose logs --tail=100 -f "$1"
    fi
}

# Function to reload Prometheus configuration
reload_prometheus() {
    echo -e "${YELLOW}Reloading Prometheus configuration...${NC}"
    curl -X POST http://localhost:9090/-/reload
    echo -e "${GREEN}Prometheus configuration reloaded successfully.${NC}"
}

# Function to run the monitoring demo script
run_demo() {
    echo -e "${YELLOW}Running the monitoring demo script...${NC}"
    
    # Check if the demo script exists
    DEMO_SCRIPT="$SCRIPT_DIR/../examples/monitoring_demo.py"
    if [ ! -f "$DEMO_SCRIPT" ]; then
        echo -e "${RED}Error: Demo script not found at $DEMO_SCRIPT${NC}"
        exit 1
    fi
    
    # Run the demo script
    python3 "$DEMO_SCRIPT" "$@"
}

# Main function to handle commands
main() {
    # Check if a command was provided
    if [ $# -eq 0 ]; then
        usage
        exit 1
    fi
    
    # Parse the command
    case "$1" in
        start)
            check_prerequisites
            start_monitoring
            ;;
        stop)
            stop_monitoring
            ;;
        restart)
            restart_monitoring
            ;;
        status)
            check_status
            ;;
        logs)
            shift
            view_logs "$@"
            ;;
        reload)
            reload_prometheus
            ;;
        demo)
            shift
            run_demo "$@"
            ;;
        help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown command '$1'${NC}"
            usage
            exit 1
            ;;
    esac
}

# Call the main function with all arguments
main "$@"