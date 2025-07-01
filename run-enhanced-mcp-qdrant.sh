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
exec python -u -m mcp_server_qdrant.main --transport stdio
