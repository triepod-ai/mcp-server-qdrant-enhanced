# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Enhanced Qdrant MCP Server - A production-ready enhancement of the original mcp-server-qdrant with CUDA 12.x GPU acceleration, multi-vector support (384D/768D/1024D), and collection-specific embedding model selection. This is a sophisticated MCP (Model Context Protocol) server that provides intelligent document storage and retrieval with automatic model optimization, now featuring MCP SDK v1.14.1 and cuDNN 9.13.0 integration.

## Common Development Commands

### Quick Start & Development
```bash
# Setup and first run
make setup              # Interactive setup (NPM or Docker)
./dev setup            # Alternative setup entry point

# Development workflow
make start             # Start server (uses existing deploy.sh)
./dev start            # Alternative start command
make dev               # Development mode with live reloading
./dev dev              # Alternative dev mode

# Container management
./deploy.sh            # Quick deploy (restarts enhanced container)
make stop              # Stop containers
make restart           # Restart containers
make logs              # Follow container logs
```

### Testing & Quality
```bash
# Testing
make test              # Run pytest tests and validation
./dev test             # Alternative test command
./dev quick-test       # Quick MCP functionality validation
pytest tests/          # Direct pytest execution

# Code quality
make lint              # Run ruff formatting and linting
make typecheck         # Run mypy type checking
make ci-test           # Run all CI-style tests (test + lint + typecheck)

# Individual tools
ruff format src/       # Format code
ruff check src/ --fix  # Lint with auto-fix
mypy src/              # Type checking
```

### Container & Build Management
```bash
# Building
make build             # Build Docker image
make rebuild           # Force rebuild (no cache)

# Container operations
docker-compose -f docker-compose.enhanced.yml up -d    # Start enhanced container
docker-compose -f docker-compose.enhanced.yml down     # Stop container
docker-compose -f docker-compose.enhanced.yml logs -f  # Follow logs

# Development utilities
make shell             # Open shell in running container
make status            # Show container status
make clean             # Clean up containers and images
```

## Architecture Overview

### Dual Implementation Strategy
The project maintains both **enhanced** and **legacy** implementations:

- **Enhanced**: `enhanced_*.py` files with GPU acceleration, multi-vector support, collection-specific models
- **Legacy**: Original `*.py` files for backward compatibility
- **Entry Points**: `enhanced_main.py` vs `main.py` for different deployment modes

### Dual Transport Architecture

The server supports two MCP transport modes running simultaneously in separate containers:

#### STDIO Transport (Default)
- **Container**: `mcp-server-qdrant-enhanced`
- **Entry Point**: `enhanced_main.py`
- **Use Case**: Claude Desktop, local MCP clients
- **Communication**: Standard input/output pipes
- **Benefits**: Simple setup, automatic process management

#### Streamable HTTP Transport (New - October 2025)
- **Container**: `mcp-server-qdrant-http`
- **Entry Point**: `enhanced_http_app.py` (ASGI module)
- **Port**: 10650
- **Endpoint**: `/mcp` (GET, POST, DELETE methods)
- **Use Case**: MCP Inspector, remote access, testing
- **Benefits**: HTTP-based access, Inspector compatibility

**Key Files**:
```
src/mcp_server_qdrant/
├── enhanced_server.py          # FastMCP server with tool definitions (shared)
├── enhanced_main.py            # STDIO transport entry point
├── enhanced_http_app.py        # HTTP transport ASGI module
└── enhanced_http_main.py       # Alternative HTTP entry point

Dockerfile.enhanced.cuda        # STDIO container
Dockerfile.enhanced.http        # HTTP container
docker-compose.enhanced.yml     # Orchestrates both containers
```

**Critical Implementation Note**:
The HTTP transport uses `mcp.streamable_http_app()` NOT `mcp.sse_app()`. These are different MCP transports:
- `streamable_http_app()` → `/mcp` endpoint (MCP Inspector compatible) ✅
- `sse_app()` → `/sse` and `/messages` endpoints (different protocol) ❌

Both containers share the same:
- Qdrant database (`localhost:6333` via `host.docker.internal`)
- GPU acceleration and CUDA support
- Collection-specific embedding models
- Tool definitions and schemas

### Core Architecture Components

#### 1. Enhanced Settings System (`enhanced_settings.py`)
- **Collection Model Mappings**: Predefined mappings from collection names to optimal embedding models
- **Model Configurations**: Three tiers of models (384D MiniLM, 768D BGE-Base, 1024D BGE-Large)
- **Auto-Selection Logic**: Intelligent model selection based on content type and collection naming patterns

```python
# Key architecture pattern: Collection → Model → Configuration
COLLECTION_MODEL_MAPPINGS = {
    "legal_analysis": "bge-large-en-v1.5",      # 1024D for complex legal content
    "lessons_learned": "bge-base-en",           # 768D for knowledge-intensive content  
    "working_solutions": "all-minilm-l6-v2",   # 384D for technical solutions (speed)
}
```

#### 2. Enhanced MCP Server (`enhanced_mcp_server.py`)
- **FastMCP Integration**: Built on FastMCP framework with enhanced tool registration
- **Connector Architecture**: Uses `EnhancedQdrantConnector` for collection-specific operations
- **Tool Registration**: Dynamic tool setup with enhanced descriptions and JSON formatting guidance

#### 3. Embedding Pipeline (`embeddings/`)
- **Factory Pattern**: `factory.py` creates appropriate embedding providers
- **Enhanced FastEmbed**: `enhanced_fastembed.py` with GPU acceleration and model routing
- **Type System**: Comprehensive type definitions in `types.py`

#### 4. Enhanced Qdrant Integration (`enhanced_qdrant.py`)
- **Collection Management**: Auto-creation with optimal configurations (quantization, HNSW parameters)
- **Model Routing**: Dynamic embedding model selection per collection
- **Performance Optimization**: Sub-100ms storage with batch support

### Tool Description Architecture
Critical pattern from recent enhancements - tool descriptions are **static documentation** that prevent user errors:

```python
# Pattern: Explicit JSON formatting guidance to prevent backtick/quote errors
description='Store documents with optional metadata. IMPORTANT: Use proper JSON syntax with double quotes (") for all keys and string values, not backticks (`). Example: {"key": "value", "nested": {"data": 123}}'
```

Located in: `docs/TOOL_DESCRIPTIONS.md` for comprehensive documentation of tool description best practices.

## Development Patterns

### Collection-Specific Model Selection
The system automatically routes collections to optimal embedding models:

1. **Legal/Complex Content** → 1024D BGE-Large models (maximum precision)
2. **Knowledge-Intensive Content** → 768D BGE-Base models (balanced performance)  
3. **Technical/Debug Content** → 384D MiniLM models (speed optimized)

### Environment Configuration
Key environment variables for enhanced functionality:
```bash
# Core connection
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=your-collection

# Enhanced features (v1.14.1+)
QDRANT_AUTO_CREATE_COLLECTIONS=true
QDRANT_ENABLE_QUANTIZATION=true
FASTEMBED_CUDA=true

# GPU acceleration (CUDA 12.x + cuDNN 9.13.0)
CUDA_VISIBLE_DEVICES=0
ONNX_CUDA_PROVIDERS=CUDAExecutionProvider,TensorrtExecutionProvider

# HNSW optimization
QDRANT_HNSW_EF_CONSTRUCT=200
QDRANT_HNSW_M=16
```

### Docker Compose Strategy
The project uses `docker-compose.enhanced.yml` with:
- **GPU Runtime**: NVIDIA runtime with device reservations for CUDA 12.x
- **Host Networking**: Direct Qdrant connection on localhost:6333
- **Volume Mounting**: Persistent logs in `./logs/`
- **16.5GB Container**: CUDA 12.x + cuDNN 9.13.0 + embedding models pre-loaded
- **Performance**: 30% improvement in embedding generation (0.019s → 0.013s)

## Key Files & Their Roles

### Core Implementation
- `src/mcp_server_qdrant/enhanced_main.py` - Enhanced server entry point
- `src/mcp_server_qdrant/enhanced_mcp_server.py` - Main server class with tool registration
- `src/mcp_server_qdrant/enhanced_settings.py` - Configuration system with model mappings
- `src/mcp_server_qdrant/enhanced_qdrant.py` - Qdrant connector with collection-specific logic

### Development Infrastructure  
- `./dev` - Unified development entry point script
- `Makefile` - Comprehensive development commands while preserving existing workflow
- `deploy.sh` - Quick deployment script (preserved from original workflow)
- `docker-compose.enhanced.yml` - Production container configuration

### Configuration & Templates
- `package.json` - NPM package metadata with enhanced features documentation
- `pyproject.toml` - Python package configuration with enhanced dependencies
- `templates/configs/` - MCP client configuration templates

### Documentation & Testing
- `docs/TOOL_DESCRIPTIONS.md` - MCP tool description best practices and lessons learned
- `tests/` - Comprehensive test suite for enhanced features
- `README.md` - Extensive documentation with dual installation methods

## Recent Updates (2025-01-25)

### MCP SDK v1.14.1 Upgrade
- **Dependency Update**: Upgraded from MCP SDK v1.3.0 to v1.14.1 in `pyproject.toml`
- **Enhanced Stability**: Improved connection handling and reduced latency
- **Backward Compatibility**: Maintains compatibility with existing MCP clients

### GPU Acceleration Enhancements (2025-11-02)
- **cuDNN 9.13.0**: Successfully installed cuDNN libraries for CUDA 12.x compatibility
- **Performance**: 30% improvement in embedding generation (0.019s → 0.013s)
- **ONNX Runtime**: GPU providers (CUDA, TensorRT) fully functional
- **Stress Testing**: 100% success rate with 500 documents, 18ms average storage time

#### GPU Troubleshooting Guide
**CUBLAS_STATUS_NOT_INITIALIZED Error Fix:**
- **Problem**: `[ONNXRuntimeError] : 1 : FAIL : CUBLAS failure 1: CUBLAS_STATUS_NOT_INITIALIZED`
- **Root Cause**: Using `nvidia/cuda:12.x-runtime-ubuntu22.04` base image (missing cuBLAS dev libraries)
- **Solution**: Switch to `nvidia/cuda:12.x-devel-ubuntu22.04` base image
- **Files**: `Dockerfile.enhanced.cuda`, `Dockerfile.enhanced.http`

**CUDA Provider Not Available Fix:**
- **Problem**: `CUDAExecutionProvider` not in available providers list
- **Root Cause**: Stable PyPI `onnxruntime-gpu` doesn't support CUDA 12.x despite documentation claims
- **Solution**: Install onnxruntime-gpu from nightly builds:
  ```bash
  pip install --pre --index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/ORT-Nightly/pypi/simple/ onnxruntime-gpu
  ```
- **Verification**: `ort.get_available_providers()` should return `['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']`

### Validation Results
- **GPU Detection**: NVIDIA GeForce RTX 3080 Ti with 12GB VRAM confirmed working
- **Search Performance**: 8ms average with 106 queries/second throughput
- **Model Routing**: Collection-specific model selection validated across all dimensions
- **Container Health**: Docker containers running optimally with GPU runtime support

## Development Workflow Preservation

This enhanced version preserves the original development workflow while adding new capabilities:

1. **Existing Commands Work**: `./deploy.sh`, docker-compose commands remain functional
2. **Enhanced Commands Available**: `./dev`, `make` targets provide additional functionality
3. **Backward Compatibility**: Legacy MCP server implementation remains available
4. **Additive Enhancement**: All new features are additions, not replacements
5. **GPU Acceleration**: Optional CUDA support with automatic CPU fallback

## MCP Integration Patterns

### Tool Registration Pattern
```python
# Tools are registered with comprehensive descriptions that prevent user errors
async def qdrant_store(ctx: Context, information: str, collection_name: str, metadata: Metadata = None):
    # Collection-specific model selection happens automatically
    entry = Entry(content=information, metadata=metadata)
    await self.qdrant_connector.store(entry, collection_name=collection_name)
```

### Tool Annotations (Updated: 2025-12-23)

All 9 MCP tools now include comprehensive `ToolAnnotations` to help MCP clients (like Claude) better understand tool behavior and optimize usage patterns.

**Annotation Structure** (from MCP spec):
- `readOnlyHint`: Tool only reads data, doesn't modify state
- `destructiveHint`: Tool may perform irreversible changes
- `idempotentHint`: Repeated calls with same args produce same result
- `openWorldHint`: Tool interacts with external systems vs internal-only operations
- `title`: Human-readable display name

**Tool Annotation Summary**:

| Tool | readOnly | destructive | idempotent | openWorld | Rationale |
|------|----------|-------------|------------|-----------|-----------|
| `qdrant_store` | ❌ | ❌ | ✅ | ❌ | Creates vectors, same content → same embedding, local DB |
| `qdrant_bulk_store` | ❌ | ❌ | ✅ | ❌ | Batch creates, deterministic embeddings, local DB |
| `qdrant_find` | ✅ | ❌ | ✅ | ❌ | Read-only search, returns point_ids, cacheable results, local DB |
| `qdrant_list_collections` | ✅ | ❌ | ✅ | ❌ | Metadata listing, no modifications, local DB |
| `qdrant_collection_info` | ✅ | ❌ | ✅ | ❌ | Collection inspection, no changes, local DB |
| `qdrant_model_mappings` | ✅ | ❌ | ✅ | ❌ | Static config display, in-memory data |
| `qdrant_get_point` | ✅ | ❌ | ✅ | ❌ | Read-only point retrieval by ID, no modifications, local DB |
| `qdrant_update_payload` | ❌ | ❌ | ✅ | ❌ | Updates payload with merge semantics, doesn't destroy, local DB |
| `qdrant_delete_points` | ❌ | **✅** | ✅ | ❌ | PERMANENT deletion, cannot be undone, idempotent (safe to retry) |

**Implementation Pattern**:
```python
from mcp.types import ToolAnnotations

self.tool(
    description="Store information in Qdrant...",
    annotations=ToolAnnotations(
        readOnlyHint=False,      # Modifies database
        destructiveHint=False,   # Creates, doesn't destroy
        idempotentHint=True,     # Same content → same embedding
        openWorldHint=False      # Local Qdrant instance
    )
)(qdrant_store)
```

**Benefits**:
- **Better UX**: MCP clients can optimize tool usage based on behavior hints
- **Caching**: Read-only + idempotent tools can be safely cached
- **Retry Logic**: Idempotent operations can be automatically retried on failure
- **UI Presentation**: Clients can show appropriate warnings for destructive operations

**Security Note**: Per MCP spec, annotations are hints only and should not be used for security-critical decisions. Always obtain explicit user consent before tool invocation.

### Key Lesson: Nested Payload Updates (2025-12-23)

The `qdrant_update_payload` tool has a critical `key` parameter for nested structures:

```
Qdrant Payload Structure:
payload
├── document: "{ content... }"
└── metadata
    ├── sync_status: "pending"
    ├── synced_to_asana: false
    └── ... other fields
```

| `key` value | Update target | Use when |
|-------------|---------------|----------|
| `None` | Root payload | Updating `payload.field` directly |
| `"metadata"` | Nested metadata | Updating `payload.metadata.field` |

**Example**: To update `payload.metadata.sync_status`:
```python
qdrant_update_payload(
    point_ids=["abc..."],
    payload={"sync_status": "synced"},
    collection_name="session_work_logs",
    key="metadata"  # REQUIRED - without this, creates payload.sync_status instead!
)
```

### Client Configuration
The server supports multiple MCP clients through dual transport (stdio/sse) and provides template configurations for:
- Claude Desktop (`claude_desktop_config.json`)
- VS Code (`cline_mcp_settings.json`)
- Cursor/Windsurf (SSE transport)

### MCP HTTP Protocol Requirements (2025-11-02)

Critical protocol requirements discovered during local testing validation:

#### HTTP Headers
```bash
# REQUIRED: Both content types must be in Accept header
Accept: application/json, text/event-stream

# REQUIRED: Session ID header (not X-Session-Id)
mcp-session-id: <session-id-from-initialize>
```

#### Session Initialization Sequence
```bash
# 1. Initialize session (creates new session ID)
POST /mcp
Headers: Accept: application/json, text/event-stream
Body: {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {...}}
Response: Returns session ID in response

# 2. Send initialized notification (REQUIRED before tool calls)
POST /mcp
Headers:
  Accept: application/json, text/event-stream
  mcp-session-id: <session-id>
Body: {"jsonrpc": "2.0", "method": "notifications/initialized"}

# 3. Now tool calls will work
POST /mcp
Headers:
  Accept: application/json, text/event-stream
  mcp-session-id: <session-id>
Body: {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
```

#### Common Errors
- **406 Not Acceptable**: Missing `text/event-stream` in Accept header
- **400 Bad Request "Missing session ID"**: Missing or incorrect `mcp-session-id` header
- **-32602 "Invalid request parameters"**: Tool called before `notifications/initialized` sent

#### Testing Pattern
```bash
# Local server testing outside container
source .venv/bin/activate
uvicorn mcp_server_qdrant.enhanced_http_app:app --host 127.0.0.1 --port 10651

# Test session flow
curl -X POST http://127.0.0.1:10651/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0"}}}'
```

#### Known Issues vs Working Features
**Working ✅**:
- MCP HTTP protocol implementation
- Session management with `mcp-session-id` header
- All 6 MCP tools (store, bulk_store, find, list_collections, collection_info, model_mappings)
- Local server testing (port 10651)
- GPU acceleration (30% improvement in embeddings)
- Collection auto-creation with model selection

**Known Issue 🔧**:
- Container HTTP timeout on port 10650 (transport/networking layer issue, NOT core MCP functionality)
- Core MCP server works perfectly - issue is container-specific networking/resource constraints
- Direct Python API calls work fine in container
- Local server (outside container) works perfectly with same code

## Performance & Production Considerations

- **GPU Acceleration**: Requires NVIDIA CUDA 12.x runtime for optimal performance
- **Model Loading**: 16.5GB container includes CUDA runtime + cuDNN + pre-loaded embedding models
- **Collection Auto-Creation**: Collections are created with optimal HNSW and quantization settings
- **Caching Strategy**: Sub-100ms storage with intelligent model reuse
- **Production Scale**: Validated with 48 active collections in production environments

## Testing Strategy

Run tests frequently during development:
```bash
make ci-test           # Complete CI-style validation
./dev quick-test       # Fast MCP functionality validation
pytest tests/test_settings.py -v  # Specific test file
```

The test suite covers enhanced settings, Qdrant integration, FastEmbed embedding, and validators with both unit and integration test patterns.

### Local MCP Server Testing (2025-11-02)

For testing MCP HTTP transport outside Docker containers:

```bash
# 1. Start local server on alternate port
source .venv/bin/activate
uvicorn mcp_server_qdrant.enhanced_http_app:app --host 127.0.0.1 --port 10651 > /tmp/mcp_local_test.log 2>&1 &

# 2. Test session initialization
curl -X POST http://127.0.0.1:10651/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0"}}}'

# 3. Extract session ID from response, send initialized notification
curl -X POST http://127.0.0.1:10651/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: <session-id>" \
  -d '{"jsonrpc": "2.0", "method": "notifications/initialized"}'

# 4. Test tool calls (list, store, find)
curl -X POST http://127.0.0.1:10651/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: <session-id>" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}'
```

**Validation Results (2025-11-02)**:
- ✅ Session initialization working (HTTP 200 OK)
- ✅ All 6 MCP tools returned from tools/list
- ✅ qdrant_store tool call successful (stored document with 384D embeddings)
- ✅ qdrant_find tool call successful (retrieved with score 0.57)
- ✅ Collection auto-creation working (local_test collection)
- ✅ Model selection working (all-minilm-l6-v2 for technical content)

**Local Environment Notes**:
- Python 3.11.2 with virtual environment (.venv)
- ONNX Runtime 1.21.0 (CPU-only on host, no GPU support in venv)
- NVIDIA RTX 3080 Ti detected but CUDA providers not available in local venv
- For GPU testing, use Docker containers with CUDA runtime

## Documentation Guidelines

For comprehensive project context and guidance, reference these documentation files:

### Recent Documentation Updates
- **[Streamable HTTP Transport](./README.md#-transport-options)** - Added dual transport support with MCP Inspector compatibility (Added: 2025-10-03)
  - New `enhanced_http_app.py` for streamable HTTP transport
  - Docker container on port 10650 with `/mcp` endpoint
  - Complete MCP Inspector integration guide
  - SSE vs Streamable HTTP implementation notes
  - Lessons learned stored in both Chroma (`mcp_integration_patterns`) and Qdrant (`mcp_streamable_http_patterns`)
- [PROJECT_STATUS.md](./PROJECT_STATUS.md) - Project development progress and session history tracking (Added: 2025-01-23)