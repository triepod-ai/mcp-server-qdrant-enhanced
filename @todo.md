# MCP Server Qdrant GPU Acceleration Implementation Todo

## Current State Summary

**Status**: MCP server operational in CPU mode, GPU acceleration pending CUDA 12.x upgrade

**What Works**:
- ✅ MCP server running and responsive
- ✅ Enhanced FastEmbed provider with collection-specific models  
- ✅ Graceful fallback from GPU to CPU implemented
- ✅ Environment variable `FASTEMBED_CUDA=true` activated
- ✅ Docker container with CUDA 11.8 base image built successfully

**What Needs Fixing**:
- ⚠️ GPU acceleration disabled due to CUDA version mismatch
- ⚠️ onnxruntime-gpu requires CUDA 12.x but container uses CUDA 11.8
- ⚠️ Missing CUDA 12 runtime libraries (libcublasLt.so.12)

## Root Cause Analysis

**Error Message**:
```
Failed to load library libonnxruntime_providers_cuda.so with error: 
libcublasLt.so.12: cannot open shared object file: No such file or directory

Require cuDNN 9.* and CUDA 12.*
```

**Solution Required**: Upgrade from CUDA 11.8 to CUDA 12.1 base image

## Implementation Plan

### Phase 1: CUDA 12.1 Upgrade
**File**: `Dockerfile.enhanced.cuda`
**Change**: Update base image from `nvidia/cuda:11.8.0-base-ubuntu22.04` to `nvidia/cuda:12.1-base-ubuntu22.04`

### Phase 2: Rebuild and Test
1. Clean rebuild container with CUDA 12.1
2. Validate GPU provider detection
3. Test embedding generation performance
4. Benchmark vs CPU baseline

### Phase 3: Performance Validation
- Test all model sizes (384D, 768D, 1024D)
- Verify collection-specific model routing
- Measure performance improvements

## Expected Performance Gains

Based on documented CUDA implementation experience:
- **Embedding Generation**: 3-10x faster
- **Vector Search**: 10-100x faster with FAISS GPU
- **Memory Efficiency**: 30-50% CPU load reduction
- **Concurrent Processing**: Better throughput for multiple collections

## Key Files Modified

### 1. Docker Configuration
- `docker-compose.enhanced.yml` - GPU runtime configuration
- `Dockerfile.enhanced.cuda` - CUDA 12.1 base image
- Environment: `FASTEMBED_CUDA=true`

### 2. Code Changes Completed
- `src/mcp_server_qdrant/embeddings/enhanced_fastembed.py` - Fixed sys import issues
- GPU detection and fallback mechanisms implemented
- Collection-specific model support active

## Technical Context

### Current Docker Setup
```yaml
services:
  mcp-server-enhanced:
    build: 
      context: .
      dockerfile: Dockerfile.enhanced.cuda
    runtime: nvidia
    environment:
      - FASTEMBED_CUDA=true
      - NVIDIA_VISIBLE_DEVICES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### CUDA Requirements
- **onnxruntime-gpu**: Requires CUDA 12.x + cuDNN 9.*
- **FastEmbed**: Supports CUDAExecutionProvider with proper CUDA setup
- **Base Image**: `nvidia/cuda:12.1-base-ubuntu22.04` (proven stable)

## Proven CUDA 12.1 Configuration

From successful Agent Zero implementation documentation:

### Dockerfile Pattern
```dockerfile
FROM nvidia/cuda:12.1-base-ubuntu22.04

# Set CUDA environment variables
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Install dependencies with CUDA support
RUN uv pip install --system \
    fastembed>=0.6.0 \
    qdrant-client>=1.12.0 \
    pydantic>=2.10.6 \
    "mcp[cli]>=1.3.0" \
    onnxruntime-gpu

ENV FASTEMBED_CUDA="true"
```

### Error Handling Pattern
```python
def _create_text_embedding(self, model_name: str) -> TextEmbedding:
    if self.use_cuda:
        try:
            return TextEmbedding(
                model_name,
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
            )
        except Exception as e:
            print(f"[WARNING] CUDA initialization failed for {model_name}, falling back to CPU: {e}", file=sys.stderr)
            return TextEmbedding(model_name, providers=['CPUExecutionProvider'])
    else:
        return TextEmbedding(model_name, providers=['CPUExecutionProvider'])
