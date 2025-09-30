#!/usr/bin/env python3
"""
Comprehensive Testing and Validation Orchestration for Qdrant MCP Server
Coordinates multiple test scenarios and generates detailed reports
"""

import subprocess
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Any

class TestOrchestrator:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "sections": {}
        }
        self.container_name = "mcp-server-qdrant-enhanced"
        
    def run_command(self, command: str, description: str = "", in_container: bool = True) -> Tuple[int, str, str]:
        """Execute command and return exit code, stdout, stderr"""
        if in_container:
            command = f"docker exec {self.container_name} bash -c '{command}'"
        
        print(f"\n📊 {description or command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    
    def test_container_health(self) -> Dict[str, Any]:
        """Test 1: Container Health and Connectivity"""
        print("\n" + "="*60)
        print("🏥 TEST 1: Container Health Validation")
        print("="*60)
        
        results = {
            "qdrant_api": False,
            "mcp_server": False,
            "collections_count": 0,
            "gpu_detected": False
        }
        
        # Check Qdrant API
        code, stdout, _ = self.run_command(
            "curl -s http://localhost:6333/collections | jq -r '.result.collections | length'",
            "Checking Qdrant API and collections",
            in_container=True
        )
        if code == 0 and stdout.strip().isdigit():
            results["qdrant_api"] = True
            results["collections_count"] = int(stdout.strip())
            print(f"✅ Qdrant API healthy with {results['collections_count']} collections")
        
        # Check MCP server process
        code, stdout, _ = self.run_command(
            "ps aux | grep -v grep | grep enhanced_main",
            "Checking MCP server process",
            in_container=True
        )
        if code == 0 and stdout:
            results["mcp_server"] = True
            print("✅ MCP server process running")
        
        # Check GPU
        code, stdout, _ = self.run_command(
            "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader",
            "Checking GPU availability",
            in_container=True
        )
        if code == 0 and "RTX" in stdout:
            results["gpu_detected"] = True
            print(f"✅ GPU detected: {stdout.strip()}")
        
        return results
    
    def test_gpu_acceleration(self) -> Dict[str, Any]:
        """Test 2: GPU/CUDA Configuration"""
        print("\n" + "="*60)
        print("🚀 TEST 2: GPU Acceleration Status")
        print("="*60)
        
        results = {
            "cuda_available": False,
            "onnx_cuda_provider": False,
            "fastembed_cuda": False,
            "actual_device": "cpu"
        }
        
        # Test CUDA availability
        code, stdout, _ = self.run_command(
            """python3 -c "
import torch
print('CUDA Available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('CUDA Device:', torch.cuda.get_device_name(0))
    print('CUDA Version:', torch.version.cuda)
"
""",
            "Testing PyTorch CUDA availability",
            in_container=True
        )
        if "CUDA Available: True" in stdout:
            results["cuda_available"] = True
            print("✅ PyTorch CUDA support confirmed")
        else:
            print("❌ PyTorch CUDA not available")
        
        # Test ONNX Runtime CUDA provider
        code, stdout, stderr = self.run_command(
            """python3 -c "
import onnxruntime as ort
providers = ort.get_available_providers()
print('Available providers:', providers)
if 'CUDAExecutionProvider' in providers:
    print('CUDA provider available')
    # Try to create session with CUDA
    try:
        import numpy as np
        from onnxruntime import InferenceSession
        # Create minimal ONNX model for testing
        session = InferenceSession(None, providers=['CUDAExecutionProvider'])
        print('CUDA provider can be initialized')
    except Exception as e:
        print(f'CUDA provider init failed: {e}')
"
""",
            "Testing ONNX Runtime CUDA provider",
            in_container=True
        )
        
        if "CUDA provider available" in stdout:
            results["onnx_cuda_provider"] = True
            print("✅ ONNX Runtime CUDA provider available")
        else:
            print(f"❌ ONNX Runtime CUDA provider not available")
            if stderr:
                print(f"   Error: {stderr[:200]}")
        
        # Test FastEmbed CUDA usage
        code, stdout, stderr = self.run_command(
            """python3 -c "
import os
os.environ['FASTEMBED_CUDA'] = 'true'
from src.mcp_server_qdrant.embeddings.enhanced_fastembed import EnhancedFastEmbedProvider
provider = EnhancedFastEmbedProvider()
print(f'FastEmbed device: {provider.device}')
print(f'CUDA enabled: {provider.cuda_enabled}')
# Test actual embedding
import numpy as np
test_text = ['Test embedding with GPU acceleration']
embeddings = provider.embed_texts(test_text, model_name='all-minilm-l6-v2')
print(f'Embedding shape: {embeddings[0].shape}')
print(f'Device used: {provider.device}')
"
""",
            "Testing FastEmbed GPU acceleration",
            in_container=True
        )
        
        if "Device used: cuda" in stdout or "Device used: gpu" in stdout:
            results["fastembed_cuda"] = True
            results["actual_device"] = "gpu"
            print("✅ FastEmbed using GPU acceleration")
        else:
            print("❌ FastEmbed falling back to CPU")
            if stderr and "CUDA" in stderr:
                print(f"   CUDA Error: {stderr[:200]}")
        
        return results
    
    def run_pytest_suite(self) -> Dict[str, Any]:
        """Test 3: Run Comprehensive Test Suite"""
        print("\n" + "="*60)
        print("🧪 TEST 3: Pytest Test Suite")
        print("="*60)
        
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "test_files": {}
        }
        
        # Run full test suite
        code, stdout, stderr = self.run_command(
            "cd /app && python -m pytest tests/ -v --tb=short --json-report --json-report-file=/tmp/pytest-report.json",
            "Running complete pytest suite",
            in_container=True
        )
        
        # Parse test results
        if "passed" in stdout or "failed" in stdout:
            lines = stdout.split('\n')
            for line in lines:
                if "passed" in line and "failed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "passed" in part and i > 0:
                            results["passed"] = int(parts[i-1])
                        if "failed" in part and i > 0:
                            results["failed"] = int(parts[i-1])
        
        # Try to read JSON report for detailed results
        code, stdout, _ = self.run_command(
            "cat /tmp/pytest-report.json 2>/dev/null | jq '.summary'",
            "Reading test report summary",
            in_container=True
        )
        if code == 0 and stdout:
            try:
                summary = json.loads(stdout)
                results["total_tests"] = summary.get("total", 0)
                results["passed"] = summary.get("passed", 0)
                results["failed"] = summary.get("failed", 0)
                print(f"📊 Test Results: {results['passed']} passed, {results['failed']} failed out of {results['total_tests']} total")
            except:
                pass
        
        # Run individual test files for details
        test_files = [
            "test_validators.py",
            "test_settings.py", 
            "test_qdrant_integration.py",
            "test_fastembed_integration.py"
        ]
        
        for test_file in test_files:
            code, stdout, _ = self.run_command(
                f"cd /app && python -m pytest tests/{test_file} -v --tb=line",
                f"Running {test_file}",
                in_container=True
            )
            
            passed = stdout.count(" PASSED")
            failed = stdout.count(" FAILED")
            results["test_files"][test_file] = {
                "passed": passed,
                "failed": failed,
                "status": "✅" if failed == 0 else "❌"
            }
            print(f"  {results['test_files'][test_file]['status']} {test_file}: {passed} passed, {failed} failed")
        
        return results
    
    def test_core_functionality(self) -> Dict[str, Any]:
        """Test 4: Core Store/Find Operations"""
        print("\n" + "="*60)
        print("🔧 TEST 4: Core Functionality Validation")
        print("="*60)
        
        results = {
            "store_operation": False,
            "find_operation": False,
            "collection_creation": False,
            "model_routing": False
        }
        
        # Test store operation
        code, stdout, stderr = self.run_command(
            """python3 -c "
import asyncio
from src.mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector
from src.mcp_server_qdrant.models import Entry

async def test_store():
    connector = EnhancedQdrantConnector()
    
    # Test storing in different collections
    entry1 = Entry(content='GPU acceleration test for MCP server', metadata={'type': 'test', 'timestamp': '2025-01-23'})
    entry2 = Entry(content='Legal document analysis with 1024D embeddings', metadata={'domain': 'legal'})
    
    # Store in technical collection (should use 384D model)
    result1 = await connector.store(entry1, collection_name='test_technical')
    print(f'Stored technical: {result1}')
    
    # Store in legal collection (should use 1024D model)  
    result2 = await connector.store(entry2, collection_name='legal_analysis')
    print(f'Stored legal: {result2}')
    
    return True

result = asyncio.run(test_store())
print(f'Store test result: {result}')
"
""",
            "Testing store operations with model routing",
            in_container=True
        )
        
        if "Store test result: True" in stdout and code == 0:
            results["store_operation"] = True
            print("✅ Store operation successful")
        else:
            print(f"❌ Store operation failed: {stderr[:200]}")
        
        # Test find operation
        code, stdout, stderr = self.run_command(
            """python3 -c "
import asyncio
from src.mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector

async def test_find():
    connector = EnhancedQdrantConnector()
    
    # Search in different collections
    results1 = await connector.find('GPU acceleration', collection_name='test_technical', limit=3)
    print(f'Technical search results: {len(results1)} found')
    
    results2 = await connector.find('legal document', collection_name='legal_analysis', limit=3)
    print(f'Legal search results: {len(results2)} found')
    
    return len(results1) > 0 or len(results2) > 0

result = asyncio.run(test_find())
print(f'Find test result: {result}')
"
""",
            "Testing find operations across collections",
            in_container=True
        )
        
        if "Find test result: True" in stdout and code == 0:
            results["find_operation"] = True
            print("✅ Find operation successful")
        else:
            print(f"❌ Find operation failed: {stderr[:200]}")
        
        # Test collection auto-creation
        code, stdout, _ = self.run_command(
            """python3 -c "
from src.mcp_server_qdrant.enhanced_settings import EnhancedSettings
settings = EnhancedSettings()
print(f'Auto-create enabled: {settings.auto_create_collections}')
print(f'Collection model mappings: {len(settings.collection_model_mappings)} predefined')
print(f'Available models: {list(settings.model_configs.keys())}')
"
""",
            "Checking collection configuration",
            in_container=True
        )
        
        if "Auto-create enabled: True" in stdout:
            results["collection_creation"] = True
            results["model_routing"] = "384" in stdout and "768" in stdout and "1024" in stdout
            print("✅ Collection auto-creation and model routing configured")
        
        return results
    
    def test_performance(self) -> Dict[str, Any]:
        """Test 5: Performance Metrics"""
        print("\n" + "="*60)
        print("⚡ TEST 5: Performance Testing")
        print("="*60)
        
        results = {
            "embedding_time_ms": 0,
            "storage_time_ms": 0,
            "search_time_ms": 0,
            "batch_performance": {}
        }
        
        # Test embedding performance
        code, stdout, _ = self.run_command(
            """python3 -c "
import time
import numpy as np
from src.mcp_server_qdrant.embeddings.enhanced_fastembed import EnhancedFastEmbedProvider

provider = EnhancedFastEmbedProvider()

# Test single embedding
text = 'Performance test for GPU-accelerated embeddings'
start = time.perf_counter()
embedding = provider.embed_texts([text], model_name='all-minilm-l6-v2')
single_time = (time.perf_counter() - start) * 1000
print(f'Single embedding: {single_time:.2f}ms')

# Test batch embedding
texts = [f'Test document {i} for batch processing' for i in range(100)]
start = time.perf_counter()
embeddings = provider.embed_texts(texts, model_name='all-minilm-l6-v2')
batch_time = (time.perf_counter() - start) * 1000
print(f'Batch (100 docs): {batch_time:.2f}ms')
print(f'Per document: {batch_time/100:.2f}ms')
print(f'Device: {provider.device}')
"
""",
            "Testing embedding performance",
            in_container=True
        )
        
        if "Single embedding:" in stdout:
            for line in stdout.split('\n'):
                if "Single embedding:" in line:
                    try:
                        results["embedding_time_ms"] = float(line.split(':')[1].replace('ms', '').strip())
                    except:
                        pass
                if "Batch (100 docs):" in line:
                    try:
                        batch_time = float(line.split(':')[1].replace('ms', '').strip())
                        results["batch_performance"]["100_docs_ms"] = batch_time
                        results["batch_performance"]["per_doc_ms"] = batch_time / 100
                    except:
                        pass
        
        # Test storage performance  
        code, stdout, _ = self.run_command(
            """python3 -c "
import asyncio
import time
from src.mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector
from src.mcp_server_qdrant.models import Entry

async def test_performance():
    connector = EnhancedQdrantConnector()
    
    # Test storage speed
    entry = Entry(content='Performance test document', metadata={'test': True})
    start = time.perf_counter()
    await connector.store(entry, collection_name='perf_test')
    storage_time = (time.perf_counter() - start) * 1000
    print(f'Storage time: {storage_time:.2f}ms')
    
    # Test search speed
    start = time.perf_counter()
    results = await connector.find('performance', collection_name='perf_test', limit=10)
    search_time = (time.perf_counter() - start) * 1000
    print(f'Search time: {search_time:.2f}ms')
    
asyncio.run(test_performance())
"
""",
            "Testing storage and search performance",
            in_container=True
        )
        
        if "Storage time:" in stdout:
            for line in stdout.split('\n'):
                if "Storage time:" in line:
                    try:
                        results["storage_time_ms"] = float(line.split(':')[1].replace('ms', '').strip())
                    except:
                        pass
                if "Search time:" in line:
                    try:
                        results["search_time_ms"] = float(line.split(':')[1].replace('ms', '').strip())
                    except:
                        pass
        
        # Performance analysis
        print(f"\n📊 Performance Summary:")
        print(f"  Embedding: {results['embedding_time_ms']:.2f}ms")
        print(f"  Storage: {results['storage_time_ms']:.2f}ms")
        print(f"  Search: {results['search_time_ms']:.2f}ms")
        
        if results.get("batch_performance"):
            print(f"  Batch (100): {results['batch_performance'].get('100_docs_ms', 0):.2f}ms")
            print(f"  Per document: {results['batch_performance'].get('per_doc_ms', 0):.2f}ms")
        
        return results
    
    def test_mcp_integration(self) -> Dict[str, Any]:
        """Test 6: MCP Server Integration"""
        print("\n" + "="*60)
        print("🔌 TEST 6: MCP Server Integration")
        print("="*60)
        
        results = {
            "server_responsive": False,
            "tools_registered": [],
            "tool_count": 0
        }
        
        # Test MCP server tools registration
        code, stdout, _ = self.run_command(
            """python3 -c "
from src.mcp_server_qdrant.enhanced_mcp_server import EnhancedQdrantMCPServer
import asyncio

async def test_mcp():
    server = EnhancedQdrantMCPServer()
    # Check registered tools
    tools = ['qdrant_store', 'qdrant_find', 'qdrant_get_collections', 
             'qdrant_delete_collection', 'qdrant_create_collection']
    
    for tool in tools:
        if hasattr(server, tool):
            print(f'Tool registered: {tool}')
    
    return True

asyncio.run(test_mcp())
"
""",
            "Testing MCP tool registration",
            in_container=True
        )
        
        if "Tool registered:" in stdout:
            results["server_responsive"] = True
            for line in stdout.split('\n'):
                if "Tool registered:" in line:
                    tool = line.split(':')[1].strip()
                    results["tools_registered"].append(tool)
            results["tool_count"] = len(results["tools_registered"])
            print(f"✅ MCP server has {results['tool_count']} tools registered")
        
        return results
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📝 COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        # Overall status calculation
        all_passed = True
        critical_issues = []
        warnings = []
        
        # Analyze results
        for section, data in self.results["sections"].items():
            if section == "container_health":
                if not data.get("mcp_server"):
                    critical_issues.append("MCP server not running")
                    all_passed = False
                if not data.get("qdrant_api"):
                    critical_issues.append("Qdrant API not responding")
                    all_passed = False
            
            elif section == "gpu_acceleration":
                if not data.get("cuda_available"):
                    warnings.append("CUDA not available - using CPU fallback")
                if data.get("actual_device") == "cpu":
                    warnings.append("FastEmbed using CPU instead of GPU")
            
            elif section == "pytest_suite":
                if data.get("failed", 0) > 0:
                    warnings.append(f"{data['failed']} pytest tests failed")
                    all_passed = False
            
            elif section == "core_functionality":
                if not data.get("store_operation"):
                    critical_issues.append("Store operation failed")
                    all_passed = False
                if not data.get("find_operation"):
                    critical_issues.append("Find operation failed")
                    all_passed = False
            
            elif section == "performance":
                if data.get("storage_time_ms", 0) > 100:
                    warnings.append(f"Storage time {data['storage_time_ms']:.2f}ms exceeds 100ms target")
        
        # Print summary
        status_emoji = "✅" if all_passed and not critical_issues else "⚠️" if warnings else "❌"
        
        print(f"\n{status_emoji} Overall Status: {'PASSED' if all_passed else 'FAILED WITH ISSUES'}")
        
        if critical_issues:
            print("\n🚨 Critical Issues:")
            for issue in critical_issues:
                print(f"  • {issue}")
        
        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"  • {warning}")
        
        # Detailed section results
        print("\n📊 Section Results:")
        for section, data in self.results["sections"].items():
            print(f"\n  {section.replace('_', ' ').title()}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    if key != "test_files":  # Skip detailed test files
                        print(f"    • {key}: {value}")
        
        # Save report to file
        with open('/tmp/test_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print("\n📄 Full report saved to: /tmp/test_report.json")
        
        return all_passed
    
    def run_all_tests(self):
        """Execute all tests in sequence"""
        print(f"🚀 Starting Comprehensive Test Orchestration at {datetime.now()}")
        print("="*60)
        
        # Run all test sections
        self.results["sections"]["container_health"] = self.test_container_health()
        self.results["sections"]["gpu_acceleration"] = self.test_gpu_acceleration()
        self.results["sections"]["pytest_suite"] = self.run_pytest_suite()
        self.results["sections"]["core_functionality"] = self.test_core_functionality()
        self.results["sections"]["performance"] = self.test_performance()
        self.results["sections"]["mcp_integration"] = self.test_mcp_integration()
        
        # Generate final report
        success = self.generate_report()
        
        return 0 if success else 1

if __name__ == "__main__":
    orchestrator = TestOrchestrator()
    exit_code = orchestrator.run_all_tests()
    sys.exit(exit_code)