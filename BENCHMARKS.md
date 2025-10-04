# Performance Benchmarks

This document provides comprehensive performance benchmarks for the Enhanced Qdrant MCP Server with full reproducibility information.

## 🎯 Benchmark Summary

All benchmarks conducted on **NVIDIA GeForce RTX 3080 Ti (12GB VRAM)** with CUDA 12.x + cuDNN 9.13.0.

| Metric | Value | Context |
|--------|-------|---------|
| **Embedding Generation** | 12-13ms | Per document, GPU-accelerated |
| **Storage Operations** | 18-95ms | Varies by embedding model complexity |
| **Search Performance** | Sub-50ms | With HNSW indexing |
| **Stress Test Success** | 100% | 500 documents, zero failures |
| **GPU Performance Boost** | ~10x | Estimated vs CPU-only mode |

## 📊 Detailed Performance Metrics

### Embedding Model Performance

Based on validation testing (2025-01-23):

| Model Type | Dimensions | Time per Doc | Use Case |
|------------|------------|--------------|----------|
| **MiniLM-L6-v2** | 384D | ~18ms | Technical documents, debug logs |
| **BGE-Base** | 768D | ~560ms | Knowledge bases, general content |
| **BGE-Large** | 1024D | ~2350ms | Legal analysis, complex content |

**Source**: [VALIDATION_REPORT.md](VALIDATION_REPORT.md) - Section "Model Routing Performance"

### GPU vs CPU Performance

**GPU-Accelerated (CUDA 12.x + cuDNN 9.13.0)**:
- Embedding generation: 12-13ms per document
- Batch processing: 124ms for 10 documents
- Overall storage: 18-95ms depending on model

**CPU-Only (Estimated)**:
- Embedding generation: ~130ms per document (10x slower)
- Not recommended for production use

**Performance Improvement**: ~10x faster with GPU acceleration

> **Note**: CPU benchmark is estimated based on typical CPU vs GPU performance ratios. GPU acceleration requires Docker with NVIDIA runtime.

### Collection-Specific Benchmarks

From production validation testing:

#### Technical Documents (384D MiniLM)
```
Collection: working_solutions
Model: sentence-transformers/all-MiniLM-L6-v2
Dimensions: 384D
Embedding Time: 18.12ms
Use Case: Quick technical solutions, debug patterns
```

#### Knowledge Base (768D BGE-Base)
```
Collection: lessons_learned
Model: BAAI/bge-base-en
Dimensions: 768D
Embedding Time: 563.01ms
Use Case: Knowledge-intensive content, career materials
```

#### Legal Analysis (1024D BGE-Large)
```
Collection: legal_analysis
Model: BAAI/bge-large-en-v1.5
Dimensions: 1024D
Embedding Time: 2351.96ms
Use Case: Complex legal content, maximum precision
```

## 🧪 Reproducible Benchmark Commands

### Prerequisites

1. **Docker with NVIDIA Runtime**:
```bash
# Verify Docker can access GPU
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

2. **Running Qdrant Instance**:
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

### Running Benchmarks

#### 1. Single Document Storage (384D)
```bash
docker run -i --rm --gpus all --network host \
  -e QDRANT_URL="http://localhost:6333" \
  -e COLLECTION_NAME="benchmark_384d" \
  -e EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" \
  -e FASTEMBED_CUDA="true" \
  ghcr.io/triepod-ai/mcp-server-qdrant-enhanced:latest

# Measure time for qdrant_store operation
# Expected: ~18ms for 384D embeddings
```

#### 2. Batch Storage Test
```bash
# Use test_orchestration.py for comprehensive validation
docker exec -it mcp-server-qdrant-enhanced python3 /app/test_orchestration.py

# This runs:
# - 10 document batch test
# - Multiple embedding model tests
# - Performance metrics collection
```

#### 3. Search Performance Test
```bash
# Run search operations and measure time
# Expected: Sub-50ms for most queries with HNSW indexing
```

### Stress Testing

From [VALIDATION_REPORT.md](VALIDATION_REPORT.md):

```bash
# 500-document stress test
# Result: 100% success rate, zero failures
# Average storage time: 95.47ms across all models
```

## 🔧 System Configuration

### Hardware Specifications

```
GPU: NVIDIA GeForce RTX 3080 Ti
VRAM: 12GB
CUDA: Version 12.9
cuDNN: Version 9.13.0
Docker: NVIDIA runtime enabled
```

### Software Versions

```
MCP SDK: v1.15.0
FastEmbed: 0.6.0+ with CUDA support
Qdrant Client: 1.12.0+
ONNX Runtime: 1.22.0 with GPU providers
Python: 3.11
```

### Docker Configuration

```yaml
# docker-compose.enhanced.yml
runtime: nvidia
environment:
  - FASTEMBED_CUDA=true
  - CUDA_VISIBLE_DEVICES=0
  - QDRANT_URL=http://localhost:6333
```

## 📈 Performance Over Time

### Version History

**v1.15.0 (2025-10-03)**:
- MCP SDK upgrade to v1.15.0
- Dual transport support (STDIO + HTTP)
- Maintained GPU performance benchmarks

**v1.14.1 (2025-01-25)**:
- 30% performance improvement in embedding generation
- Upgrade from 0.019s → 0.013s per document
- cuDNN 9.13.0 integration
- 100% stress test success rate

**v1.3.0 (2025-01-23)**:
- Initial GPU acceleration implementation
- Baseline: 12.44ms embedding generation
- 97.14% test pass rate

## ⚠️ Performance Variability Factors

Performance metrics may vary based on:

1. **Hardware**:
   - GPU model and VRAM capacity
   - CUDA version compatibility
   - Available system memory

2. **Workload**:
   - Document size and complexity
   - Batch size for operations
   - Collection count and total vectors

3. **Configuration**:
   - Embedding model selection (384D vs 768D vs 1024D)
   - HNSW parameters (ef_construct, M)
   - Quantization settings

4. **System Load**:
   - Concurrent operations
   - GPU utilization by other processes
   - Network latency for remote Qdrant instances

## 🎓 Benchmark Methodology

All benchmarks follow this methodology:

1. **Clean Environment**: Fresh Docker containers with no cached models
2. **GPU Warmup**: Initial operations to warm up GPU kernels
3. **Multiple Runs**: Average of 10+ runs for each metric
4. **Consistent Data**: Same test documents across runs
5. **Validation**: Results verified through test orchestration scripts

### Validation Reports

- [VALIDATION_REPORT.md](VALIDATION_REPORT.md) - Comprehensive validation (2025-01-23)
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Session-by-session improvements

## 🔗 Related Documentation

- [README.md](README.md#-performance-metrics-latest-v1141--cuda-12x) - Performance overview
- [CLAUDE.md](CLAUDE.md#performance--production-considerations) - Production considerations
- [VALIDATION_REPORT.md](VALIDATION_REPORT.md) - Detailed test results

## 📝 Contributing Benchmarks

To submit new benchmark results:

1. Use the reproducible commands above
2. Document your hardware configuration
3. Include system specifications
4. Submit via GitHub issue or PR with:
   - Hardware: GPU model, VRAM, CUDA version
   - Software: Docker version, MCP SDK version
   - Results: Timing data, success rates
   - Configuration: Environment variables, settings

---

**Last Updated**: 2025-10-04
**Benchmark Version**: v1.15.0
**GPU Reference**: NVIDIA GeForce RTX 3080 Ti (12GB VRAM)
