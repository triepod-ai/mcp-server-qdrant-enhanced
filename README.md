# Enhanced Qdrant MCP Server

[![NPM Package](https://img.shields.io/npm/v/@triepod-ai/mcp-server-qdrant-enhanced)](https://www.npmjs.com/package/@triepod-ai/mcp-server-qdrant-enhanced)
[![Docker Image](https://img.shields.io/docker/v/triepod-ai/mcp-server-qdrant-enhanced?label=docker)](https://github.com/triepod-ai/mcp-server-qdrant-enhanced/pkgs/container/mcp-server-qdrant-enhanced)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![GitHub Actions](https://github.com/triepod-ai/mcp-server-qdrant-enhanced/workflows/Build%20and%20Publish/badge.svg)](https://github.com/triepod-ai/mcp-server-qdrant-enhanced/actions)

> **🚀 Production-Ready Enhancement** of the original [mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant) with GPU acceleration, multi-vector support, and enterprise-grade deployment infrastructure.

**Enhanced Model Context Protocol server** for [Qdrant](https://qdrant.tech/) vector database with advanced features including GPU acceleration, collection-specific embedding models, and production deployment automation.

## 🌟 Why This Enhanced Version?

This fork transforms the basic MCP server into a **production-ready solution** with:

- **🚀 10x Performance**: GPU acceleration with FastEmbed and CUDA support
- **🧠 Smart Model Selection**: Automatic 384D/768D/1024D embedding selection based on collection type  
- **🐳 Production Infrastructure**: Complete Docker automation with 4.49GB optimized containers
- **📦 Dual Installation**: NPM package + Docker options for maximum accessibility
- **⚡ Zero-Config Setup**: Interactive installer with platform detection
- **🔄 48 Production Collections**: Battle-tested with real workloads

## Overview

An enhanced Model Context Protocol server for keeping and retrieving memories in the Qdrant vector search engine with **structured data returns**, **TypeScript-inspired type validation**, **collection-specific embedding models**, and **optimized 768D career collections**.

### ✨ Enhanced Features

- **🎯 Structured Data Returns**: JSON objects instead of formatted strings for better programmatic access
- **🛡️ Type Safety**: TypeScript-inspired type guards and comprehensive validation
- **📊 Score-Based Filtering**: Relevance thresholds and result ranking
- **🔄 Retry Logic**: Exponential backoff for robust error handling
- **🎨 Multi-Vector Support**: Collection-specific embedding models (384D/768D/1024D)
- **⚡ Enhanced Performance**: Optimized search with connection management
- **🚀 768D Career Collections**: Migrated career collections using BGE-Base models for superior semantic understanding
- **🔒 Safe Migration**: Zero data loss migration with comprehensive backup strategies

## 🚀 Quick Start

Get up and running with the Enhanced Qdrant MCP Server in under 2 minutes! Choose your preferred installation method:

### 🎯 One-Command Setup (Recommended)

The easiest way to get started - interactive setup that guides you through the entire process:

```bash
curl -sSL https://raw.githubusercontent.com/triepod-ai/mcp-server-qdrant-enhanced/main/setup-qdrant-enhanced.sh | bash
```

This script will:
- ✅ Detect your platform and requirements  
- ✅ Let you choose between NPM or Docker installation
- ✅ Configure Qdrant connection settings
- ✅ Generate MCP client configurations (Claude Desktop, VS Code)
- ✅ Test your setup and validate connectivity

### 📦 Option 1: NPM Package (Development)

Perfect for developers who want direct command access and easy integration:

```bash
# Install globally
npm install -g @triepod-ai/mcp-server-qdrant-enhanced

# Verify installation
mcp-server-qdrant-enhanced --help

# Quick test (requires running Qdrant instance)
QDRANT_URL="http://localhost:6333" COLLECTION_NAME="test" mcp-server-qdrant-enhanced --transport stdio
```

**Requirements:** Node.js 18+, Python 3.10+, running Qdrant instance

### 🐳 Option 2: Docker Container (Production)

Complete isolation with all dependencies and models pre-installed:

```bash
# Pull the pre-built image (4.49GB with embedded models)
docker pull ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest

# Quick run with host networking
docker run -it --rm --network host \
  -e QDRANT_URL="http://localhost:6333" \
  -e COLLECTION_NAME="enhanced-collection" \
  ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest

# Or use Docker Compose for persistent setup
curl -sSL https://raw.githubusercontent.com/triepod-ai/mcp-server-qdrant-enhanced/main/docker-compose.yml -o docker-compose.yml
docker-compose up -d
```

**Requirements:** Docker, running Qdrant instance

### ⚡ What You Get

After installation, you'll have access to:

- **🎯 Enhanced MCP Tools**: `qdrant-store`, `qdrant-find`, `qdrant-list-collections`, etc.
- **🧠 Smart Model Selection**: Automatic 384D/768D/1024D model selection based on collection type
- **🚀 GPU Acceleration**: FastEmbed with CUDA support for lightning-fast embeddings
- **📊 Production Collections**: 48 pre-configured collection types with optimal model mappings
- **🔄 Zero-Config Operation**: Works out of the box with sensible defaults

### 🔧 Quick Integration

Add to your MCP client configuration:

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "qdrant-enhanced": {
      "command": "mcp-server-qdrant-enhanced",
      "args": ["--transport", "stdio"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "your-collection"
      }
    }
  }
}
```

**Need help?** The setup script generates these configurations automatically! 🎊

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
- **GPU Acceleration**: FastEmbed with CUDA support for 10x faster embedding generation
- **Smart Model Selection**: Collection-specific routing to optimal 384D/768D/1024D models
- **Quantization Optimized**: 40% memory reduction while maintaining search quality
- **Production Validated**: Sub-second response times across 48 active collections

### 🔧 Advanced Architecture
- **Separation of Concerns**: MCP server (4.49GB with models) + Qdrant DB (279MB storage)
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
| `TOOL_STORE_DESCRIPTION`      | Custom description for the store tool                               | See default in [`settings.py`](src/mcp_server_qdrant/settings.py) |
| `TOOL_FIND_DESCRIPTION`       | Custom description for the find tool                                | See default in [`settings.py`](src/mcp_server_qdrant/settings.py) |

Note: You cannot provide both `QDRANT_URL` and `QDRANT_LOCAL_PATH` at the same time.

> [!IMPORTANT]
> Command-line arguments are not supported anymore! Please use environment variables for all configuration.

## Installation Options

> **⚡ Quick Setup Available!** For the fastest installation experience, see the [Quick Start](#-quick-start) section above which includes both NPM and Docker options with automated setup.

### Enhanced Installation Methods

This enhanced fork offers multiple installation paths optimized for different use cases:

1. **🎯 [Interactive Setup Script](#-one-command-setup-recommended)** - One command, fully guided setup
2. **📦 [NPM Package](#-option-1-npm-package-development)** - Perfect for development and easy integration  
3. **🐳 [Docker Container](#-option-2-docker-container-production)** - Production-ready with embedded models

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
# Test NPM package installation
npm install -g @triepod-ai/mcp-server-qdrant-enhanced
mcp-server-qdrant-enhanced --help

# Test Docker container
docker run -it --rm ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest --help
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
