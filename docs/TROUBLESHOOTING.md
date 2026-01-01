# Troubleshooting Guide

This guide consolidates common issues and solutions for the Enhanced Qdrant MCP Server.

## Quick Reference

| Issue | Solution |
|-------|----------|
| CUBLAS_STATUS_NOT_INITIALIZED | Use `cuda:12.x-devel` base image |
| CUDAExecutionProvider not available | Install onnxruntime-gpu from nightly |
| 406 Not Acceptable | Add `text/event-stream` to Accept header |
| Missing session ID | Include `mcp-session-id` header |
| Nested metadata not updating | Use `key="metadata"` parameter |

---

## GPU / CUDA Issues

### CUBLAS_STATUS_NOT_INITIALIZED

**Error:**
```
[ONNXRuntimeError] : 1 : FAIL : CUBLAS failure 1: CUBLAS_STATUS_NOT_INITIALIZED
```

**Root Cause:** Using `nvidia/cuda:12.x-runtime-ubuntu22.04` base image (missing cuBLAS dev libraries)

**Solution:** Switch to development base image in Dockerfile:
```dockerfile
FROM nvidia/cuda:12.x-devel-ubuntu22.04
```

**Files affected:** `Dockerfile.enhanced.cuda`, `Dockerfile.enhanced.http`

---

### CUDAExecutionProvider Not Available

**Problem:** `CUDAExecutionProvider` not in `ort.get_available_providers()` list

**Root Cause:** Stable PyPI `onnxruntime-gpu` doesn't support CUDA 12.x despite documentation claims

**Solution:** Install from nightly builds:
```bash
pip install --pre --index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/ORT-Nightly/pypi/simple/ onnxruntime-gpu
```

**Verification:**
```python
import onnxruntime as ort
print(ort.get_available_providers())
# Expected: ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
```

---

### cuDNN Warnings (Expected)

**Warning messages:**
```
[WARNING] Failed to create CUDAExecutionProvider. Require cuDNN 9.* and CUDA 12.*
[WARNING] Attempt to set CUDAExecutionProvider failed. Current providers: ['CPUExecutionProvider']
```

**This is normal behavior** when GPU libraries are unavailable. The system falls back to CPU execution gracefully with no functionality loss.

---

## HTTP Transport Issues

### 406 Not Acceptable

**Problem:** Server returns HTTP 406 status

**Cause:** Missing `text/event-stream` in Accept header

**Solution:** Include both content types:
```bash
curl -X POST http://localhost:10650/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", ...}'
```

---

### 400 Bad Request "Missing session ID"

**Problem:** Tool calls fail with "Missing session ID" error

**Cause:** Missing or incorrect session header

**Solution:** Use `mcp-session-id` header (not `X-Session-Id`):
```bash
curl -X POST http://localhost:10650/mcp \
  -H "mcp-session-id: YOUR_SESSION_ID" \
  ...
```

**Note:** Get session ID from the response headers of the `initialize` call.

---

### -32602 "Invalid request parameters"

**Problem:** Tool calls fail before session is initialized

**Cause:** Tool called before `notifications/initialized` was sent

**Solution:** Follow the correct initialization sequence:
1. Send `initialize` request
2. Extract `mcp-session-id` from response
3. Send `notifications/initialized` notification
4. Now tool calls will work

See [CURL_TESTING_GUIDE.md](./CURL_TESTING_GUIDE.md) for complete examples.

---

## Tool-Specific Issues

### qdrant_update_payload - Nested Updates Not Working

**Problem:** Updates create root-level payload fields instead of updating metadata

**Cause:** Missing `key` parameter for nested structures

**Background:** Qdrant payloads have nested structure:
```
payload
├── document: "{ content... }"
└── metadata
    ├── sync_status: "pending"
    ├── synced_to_asana: false
    └── ... other fields
```

**Solution:** Use `key="metadata"` for nested payload.metadata.* fields:
```json
{
  "name": "qdrant_update_payload",
  "arguments": {
    "point_ids": ["abc123-..."],
    "payload": {"sync_status": "synced"},
    "collection_name": "my_collection",
    "key": "metadata"
  }
}
```

| `key` value | Update target | Use when |
|-------------|---------------|----------|
| `None` | Root payload | Updating `payload.field` directly |
| `"metadata"` | Nested metadata | Updating `payload.metadata.field` |

---

### Collection Auto-Creation - Wrong Model Selected

**Problem:** Collection created with unexpected embedding model

**Cause:** Collection name doesn't match naming patterns for model selection

**Solution:** Use semantic collection names that trigger automatic model selection:

| Name Pattern | Model | Dimensions |
|--------------|-------|------------|
| `*legal*`, `*career*`, `*contract*` | BGE-Large | 1024D |
| `*lessons*`, `*knowledge*`, `*analysis*` | BGE-Base | 768D |
| `*debug*`, `*technical*`, `*working*`, `*solutions*` | MiniLM | 384D |

**Examples:**
- `legal_analysis` → 1024D (complex content)
- `lessons_learned` → 768D (knowledge-intensive)
- `working_solutions` → 384D (speed-optimized)

---

## Container Issues

### HTTP Container Timeout on Port 10650

**Problem:** Requests to `http://localhost:10650/mcp` timeout

**Status:** Known issue (container networking layer, not MCP functionality)

**Verification:** Core MCP functionality works - issue is container-specific

**Workaround:** Use local server testing on alternate port:
```bash
source .venv/bin/activate
uvicorn mcp_server_qdrant.enhanced_http_app:app --host 127.0.0.1 --port 10651
```

---

### GPU Not Detected in Container

**Verification:**
```bash
docker exec mcp-server-qdrant-enhanced nvidia-smi
```

**Solutions:**
1. Ensure `--gpus all` flag in docker run command
2. Verify NVIDIA Docker runtime is configured:
   ```bash
   docker info | grep -i runtime
   ```
3. Check docker-compose.yml includes:
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: all
             capabilities: [gpu]
   ```

---

## Getting Help

1. **Check logs:** `docker-compose -f docker-compose.enhanced.yml logs -f`
2. **Run tests:** `make test` or `./dev quick-test`
3. **HTTP testing:** `./scripts/test-mcp-http.sh`
4. **Full validation:** See [VALIDATION_REPORT.md](../VALIDATION_REPORT.md)

For issues not covered here, check:
- [CURL_TESTING_GUIDE.md](./CURL_TESTING_GUIDE.md) - HTTP protocol details
- [CUDA_IMPLEMENTATION_SUMMARY.md](./CUDA_IMPLEMENTATION_SUMMARY.md) - GPU acceleration details
- [CLAUDE.md](../CLAUDE.md) - Development guidance
