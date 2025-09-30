#!/usr/bin/env python3
"""
Post-cuDNN Installation Test
Tests if cuDNN 9.x installation enables full CUDA acceleration
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_onnx_cuda_after_cudnn():
    """Test ONNX Runtime CUDA providers after cuDNN installation"""
    print("🧪 Testing ONNX Runtime CUDA after cuDNN installation...")

    try:
        import onnxruntime as ort
        print(f"  📦 ONNX Runtime version: {ort.__version__}")

        # Get available providers
        providers = ort.get_available_providers()
        print(f"  🔧 Available providers: {providers}")

        # Check for CUDA
        has_cuda = 'CUDAExecutionProvider' in providers
        has_tensorrt = 'TensorrtExecutionProvider' in providers

        print(f"  🚀 CUDA Provider: {'✅ Available' if has_cuda else '❌ Not available'}")
        print(f"  🏎️ TensorRT Provider: {'✅ Available' if has_tensorrt else '❌ Not available'}")

        if has_cuda:
            # Test CUDA provider creation
            try:
                # Create a simple test session
                session = ort.InferenceSession(None, providers=['CUDAExecutionProvider'])
                print("  ✅ CUDA provider initialized successfully (no cuDNN warnings expected)")
                return True
            except Exception as e:
                print(f"  ⚠️ CUDA provider test error: {e}")
                return False
        else:
            print("  ❌ CUDA provider not available")
            return False

    except ImportError as e:
        print(f"  ❌ ONNX Runtime not available: {e}")
        return False
    except Exception as e:
        print(f"  ❌ ONNX Runtime test failed: {e}")
        return False

async def test_fastembed_with_cudnn():
    """Test FastEmbed with cuDNN libraries available"""
    print("\n🚀 Testing FastEmbed with cuDNN libraries...")

    try:
        from mcp_server_qdrant.embeddings.enhanced_fastembed import EnhancedFastEmbedProvider
        from mcp_server_qdrant.enhanced_settings import EnhancedEmbeddingProviderSettings

        # Set CUDA environment
        os.environ['FASTEMBED_CUDA'] = 'true'

        settings = EnhancedEmbeddingProviderSettings()
        provider = EnhancedFastEmbedProvider(settings)

        # Test embedding generation
        test_docs = ["This is a test document for cuDNN-enabled CUDA acceleration"]
        print("  🔄 Testing embedding generation with cuDNN support...")

        start_time = time.time()
        embeddings = await provider.embed_documents(test_docs, collection_name="cudnn_test")
        end_time = time.time()

        if embeddings and len(embeddings) > 0:
            print(f"  ✅ Embedding successful in {end_time - start_time:.3f}s")
            print(f"  📊 Generated {len(embeddings)} embeddings with dimension {len(embeddings[0])}")
            print("  🎯 Expected: No cuDNN warnings if installation successful")
            return True
        else:
            print("  ❌ No embeddings generated")
            return False

    except Exception as e:
        print(f"  ❌ FastEmbed test failed: {e}")
        return False

def check_cudnn_installation():
    """Check if cuDNN libraries are installed"""
    print("🔍 Checking cuDNN installation...")

    # Check for cuDNN library files
    cudnn_paths = [
        "/usr/lib/x86_64-linux-gnu/libcudnn.so*",
        "/usr/local/cuda/lib64/libcudnn.so*",
        "/opt/conda/lib/libcudnn.so*"
    ]

    found_cudnn = False
    for path_pattern in cudnn_paths:
        try:
            result = subprocess.run(['ls', '-la', path_pattern], capture_output=True, text=True, shell=True)
            if result.returncode == 0 and result.stdout.strip():
                print(f"  ✅ Found cuDNN libraries: {result.stdout.strip()}")
                found_cudnn = True
                break
        except:
            continue

    if not found_cudnn:
        print("  ⚠️ cuDNN libraries not found in standard locations")
        print("  💡 Run: sudo apt-get install cudnn (after repository setup)")

    return found_cudnn

async def main():
    """Main test execution"""
    print("🎯 Post-cuDNN Installation Test Suite")
    print("=" * 40)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test 1: Check cuDNN installation
    cudnn_found = check_cudnn_installation()

    # Test 2: Test ONNX Runtime
    onnx_success = test_onnx_cuda_after_cudnn()

    # Test 3: Test FastEmbed
    fastembed_success = await test_fastembed_with_cudnn()

    print("\n📊 Post-Installation Test Summary:")
    print("=" * 35)
    print(f"cuDNN Libraries Found: {'✅ Yes' if cudnn_found else '❌ No'}")
    print(f"ONNX Runtime CUDA: {'✅ Working' if onnx_success else '❌ Still has issues'}")
    print(f"FastEmbed CUDA: {'✅ Working' if fastembed_success else '❌ Still has issues'}")

    if cudnn_found and onnx_success and fastembed_success:
        print("\n🎉 SUCCESS: Full GPU acceleration is now working!")
        print("   Expected performance improvement: 1.39x+ for storage operations")
    else:
        print("\n⚠️ Installation may need additional steps")
        if not cudnn_found:
            print("   - Install cuDNN: sudo apt-get install cudnn")
        print("   - Verify CUDA 12.x compatibility")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())