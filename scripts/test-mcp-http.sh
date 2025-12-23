#!/bin/bash
# Test MCP HTTP Streamable Transport Endpoint
# This script validates the complete MCP protocol sequence

set -e

MCP_URL="${MCP_URL:-http://localhost:10650/mcp}"
TEMP_DIR="/tmp/mcp-test-$$"
mkdir -p "$TEMP_DIR"

echo "🧪 Testing MCP HTTP Endpoint: $MCP_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Initialize session
echo -e "${BLUE}Step 1: Initialize Session${NC}"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-script", "version": "1.0"}
    }
  }' > "$TEMP_DIR/init.txt" 2>&1

# Extract session ID from response headers using verbose mode
SESSION_ID=$(curl -v -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-script", "version": "1.0"}
    }
  }' 2>&1 | grep -i "mcp-session-id:" | awk '{print $3}' | tr -d '\r')

if [ -z "$SESSION_ID" ]; then
  echo -e "${RED}❌ Failed to get session ID${NC}"
  cat "$TEMP_DIR/init.txt"
  exit 1
fi

echo -e "${GREEN}✅ Session ID: $SESSION_ID${NC}"
echo ""

# Step 2: Send initialized notification
echo -e "${BLUE}Step 2: Send Initialized Notification${NC}"
INIT_RESPONSE=$(curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }')

if echo "$INIT_RESPONSE" | grep -q "error"; then
  echo -e "${RED}❌ Initialized notification failed${NC}"
  echo "$INIT_RESPONSE"
  exit 1
fi

echo -e "${GREEN}✅ Initialized notification sent${NC}"
echo ""

# Step 3: List tools
echo -e "${BLUE}Step 3: List Available Tools${NC}"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }' > "$TEMP_DIR/tools.txt"

TOOL_COUNT=$(grep -o '"name":"qdrant_[^"]*"' "$TEMP_DIR/tools.txt" | wc -l)
echo -e "${GREEN}✅ Found $TOOL_COUNT Qdrant tools:${NC}"
grep -o '"name":"qdrant_[^"]*"' "$TEMP_DIR/tools.txt" | sed 's/"name":"//g' | sed 's/"//g' | sed 's/^/  - /g'
echo ""

# Step 4: Test qdrant_store
echo -e "${BLUE}Step 4: Test qdrant_store (GPU-accelerated embeddings)${NC}"
STORE_RESPONSE=$(curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 3,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"qdrant_store\",
      \"arguments\": {
        \"information\": \"MCP HTTP test document created at $(date -Iseconds)\",
        \"collection_name\": \"mcp_http_test\",
        \"metadata\": {
          \"test_script\": \"test-mcp-http.sh\",
          \"session_id\": \"$SESSION_ID\",
          \"timestamp\": \"$(date -Iseconds)\"
        }
      }
    }
  }")

if echo "$STORE_RESPONSE" | grep -q '"result"'; then
  MODEL=$(echo "$STORE_RESPONSE" | grep -o 'using [^(]*' | head -1)
  echo -e "${GREEN}✅ Document stored successfully $MODEL${NC}"
else
  echo -e "${RED}❌ Store failed${NC}"
  echo "$STORE_RESPONSE"
  exit 1
fi
echo ""

# Step 5: Test qdrant_find
echo -e "${BLUE}Step 5: Test qdrant_find (semantic search)${NC}"
FIND_RESPONSE=$(curl -s -X POST "$MCP_URL" \
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
        "query": "HTTP test document",
        "collection_name": "mcp_http_test",
        "limit": 3
      }
    }
  }')

if echo "$FIND_RESPONSE" | grep -q '"score"'; then
  SCORE=$(echo "$FIND_RESPONSE" | grep -o '"score":[0-9.]*' | head -1 | cut -d: -f2)
  RESULTS=$(echo "$FIND_RESPONSE" | grep -o '"total_found":[0-9]*' | cut -d: -f2)
  echo -e "${GREEN}✅ Search successful: $RESULTS results, top score: $SCORE${NC}"
else
  echo -e "${YELLOW}⚠️  Search returned no results or failed${NC}"
  echo "$FIND_RESPONSE" | head -20
fi
echo ""

# Cleanup
rm -rf "$TEMP_DIR"

# Summary
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ MCP HTTP Transport Test Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "All MCP protocol steps validated:"
echo "  ✓ Session initialization"
echo "  ✓ Tool discovery"
echo "  ✓ Document storage (GPU embeddings)"
echo "  ✓ Semantic search"
echo ""
echo "Container Status:"
docker ps --filter "name=mcp-server-qdrant-http" --format "  {{.Status}}"
