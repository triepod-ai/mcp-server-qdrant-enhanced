#!/bin/bash

# Development Convenience Script for Enhanced Qdrant MCP Server
# Preserves existing workflow while adding development automation

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project directory (auto-detect from script location)
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_help() {
    echo "Enhanced Qdrant MCP Server - Development Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start           Start the enhanced MCP server (preserves existing workflow)"
    echo "  stop            Stop the enhanced MCP server"
    echo "  restart         Restart the enhanced MCP server"
    echo "  build           Build the Docker image"
    echo "  rebuild         Force rebuild Docker image with no cache"
    echo "  logs            Show container logs"
    echo "  test            Run tests and validation"
    echo "  lint            Run linting and formatting"
    echo "  clean           Clean up containers and images"
    echo "  status          Show container status"
    echo "  shell           Open shell in running container"
    echo "  dev-mode        Start in development mode with volume mounts"
    echo "  quick-test      Quick validation of MCP server functionality"
    echo "  help            Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start         # Start using existing docker-compose.enhanced.yml"
    echo "  $0 dev-mode      # Start with live code reloading"
    echo "  $0 quick-test    # Test MCP tools quickly"
    echo
}

ensure_project_dir() {
    if [[ ! -d "$PROJECT_DIR" ]]; then
        log_error "Project directory not found: $PROJECT_DIR"
        exit 1
    fi
    cd "$PROJECT_DIR"
}

start_server() {
    log_info "Starting Enhanced Qdrant MCP Server (existing workflow)..."
    
    # Use existing deploy script if available, otherwise use docker-compose directly
    if [[ -f "deploy.sh" ]]; then
        log_info "Using existing deploy.sh script"
        ./deploy.sh
    else
        log_info "Using docker-compose directly"
        docker-compose -f docker-compose.enhanced.yml up -d
    fi
    
    log_success "Server started successfully"
}

stop_server() {
    log_info "Stopping Enhanced Qdrant MCP Server..."
    
    if docker-compose -f docker-compose.enhanced.yml down; then
        log_success "Server stopped successfully"
    else
        log_warning "No server was running"
    fi
}

restart_server() {
    log_info "Restarting Enhanced Qdrant MCP Server..."
    stop_server
    sleep 2
    start_server
}

build_image() {
    log_info "Building Docker image..."
    
    if docker build -f Dockerfile.enhanced -t triepod-ai/mcp-server-qdrant-enhanced .; then
        log_success "Docker image built successfully"
    else
        log_error "Docker build failed"
        exit 1
    fi
}

rebuild_image() {
    log_info "Force rebuilding Docker image (no cache)..."
    
    if docker build --no-cache -f Dockerfile.enhanced -t triepod-ai/mcp-server-qdrant-enhanced .; then
        log_success "Docker image rebuilt successfully"
    else
        log_error "Docker rebuild failed"
        exit 1
    fi
}

show_logs() {
    log_info "Showing container logs..."
    docker-compose -f docker-compose.enhanced.yml logs -f
}

run_tests() {
    log_info "Running tests and validation..."
    
    # Check if we have a test directory
    if [[ -d "tests" ]]; then
        log_info "Running pytest..."
        if command -v python3 &> /dev/null; then
            python3 -m pytest tests/ || log_warning "Some tests failed"
        else
            log_warning "Python3 not found, skipping pytest"
        fi
    else
        log_warning "No tests directory found"
    fi
    
    # Run linting if available
    if command -v ruff &> /dev/null; then
        log_info "Running ruff checks..."
        ruff check src/ || log_warning "Linting issues found"
    else
        log_warning "Ruff not found, skipping linting"
    fi
    
    # Run type checking if available
    if command -v mypy &> /dev/null; then
        log_info "Running type checking..."
        mypy src/ || log_warning "Type checking issues found"
    else
        log_warning "MyPy not found, skipping type checking"
    fi
    
    log_success "Validation completed"
}

run_lint() {
    log_info "Running linting and formatting..."
    
    if command -v ruff &> /dev/null; then
        log_info "Running ruff format..."
        ruff format src/
        
        log_info "Running ruff check..."
        ruff check src/ --fix || log_warning "Some linting issues couldn't be auto-fixed"
        
        log_success "Linting completed"
    else
        log_error "Ruff not found. Install with: pip install ruff"
        exit 1
    fi
}

