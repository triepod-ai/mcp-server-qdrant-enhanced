#!/bin/bash

# Quick Deploy Script for Enhanced Qdrant MCP Server
# Restarts the enhanced MCP server with proper 768D BGE-Base configurations

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project directory (auto-detect from script location)
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "$0")" && pwd)}"

echo -e "${BLUE}🚀 Deploying Enhanced Qdrant MCP Server...${NC}"

# Navigate to project directory
echo -e "${BLUE}📁 Changing to project directory: ${PROJECT_DIR}${NC}"
cd "${PROJECT_DIR}"

# Stop current container
echo -e "${BLUE}⏹️  Stopping current MCP server container...${NC}"
if docker-compose -f docker-compose.enhanced.yml down; then
    echo -e "${GREEN}✅ Container stopped successfully${NC}"
else
    echo -e "${YELLOW}⚠️  No container was running${NC}"
fi

# Start enhanced container
echo -e "${BLUE}🔄 Starting enhanced MCP server container...${NC}"
if docker-compose -f docker-compose.enhanced.yml up -d; then
    echo -e "${GREEN}✅ Enhanced MCP server started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start container${NC}"
    exit 1
fi

# Verify container is running
echo -e "${BLUE}🔍 Verifying container status...${NC}"
if docker ps | grep -q "mcp-server-qdrant-enhanced"; then
    echo -e "${GREEN}✅ Container is running${NC}"
    docker ps | grep "mcp-server-qdrant-enhanced"
else
    echo -e "${RED}❌ Container failed to start${NC}"
    exit 1
fi

echo
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Restart Claude Code to load enhanced configuration"
echo "2. Test collections will now use correct 768D BGE-Base models:"
echo "   • contextual_knowledge"
echo "   • triepod-documentation" 
echo "   • development_patterns"
echo
echo -e "${BLUE}🔧 Verification Commands:${NC}"
echo "• Check model mappings: Use MCP tool qdrant_model_mappings"
echo "• Test collection: Use MCP tool qdrant_collection_info"
echo
echo -e "${YELLOW}💡 Remember: Collections created after this deployment will automatically use the correct enhanced configurations!${NC}"