```

## Step-by-Step Implementation

### Step 1: Update Dockerfile
```bash
# Edit Dockerfile.enhanced.cuda
# Change: FROM nvidia/cuda:11.8.0-base-ubuntu22.04  
# To:     FROM nvidia/cuda:12.1-base-ubuntu22.04
```

### Step 2: Clean Rebuild
```bash
# Stop current container
docker-compose -f docker-compose.enhanced.yml down

# Remove old image
docker rmi mcp-server-qdrant-enhanced:latest

# Fresh build with CUDA 12.1
docker-compose -f docker-compose.enhanced.yml build --no-cache

# Start with GPU support
docker-compose -f docker-compose.enhanced.yml up -d
```

### Step 3: Validate GPU Detection
```bash
# Check container logs for CUDA initialization
docker logs mcp-server-qdrant-enhanced

# Should see:
# - No CUDA provider errors
# - Successful GPU resource allocation
# - FastEmbed models loaded with CUDAExecutionProvider
```

### Step 4: Performance Testing
```bash
# Test embedding generation with different models
# Monitor GPU utilization: nvidia-smi
# Benchmark vs previous CPU performance
```

## Success Criteria

### Technical Validation
- [ ] Container starts without CUDA provider errors
- [ ] CUDAExecutionProvider available in FastEmbed
- [ ] GPU memory allocation successful
- [ ] All collection-specific models load with GPU support

### Performance Validation  
- [ ] Embedding generation 3-10x faster than CPU
- [ ] GPU utilization visible in nvidia-smi
- [ ] Memory efficiency improvements observed
- [ ] Fallback to CPU works when GPU unavailable

## Risk Mitigation

### Fallback Strategy
- CPU-only mode already working as backup
- Environment variable toggle: `FASTEMBED_CUDA=false`
- Original `Dockerfile.enhanced` available for CPU-only deployment

### Rollback Plan
```bash
# Quick rollback to CPU mode
docker-compose -f docker-compose.enhanced.yml down
# Edit docker-compose.enhanced.yml: FASTEMBED_CUDA=false
docker-compose -f docker-compose.enhanced.yml up -d
```

## Next Session Commands

1. **Start Here**:
   ```bash
   cd /home/bryan/mcp-servers/mcp-server-qdrant
   ```

2. **Update CUDA Version**:
   ```bash
   # Already done: Edit Dockerfile.enhanced.cuda line 2
   # FROM nvidia/cuda:12.1-base-ubuntu22.04
   ```

3. **Clean Rebuild**:
   ```bash
   docker-compose -f docker-compose.enhanced.yml down
   docker rmi mcp-server-qdrant-enhanced:latest
   docker-compose -f docker-compose.enhanced.yml build --no-cache
   docker-compose -f docker-compose.enhanced.yml up -d
   ```

4. **Validate Results**:
   ```bash
   docker logs mcp-server-qdrant-enhanced
   nvidia-smi  # Check GPU utilization
   ```

## Documentation References

- **CUDA Implementation Guide**: Stored in technical_documentation collection
- **Agent Zero CUDA Lessons**: 20 critical lessons from production deployment  
- **Docker GPU Configuration**: Proven patterns from Agent Zero success
- **Performance Benchmarks**: Expected 3-100x improvements documented

## Current Environment

- **Host OS**: Linux WSL2
- **Docker**: GPU runtime configured
- **NVIDIA Driver**: Compatible with CUDA 12.x
- **Base Directory**: `/home/bryan/mcp-servers/mcp-server-qdrant`
- **Active Branch**: master (4 commits ahead with GPU work)

## Context for New Session

This todo represents completion of GPU acceleration for an MCP server that provides enhanced embedding capabilities with collection-specific models. The server is currently operational in CPU mode but requires CUDA 12.1 upgrade to unlock 3-100x performance improvements documented in previous successful CUDA implementations.

The upgrade path is clear and low-risk due to existing fallback mechanisms and proven CUDA 12.1 configuration patterns from Agent Zero documentation.