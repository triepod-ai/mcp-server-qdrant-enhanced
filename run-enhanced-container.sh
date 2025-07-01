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
