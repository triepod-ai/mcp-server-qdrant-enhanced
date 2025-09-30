# Archived Tests

This directory contains historical test files that have been superseded by more comprehensive implementations. These tests are preserved for reference and historical context.

## Archived Files

### test_onnx_cuda.py
**Purpose**: Basic ONNX Runtime CUDA provider availability testing

**Superseded by**: `tests/integration/test_cuda_implementation.py`

**Why archived**:
- Limited to basic provider detection
- No performance testing
- No comprehensive GPU validation
- Replaced by more complete CUDA implementation test

### test_post_cudnn.py
**Purpose**: Post-cuDNN 9.x installation validation

**Superseded by**: `tests/integration/test_cuda_implementation.py`

**Why archived**:
- Single-purpose validation script
- Specific to cuDNN installation milestone
- Functionality integrated into comprehensive CUDA tests
- No longer needed after successful cuDNN integration

### validate_system.py
**Purpose**: System-level validation of MCP server functionality

**Superseded by**: `tests/integration/test_orchestration.py`

**Why archived**:
- Basic validation without comprehensive reporting
- Limited scope compared to orchestration suite
- No structured test result tracking
- Replaced by coordinated test orchestration

### final_validation.py
**Purpose**: Summary validation report for GPU acceleration implementation

**Superseded by**: `tests/integration/test_orchestration.py`

**Why archived**:
- Static summary report, not dynamic testing
- Specific to GPU implementation milestone
- No actual test execution, just status reporting
- Replaced by comprehensive orchestrated testing with live results

## Usage

These files are preserved for historical reference and can be reviewed to understand:
- Evolution of the test suite
- Historical validation approaches
- Specific implementation milestones
- Testing patterns that were later improved

**Do not use these tests in production or CI/CD pipelines.** Use the current test suite in `tests/integration/` and `tests/unit/` instead.

## Migration Path

If you need to reference functionality from archived tests:

1. **GPU/CUDA Testing** → Use `tests/integration/test_cuda_implementation.py`
2. **System Validation** → Use `tests/integration/test_orchestration.py`
3. **Specific Milestones** → Review git history for context

## Historical Context

These tests were created during the following development milestones:

- **2025-01-24**: Initial CUDA 12.x implementation and cuDNN 9.13.0 integration
- **2025-01-25**: MCP SDK v1.14.1 upgrade and GPU acceleration validation
- **2025-01-26**: Test suite consolidation and organization

For complete project history, see `PROJECT_STATUS.md` in the repository root.
