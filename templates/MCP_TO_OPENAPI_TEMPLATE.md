# MCP Server to OpenAPI REST Endpoints Template

This template provides a standardized approach to expose any MCP (Model Context Protocol) server as OpenAPI-compatible REST endpoints using `mcpo` from the openapi-servers project.

## Overview

**Purpose**: Convert MCP tools into REST API endpoints with automatic OpenAPI schema generation
**Tool**: `mcpo` (MCP-to-OpenAPI proxy)
**Port**: 9134 (non-standard port to avoid conflicts)
**Benefits**: Zero code changes, automatic documentation, production-ready features

## Prerequisites

```bash
# Ensure uvx is available (comes with uv)
uvx --version

# Test mcpo availability
uvx mcpo --help
```

## Template Structure

### 1. Basic Setup Command

```bash
# Generic template - replace with your MCP server specifics
uvx mcpo \
  --port 9134 \
  --host 0.0.0.0 \
  --cors-allow-origins "*" \
  -- <MCP_SERVER_COMMAND>
```

### 2. MCP Server Command Patterns

Choose the appropriate pattern for your MCP server:

#### A. Python Module with Virtual Environment
```bash
# For servers with virtual environments (recommended)
uvx mcpo --port 9134 -- /path/to/project/.venv/bin/python -m your_mcp_module.main --transport stdio
```

#### B. Installed Entry Point
```bash
# For globally installed MCP servers
uvx mcpo --port 9134 -- your-mcp-server-command
```

#### C. Direct Python Script
```bash
# For standalone Python scripts
uvx mcpo --port 9134 -- python /path/to/your/mcp_server.py --transport stdio
```

#### D. Node.js MCP Server
```bash
# For Node.js based MCP servers
uvx mcpo --port 9134 -- node /path/to/your/mcp-server.js
```

### 3. Configuration Options

```bash
# Full configuration template
uvx mcpo \
  --port 9134 \                    # API port (avoid 8000, 3000, 8080)
  --host 0.0.0.0 \                # Allow external access
  --cors-allow-origins "*" \       # Enable CORS for web clients
  --api-key "your-secret-key" \    # Optional: Add API authentication
  --path-prefix "/api/v1" \        # Optional: URL prefix
  --name "Your MCP API" \          # Custom API name
  --description "Your API Description" \
  --version "1.0.0" \              # API version
  -- <MCP_SERVER_COMMAND>
```

### 4. Background Execution

```bash
# Run in background with logging
nohup uvx mcpo --port 9134 -- <MCP_SERVER_COMMAND> > mcpo.log 2>&1 &

# Save process ID for later management
echo $! > mcpo.pid
```

## Project-Specific Implementation

### Qdrant MCP Server Example

```bash
# Our working implementation
uvx mcpo \
  --port 9134 \
  --host 0.0.0.0 \
  --cors-allow-origins "*" \
  --name "Qdrant Vector Database API" \
  --description "Enhanced Qdrant MCP Server with GPU acceleration and collection-specific embedding models" \
  --version "0.7.1" \
  -- ./.venv/bin/python -m mcp_server_qdrant.enhanced_main --transport stdio
```

## Verification Steps

### 1. Health Check
```bash
# Test server startup
curl -f http://localhost:9134/docs || echo "Server not ready"
```

### 2. OpenAPI Schema Validation
```bash
# Get and validate OpenAPI schema
curl -s http://localhost:9134/openapi.json | python3 -m json.tool > openapi_schema.json
```

### 3. Tool Discovery
```bash
# List available endpoints (tools converted to REST)
curl -s http://localhost:9134/openapi.json | grep -o '"\/[^"]*"' | sort | uniq
```

### 4. Functional Testing
```bash
# Test a simple endpoint (adjust based on your MCP tools)
curl -X POST http://localhost:9134/<your_tool_endpoint> \
  -H "Content-Type: application/json" \
  -d '{"param1": "value1", "param2": "value2"}'
```

## Integration Patterns

### 1. Development Environment
```bash
# Local development with hot reload
uvx mcpo --port 9134 --hot-reload -- <MCP_SERVER_COMMAND>
```