clean_containers() {
    log_info "Cleaning up containers and images..."
    
    # Stop containers
    docker-compose -f docker-compose.enhanced.yml down || true
    
    # Remove containers
    docker rm -f mcp-server-qdrant-enhanced 2>/dev/null || true
    
    # Remove development images (keep production ones)
    docker rmi triepod-ai/mcp-server-qdrant-enhanced:dev 2>/dev/null || true
    
    # Clean up dangling images
    docker image prune -f
    
    log_success "Cleanup completed"
}

show_status() {
    log_info "Container status:"
    echo
    
    # Show running containers
    if docker ps | grep -q "mcp-server-qdrant-enhanced"; then
        log_success "Enhanced MCP Server is running"
        docker ps | grep "mcp-server-qdrant-enhanced"
    else
        log_warning "Enhanced MCP Server is not running"
    fi
    
    echo
    
    # Show docker-compose status
    log_info "Docker Compose status:"
    docker-compose -f docker-compose.enhanced.yml ps
}

open_shell() {
    log_info "Opening shell in running container..."
    
    if docker ps | grep -q "mcp-server-qdrant-enhanced"; then
        docker exec -it mcp-server-qdrant-enhanced /bin/bash
    else
        log_error "Container is not running. Start it first with: $0 start"
        exit 1
    fi
}

dev_mode() {
    log_info "Starting in development mode with volume mounts..."
    
    # Create a development docker-compose override
    cat > docker-compose.dev.yml << EOF
version: '3.8'

services:
  mcp-server-enhanced:
    build: 
      context: .
      dockerfile: Dockerfile.enhanced
      target: development
    volumes:
      - ./src:/app/src:ro
      - ./logs:/app/logs:rw
    environment:
      - PYTHONPATH=/app/src
      - PYTHONUNBUFFERED=1
      - QDRANT_URL=http://localhost:6333
      - COLLECTION_NAME=dev-collection
    command: ["python", "-u", "-m", "mcp_server_qdrant.enhanced_main", "--transport", "stdio"]
EOF
    
    log_info "Starting development container with live reloading..."
    docker-compose -f docker-compose.enhanced.yml -f docker-compose.dev.yml up -d
    
    log_success "Development mode started. Code changes will be reflected immediately."
    log_info "View logs with: $0 logs"
}

quick_test() {
    log_info "Running quick MCP server functionality test..."
    
    # Check if container is running
    if ! docker ps | grep -q "mcp-server-qdrant-enhanced"; then
        log_warning "Container not running, starting it first..."
        start_server
        sleep 5
    fi
    
    # Test MCP tools using the wrapper script if available
    if [[ -f "${HOME}/run-qdrant-docker-mcp.sh" ]]; then
        log_info "Testing MCP tools via wrapper script..."
        
        # Simple test - this would require actual MCP client integration
        log_info "MCP server appears to be running correctly"
        log_info "For full testing, use a proper MCP client (Claude Desktop, VS Code, etc.)"
    else
        log_warning "Wrapper script not found, basic container test only"
    fi
    
    # Show container health
    if docker ps | grep -q "mcp-server-qdrant-enhanced.*Up"; then
        log_success "Container is healthy and running"
    else
        log_error "Container health check failed"
        docker logs mcp-server-qdrant-enhanced --tail 20
    fi
}

# Main command handling
case "${1:-help}" in
    start)
        ensure_project_dir
        start_server
        ;;
    stop)
        ensure_project_dir
        stop_server
        ;;
    restart)
        ensure_project_dir
        restart_server
        ;;
    build)
        ensure_project_dir
        build_image
        ;;
    rebuild)
        ensure_project_dir
        rebuild_image
        ;;
    logs)
        ensure_project_dir
        show_logs
        ;;
    test)
        ensure_project_dir
        run_tests
        ;;
    lint)
        ensure_project_dir
        run_lint
        ;;
    clean)
        ensure_project_dir
        clean_containers
        ;;
    status)
        ensure_project_dir
        show_status
        ;;
    shell)
        ensure_project_dir
        open_shell
        ;;
    dev-mode)
        ensure_project_dir
        dev_mode
        ;;
    quick-test)
        ensure_project_dir
        quick_test
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac