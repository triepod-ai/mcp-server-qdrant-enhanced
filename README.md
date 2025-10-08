# Enhanced Qdrant MCP Server

[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue)](https://github.com/triepod-ai/mcp-server-qdrant-enhanced/pkgs/container/mcp-server-qdrant-enhanced)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![GitHub Actions](https://github.com/triepod-ai/mcp-server-qdrant-enhanced/workflows/Build%20and%20Publish/badge.svg)](https://github.com/triepod-ai/mcp-server-qdrant-enhanced/actions)
[![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-green.svg)](https://developer.nvidia.com/cuda-downloads)

> **🚀 Production-Ready Enhancement** of the original [mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant) with GPU acceleration, multi-vector support, and enterprise-grade deployment infrastructure.

**Enhanced Model Context Protocol server** for [Qdrant](https://qdrant.tech/) vector database with advanced features including GPU acceleration, collection-specific embedding models, and production deployment automation.

## 🌟 Why This Enhanced Version?

This fork transforms the basic MCP server into a **production-ready solution** with:

- **🚀 30% Performance Improvement**: GPU acceleration with FastEmbed and CUDA 12.x support
- **🧠 Smart Model Selection**: Automatic 384D/768D/1024D embedding selection based on collection type
- **🐳 Production Infrastructure**: Complete Docker automation with pre-configured CUDA environment
- **📦 Docker-First Distribution**: GPU acceleration requires Docker (CUDA + cuDNN + models = 16.5GB)
- **⚡ Zero-Config GPU Setup**: All dependencies pre-installed in container
- **🔄 48 Production Collections**: Battle-tested with real workloads

## MCP SDK Version

**Current Version**: Python MCP SDK 1.15.0 (upgraded October 1, 2025)

This server uses the latest Model Context Protocol SDK with enhanced features:
- Paginated list decorators for prompts, resources, and tools
- Protected resource metadata improvements
- Enhanced security with HTTP 403 for invalid Origin headers
- Default values in elicitation schemas
- Additional metadata and icon support

**Previous Version**: 1.14.1 → **Upgrade Jump**: Minor version update with new protocol features

For complete MCP protocol documentation, see [Model Context Protocol](https://modelcontextprotocol.io/).

## Overview

An enhanced Model Context Protocol server for keeping and retrieving memories in the Qdrant vector search engine with **structured data returns**, **TypeScript-inspired type validation**, **collection-specific embedding models**, and **optimized 768D career collections**.

### ✨ Enhanced Features

- **🎯 Structured Data Returns**: JSON objects instead of formatted strings for better programmatic access
- **🛡️ Type Safety**: TypeScript-inspired type guards and comprehensive validation
- **📊 Score-Based Filtering**: Relevance thresholds and result ranking
- **🔄 Retry Logic**: Exponential backoff for robust error handling
- **🎨 Multi-Vector Support**: Collection-specific embedding models (384D/768D/1024D)
- **⚡ GPU Acceleration**: CUDA-enabled FastEmbed with 30% performance improvement (0.019s → 0.013s)
- **🚀 MCP SDK v1.14.1**: Latest Model Context Protocol support with enhanced stability
- **🔧 cuDNN Integration**: Full CUDA 12.x compatibility with cuDNN 9.13.0
- **📈 Production Validated**: 100% success rate with 500-document stress testing
- **🔒 Safe Migration**: Zero data loss migration with comprehensive backup strategies

### 📈 Performance Metrics (Latest v1.14.1 + CUDA 12.x)

**GPU-Accelerated Performance:**
- **Embedding Generation:** 12-13ms per document (30% improvement over previous versions)
- **Storage Operations:** 18-95ms depending on model complexity (100% success rate with 500 documents)
- **Search Performance:** Sub-50ms with optimized HNSW indexing
- **MCP SDK:** v1.14.1 with enhanced stability and reduced latency

**Collection-Specific Performance (Validated):**
- **Technical Documents:** ~18ms with 384D embeddings (speed-optimized for fast retrieval)
- **Knowledge Base:** ~560ms with 768D embeddings (balanced precision/performance)
- **Legal Documents:** ~2350ms with 1024D embeddings (maximum precision for complex content)

> **📊 Benchmark Methodology**: Performance metrics based on validated testing with NVIDIA RTX 3080 Ti (12GB VRAM). See [VALIDATION_REPORT.md](VALIDATION_REPORT.md) for detailed benchmark results and methodology. Performance varies by hardware, workload, and model selection.

**System Requirements:**
- **CUDA:** Version 12.x with cuDNN 9.13.0 for optimal GPU acceleration
- **GPU Memory:** 12GB+ VRAM recommended for large document processing
- **Stress Tested:** 100% success rate across 500 documents with zero failures

## 🚀 Quick Start

**⚠️ GPU Acceleration Requires Docker**: This enhanced version's 30% performance improvement comes from GPU acceleration with CUDA 12.x and cuDNN 9.13.0. These dependencies (16.5GB) are pre-installed in the Docker image. Manual installation of CUDA/cuDNN is complex and error-prone.

### 🐳 Docker Installation (Recommended - GPU-Accelerated)

The only practical way to get full GPU acceleration:

```bash
# Pull the pre-built image (16.5GB with CUDA, cuDNN, and embedding models)
docker pull ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest

# Run with GPU support (requires NVIDIA Docker runtime)
docker run -it --rm \
  --gpus all \
  --network host \
  -e QDRANT_URL="http://localhost:6333" \
  -e COLLECTION_NAME="enhanced-collection" \
  -e FASTEMBED_CUDA="true" \
  ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest

# Or use Docker Compose for persistent setup
curl -sSL https://raw.githubusercontent.com/triepod-ai/mcp-server-qdrant-enhanced/main/docker-compose.enhanced.yml -o docker-compose.yml
docker-compose -f docker-compose.enhanced.yml up -d
```

**Requirements:**
- Docker with NVIDIA runtime (for GPU acceleration)
- NVIDIA GPU with CUDA 12.x support
- Running Qdrant instance (localhost:6333)
- 16.5GB disk space for image

**What you get:**
- ✅ CUDA 12.x runtime pre-configured
- ✅ cuDNN 9.13.0 libraries installed
- ✅ All embedding models pre-downloaded
- ✅ 30% faster embedding generation (13ms vs 19ms)
- ✅ Zero configuration required

### 🔧 Development Setup (CPU-Only, Without GPU)

For developers who want to modify code but **won't get GPU acceleration**:

```bash
# Clone and setup with uv package manager
git clone https://github.com/triepod-ai/mcp-server-qdrant-enhanced.git
cd mcp-server-qdrant-enhanced

# Install dependencies
uv pip install -e .

# Run in CPU mode (much slower than Docker GPU version)
QDRANT_URL="http://localhost:6333" COLLECTION_NAME="test" python -m mcp_server_qdrant.enhanced_main --transport stdio
```

**Note:** CPU mode is ~3x slower than GPU-accelerated Docker version. Use this only for development/testing code changes.

### 🔧 Claude Desktop Integration

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

**Using Docker (GPU-accelerated):**
```json
{
  "mcpServers": {
    "qdrant-enhanced": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--gpus", "all",
        "--network", "host",
        "-e", "QDRANT_URL=http://localhost:6333",
        "-e", "COLLECTION_NAME=your-collection",
        "-e", "FASTEMBED_CUDA=true",
        "ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest"
      ]
    }
  }
}
```

**Using CPU mode (development only, ~3x slower):**
```json
{
  "mcpServers": {
    "qdrant-dev": {
      "command": "uvx",
      "args": ["mcp-server-qdrant"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "your-collection"
      }
    }
  }
}
```

**Note:** CPU mode uses the original unenhanced package from PyPI. For GPU acceleration and enhanced features, use Docker.

---

## 🔌 Transport Options

The Enhanced Qdrant MCP Server supports two transport modes for different use cases:

### STDIO Transport (Default)

**Use Case**: Direct integration with MCP clients like Claude Desktop, VS Code extensions
**Benefits**: Simple setup, automatic process management, secure local communication
**Recommended For**: Development, Claude Desktop, local MCP clients

```bash
# Using Docker with GPU acceleration (recommended)
docker-compose -f docker-compose.enhanced.yml up -d mcp-server-enhanced

# Or run directly
docker run -i --rm --gpus all --network host \
  -e QDRANT_URL="http://localhost:6333" \
  -e COLLECTION_NAME="your-collection" \
  ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest
```

**Claude Desktop Configuration**:
```json
{
  "qdrant-enhanced": {
    "command": "docker",
    "args": [
      "run", "-i", "--rm",
      "--gpus", "all",
      "--network", "host",
      "-e", "QDRANT_URL=http://localhost:6333",
      "-e", "COLLECTION_NAME=your-collection",
      "ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest"
    ]
  }
}
```

### Streamable HTTP Transport (New!)

**Use Case**: MCP Inspector testing, remote connections, web-based clients
**Benefits**: HTTP-based access, MCP Inspector compatibility, network accessibility
**Recommended For**: Testing, debugging, MCP Inspector, remote access

```bash
# Using Docker with HTTP transport
docker-compose -f docker-compose.enhanced.yml up -d mcp-server-qdrant-http
```

**MCP Inspector Connection**:
- **URL**: `http://localhost:10650/mcp`
- **Transport Type**: `streamable-http`

**Features**:
- ✅ Full MCP protocol support with proper tool schemas
- ✅ Compatible with MCP Inspector for interactive testing
- ✅ Runs on port 10650 with GET, POST, DELETE methods
- ✅ StreamableHTTP session management
- ✅ Same GPU acceleration and model selection as STDIO transport

**Connection Verification**:
```bash
# Check container is running
docker ps --filter name=mcp-server-qdrant-http

# View logs for StreamableHTTP session manager confirmation
docker logs mcp-server-qdrant-http --tail 20
# Look for: "StreamableHTTP session manager started"

# Test endpoint
curl -I http://localhost:10650/mcp
# Expected: HTTP/1.1 405 with Allow: GET, POST, DELETE
```

### Dual Transport Setup

Both transports can run simultaneously in separate containers:

```bash
# Start both STDIO and HTTP containers
docker-compose -f docker-compose.enhanced.yml up -d

# Verify both are running
docker ps --filter name=mcp-server-qdrant
```

This allows you to:
- Use STDIO transport for Claude Desktop integration
- Use HTTP transport for MCP Inspector testing
- Both share the same Qdrant database at `localhost:6333`

### Transport Comparison

| Feature | STDIO Transport | HTTP Transport |
|---------|----------------|----------------|
| **Primary Use** | Local MCP clients | Remote access, testing |
| **Claude Desktop** | ✅ Recommended | ❌ Not supported |
| **MCP Inspector** | ❌ Not compatible | ✅ Fully supported |
| **Network Access** | Local only | HTTP accessible |
| **Port** | N/A (stdio pipes) | 10650 |
| **Endpoint** | N/A | `/mcp` |
| **Session Management** | Process-based | HTTP session-based |
| **Setup Complexity** | Simple | Moderate |
| **GPU Acceleration** | ✅ Full support | ✅ Full support |
| **Model Selection** | ✅ All models | ✅ All models |

### Important Implementation Notes

#### SSE vs Streamable HTTP
⚠️ **Critical**: `mcp.sse_app()` ≠ `mcp.streamable_http_app()`

These are **different MCP transports** with different endpoints:
- **SSE Transport**: `/sse` and `/messages` endpoints (not MCP Inspector compatible)
- **Streamable HTTP**: `/mcp` endpoint (MCP Inspector compatible)

**Correct Implementation** (see `enhanced_http_app.py`):
```python
from mcp_server_qdrant.enhanced_server import mcp

# ✅ CORRECT: For MCP Inspector and streamable HTTP clients
app = mcp.streamable_http_app()

# ❌ WRONG: Creates incompatible SSE endpoints
# app = mcp.sse_app()  # Don't use this!
```

For complete implementation details and troubleshooting, see the comprehensive guide in:
- Chroma collection: `mcp_integration_patterns`
- Qdrant collection: `mcp_streamable_http_patterns`

---

## Components

### Tools

1. `qdrant-store`
   - Store information with automatic collection-specific embedding model selection
   - Input:
     - `information` (string): Information to store
     - `metadata` (JSON): Optional metadata to store with validation
     - `collection_name` (string): Collection name (required if no default)
   - Returns: Confirmation with model info (`"Stored in collection using model (dimensions): content"`)

2. `qdrant-find` **[Enhanced with Structured Returns]**
   - Retrieve relevant information with structured results and filtering
   - Input:
     - `query` (string): Search query with automatic sanitization
     - `collection_name` (string): Collection name (required if no default)
     - `limit` (integer, optional): Maximum results to return (default: 10)
     - `score_threshold` (float, optional): Minimum relevance score (default: 0.0)
   - Returns: **Structured JSON response**:
     ```json
     {
       "query": "search terms",
       "collection": "collection_name",
       "results": [
         {
           "content": "document content",
           "score": 0.95,
           "metadata": {"key": "value"},
           "collection": "collection_name", 
           "vector_model": "bge-large-en-v1.5"
         }
       ],
       "total_found": 1,
       "search_params": {"limit": 10, "score_threshold": 0.0},
       "timestamp": "2025-01-15T10:30:00Z"
     }
     ```

3. `qdrant-list-collections` **[New]**
   - List all collections with configuration details
   - Returns: Formatted collection info with vector dimensions and models

4. `qdrant-collection-info` **[New]**
   - Get detailed information about a specific collection
   - Input: `collection_name` (string)
   - Returns: Comprehensive collection details including optimization status

5. `qdrant-model-mappings` **[New]**
   - Show current collection-to-model mappings and available configurations
   - Returns: Model mapping configuration and available options

## 🎯 Collection-Specific Embedding Models

This server automatically selects optimal embedding models based on collection names:

### 🏆 Career Collections (768D BGE-Base Models)
- **`resume_projects`**: Portfolio and resume content using BAAI/bge-base-en (768D)
- **`job_search`**: Job applications and career materials using BAAI/bge-base-en (768D)  
- **`mcp-optimization-knowledge`**: Technical optimization knowledge using BAAI/bge-base-en (768D)
- **`project_achievements`**: Career accomplishments using BAAI/bge-base-en (768D)

### 🔬 Legal & Workplace (1024D BGE-Large Models)
- **`legal_analysis`**: Complex legal content using BAAI/bge-large-en-v1.5 (1024D)
- **`workplace_documentation`**: Business and workplace docs using BAAI/bge-base-en-v1.5 (768D)

### 🎵 Media & Knowledge Content (768D BGE-Base Models)
- **`music_videos`**: Video content and metadata using BAAI/bge-base-en (768D)

### ⚡ Technical Collections (384D MiniLM Models)
- **`working_solutions`**: Quick technical solutions using sentence-transformers/all-MiniLM-L6-v2 (384D)
- **`debugging_patterns`**: Debug patterns using sentence-transformers/all-MiniLM-L6-v2 (384D)
- **`troubleshooting`**: General troubleshooting and technical issues using sentence-transformers/all-MiniLM-L6-v2 (384D)
- **Default collections**: Use 384D MiniLM for speed and efficiency

### 📊 Search Quality Improvements
Recent migration to optimized models achieved **0.75-0.82 search scores** for career content, representing significant quality improvements over generic embeddings.

## 🚀 Migration from Legacy Version

**Breaking Change Notice**: The `qdrant-find` tool now returns structured JSON instead of formatted strings.

### Quick Migration Guide

**Before (Legacy)**:
```python
results = await qdrant_find(ctx, "query", "collection")
# Returns: ["Results for query 'query'", "<entry><content>...</content></entry>"]
```

**After (Enhanced)**:
```python
response = await qdrant_find(ctx, "query", "collection", score_threshold=0.7)
# Returns: {"query": "query", "results": [{"content": "...", "score": 0.95, ...}], ...}

# Direct access to structured data
for result in response["results"]:
    content = result["content"]
    score = result["score"] 
    metadata = result["metadata"]
```

📖 **[Complete Migration Guide](docs/MIGRATION_GUIDE.md)** | 💡 **[Usage Examples](examples/enhanced_usage.py)**

## 🏆 What Makes This Enhancement Special

### ✅ Enterprise-Grade Performance
- **GPU Acceleration**: FastEmbed with CUDA support for 30% faster embedding generation
- **Smart Model Selection**: Collection-specific routing to optimal 384D/768D/1024D models
- **Quantization Optimized**: 40% memory reduction while maintaining search quality
- **Production Validated**: Sub-second response times across 48 active collections

### 🔧 Advanced Architecture
- **Separation of Concerns**: MCP server (16.5GB with CUDA + models) + Qdrant DB (279MB storage)
- **Multi-Vector Support**: Automatic model selection based on collection naming patterns
- **Zero-Config Deployment**: Interactive setup with platform detection and validation
- **CI/CD Automation**: GitHub Actions with multi-architecture builds and security scanning

### 📊 Real-World Results
- **Search Quality**: Achieved 0.75-0.82 scores for career content (major improvement over generic embeddings)
- **Production Scale**: 48 active collections with zero data loss migrations
- **Developer Experience**: One-command setup, dual installation methods, comprehensive documentation

## Environment Variables

The configuration of the server is done using environment variables:

| Name                          | Description                                                         | Default Value                                                     |
|-------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------|
| `QDRANT_URL`                  | URL of the Qdrant server                                            | None                                                              |
| `QDRANT_API_KEY`              | API key for the Qdrant server                                       | None                                                              |
| `COLLECTION_NAME`             | Name of the default collection to use                               | None                                                              |
| `QDRANT_LOCAL_PATH`           | Path to the local Qdrant database (alternative to `QDRANT_URL`)     | None                                                              |
| `EMBEDDING_PROVIDER`          | Embedding provider to use (currently only "fastembed" is supported) | `fastembed`                                                       |
| `EMBEDDING_MODEL`             | Name of the embedding model to use (overridden by collection mappings) | `sentence-transformers/all-MiniLM-L6-v2`                          |
| `QDRANT_AUTO_CREATE_COLLECTIONS` | **[Enhanced]** Auto-create collections with optimal settings    | `true`                                                            |
| `QDRANT_ENABLE_QUANTIZATION`  | **[Enhanced]** Enable vector quantization for memory optimization   | `true`                                                            |
| `COLLECTION_MODEL_MAPPINGS`   | **[Enhanced]** JSON mapping of collections to specific embedding models | Auto-configured based on collection names                         |
| `QDRANT_SEARCH_LIMIT`         | **[Enhanced]** Default maximum search results                       | `10`                                                              |
| `QDRANT_HNSW_EF_CONSTRUCT`    | **[Enhanced]** HNSW ef_construct parameter                          | `128`                                                             |
| `QDRANT_HNSW_M`               | **[Enhanced]** HNSW M parameter                                     | `16`                                                              |
| `FASTEMBED_CUDA`              | **[New v1.14.1]** Enable CUDA GPU acceleration for embeddings      | `true` (when GPU available)                                       |
| `CUDA_VISIBLE_DEVICES`        | **[New v1.14.1]** Specify GPU devices for CUDA acceleration        | `0` (first GPU)                                                   |
| `TOOL_STORE_DESCRIPTION`      | Custom description for the store tool                               | See default in [`settings.py`](src/mcp_server_qdrant/settings.py) |
| `TOOL_FIND_DESCRIPTION`       | Custom description for the find tool                                | See default in [`settings.py`](src/mcp_server_qdrant/settings.py) |

Note: You cannot provide both `QDRANT_URL` and `QDRANT_LOCAL_PATH` at the same time.

> [!IMPORTANT]
> Command-line arguments are not supported anymore! Please use environment variables for all configuration.

## Installation Options

### Why Docker is Required for GPU Acceleration

The enhanced version's main value proposition is **30% performance improvement from GPU acceleration**. This requires:

- **CUDA 12.x Runtime** (~5GB) - Complex installation, OS-specific
- **cuDNN 9.13.0 Libraries** (~2GB) - Requires NVIDIA account, manual download
- **Embedding Models** (~3-4GB) - Pre-downloaded for immediate use
- **Proper LD_LIBRARY_PATH** - Environment configuration
- **GPU Driver Compatibility** - Must match CUDA version

**Docker Pre-Packages Everything**: All dependencies, configurations, and models in one 16.5GB image that works out of the box.

### Installation Methods

1. **🐳 [Docker Container](#-docker-installation-recommended---gpu-accelerated)** - Primary method for GPU acceleration
2. **🔧 [Development Setup](#-development-setup-cpu-only-without-gpu)** - For code modifications (CPU-only, ~3x slower)

### Traditional Docker Compose Setup

For users who prefer manual Docker Compose configuration without the automated setup:

**Prerequisites:**
- Docker and Docker Compose installed.
- An existing Qdrant instance (either local or remote).

**Configuration:**
    *   Create a `.env` file to manage environment variables:

        ```dotenv
        # .env file
        QDRANT_URL=http://host.docker.internal:6333
        COLLECTION_NAME=my-collection
        MCP_TRANSPORT=sse
        HOST_PORT=8002
        # QDRANT_API_KEY=YOUR_API_KEY # Uncomment and set if your Qdrant requires authentication
        # EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 # Optional: Overrides the default model
        ```

    **Important**: Use `host.docker.internal:6333` instead of `localhost:6333` for Docker networking.

3.  **Platform-specific Setup:**

    **Windows/macOS (Docker Desktop):**
    ```bash
    docker-compose up -d
    ```

    **Linux (host networking):**
    ```bash
    docker-compose -f docker-compose.linux.yml up -d
    ```

4.  **Testing the Deployment:**
    ```bash
    ./test-docker-deployment.sh
    ```

5.  **Stopping the Server:**
    ```bash
    docker-compose down
    ```

### Installing via Smithery

To install Qdrant MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/protocol/mcp-server-qdrant):

```bash
npx @smithery/cli install mcp-server-qdrant --client claude
```

> **⚠️ Note**: Smithery installs the **original unenhanced package** from PyPI (CPU-only, no GPU acceleration). For the enhanced version with 30% performance improvement, use the [Docker installation method](#-docker-installation-recommended---gpu-accelerated) above.

### Manual configuration of Claude Desktop

To use this server with the Claude Desktop app, add the following configuration to the "mcpServers" section of your
`claude_desktop_config.json`:

#### Docker Deployment (Recommended)

After running the enhanced setup script, use this configuration:

```json
{
  "qdrant-enhanced": {
    "command": "mcp-server-qdrant-enhanced",
    "args": ["--transport", "stdio"],
    "env": {
      "QDRANT_URL": "http://localhost:6333",
      "COLLECTION_NAME": "your-collection"
    }
  }
}
```

#### Legacy uvx Deployment (Deprecated)

```json
{
  "qdrant": {
    "command": "uvx",
    "args": ["mcp-server-qdrant"],
    "env": {
      "QDRANT_URL": "http://localhost:6333",
      "COLLECTION_NAME": "my-collection",
      "MCP_TRANSPORT": "sse"
    }
  }
}
```

> [!NOTE]
> Some MCP clients (like Windsurf, Claude Desktop, or certain VS Code configurations) may require a `command` entry in their settings and might not support connecting directly to a running container via `sseUrl` alone. In such cases, using `uvx` as a proxy is necessary. Ensure the `env` block within the client configuration correctly sets `MCP_TRANSPORT: "sse"` for the `uvx` process, and the client's `transportType` is also set to `"sse"`. Example:
> ```json
> // In cline_mcp_settings.json or claude_desktop_config.json
> "qdrant-via-uvx": {
>   "command": "uvx",
>   "args": [ "mcp-server-qdrant" ],
>   "env": {
>     "QDRANT_URL": "http://localhost:6333", // Or your Qdrant URL
>     "COLLECTION_NAME": "my-collection",    // Your collection name
>     "MCP_TRANSPORT": "sse"                 // Instruct uvx process
>     // "QDRANT_API_KEY": "YOUR_API_KEY",   // Add if needed
>   },
>   "transportType": "sse",                  // Instruct client
>   "disabled": false,
>   "autoApprove": []
> }
> ```

For local Qdrant mode:

```json
{
  "qdrant": {
    // NOTE: Configuration below assumes direct uvx execution, which is deprecated.
    // Please refer to the 'Installation and Running with Docker Compose' section
    // and configure your MCP client accordingly. Local path mode is generally
    // not applicable with the standard Docker Compose setup.
    // Example using uvx (deprecated):
    // "command": "uvx",
    // "args": ["mcp-server-qdrant", "--transport", "stdio"], // Stdio might work locally but SSE is preferred
    // "env": {
    //  "QDRANT_LOCAL_PATH": "/path/to/qdrant/database",
      "COLLECTION_NAME": "your-collection-name",
      "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
    }
  }
}
```

This MCP server will automatically create a collection with the specified name if it doesn't exist.

The server automatically selects optimal embedding models based on collection names:
- **Career collections** use 768D BGE-Base models for superior semantic understanding
- **Legal/complex content** uses 1024D BGE-Large models for maximum precision  
- **Technical/debug content** uses 384D MiniLM models for speed and efficiency
- **Default collections** fall back to `sentence-transformers/all-MiniLM-L6-v2`

Only [FastEmbed](https://qdrant.github.io/fastembed/) models are currently supported.

## Support for other tools

This MCP server can be used with any MCP-compatible client. For example, you can use it with
[Cursor](https://docs.cursor.com/context/model-context-protocol) and [VS Code](https://code.visualstudio.com/docs), which provide built-in support for the Model Context
Protocol.

### Using with Cursor/Windsurf

You can configure this MCP server to work as a code search tool for Cursor or Windsurf by customizing the tool
descriptions:

```bash
QDRANT_URL="http://localhost:6333" \
COLLECTION_NAME="code-snippets" \
TOOL_STORE_DESCRIPTION="Store reusable code snippets for later retrieval. \
The 'information' parameter should contain a natural language description of what the code does, \
while the actual code should be included in the 'metadata' parameter as a 'code' property. \
The value of 'metadata' is a Python dictionary with strings as keys. \
Use this whenever you generate some code snippet." \
TOOL_FIND_DESCRIPTION="Search for relevant code snippets based on natural language descriptions. The 'query' parameter should describe what you're looking for, and the tool will return the most relevant code snippets. Use this when you need to find existing code snippets for reuse or reference."
# Make sure the server is running via `docker compose up -d`
```

In Cursor/Windsurf, you can configure the MCP server in your settings. Connect to the running Docker container using the SSE transport protocol. The setup process is detailed in the [Cursor documentation](https://docs.cursor.com/context/model-context-protocol#adding-an-mcp-server-to-cursor). If the container is running locally and port `8002` is mapped (as per the `docker-compose.yml`), use this URL:

```
http://localhost:8002/sse
```

> [!TIP]
> We suggest SSE transport as a preferred way to connect Cursor/Windsurf to the MCP server, as it can support remote
> connections. That makes it easy to share the server with your team or use it in a cloud environment.

This configuration transforms the Qdrant MCP server into a specialized code search tool that can:

1. Store code snippets, documentation, and implementation details
2. Retrieve relevant code examples based on semantic search
3. Help developers find specific implementations or usage patterns

You can populate the database by storing natural language descriptions of code snippets (in the `information` parameter)
along with the actual code (in the `metadata.code` property), and then search for them using natural language queries
that describe what you're looking for.

> [!NOTE]
> The tool descriptions provided above are examples and may need to be customized for your specific use case. Consider
> adjusting the descriptions to better match your team's workflow and the specific types of code snippets you want to
> store and retrieve.

**If you have successfully installed the `mcp-server-qdrant`, but still can't get it to work with Cursor, please
consider creating the [Cursor rules](https://docs.cursor.com/context/rules-for-ai) so the MCP tools are always used when
the agent produces a new code snippet.** You can restrict the rules to only work for certain file types, to avoid using
the MCP server for the documentation or other types of content.

### Using with Claude Code

You can enhance Claude Code's capabilities by connecting it to this MCP server, enabling semantic search over your
existing codebase.

#### Setting up mcp-server-qdrant

1. Add the MCP server to Claude Code:

    ```shell
    # Add mcp-server-qdrant configured for code search
    claude mcp add code-search \
    -e QDRANT_URL="http://localhost:6333" \
    -e COLLECTION_NAME="code-repository" \
    -e EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" \
    -e TOOL_STORE_DESCRIPTION="Store code snippets with descriptions. The 'information' parameter should contain a natural language description of what the code does, while the actual code should be included in the 'metadata' parameter as a 'code' property." \
    -e TOOL_FIND_DESCRIPTION="Search for relevant code snippets using natural language. The 'query' parameter should describe the functionality you're looking for." \
    # NOTE: The `claude mcp add` command shown uses uvx directly, which is deprecated.
    # Adapt this for your Docker Compose setup. You might configure Claude Code
    # to connect directly to the running container's SSE endpoint
    # (e.g., http://localhost:8002/sse) if Claude Code supports that,
    # or use a tool like docker-mcp within Claude Code's MCP settings
    # to manage the Docker Compose lifecycle.
    # Example Connection (Conceptual - check Claude Code docs for specifics):
    # claude mcp add code-search-docker --transport sse --sse-url http://localhost:8002/sse
    ```

2. Verify the server was added:

    ```shell
    claude mcp list
    ```

#### Using Semantic Code Search in Claude Code

Tool descriptions, specified in `TOOL_STORE_DESCRIPTION` and `TOOL_FIND_DESCRIPTION`, guide Claude Code on how to use
the MCP server. The ones provided above are examples and may need to be customized for your specific use case. However,
Claude Code should be already able to:

1. Use the `qdrant-store` tool to store code snippets with descriptions.
2. Use the `qdrant-find` tool to search for relevant code snippets using natural language.

### Run MCP server in Development Mode

The MCP server can be run in development mode using the `mcp dev` command. This will start the server and open the MCP
inspector in your browser.

```shell
COLLECTION_NAME=mcp-dev mcp dev src/mcp_server_qdrant/server.py
```

### Using with VS Code

<!-- Installation buttons using deprecated methods (uvx, docker run) have been removed. -->
<!-- Please refer to the Docker Compose instructions above. -->

#### Manual Installation

Add the following JSON block to your User Settings (`settings.json`) or Workspace Settings (`.vscode/settings.json`) file in VS Code.

**Recommended Method: Using `docker-mcp` (Requires `docker-mcp` server)**

This method uses the `docker-mcp` server to manage the Docker Compose lifecycle.

```json
// In your main MCP settings file (e.g., cline_mcp_settings.json)
// Ensure docker-mcp server is configured first.
{
  "mcpServers": {
    // ... other servers ...
    "docker-managed-qdrant": {
      "command": "docker-mcp", // Use the docker-mcp server
      "args": [
        "deploy-compose",
        "--project-name", "mcp-qdrant",
        "--compose-yaml", "l:/ToolNexusMCP_plugins/mcp-server-qdrant/docker-compose.yml" // Adjust path if needed
        // Environment variables are handled by docker-compose.yml and .env file
      ],
      "transportType": "stdio" // docker-mcp uses stdio
    }
    // Note: The actual qdrant server tools will be exposed via the container's connection,
    // usually SSE on http://localhost:8002/sse. The docker-mcp entry above just manages deployment.
    // You might need a separate entry to connect to the service itself, or the client
    // might automatically detect it if using a standard discovery mechanism.
  }
}

// Alternatively, configure VS Code to connect directly via SSE:
{
  "mcp": {
    "servers": {
      "qdrant-sse": {
        "transportType": "sse",
        "sseUrl": "http://localhost:8002/sse"
        // Assumes the container is running independently (e.g., via `docker compose up -d`)
      }
    }
  }
}
```

**(Deprecated Examples Below - For Reference Only)**

```json
// DEPRECATED Example using uvx:
// {
//   "mcp": {
//     "inputs": [ /* ... define inputs if needed ... */ ],
//     "servers": {
//       "qdrant-uvx-deprecated": {
//         "command": "uvx",
//         "args": ["mcp-server-qdrant", "--transport", "sse"], // Use SSE
//         "env": {
//           "QDRANT_URL": "${input:qdrantUrl}", // Requires inputs defined
//           "QDRANT_API_KEY": "${input:qdrantApiKey}",
//           "COLLECTION_NAME": "${input:collectionName}"
//         }
//       }
//     }
//   }
// }
```

```json
// DEPRECATED Example using docker run:
// {
//   "mcp": {
//     "inputs": [ /* ... define inputs if needed ... */ ],
//     "servers": {
//       "qdrant-docker-run-deprecated": {
//         "command": "docker",
//         "args": [
//           "run",
//           "-p", "8002:8000", // Use updated port mapping
//           "-i",
//           "--rm", // Consider removing --rm if you want to reuse the container
//           "--network", "chroma-mcp_chroma-memory-network", // Example network
//           "-e", "QDRANT_URL=${input:qdrantUrl}", // Pass env vars directly
//           "-e", "QDRANT_API_KEY=${input:qdrantApiKey}",
//           "-e", "COLLECTION_NAME=${input:collectionName}",
//           "mcp-server-qdrant:latest" // Assumes image is built/pulled with 'latest' tag
//         ],
//         // Env here might be redundant if passed in args
//         "env": {}
//       }
//     }
//   }
// }
```

> [!NOTE]
> The VS Code examples above primarily use deprecated `uvx` or `docker run` methods directly within the VS Code settings. For setups using **Docker Compose** (as recommended earlier), connecting VS Code typically involves either:
> 1.  **Direct SSE Connection:** If your VS Code MCP extension supports it, configure it to connect directly to the running container's mapped SSE port (e.g., `http://localhost:8002/sse` if using the provided `docker-compose.yml`). This might look like the "Alternatively" example under the `docker-mcp` section but ensure your extension supports the `sseUrl` field directly.
> 2.  **`docker-mcp`:** Use the `docker-mcp` server to manage the compose lifecycle (as shown in the "Recommended Method"). The connection to the actual tools would still happen via SSE, either automatically detected or configured separately.
> 3.  **`uvx` as Proxy (if direct SSE fails):** If direct SSE connection isn't supported by your VS Code client setup, use the `uvx` method similar to the configuration shown in the note under "Manual configuration of Claude Desktop", ensuring `env.MCP_TRANSPORT` and `transportType` are both `sse`.

## 🤝 Contributing

We welcome contributions to the Enhanced Qdrant MCP Server! This project demonstrates how to enhance open-source projects with enterprise-grade features.

### 🚀 Getting Started

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/triepod-ai/mcp-server-qdrant-enhanced.git
   cd mcp-server-qdrant-enhanced
   ```

2. **Development Setup**:
   ```bash
   # Quick development environment
   ./dev setup
   
   # Or manual setup
   make dev-setup
   ```

3. **Development Workflow**:
   ```bash
   ./dev start     # Start server (preserves existing workflow)
   ./dev dev       # Development mode with live reloading  
   ./dev test      # Run tests and validation
   ./dev lint      # Run linting and formatting
   ```

### 💡 Contribution Areas

- **Performance Optimizations**: GPU acceleration, quantization improvements
- **Model Integration**: New embedding models, collection-specific optimizations
- **Deployment Automation**: CI/CD enhancements, installation methods
- **Documentation**: Usage examples, migration guides, tutorials
- **Testing**: Unit tests, integration tests, performance benchmarks

### 🔧 Development Tools

This project includes comprehensive development tools while preserving the original workflow:

- **Makefile**: Standard development commands (`make start`, `make test`, `make lint`)
- **Development Scripts**: `./dev` entry point for common tasks
- **Docker Development**: Live-reload containers for fast iteration
- **GitHub Actions**: Automated testing, building, and publishing

If you have suggestions for improvements or want to report a bug, please open an issue! We'd love all contributions that help make this enhanced MCP server even better.

### 🧪 Testing Locally

#### MCP Inspector (Recommended)

Use the [MCP inspector](https://github.com/modelcontextprotocol/inspector) for interactive testing:

```bash
# Enhanced server with memory-based Qdrant
QDRANT_URL=":memory:" COLLECTION_NAME="test" \
mcp dev src/mcp_server_qdrant/enhanced_main.py

# Open browser to http://localhost:5173
```

#### Quick Development Testing

```bash
# Start development environment
./dev dev

# Run quick validation
./dev quick-test

# View logs
./dev logs
```

#### Production Testing

```bash
# Test Docker container (GPU-accelerated enhanced version)
docker run -it --rm --gpus all \
  ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest --help

# Test with actual Qdrant connection
docker run -it --rm --gpus all --network host \
  -e QDRANT_URL="http://localhost:6333" \
  -e COLLECTION_NAME="test" \
  ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest

# CPU-only mode (original package, much slower)
uvx mcp-server-qdrant --help
```

## 🔒 Data Safety and Migration

### Backup Strategy
- **Automated Backups**: Comprehensive data backup before any migration operations
- **Zero Data Loss**: All migrations performed with complete data preservation
- **Rollback Capability**: Ability to restore previous collection configurations
- **Timestamped Backups**: All backup data stored with timestamps for audit trails

### Migration Features  
- **Safe Collection Migration**: Migrate between different embedding models with zero downtime
- **Model Optimization**: Automatic selection of optimal models based on content type
- **Performance Validation**: Search quality verification after migrations
- **Docker Integration**: Seamless configuration updates in containerized environments

## 📄 License

This Enhanced Qdrant MCP Server is licensed under the Apache License 2.0. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the Apache License 2.0. 

For more details, please see the [LICENSE](LICENSE) file in the project repository.

## 🙏 Acknowledgments

- **Original Project**: Built upon the excellent foundation of [mcp-server-qdrant](https://github.com/modelcontextprotocol/mcp-server-qdrant)
- **Qdrant Team**: For the powerful vector database that makes this possible
- **FastEmbed**: For GPU-accelerated embedding generation
- **Model Context Protocol**: For the standardized framework enabling LLM integrations

## 🔗 Related Projects

- **[Original mcp-server-qdrant](https://github.com/modelcontextprotocol/mcp-server-qdrant)**: The foundational MCP server this enhancement is based on
- **[Qdrant](https://qdrant.tech/)**: The vector search engine powering the storage layer
- **[FastEmbed](https://github.com/qdrant/fastembed)**: GPU-accelerated embedding generation library
- **[Model Context Protocol](https://modelcontextprotocol.io/)**: The standardized protocol for LLM tool integration

---

**Made with ❤️ by [triepod-ai](https://github.com/triepod-ai)** | **Enhanced for Production Use** | **Star ⭐ if this helps your project!**
