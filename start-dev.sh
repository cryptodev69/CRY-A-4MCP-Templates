#!/bin/bash

# CRY-A-4MCP Development Server Startup Script
# This script manages both frontend and backend services in a unified way

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[CRY-A-4MCP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ ! -z "$pids" ]; then
        print_warning "Found existing processes on port $port. Terminating..."
        
        # Check if any of the processes are system processes that shouldn't be killed
        local system_processes=$(lsof -ti:$port 2>/dev/null | xargs ps -p 2>/dev/null | grep -E "ControlCenter|SystemUIServer|Finder" || true)
        
        if [ ! -z "$system_processes" ]; then
            print_warning "System process detected on port $port. Trying alternative port..."
            return 2  # Special return code for system process
        fi
        
        echo $pids | xargs kill -9 2>/dev/null || true
        sleep 2
        
        # Double check if processes are killed
        local remaining_pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$remaining_pids" ]; then
            print_error "Failed to kill all processes on port $port"
            return 1
        else
            print_success "Port $port is now available"
        fi
    else
        print_status "Port $port is available"
    fi
    return 0
}

# Function to cleanup processes on exit
cleanup() {
    print_status "Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend server stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if required directories exist
if [ ! -d "starter-mcp-server" ]; then
    print_error "starter-mcp-server directory not found!"
    exit 1
fi

if [ ! -d "frontend" ]; then
    print_error "frontend directory not found!"
    exit 1
fi

print_status "Starting CRY-A-4MCP Development Environment..."

# Kill any existing processes on target ports
print_status "Checking and clearing target ports..."
if ! kill_port 4000; then  # Backend port
    print_error "Failed to clear port 4000. Exiting."
    exit 1
fi

# Handle frontend port with fallback
FRONTEND_PORT=5000
set +e  # Temporarily disable exit on error
kill_port 5000
kill_port_result=$?
set -e  # Re-enable exit on error

if [ "$kill_port_result" = "2" ]; then
    # System process detected, try alternative ports
    print_status "Trying alternative frontend ports..."
    for alt_port in 3000 3001 5001 5002 8080; do
        set +e
        kill_port $alt_port
        alt_result=$?
        set -e
        if [ "$alt_result" = "0" ]; then
            FRONTEND_PORT=$alt_port
            print_success "Will use port $FRONTEND_PORT for frontend"
            break
        fi
    done
    if [ "$FRONTEND_PORT" = "5000" ]; then
        print_error "No available alternative ports found. Exiting."
        exit 1
    fi
elif [ "$kill_port_result" != "0" ]; then
    print_error "Failed to clear port 5000. Exiting."
    exit 1
fi

print_success "All target ports are now available"

# Check if virtual environment exists for backend
if [ ! -d "starter-mcp-server/venv311" ]; then
    print_error "Python virtual environment not found at starter-mcp-server/venv311"
    print_status "Please run setup first or create the virtual environment"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    print_status "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    print_success "Frontend dependencies installed"
fi

# Start backend server
print_status "Starting backend server on port 4000..."
cd starter-mcp-server
source venv311/bin/activate
python -m src.cry_a_4mcp.web_api &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend server failed to start"
    exit 1
fi

print_success "Backend server started (PID: $BACKEND_PID)"

# Start frontend server
print_status "Starting frontend server on port $FRONTEND_PORT..."
cd frontend
# Override the hardcoded PORT in package.json by setting environment variable
export PORT=$FRONTEND_PORT
npm run start &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend server failed to start"
    cleanup
    exit 1
fi

print_success "Frontend server started (PID: $FRONTEND_PID)"

print_status "=================================================="
print_success "CRY-A-4MCP Development Environment is ready!"
print_status "Frontend: http://localhost:$FRONTEND_PORT"
print_status "Backend API: http://localhost:4000"
print_status "=================================================="
print_warning "Press Ctrl+C to stop all services"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID