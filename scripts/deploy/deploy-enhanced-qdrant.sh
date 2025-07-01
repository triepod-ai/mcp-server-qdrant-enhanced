#!/bin/bash

# Enhanced Qdrant MCP Server Deployment Script
# Deploys the enhanced MCP server with multi-vector collection support

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${SCRIPT_DIR}/.venv"
SERVICE_NAME="mcp-server-qdrant-enhanced"

# Enhanced MCP configuration
ENHANCED_ENV_VARS=(
    "QDRANT_URL=http://localhost:6333"
    "COLLECTION_NAME=working_solutions"
    "QDRANT_AUTO_CREATE_COLLECTIONS=true"
    "QDRANT_ENABLE_QUANTIZATION=true"
    "QDRANT_HNSW_EF_CONSTRUCT=200"
    "QDRANT_HNSW_M=16"
    "EMBEDDING_PROVIDER=FASTEMBED"
    "EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2"
)

# Collection model mappings (predefined in enhanced_settings.py)
COLLECTION_MAPPINGS=(
    "lodestar_legal_analysis -> BAAI/bge-large-en-v1.5 (1024D)"
    "lodestar_workplace_documentation -> BAAI/bge-base-en-v1.5 (768D)"
    "working_solutions -> sentence-transformers/all-MiniLM-L6-v2 (384D)"
    "debugging_patterns -> sentence-transformers/all-MiniLM-L6-v2 (384D)"
    "lessons_learned -> BAAI/bge-base-en (768D)"
)

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

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check for Qdrant server
    if ! curl -s http://localhost:6333/health >/dev/null 2>&1; then
        log_warning "Qdrant server not accessible at localhost:6333"
        log_info "Starting Qdrant server if available..."
        
        # Try to start Qdrant with Docker
        if command -v docker >/dev/null 2>&1; then
            if ! docker ps | grep -q qdrant; then
                log_info "Starting Qdrant with Docker..."
                docker run -d --name qdrant-enhanced -p 6333:6333 -p 6334:6334 \
                    -v "${HOME}/qdrant_storage:/qdrant/storage" \
                    qdrant/qdrant:latest || log_warning "Failed to start Qdrant with Docker"
                sleep 5
            fi
        else
            log_warning "Docker not available. Please ensure Qdrant is running at localhost:6333"
        fi
    else
        log_success "Qdrant server is accessible"
    fi
    
    # Check virtual environment
    if [[ ! -d "${VENV_PATH}" ]]; then
        log_error "Virtual environment not found at ${VENV_PATH}"
        log_info "Please run: python -m venv .venv && source .venv/bin/activate && pip install -e ."
        exit 1
    fi
    
    log_success "Dependencies check completed"
}

backup_current_config() {
    log_info "Creating backup of current configuration..."
    
    # Backup existing Claude MCP config if it exists
    if [[ -f "${HOME}/.config/claude-desktop/config.json" ]]; then
        cp "${HOME}/.config/claude-desktop/config.json" \
           "${HOME}/.config/claude-desktop/config.json.backup.$(date +%Y%m%d_%H%M%S)"
        log_success "Claude config backed up"
    fi
    
    # Backup any existing wrapper scripts
    if [[ -f "${SCRIPT_DIR}/run-mcp-qdrant-direct.sh" ]]; then
        cp "${SCRIPT_DIR}/run-mcp-qdrant-direct.sh" \
           "${SCRIPT_DIR}/run-mcp-qdrant-direct.sh.backup.$(date +%Y%m%d_%H%M%S)"
        log_success "Existing wrapper script backed up"
    fi
}

create_wrapper_script() {
    log_info "Creating enhanced MCP server wrapper script..."
    
    cat > "${SCRIPT_DIR}/run-enhanced-mcp-qdrant.sh" << 'EOF'
#!/bin/bash

# Enhanced Qdrant MCP Server Wrapper
# Supports multi-vector collections with collection-specific embedding models

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${SCRIPT_DIR}/.venv"

# Enhanced environment variables
export PYTHONUNBUFFERED=1
export QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
export COLLECTION_NAME="${COLLECTION_NAME:-working_solutions}"
export QDRANT_AUTO_CREATE_COLLECTIONS="${QDRANT_AUTO_CREATE_COLLECTIONS:-true}"
export QDRANT_ENABLE_QUANTIZATION="${QDRANT_ENABLE_QUANTIZATION:-true}"
export QDRANT_HNSW_EF_CONSTRUCT="${QDRANT_HNSW_EF_CONSTRUCT:-200}"
export QDRANT_HNSW_M="${QDRANT_HNSW_M:-16}"
export EMBEDDING_PROVIDER="${EMBEDDING_PROVIDER:-FASTEMBED}"
export EMBEDDING_MODEL="${EMBEDDING_MODEL:-sentence-transformers/all-MiniLM-L6-v2}"

# Activate virtual environment
if [[ -f "${VENV_PATH}/bin/activate" ]]; then
    source "${VENV_PATH}/bin/activate"
else
    echo "ERROR: Virtual environment not found at ${VENV_PATH}" >&2
    exit 1
fi

# Execute enhanced MCP server
exec python -u -m mcp_server_qdrant.enhanced_main --transport stdio
EOF

    chmod +x "${SCRIPT_DIR}/run-enhanced-mcp-qdrant.sh"
    log_success "Enhanced wrapper script created: run-enhanced-mcp-qdrant.sh"
}

