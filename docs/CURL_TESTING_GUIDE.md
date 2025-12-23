# MCP HTTP Endpoint - Complete curl Testing Guide

This guide shows how to manually test the MCP HTTP streamable transport endpoint using curl commands.

## Quick Start

Run the automated test script:

```bash
./scripts/test-mcp-http.sh
```

Or use the slash command in Claude Code:

```
/test-mcp-http
```

## Manual Testing Steps

### Prerequisites

```bash
# Ensure container is running
docker ps | grep mcp-server-qdrant-http

# Set endpoint URL
MCP_URL="http://localhost:10650/mcp"
```

### Step 1: Initialize Session

**Request:**

```bash
curl -v -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "manual-test",
        "version": "1.0"
      }
    }
  }'
```

**Expected Response:**

```
< HTTP/1.1 200 OK
< mcp-session-id: abc123def456...
< content-type: text/event-stream

event: message
data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05",...}}
```

**Extract Session ID:**

```bash
# From headers (look for 'mcp-session-id:' line)
SESSION_ID="abc123def456..."  # Copy the actual value
```

### Step 2: Send Initialized Notification

**Request:**

```bash
curl -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
```

**Expected Response:**

Silent success (no error response)

### Step 3: List Available Tools

**Request:**

```bash
curl -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
```

**Expected Response:**

```json
event: message
data: {
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {"name": "qdrant_store", "description": "...", "inputSchema": {...}},
      {"name": "qdrant_bulk_store", ...},
      {"name": "qdrant_find", ...},
      {"name": "qdrant_list_collections", ...},
      {"name": "qdrant_collection_info", ...},
      {"name": "qdrant_model_mappings", ...}
    ]
  }
}
```

**Parse Tool Names:**

```bash
curl -s -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | grep -o '"name":"[^"]*"' | cut -d'"' -f4
```

### Step 4: Call qdrant_store Tool

**Request:**

```bash
curl -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "qdrant_store",
      "arguments": {
        "information": "Test document for MCP validation",
        "collection_name": "curl_test",
        "metadata": {
          "test_type": "curl_manual",
          "timestamp": "2025-11-02T12:00:00Z"
        }
      }
    }
  }'
```

**Expected Response:**

```json
event: message
data: {"method":"notifications/message","params":{"level":"debug","data":"Enhanced storing information in collection curl_test"},"jsonrpc":"2.0"}

event: message
data: {
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [{
      "type": "text",
      "text": "Stored in curl_test using all-minilm-l6-v2 (384D): Test document..."
    }],
    "isError": false
  }
}
```

### Step 5: Call qdrant_find Tool

**Request:**

```bash
curl -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "qdrant_find",
      "arguments": {
        "query": "MCP validation",
        "collection_name": "curl_test",
        "limit": 5
      }
    }
  }'
```

**Expected Response:**

```json
event: message
data: {
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\n  \"query\": \"MCP validation\",\n  \"collection\": \"curl_test\",\n  \"results\": [\n    {\n      \"content\": \"Test document for MCP validation\",\n      \"score\": 0.785,\n      \"metadata\": {...},\n      \"vector_model\": \"all-minilm-l6-v2\"\n    }\n  ],\n  \"total_found\": 1\n}"
    }],
    "isError": false
  }
}
```

### Step 6: Other Tool Calls

**List Collections:**

```bash
curl -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "qdrant_list_collections",
      "arguments": {}
    }
  }'
```

**Get Collection Info:**

```bash
curl -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "qdrant_collection_info",
      "arguments": {
        "collection_name": "curl_test"
      }
    }
  }'
```

**Show Model Mappings:**

```bash
curl -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
      "name": "qdrant_model_mappings",
      "arguments": {}
    }
  }'
```

**Bulk Store:**

```bash
curl -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 8,
    "method": "tools/call",
    "params": {
      "name": "qdrant_bulk_store",
      "arguments": {
        "documents": [
          "First test document",
          "Second test document",
          "Third test document"
        ],
        "collection_name": "curl_bulk_test",
        "batch_size": 100
      }
    }
  }'
```

## Common Issues and Solutions

### 406 Not Acceptable

**Problem:**
```
< HTTP/1.1 406 Not Acceptable
```

**Cause:** Missing `text/event-stream` in Accept header

**Solution:**
```bash
# Wrong:
-H "Accept: application/json"

# Correct:
-H "Accept: application/json, text/event-stream"
```

### 400 Bad Request - Missing session ID

**Problem:**
```json
{"jsonrpc":"2.0","error":{"code":-32600,"message":"Bad Request: Missing session ID"}}
```

**Cause:** Missing or incorrect session header

**Solution:**
```bash
# Wrong:
-H "X-Session-Id: abc123"

# Correct:
-H "mcp-session-id: abc123"
```

### Tool Call Before Initialization

**Problem:**
```json
{"jsonrpc":"2.0","error":{"code":-32602,"message":"Invalid request parameters"}}
```

**Cause:** Skipped the `notifications/initialized` step

**Solution:** Always send initialized notification after initialize, before any tool calls

### GET Method Error

**Problem:**
```
< HTTP/1.1 400 Bad Request
```

**Cause:** Using GET instead of POST

**Solution:** All MCP endpoints require POST method

## Response Format

All MCP responses use Server-Sent Events (SSE) format:

```
event: message
data: {JSON-RPC response}
```

To parse in shell scripts:

```bash
# Extract just the JSON data
curl ... | grep "^data: " | sed 's/^data: //'

# Pretty print
curl ... | grep "^data: " | sed 's/^data: //' | python3 -m json.tool
```

## Testing Container Health

```bash
# Check container status
docker ps --filter "name=mcp-server-qdrant-http"

# Check GPU access
docker exec mcp-server-qdrant-http nvidia-smi

# Check CUDA providers
docker exec mcp-server-qdrant-http python3 -c "import onnxruntime as ort; print(ort.get_available_providers())"

# Follow logs
docker logs -f mcp-server-qdrant-http

# Check recent requests
docker logs mcp-server-qdrant-http 2>&1 | grep "POST /mcp" | tail -20
```

## Performance Benchmarking

Time tool execution:

```bash
time curl -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":99,"method":"tools/call","params":{"name":"qdrant_store","arguments":{"information":"Benchmark test","collection_name":"benchmark"}}}'
```

Measure GPU utilization during requests:

```bash
# Terminal 1: Run curl request
curl -X POST $MCP_URL ...

# Terminal 2: Monitor GPU
watch -n 0.1 nvidia-smi
```

## Complete Test Script

Save this as `test-complete.sh`:

```bash
#!/bin/bash
set -e

MCP_URL="http://localhost:10650/mcp"

# Initialize and get session ID
SESSION_ID=$(curl -v -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  2>&1 | grep -i "mcp-session-id:" | awk '{print $3}' | tr -d '\r')

echo "Session ID: $SESSION_ID"

# Send initialized
curl -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

echo "✅ Initialized"

# List tools
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | grep -o '"name":"[^"]*"' | cut -d'"' -f4

echo "✅ Tools listed"

# Test store
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"qdrant_store","arguments":{"information":"Test","collection_name":"test"}}}'

echo "✅ Store test complete"
```

## References

- MCP Protocol Spec: https://spec.modelcontextprotocol.io
- FastMCP Documentation: https://github.com/jlowin/fastmcp
- Qdrant API: https://qdrant.tech/documentation/