### 2. Production Environment
```bash
# Production with SSL and authentication
uvx mcpo \
  --port 9134 \
  --ssl-certfile /path/to/cert.pem \
  --ssl-keyfile /path/to/key.pem \
  --api-key "${MCP_API_KEY}" \
  --strict-auth \
  -- <MCP_SERVER_COMMAND>
```

### 3. Docker Integration
```dockerfile
# Add to your MCP server Dockerfile
RUN pip install mcpo

# Expose OpenAPI port
EXPOSE 9134

# Start command (in docker-compose or CMD)
CMD ["uvx", "mcpo", "--port", "9134", "--host", "0.0.0.0", "--", "your-mcp-command"]
```

### 4. Systemd Service
```ini
# /etc/systemd/system/mcp-api.service
[Unit]
Description=MCP Server OpenAPI Proxy
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/your/mcp/server
ExecStart=/usr/bin/uvx mcpo --port 9134 -- <MCP_SERVER_COMMAND>
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Port Management

### Recommended Port Ranges
- **9134**: Primary recommendation (not commonly used)
- **9135-9139**: Alternative ports for multiple MCP APIs
- **Avoid**: 8000, 8080, 3000, 5000 (commonly used by other services)

### Port Conflict Resolution
```bash
# Check if port is in use
netstat -tulpn | grep :9134

# Find alternative port
for port in {9134..9139}; do
  if ! netstat -tulpn | grep -q ":$port "; then
    echo "Port $port is available"
    break
  fi
done
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Use full path to Python executable with virtual environment
2. **Connection refused**: Check if MCP server command works independently
3. **Port already in use**: Use different port or kill existing process
4. **CORS errors**: Add `--cors-allow-origins "*"` for development

### Debug Mode
```bash
# Enable verbose logging
uvx mcpo --port 9134 --log-level DEBUG -- <MCP_SERVER_COMMAND>
```

### Process Management
```bash
# Kill mcpo process
pkill -f "mcpo.*port 9134"

# Or using saved PID
kill $(cat mcpo.pid)
```

## API Documentation Access

Once running, your MCP server will be available as REST API:

- **Swagger UI**: `http://localhost:9134/docs`
- **OpenAPI Schema**: `http://localhost:9134/openapi.json`
- **ReDoc**: `http://localhost:9134/redoc`

## Security Considerations

1. **API Keys**: Use `--api-key` for authentication in production
2. **CORS**: Restrict `--cors-allow-origins` to specific domains in production
3. **SSL**: Use `--ssl-certfile` and `--ssl-keyfile` for HTTPS
4. **Firewall**: Restrict access to port 9134 as needed
5. **Rate Limiting**: Consider adding a reverse proxy with rate limiting

## Automation Script Template

```bash
#!/bin/bash
# start-mcp-api.sh

set -e

# Configuration
MCP_PORT=${MCP_PORT:-9134}
MCP_HOST=${MCP_HOST:-0.0.0.0}
MCP_SERVER_COMMAND="$1"

if [ -z "$MCP_SERVER_COMMAND" ]; then
  echo "Usage: $0 '<MCP_SERVER_COMMAND>'"
  echo "Example: $0 'python -m my_mcp.main --transport stdio'"
  exit 1
fi

# Check if port is available
if netstat -tulpn | grep -q ":$MCP_PORT "; then
  echo "Error: Port $MCP_PORT is already in use"
  exit 1
fi

# Start mcpo
echo "Starting MCP OpenAPI proxy on port $MCP_PORT..."
exec uvx mcpo \
  --port "$MCP_PORT" \
  --host "$MCP_HOST" \
  --cors-allow-origins "*" \
  -- $MCP_SERVER_COMMAND
```

## Usage Example

```bash
# Make script executable
chmod +x start-mcp-api.sh

# Use with any MCP server
./start-mcp-api.sh "python -m my_mcp_server.main --transport stdio"
```

This template provides a complete, reusable solution for exposing any MCP server as OpenAPI-compatible REST endpoints with comprehensive documentation and production considerations.