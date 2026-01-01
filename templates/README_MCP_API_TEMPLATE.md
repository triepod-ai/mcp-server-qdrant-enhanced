# MCP Server to OpenAPI Template - Usage Guide

## Quick Start

This template enables any MCP server to be exposed as OpenAPI-compatible REST endpoints using port **9134** (non-standard to avoid conflicts).

### Files Created

1. **`templates/MCP_TO_OPENAPI_TEMPLATE.md`** - Complete documentation and patterns
2. **`start-mcp-api.sh`** - Universal automation script
3. **`templates/README_MCP_API_TEMPLATE.md`** - This usage guide

## Instant Usage

### For This Project (Qdrant MCP Server)

```bash
# Start the enhanced Qdrant MCP server as REST API
./start-mcp-api.sh "./.venv/bin/python -m mcp_server_qdrant.enhanced_main --transport stdio" "Enhanced Qdrant MCP Server"

# Access the API
open http://localhost:9134/docs  # Swagger UI
curl http://localhost:9134/openapi.json  # OpenAPI schema
```

### For Other MCP Servers

```bash
# Copy the template files to your MCP project
cp templates/MCP_TO_OPENAPI_TEMPLATE.md /path/to/your/mcp-project/
cp start-mcp-api.sh /path/to/your/mcp-project/
chmod +x /path/to/your/mcp-project/start-mcp-api.sh

# Adapt for your MCP server
cd /path/to/your/mcp-project
./start-mcp-api.sh "your-mcp-server-command" "Your Project Name"
```

## Common Patterns

### Python MCP Servers with Virtual Environments
```bash
./start-mcp-api.sh "/path/to/.venv/bin/python -m your_mcp.main --transport stdio" "Your MCP Server"
```

### Globally Installed MCP Servers
```bash
./start-mcp-api.sh "your-mcp-server-command" "Your MCP Server"
```

### Node.js MCP Servers
```bash
./start-mcp-api.sh "node /path/to/your-mcp-server.js" "Your Node MCP Server"
```

### Custom Port
```bash
MCP_PORT=9135 ./start-mcp-api.sh "your-mcp-command" "Your MCP Server"
```

## Validated Test Results

✅ **Port 9134**: Successfully tested and confirmed working
✅ **Swagger UI**: Available at `http://localhost:9134/docs`
✅ **OpenAPI Schema**: Generated automatically from MCP tools
✅ **Store Operation**: `POST /qdrant_store` working
✅ **Search Operation**: `POST /qdrant_find` working
✅ **List Collections**: `POST /qdrant_list_collections` working
✅ **CORS Enabled**: Cross-origin requests supported

### Test Commands Used

```bash
# Store document
curl -X POST http://localhost:9134/qdrant_store \
  -H "Content-Type: application/json" \
  -d '{"information": "Template test document using port 9134", "collection_name": "template_test_collection", "metadata": {"source": "template_test", "port": 9134}}'

# Search documents
curl -X POST http://localhost:9134/qdrant_find \
  -H "Content-Type: application/json" \
  -d '{"query": "template test document", "collection_name": "template_test_collection", "limit": 3}'
```

## Port Strategy

- **Primary Port**: 9134 (chosen to avoid common conflicts)
- **Alternative Ports**: 9135-9139 for multiple APIs
- **Avoided Ports**: 8000, 8080, 3000, 5000 (commonly used)

### Port Conflict Resolution

```bash
# Check if port is in use
netstat -tulpn | grep :9134

# Use alternative port if needed
MCP_PORT=9135 ./start-mcp-api.sh "your-mcp-command"
```

## Production Deployment

### With Authentication
```bash
uvx mcpo \
  --port 9134 \
  --api-key "your-secret-key" \
  --strict-auth \
  -- your-mcp-command
```

### With SSL
```bash
uvx mcpo \
  --port 9134 \
  --ssl-certfile /path/to/cert.pem \
  --ssl-keyfile /path/to/key.pem \
  -- your-mcp-command
```

### With Restricted CORS
```bash
uvx mcpo \
  --port 9134 \
  --cors-allow-origins "https://yourdomain.com,https://api.yourdomain.com" \
  -- your-mcp-command
```

## Process Management

### Background Execution
```bash
# Start in background
nohup ./start-mcp-api.sh "your-mcp-command" > mcpo.log 2>&1 &
echo $! > mcpo.pid

# Stop
kill $(cat mcpo.pid)
```

### Using Screen/Tmux
```bash
# Start in screen session
screen -S mcp-api ./start-mcp-api.sh "your-mcp-command"

# Detach: Ctrl+A, D
# Reattach: screen -r mcp-api
```

## Integration Examples

### Docker Compose
```yaml
version: '3.8'
services:
  mcp-api:
    build: .
    ports:
      - "9134:9134"
    command: uvx mcpo --port 9134 --host 0.0.0.0 -- your-mcp-command
    environment:
      - MCP_PORT=9134
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-api.domain.com;

    location / {
        proxy_pass http://localhost:9134;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Systemd Service
```ini
[Unit]
Description=MCP OpenAPI Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/your/mcp-server
ExecStart=/path/to/start-mcp-api.sh "your-mcp-command" "Your MCP Server"
Restart=always

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Common Issues

1. **Port in use**: Use `MCP_PORT=9135` to try different port
2. **Module not found**: Use full path to Python executable with venv
3. **CORS errors**: Ensure `--cors-allow-origins "*"` is set
4. **Connection refused**: Check MCP server command works independently

### Debug Mode
```bash
# Enable verbose logging in the script
uvx mcpo --port 9134 --log-level DEBUG -- your-mcp-command
```

### Health Check
```bash
# Quick health check
curl -f http://localhost:9134/docs && echo "✅ API is healthy" || echo "❌ API is down"
```

## Benefits of This Template

1. **Zero Code Changes**: Works with any existing MCP server
2. **Standardized Port**: 9134 avoids common conflicts
3. **Production Ready**: Includes authentication, SSL, CORS options
4. **Automated Setup**: Single script handles all configuration
5. **Universal**: Works with Python, Node.js, any MCP server
6. **Well-Documented**: Complete patterns and examples included
7. **Tested**: Validated with real Qdrant MCP server implementation

## Next Steps

1. Copy template files to your MCP project
2. Run `./start-mcp-api.sh "your-mcp-command"`
3. Access `http://localhost:9134/docs` for Swagger UI
4. Integrate with your existing infrastructure
5. Configure authentication and SSL for production

This template provides a battle-tested, production-ready solution for exposing any MCP server as OpenAPI-compatible REST endpoints.