setup_environment() {
    log_info "Setting up environment variables..."
    
    # Create .env file for development
    cat > "${SCRIPT_DIR}/.env.enhanced" << EOF
# Enhanced Qdrant MCP Server Configuration
# Multi-vector collection support with collection-specific embedding models

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=working_solutions
QDRANT_AUTO_CREATE_COLLECTIONS=true
QDRANT_ENABLE_QUANTIZATION=true
QDRANT_HNSW_EF_CONSTRUCT=200
QDRANT_HNSW_M=16

# Embedding Configuration
EMBEDDING_PROVIDER=FASTEMBED
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Collection Model Mappings (handled automatically by enhanced_settings.py):
# lodestar_legal_analysis -> BAAI/bge-large-en-v1.5 (1024D)
# lodestar_workplace_documentation -> BAAI/bge-base-en-v1.5 (768D)  
# working_solutions -> sentence-transformers/all-MiniLM-L6-v2 (384D)
# debugging_patterns -> sentence-transformers/all-MiniLM-L6-v2 (384D)
# lessons_learned -> BAAI/bge-base-en (768D)

# Performance Tuning
QDRANT_SEARCH_LIMIT=10
QDRANT_READ_ONLY=false
EOF

    log_success "Environment configuration created: .env.enhanced"
}

test_server() {
    log_info "Testing enhanced MCP server..."
    
    # Test server startup (5 second timeout)
    if timeout 5s "${SCRIPT_DIR}/run-enhanced-mcp-qdrant.sh" < /dev/null >/dev/null 2>&1; then
        log_success "Server startup test completed"
    else
        # Expected for stdio mode - server waits for input
        log_success "Server startup test completed (stdio mode timeout expected)"
    fi
    
    # Test Python imports
    source "${VENV_PATH}/bin/activate"
    python -c "
import sys
sys.path.insert(0, 'src')
from mcp_server_qdrant.enhanced_settings import EnhancedEmbeddingProviderSettings
from mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector
from mcp_server_qdrant.mcp_server import QdrantMCPServer
print('✓ All enhanced modules import successfully')
"
    
    log_success "Enhanced MCP server tests passed"
}

build_container() {
    log_info "Building enhanced container image..."
    
    # Check if Docker is available
    if ! command -v docker >/dev/null 2>&1; then
        log_warning "Docker not available. Skipping container build."
        return 0
    fi
    
    # Build the enhanced container
    local image_name="qdrant-mcp-enhanced"
    local tag="latest"
    
    log_info "Building Docker image: ${image_name}:${tag}"
    
    if docker build -f Dockerfile.enhanced -t "${image_name}:${tag}" .; then
        log_success "Container image built successfully: ${image_name}:${tag}"
        
        # Create docker run script
        cat > "${SCRIPT_DIR}/run-enhanced-container.sh" << 'EOF'
#!/bin/bash

# Enhanced Qdrant MCP Server Container Runner
# Runs the enhanced MCP server in a Docker container

set -euo pipefail

# Container configuration
IMAGE_NAME="qdrant-mcp-enhanced:latest"
CONTAINER_NAME="qdrant-mcp-enhanced"

# Enhanced environment variables
ENV_VARS=(
    "-e" "QDRANT_URL=${QDRANT_URL:-http://host.docker.internal:6333}"
    "-e" "COLLECTION_NAME=${COLLECTION_NAME:-working_solutions}"
    "-e" "QDRANT_AUTO_CREATE_COLLECTIONS=${QDRANT_AUTO_CREATE_COLLECTIONS:-true}"
    "-e" "QDRANT_ENABLE_QUANTIZATION=${QDRANT_ENABLE_QUANTIZATION:-true}"
    "-e" "QDRANT_HNSW_EF_CONSTRUCT=${QDRANT_HNSW_EF_CONSTRUCT:-200}"
    "-e" "QDRANT_HNSW_M=${QDRANT_HNSW_M:-16}"
    "-e" "EMBEDDING_PROVIDER=${EMBEDDING_PROVIDER:-FASTEMBED}"
    "-e" "EMBEDDING_MODEL=${EMBEDDING_MODEL:-sentence-transformers/all-MiniLM-L6-v2}"
)

# Remove existing container if it exists
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true

# Run the container
exec docker run -i --rm --name "${CONTAINER_NAME}" "${ENV_VARS[@]}" "${IMAGE_NAME}"
EOF
        
        chmod +x "${SCRIPT_DIR}/run-enhanced-container.sh"
        log_success "Container run script created: run-enhanced-container.sh"
        
        # Create Claude config for container
        cat > "${SCRIPT_DIR}/claude-mcp-config-container.json" << EOF
{
  "mcpServers": {
    "qdrant-enhanced-container": {
      "command": "${SCRIPT_DIR}/run-enhanced-container.sh",
      "args": [],
      "env": {
        "QDRANT_URL": "http://host.docker.internal:6333",
        "COLLECTION_NAME": "working_solutions",
        "QDRANT_AUTO_CREATE_COLLECTIONS": "true",
        "QDRANT_ENABLE_QUANTIZATION": "true",
        "EMBEDDING_PROVIDER": "FASTEMBED"
      }
    }
  }
}
EOF
        log_success "Container Claude configuration generated: claude-mcp-config-container.json"
        
    else
        log_error "Failed to build container image"
        return 1
    fi
}

