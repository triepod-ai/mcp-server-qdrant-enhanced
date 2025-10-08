#!/bin/bash
# start-mcp-api.sh - Universal MCP Server to OpenAPI REST API starter
# Usage: ./start-mcp-api.sh '<MCP_SERVER_COMMAND>'

set -e

# Configuration
MCP_PORT=${MCP_PORT:-9134}
MCP_HOST=${MCP_HOST:-0.0.0.0}
MCP_SERVER_COMMAND="$1"
PROJECT_NAME=${2:-"MCP Server"}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Validate input
if [ -z "$MCP_SERVER_COMMAND" ]; then
  log_error "Usage: $0 '<MCP_SERVER_COMMAND>' [project_name]"
  echo ""
  echo "Examples:"
  echo "  $0 'python -m my_mcp.main --transport stdio' 'My MCP Server'"
  echo "  $0 '/path/to/.venv/bin/python -m mcp_server.main --transport stdio'"
  echo "  $0 'my-mcp-server-command'"
  exit 1
fi

# Check if port is available
log_info "Checking if port $MCP_PORT is available..."
if netstat -tulpn 2>/dev/null | grep -q ":$MCP_PORT "; then
  log_error "Port $MCP_PORT is already in use"
  echo "Processes using port $MCP_PORT:"
  netstat -tulpn | grep ":$MCP_PORT "
  echo ""
  echo "You can:"
  echo "  1. Kill the process: pkill -f 'mcpo.*port $MCP_PORT'"
  echo "  2. Use a different port: MCP_PORT=9135 $0 '$MCP_SERVER_COMMAND'"
  exit 1
fi

log_success "Port $MCP_PORT is available"

# Test mcpo availability
log_info "Checking mcpo availability..."
if ! uvx mcpo --help &>/dev/null; then
  log_error "mcpo is not available via uvx"
  echo "Install with: uvx --help  # Should show uvx is available"
  exit 1
fi

log_success "mcpo is available"

# Test MCP server command independently (optional quick test)
log_info "Starting MCP OpenAPI proxy on port $MCP_PORT..."
echo "Project: $PROJECT_NAME"
echo "Command: $MCP_SERVER_COMMAND"
echo ""

# Start mcpo with enhanced configuration
exec uvx mcpo \
  --port "$MCP_PORT" \
  --host "$MCP_HOST" \
  --cors-allow-origins "*" \
  --name "$PROJECT_NAME API" \
  --description "OpenAPI endpoints for $PROJECT_NAME MCP server" \
  --version "1.0.0" \
  -- $MCP_SERVER_COMMAND