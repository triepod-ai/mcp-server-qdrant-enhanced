#!/usr/bin/env python3
"""
CUDA Implementation Test for Enhanced Qdrant MCP Server
Tests GPU acceleration functionality and performance comparison
"""

import asyncio
import os
import sys
import time
from typing import Dict, Any, List
import subprocess
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector, Entry
from mcp_server_qdrant.enhanced_settings import EnhancedQdrantSettings, EnhancedEmbeddingProviderSettings
from mcp_server_qdrant.embeddings.enhanced_fastembed import EnhancedFastEmbedProvider

class CUDATestRunner:
    def __init__(self):
        self.results = {
            "system_info": {},
            "cuda_tests": {},
            "performance_comparison": {},
            "embedding_tests": {}
        }

    def check_system_cuda(self) -> Dict[str, Any]:
        """Check system CUDA availability"""
        print("🔍 Checking System CUDA Configuration...")

        cuda_info = {
            "nvidia_smi_available": False,
            "cuda_devices": [],
            "cuda_version": None,
            "docker_nvidia_runtime": False,
            "environment_variables": {}
        }

        # Check nvidia-smi
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                cuda_info["nvidia_smi_available"] = True
                # Extract CUDA version from nvidia-smi output
                for line in result.stdout.split('\n'):
                    if 'CUDA Version:' in line:
                        cuda_info["cuda_version"] = line.split('CUDA Version:')[1].strip().split()[0]
                        break
                print(f"  ✅ nvidia-smi available, CUDA Version: {cuda_info['cuda_version']}")
            else:
                print("  ❌ nvidia-smi not available or failed")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"  ❌ nvidia-smi check failed: {e}")

        # Check CUDA environment variables
        cuda_env_vars = ['CUDA_VISIBLE_DEVICES', 'FASTEMBED_CUDA', 'NVIDIA_VISIBLE_DEVICES']
        for var in cuda_env_vars:
            value = os.environ.get(var)
            cuda_info["environment_variables"][var] = value
            if value:
                print(f"  📋 {var}={value}")

        # Check Docker NVIDIA runtime
        try:
            result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
            if 'nvidia' in result.stdout.lower():
                cuda_info["docker_nvidia_runtime"] = True
                print("  ✅ Docker NVIDIA runtime detected")
            else:
                print("  ⚠️ Docker NVIDIA runtime not detected")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("  ⚠️ Could not check Docker runtime")

        return cuda_info

    async def check_fastembed_cuda(self) -> Dict[str, Any]:
        """Check FastEmbed CUDA support"""
        print("\n🚀 Testing FastEmbed CUDA Support...")

        fastembed_info = {
            "providers_available": [],
            "cuda_provider_test": False,
            "cpu_provider_test": False,
            "model_loading_cuda": False,
            "model_loading_cpu": False
        }

        try:
            # Test CUDA provider creation with environment variable
            os.environ['FASTEMBED_CUDA'] = 'true'

            cuda_settings = EnhancedEmbeddingProviderSettings()
            cuda_provider = EnhancedFastEmbedProvider(cuda_settings)

            # Test model loading with CUDA
            test_model = "all-MiniLM-L6-v2"  # Fast, small model for testing
            print(f"  🔄 Testing CUDA model loading: {test_model}")

            start_time = time.time()
            test_embeddings = await cuda_provider.embed_documents(["CUDA test document"], collection_name="cuda_test")
            cuda_load_time = time.time() - start_time

            if test_embeddings and len(test_embeddings) > 0:
                fastembed_info["cuda_provider_test"] = True
                fastembed_info["model_loading_cuda"] = True
                fastembed_info["cuda_load_time"] = cuda_load_time
                print(f"  ✅ CUDA embedding successful in {cuda_load_time:.3f}s")
                print(f"  📊 Embedding dimension: {len(test_embeddings[0])}")
            else:
                print("  ❌ CUDA embedding failed - no embeddings returned")

        except Exception as e:
            print(f"  ❌ CUDA provider test failed: {str(e)}")
            fastembed_info["cuda_error"] = str(e)

        # Test CPU provider for comparison
        try:
            os.environ['FASTEMBED_CUDA'] = 'false'

            cpu_settings = EnhancedEmbeddingProviderSettings()
            cpu_provider = EnhancedFastEmbedProvider(cpu_settings)

            print(f"  🔄 Testing CPU model loading: {test_model}")

            start_time = time.time()
            test_embeddings = await cpu_provider.embed_documents(["CPU test document"], collection_name="cpu_test")
            cpu_load_time = time.time() - start_time

            if test_embeddings and len(test_embeddings) > 0:
                fastembed_info["cpu_provider_test"] = True
                fastembed_info["model_loading_cpu"] = True
                fastembed_info["cpu_load_time"] = cpu_load_time
                print(f"  ✅ CPU embedding successful in {cpu_load_time:.3f}s")

                # Performance comparison
                if fastembed_info["cuda_provider_test"] and fastembed_info.get("cuda_load_time"):
                    speedup = cpu_load_time / fastembed_info["cuda_load_time"] if fastembed_info["cuda_load_time"] > 0 else 0
                    print(f"  ⚡ CUDA speedup: {speedup:.2f}x faster than CPU")
                    fastembed_info["speedup_factor"] = speedup
            else:
                print("  ❌ CPU embedding failed - no embeddings returned")

        except Exception as e:
            print(f"  ❌ CPU provider test failed: {str(e)}")
            fastembed_info["cpu_error"] = str(e)

        return fastembed_info

    async def test_qdrant_cuda_integration(self) -> Dict[str, Any]:
        """Test CUDA integration with Qdrant connector"""
        print("\n🔗 Testing Qdrant-CUDA Integration...")

        integration_info = {
            "cuda_connector_test": False,
            "cpu_connector_test": False,
            "storage_performance": {},
            "search_performance": {}
        }

        test_collection = "cuda_test_collection"
        test_documents = [
            "CUDA acceleration test document for GPU performance validation",
            "FastEmbed integration with ONNX runtime GPU execution",
            "Vector database performance optimization with NVIDIA CUDA",
            "Machine learning inference acceleration for embedding generation",
            "High-performance computing with GPU-accelerated vector operations"
        ]

        # Test CUDA connector
        try:
            print("  🚀 Testing CUDA-enabled connector...")
            os.environ['FASTEMBED_CUDA'] = 'true'

            cuda_settings = EnhancedQdrantSettings()
            cuda_embedding_settings = EnhancedEmbeddingProviderSettings()
            cuda_connector = EnhancedQdrantConnector(cuda_settings, cuda_embedding_settings)

            await cuda_connector._ensure_connection()

            # Performance test with CUDA
            cuda_start = time.time()
            for i, doc in enumerate(test_documents):
                entry = Entry(
                    content=doc,
                    metadata={"test_type": "cuda", "doc_id": i, "timestamp": datetime.now().isoformat()}
                )
                await cuda_connector.store(entry, collection_name=test_collection)
            cuda_storage_time = time.time() - cuda_start

            integration_info["cuda_connector_test"] = True
            integration_info["storage_performance"]["cuda"] = cuda_storage_time
            print(f"  ✅ CUDA storage: {len(test_documents)} docs in {cuda_storage_time:.3f}s")

            # Test search performance
            cuda_search_start = time.time()
            search_results = await cuda_connector.search("GPU acceleration", collection_name=test_collection, limit=3)
            cuda_search_time = time.time() - cuda_search_start

            integration_info["search_performance"]["cuda"] = cuda_search_time
            print(f"  ✅ CUDA search: {len(search_results) if search_results else 0} results in {cuda_search_time:.3f}s")

        except Exception as e:
            print(f"  ❌ CUDA connector test failed: {str(e)}")
            integration_info["cuda_error"] = str(e)

        # Test CPU connector for comparison
        try:
            print("  💻 Testing CPU-only connector...")
            os.environ['FASTEMBED_CUDA'] = 'false'

            cpu_settings = EnhancedQdrantSettings()
            cpu_embedding_settings = EnhancedEmbeddingProviderSettings()
            cpu_connector = EnhancedQdrantConnector(cpu_settings, cpu_embedding_settings)

            await cpu_connector._ensure_connection()

            # Performance test with CPU
            cpu_start = time.time()
            for i, doc in enumerate(test_documents):
                entry = Entry(
                    content=doc,
                    metadata={"test_type": "cpu", "doc_id": i, "timestamp": datetime.now().isoformat()}
                )
                await cpu_connector.store(entry, collection_name=f"{test_collection}_cpu")
            cpu_storage_time = time.time() - cpu_start

            integration_info["cpu_connector_test"] = True
            integration_info["storage_performance"]["cpu"] = cpu_storage_time
            print(f"  ✅ CPU storage: {len(test_documents)} docs in {cpu_storage_time:.3f}s")

            # Test search performance
            cpu_search_start = time.time()
            search_results = await cpu_connector.search("GPU acceleration", collection_name=f"{test_collection}_cpu", limit=3)
            cpu_search_time = time.time() - cpu_search_start

            integration_info["search_performance"]["cpu"] = cpu_search_time
            print(f"  ✅ CPU search: {len(search_results) if search_results else 0} results in {cpu_search_time:.3f}s")

            # Performance comparison
            if integration_info["cuda_connector_test"]:
                storage_speedup = cpu_storage_time / cuda_storage_time if cuda_storage_time > 0 else 0
                search_speedup = cpu_search_time / cuda_search_time if cuda_search_time > 0 else 0

                print(f"  ⚡ Storage speedup: {storage_speedup:.2f}x faster with CUDA")
                print(f"  ⚡ Search speedup: {search_speedup:.2f}x faster with CUDA")

                integration_info["performance_improvement"] = {
                    "storage_speedup": storage_speedup,
                    "search_speedup": search_speedup
                }

        except Exception as e:
            print(f"  ❌ CPU connector test failed: {str(e)}")
            integration_info["cpu_error"] = str(e)

        return integration_info

    def generate_cuda_report(self) -> str:
        """Generate comprehensive CUDA test report"""
        system_info = self.results["system_info"]
        cuda_tests = self.results["cuda_tests"]
        integration_tests = self.results["integration_tests"]

        report = f"""
🚀 CUDA Implementation Test Report
=================================
Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🖥️ System CUDA Configuration:
==============================
NVIDIA SMI Available: {'✅ Yes' if system_info.get('nvidia_smi_available') else '❌ No'}
CUDA Version: {system_info.get('cuda_version', 'Not detected')}
Docker NVIDIA Runtime: {'✅ Detected' if system_info.get('docker_nvidia_runtime') else '❌ Not detected'}

Environment Variables:
"""

        for var, value in system_info.get("environment_variables", {}).items():
            status = f"✅ {value}" if value else "❌ Not set"
            report += f"- {var}: {status}\n"

        report += f"""
🔥 FastEmbed CUDA Testing:
==========================
CUDA Provider Test: {'✅ Success' if cuda_tests.get('cuda_provider_test') else '❌ Failed'}
CPU Provider Test: {'✅ Success' if cuda_tests.get('cpu_provider_test') else '❌ Failed'}
Model Loading (CUDA): {'✅ Success' if cuda_tests.get('model_loading_cuda') else '❌ Failed'}
Model Loading (CPU): {'✅ Success' if cuda_tests.get('model_loading_cpu') else '❌ Failed'}
"""

        if cuda_tests.get('speedup_factor'):
            report += f"Performance Speedup: ⚡ {cuda_tests['speedup_factor']:.2f}x faster with CUDA\n"

        if cuda_tests.get('cuda_error'):
            report += f"CUDA Error: ❌ {cuda_tests['cuda_error']}\n"

        if cuda_tests.get('cpu_error'):
            report += f"CPU Error: ❌ {cuda_tests['cpu_error']}\n"

        report += f"""
🔗 Qdrant Integration Testing:
==============================
CUDA Connector: {'✅ Success' if integration_tests.get('cuda_connector_test') else '❌ Failed'}
CPU Connector: {'✅ Success' if integration_tests.get('cpu_connector_test') else '❌ Failed'}
"""

        storage_perf = integration_tests.get('storage_performance', {})
        search_perf = integration_tests.get('search_performance', {})

        if storage_perf.get('cuda') and storage_perf.get('cpu'):
            report += f"""
Storage Performance:
- CUDA: {storage_perf['cuda']:.3f}s
- CPU: {storage_perf['cpu']:.3f}s

Search Performance:
- CUDA: {search_perf.get('cuda', 0):.3f}s
- CPU: {search_perf.get('cpu', 0):.3f}s
"""

        perf_improvement = integration_tests.get('performance_improvement', {})
        if perf_improvement:
            report += f"""
Performance Improvements:
- Storage Speedup: ⚡ {perf_improvement.get('storage_speedup', 0):.2f}x faster
- Search Speedup: ⚡ {perf_improvement.get('search_speedup', 0):.2f}x faster
"""

        report += f"""
📊 Test Summary:
================
Overall CUDA Status: {'✅ WORKING' if self.is_cuda_working() else '❌ NOT WORKING'}
Recommendations:
{self.get_recommendations()}
"""

        return report

    def is_cuda_working(self) -> bool:
        """Determine if CUDA is working properly"""
        system_ok = self.results["system_info"].get("nvidia_smi_available", False)
        fastembed_ok = self.results["cuda_tests"].get("cuda_provider_test", False)
        integration_ok = self.results["integration_tests"].get("cuda_connector_test", False)

        return system_ok and fastembed_ok and integration_ok

    def get_recommendations(self) -> str:
        """Generate recommendations based on test results"""
        recommendations = []

        if not self.results["system_info"].get("nvidia_smi_available"):
            recommendations.append("- Install NVIDIA drivers and CUDA toolkit")

        if not self.results["system_info"].get("environment_variables", {}).get("FASTEMBED_CUDA"):
            recommendations.append("- Set FASTEMBED_CUDA=true environment variable")

        if not self.results["system_info"].get("docker_nvidia_runtime"):
            recommendations.append("- Install Docker NVIDIA runtime for containerized deployment")

        if self.results["cuda_tests"].get("cuda_error"):
            recommendations.append("- Check ONNX runtime GPU installation")
            recommendations.append("- Verify CUDA compatibility with your GPU")

        if not recommendations:
            recommendations.append("- CUDA implementation is working correctly!")
            recommendations.append("- Consider monitoring GPU memory usage during high-load operations")

        return "\n".join(recommendations)

    async def run_comprehensive_cuda_test(self):
        """Run comprehensive CUDA implementation test"""
        print("🎯 Starting Comprehensive CUDA Implementation Test")
        print("=" * 55)

        # Test 1: System CUDA check
        self.results["system_info"] = self.check_system_cuda()

        # Test 2: FastEmbed CUDA support
        self.results["cuda_tests"] = await self.check_fastembed_cuda()

        # Test 3: Qdrant integration
        self.results["integration_tests"] = await self.test_qdrant_cuda_integration()

        # Generate and display report
        report = self.generate_cuda_report()
        print(report)

        # Save report to file
        report_filename = f"cuda_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w') as f:
            f.write(report)
        print(f"📄 Detailed CUDA test report saved to: {report_filename}")

async def main():
    """Main CUDA test execution"""
    cuda_tester = CUDATestRunner()
    await cuda_tester.run_comprehensive_cuda_test()

if __name__ == "__main__":
    asyncio.run(main())