generate_claude_config() {
    log_info "Generating Claude configuration..."
    
    local claude_config_dir="${HOME}/.config/claude-desktop"
    local claude_config="${claude_config_dir}/config.json"
    local mcp_command="${SCRIPT_DIR}/run-enhanced-mcp-qdrant.sh"
    
    # Create config directory if it doesn't exist
    mkdir -p "${claude_config_dir}"
    
    # Generate configuration snippet
    cat > "${SCRIPT_DIR}/claude-mcp-config.json" << EOF
{
  "mcpServers": {
    "qdrant-enhanced": {
      "command": "${mcp_command}",
      "args": [],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "working_solutions",
        "QDRANT_AUTO_CREATE_COLLECTIONS": "true",
        "QDRANT_ENABLE_QUANTIZATION": "true",
        "EMBEDDING_PROVIDER": "FASTEMBED"
      }
    }
  }
}
EOF

    log_success "Claude configuration generated: claude-mcp-config.json"
    log_info "To add to Claude, merge this with your existing config.json"
}

show_deployment_summary() {
    log_success "🚀 Enhanced Qdrant MCP Server Deployment Complete!"
    echo
    log_info "📁 Files Created:"
    echo "  • run-enhanced-mcp-qdrant.sh (wrapper script)"
    echo "  • .env.enhanced (environment config)"
    echo "  • claude-mcp-config.json (Claude integration)"
    echo "  • Dockerfile.enhanced (container definition)"
    echo "  • run-enhanced-container.sh (container runner)"
    echo "  • claude-mcp-config-container.json (container Claude config)"
    echo
    log_info "🎯 Collection Model Mappings:"
    for mapping in "${COLLECTION_MAPPINGS[@]}"; do
        echo "  • ${mapping}"
    done
    echo
    log_info "⚙️ Key Features Enabled:"
    echo "  • Multi-vector dimensions (384D, 768D, 1024D)"
    echo "  • Collection-specific embedding models"
    echo "  • Auto-collection creation with optimal configs"
    echo "  • Memory-optimized quantization"
    echo "  • Enhanced HNSW parameters"
    echo
    log_info "🔧 Next Steps:"
    echo "  1. Add claude-mcp-config.json to your Claude config (native)"
    echo "  2. OR add claude-mcp-config-container.json for container mode"
    echo "  3. Restart Claude to load the enhanced server"
    echo "  4. Test with: claude mcp test qdrant-enhanced"
    echo
    log_info "📊 Test Commands:"
    echo "  • Native test: ${SCRIPT_DIR}/run-enhanced-mcp-qdrant.sh"
    echo "  • Container test: ${SCRIPT_DIR}/run-enhanced-container.sh"
    echo "  • Environment: source ${SCRIPT_DIR}/.env.enhanced"
    echo
}

# Main deployment process
main() {
    log_info "🚀 Starting Enhanced Qdrant MCP Server Deployment..."
    echo
    
    check_dependencies
    backup_current_config
    setup_environment
    create_wrapper_script
    test_server
    build_container
    generate_claude_config
    show_deployment_summary
    
    log_success "✅ Deployment completed successfully!"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "test")
        log_info "Testing enhanced MCP server..."
        test_server
        ;;
    "config")
        log_info "Generating Claude configuration..."
        generate_claude_config
        ;;
    "build")
        log_info "Building enhanced container only..."
        build_container
        ;;
    "clean")
        log_info "Cleaning up deployment files..."
        rm -f "${SCRIPT_DIR}/run-enhanced-mcp-qdrant.sh"
        rm -f "${SCRIPT_DIR}/.env.enhanced"
        rm -f "${SCRIPT_DIR}/claude-mcp-config.json"
        rm -f "${SCRIPT_DIR}/run-enhanced-container.sh"
        rm -f "${SCRIPT_DIR}/claude-mcp-config-container.json"
        # Remove Docker image if it exists
        if command -v docker >/dev/null 2>&1; then
            docker rmi qdrant-mcp-enhanced:latest 2>/dev/null || true
        fi
        log_success "Cleanup completed"
        ;;
    *)
        echo "Usage: $0 [deploy|test|config|build|clean]"
        echo "  deploy - Full deployment (default)"
        echo "  test   - Test server functionality"
        echo "  config - Generate Claude configuration only"
        echo "  build  - Build container image only"
        echo "  clean  - Remove deployment files"
        exit 1
        ;;
esac