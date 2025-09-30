# Test Suite Documentation

This directory contains the organized test suite for the Enhanced Qdrant MCP Server.

## Directory Structure

```
tests/
├── integration/          # Integration and system-level tests
│   ├── test_orchestration.py       # Comprehensive test orchestrator
│   ├── stress_test.py               # High-volume operations testing
│   └── test_cuda_implementation.py  # GPU/CUDA functionality tests
├── unit/                 # Unit tests for specific functionality
│   ├── parameter_tester.py          # MCP parameter validation
│   ├── test_mcp_search.py           # MCP search functionality
│   └── mcp_test_writer.py           # MCP write operations
├── archive/              # Archived/obsolete tests
│   ├── test_onnx_cuda.py            # Historical ONNX CUDA tests
│   ├── test_post_cudnn.py           # Post-cuDNN validation
│   ├── validate_system.py           # System validation
│   └── final_validation.py          # Final validation report
└── README.md             # This file
```

## Running Tests

### Integration Tests

Integration tests validate end-to-end functionality and system behavior:

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific integration test
python tests/integration/test_orchestration.py
python tests/integration/stress_test.py
python tests/integration/test_cuda_implementation.py
```

#### test_orchestration.py
Comprehensive test orchestration that coordinates multiple test scenarios:
- Container health validation
- Qdrant API connectivity
- GPU detection and acceleration
- MCP server functionality
- Collection operations

**Usage:**
```bash
python tests/integration/test_orchestration.py
```

#### stress_test.py
High-volume operations testing for performance validation:
- 500+ document storage operations
- Bulk storage performance
- Search performance under load
- GPU acceleration benchmarks

**Usage:**
```bash
python tests/integration/stress_test.py
```

#### test_cuda_implementation.py
GPU/CUDA functionality and performance testing:
- CUDA availability detection
- ONNX Runtime GPU providers
- Embedding generation performance
- CPU vs GPU comparison

**Usage:**
```bash
python tests/integration/test_cuda_implementation.py
```

### Unit Tests

Unit tests validate specific components and functionality:

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific unit test
python tests/unit/parameter_tester.py
python tests/unit/test_mcp_search.py
python tests/unit/mcp_test_writer.py
```

#### parameter_tester.py
Systematic MCP tool parameter testing:
- Parameter type validation
- Default behavior verification
- Error condition testing
- Performance characteristics

**Usage:**
```bash
python tests/unit/parameter_tester.py
```

#### test_mcp_search.py
MCP search functionality validation:
- Semantic search operations
- Collection-specific model routing
- Search result accuracy

**Usage:**
```bash
python tests/unit/test_mcp_search.py
```

#### mcp_test_writer.py
MCP write operations testing:
- Document storage operations
- Metadata handling
- Bulk write operations

**Usage:**
```bash
python tests/unit/mcp_test_writer.py
```

## Test Utilities

Utility scripts for test data management are located in `scripts/utilities/`:

### cleanup_test_data.py
Consolidated utility for cleaning test documents from collections:

```bash
# Delete by metadata (default mode)
python scripts/utilities/cleanup_test_data.py --collection lodestar_legal_analysis

# Delete by content patterns
python scripts/utilities/cleanup_test_data.py --mode pattern --patterns "GPU-Accelerated"

# Custom test types
python scripts/utilities/cleanup_test_data.py --test-types gpu_test debug_test

# Show help
python scripts/utilities/cleanup_test_data.py --help
```

### collection_inspector.py
Inspect Qdrant collections and their contents:

```bash
# List all collections
python scripts/utilities/collection_inspector.py --mode list

# Inspect specific collection
python scripts/utilities/collection_inspector.py --mode inspect --collection my_collection

# Find largest collection
python scripts/utilities/collection_inspector.py --mode largest

# Show help
python scripts/utilities/collection_inspector.py --help
```

## Archived Tests

The `tests/archive/` directory contains historical tests that have been superseded by more comprehensive implementations. These are preserved for reference but are not actively maintained:

- **test_onnx_cuda.py**: Basic ONNX Runtime CUDA provider tests (superseded by test_cuda_implementation.py)
- **test_post_cudnn.py**: Post-cuDNN installation validation (superseded by test_cuda_implementation.py)
- **validate_system.py**: System-level validation (superseded by test_orchestration.py)
- **final_validation.py**: Final validation summary (superseded by test_orchestration.py)

## Test Requirements

### Docker Environment
Most integration tests require the Enhanced Qdrant MCP Server container to be running:

```bash
docker-compose -f docker-compose.enhanced.yml up -d
```

### Python Dependencies
All test dependencies are included in the main project dependencies:

```bash
pip install -e .
# or
uv sync
```

### GPU Testing
GPU-related tests require:
- NVIDIA GPU with CUDA 12.x support
- CUDA 12.x runtime installed
- cuDNN 9.13.0 libraries
- Docker with NVIDIA runtime support

## Test Conventions

### File Naming
- Integration tests: `test_*.py` or descriptive names (e.g., `stress_test.py`)
- Unit tests: `test_*.py` or `*_tester.py`
- Utilities: `*_utility.py` or descriptive names

### Test Execution
- All tests should be executable as standalone scripts
- Tests should be compatible with pytest when applicable
- Tests should clean up after themselves (use cleanup utilities)

### Output
- Use clear, descriptive output messages
- Include progress indicators for long-running tests
- Report success/failure with summary statistics

## Contributing

When adding new tests:

1. **Place tests in the appropriate directory**:
   - `tests/integration/` for system-level tests
   - `tests/unit/` for component tests

2. **Follow naming conventions**:
   - Descriptive filenames
   - Clear function/class names
   - Comprehensive docstrings

3. **Include documentation**:
   - Update this README with usage instructions
   - Add inline comments for complex logic
   - Document required environment setup

4. **Clean up test data**:
   - Use unique identifiers for test documents
   - Add cleanup code or use provided utilities
   - Don't leave test data in production collections

## Quick Reference

```bash
# Run all tests
pytest tests/ -v

# Run integration tests only
pytest tests/integration/ -v

# Run unit tests only
pytest tests/unit/ -v

# Run specific test file
python tests/integration/test_orchestration.py

# Clean up test data
python scripts/utilities/cleanup_test_data.py

# Inspect collections
python scripts/utilities/collection_inspector.py --mode list
```

## Support

For issues or questions about the test suite:
- Check test output for detailed error messages
- Review container logs: `docker-compose -f docker-compose.enhanced.yml logs -f`
- Verify Qdrant connectivity: `curl http://localhost:6333/collections`
- Check GPU availability: `nvidia-smi` (for GPU tests)
